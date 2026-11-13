#!/usr/bin/env python3
"""
Akiba Robot Odometry Node
Motor hız verilerinden (mps_info) odometri hesaplar ve yayınlar
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Vector3, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
import math


class AkibaOdometryNode(Node):
    def __init__(self):
        super().__init__('akiba_odometry_node')
        
        # Parametreler - Kalibre edilmiş değerler
        self.declare_parameter('wheel_base', 0.319
)      # Kalibre: 130°/90° düzeltmesi
        self.declare_parameter('wheel_diameter', 0.111)  # Kalibre: Mesafe düzeltmesi
        self.declare_parameter('publish_tf', True)
        self.declare_parameter('base_frame', 'base_footprint')
        self.declare_parameter('odom_frame', 'odom')
        
        # Parametreleri al
        self.wheel_base = self.get_parameter('wheel_base').value
        self.wheel_diameter = self.get_parameter('wheel_diameter').value
        self.publish_tf = self.get_parameter('publish_tf').value
        self.base_frame = self.get_parameter('base_frame').value
        self.odom_frame = self.get_parameter('odom_frame').value
        
        # Odometri durumu
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        
        # Önceki zaman damgası
        self.last_time = None
        
        # Publisher'lar
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        
        # TF Broadcaster
        if self.publish_tf:
            self.tf_broadcaster = TransformBroadcaster(self)
        
        # QoS Profile - BEST_EFFORT (STM32 ile uyumlu)
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # Subscriber
        self.create_subscription(
            Vector3,
            '/akiba_1/mps_info',
            self.mps_callback,
            qos_profile
        )
        
        self.get_logger().info('=' * 60)
        self.get_logger().info(' Akiba Odometry Node başlatıldı!')
        self.get_logger().info(f'   Wheel base: {self.wheel_base}m (Kalibre)')
        self.get_logger().info(f'   Wheel diameter: {self.wheel_diameter}m (Kalibre)')
        self.get_logger().info(f'   Frames: {self.odom_frame} -> {self.base_frame}')
        self.get_logger().info(f'   QoS: BEST_EFFORT')
        self.get_logger().info('=' * 60)
    
    def mps_callback(self, msg):
        """
        STM32'den gelen motor hızlarını işle ve odometri hesapla
        msg.x: Motor 1 (Sağ tekerlek) hızı (m/s)
        msg.y: Motor 2 (Sol tekerlek) hızı (m/s)
        msg.z: Timestamp (milliseconds)
        """
        current_time = self.get_clock().now()
        
        # İlk mesaj ise sadece zamanı kaydet
        if self.last_time is None:
            self.last_time = current_time
            self.get_logger().info(' İlk MPS mesajı alındı!')
            return
        
        # Delta time hesapla (saniye cinsinden)
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time
        
        # Çok küçük veya çok büyük dt değerlerini filtrele
        if dt <= 0.0 or dt > 1.0:
            self.get_logger().warn(f'Anormal dt değeri: {dt}s, atlanıyor')
            return
        
        # Motor hızları (m/s)
        v_right = msg.x  # Motor 1 (Sağ)
        v_left = msg.y   # Motor 2 (Sol)
        
        # Diferansiyel sürüş kinematiği
        v = (v_right + v_left) / 2.0  # Ortalama doğrusal hız
        omega = (v_right - v_left) / self.wheel_base  # Açısal hız
        
        # Delta pozisyon hesapla
        delta_s = v * dt  # Doğrusal yer değiştirme
        delta_theta = omega * dt  # Açısal yer değiştirme
        
        # Yeni pozisyonu hesapla (Orta nokta yöntemi)
        theta_mid = self.theta + delta_theta / 2.0
        
        self.x += delta_s * math.cos(theta_mid)
        self.y += delta_s * math.sin(theta_mid)
        self.theta += delta_theta
        
        # Theta'yı [-pi, pi] aralığında tut
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
        
        # Odometry mesajı oluştur ve yayınla
        self.publish_odometry(current_time, v, omega)
    
    def publish_odometry(self, current_time, v, omega):
        """Odometry mesajı ve TF oluştur"""
        
        # Odometry mesajı
        odom = Odometry()
        odom.header.stamp = current_time.to_msg()
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame
        
        # Pozisyon
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        
        # Quaternion (yaw -> quaternion dönüşümü)
        odom.pose.pose.orientation.x = 0.0
        odom.pose.pose.orientation.y = 0.0
        odom.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        odom.pose.pose.orientation.w = math.cos(self.theta / 2.0)
        
        # Hız (robot frame'inde)
        odom.twist.twist.linear.x = v
        odom.twist.twist.linear.y = 0.0
        odom.twist.twist.angular.z = omega
        
        # Kovaryans matrisleri
        odom.pose.covariance = [
            0.01, 0.0,   0.0, 0.0, 0.0, 0.0,
            0.0,  0.01,  0.0, 0.0, 0.0, 0.0,
            0.0,  0.0,   1e6, 0.0, 0.0, 0.0,
            0.0,  0.0,   0.0, 1e6, 0.0, 0.0,
            0.0,  0.0,   0.0, 0.0, 1e6, 0.0,
            0.0,  0.0,   0.0, 0.0, 0.0, 0.1
        ]
        
        odom.twist.covariance = [
            0.01, 0.0,   0.0, 0.0, 0.0, 0.0,
            0.0,  0.01,  0.0, 0.0, 0.0, 0.0,
            0.0,  0.0,   1e6, 0.0, 0.0, 0.0,
            0.0,  0.0,   0.0, 1e6, 0.0, 0.0,
            0.0,  0.0,   0.0, 0.0, 1e6, 0.0,
            0.0,  0.0,   0.0, 0.0, 0.0, 0.05
        ]
        
        # Yayınla
        self.odom_pub.publish(odom)
        
        # TF yayınla
        if self.publish_tf:
            t = TransformStamped()
            t.header.stamp = current_time.to_msg()
            t.header.frame_id = self.odom_frame
            t.child_frame_id = self.base_frame
            
            t.transform.translation.x = self.x
            t.transform.translation.y = self.y
            t.transform.translation.z = 0.0
            
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = math.sin(self.theta / 2.0)
            t.transform.rotation.w = math.cos(self.theta / 2.0)
            
            self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = AkibaOdometryNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('\n Odometry node durduruldu.')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

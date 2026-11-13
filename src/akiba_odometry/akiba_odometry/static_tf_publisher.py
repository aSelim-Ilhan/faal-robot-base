#!/usr/bin/env python3
"""
Static TF Publisher for Akiba Robot
Fiziksel Boyutlar:
- Robot: 92cm x 48cm x 55cm
- LIDAR: Merkezden 43cm ileri, yerden 41cm
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster


class AkibaStaticTFPublisher(Node):
    def __init__(self):
        super().__init__('akiba_static_tf_publisher')
        
        self.tf_static_broadcaster = StaticTransformBroadcaster(self)
        self.publish_static_transforms()
        
        self.get_logger().info('Akiba Static TF Publisher başlatıldı')
        self.get_logger().info('Robot: 92cm x 48cm x 55cm')
        self.get_logger().info('LIDAR: +43cm ileri, +41cm yukarı')
    
    def publish_static_transforms(self):
        """Statik TF'leri yayınla"""
        
        transforms = []
        
        # 1. base_footprint -> base_link
        # base_link robotun geometrik merkezi, yerden ~8cm yukarıda
        t1 = TransformStamped()
        t1.header.stamp = self.get_clock().now().to_msg()
        t1.header.frame_id = 'base_footprint'
        t1.child_frame_id = 'base_link'
        t1.transform.translation.x = 0.0
        t1.transform.translation.y = 0.0
        t1.transform.translation.z = 0.08  # Yerden 8cm yukarı
        t1.transform.rotation.x = 0.0
        t1.transform.rotation.y = 0.0
        t1.transform.rotation.z = 0.0
        t1.transform.rotation.w = 1.0
        transforms.append(t1)
        
        # 2. base_link -> imu_link
        # IMU genellikle robot merkezinde
        t2 = TransformStamped()
        t2.header.stamp = self.get_clock().now().to_msg()
        t2.header.frame_id = 'base_link'
        t2.child_frame_id = 'imu_link'
        t2.transform.translation.x = 0.0
        t2.transform.translation.y = 0.0
        t2.transform.translation.z = 0.02  # 2cm yukarı
        t2.transform.rotation.x = 0.0
        t2.transform.rotation.y = 0.0
        t2.transform.rotation.z = 0.0
        t2.transform.rotation.w = 1.0
        transforms.append(t2)
        
        # 3. base_link -> laser_link
        # LIDAR: Merkezden 43cm ileri, yerden 41cm
        # base_link yerden 8cm, LIDAR yerden 41cm
        # Z farkı: 41 - 8 = 33cm
        t3 = TransformStamped()
        t3.header.stamp = self.get_clock().now().to_msg()
        t3.header.frame_id = 'base_link'
        t3.child_frame_id = 'laser_link'
        t3.transform.translation.x = 0.43   # 43cm ileri
        t3.transform.translation.y = 0.0    # Merkezde
        t3.transform.translation.z = 0.33   # base_link'ten 33cm yukarı
        t3.transform.rotation.x = 0.0
        t3.transform.rotation.y = 0.0
        t3.transform.rotation.z = 0.0       # Normal yön
        t3.transform.rotation.w = 1.0
        transforms.append(t3)
        
        # Tüm TF'leri yayınla
        self.tf_static_broadcaster.sendTransform(transforms)
        
        self.get_logger().info('Statik TF\'ler yayınlandı:')
        self.get_logger().info('  - base_footprint -> base_link (Z: 0.08m)')
        self.get_logger().info('  - base_link -> imu_link (Z: 0.02m)')
        self.get_logger().info('  - base_link -> laser_link (X: 0.43m, Z: 0.33m)')


def main(args=None):
    rclpy.init(args=args)
    node = AkibaStaticTFPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

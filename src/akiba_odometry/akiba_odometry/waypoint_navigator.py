#!/usr/bin/env python3
"""
Akiba Robot - Waypoint Navigator (4 DURAK)
Başlangıç noktasına git → 4 durakta dur → Başlangıç noktasına dön
SIRA: 1 → 2 → 3 → 4 → Başlangıç
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import time


class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')
        
        # Action client
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Başlangıç noktası (1. Durak)
        self.start_pose = {
            'x': 0.04,
            'y': 0.0,
            'z': 0.0,      # Düz ileri
            'w': 1.0       # Düz ileri
        }
        
        # Duraklar - DOĞRU SIRA: 1, 2, 3, 4
        self.waypoints = [
            {'x': 0.71,  'y': -1.27, 'z': 0.0, 'w': 1.0},    # 1. durak - düz ileri ↑
            {'x': 2.99,  'y': -1.27, 'z': 0.0, 'w': 1.0},    # 2. durak - düz ileri ↑
            {'x': 3.15,  'y': 0.8,  'z': 0.9, 'w': -0.1},    # 3. durak
            {'x': 1.07,  'y': 0.8,  'z': 0.9, 'w': -0.1},    # 4. durak
        ]
        
        self.get_logger().info(' Waypoint Navigator başlatıldı! (4 DURAK)')
        self.get_logger().info(f' Başlangıç noktası: x={self.start_pose["x"]}, y={self.start_pose["y"]}')
    
    def create_goal(self, x, y, qz, qw):
        """Nav2 goal mesajı oluştur"""
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw
        
        return goal_msg
    
    def send_goal(self, x, y, qz, qw, waypoint_name):
        """Hedefe git"""
        self.get_logger().info(f' {waypoint_name} gidiliyor... (x={x:.2f}, y={y:.2f})')
        
        # Action server hazır mı bekle
        self._action_client.wait_for_server()
        
        # Goal gönder
        goal_msg = self.create_goal(x, y, qz, qw)
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        
        # Goal kabul edilmesini bekle
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error(f' {waypoint_name} reddedildi!')
            return False
        
        self.get_logger().info(f' {waypoint_name} kabul edildi, gidiliyor...')
        
        # Sonucu bekle
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        
        result = result_future.result().result
        
        if result:
            self.get_logger().info(f' {waypoint_name} ulaşıldı!')
            return True
        else:
            self.get_logger().error(f' {waypoint_name} başarısız!')
            return False
    
    def feedback_callback(self, feedback_msg):
        """Navigation feedback (opsiyonel)"""
        pass
    
    def run(self):
        """Ana rota döngüsü"""
        self.get_logger().info('')
        self.get_logger().info('=' * 60)
        self.get_logger().info(' BAŞLANGIÇ NOKTASINA GİDİLİYOR')
        self.get_logger().info('=' * 60)
        self.get_logger().info('')
        
        # 1. ADIM: Başlangıç noktasına git
        success = self.send_goal(
            self.start_pose['x'],
            self.start_pose['y'],
            self.start_pose['z'],
            self.start_pose['w'],
            'Başlangıç Noktası'
        )
        
        if not success:
            self.get_logger().error(' Başlangıç noktasına gidilemedi! Rota iptal edildi.')
            return
        
        # Başlangıçta bekle (5 saniye)
        self.get_logger().info('  Başlangıç noktasında - 5 saniye bekleniyor...')
        time.sleep(5.0)
        self.get_logger().info('')
        
        self.get_logger().info('=' * 60)
        self.get_logger().info(' DURAK ROTASI BAŞLIYOR! (1 → 2 → 3 → 4)')
        self.get_logger().info('=' * 60)
        self.get_logger().info('')
        
        # 2. ADIM: 4 durakta sırayla dur
        for i, wp in enumerate(self.waypoints, start=1):
            success = self.send_goal(
                wp['x'], wp['y'], wp['z'], wp['w'],
                f'Durak {i}/4'
            )
            
            if not success:
                self.get_logger().error(' Rota iptal edildi!')
                return
            
            # Durakta bekle (5 saniye)
            self.get_logger().info(f'  Durak {i}/4 - 5 saniye bekleniyor...')
            time.sleep(5.0)
            self.get_logger().info('')
        
        # 3. ADIM: Başlangıç noktasına geri dön
        self.get_logger().info('=' * 60)
        self.get_logger().info(' BAŞLANGIÇ NOKTASINA GERİ DÖNÜLÜYOR')
        self.get_logger().info('=' * 60)
        self.get_logger().info('')
        
        success = self.send_goal(
            self.start_pose['x'],
            self.start_pose['y'],
            self.start_pose['z'],
            self.start_pose['w'],
            'Başlangıç Noktası (Dönüş)'
        )
        
        if success:
            self.get_logger().info('')
            self.get_logger().info('=' * 60)
            self.get_logger().info(' ROTA TAMAMLANDI!')
            self.get_logger().info('   Başlangıç → Durak 1 → 2 → 3 → 4 → Başlangıç')
            self.get_logger().info('=' * 60)
        else:
            self.get_logger().error(' Başlangıç noktasına dönüş başarısız!')


def main(args=None):
    rclpy.init(args=args)
    navigator = WaypointNavigator()
    
    try:
        navigator.run()
    except KeyboardInterrupt:
        navigator.get_logger().info('  Rota durduruldu!')
    finally:
        navigator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

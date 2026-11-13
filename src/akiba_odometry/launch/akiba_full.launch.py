#!/usr/bin/env python3
"""
Akiba Robot - Tam Sistem Launch
Odometry + EKF + TF'leri tek komutla başlatır
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    
    pkg_share = get_package_share_directory('akiba_odometry')
    
    # Config dosyaları
    odometry_config = os.path.join(pkg_share, 'config', 'odometry_params.yaml')
    ekf_config = os.path.join(pkg_share, 'config', 'ekf_config.yaml')
    
    # 1. Odometry Node - Config dosyasından parametreleri yükle
    odometry_node = Node(
        package='akiba_odometry',
        executable='odometry_node',
        name='odometry_node',
        output='screen',
        parameters=[odometry_config]  # YAML dosyasından yükle!
    )
    
    # 2. Static TF Publisher
    static_tf_node = Node(
        package='akiba_odometry',
        executable='static_tf_publisher',
        name='static_tf_publisher',
        output='screen'
    )
    
    # 3. EKF Node
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config]
    )
    
    return LaunchDescription([
        odometry_node,
        static_tf_node,
        ekf_node
    ])

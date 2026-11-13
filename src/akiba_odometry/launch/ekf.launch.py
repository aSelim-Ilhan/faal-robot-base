#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    
    # Config dosyası yolu
    ekf_config = os.path.join(
        get_package_share_directory('akiba_odometry'),
        'config',
        'ekf_config.yaml'
    )
    
    # EKF node
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config],
        remappings=[('odometry/filtered', 'odometry/filtered')]
    )
    
    return LaunchDescription([
        ekf_node
    ])

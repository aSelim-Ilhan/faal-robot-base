#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    
    # Launch argümanları
    wheel_base_arg = DeclareLaunchArgument(
        'wheel_base',
        default_value='0.422',
        description='Robot tekerlek tabanı (m)'
    )
    
    wheel_diameter_arg = DeclareLaunchArgument(
        'wheel_diameter',
        default_value='0.16',
        description='Tekerlek çapı (m)'
    )
    
    publish_tf_arg = DeclareLaunchArgument(
        'publish_tf',
        default_value='true',
        description='TF yayınlansın mı?'
    )
    
    # Odometry node
    odometry_node = Node(
        package='akiba_odometry',
        executable='odometry_node',
        name='odometry_node',
        output='screen',
        parameters=[{
            'wheel_base': LaunchConfiguration('wheel_base'),
            'wheel_diameter': LaunchConfiguration('wheel_diameter'),
            'publish_tf': LaunchConfiguration('publish_tf'),
            'base_frame': 'base_footprint',
            'odom_frame': 'odom'
        }]
    )
    
    # Static TF publisher
    static_tf_node = Node(
        package='akiba_odometry',
        executable='static_tf_publisher',
        name='static_tf_publisher',
        output='screen'
    )
    
    return LaunchDescription([
        wheel_base_arg,
        wheel_diameter_arg,
        publish_tf_arg,
        odometry_node,
        static_tf_node
    ])

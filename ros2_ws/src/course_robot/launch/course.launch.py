"""Launch the lightweight course world in MVSim and optionally RViz2."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Create the launch description for the course simulator."""
    course_share = get_package_share_directory('course_robot')
    default_world = os.path.join(
        course_share, 'worlds', 'course.world.xml')
    rviz_config = os.path.join(
        course_share, 'config', 'course.rviz')

    headless = LaunchConfiguration('headless')
    use_rviz = LaunchConfiguration('use_rviz')
    world_file = LaunchConfiguration('world')
    do_fake_localization = LaunchConfiguration('do_fake_localization')
    publish_odom_tf = LaunchConfiguration('publish_odom_tf')
    realtime_factor = LaunchConfiguration('realtime_factor')

    return LaunchDescription([
        DeclareLaunchArgument(
            'world', default_value=default_world,
            description='Absolute path to an MVSim world XML file'),
        DeclareLaunchArgument(
            'headless', default_value='false',
            description='Disable the MVSim GUI'),
        DeclareLaunchArgument(
            'use_rviz', default_value='true',
            description='Start RViz2'),
        DeclareLaunchArgument(
            'do_fake_localization', default_value='true',
            description='Publish a fixed map-to-odom transform'),
        DeclareLaunchArgument(
            'publish_odom_tf', default_value='true',
            description='Publish the odom-to-base_link transform'),
        DeclareLaunchArgument(
            'realtime_factor', default_value='1.0',
            description='MVSim speed relative to wall time'),
        Node(
            package='mvsim',
            executable='mvsim_node',
            name='mvsim',
            output='screen',
            parameters=[{
                'world_file': world_file,
                'headless': headless,
                'do_fake_localization': do_fake_localization,
                'publish_tf_odom2baselink': publish_odom_tf,
                'force_publish_vehicle_namespace': False,
                'publish_log_topics': False,
                'use_sim_time': False,
                'realtime_factor': realtime_factor,
            }],
        ),
        Node(
            package='course_robot',
            executable='scan_relay',
            name='scan_relay',
            output='screen',
        ),
        Node(
            condition=IfCondition(use_rviz),
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
        ),
    ])

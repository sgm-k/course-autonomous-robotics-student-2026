"""Launch MVSim with SLAM Toolbox for course mapping exercises."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Create the simulator and asynchronous SLAM launch description."""
    course_share = get_package_share_directory('course_robot')
    slam_share = get_package_share_directory('slam_toolbox')

    course_launch = os.path.join(course_share, 'launch', 'course.launch.py')
    slam_launch = os.path.join(
        slam_share, 'launch', 'online_async_launch.py')
    slam_params = os.path.join(course_share, 'config', 'slam.yaml')

    headless = LaunchConfiguration('headless')
    use_rviz = LaunchConfiguration('use_rviz')
    world = LaunchConfiguration('world')

    return LaunchDescription([
        DeclareLaunchArgument(
            'world', default_value=os.path.join(
                course_share, 'worlds', 'course.world.xml'),
            description='Absolute path to an MVSim world XML file'),
        DeclareLaunchArgument(
            'headless', default_value='false',
            description='Disable the MVSim GUI'),
        DeclareLaunchArgument(
            'use_rviz', default_value='true',
            description='Start RViz2'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(course_launch),
            launch_arguments={
                'headless': headless,
                'use_rviz': use_rviz,
                'world': world,
                'do_fake_localization': 'false',
                'publish_odom_tf': 'true',
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_launch),
            launch_arguments={
                'slam_params_file': slam_params,
                # MVSim timestamps use wall time and it publishes no /clock.
                'use_sim_time': 'false',
                'autostart': 'true',
            }.items(),
        ),
    ])

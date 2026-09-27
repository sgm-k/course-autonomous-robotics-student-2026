"""Launch MVSim and AMCL against a course map."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Create the simulator and Nav2 localization launch description."""
    course_share = get_package_share_directory('course_robot')
    nav2_share = get_package_share_directory('nav2_bringup')

    map_file = LaunchConfiguration('map')
    headless = LaunchConfiguration('headless')
    use_rviz = LaunchConfiguration('use_rviz')
    world = LaunchConfiguration('world')
    params_file = os.path.join(course_share, 'config', 'nav2_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'world', default_value=os.path.join(
                course_share, 'worlds', 'course.world.xml'),
            description='Absolute path to an MVSim world XML file'),
        DeclareLaunchArgument(
            'map', description='Absolute path to the map YAML file'),
        DeclareLaunchArgument(
            'headless', default_value='false',
            description='Disable the MVSim GUI'),
        DeclareLaunchArgument(
            'use_rviz', default_value='true',
            description='Start RViz2'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(course_share, 'launch', 'course.launch.py')),
            launch_arguments={
                'headless': headless,
                'use_rviz': use_rviz,
                'world': world,
                'do_fake_localization': 'false',
                'publish_odom_tf': 'true',
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_share, 'launch',
                             'localization_launch.py')),
            launch_arguments={
                'map': map_file,
                'params_file': params_file,
                'use_sim_time': 'false',
                'autostart': 'true',
                'use_composition': 'False',
            }.items(),
        ),
    ])

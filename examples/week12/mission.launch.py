"""巡回ミッションを1つのコマンドで起動する起動ファイル（第12回の演習）。

シミュレータ・自己位置推定・Nav2（course_robot の navigation.launch.py）と、
巡回のノード（week12 の mission）を、パラメータのファイルを付けて起動する。
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    course_share = get_package_share_directory('course_robot')
    week12_share = get_package_share_directory('week12')
    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params')

    return LaunchDescription([
        # 起動するときに map:=... で地図を変えられるようにする
        DeclareLaunchArgument(
            'map', default_value=os.path.expanduser('~/maps/week06.yaml'),
            description='使う地図の YAML ファイル'),
        # params:=... でパラメータのファイルを変えられるようにする
        DeclareLaunchArgument(
            'params', default_value=os.path.join(week12_share, 'config', 'mission.yaml'),
            description='巡回のノードのパラメータのファイル'),
        # 別の起動ファイルを取り込む
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(course_share, 'launch', 'navigation.launch.py')),
            launch_arguments={'map': map_file}.items(),
        ),
        # 自分のノードを、パラメータのファイルを付けて起動する
        Node(
            package='week12',
            executable='mission',
            name='mission',
            output='screen',
            parameters=[params_file],
        ),
    ])

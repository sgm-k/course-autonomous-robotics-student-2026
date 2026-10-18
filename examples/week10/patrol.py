"""Nav2 に、決めた地点を順に回らせるプログラム（第10回の演習）。

ナビゲーション（navigation.launch.py）を起動し、RViz2 ではじめの位置を教えてから動かす。
地点の座標は地図の座標 [m]（原点はスタート地点）。
"""

import math
import time

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy

# 回る地点 (x [m], y [m], 向き [度])。地図に合わせて変える
WAYPOINTS = [
    (0.7, 2.4, 0.0),     # 左上の部屋
    (3.5, 1.8, 0.0),     # 真ん中の部屋
    (0.0, 0.0, 0.0),     # スタート地点に戻る
]


def make_pose(navigator, x, y, yaw_deg):
    """地図の座標 (x, y) と向きから、目標の姿勢 PoseStamped を作る。"""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    yaw = math.radians(yaw_deg)
    pose.pose.orientation.z = math.sin(yaw / 2)   # 向きはクォータニオンで表す（第5回）
    pose.pose.orientation.w = math.cos(yaw / 2)
    return pose


def main():
    rclpy.init()
    navigator = BasicNavigator()
    navigator.waitUntilNav2Active(localizer='amcl')   # Nav2 の準備ができるまで待つ

    for i, (x, y, yaw) in enumerate(WAYPOINTS, start=1):
        print(f'地点 {i}：({x}, {y}) に向かう')
        start = time.time()
        navigator.goToPose(make_pose(navigator, x, y, yaw))
        while not navigator.isTaskComplete():
            feedback = navigator.getFeedback()
            if feedback:
                print(f'  残り {feedback.distance_remaining:.2f} m', end='\r')
            time.sleep(0.5)
        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print(f'地点 {i}：着いた（{time.time() - start:.1f} 秒）       ')
        else:
            print(f'地点 {i}：着けなかった（{result}）')
            break

    rclpy.shutdown()


if __name__ == '__main__':
    main()

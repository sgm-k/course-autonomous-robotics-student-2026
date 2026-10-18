"""巡回ミッションを、状態を切り替えながら進めるノード（第12回の演習）。

状態：はじめ → 地点に向かう → 着いた（次の地点へ）… → 終わり
地点と待ち時間は、パラメータのファイル（mission.yaml）から読む。
"""

import math
import time

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy
from rclpy.executors import ExternalShutdownException


def make_pose(navigator, x, y, yaw_deg):
    """地図の座標 (x, y) と向き [度] から PoseStamped を作る（第10回と同じ）。"""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(math.radians(yaw_deg) / 2)
    pose.pose.orientation.w = math.cos(math.radians(yaw_deg) / 2)
    return pose


class Mission:
    """状態を1つずつ切り替えて、巡回を進める（ステートマシン）。"""

    def __init__(self, navigator):
        self.nav = navigator
        navigator.declare_parameter('waypoints', [0.0, 0.0])  # x1, y1, x2, y2, ... [m]
        navigator.declare_parameter('wait_time', 1.0)         # 地点に着いてから待つ時間 [s]
        values = navigator.get_parameter('waypoints').value
        self.points = list(zip(values[0::2], values[1::2]))
        self.wait_time = navigator.get_parameter('wait_time').value
        self.index = 0
        self.reached = 0
        self.state = 'はじめ'
        self.start_time = time.time()

    def change(self, new_state):
        """状態を切り替え、記録に残す。"""
        self.nav.get_logger().info(f'状態：{self.state} → {new_state}')
        self.state = new_state

    def step(self):
        """今の状態に合わせて、1回分の仕事をする。終わったら False を返す。"""
        if self.state == 'はじめ':
            pose = make_pose(self.nav, 0.0, 0.0, 0.0)
            self.nav.setInitialPose(pose)                # はじめの位置を教える（RViz2 は使わない）
            self.nav.waitUntilNav2Active(localizer='amcl')
            self.change('地点に向かう')
        elif self.state == '地点に向かう':
            x, y = self.points[self.index]
            self.nav.get_logger().info(f'地点 {self.index + 1}/{len(self.points)}：({x}, {y})')
            self.nav.goToPose(make_pose(self.nav, x, y, 0.0))
            while not self.nav.isTaskComplete():
                time.sleep(0.2)
            if self.nav.getResult() == TaskResult.SUCCEEDED:
                self.reached += 1
                self.change('着いた')
            else:
                self.nav.get_logger().warn('着けなかった。次の地点に進む')
                self.change('次へ')
        elif self.state == '着いた':
            time.sleep(self.wait_time)
            self.change('次へ')
        elif self.state == '次へ':
            self.index += 1
            if self.index < len(self.points):
                self.change('地点に向かう')
            else:
                self.change('終わり')
        elif self.state == '終わり':
            self.nav.get_logger().info(
                f'巡回が終わった：{self.reached}/{len(self.points)} 地点、'
                f'{time.time() - self.start_time:.0f} 秒')
            return False
        return True


def main():
    rclpy.init()
    navigator = BasicNavigator()
    mission = Mission(navigator)
    try:
        while mission.step():
            pass
    except (KeyboardInterrupt, ExternalShutdownException):
        if rclpy.ok():
            navigator.cancelTask()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

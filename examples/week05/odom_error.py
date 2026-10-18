"""オドメトリと真値を比べて、ずれを表示するノード（第5回の課題）。

TODO の部分を書いて完成させる。
"""

import math

from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


def yaw_from_quaternion(q):
    """クォータニオン（向きの表し方）から、平面の向き yaw [rad] を求める。"""
    return 2.0 * math.atan2(q.z, q.w)


def normalize_angle(angle):
    """角度を -π から π の範囲に直す（例：350° → -10°）。"""
    return math.atan2(math.sin(angle), math.cos(angle))


def pose_error(odom, truth):
    """オドメトリと真値（どちらも (x, y, yaw)）のずれを、位置 [m] と向き [rad] で返す。"""
    distance = 0.0
    yaw = 0.0
    # TODO: 次の2つを計算して、distance と yaw に入れる。
    #   1. 位置のずれ：点 (odom[0], odom[1]) と点 (truth[0], truth[1]) の距離。math.hypot を使う
    #   2. 向きのずれ：odom[2] - truth[2] を normalize_angle で -π〜π に直したもの
    return distance, yaw


class OdomError(Node):
    """/odom と /base_pose_ground_truth を受け取り、1 秒ごとにずれを表示する。"""

    def __init__(self):
        super().__init__('odom_error')
        self.odom = None     # オドメトリ (x, y, yaw)
        self.truth = None    # 真値をスタート地点から見た (x, y, yaw)
        self.start = None    # スタート地点の真値 (x, y, yaw)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(
            Odometry, '/base_pose_ground_truth', self.truth_callback, 10)
        self.create_timer(1.0, self.timer_callback)

    def odom_callback(self, msg):
        p = msg.pose.pose
        self.odom = (p.position.x, p.position.y, yaw_from_quaternion(p.orientation))

    def truth_callback(self, msg):
        p = msg.pose.pose
        x, y, yaw = p.position.x, p.position.y, yaw_from_quaternion(p.orientation)
        if self.start is None:
            self.start = (x, y, yaw)  # 最初に届いた真値を、スタート地点とする
        # 真値は部屋の座標で届くので、オドメトリと同じ「スタート地点から見た座標」に直す
        x0, y0, yaw0 = self.start
        dx, dy = x - x0, y - y0
        self.truth = (math.cos(yaw0) * dx + math.sin(yaw0) * dy,
                      -math.sin(yaw0) * dx + math.cos(yaw0) * dy,
                      normalize_angle(yaw - yaw0))

    def timer_callback(self):
        if self.odom is None or self.truth is None:
            self.get_logger().info('データを待っている')
            return
        distance, yaw = pose_error(self.odom, self.truth)
        o, t = self.odom, self.truth
        self.get_logger().info(
            f'オドメトリ ({o[0]:5.2f}, {o[1]:5.2f}, {math.degrees(o[2]):6.1f}°)　'
            f'真値 ({t[0]:5.2f}, {t[1]:5.2f}, {math.degrees(t[2]):6.1f}°)　'
            f'ずれ {distance * 100:5.1f} cm {math.degrees(yaw):6.1f}°')


def main():
    rclpy.init()
    node = OdomError()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

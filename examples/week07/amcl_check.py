"""AMCL の推定とオドメトリを、真値と比べて表示するノード（第7回の演習）。"""

import math

from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node


def yaw_from_quaternion(q):
    """クォータニオンから、平面の向き yaw [rad] を求める。"""
    return 2.0 * math.atan2(q.z, q.w)


def normalize_angle(angle):
    """角度を -π から π の範囲に直す。"""
    return math.atan2(math.sin(angle), math.cos(angle))


def pose_error(a, b):
    """2つの (x, y, yaw) のずれを、位置 [m] と向き [rad] で返す（第5回の課題と同じ）。"""
    return math.hypot(a[0] - b[0], a[1] - b[1]), normalize_angle(a[2] - b[2])


def to_tuple(pose):
    """ROS 2 の Pose を (x, y, yaw) にする。"""
    return (pose.position.x, pose.position.y, yaw_from_quaternion(pose.orientation))


class AmclCheck(Node):
    """/amcl_pose、/odom、/base_pose_ground_truth を受け取り、1 秒ごとにずれを表示する。"""

    def __init__(self):
        super().__init__('amcl_check')
        self.amcl = None
        self.odom = None
        self.truth = None
        self.start = None
        self.create_subscription(
            PoseWithCovarianceStamped, '/amcl_pose', self.amcl_callback, 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(
            Odometry, '/base_pose_ground_truth', self.truth_callback, 10)
        self.create_timer(1.0, self.timer_callback)

    def amcl_callback(self, msg):
        self.amcl = to_tuple(msg.pose.pose)   # 地図の座標（原点はスタート地点）

    def odom_callback(self, msg):
        self.odom = to_tuple(msg.pose.pose)   # オドメトリの座標（原点はスタート地点）

    def truth_callback(self, msg):
        x, y, yaw = to_tuple(msg.pose.pose)
        if self.start is None:
            self.start = (x, y, yaw)
        # 真値は部屋の座標で届くので、スタート地点から見た座標に直す（第5回と同じ）
        x0, y0, yaw0 = self.start
        dx, dy = x - x0, y - y0
        self.truth = (math.cos(yaw0) * dx + math.sin(yaw0) * dy,
                      -math.sin(yaw0) * dx + math.cos(yaw0) * dy,
                      normalize_angle(yaw - yaw0))

    def timer_callback(self):
        if self.amcl is None or self.odom is None or self.truth is None:
            self.get_logger().info('データを待っている（RViz2 で 2D Pose Estimate をする）')
            return
        da, ya = pose_error(self.amcl, self.truth)
        do, yo = pose_error(self.odom, self.truth)
        self.get_logger().info(
            f'AMCL のずれ {da * 100:5.1f} cm {math.degrees(ya):6.1f}°　'
            f'オドメトリのずれ {do * 100:5.1f} cm {math.degrees(yo):6.1f}°')


def main():
    rclpy.init()
    node = AmclCheck()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

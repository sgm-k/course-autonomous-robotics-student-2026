"""正面 ±15° の距離の最小値と中央値を表示するノード（第4回の課題）。

TODO の部分を書いて完成させる。
"""

import math
from statistics import median

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

HALF_ANGLE_DEG = 15.0  # 正面から左右に何度までを調べるか [度]


def front_values(msg, half_angle):
    """正面 ±half_angle [rad] の中で、測れた距離だけをリストにして返す。"""
    values = []
    for i in range(len(msg.ranges)):
        angle = msg.angle_min + i * msg.angle_increment  # i 番目の光線の角度 [rad]
        distance = msg.ranges[i]                         # i 番目の光線の距離 [m]
        # TODO: 次の2つを両方満たすときだけ、values.append(distance) で加える。
        #   1. 角度が -half_angle 以上、half_angle 以下
        #   2. 距離が測れている（msg.range_min 以上、msg.range_max より小さい）
    return values


class FrontDistance(Node):
    """/laser1 を受け取り、正面の距離の最小値と中央値を表示する。"""

    def __init__(self):
        super().__init__('front_distance')
        self.sub = self.create_subscription(
            LaserScan, '/laser1', self.callback, 10)

    def callback(self, msg):
        values = front_values(msg, math.radians(HALF_ANGLE_DEG))
        if values:
            self.get_logger().info(
                f'光線 {len(values)} 本　最小値 {min(values):.2f} m　'
                f'中央値 {median(values):.2f} m')
        else:
            self.get_logger().info('正面に、測れる距離の物がない')


def main():
    rclpy.init()
    node = FrontDistance()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

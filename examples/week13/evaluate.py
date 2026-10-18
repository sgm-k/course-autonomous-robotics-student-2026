"""ロボットの走行を測るノード（第13回の課題）。

真値 /base_pose_ground_truth を受け取り、動き始めてから最後に止まるまでの
走行時間・走行距離・最高速度を測る。Ctrl+C を押すと、結果を表示して終わる。
TODO の部分（走行距離と最高速度）を書いて完成させる。
"""

import math

from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

MOVING_SPEED = 0.02   # これより速ければ「動いている」とみなす [m/s]


class Evaluate(Node):
    """真値から、走行時間・走行距離・最高速度を測る。"""

    def __init__(self):
        super().__init__('evaluate')
        self.prev = None          # 1つ前に届いた (時刻 [s], x, y)
        self.distance = 0.0       # 走行距離 [m]
        self.max_speed = 0.0      # 最高速度 [m/s]
        self.first_move = None    # 動き始めた時刻 [s]
        self.last_move = None     # 最後に動いていた時刻 [s]
        self.create_subscription(
            Odometry, '/base_pose_ground_truth', self.truth_callback, 10)
        self.create_timer(5.0, self.report)
        self.get_logger().info('測り始めた。終わったら Ctrl+C を押す')

    def truth_callback(self, msg):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        x, y = msg.pose.pose.position.x, msg.pose.pose.position.y
        if self.prev is not None:
            t0, x0, y0 = self.prev
            dt = t - t0
            if dt > 0.0:
                step = math.hypot(x - x0, y - y0)   # 前の位置から進んだ距離 [m]
                speed = step / dt                    # そのときの速さ [m/s]
                if speed > MOVING_SPEED:
                    if self.first_move is None:
                        self.first_move = t0
                    self.last_move = t
                    # TODO: 次の2つを書く。
                    #   1. 走行距離 self.distance に、step を足す
                    #   2. speed が self.max_speed より大きければ、self.max_speed を speed にする
        self.prev = (t, x, y)

    def result(self):
        """(走行時間 [s], 走行距離 [m], 最高速度 [m/s]) を返す。"""
        if self.first_move is None:
            return 0.0, 0.0, 0.0
        return self.last_move - self.first_move, self.distance, self.max_speed

    def report(self):
        time_s, dist, vmax = self.result()
        self.get_logger().info(f'ここまで：{time_s:.1f} 秒、{dist:.2f} m')


def main():
    rclpy.init()
    node = Evaluate()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    time_s, dist, vmax = node.result()
    print(f'走行時間 {time_s:.1f} s　走行距離 {dist:.2f} m　最高速度 {vmax:.3f} m/s')
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

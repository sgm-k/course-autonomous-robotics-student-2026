"""1辺 1 m の正方形を、時間で区切って走るノード（第5回の演習）。"""

import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

SIDE = 1.0           # 正方形の1辺 [m]
LINEAR_SPEED = 0.2   # 前に進む速さ [m/s]
ANGULAR_SPEED = 0.5  # 左に回る速さ [rad/s]


class SquareDrive(Node):
    """前進と 90° の左回りを4回くり返す。"""

    def __init__(self):
        super().__init__('square_drive')
        # パブリッシャを作る：型 Twist、トピック /cmd_vel
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        # タイマーを作る：0.1 秒ごとに self.timer_callback を呼ぶ
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.forward_time = SIDE / LINEAR_SPEED           # 1辺を進む時間 [s]
        self.turn_time = (math.pi / 2) / ANGULAR_SPEED    # 90° 回る時間 [s]
        self.step = 0          # 何番目の動きか（0, 2, 4, 6：前進　1, 3, 5, 7：回転）
        self.step_start = None
        self.finished = False

    def timer_callback(self):
        """0.1 秒ごとに呼ばれ、今の動きに合わせた速度指令を送る。"""
        if self.pub.get_subscription_count() == 0:
            return  # シミュレータとつながるまで待つ
        now = self.get_clock().now()
        if self.step_start is None:
            self.step_start = now
            self.get_logger().info('正方形を走り始める')
        elapsed = (now - self.step_start).nanoseconds / 1e9

        msg = Twist()
        if self.step >= 8:
            self.finished = True                 # 4辺を走り終えた。速度 0 を送る
        elif self.step % 2 == 0:                 # 前進
            if elapsed < self.forward_time:
                msg.linear.x = LINEAR_SPEED
            else:
                self.next_step(now)
        else:                                    # その場で左に 90° 回る
            if elapsed < self.turn_time:
                msg.angular.z = ANGULAR_SPEED
            else:
                self.next_step(now)
        self.pub.publish(msg)

    def next_step(self, now):
        """次の動きに進む。"""
        self.step += 1
        self.step_start = now
        self.get_logger().info(f'動き {self.step} / 8 が終わった')


def main():
    rclpy.init()
    node = SquareDrive()
    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    if rclpy.ok():
        node.pub.publish(Twist())  # 最後に止める
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

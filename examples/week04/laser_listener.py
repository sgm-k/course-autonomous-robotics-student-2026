"""LiDAR が測った正面の距離を表示するノード（第4回の演習）。"""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LaserListener(Node):
    """/laser1 を受け取り、正面（角度 0）の距離を表示する。"""

    def __init__(self):
        super().__init__('laser_listener')  # ノード名
        # サブスクライバを作る：型 LaserScan、トピック /laser1。
        # データが届くたびに self.callback が呼ばれる。
        self.sub = self.create_subscription(
            LaserScan, '/laser1', self.callback, 10)

    def callback(self, msg):
        """1回分のスキャンが届くたびに呼ばれる。"""
        # 角度 0（正面）が、ranges の何番目にあたるかを計算する。
        index = round((0.0 - msg.angle_min) / msg.angle_increment)
        front = msg.ranges[index]
        self.get_logger().info(f'正面の距離: {front:.2f} m')


def main():
    rclpy.init()
    node = LaserListener()
    try:
        rclpy.spin(node)  # Ctrl+C を押すまで、callback を呼び続ける
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

"""決めた経路に沿って走るノード（Pure Pursuit、第11回の課題）。

経路は、スタート地点から見た座標（オドメトリの座標）で、1辺 1 m の正方形を左回りに1周する。
TODO の部分（曲がり具合と、回る速さの計算）を書いて完成させる。
"""

import math

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


def make_path(step=0.05):
    """1辺 1 m の正方形の経路を、step [m] ごとの点のリストにする。"""
    corners = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]
    path = []
    for (x0, y0), (x1, y1) in zip(corners, corners[1:]):
        n = int(round(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n):
            path.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    path.append(corners[-1])
    return path


def yaw_from_quaternion(q):
    return 2.0 * math.atan2(q.z, q.w)


class PurePursuit(Node):
    """/odom を受け取り、経路上の少し先の点に向かうように /cmd_vel を送る。"""

    def __init__(self):
        super().__init__('pure_pursuit')
        self.declare_parameter('speed', 0.15)       # 前に進む速さ [m/s]
        self.declare_parameter('lookahead', 0.3)    # どれだけ先の点を目指すか [m]
        self.speed = self.get_parameter('speed').value
        self.lookahead = self.get_parameter('lookahead').value
        self.path = make_path()
        self.index = 0           # 経路のどこまで進んだか（いちばん近い点の番号）
        self.pose = None
        self.errors = []         # 経路からのずれ [m] の記録
        self.finished = False
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_timer(0.1, self.timer_callback)
        self.get_logger().info(f'speed={self.speed} m/s, lookahead={self.lookahead} m')

    def odom_callback(self, msg):
        p = msg.pose.pose
        self.pose = (p.position.x, p.position.y, yaw_from_quaternion(p.orientation))

    def timer_callback(self):
        if self.pose is None or self.finished:
            return
        x, y, yaw = self.pose
        # いちばん近い点を、今の点から少し先までの間で探す（後ろには戻らない）
        window = range(self.index, min(self.index + 20, len(self.path)))
        self.index = min(window, key=lambda i: math.hypot(self.path[i][0] - x, self.path[i][1] - y))
        nearest = self.path[self.index]
        self.errors.append(math.hypot(nearest[0] - x, nearest[1] - y))
        if self.index >= len(self.path) - 1:
            self.finish()
            return
        # 目指す点：いちばん近い点から、経路に沿って lookahead だけ先の点
        target = self.path[-1]
        for i in range(self.index, len(self.path)):
            if math.hypot(self.path[i][0] - x, self.path[i][1] - y) >= self.lookahead:
                target = self.path[i]
                break
        # 目指す点を、ロボットから見た座標（前が x、左が y）に直す
        dx, dy = target[0] - x, target[1] - y
        tx = math.cos(yaw) * dx + math.sin(yaw) * dy
        ty = -math.sin(yaw) * dx + math.cos(yaw) * dy
        msg = Twist()
        msg.linear.x = self.speed
        # TODO: Pure Pursuit で、回る速さ msg.angular.z を決める。
        #   1. 曲がり具合（曲率）curvature = 2 × ty ÷ L²。L は目指す点までの距離で、math.hypot(tx, ty)
        #   2. 回る速さ msg.angular.z = 前に進む速さ × curvature
        self.pub.publish(msg)

    def finish(self):
        self.pub.publish(Twist())
        self.finished = True
        mean = sum(self.errors) / len(self.errors)
        self.get_logger().info(
            f'1周した。経路からのずれ：平均 {mean * 100:.1f} cm、最大 {max(self.errors) * 100:.1f} cm')


def main():
    rclpy.init()
    node = PurePursuit()
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

"""前に進み、正面に物が近づいたら止まるノード（第8回の課題）。

TODO の部分を書いて完成させる。
"""

import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


def front_min(msg, half_angle):
    """正面 ±half_angle [rad] の中で、測れた距離の最小値を返す。なければ None（第4回の課題と同じ考え方）。"""
    values = []
    for i in range(len(msg.ranges)):
        angle = msg.angle_min + i * msg.angle_increment
        distance = msg.ranges[i]
        if -half_angle <= angle <= half_angle and msg.range_min <= distance < msg.range_max:
            values.append(distance)
    if values:
        return min(values)
    return None


class ObstacleStop(Node):
    """/laser1 を受け取り、/cmd_vel に速度指令を送る（受け取って送るノード）。"""

    def __init__(self):
        super().__init__('obstacle_stop')
        # パラメータを宣言する。--ros-args -p 名前:=値 で変えられる
        self.declare_parameter('speed', 0.15)          # 前に進む速さ [m/s]
        self.declare_parameter('stop_distance', 0.5)   # これより近づいたら止まる [m]
        self.declare_parameter('half_angle_deg', 20.0) # 正面から左右に何度まで見るか [度]
        self.speed = self.get_parameter('speed').value
        self.stop_distance = self.get_parameter('stop_distance').value
        self.half_angle = math.radians(self.get_parameter('half_angle_deg').value)

        self.front = None        # 正面の物までの距離 [m]。測れないときは None
        self.no_data = True      # まだ /laser1 が届いていない
        self.create_subscription(LaserScan, '/laser1', self.scan_callback, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_timer(0.1, self.timer_callback)
        self.get_logger().info(
            f'speed={self.speed} m/s, stop_distance={self.stop_distance} m')

    def scan_callback(self, msg):
        self.front = front_min(msg, self.half_angle)
        self.no_data = False

    def timer_callback(self):
        msg = Twist()
        # TODO: 次の決まりで msg.linear.x（前に進む速さ）を決める。
        #   1. まだ /laser1 が届いていない（self.no_data が True）なら、0.0（止まる）
        #   2. 正面に物があり（self.front が None でない）、self.front が self.stop_distance より小さいなら、0.0
        #   3. それ以外なら、self.speed
        self.pub.publish(msg)
        front = '3.5 m より遠い' if self.front is None else f'{self.front:.2f} m'
        self.get_logger().info(f'正面 {front}　速さ {msg.linear.x:.2f} m/s',
                               throttle_duration_sec=1.0)


def main():
    rclpy.init()
    node = ObstacleStop()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    if rclpy.ok():
        node.pub.publish(Twist())  # 最後に止める
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()

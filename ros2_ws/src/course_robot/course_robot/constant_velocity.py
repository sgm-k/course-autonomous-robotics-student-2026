"""Publish a velocity command for a limited time, then stop the robot."""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class ConstantVelocity(Node):
    """A small publisher used in the ROS 2 fundamentals lesson."""

    def __init__(self) -> None:
        super().__init__('constant_velocity')
        self.declare_parameter('linear_speed', 0.15)
        self.declare_parameter('angular_speed', 0.0)
        self.declare_parameter('duration', 3.0)

        self.linear_speed = float(
            self.get_parameter('linear_speed').value)
        self.angular_speed = float(
            self.get_parameter('angular_speed').value)
        self.duration = float(self.get_parameter('duration').value)

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        # Start timing only after the simulator has subscribed to /cmd_vel.
        # Otherwise the first commands are lost while ROS 2 is connecting,
        # and the robot moves for less than `duration` seconds.
        self.start_time = None
        self.finished = False
        self.timer = self.create_timer(0.1, self.publish_command)

    def publish_command(self) -> None:
        """Publish motion until duration elapses, then publish zero velocity."""
        if self.start_time is None:
            if self.publisher.get_subscription_count() == 0:
                return
            self.start_time = self.get_clock().now()
            self.get_logger().info(
                f'start: linear_speed={self.linear_speed} m/s, '
                f'angular_speed={self.angular_speed} rad/s, '
                f'duration={self.duration} s')
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        command = Twist()

        if elapsed < self.duration:
            command.linear.x = self.linear_speed
            command.angular.z = self.angular_speed
        else:
            self.finished = True

        self.publisher.publish(command)

    def stop(self) -> None:
        """Publish a final zero-velocity command."""
        self.publisher.publish(Twist())


def main(args=None) -> None:
    """Run the node until motion duration ends or the user interrupts it."""
    rclpy.init(args=args)
    node = ConstantVelocity()
    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.1)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.stop()
            rclpy.spin_once(node, timeout_sec=0.1)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

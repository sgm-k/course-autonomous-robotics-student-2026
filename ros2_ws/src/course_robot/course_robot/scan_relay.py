"""Relay MVSim LaserScan messages with ROS wall-clock timestamps."""

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class ScanRelay(Node):
    """Publish time-aligned scans for SLAM and Nav2 consumers."""

    def __init__(self) -> None:
        super().__init__('scan_relay')
        self.publisher = self.create_publisher(
            LaserScan, '/scan', qos_profile_sensor_data)
        self.subscription = self.create_subscription(
            LaserScan, '/laser1', self.relay, qos_profile_sensor_data)

    def relay(self, message: LaserScan) -> None:
        """Replace the simulator stamp and republish the scan."""
        message.header.stamp = self.get_clock().now().to_msg()
        self.publisher.publish(message)


def main(args=None) -> None:
    """Run the scan relay until interrupted."""
    rclpy.init(args=args)
    node = ScanRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

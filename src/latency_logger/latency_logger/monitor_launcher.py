import rclpy
from rclpy.node import Node
import subprocess


class MonitorLauncher(Node):
    def __init__(self):
        super().__init__('monitor_launcher')
        self.get_logger().info('Starting all loggers...')

        subprocess.Popen(['ros2', 'run', 'latency_logger', 'jetson_logger'])
        subprocess.Popen(['ros2', 'run', 'latency_logger', 'data_logger'])
        subprocess.Popen(['ros2', 'run', 'latency_logger', 'obstacle_logger'])

        self.get_logger().info('All loggers started!')


def main(args=None):
    rclpy.init(args=args)
    node = MonitorLauncher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Stop')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
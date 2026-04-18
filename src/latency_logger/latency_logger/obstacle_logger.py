import rclpy
from rclpy.node import Node
from mavros_msgs.msg import ObstacleDistance3D
from sensor_msgs.msg import PointCloud2 as pc2


import csv
import os
from datetime import datetime


class ObstacleLogger(Node):
    def __init__(self):
        super().__init__('obstacle_logger')

        log_dir = os.path.join(os.getcwd(), 'obstacle_logs')
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_path = os.path.join(log_dir, f'obstacles_{timestamp}.csv')

        self.csv_file = open(log_path, 'w', newline='')
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(['timestamp', 'x', 'y', 'z'])

        self.get_logger().info(f'Logging obstacles to: {log_path}')

        self.subscription = self.create_subscription(
            PointCloud2,
            '/merged_cloud/obstacles',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        
        for point in pc2.read_points(msg, field_names = ('x', 'y', 'z'), skip_nans=True):
            x, y, z = point
            self.writer.writerow([timestamp, x, y, z])
            self.csv_file.flush()
            self.get_logger().info(f'Logged -> x: {x:.3f}, y: {y:.3f}, z: {z:.3f}')         

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleLogger()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('end')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

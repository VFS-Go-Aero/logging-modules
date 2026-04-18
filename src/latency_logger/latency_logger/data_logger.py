import os
import subprocess
import threading
import time
from datetime import datetime

import rclpy
from rclpy.node import Node

LATENCY_LOGS_DIR = os.path.expanduser('~/ros2_ws/latency_logs')

HZ_TIME = 10

os.makedirs(LATENCY_LOGS_DIR, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


LOG_FILE = os.path.join(LATENCY_LOGS_DIR, f"data_log_{TIMESTAMP}.csv")


class DataLoggerNode(Node):

    def __init__(self):
        super().__init__('data_logger')
        self.get_logger().info("Logger started.")
        self.get_logger().info(f"Saving to: {LOG_FILE}")
        
        with open(LOG_FILE, "w") as f:
            f.write("Timestamp,Topic,Rate(Hz)\n")
        
        thread = threading.Thread(target=self.run_loop, daemon=True)
        thread.start()

    def run_loop(self):
        while True:
            self.timer_callback()

    def log_row(self, timestamp, topic, rate):
     
        row = f"{timestamp},{topic},{rate}"
        print(f"Logged: {row}")
        with open(LOG_FILE, "a") as f:
            f.write(row + "\n")

    def get_topics(self):
        try:
            result = subprocess.run(
                "ros2 topic list | grep /merged", shell=True, check=True,
                capture_output=True, text=True, timeout=10
            )
            topics_raw = result.stdout
            if not topics_raw:
                return []
            return [t for t in topics_raw.splitlines() if t.strip()]
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return []

    def get_topic_rate(self, topic):
        try:
            proc = subprocess.Popen(
                ["ros2", "topic", "hz", topic],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            try:
                stdout, _ = proc.communicate(timeout=HZ_TIME)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, _ = proc.communicate()

            for line in stdout.splitlines():
                if "average rate:" in line:
                    try:
                        return f"{float(line.split('average rate:')[1].strip()):.2f}"
                    except ValueError:
                        pass
            return "0.0"

        except Exception as e:
            self.get_logger().warn(f"hz failed for {topic}: {e}")
            return "0.0"

    def timer_callback(self):
        topics = self.get_topics()
        
        if not topics:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_row(timestamp, "NO_TOPICS_FOUND", "0.0")
            return

        for topic in topics:
            rate = self.get_topic_rate(topic)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_row(timestamp, topic, rate)


def main(args=None):
    rclpy.init(args=args)
    node = DataLoggerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nLogger stopped.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
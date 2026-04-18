import os
import subprocess
import threading
import time
from datetime import datetime

import rclpy
from rclpy.node import Node

import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

LATENCY_LOGS_DIR = os.path.expanduser('~/ros2_ws/latency_logs')

HZ_TIME = 10

os.makedirs(LATENCY_LOGS_DIR, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

LOG_FILE = os.path.join(LATENCY_LOGS_DIR, f"data_log_{TIMESTAMP}.csv")
GRAPH_FILE = os.path.join(LATENCY_LOGS_DIR, f"data_graph_{TIMESTAMP}.png")


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

    def generate_graph(self):
        # Read CSV
        topic_data = defaultdict(lambda: {'timestamps': [], 'rates': []})

        try:
            with open(LOG_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    topic = row['Topic']
                    if topic == 'NO_TOPICS_FOUND':
                        continue
                    try:
                        ts = datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S')
                        rate = float(row['Rate(Hz)'])
                        topic_data[topic]['timestamps'].append(ts)
                        topic_data[topic]['rates'].append(rate)
                    except (ValueError, KeyError):
                        continue
        except FileNotFoundError:
            print(f"Log file not found: {LOG_FILE}")
            return

        if not topic_data:
            print("No valid topic data to graph.")
            return

        # One subplot per topic
        n = len(topic_data)
        fig, axes = plt.subplots(n, 1, figsize=(12, 4 * n), sharex=True)
        if n == 1:
            axes = [axes]

        fig.suptitle(f'Topic Publish Rates — {TIMESTAMP}', fontsize=14, fontweight='bold')

        for ax, (topic, data) in zip(axes, topic_data.items()):
            timestamps = data['timestamps']
            rates = data['rates']

            ax.plot(timestamps, rates, linewidth=1.5, marker='o', markersize=3, label=topic)
            ax.fill_between(timestamps, rates, alpha=0.15)
            ax.set_ylabel('Rate (Hz)', fontsize=10)
            ax.set_title(topic, fontsize=10, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.set_ylim(bottom=0)

            # Annotate mean
            mean_rate = sum(rates) / len(rates)
            ax.axhline(mean_rate, color='red', linestyle='--', linewidth=1, alpha=0.7)
            ax.text(
                timestamps[-1], mean_rate,
                f' mean: {mean_rate:.2f} Hz',
                va='bottom', ha='right', fontsize=8, color='red'
            )

        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate(rotation=30)

        plt.tight_layout()
        plt.savefig(GRAPH_FILE, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Graph saved to: {GRAPH_FILE}")


def main(args=None):
    rclpy.init(args=args)
    node = DataLoggerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nLogger stopped.")
    finally:
        print("Generating graph...")
        node.generate_graph()
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
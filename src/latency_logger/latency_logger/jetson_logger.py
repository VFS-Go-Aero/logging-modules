import os
import re
import subprocess
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import rclpy
from rclpy.node import Node

LOG_DIR = os.path.expanduser("~/ros2_ws/tegrastats_logs")
os.makedirs(LOG_DIR, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"tegrastats_{TIMESTAMP}.log")
GRAPH_FILE = os.path.join(LOG_DIR, f"tegrastats_{TIMESTAMP}.png")


def parse_log(log_file):
    data = {"cpu": [], "gpu": [], "ram": [], "cpu_temp": [], "gpu_temp": []}

    with open(log_file, "r") as f:
        for line in f:
            cpu = re.search(r"CPU \[([^\]]+)\]", line)
            if cpu:
                cores = re.findall(r"(\d+)%@\d+", cpu.group(1))
                if cores:
                    avg = sum(int(c) for c in cores) / len(cores)
                    data["cpu"].append(round(avg, 1))

            gpu = re.search(r"GR3D_FREQ (\d+)%", line)
            if gpu:
                data["gpu"].append(int(gpu.group(1)))

            ram = re.search(r"RAM (\d+)/(\d+)MB", line)
            if ram:
                pct = round(int(ram.group(1)) / int(ram.group(2)) * 100, 1)
                data["ram"].append(pct)

            cpu_temp = re.search(r"cpu@([\d.]+)C", line)
            if cpu_temp:
                data["cpu_temp"].append(float(cpu_temp.group(1)))

            gpu_temp = re.search(r"gpu@([\d.]+)C", line)
            if gpu_temp:
                data["gpu_temp"].append(float(gpu_temp.group(1)))

    return data


def save_graphs(log_file, graph_file):
    print("Generating graphs...")
    data = parse_log(log_file)

    fig, axes = plt.subplots(4, 1, figsize=(12, 16))
    fig.suptitle(f"Tegrastats Report\n{TIMESTAMP}", fontsize=14)

    axes[0].plot(data["cpu"], color="#378ADD", linewidth=1)
    axes[0].set_title("CPU Usage (%)")
    axes[0].set_ylim(0, 100)
    axes[0].set_ylabel("%")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(data["gpu"], color="#1D9E75", linewidth=1)
    axes[1].set_title("GPU Usage (%)")
    axes[1].set_ylim(0, 100)
    axes[1].set_ylabel("%")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(data["ram"], color="#D85A30", linewidth=1)
    axes[2].set_title("RAM Usage (%)")
    axes[2].set_ylim(0, 100)
    axes[2].set_ylabel("%")
    axes[2].grid(True, alpha=0.3)

    axes[3].plot(data["cpu_temp"], color="#378ADD", linewidth=1, label="CPU")
    axes[3].plot(data["gpu_temp"], color="#1D9E75", linewidth=1, label="GPU")
    axes[3].set_title("Temperatures (C)")
    axes[3].set_ylabel("C")
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)

    for ax in axes:
        ax.set_xlabel("Sample")

    plt.tight_layout()
    plt.savefig(graph_file, dpi=150)
    plt.close()
    print(f"Graph saved to: {graph_file}")


class TegrastatsNode(Node):
    def __init__(self):
        super().__init__('jetson_logger')
        self.get_logger().info(f"Saving to: {LOG_FILE}")
        self.process = subprocess.Popen(
            ["tegrastats", "--interval", "100", "--logfile", LOG_FILE]
        )

    def stop(self):
        self.process.terminate()
        self.process.wait()


def main(args=None):
    rclpy.init(args=args)
    node = TegrastatsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass
        save_graphs(LOG_FILE, GRAPH_FILE)


if __name__ == "__main__":
    main()
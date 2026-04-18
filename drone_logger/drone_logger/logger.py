import os
import time
import rclpy
import numpy as np
import pandas as pd
import psutil
import pynvml

from rclpy.node import Node
from codecarbon import EmissionTracker


class Logger(Node):
    def __init__(self):
        super().__init__("logger")
        self.get_logger().info("logger node initialized")

        self._log = pd.DataFrame(columns=[
            "timestamp",
            "cpu_percent_usage",
            "cpu_core_usage",
            "ram_percent_usage",
            "ram_total_usage",
            "gpu_usage",
            "gpu_percent_memory_usage",
            "gpu_total_memory_usage"
        ])

        self._tracker = EmissionTracker(save_to_file=False, logging_levels="error")

        pynvml.nvmlInit()
        self._gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        self._gpu_info = pynvml.nvmlDeviceGetMemoryInfo(self._gpu_handle)
        self._gpu_util = pynvml.nvmlDeviceGetUtilizationRates(self._gpu_handle)
        self._gpu_total = self._gpu_info.total // (1024 ** 2)  # Convert bytes to MB

        self._ram = psutil.virtual_memory()
        self._ram_total = self._ram.total // (1024 ** 2)  # Convert bytes to MB

    def get_log_entry(self):
        cpu_percent_usage = psutil.cpu_percent()
        cpu_core_usage = psutil.cpu_percent(logical=True)

        ram_percent_usage = self._ram.percent
        ram_total_usage = self._ram.used // (1024 ** 2)  # Convert bytes to MB

        gpu_usage = self._gpu_util.gpu
        gpu_percent_memory_usage = (self._gpu_info.used / self._gpu_total) * 100  # Percentage
        gpu_total_memory_usage = self._gpu_info.used // (1024 ** 2)  # Convert bytes to MB

        total_power_draw = self._tracker._measure_current_and_energy()._total_power_w

        return cpu_percent_usage, cpu_core_usage, ram_percent_usage, ram_total_usage, gpu_usage, gpu_percent_memory_usage, gpu_total_memory_usage, total_power_draw
    
    def log(self):
        timestamp = time.time()
        log_entry = self.get_log_entry()
        self._log.loc[len(self._log)] = [timestamp] + list(log_entry)
        self.get_logger().info(f"Logged data at {timestamp}")
    
    def save_log(self, path="~/ros2_ws/drone_logs", filename=None):
        if not os.path.exists(path):
            os.makedirs(path)
        if filename is None:
            filename = f"drone_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        self._log.to_csv(os.path.join(path, filename), index=False)
        self.get_logger().info(f"Log saved to {filename}")
        self._tracker.stop()
        self.get_logger().info("Power tracker stopped")


def main():
    rclpy.init()
    node = Logger()
    rclpy.spin(node)
    node.save_log()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

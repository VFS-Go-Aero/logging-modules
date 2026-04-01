import os

from setuptools import setup

package_name = "drone_logger"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name), ["launch/drone_logger_launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Vertical Flight Systems Purdue",
    maintainer_email="vfspurd@purdue.edu",
    description="Minimal ROS 2 package for drone logging.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "drone_logger_node = drone_logger.drone_logger_node:main",
        ],
    },
    url="https://github.com/Vertical-Flight-Systems-Purdue/drone-logger"
)
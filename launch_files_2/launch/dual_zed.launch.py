from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # ZED 1 (USB ID or S/N sets which camera it picks)
    zed1 = Node(
        package="zed_wrapper",
        executable="zed_wrapper",
        namespace="zed1",
        name="zed1",
        parameters=[{
            "general": {
                "camera_name": "zed1",
                "serial_number": 44659546,    # <--- put S/N or leave 0 for auto
            }
        }]
    )

    # ZED 2
    zed2 = Node(
        package="zed_wrapper",
        executable="zed_wrapper",
        namespace="zed2",
        name="zed2",
        parameters=[{
            "general": {
                "camera_name": "zed2",
                "serial_number": 42203370,    # <--- change this to second camera S/N
            }
        }]
    )

    return LaunchDescription([zed1, zed2])

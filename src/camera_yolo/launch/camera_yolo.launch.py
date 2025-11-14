from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        # ------------------------------------------------------------
        # 1. CAMERA NODE
        # ------------------------------------------------------------
        Node(
            package="camera_yolo",
            executable="camera_node",
            name="camera_node",
            output="screen",
        ),

        # ------------------------------------------------------------
        # 2. YOLO NODE (subscribes to /camera/raw_frame)
        # ------------------------------------------------------------
        Node(
            package="camera_yolo",
            executable="yolo_node",
            name="yolo_node",
            output="screen",
        ),
    ])

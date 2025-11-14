from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os

def generate_launch_description():

    pkg_arduino = os.path.join(
        get_package_share_directory('arduino_interface'),
        'launch',
        'arduino.launch.py'
    )

    pkg_camera = os.path.join(
        get_package_share_directory('camera_yolo'),
        'launch',
        'camera_yolo.launch.py'
    )

    pkg_robot = os.path.join(
        get_package_share_directory('robot_control'),
        'launch',
        'robot_control.launch.py'
    )

    return LaunchDescription([

        # ----------------------------------------------------------
        # 1. Arduino Serial Node (auto-detects serial port)
        # ----------------------------------------------------------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(pkg_arduino)
        ),

        # ----------------------------------------------------------
        # 2. Camera + YOLO Pipeline
        # ----------------------------------------------------------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(pkg_camera)
        ),

        # ----------------------------------------------------------
        # 3. Motion Control Services
        # ----------------------------------------------------------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(pkg_robot)
        ),
    ])


# Required import placed here (ROS2 prefers this pattern)
from ament_index_python.packages import get_package_share_directory
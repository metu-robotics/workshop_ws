from launch import LaunchDescription
from launch_ros.actions import Node


ARDUINOPORT = '/dev/ttyCH341USB0'  # modify as needed

def generate_launch_description():
    port = ARDUINOPORT
    return LaunchDescription([
        # ------------------------------------------------------------
        # Start the Arduino serial interface node
        # ------------------------------------------------------------
        Node(
            package="arduino_interface",
            executable="serial_node",
            name="arduino_serial_node",
            output="screen",
            parameters=[
                {"port": port},
                {"baudrate": 115200}
            ]
        ),
    ])

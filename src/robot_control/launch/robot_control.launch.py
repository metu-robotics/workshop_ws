from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package="robot_control",
            executable="robot_control_node",
            name="robot_control",
            output="screen",

            # Parameters for easy tuning
            parameters=[
                {"forward_speed": 0.7},
                {"backward_speed": -0.7},
                {"turn_speed": 2.0},
                {"move_duration": 1.0},
            ]
        )
    ])

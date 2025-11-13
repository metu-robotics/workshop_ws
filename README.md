# ROS2 Robot Workshop Project

This repository contains the complete ROS2 project used for the METU NCC Robotics Society workshops.

## Packages
- **arduino_interface** — Communication with Arduino (motors, ultrasonic sensor, buzzer)
- **camera_yolo** — Camera capture and YOLO-based object detection
- **robot_control** — High-level decision making & behavior logic
- **demo_launch** — Combined bringup launch files

## Workspace
Clone inside `~/workshop_ws` or build using:
```bash
cd ~/workshop_ws
colcon build
source install/setup.bash
```

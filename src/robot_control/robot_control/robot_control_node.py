#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger
import threading
import time


class RobotControlNode(Node):
    def __init__(self):
        super().__init__("robot_control")

        self.declare_parameter("move_duration", 1.0)
        self.declare_parameter("forward_speed", 0.7)
        self.declare_parameter("backward_speed", -0.7)
        self.declare_parameter("turn_speed", 2.0)

        # ---------------------------------------------------------
        # Publisher
        # ---------------------------------------------------------
        self.cmd_pub = self.create_publisher(Twist, "cmd_vel", 10)

        # ---------------------------------------------------------
        # Services
        # ---------------------------------------------------------
        self.create_service(Trigger, "move_forward", self.move_forward)
        self.create_service(Trigger, "move_backward", self.move_backward)
        self.create_service(Trigger, "turn_left", self.turn_left)
        self.create_service(Trigger, "turn_right", self.turn_right)
        self.create_service(Trigger, "stop", self.stop_now)

        self.get_logger().info("RobotControlNode is ready")

    # =================================================================
    # INTERNAL HELPERS
    # =================================================================
    def _publish_cmd(self, lin_x=0.0, ang_z=0.0):
        msg = Twist()
        msg.linear.x = lin_x
        msg.angular.z = ang_z
        self.cmd_pub.publish(msg)

    def _perform_motion(self, lin_x, ang_z):
        duration = float(self.get_parameter("move_duration").value)

        # Movement
        self._publish_cmd(lin_x, ang_z)

        # Run timer in background
        t = threading.Thread(target=self._stop_after, args=(duration,))
        t.daemon = True
        t.start()

    def _stop_after(self, duration):
        time.sleep(duration)
        self._publish_cmd(0.0, 0.0)

    # =================================================================
    # SERVICE HANDLERS
    # =================================================================
    def move_forward(self, request, response):
        speed = float(self.get_parameter("forward_speed").value)
        self._perform_motion(speed, 0.0)
        response.success = True
        response.message = "Moving forward"
        return response

    def move_backward(self, request, response):
        speed = float(self.get_parameter("backward_speed").value)
        self._perform_motion(speed, 0.0)
        response.success = True
        response.message = "Moving backward"
        return response

    def turn_left(self, request, response):
        speed = float(self.get_parameter("turn_speed").value)
        self._perform_motion(0.0, speed)
        response.success = True
        response.message = "Turning left"
        return response

    def turn_right(self, request, response):
        speed = float(self.get_parameter("turn_speed").value)
        self._perform_motion(0.0, -speed)
        response.success = True
        response.message = "Turning right"
        return response

    def stop_now(self, request, response):
        self._publish_cmd(0.0, 0.0)
        response.success = True
        response.message = "Stopped"
        return response


def main():
    rclpy.init()
    node = RobotControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

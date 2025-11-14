#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
from robot_interfaces.srv import Buzz
import serial
import threading
import time

class ArduinoInterfaceNode(Node):
    def __init__(self):
        super().__init__('arduino_interface')

        self.declare_parameter("port")
        self.declare_parameter("baudrate")


        # ---------------------------------------------------------
        # Publishers
        # ---------------------------------------------------------
        self.dist_pub = self.create_publisher(Float32, 'distance', 10)

        # ---------------------------------------------------------
        # Subscribers
        # ---------------------------------------------------------
        self.create_subscription(Twist, 'cmd_vel', self.cmd_vel_callback, 10)

        # ---------------------------------------------------------
        # Service: /buzz
        # ---------------------------------------------------------
        self.buzz_srv = self.create_service(Buzz, 'buzz', self.buzz_service)

        # ---------------------------------------------------------
        # Serial connection (Jetson CH341 clone port)
        # ---------------------------------------------------------
        port = self.get_parameter("port").get_parameter_value().string_value
        baud = self.get_parameter("baudrate").get_parameter_value().integer_value

        try:
            self.ser = serial.Serial(port, baud, timeout=0.1)
            time.sleep(2.0)  # allow Arduino auto-reset
            self.get_logger().info(f"[OK] Connected to Arduino on {port}")
        except Exception as e:
            self.get_logger().error(f"[ERROR] Cannot open {port}: {e}")
            raise SystemExit

        # ---------------------------------------------------------
        # Serial reader thread
        # ---------------------------------------------------------
        self.running = True
        self.reader_thread = threading.Thread(target=self.serial_reader)
        self.reader_thread.daemon = True
        self.reader_thread.start()

    # =============================================================
    # SERIAL READER (Arduino → Jetson)
    # =============================================================
    def serial_reader(self):
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    raw = self.ser.readline().decode('utf-8', 'ignore').strip()

                    # Expected format:  DIST:<value>
                    if raw.startswith("DIST:"):
                        try:
                            value = float(raw[5:])
                            msg = Float32()
                            msg.data = value
                            self.dist_pub.publish(msg)
                        except ValueError:
                            pass  # skip malformed values

            except Exception as e:
                self.get_logger().error(f"Serial read error: {e}")

            time.sleep(0.01)

    # =============================================================
    # SERIAL WRITE (Jetson → Arduino)
    # =============================================================
    def send_to_arduino(self, text: str):
        """Send a line-terminated string to the Arduino."""
        try:
            self.ser.write((text + "\n").encode('utf-8'))
        except Exception as e:
            self.get_logger().error(f"Serial write error: {e}")

    # =============================================================
    # /cmd_vel callback
    # -------------------------------------------------------------
    # Converts linear + angular velocities to:
    #     CMDVEL:<lin>,<ang>
    # =============================================================
    def cmd_vel_callback(self, msg: Twist):
        lin = msg.linear.x
        ang = msg.angular.z

        cmd = f"CMDVEL:{lin:.3f},{ang:.3f}"
        self.send_to_arduino(cmd)

    # =============================================================
    # /buzz service
    # -------------------------------------------------------------
    # Request:
    #     duration (float)
    #
    # Behavior:
    #     - Turn buzz ON via "BUZZER:1"
    #     - Wait <duration> seconds in another thread
    #     - Turn buzz OFF via "BUZZER:0"
    #
    # Non-blocking for the ROS thread.
    # =============================================================
    def buzz_service(self, request, response):
        duration = max(0.05, float(request.duration))  # avoid 0 sec

        self.get_logger().info(f"Buzz requested for {duration:.2f} seconds")

        # BUZZ ON
        self.send_to_arduino("BUZZER:1")

        # Timer thread
        t = threading.Thread(target=self._buzz_timer, args=(duration,))
        t.daemon = True
        t.start()

        response.success = True
        return response

    def _buzz_timer(self, duration: float):
        time.sleep(duration)
        self.send_to_arduino("BUZZER:0")

    # =============================================================
    # Shutdown cleanup
    # =============================================================
    def destroy_node(self):
        self.running = False
        time.sleep(0.1)
        if self.ser and self.ser.is_open:
            self.ser.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = ArduinoInterfaceNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

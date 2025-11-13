#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import signal
import sys


# ============================================================
# Parameters
# ============================================================

FPS = 15                 # Modify this to change publishing rate
CAMERA_DEVICE = 0        # USB webcam (usually /dev/video0)

# ============================================================

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')

        # Publisher
        self.publisher_ = self.create_publisher(Image, 'camera/raw', 10)

        # CvBridge for image conversion
        self.bridge = CvBridge()

        # OpenCV camera
        self.cap = cv2.VideoCapture(CAMERA_DEVICE)
        if not self.cap.isOpened():
            self.get_logger().error(f"Cannot open camera {CAMERA_DEVICE}")
            raise SystemExit
        
        # Attempt to set FPS (may be ignored by some webcams)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)

        # Timer for publishing
        timer_period = 1.0 / FPS
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info(f"Camera node started at {FPS} FPS")

    # ========================================================
    # Timer callback: capture + publish
    # ========================================================
    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warning("Failed to capture frame")
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.publisher_.publish(msg)

    # ========================================================
    # Cleanup
    # ========================================================
    def destroy_node(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        super().destroy_node()

def main():
    rclpy.init()
    node = CameraNode()

    def shutdown_handler(sig, frame):
        node.get_logger().info("Shutting down cleanly...")
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        shutdown_handler(None, None)

if __name__ == '__main__':
    main()

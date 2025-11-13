#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import time


FPS = 5
BY_ID_PATH = "/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._A4tech_FHD_1080P_PC_Camera_SN0001-video-index0"


def resolve_video_device():
    """
    Returns the real /dev/videoX path for the by-id device.
    Example: /dev/video4
    """
    return os.path.realpath(BY_ID_PATH)


def video_path_to_index(path):
    """
    Extract numeric index from /dev/videoX
    """
    try:
        return int(path.replace("/dev/video", ""))
    except:
        return None


class CameraNode(Node):
    def __init__(self):
        super().__init__("camera_node")

        self.publisher_ = self.create_publisher(Image, "/camera/raw", 10)
        self.bridge = CvBridge()
        self._shutting_down = False

        # ------------------------------------------------------
        # Resolve device reliably using by-id → /dev/videoX
        # ------------------------------------------------------
        device_path = resolve_video_device()
        self.get_logger().info(f"Resolved device path: {device_path}")

        DEVICE_INDEX = video_path_to_index(device_path)
        if DEVICE_INDEX is None:
            self.get_logger().error(f"Invalid device path: {device_path}")
            raise SystemExit

        self.get_logger().info(f"Opening camera at /dev/video{DEVICE_INDEX} via V4L2")

        # ------------------------------------------------------
        # Try opening capture via V4L2 backend
        # ------------------------------------------------------
        self.cap = cv2.VideoCapture(DEVICE_INDEX, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            self.get_logger().error(f"Failed to open /dev/video{DEVICE_INDEX}")
            raise SystemExit

        # Reduce latency
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.timer = self.create_timer(1.0 / FPS, self.timer_callback)
        self.get_logger().info(f"Camera node started at {FPS} FPS")

    def timer_callback(self):
        if self._shutting_down:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Failed to capture frame.")
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_frame"
        self.publisher_.publish(msg)

    def destroy_node(self):
        self._shutting_down = True
        self.get_logger().info("Releasing video device...")

        try:
            if hasattr(self, "timer"):
                self.timer.cancel()

            if hasattr(self, "cap") and self.cap.isOpened():
                self.cap.read()
                time.sleep(0.03)
                self.cap.release()
        except Exception as e:
            self.get_logger().warn(f"Cleanup exception: {e}")

        super().destroy_node()


def main():
    rclpy.init()
    node = CameraNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
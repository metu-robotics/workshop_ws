#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os


FPS = 1
WIDTH = 640
HEIGHT = 480

# Define the by-id path for the specific camera
# To find your camera's by-id path, use:
#   ls -l /dev/v4l/by-id/
BY_ID_PATH = "/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._A4tech_FHD_1080P_PC_Camera_SN0001-video-index0"


def resolve_video_device():
    return os.path.realpath(BY_ID_PATH)


def video_path_to_index(path):
    try:
        return int(path.replace("/dev/video", ""))
    except:
        return None


class CameraNode(Node):
    def __init__(self):
        super().__init__("camera_node")

        self.publisher_ = self.create_publisher(Image, "/camera/raw_frame", 10)
        self.bridge = CvBridge()

        device_path = resolve_video_device()
        DEVICE_INDEX = video_path_to_index(device_path)

        self.get_logger().info(f"Opening camera via GStreamer: {device_path}")

        self.cap = cv2.VideoCapture(DEVICE_INDEX, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)


        if not self.cap.isOpened():
            self.get_logger().error("Failed to open GStreamer camera pipeline.")
            raise SystemExit

        self.timer = self.create_timer(1.0 / FPS, self.timer_callback)
        self.get_logger().info("Camera node started.")

    def timer_callback(self):
        ret, frame = self.cap.read()

        if not ret or frame is None:
            self.get_logger().warn("Failed to capture frame.")
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_frame"

        self.publisher_.publish(msg)

    def destroy_node(self):
        if self.cap.isOpened():
            self.cap.release()
        super().destroy_node()


def main():
    rclpy.init()
    node = CameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
#    rclpy.shutdown()


if __name__ == "__main__":
    main()

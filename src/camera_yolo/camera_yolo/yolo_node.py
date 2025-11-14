#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import json
import cv2
from ultralytics import YOLO


class YoloNode(Node):
    def __init__(self):
        super().__init__("yolo_node")

        # Subscribe to camera stream
        self.subscription = self.create_subscription(
            Image,
            "/camera/raw_frame",
            self.image_callback,
            10
        )

        # Publish JSON detections
        self.publisher = self.create_publisher(String, "/camera/detections", 10)

        self.bridge = CvBridge()

        # Load YOLO model
        self.get_logger().info("Loading YOLO model...")
        self.model = YOLO("yolov8n.pt")   # replace with your model file

        self.get_logger().info("YOLO node initialized.")

    def image_callback(self, msg: Image):
        # Convert ROS image → CV2
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        # Run YOLO inference
        results = self.model(frame, verbose=False)[0]

        detections_list = []

        # Parse YOLO detections
        for box in results.boxes:
            cls_id = int(box.cls[0])
            cls_name = results.names[cls_id]
            conf = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            detections_list.append({
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": round(conf, 3),
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                }
            })

        # Construct JSON message
        json_msg = {
            "timestamp": msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9,
            "num_detections": len(detections_list),
            "detections": detections_list
        }

        # Publish as String
        ros_msg = String()
        ros_msg.data = json.dumps(json_msg)

        self.publisher.publish(ros_msg)
        self.get_logger().info(f"Published {len(detections_list)} detections")


def main(args=None):
    rclpy.init(args=args)
    node = YoloNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
#    rclpy.shutdown()


if __name__ == "__main__":
    main()
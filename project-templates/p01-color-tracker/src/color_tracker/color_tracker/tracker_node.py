"""
颜色追踪节点
订阅摄像头图像，检测目标颜色物体，发布 Twist 控制小乌龟
"""
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge


class ColorTrackerNode(Node):
    def __init__(self):
        super().__init__('color_tracker')

        # 红色 HSV 范围（可调）
        self.lower_hsv = np.array([0, 100, 100])
        self.upper_hsv = np.array([10, 255, 255])

        # ROS 接口
        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.get_logger().info('颜色追踪节点已启动')

    # ===========================================================
    # TODO 1: 实现颜色检测函数
    # ===========================================================
    def detect_color(self, frame):
        """
        输入 BGR 图像，返回 (x, y) 中心坐标，找不到返回 None
        
        实现步骤：
        1. cv2.cvtColor 转 HSV
        2. cv2.inRange(hsv, self.lower_hsv, self.upper_hsv) 得到 mask
        3. cv2.findContours(mask, ...) 找轮廓
        4. 用 max(contours, key=cv2.contourArea) 取最大轮廓
        5. cv2.moments() 计算质心，返回 (cx, cy)
        """
        # TODO: 你的代码
        raise NotImplementedError("请实现颜色检测函数 detect_color()")

    # ===========================================================
    # TODO 2: 根据目标位置计算控制命令
    # ===========================================================
    def compute_twist(self, target_x, frame_width):
        """
        根据目标 x 坐标返回 Twist 消息
        
        策略：
        - |偏离中心| < 50 像素：前进
        - 在左半边：linear.x = 0.3, angular.z > 0
        - 在右半边：linear.x = 0.3, angular.z < 0
        - 偏离越远，转速越大
        
        建议公式: error = (frame_width/2 - target_x) / (frame_width/2)
                  twist.angular.z = error * Kp  (Kp 在 1.0~3.0 范围)
        """
        twist = Twist()
        # TODO: 你的代码
        raise NotImplementedError("请实现 compute_twist()")

    # ===========================================================
    # TODO 3: 图像回调串联整个流程
    # ===========================================================
    def image_callback(self, msg):
        """订阅图像 → 检测 → 发布控制命令"""
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'图像转换失败: {e}')
            return

        # TODO: 调用 detect_color(frame)
        # TODO: 如果检测到目标，调用 compute_twist 并发布到 self.cmd_pub
        # TODO: 否则发布零速度（停止）
        pass


def main(args=None):
    rclpy.init(args=args)
    node = ColorTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

# 项目 1：视觉颜色追踪机器人

> 🎯 难度 ⭐⭐ · 技术：OpenCV + ROS2 + Turtlesim

## 项目目标

让 Turtlesim 中的小乌龟自动追踪摄像头看到的特定颜色物体（例如红色球）：
- 物体在画面左 → 小乌龟左转
- 物体在画面右 → 小乌龟右转
- 物体在画面中心 → 小乌龟前进

## 🚀 快速启动

```bash
# 1. 启动容器
docker compose up -d
docker compose exec dev bash

# 2. 编译
colcon build && source install/setup.bash

# 3. 启动 Turtlesim
ros2 run turtlesim turtlesim_node &

# 4. 启动颜色追踪节点
ros2 run color_tracker tracker_node
```

## 📁 项目结构

```
p01-color-tracker/
├── Dockerfile                          # 容器配置
├── docker-compose.yml                  # 容器编排
├── README.md                            # 本文件
├── src/
│   └── color_tracker/
│       ├── package.xml
│       ├── setup.py
│       ├── color_tracker/
│       │   ├── __init__.py
│       │   └── tracker_node.py         # ⭐ 学生填代码的地方
│       └── launch/
│           └── tracker.launch.py
├── test/
│   └── test_color_detection.py         # 单元测试
└── demo/
    └── sample.mp4                       # 测试用视频
```

## ✍️ 你要做的（TODO 列表）

打开 `src/color_tracker/color_tracker/tracker_node.py`，完成 3 个核心函数：

### TODO 1：HSV 颜色检测

```python
def detect_color(self, frame):
    """
    输入 BGR 图像，返回目标颜色物体的中心坐标 (x, y)
    
    要求：
    1. 转 HSV 色彩空间
    2. 用 cv2.inRange 提取目标颜色（参数 self.lower_hsv / self.upper_hsv）
    3. 用 cv2.findContours 找轮廓
    4. 选最大的轮廓，返回质心坐标
    5. 若没找到 → 返回 None
    """
    # TODO: 你的代码（约 10-15 行）
    pass
```

### TODO 2：根据位置计算控制命令

```python
def compute_twist(self, target_x, frame_width):
    """
    根据目标在图像中的 x 坐标，返回 Twist 消息
    
    要求：
    1. 目标在中心 ± 50 像素 → 前进（linear.x = 0.5）
    2. 目标偏左 → 左转（angular.z > 0）
    3. 目标偏右 → 右转（angular.z < 0）
    4. 角速度大小应与偏离量成正比
    """
    # TODO: 你的代码（约 10 行）
    pass
```

### TODO 3：发布控制命令

```python
def image_callback(self, msg):
    """
    订阅图像 → 检测 → 发布 cmd_vel
    """
    # 1. 将 ROS Image 转为 OpenCV（已写好）
    frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
    
    # TODO: 调用 detect_color 和 compute_twist，发布到 /turtle1/cmd_vel
    pass
```

## 🧪 测试

```bash
# 单元测试（不需要摄像头）
pytest test/

# 集成测试（需要摄像头或视频文件）
ros2 launch color_tracker tracker.launch.py use_video:=demo/sample.mp4
```

## 💡 提示

- HSV 颜色范围参考：红色 H=[0, 10] 或 [170, 180]；绿色 H=[40, 80]；蓝色 H=[100, 130]
- 用 `cv2.imshow` 实时显示中间结果，方便调试
- `force_smoothing` 推荐用滑动平均（避免抖动）

## 🌟 加分项

- [ ] 用滑动条 (`cv2.createTrackbar`) 实时调 HSV 阈值
- [ ] 增加距离估计（用轮廓面积近似）
- [ ] 处理多目标（追踪最大的，或最近的）
- [ ] 失去目标后自动巡逻

## 📊 评分要点

| 评分点 | 占比 |
|--------|------|
| detect_color 实现正确 | 15% |
| compute_twist 逻辑合理 | 15% |
| 实际运行效果 | 30% |
| 测试通过率 | 15% |
| 代码注释 + README | 10% |
| 演示视频 | 15% |

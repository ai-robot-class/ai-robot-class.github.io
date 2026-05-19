# 项目 3：简单目标检测系统

> ⭐⭐⭐ · 技术：Ultralytics YOLOv8 + ROS2 + Image_view

## 🎯 项目目标

从摄像头/视频实时检测物体，发布检测结果到 ROS2 话题

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
ros2 run yolo_detector detector_node
# 另一终端查看：
ros2 run rqt_image_view rqt_image_view
```

## ✍️ 你要做的（TODO 列表）

### TODO 1：`detect_objects`

调用 YOLO 模型推理（self.model(frame)），返回 boxes + labels + confs

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 2：`publish_detections`

把检测结果封装为 vision_msgs/Detection2DArray 并发布

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 3：`draw_overlay`

在图像上画检测框 + 标签 + 置信度，并发布标注后图像

```python
# 在源码中找到这个函数，按注释提示实现
```



## 🧪 测试

```bash
pytest test/
```

## 📊 评分要点

| 评分点 | 占比 |
|--------|------|
| 核心 TODO 实现正确 | 40% |
| 运行效果 | 30% |
| 代码质量 | 15% |
| 文档与演示视频 | 15% |

## 💡 提示

- 先把 `templates/` 下的骨架代码读一遍，理解整体流程
- 不会写时去看 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) 或官方教程
- 卡住超过 30 分钟立即在课程群提问，不要硬磕

## 🌟 加分项

- 录制 2-3 分钟的演示视频
- 写技术博客记录开发过程
- 用 GitHub Issues 跟踪自己的开发任务

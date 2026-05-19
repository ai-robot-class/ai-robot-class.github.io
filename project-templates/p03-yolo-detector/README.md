# 项目 3：KITTI 数据集物体检测可视化

> ⭐⭐⭐ · 技术：YOLOv8 + ROS2 bag + KITTI

## 🎯 项目目标

在 KITTI ROS bag 上跑 YOLO 检测，发布到 ROS topic，并生成检测统计报告

## 📦 数据来源（无需任何硬件）

✅ **课程已准备好**：Week 6 实验用过的 KITTI ROS bag（约 200MB）

下载：`bash demo/download_kitti.sh`

包含 100 帧前置相机图像 + 同步的 IMU/GPS

## ⚙️ 运行模式

| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认（无硬件）** | KITTI `.bag` 文件 | `detections.csv` + `annotated.mp4` |
| 🟡 **扩展（有摄像头）** | `/dev/video0` 实时 | RViz 实时显示 |

## 🚀 快速启动

```bash
# 1. 启动容器（首次约 2-5 分钟）
docker compose up -d
docker compose exec dev bash

# 2. 下载数据集（如有）
bash demo/download_data.sh 2>/dev/null || true

# 3. 编译
colcon build && source install/setup.bash

# 4. 默认无硬件模式运行
# 1. 下载 KITTI bag
bash demo/download_kitti.sh

# 2. 启动 YOLO 节点
ros2 run yolo_detector detector_node &

# 3. 回放 KITTI bag
ros2 bag play demo/kitti_seq00.bag

# 4. 查看结果
cat detections.csv  # 检测统计
xdg-open annotated.mp4  # 标注视频
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`detect_objects`

调用 YOLO 模型 (`yolov8n.pt` CPU 推理，~50ms/帧) 返回 boxes/labels/confs

### TODO 2：`publish_to_ros`

把检测结果封装成 `vision_msgs/Detection2DArray` 发布

### TODO 3：`generate_stats`

统计 100 帧内各类别出现次数 + 写入 CSV + 绘制柱状图



## 🧪 测试

```bash
pytest test/

# 项目特定的端到端测试
bash test/integration_test.sh
```

## 📊 评分要点

| 评分点 | 占比 |
|--------|------|
| 3 个 TODO 实现正确性 | 40% |
| 在提供数据集上的运行效果 | 30% |
| 代码质量（注释、命名、模块化）| 15% |
| 文档完整度 + 演示视频 | 10% |
| **加分**：自己采集额外数据/改进算法 | +5% |

## 🔌 扩展：使用真实硬件

如果你有 `/dev/video0`，把它加到 `docker-compose.yml` 的 `devices:` 字段，然后用 `--source camera` 参数运行。但**不是必须**。

## 💡 提示

- 把 `templates/` 下的骨架代码读一遍，理解整体流程
- 不会写时去看 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) 或官方教程
- **卡住超过 30 分钟立即在课程群提问**，不要硬磕

## 🌟 加分项

- 录制 2-3 分钟的演示视频上传
- 在 README 中写技术博客式的开发记录
- 测试自己的算法在更多数据上的效果
- 提供完整的可视化（matplotlib/rviz）

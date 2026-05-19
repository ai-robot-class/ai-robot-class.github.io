# 项目 7：Gazebo 仿真 + YOLO 智能巡检

> ⭐⭐⭐⭐ · 技术：Gazebo + Nav2 + YOLO + 报告生成

## 🎯 项目目标

机器人在仿真城市/办公室自动巡检，发现人/车辆等关键目标时停下并生成异常报告

## 📦 数据来源（无需任何硬件）

✅ **完全仿真**：
- Gazebo aws_robomaker_hospital_world（医院场景）
- Gazebo turtlebot3_house（住宅场景）
- 巡检点：`config/waypoints.yaml`（10 个预设点）
- YOLO 模型：yolov8n.pt（4.7MB，CPU 推理）

## ⚙️ 运行模式

| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认（纯仿真）** | Gazebo 内置场景 | 巡检视频 + 异常报告 PDF |
| 🟢 **扩展（KITTI bag）** | KITTI 城市场景 bag | 静态场景的异常检测分析 |

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
# 启动仿真环境
ros2 launch patrol_robot full_stack.launch.py world:=hospital

# 启动巡检任务
ros2 run patrol_robot mission_executor --waypoints config/waypoints.yaml

# 完成后查看报告
xdg-open patrol_report.pdf
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`waypoints_publisher`

从 YAML 读取巡检点，按顺序通过 Nav2 Action 发送，等待完成后切下一个

### TODO 2：`detect_and_log`

在每个巡检点暂停 3 秒，用 YOLO 检测仿真相机话题，记录"位置+时间+检测到的类别"

### TODO 3：`generate_pdf_report`

用 reportlab 生成 PDF 报告，包含地图轨迹、检测时间线、各类别统计图



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

## 💡 提示

- 把 `templates/` 下的骨架代码读一遍，理解整体流程
- 不会写时去看 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) 或官方教程
- **卡住超过 30 分钟立即在课程群提问**，不要硬磕

## 🌟 加分项

- 录制 2-3 分钟的演示视频上传
- 在 README 中写技术博客式的开发记录
- 测试自己的算法在更多数据上的效果
- 提供完整的可视化（matplotlib/rviz）

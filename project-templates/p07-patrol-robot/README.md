# 项目 7：智能巡检机器人

> ⭐⭐⭐⭐ · 技术：SLAM + YOLO + TTS（语音播报）+ ROS2

## 🎯 项目目标

机器人按预设路径巡检 → 发现目标自动停下 → 播报"检测到 XXX"

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
ros2 launch patrol_robot full_stack.launch.py
```

## ✍️ 你要做的（TODO 列表）

### TODO 1：`waypoints_publisher`

从 waypoints.yaml 读取巡检点，按顺序发送给 Nav2

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 2：`detect_anomaly`

订阅 YOLO 检测话题，发现 "person" 或 "fire" 等关键类别时返回告警

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 3：`voice_alarm`

收到告警后停下机器人，用 TTS 播报告警内容并写入 anomaly_log.txt

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

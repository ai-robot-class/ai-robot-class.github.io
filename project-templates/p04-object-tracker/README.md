# 项目 4：物体追踪与跟随

> ⭐⭐⭐ · 技术：YOLO + SORT 多目标跟踪 + ROS2

## 🎯 项目目标

识别+持续跟踪特定物体，给出 ID 标号；让机器人跟随保持安全距离

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
ros2 launch object_tracker tracker.launch.py
```

## ✍️ 你要做的（TODO 列表）

### TODO 1：`init_tracker`

初始化 SORT 跟踪器（构造卡尔曼滤波器参数）

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 2：`update_tracker`

每帧用 YOLO 检测结果更新 SORT，返回稳定的 ID 列表

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 3：`compute_follow_cmd`

根据目标 bbox 大小（远近）和位置（左右），输出 Twist 让机器人跟随并保持 1m 距离

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

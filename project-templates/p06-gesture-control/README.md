# 项目 6：手势识别控制

> ⭐⭐⭐ · 技术：MediaPipe Hands + ROS2

## 🎯 项目目标

用手势（手掌 / 拳头 / 食指方向）控制机器人运动

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
ros2 run gesture_control gesture_node
```

## ✍️ 你要做的（TODO 列表）

### TODO 1：`detect_landmarks`

用 mp.solutions.hands 检测 21 个手部关键点

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 2：`classify_gesture`

根据关键点位置判断手势：手掌张开 / 拳头 / 指向 X 方向（共 5 类）

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 3：`gesture_to_twist`

把手势映射为 Twist 命令（手掌=停止，拳头=前进，食指方向=转弯方向）

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

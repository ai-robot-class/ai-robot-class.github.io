# 项目 9：机械臂物体抓取

> ⭐⭐⭐⭐⭐ · 技术：MoveIt2 + 视觉定位 + ROS2

## 🎯 项目目标

相机识别物体 3D 位置 → 用逆运动学规划路径 → 机械臂抓取放到目标盒子

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
ros2 launch arm_grasp moveit_demo.launch.py
# 等 RViz 启动后：
ros2 service call /trigger_grasp std_srvs/srv/Trigger {}
```

## ✍️ 你要做的（TODO 列表）

### TODO 1：`detect_object_3d`

从 RGB-D 相机数据，用 YOLO 检测 + 深度图反投影，得到物体世界坐标 (x,y,z)

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 2：`plan_grasp`

用 MoveIt MoveGroup API 规划机械臂从初始位置到抓取位姿的路径

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 3：`execute_pick_and_place`

编排完整流程：移到上方 → 下降抓取 → 抬起 → 移到目标点 → 释放

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

# 项目 5：多传感器融合导航

> ⭐⭐⭐⭐ · 技术：ROS2 Nav2 + slam_toolbox + 仿真环境（TurtleBot3）

## 🎯 项目目标

让仿真机器人在未知环境中 SLAM 建图 → 保存地图 → 用 Nav2 自主导航避障

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
# 1. 启动仿真
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# 2. SLAM 建图
ros2 launch nav2_fusion slam.launch.py

# 3. 用键盘走一圈，保存地图后切换 Nav2
ros2 launch nav2_fusion nav.launch.py map:=my_map.yaml
```

## ✍️ 你要做的（TODO 列表）

### TODO 1：`configure_nav2_params`

修改 nav2_params.yaml 中的 controller / planner 参数（DWB + NavFn）

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 2：`write_lifecycle_manager`

编写 lifecycle 自动启动脚本，确保所有 Nav2 节点正常激活

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 3：`add_goal_publisher`

订阅 /goal 话题，把目标点格式化为 NavigateToPose action 调用

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

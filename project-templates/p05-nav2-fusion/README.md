# 项目 5：Gazebo 仿真 SLAM + Nav2 自主导航

> ⭐⭐⭐⭐ · 技术：Gazebo Classic + slam_toolbox + Nav2

## 🎯 项目目标

在 TurtleBot3 仿真环境中：① 自动建图 ② 保存地图 ③ Nav2 自主导航穿越障碍

## 📦 数据来源（无需任何硬件）

✅ **完全仿真，零硬件**：
- TurtleBot3 仿真模型（apt 自带）
- Gazebo 自带地图：empty / house / world / aws_hospital
- 课程额外提供：`worlds/maze.world`（迷宫场景）

## ⚙️ 运行模式

| 模式 | 仿真器 | 资源占用 |
|------|--------|---------|
| 🟢 **默认** | Gazebo Classic（轻量）| ~2GB RAM, CPU 单核 50% |
| 🟢 **备选** | Stage 2D（极轻量）| ~500MB RAM |

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
# 1. 启动 Gazebo + TurtleBot3
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py &

# 2. SLAM 建图（手动键盘控制走一圈）
ros2 launch nav2_fusion slam.launch.py &
ros2 run turtlebot3_teleop teleop_keyboard

# 3. 保存地图
ros2 run nav2_map_server map_saver_cli -f my_map

# 4. 启动 Nav2 自主导航
ros2 launch nav2_fusion nav.launch.py map:=my_map.yaml
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`configure_nav_params`

在 `nav2_params.yaml` 中调整 DWB controller / NavFn planner 关键参数（max_vel_x, inflation_radius, etc.）

### TODO 2：`write_goal_sender`

用 NavigateToPose Action client 发送目标点；订阅 feedback 并打印进度

### TODO 3：`measure_metrics`

记录 5 次导航任务：成功率、平均时长、平均路径长度，写入报告



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

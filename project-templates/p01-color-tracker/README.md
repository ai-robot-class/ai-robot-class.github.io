# 项目 1：基于视频的颜色追踪（ROS bag 输出）

> ⭐⭐ · 技术：OpenCV + ROS2 + 视频文件

## 🎯 项目目标

从给定视频中追踪特定颜色物体，输出处理后视频和 ROS bag（cmd_vel 命令序列）

## 📦 数据来源（无需任何硬件）

课程提供 `demo/colored_ball.mp4`（红色小球在白桌子上滚动）
扩展可用：B 站/YouTube 任意颜色物体视频

## ⚙️ 运行模式

| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认（无硬件）** | `demo/colored_ball.mp4` | `output.mp4` + `cmd_vel.bag` |
| 🟡 **扩展（有摄像头）** | `/dev/video0` 实时 | 实时 RViz 显示 |

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
# 默认无硬件模式
ros2 run color_tracker tracker_node --video demo/colored_ball.mp4 \
    --output output.mp4 --bag cmd_vel.bag

# 验证：回放 bag 看 Twist 序列
ros2 bag play cmd_vel.bag &
ros2 topic echo /cmd_vel
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`detect_color`

在 BGR 帧中用 HSV 阈值检测目标颜色，返回最大轮廓中心 (x, y)

### TODO 2：`compute_twist`

根据目标 x 偏离图像中心的程度，输出 Twist（含线速度+角速度）

### TODO 3：`save_to_bag`

把每帧产生的 Twist 写入 ROS bag，便于回放或离线分析



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

# 项目 6：基于视频的手势识别命令

> ⭐⭐⭐ · 技术：MediaPipe Hands + ROS2

## 🎯 项目目标

从手势演示视频识别手势序列，转换成 Twist 命令保存为 ROS bag，可在 Turtlesim 回放

## 📦 数据来源（无需任何硬件）

课程提供 6 个手势演示视频（每段 5-10 秒）：
- `demo/gesture_palm.mp4` (张开手掌 = 停止)
- `demo/gesture_fist.mp4` (拳头 = 前进)
- `demo/gesture_point_left.mp4` (食指向左 = 左转)
- `demo/gesture_point_right.mp4` (食指向右 = 右转)
- `demo/gesture_thumbs_up.mp4` (竖大拇指 = 加速)
- `demo/gesture_mixed.mp4` (混合手势序列)

## ⚙️ 运行模式

| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认** | `demo/*.mp4` 手势视频 | 命令序列 + Turtlesim 轨迹图 |
| 🟡 **扩展（有摄像头）** | `/dev/video0` | 实时手势 → Twist |

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
# 处理单个视频
python -m gesture_control.run --video demo/gesture_mixed.mp4 \
    --output commands.csv --bag commands.bag

# 在 Turtlesim 上回放
ros2 run turtlesim turtlesim_node &
ros2 bag play commands.bag
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`extract_landmarks`

用 `mp.solutions.hands` 处理视频每一帧，得到 21 个手部关键点的 (x,y,z)

### TODO 2：`classify_gesture`

基于关键点的相对位置和角度，分类 5 种手势（不用深度学习，纯几何规则）

### TODO 3：`gesture_to_twist_sequence`

把视频识别出的手势按时间顺序输出 Twist 序列（带时间戳）



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

# 项目 2：基于音频文件的语音命令解析

> ⭐⭐ · 技术：SpeechRecognition (offline) + ROS2 Turtlesim

## 🎯 项目目标

从音频文件识别中文语音命令，控制 Turtlesim 走出指定轨迹，生成动画 GIF

## 📦 数据来源（无需任何硬件）

课程提供 5 个预录音频：
- `demo/forward.wav`  → "前进 5 秒"
- `demo/turn_left.wav` → "向左转 90 度"
- `demo/circle.wav` → "走一个圆形"
- `demo/square.wav` → "画一个方形"
- `demo/stop.wav` → "停止"

学生也可以用手机录制自己的音频（导出 wav 上传到项目目录）

## ⚙️ 运行模式

| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认（无硬件）** | `demo/*.wav` | Turtlesim 截图 + GIF |
| 🟡 **扩展（有麦克风）** | `/dev/snd` 实时录音 | 实时控制 |

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
# 默认：解析 demo 音频
ros2 run voice_turtle voice_node --audio demo/circle.wav

# 输出 trajectory.png 和 trajectory.gif
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`load_and_recognize`

用 SpeechRecognition + Vosk **离线**模型识别 wav 文件（不依赖网络）

### TODO 2：`parse_command`

把识别文本映射为 Twist 序列（"前进 5 秒" → [Twist(x=1.0)]*5）

### TODO 3：`execute_and_record`

在 Turtlesim 执行命令，同时用 matplotlib 把轨迹画成 PNG/GIF



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

如果你有 `/dev/snd`，把它加到 `docker-compose.yml` 的 `devices:` 字段，然后用 `--source camera` 参数运行。但**不是必须**。

## 💡 提示

- 把 `templates/` 下的骨架代码读一遍，理解整体流程
- 不会写时去看 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) 或官方教程
- **卡住超过 30 分钟立即在课程群提问**，不要硬磕

## 🌟 加分项

- 录制 2-3 分钟的演示视频上传
- 在 README 中写技术博客式的开发记录
- 测试自己的算法在更多数据上的效果
- 提供完整的可视化（matplotlib/rviz）

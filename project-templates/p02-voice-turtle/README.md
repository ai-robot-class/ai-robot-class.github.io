# 项目 2：语音控制小乌龟

> ⭐⭐ · 技术：SpeechRecognition + pyttsx3 + ROS2 + Turtlesim

## 🎯 项目目标

用语音指令"前进/后退/左转/右转/停止"控制 Turtlesim

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
ros2 run turtlesim turtlesim_node &
ros2 run voice_turtle voice_node
```

## ✍️ 你要做的（TODO 列表）

### TODO 1：`recognize_command`

调用 sr.Recognizer().recognize_google 识别中文语音，返回识别字符串

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 2：`parse_command`

把识别到的文字映射为 Twist（"前进"→linear.x=1, "左转"→angular.z=1 等）

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 3：`voice_feedback`

识别成功后用 pyttsx3 播报"已收到命令：xxx"

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

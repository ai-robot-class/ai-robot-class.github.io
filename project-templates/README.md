# 🐳 期末项目 Docker 仿真模板

> 为 Week 12 公布的 10 个项目选题，每个都准备好了**开箱即用的 Docker 环境**和**代码框架骨架**。
>
> ✅ 学生只需要专注**填核心算法代码**（用 `# TODO:` 标注的位置），不用花时间纠结环境。

## 🎯 设计原则

1. **环境零配置**：`docker compose up` 一条命令启动
2. **GUI 已配置好**：X11 转发已设好，RViz/Gazebo 弹窗即开即用
3. **依赖完整**：ROS2 Humble + OpenCV + PyTorch + YOLO + ... 全部预装
4. **骨架代码**：完整的 ROS2 包、节点框架、CMakeLists/setup.py 都写好
5. **核心留空**：把"考点"留给学生（用 `# TODO:` 注释明确标出）
6. **测试用例**：提供单元测试 + 集成测试 + 演示数据

## 📦 通用基础镜像（所有项目共用）

`templates/Dockerfile.base`：

```dockerfile
FROM osrf/ros:humble-desktop-full

# ===== 系统工具 =====
RUN apt-get update && apt-get install -y \
    python3-pip git wget curl vim tmux \
    x11-apps mesa-utils libgl1-mesa-glx \
    portaudio19-dev libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# ===== Python 通用依赖 =====
RUN pip3 install --no-cache-dir \
    numpy scipy matplotlib pandas \
    opencv-python opencv-contrib-python \
    torch torchvision \
    ultralytics \
    speechrecognition pyttsx3 gtts pyaudio \
    mediapipe \
    pybullet \
    rich loguru

# ===== ROS2 工作空间 =====
WORKDIR /workspace
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc \
 && echo "source /workspace/install/setup.bash 2>/dev/null || true" >> ~/.bashrc

# ===== X11 GUI 转发 =====
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1

CMD ["/bin/bash"]
```

## 🚀 学生使用流程

```bash
# 1. fork / clone 项目模板
git clone https://github.com/ai-robot-class/project-templates.git
cd project-templates/p01-color-tracker  # 选择你的项目

# 2. 启动环境（首次会自动拉取镜像，约 2-5 分钟）
docker compose up -d

# 3. 进入容器
docker compose exec dev bash

# 4. 编译 ROS2 包
colcon build && source install/setup.bash

# 5. 找到 TODO，写自己的代码！
# 5a. 在容器外用 VSCode 打开项目目录即可（容器是为了运行环境，写代码可以在宿主机写）

# 6. 运行 & 测试
ros2 launch color_tracker tracker.launch.py

# 7. 完成后提交到自己的 GitHub
git add . && git commit -m "完成颜色追踪核心" && git push
```

## 📋 10 个项目模板列表

| # | 项目 | 难度 | 主要技术 | 容器目录 |
|---|------|------|---------|---------|
| 1 | 视觉颜色追踪机器人 | ⭐⭐ | OpenCV + Turtlesim | `p01-color-tracker/` |
| 2 | 语音控制小乌龟 | ⭐⭐ | SpeechRecognition + ROS2 | `p02-voice-turtle/` |
| 3 | 简单目标检测系统 | ⭐⭐⭐ | YOLO + ROS2 | `p03-yolo-detector/` |
| 4 | 物体追踪与跟随 | ⭐⭐⭐ | YOLO + SORT | `p04-object-tracker/` |
| 5 | 多传感器融合导航 | ⭐⭐⭐⭐ | Nav2 + 激光雷达仿真 | `p05-nav2-fusion/` |
| 6 | 手势识别控制 | ⭐⭐⭐ | MediaPipe + ROS2 | `p06-gesture-control/` |
| 7 | 智能巡检机器人 | ⭐⭐⭐⭐ | SLAM + YOLO + TTS | `p07-patrol-robot/` |
| 8 | 人脸识别门禁系统 | ⭐⭐⭐⭐ | face_recognition + ROS2 | `p08-face-access/` |
| 9 | 机械臂物体抓取 | ⭐⭐⭐⭐⭐ | MoveIt2 + 视觉 | `p09-arm-grasp/` |
| 10 | 四足机器人控制 | ⭐⭐⭐⭐⭐ | PyBullet + 步态 | `p10-quadruped/` |

## 🎓 评分说明

容器配置和模板代码**不计入评分**。评分聚焦在：

| 项目 | 占比 | 评分点 |
|------|------|--------|
| 核心算法 TODO 完成度 | 40% | 是否正确实现关键代码 |
| 代码质量 | 20% | 注释、命名、结构、可读性 |
| 测试通过率 | 15% | 提供的单元测试 |
| 演示效果 | 15% | 实际跑起来的效果 |
| 文档报告 | 10% | README + 演示视频 |

## 🔧 常见问题

### Q: 容器内 GUI 弹不出来？

A: 宿主机需要先允许 X11：
```bash
xhost +local:docker  # Linux
# 或在 WSL2: 安装 WSLg（Win11/Win10 22H2 自带）
```

### Q: 摄像头/麦克风进不了容器？

A: `docker-compose.yml` 已经映射了 `/dev/video0` 和 `/dev/snd`，启动前确保宿主机插好。

### Q: 没有 GPU 也能跑 YOLO？

A: 默认用 CPU。如果有 NVIDIA GPU，按 `templates/gpu-setup.md` 配置 nvidia-runtime。

### Q: 想用 IDE 调试容器里的代码？

A: VSCode 装 `Remote Containers` 扩展，一键 attach 到容器。

---

*维护：信韩大学 软件学院 · AI 机器人课程组*

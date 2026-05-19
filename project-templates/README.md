# 🐳 期末项目 Docker 仿真模板

> 为 Week 12 公布的 10 个项目选题，每个都准备好了**开箱即用的 Docker 环境**和**代码框架骨架**。
>
> ✅ 学生只需要专注**填核心算法代码**（用 `# TODO:` 标注的位置），不用花时间纠结环境。

## 🎯 核心设计原则

### 💯 默认无硬件即可完成所有项目！

考虑到学生硬件条件参差不齐，**全部 10 个项目重新设计为：默认使用数据集 / ROS bag / 仿真**，
不依赖摄像头、麦克风、独显等任何外设。

| 你的电脑情况 | 能否完成所有项目？ |
|------------|------------------|
| 💻 普通笔记本（无摄像头/无麦克风） | ✅ 全部 10 个项目可完成 |
| 🍎 MacBook Air（M1/M2，无 GPU） | ✅ 全部可完成（Docker Desktop 必装）|
| 🪟 Windows + WSL2 | ✅ 全部可完成 |
| 🐧 Linux 台式机（有摄像头） | ✅ 默认模式 + 扩展模式都行 |

### 🔄 数据源策略

| 数据类型 | 默认提供 | 来源 |
|---------|---------|------|
| 视频 | `demo/*.mp4` | 课程组录制 + 公开数据集 |
| ROS bag | KITTI / 自录场景 | 课程仓库 + 自动下载脚本 |
| 音频 | `demo/*.wav` | 课程组录制 + 学生可自录 |
| 图像数据集 | MOT17 / LFW 子集 | 公开数据集 |
| 仿真 | Gazebo / PyBullet | apt / pip 自带 |

### 🔧 容器策略

1. **环境零配置**：`docker compose up` 一条命令启动
2. **GUI 已配置好**：X11 转发已设好，RViz/Gazebo 弹窗即开即用
3. **依赖完整**：ROS2 Humble + OpenCV + PyTorch + YOLO + ... 全部预装
4. **骨架代码**：完整的 ROS2 包、节点框架、CMakeLists/setup.py 都写好
5. **核心留空**：把"考点"留给学生（用 `# TODO:` 注释明确标出）
6. **测试用例**：提供单元测试 + 集成测试 + 演示数据
7. **硬件作为扩展**：摄像头/麦克风在 docker-compose.yml 中被注释，需要时再启用

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

## 📋 10 个项目模板列表（默认无硬件可完成）

| # | 项目 | 难度 | 数据源（无硬件） | 输出 |
|---|------|------|-----------------|------|
| 1 | 基于视频的颜色追踪 | ⭐⭐ | 课程提供 `colored_ball.mp4` | 处理后视频 + ROS bag |
| 2 | 基于音频文件的语音命令解析 | ⭐⭐ | 课程提供 `*.wav` 命令音频 | Turtlesim 轨迹图 |
| 3 | KITTI 数据集物体检测 | ⭐⭐⭐ | KITTI ROS bag（Week 6 用过）| 检测视频 + 统计 CSV |
| 4 | MOT17 多目标追踪 | ⭐⭐⭐ | MOT17 行人数据集 | 追踪视频 + MOTA 指标 |
| 5 | Gazebo SLAM + Nav2 导航 | ⭐⭐⭐⭐ | TurtleBot3 仿真环境 | 自主导航实验报告 |
| 6 | 视频手势识别 | ⭐⭐⭐ | 课程提供 6 个手势视频 | 命令序列 + 轨迹图 |
| 7 | Gazebo 智能巡检 | ⭐⭐⭐⭐ | 仿真医院/住宅环境 | PDF 巡检报告 |
| 8 | 人脸数据集识别 | ⭐⭐⭐⭐ | LFW 子集 / 课程提供照片 | 准确率/混淆矩阵 |
| 9 | PyBullet 机械臂抓取 | ⭐⭐⭐⭐⭐ | 纯 PyBullet 仿真 | 抓取演示视频 |
| 10 | PyBullet 四足步态优化 | ⭐⭐⭐⭐⭐ | PyBullet Laikago 模型 | 优化后步态视频 |

### 💪 项目设计亮点

| 设计思路 | 体现 |
|---------|------|
| **复用本课程知识** | KITTI bag（Week 6）、YOLO（Week 10）、追踪（Week 11）、Docker（Week 8） |
| **公开数据集** | MOT17、LFW、KITTI 等业界常用基准 |
| **完全可仿真** | Gazebo / PyBullet 跑得动的项目占 4 个 |
| **可量化评价** | 多个项目提供真值数据，可计算 mAP/MOTA/准确率等指标 |
| **可扩展性** | 有硬件的同学可以一键启用真实摄像头/麦克风（加分项）|

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

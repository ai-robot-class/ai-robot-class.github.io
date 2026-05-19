"""项目模板生成脚本 v2 - 默认无硬件模式（数据集/ROS bag/仿真）"""
import os
from pathlib import Path

PROJECTS = {
    'p01-color-tracker': {
        'title': '项目 1：基于视频的颜色追踪（ROS bag 输出）',
        'level': '⭐⭐',
        'tech': 'OpenCV + ROS2 + 视频文件',
        'goal': '从给定视频中追踪特定颜色物体，输出处理后视频和 ROS bag（cmd_vel 命令序列）',
        'data_source': '''课程提供 `demo/colored_ball.mp4`（红色小球在白桌子上滚动）
扩展可用：B 站/YouTube 任意颜色物体视频''',
        'hardware_modes': '''| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认（无硬件）** | `demo/colored_ball.mp4` | `output.mp4` + `cmd_vel.bag` |
| 🟡 **扩展（有摄像头）** | `/dev/video0` 实时 | 实时 RViz 显示 |''',
        'apt': 'ros-humble-cv-bridge ros-humble-rosbag2',
        'pip': 'opencv-python numpy',
        'devices': '',  # 默认不挂载摄像头
        'optional_devices': '/dev/video0',
        'todos': [
            ('detect_color', '在 BGR 帧中用 HSV 阈值检测目标颜色，返回最大轮廓中心 (x, y)'),
            ('compute_twist', '根据目标 x 偏离图像中心的程度，输出 Twist（含线速度+角速度）'),
            ('save_to_bag', '把每帧产生的 Twist 写入 ROS bag，便于回放或离线分析'),
        ],
        'run': '''# 默认无硬件模式
ros2 run color_tracker tracker_node --video demo/colored_ball.mp4 \\
    --output output.mp4 --bag cmd_vel.bag

# 验证：回放 bag 看 Twist 序列
ros2 bag play cmd_vel.bag &
ros2 topic echo /cmd_vel''',
    },
    'p02-voice-turtle': {
        'title': '项目 2：基于音频文件的语音命令解析',
        'level': '⭐⭐',
        'tech': 'SpeechRecognition (offline) + ROS2 Turtlesim',
        'goal': '从音频文件识别中文语音命令，控制 Turtlesim 走出指定轨迹，生成动画 GIF',
        'data_source': '''课程提供 5 个预录音频：
- `demo/forward.wav`  → "前进 5 秒"
- `demo/turn_left.wav` → "向左转 90 度"
- `demo/circle.wav` → "走一个圆形"
- `demo/square.wav` → "画一个方形"
- `demo/stop.wav` → "停止"

学生也可以用手机录制自己的音频（导出 wav 上传到项目目录）''',
        'hardware_modes': '''| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认（无硬件）** | `demo/*.wav` | Turtlesim 截图 + GIF |
| 🟡 **扩展（有麦克风）** | `/dev/snd` 实时录音 | 实时控制 |''',
        'apt': 'ros-humble-turtlesim portaudio19-dev libsndfile1 ffmpeg',
        'pip': 'speech_recognition vosk pyttsx3 gtts librosa imageio[ffmpeg]',
        'devices': '',
        'optional_devices': '/dev/snd',
        'todos': [
            ('load_and_recognize', '用 SpeechRecognition + Vosk **离线**模型识别 wav 文件（不依赖网络）'),
            ('parse_command', '把识别文本映射为 Twist 序列（"前进 5 秒" → [Twist(x=1.0)]*5）'),
            ('execute_and_record', '在 Turtlesim 执行命令，同时用 matplotlib 把轨迹画成 PNG/GIF'),
        ],
        'run': '''# 默认：解析 demo 音频
ros2 run voice_turtle voice_node --audio demo/circle.wav

# 输出 trajectory.png 和 trajectory.gif''',
    },
    'p03-yolo-detector': {
        'title': '项目 3：KITTI 数据集物体检测可视化',
        'level': '⭐⭐⭐',
        'tech': 'YOLOv8 + ROS2 bag + KITTI',
        'goal': '在 KITTI ROS bag 上跑 YOLO 检测，发布到 ROS topic，并生成检测统计报告',
        'data_source': '''✅ **课程已准备好**：Week 6 实验用过的 KITTI ROS bag（约 200MB）

下载：`bash demo/download_kitti.sh`

包含 100 帧前置相机图像 + 同步的 IMU/GPS''',
        'hardware_modes': '''| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认（无硬件）** | KITTI `.bag` 文件 | `detections.csv` + `annotated.mp4` |
| 🟡 **扩展（有摄像头）** | `/dev/video0` 实时 | RViz 实时显示 |''',
        'apt': 'ros-humble-cv-bridge ros-humble-image-view ros-humble-rosbag2',
        'pip': 'ultralytics opencv-python numpy pandas',
        'devices': '',
        'optional_devices': '/dev/video0',
        'todos': [
            ('detect_objects', '调用 YOLO 模型 (`yolov8n.pt` CPU 推理，~50ms/帧) 返回 boxes/labels/confs'),
            ('publish_to_ros', '把检测结果封装成 `vision_msgs/Detection2DArray` 发布'),
            ('generate_stats', '统计 100 帧内各类别出现次数 + 写入 CSV + 绘制柱状图'),
        ],
        'run': '''# 1. 下载 KITTI bag
bash demo/download_kitti.sh

# 2. 启动 YOLO 节点
ros2 run yolo_detector detector_node &

# 3. 回放 KITTI bag
ros2 bag play demo/kitti_seq00.bag

# 4. 查看结果
cat detections.csv  # 检测统计
xdg-open annotated.mp4  # 标注视频''',
    },
    'p04-object-tracker': {
        'title': '项目 4：MOT17 / KITTI Tracking 多目标追踪',
        'level': '⭐⭐⭐',
        'tech': 'YOLOv8 + SORT + ROS2 bag',
        'goal': '在 MOT17 行人追踪数据集上跑 YOLO + SORT，输出带 track_id 的视频，计算 MOTA/IDF1 指标',
        'data_source': '''课程提供数据集子集：
- `demo/MOT17-04.mp4` （525 帧行人场景）
- `demo/MOT17-04-gt.txt`（真值标注）

完整 MOT17：https://motchallenge.net/data/MOT17/''',
        'hardware_modes': '''| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认** | `demo/MOT17-04.mp4` | `tracked.mp4` + `metrics.json` |
| 🟡 **扩展（有摄像头）** | `/dev/video0` | 实时追踪可视化 |''',
        'apt': 'ros-humble-cv-bridge ros-humble-rosbag2',
        'pip': 'ultralytics filterpy scipy motmetrics pandas',
        'devices': '',
        'optional_devices': '/dev/video0',
        'todos': [
            ('init_tracker', '初始化 SORT：每个 Track 内置卡尔曼滤波器（状态 = [x, y, s, r, vx, vy, vs]）'),
            ('match_detections', '用匈牙利算法 (`scipy.optimize.linear_sum_assignment`) 关联 detection ↔ track（IoU 阈值 0.3）'),
            ('compute_motrics', '用 `motmetrics` 计算 MOTA / IDF1 / FP / FN / IDsw 五项指标'),
        ],
        'run': '''# 端到端跑通
python -m object_tracker.run --video demo/MOT17-04.mp4 \\
    --gt demo/MOT17-04-gt.txt \\
    --output tracked.mp4

# 输出
# tracked.mp4 - 带 track ID 的可视化
# metrics.json - MOTA 等指标
# 期末报告: 对比不同 IoU 阈值的 MOTA 变化''',
    },
    'p05-nav2-fusion': {
        'title': '项目 5：Gazebo 仿真 SLAM + Nav2 自主导航',
        'level': '⭐⭐⭐⭐',
        'tech': 'Gazebo Classic + slam_toolbox + Nav2',
        'goal': '在 TurtleBot3 仿真环境中：① 自动建图 ② 保存地图 ③ Nav2 自主导航穿越障碍',
        'data_source': '''✅ **完全仿真，零硬件**：
- TurtleBot3 仿真模型（apt 自带）
- Gazebo 自带地图：empty / house / world / aws_hospital
- 课程额外提供：`worlds/maze.world`（迷宫场景）''',
        'hardware_modes': '''| 模式 | 仿真器 | 资源占用 |
|------|--------|---------|
| 🟢 **默认** | Gazebo Classic（轻量）| ~2GB RAM, CPU 单核 50% |
| 🟢 **备选** | Stage 2D（极轻量）| ~500MB RAM |''',
        'apt': '''ros-humble-nav2-bringup ros-humble-slam-toolbox \\
    ros-humble-turtlebot3-* ros-humble-gazebo-ros-pkgs \\
    ros-humble-stage-ros2''',
        'pip': 'numpy matplotlib',
        'devices': '',
        'optional_devices': '',
        'todos': [
            ('configure_nav_params', '在 `nav2_params.yaml` 中调整 DWB controller / NavFn planner 关键参数（max_vel_x, inflation_radius, etc.）'),
            ('write_goal_sender', '用 NavigateToPose Action client 发送目标点；订阅 feedback 并打印进度'),
            ('measure_metrics', '记录 5 次导航任务：成功率、平均时长、平均路径长度，写入报告'),
        ],
        'run': '''# 1. 启动 Gazebo + TurtleBot3
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py &

# 2. SLAM 建图（手动键盘控制走一圈）
ros2 launch nav2_fusion slam.launch.py &
ros2 run turtlebot3_teleop teleop_keyboard

# 3. 保存地图
ros2 run nav2_map_server map_saver_cli -f my_map

# 4. 启动 Nav2 自主导航
ros2 launch nav2_fusion nav.launch.py map:=my_map.yaml''',
    },
    'p06-gesture-control': {
        'title': '项目 6：基于视频的手势识别命令',
        'level': '⭐⭐⭐',
        'tech': 'MediaPipe Hands + ROS2',
        'goal': '从手势演示视频识别手势序列，转换成 Twist 命令保存为 ROS bag，可在 Turtlesim 回放',
        'data_source': '''课程提供 6 个手势演示视频（每段 5-10 秒）：
- `demo/gesture_palm.mp4` (张开手掌 = 停止)
- `demo/gesture_fist.mp4` (拳头 = 前进)
- `demo/gesture_point_left.mp4` (食指向左 = 左转)
- `demo/gesture_point_right.mp4` (食指向右 = 右转)
- `demo/gesture_thumbs_up.mp4` (竖大拇指 = 加速)
- `demo/gesture_mixed.mp4` (混合手势序列)''',
        'hardware_modes': '''| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认** | `demo/*.mp4` 手势视频 | 命令序列 + Turtlesim 轨迹图 |
| 🟡 **扩展（有摄像头）** | `/dev/video0` | 实时手势 → Twist |''',
        'apt': 'ros-humble-turtlesim ros-humble-cv-bridge',
        'pip': 'mediapipe opencv-python numpy matplotlib',
        'devices': '',
        'optional_devices': '/dev/video0',
        'todos': [
            ('extract_landmarks', '用 `mp.solutions.hands` 处理视频每一帧，得到 21 个手部关键点的 (x,y,z)'),
            ('classify_gesture', '基于关键点的相对位置和角度，分类 5 种手势（不用深度学习，纯几何规则）'),
            ('gesture_to_twist_sequence', '把视频识别出的手势按时间顺序输出 Twist 序列（带时间戳）'),
        ],
        'run': '''# 处理单个视频
python -m gesture_control.run --video demo/gesture_mixed.mp4 \\
    --output commands.csv --bag commands.bag

# 在 Turtlesim 上回放
ros2 run turtlesim turtlesim_node &
ros2 bag play commands.bag''',
    },
    'p07-patrol-robot': {
        'title': '项目 7：Gazebo 仿真 + YOLO 智能巡检',
        'level': '⭐⭐⭐⭐',
        'tech': 'Gazebo + Nav2 + YOLO + 报告生成',
        'goal': '机器人在仿真城市/办公室自动巡检，发现人/车辆等关键目标时停下并生成异常报告',
        'data_source': '''✅ **完全仿真**：
- Gazebo aws_robomaker_hospital_world（医院场景）
- Gazebo turtlebot3_house（住宅场景）
- 巡检点：`config/waypoints.yaml`（10 个预设点）
- YOLO 模型：yolov8n.pt（4.7MB，CPU 推理）''',
        'hardware_modes': '''| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认（纯仿真）** | Gazebo 内置场景 | 巡检视频 + 异常报告 PDF |
| 🟢 **扩展（KITTI bag）** | KITTI 城市场景 bag | 静态场景的异常检测分析 |''',
        'apt': '''ros-humble-nav2-bringup ros-humble-turtlebot3-* \\
    ros-humble-gazebo-ros-pkgs ros-humble-cv-bridge''',
        'pip': 'ultralytics matplotlib reportlab pdfkit',
        'devices': '',
        'optional_devices': '',
        'todos': [
            ('waypoints_publisher', '从 YAML 读取巡检点，按顺序通过 Nav2 Action 发送，等待完成后切下一个'),
            ('detect_and_log', '在每个巡检点暂停 3 秒，用 YOLO 检测仿真相机话题，记录"位置+时间+检测到的类别"'),
            ('generate_pdf_report', '用 reportlab 生成 PDF 报告，包含地图轨迹、检测时间线、各类别统计图'),
        ],
        'run': '''# 启动仿真环境
ros2 launch patrol_robot full_stack.launch.py world:=hospital

# 启动巡检任务
ros2 run patrol_robot mission_executor --waypoints config/waypoints.yaml

# 完成后查看报告
xdg-open patrol_report.pdf''',
    },
    'p08-face-access': {
        'title': '项目 8：基于人脸数据集的识别系统',
        'level': '⭐⭐⭐⭐',
        'tech': 'face_recognition (dlib) + SQLite + ROS2',
        'goal': '用公开人脸数据集训练注册库，对测试集图片做人脸识别，计算准确率/召回率',
        'data_source': '''课程提供数据集（已过滤许可允许的子集）：
- `demo/known_faces/`：10 个人，每人 5 张训练照片
- `demo/test_faces/`：50 张测试照片（含已注册和陌生人）
- `demo/test_labels.csv`：测试集真值标注

学生也可用：
- LFW (http://vis-www.cs.umass.edu/lfw/)
- 自己和朋友的照片（合规收集，并签同意书）''',
        'hardware_modes': '''| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认** | `demo/test_faces/*.jpg` | accuracy_report.json |
| 🟡 **扩展（有摄像头）** | `/dev/video0` | 实时识别+开门信号 |''',
        'apt': 'cmake build-essential libboost-all-dev libopenblas-dev libsqlite3-dev',
        'pip': 'face_recognition dlib opencv-python sqlite3 numpy',
        'devices': '',
        'optional_devices': '/dev/video0',
        'todos': [
            ('enroll_known_faces', '遍历 `known_faces/<人名>/*.jpg`，提取 128 维 face encoding，存入 SQLite'),
            ('recognize_image', '加载测试图片，提取 encoding，与数据库比对（threshold=0.6），返回识别结果'),
            ('compute_metrics', '在测试集上跑识别，计算 confusion matrix + 准确率/精度/召回率/F1'),
        ],
        'run': '''# 1. 注册已知人脸
python -m face_access.enroll --dir demo/known_faces --db faces.db

# 2. 在测试集上评估
python -m face_access.evaluate --test demo/test_faces \\
    --labels demo/test_labels.csv --db faces.db

# 输出：accuracy_report.json + confusion_matrix.png''',
    },
    'p09-arm-grasp': {
        'title': '项目 9：PyBullet 机械臂仿真抓取',
        'level': '⭐⭐⭐⭐⭐',
        'tech': 'PyBullet + 内置 Kuka/Franka URDF + 视觉伺服',
        'goal': '在 PyBullet 仿真中：机械臂识别桌面方块位置 → 规划抓取 → 放入指定箱子',
        'data_source': '''✅ **完全仿真**：
- 机械臂：PyBullet 自带 Kuka iiwa（7 DoF）/ Franka Panda
- 物体：随机放置的彩色方块（红/绿/蓝各 3 个）
- 仿真相机：PyBullet 内置（不需要真实摄像头）''',
        'hardware_modes': '''| 模式 | 工具 |
|------|------|
| 🟢 **默认** | PyBullet 仿真（CPU 跑得动） |
| 🟢 **可选** | MoveIt2 + Gazebo（更高保真，需更多 CPU/RAM） |''',
        'apt': '',
        'pip': 'pybullet numpy opencv-python matplotlib',
        'devices': '',
        'optional_devices': '',
        'todos': [
            ('detect_blocks', '从 PyBullet 仿真相机获取 RGB+depth，用 OpenCV 阈值分割检测彩色方块的世界坐标'),
            ('inverse_kinematics', '用 `p.calculateInverseKinematics` 给定目标位姿，求 7 DoF 关节角'),
            ('pick_and_place', '编排完整流程：靠近 → 闭合夹爪 → 抬起 → 移到箱子 → 释放'),
        ],
        'run': '''python -m arm_grasp.run --robot kuka --target_color red \\
    --save_video grasp.mp4''',
    },
    'p10-quadruped': {
        'title': '项目 10：PyBullet 四足机器人步态优化',
        'level': '⭐⭐⭐⭐⭐',
        'tech': 'PyBullet + Trot 步态 + CMA-ES 参数优化',
        'goal': '让 Laikago 四足机器人在仿真中实现 Trot 步态走直线，并用 CMA-ES 自动调参提升速度',
        'data_source': '''✅ **完全仿真**：
- 模型：PyBullet 自带 Laikago URDF（也支持 A1、Anymal）
- 地形：平地 / 斜坡 / 阶梯（来自 pybullet_data）''',
        'hardware_modes': '''| 模式 | 资源 |
|------|------|
| 🟢 **默认** | PyBullet 仿真，CPU 单核可跑 |
| 🟢 **加速可选** | 关闭 GUI 渲染（headless）跑参数搜索更快 |''',
        'apt': '',
        'pip': 'pybullet numpy matplotlib cma',
        'devices': '',
        'optional_devices': '',
        'todos': [
            ('trot_phase_generator', '生成 4 条腿的 Trot 步态相位（对角线腿同步，相位相差 π）'),
            ('inverse_kinematics_leg', '给定足端目标位置 (x,y,z)，反解出髋/大腿/小腿关节角度'),
            ('optimize_gait_params', '用 CMA-ES 优化 [步频, 步长, 抬腿高度] 三个参数，目标是 10 秒内走得最远'),
        ],
        'run': '''# 默认参数走一遍
python -m quadruped.run_trot --duration 10

# 用 CMA-ES 自动调参（headless 模式更快）
python -m quadruped.optimize --headless --iters 50

# 用最优参数跑并录像
python -m quadruped.run_trot --params best_params.npy --save_video trot.mp4''',
    },
}


def render_readme(name, info):
    todo_section = ""
    for i, (fname, desc) in enumerate(info['todos'], 1):
        todo_section += f"### TODO {i}：`{fname}`\n\n{desc}\n\n"

    optional = info.get('optional_devices', '')
    extension_note = ""
    if optional:
        extension_note = f"\n## 🔌 扩展：使用真实硬件\n\n如果你有 `{optional}`，把它加到 `docker-compose.yml` 的 `devices:` 字段，然后用 `--source camera` 参数运行。但**不是必须**。\n"

    return f"""# {info['title']}

> {info['level']} · 技术：{info['tech']}

## 🎯 项目目标

{info['goal']}

## 📦 数据来源（无需任何硬件）

{info['data_source']}

## ⚙️ 运行模式

{info['hardware_modes']}

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
{info['run']}
```

## ✍️ 你要做的（3 个 TODO 函数）

{todo_section}

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
{extension_note}
## 💡 提示

- 把 `templates/` 下的骨架代码读一遍，理解整体流程
- 不会写时去看 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) 或官方教程
- **卡住超过 30 分钟立即在课程群提问**，不要硬磕

## 🌟 加分项

- 录制 2-3 分钟的演示视频上传
- 在 README 中写技术博客式的开发记录
- 测试自己的算法在更多数据上的效果
- 提供完整的可视化（matplotlib/rviz）
"""


def render_dockerfile(name, info):
    apt = info['apt'].strip()
    pip_packages = info['pip']
    extra_apt = f" {apt}" if apt else ""
    return f"""FROM osrf/ros:humble-desktop-full

RUN apt-get update && apt-get install -y \\
    python3-pip git vim wget curl x11-apps mesa-utils libgl1-mesa-glx{extra_apt} \\
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \\
    numpy opencv-python pytest rich loguru \\
    {pip_packages}

WORKDIR /workspace
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc \\
 && echo "source /workspace/install/setup.bash 2>/dev/null || true" >> /root/.bashrc

ENV DISPLAY=:0 QT_X11_NO_MITSHM=1
CMD ["/bin/bash"]
"""


def render_compose(name, info):
    """默认不挂载摄像头/麦克风，注释掉作为可选项"""
    optional = info.get('optional_devices', '').split()
    optional_lines = ""
    for dev in optional:
        optional_lines += f"      # - {dev}:{dev}  # 取消注释以启用 {dev}\n"

    optional_devices_block = ""
    if optional:
        optional_devices_block = "    # 取消注释下面的设备和卷映射以使用真实硬件\n    # devices:\n"
        for dev in optional:
            optional_devices_block += f"    #   - {dev}\n"

    return f"""services:
  dev:
    build: .
    image: airobot-class/{name}:latest
    container_name: {name}
    network_mode: host
    privileged: false
    environment:
      - DISPLAY=${{DISPLAY:-:0}}
      - QT_X11_NO_MITSHM=1
      - ROS_DOMAIN_ID=42
    volumes:
      - .:/workspace
      - /tmp/.X11-unix:/tmp/.X11-unix
{optional_lines.rstrip() if optional_lines else ''}
{optional_devices_block}
    stdin_open: true
    tty: true
    command: /bin/bash
"""


def render_demo_download_script(name, info):
    """为每个项目生成数据集下载脚本占位"""
    return f"""#!/bin/bash
# 项目 {name} 数据集下载脚本
# 课程组会维护这个脚本，提供必要的演示数据
set -e

DEMO_DIR="$(dirname "$0")"
cd "$DEMO_DIR"

echo "📥 下载 {name} 演示数据..."

# TODO: 课程组在此添加具体的下载逻辑
# 示例：
# wget https://course.a-real.me/data/{name}/sample.mp4 -O sample.mp4
# wget https://course.a-real.me/data/{name}/test_data.bag -O test_data.bag

echo "✅ 数据下载完成（占位脚本，请联系教师获取实际数据）"
"""


def main():
    base = Path(__file__).resolve().parent.parent
    for name, info in PROJECTS.items():
        proj_dir = base / name
        proj_dir.mkdir(parents=True, exist_ok=True)
        (proj_dir / 'README.md').write_text(render_readme(name, info))
        (proj_dir / 'Dockerfile').write_text(render_dockerfile(name, info))
        (proj_dir / 'docker-compose.yml').write_text(render_compose(name, info))
        # 创建 demo 数据目录 + 占位脚本
        demo_dir = proj_dir / 'demo'
        demo_dir.mkdir(exist_ok=True)
        (demo_dir / 'download_data.sh').write_text(render_demo_download_script(name, info))
        os.chmod(demo_dir / 'download_data.sh', 0o755)
        # 创建 src 目录占位
        (proj_dir / 'src').mkdir(exist_ok=True)
        (proj_dir / 'src' / '.gitkeep').touch()
        # test 目录
        (proj_dir / 'test').mkdir(exist_ok=True)
        (proj_dir / 'test' / '.gitkeep').touch()
        print(f"  ✅ {name}: {info['title']}")
    print(f"\n生成完毕：{len(PROJECTS)} 个项目模板（默认无硬件可完成）")


if __name__ == '__main__':
    main()

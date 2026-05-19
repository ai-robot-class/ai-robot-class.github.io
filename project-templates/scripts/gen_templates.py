"""快速生成项目模板的脚本"""
import os
from pathlib import Path

PROJECTS = {
    'p02-voice-turtle': {
        'title': '项目 2：语音控制小乌龟',
        'level': '⭐⭐',
        'tech': 'SpeechRecognition + pyttsx3 + ROS2 + Turtlesim',
        'goal': '用语音指令"前进/后退/左转/右转/停止"控制 Turtlesim',
        'apt': 'ros-humble-turtlesim portaudio19-dev libsndfile1 espeak espeak-ng pulseaudio',
        'pip': 'speech_recognition pyttsx3 pyaudio gtts',
        'devices': '/dev/snd',
        'todos': [
            ('recognize_command', '调用 sr.Recognizer().recognize_google 识别中文语音，返回识别字符串'),
            ('parse_command', '把识别到的文字映射为 Twist（"前进"→linear.x=1, "左转"→angular.z=1 等）'),
            ('voice_feedback', '识别成功后用 pyttsx3 播报"已收到命令：xxx"'),
        ],
        'run': '''ros2 run turtlesim turtlesim_node &
ros2 run voice_turtle voice_node''',
    },
    'p03-yolo-detector': {
        'title': '项目 3：简单目标检测系统',
        'level': '⭐⭐⭐',
        'tech': 'Ultralytics YOLOv8 + ROS2 + Image_view',
        'goal': '从摄像头/视频实时检测物体，发布检测结果到 ROS2 话题',
        'apt': 'ros-humble-cv-bridge ros-humble-image-view',
        'pip': 'ultralytics opencv-python numpy',
        'devices': '/dev/video0',
        'todos': [
            ('detect_objects', '调用 YOLO 模型推理（self.model(frame)），返回 boxes + labels + confs'),
            ('publish_detections', '把检测结果封装为 vision_msgs/Detection2DArray 并发布'),
            ('draw_overlay', '在图像上画检测框 + 标签 + 置信度，并发布标注后图像'),
        ],
        'run': '''ros2 run yolo_detector detector_node
# 另一终端查看：
ros2 run rqt_image_view rqt_image_view''',
    },
    'p04-object-tracker': {
        'title': '项目 4：物体追踪与跟随',
        'level': '⭐⭐⭐',
        'tech': 'YOLO + SORT 多目标跟踪 + ROS2',
        'goal': '识别+持续跟踪特定物体，给出 ID 标号；让机器人跟随保持安全距离',
        'apt': 'ros-humble-cv-bridge',
        'pip': 'ultralytics filterpy lap scipy',
        'devices': '/dev/video0',
        'todos': [
            ('init_tracker', '初始化 SORT 跟踪器（构造卡尔曼滤波器参数）'),
            ('update_tracker', '每帧用 YOLO 检测结果更新 SORT，返回稳定的 ID 列表'),
            ('compute_follow_cmd', '根据目标 bbox 大小（远近）和位置（左右），输出 Twist 让机器人跟随并保持 1m 距离'),
        ],
        'run': '''ros2 launch object_tracker tracker.launch.py''',
    },
    'p05-nav2-fusion': {
        'title': '项目 5：多传感器融合导航',
        'level': '⭐⭐⭐⭐',
        'tech': 'ROS2 Nav2 + slam_toolbox + 仿真环境（TurtleBot3）',
        'goal': '让仿真机器人在未知环境中 SLAM 建图 → 保存地图 → 用 Nav2 自主导航避障',
        'apt': '''ros-humble-nav2-bringup ros-humble-slam-toolbox \\
    ros-humble-turtlebot3-* ros-humble-gazebo-ros-pkgs''',
        'pip': 'numpy matplotlib',
        'devices': '',
        'todos': [
            ('configure_nav2_params', '修改 nav2_params.yaml 中的 controller / planner 参数（DWB + NavFn）'),
            ('write_lifecycle_manager', '编写 lifecycle 自动启动脚本，确保所有 Nav2 节点正常激活'),
            ('add_goal_publisher', '订阅 /goal 话题，把目标点格式化为 NavigateToPose action 调用'),
        ],
        'run': '''# 1. 启动仿真
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# 2. SLAM 建图
ros2 launch nav2_fusion slam.launch.py

# 3. 用键盘走一圈，保存地图后切换 Nav2
ros2 launch nav2_fusion nav.launch.py map:=my_map.yaml''',
    },
    'p06-gesture-control': {
        'title': '项目 6：手势识别控制',
        'level': '⭐⭐⭐',
        'tech': 'MediaPipe Hands + ROS2',
        'goal': '用手势（手掌 / 拳头 / 食指方向）控制机器人运动',
        'apt': 'ros-humble-cv-bridge',
        'pip': 'mediapipe opencv-python',
        'devices': '/dev/video0',
        'todos': [
            ('detect_landmarks', '用 mp.solutions.hands 检测 21 个手部关键点'),
            ('classify_gesture', '根据关键点位置判断手势：手掌张开 / 拳头 / 指向 X 方向（共 5 类）'),
            ('gesture_to_twist', '把手势映射为 Twist 命令（手掌=停止，拳头=前进，食指方向=转弯方向）'),
        ],
        'run': '''ros2 run gesture_control gesture_node''',
    },
    'p07-patrol-robot': {
        'title': '项目 7：智能巡检机器人',
        'level': '⭐⭐⭐⭐',
        'tech': 'SLAM + YOLO + TTS（语音播报）+ ROS2',
        'goal': '机器人按预设路径巡检 → 发现目标自动停下 → 播报"检测到 XXX"',
        'apt': '''ros-humble-nav2-bringup ros-humble-slam-toolbox \\
    ros-humble-turtlebot3-* ros-humble-gazebo-ros-pkgs \\
    espeak espeak-ng pulseaudio''',
        'pip': 'ultralytics pyttsx3 gtts',
        'devices': '/dev/snd',
        'todos': [
            ('waypoints_publisher', '从 waypoints.yaml 读取巡检点，按顺序发送给 Nav2'),
            ('detect_anomaly', '订阅 YOLO 检测话题，发现 "person" 或 "fire" 等关键类别时返回告警'),
            ('voice_alarm', '收到告警后停下机器人，用 TTS 播报告警内容并写入 anomaly_log.txt'),
        ],
        'run': '''ros2 launch patrol_robot full_stack.launch.py''',
    },
    'p08-face-access': {
        'title': '项目 8：人脸识别门禁系统',
        'level': '⭐⭐⭐⭐',
        'tech': 'face_recognition (dlib) + SQLite + ROS2',
        'goal': '摄像头识别人脸 → 比对数据库 → 已注册=开门，陌生人=报警',
        'apt': '''cmake build-essential libboost-all-dev libopenblas-dev \\
    ros-humble-cv-bridge''',
        'pip': 'face_recognition dlib opencv-python',
        'devices': '/dev/video0',
        'todos': [
            ('enroll_face', '从图片提取人脸 encoding，写入 SQLite 数据库（id, name, encoding）'),
            ('recognize_face', '实时摄像头帧 → 提取 encoding → 与数据库比对，返回 name 或 "stranger"'),
            ('control_door', '识别成功发布 "/door/open" 话题；陌生人发布 "/alarm" 并保存抓拍照片'),
        ],
        'run': '''# 注册人脸
ros2 run face_access enroll --name "张三" --image alice.jpg

# 启动识别
ros2 run face_access recognizer_node''',
    },
    'p09-arm-grasp': {
        'title': '项目 9：机械臂物体抓取',
        'level': '⭐⭐⭐⭐⭐',
        'tech': 'MoveIt2 + 视觉定位 + ROS2',
        'goal': '相机识别物体 3D 位置 → 用逆运动学规划路径 → 机械臂抓取放到目标盒子',
        'apt': '''ros-humble-moveit ros-humble-moveit-ros-visualization \\
    ros-humble-moveit-resources ros-humble-cv-bridge''',
        'pip': 'ultralytics open3d numpy',
        'devices': '',
        'todos': [
            ('detect_object_3d', '从 RGB-D 相机数据，用 YOLO 检测 + 深度图反投影，得到物体世界坐标 (x,y,z)'),
            ('plan_grasp', '用 MoveIt MoveGroup API 规划机械臂从初始位置到抓取位姿的路径'),
            ('execute_pick_and_place', '编排完整流程：移到上方 → 下降抓取 → 抬起 → 移到目标点 → 释放'),
        ],
        'run': '''ros2 launch arm_grasp moveit_demo.launch.py
# 等 RViz 启动后：
ros2 service call /trigger_grasp std_srvs/srv/Trigger {}''',
    },
    'p10-quadruped': {
        'title': '项目 10：四足机器人基础控制',
        'level': '⭐⭐⭐⭐⭐',
        'tech': 'PyBullet + 步态生成 + 控制算法',
        'goal': '在 PyBullet 中让四足机器人（Laikago）实现 Trot 步态走直线',
        'apt': '',
        'pip': 'pybullet numpy matplotlib',
        'devices': '',
        'todos': [
            ('compute_leg_phase', '为 4 条腿生成 Trot 步态的相位（对角腿同步，相差半周期）'),
            ('inverse_kinematics_leg', '给定目标足端位置 (x, y, z)，反解出髋/大腿/小腿 3 个关节角度'),
            ('gait_step', '在每个仿真步：根据时间 t 计算每条腿当前应在的足端位置 → IK → 发关节指令'),
        ],
        'run': '''python -m quadruped.run_trot --frequency 1.5''',
    },
}


def render_readme(name, info):
    todo_section = ""
    for i, (fname, desc) in enumerate(info['todos'], 1):
        todo_section += f"### TODO {i}：`{fname}`\n\n{desc}\n\n```python\n# 在源码中找到这个函数，按注释提示实现\n```\n\n"
    return f"""# {info['title']}

> {info['level']} · 技术：{info['tech']}

## 🎯 项目目标

{info['goal']}

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
{info['run']}
```

## ✍️ 你要做的（TODO 列表）

{todo_section}

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
"""


def render_dockerfile(name, info):
    apt = info['apt'].strip()
    pip_packages = info['pip']
    extra_apt = f" {apt}" if apt else ""
    return f"""FROM osrf/ros:humble-desktop-full

RUN apt-get update && apt-get install -y \\
    python3-pip git vim x11-apps mesa-utils libgl1-mesa-glx{extra_apt} \\
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
    devices = info.get('devices', '')
    dev_lines = ""
    if devices:
        for dev in devices.split():
            dev_lines += f"      - {dev}\n"
        dev_section = f"""    devices:
{dev_lines.rstrip()}
    volumes:
      - .:/workspace
      - /tmp/.X11-unix:/tmp/.X11-unix
{''.join(f'      - {d}:{d}{chr(10)}' for d in devices.split()).rstrip()}"""
    else:
        dev_section = """    volumes:
      - .:/workspace
      - /tmp/.X11-unix:/tmp/.X11-unix"""
    return f"""services:
  dev:
    build: .
    image: airobot-class/{name}:latest
    container_name: {name}
    network_mode: host
    privileged: true
    environment:
      - DISPLAY=${{DISPLAY:-:0}}
      - QT_X11_NO_MITSHM=1
      - ROS_DOMAIN_ID=42
{dev_section}
    stdin_open: true
    tty: true
    command: /bin/bash
"""


def main():
    base = Path(__file__).resolve().parent.parent
    for name, info in PROJECTS.items():
        proj_dir = base / name
        proj_dir.mkdir(parents=True, exist_ok=True)
        (proj_dir / 'README.md').write_text(render_readme(name, info))
        (proj_dir / 'Dockerfile').write_text(render_dockerfile(name, info))
        (proj_dir / 'docker-compose.yml').write_text(render_compose(name, info))
        # 创建 src 目录占位
        (proj_dir / 'src').mkdir(exist_ok=True)
        (proj_dir / 'src' / '.gitkeep').touch()
        print(f"  ✅ {name}: {info['title']}")
    print(f"\n生成完毕：{len(PROJECTS)} 个项目模板")


if __name__ == '__main__':
    main()

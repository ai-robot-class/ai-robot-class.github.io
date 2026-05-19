# 第12周：视觉与语音入门 + 期末项目启动

**课时**: 3小时（一次课）

---

## 📋 本周课程大纲

| 模块 | 时间 | 主题 | 内容 |
|------|------|------|------|
| 模块1 | 60分钟 | OpenCV视觉处理 | 图像处理+颜色检测 |
| 模块2 | 40分钟 | 语音技术入门 | 识别与合成 |
| 茶歇 | 10分钟 | 休息 | - |
| 模块3 | 70分钟 | 期末项目启动 | 分组选题+计划 |

---

## 第一模块：OpenCV视觉处理（60分钟）

### ⏱️ 时间分配

| 环节 | 时间 | 内容 |
|------|------|------|
| 讲解+演示 | 30分钟 | OpenCV基础快速入门 |
| 实践 | 30分钟 | 颜色检测与追踪实战 |

---

## 12.1 OpenCV快速入门

> OpenCV是最流行的计算机视觉库，简单易用！

### 12.1.1 安装与验证

```bash
# 安装OpenCV
pip install opencv-python opencv-contrib-python

# 验证
python3 -c "import cv2; print(f'OpenCV版本: {cv2.__version__}')"
```

### 12.1.2 图像基本操作（15分钟掌握）

```python
import cv2
import numpy as np

# 1. 读取图像
img = cv2.imread('robot.jpg')
print(f"图像形状: {img.shape}")  # (高, 宽, 通道)

# 2. 显示图像
cv2.imshow('Original', img)
cv2.waitKey(0)  # 按任意键关闭
cv2.destroyAllWindows()

# 3. 颜色空间转换
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰度图
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)    # HSV颜色空间

# 4. 图像缩放
resized = cv2.resize(img, (640, 480))

# 5. 图像裁剪（数组切片）
cropped = img[100:300, 200:400]

# 6. 绘制图形
cv2.rectangle(img, (50, 50), (200, 200), (0, 255, 0), 2)  # 绿色矩形
cv2.circle(img, (320, 240), 50, (0, 0, 255), -1)         # 红色实心圆
cv2.putText(img, 'Robot', (100, 100), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

# 7. 保存图像
cv2.imwrite('output.jpg', img)
```

### 12.1.3 边缘检测（5分钟掌握）

```python
# Canny边缘检测
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 50, 150)

cv2.imshow('Edges', edges)
cv2.waitKey(0)
```

---

## 12.2 颜色检测与追踪

> 最实用的入门技术：通过颜色追踪物体！

### 12.2.1 HSV颜色空间

```
为什么用HSV而不是RGB？

RGB: 受光照影响大
HSV: 颜色、亮度分离
     H (Hue): 色调 (0-180)
     S (Saturation): 饱和度 (0-255)
     V (Value): 明度 (0-255)

常见颜色HSV范围：
• 红色: [0, 120, 70] ~ [10, 255, 255]
• 绿色: [40, 40, 40] ~ [80, 255, 255]
• 蓝色: [100, 43, 46] ~ [124, 255, 255]
```

### 12.2.2 颜色检测实战

```python
import cv2
import numpy as np

# 打开摄像头
cap = cv2.VideoCapture(0)

# 定义红色范围（HSV）
lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 转HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 颜色过滤（创建mask）
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    # 形态学操作（去噪）
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # 找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                    cv2.CHAIN_APPROX_SIMPLE)
    
    # 处理最大轮廓（追踪最大红色物体）
    if contours:
        largest = max(contours, key=cv2.contourArea)
        
        # 计算外接矩形
        x, y, w, h = cv2.boundingRect(largest)
        
        # 计算中心点
        cx, cy = x + w//2, y + h//2
        
        # 绘制结果
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        cv2.putText(frame, f'Red Object ({cx}, {cy})', (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # 显示
    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### 12.2.3 实践练习：颜色调节工具

```python
def nothing(x):
    pass

# 创建窗口和滑块
cv2.namedWindow('HSV Tuner')
cv2.createTrackbar('H_min', 'HSV Tuner', 0, 180, nothing)
cv2.createTrackbar('H_max', 'HSV Tuner', 180, 180, nothing)
cv2.createTrackbar('S_min', 'HSV Tuner', 0, 255, nothing)
cv2.createTrackbar('S_max', 'HSV Tuner', 255, 255, nothing)
cv2.createTrackbar('V_min', 'HSV Tuner', 0, 255, nothing)
cv2.createTrackbar('V_max', 'HSV Tuner', 255, 255, nothing)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 读取滑块值
    h_min = cv2.getTrackbarPos('H_min', 'HSV Tuner')
    h_max = cv2.getTrackbarPos('H_max', 'HSV Tuner')
    s_min = cv2.getTrackbarPos('S_min', 'HSV Tuner')
    s_max = cv2.getTrackbarPos('S_max', 'HSV Tuner')
    v_min = cv2.getTrackbarPos('V_min', 'HSV Tuner')
    v_max = cv2.getTrackbarPos('V_max', 'HSV Tuner')
    
    # 创建mask
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower, upper)
    
    # 应用mask
    result = cv2.bitwise_and(frame, frame, mask=mask)
    
    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)
    cv2.imshow('Result', result)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 第二模块：语音技术入门（40分钟）

### ⏱️ 时间分配

| 环节 | 时间 | 内容 |
|------|------|------|
| 讲解+演示 | 20分钟 | 语音识别入门 |
| 讲解+演示 | 20分钟 | 语音合成入门 |

---

## 12.3 语音识别入门

> 让机器人"听懂"人话

### 12.3.1 安装语音库

```bash
# 语音识别
pip install SpeechRecognition pyaudio

# 中文语音识别（可选）
pip install paddlespeech

# 文字转语音
pip install pyttsx3 gTTS
```

### 12.3.2 简单语音识别

```python
import speech_recognition as sr

# 创建识别器
recognizer = sr.Recognizer()

# 使用麦克风
with sr.Microphone() as source:
    print("请说话...")
    
    # 调整环境噪音
    recognizer.adjust_for_ambient_noise(source)
    
    # 录音
    audio = recognizer.listen(source)
    
    print("识别中...")
    
    try:
        # 使用Google语音识别（需要网络）
        text = recognizer.recognize_google(audio, language='zh-CN')
        print(f"你说的是: {text}")
        
    except sr.UnknownValueError:
        print("听不清楚")
    except sr.RequestError:
        print("识别服务出错")
```

### 12.3.3 语音命令识别

```python
import speech_recognition as sr

def recognize_command():
    """识别语音命令"""
    recognizer = sr.Recognizer()
    
    # 定义命令词
    commands = {
        '前进': 'forward',
        '后退': 'backward',
        '左转': 'left',
        '右转': 'right',
        '停止': 'stop'
    }
    
    with sr.Microphone() as source:
        print("等待命令...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio, language='zh-CN')
            print(f"识别到: {text}")
            
            # 匹配命令
            for cmd, action in commands.items():
                if cmd in text:
                    print(f"执行: {action}")
                    return action
            
            print("未识别到有效命令")
            return None
            
        except:
            print("识别失败")
            return None

# 测试
while True:
    cmd = recognize_command()
    if cmd == 'stop':
        break
```

---

## 12.4 语音合成入门

> 让机器人"说话"

### 12.4.1 离线语音合成（pyttsx3）

```python
import pyttsx3

# 创建引擎
engine = pyttsx3.init()

# 设置属性
engine.setProperty('rate', 150)     # 语速
engine.setProperty('volume', 0.9)   # 音量

# 朗读文本
engine.say("你好，我是机器人")
engine.say("Hello, I am a robot")

# 等待完成
engine.runAndWait()
```

### 12.4.2 在线语音合成（gTTS）

```python
from gtts import gTTS
import os

# 中文
text_zh = "欢迎来到机器人课程"
tts = gTTS(text=text_zh, lang='zh-cn')
tts.save("welcome_zh.mp3")

# 英文
text_en = "Welcome to robotics course"
tts = gTTS(text=text_en, lang='en')
tts.save("welcome_en.mp3")

# 播放
os.system("mpg123 welcome_zh.mp3")  # Linux
# os.system("start welcome_zh.mp3")  # Windows
```

### 12.4.3 简单对话机器人

```python
import speech_recognition as sr
import pyttsx3

class VoiceBot:
    """简单语音机器人"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
    
    def listen(self):
        """听"""
        with sr.Microphone() as source:
            print("机器人在听...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, timeout=5)
            
            try:
                text = self.recognizer.recognize_google(audio, language='zh-CN')
                print(f"用户: {text}")
                return text
            except:
                return None
    
    def speak(self, text):
        """说"""
        print(f"机器人: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def respond(self, user_input):
        """简单回应"""
        if '你好' in user_input:
            return "你好，我是机器人"
        elif '名字' in user_input:
            return "我叫小机"
        elif '天气' in user_input:
            return "今天天气不错"
        elif '再见' in user_input:
            return "再见"
        else:
            return "我听不懂"
    
    def run(self):
        """运行"""
        self.speak("你好，我是语音机器人")
        
        while True:
            user_input = self.listen()
            
            if user_input:
                response = self.respond(user_input)
                self.speak(response)
                
                if '再见' in user_input:
                    break

# 运行
if __name__ == '__main__':
    bot = VoiceBot()
    bot.run()
```

---

## 第三模块：期末项目启动（70分钟）

### 12.5.1 项目要求说明（20分钟）

**项目时间线**：
- **第12周**：分组、选题、制定计划
- **第13周**：实施、调试、准备展示
- **第14周**（如有）：项目展示与答辩

**项目要求**：
1. **组队**：2-3人一组，或单人完成简单项目
2. **选题**：从给定题目中选择，或自拟题目（需审批）
3. **提交物**：
   - 代码（GitHub仓库）
   - 演示视频（2-5分钟）
   - 项目报告（README.md）
   - 现场演示（可选）

**评分标准**：
| 项目 | 占比 | 说明 |
|------|------|------|
| 功能完整度 | 40% | 是否实现核心功能 |
| 技术难度 | 30% | 技术复杂度与创新性 |
| 代码质量 | 15% | 代码规范、注释、可读性 |
| 文档报告 | 15% | README、演示视频质量 |

---

### 12.5.2 项目选题（10个方向）

> 💡 **每个项目都已为你准备好 Docker 仿真环境 + 代码骨架**！
> 在 [`project-templates/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates) 目录中。
>
> ✅ 你只需要 `docker compose up -d` 启动环境，然后填写代码里 `# TODO:` 标注的核心算法部分（每个项目 3 个 TODO 函数）。
>
> ❌ 不用花时间配环境、装依赖、踩 ROS2 坑！



#### 📦 初级项目（适合单人或2人）

**1. 视觉颜色追踪机器人**
- **难度**: ⭐⭐
- **技术**: OpenCV颜色检测 + ROS2
- **目标**: 机器人追踪特定颜色物体移动
- **模板**: [`project-templates/p01-color-tracker/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p01-color-tracker)

**2. 语音控制小乌龟**
- **难度**: ⭐⭐
- **技术**: 语音识别 + ROS2 Turtlesim
- **目标**: 语音命令控制小乌龟运动
- **模板**: [`project-templates/p02-voice-turtle/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p02-voice-turtle)

**3. 简单目标检测系统**
- **难度**: ⭐⭐⭐
- **技术**: YOLO + ROS2
- **目标**: 摄像头实时检测并标注物体
- **模板**: [`project-templates/p03-yolo-detector/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p03-yolo-detector)

#### 🚀 中级项目（适合2-3人）

**4. 物体追踪与跟随**
- **难度**: ⭐⭐⭐
- **技术**: YOLO + Sort追踪 + ROS2
- **目标**: 机器人识别并跟随特定物体
- **模板**: [`project-templates/p04-object-tracker/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p04-object-tracker)

**5. 多传感器融合导航**
- **难度**: ⭐⭐⭐⭐
- **技术**: 相机 + 激光雷达 + ROS2 Nav2
- **目标**: 机器人自主避障导航
- **模板**: [`project-templates/p05-nav2-fusion/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p05-nav2-fusion)

**6. 手势识别控制**
- **难度**: ⭐⭐⭐
- **技术**: MediaPipe手势识别 + ROS2
- **目标**: 手势控制机器人运动
- **模板**: [`project-templates/p06-gesture-control/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p06-gesture-control)

#### 🏆 高级项目（适合3人或有基础）

**7. 智能巡检机器人**
- **难度**: ⭐⭐⭐⭐
- **技术**: SLAM + 目标检测 + 语音播报
- **目标**: 自主巡检并识别异常
- **模板**: [`project-templates/p07-patrol-robot/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p07-patrol-robot)

**8. 人脸识别门禁系统**
- **难度**: ⭐⭐⭐⭐
- **技术**: 人脸检测/识别 + 数据库 + ROS2
- **目标**: 识别授权人员并控制门禁
- **模板**: [`project-templates/p08-face-access/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p08-face-access)

**9. 机械臂物体抓取**
- **难度**: ⭐⭐⭐⭐⭐
- **技术**: 目标检测 + 逆运动学 + MoveIt
- **目标**: 识别物体位置并抓取
- **模板**: [`project-templates/p09-arm-grasp/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p09-arm-grasp)

**10. 四足机器人基础控制（第13周专题）**
- **难度**: ⭐⭐⭐⭐⭐
- **技术**: PyBullet仿真 + 步态生成
- **目标**: 四足机器人行走控制
- **扩展**: 地形适应
- **模板**: [`project-templates/p10-quadruped/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p10-quadruped)

---

### 12.5.3 📦 项目 Docker 模板使用指南

每个选题都在 `project-templates/p01-...` 到 `p10-...` 准备好：

```
p0X-xxxxxx/
├── README.md             # 项目说明 + 3 个核心 TODO 任务
├── Dockerfile            # 容器镜像（ROS2 Humble + 全部依赖）
├── docker-compose.yml    # 一键启动配置（GUI/摄像头/麦克风都准备好）
├── src/                  # 代码骨架（已写好 ROS2 框架，留 TODO 给你）
└── test/                 # 单元测试（提交前自测）
```

#### 🚀 使用流程（每位同学只需 5 步）

```bash
# 1. Fork 课程仓库到自己 GitHub，clone 到本地
git clone https://github.com/<你的用户名>/ai-robot-class.github.io.git
cd ai-robot-class.github.io/project-templates/p01-color-tracker  # 选你的项目

# 2. 启动容器（首次约 2-5 分钟拉镜像）
docker compose up -d

# 3. 进入容器开发
docker compose exec dev bash

# 4. 在容器内编译运行
colcon build && source install/setup.bash
# 找到 src/xxxx_node.py 中的 # TODO，开始写代码！

# 5. 完成后提交自己的 GitHub 仓库
git add . && git commit -m "完成 P01 颜色追踪核心" && git push
```

#### 🎯 评分聚焦在算法实现

容器配置和骨架代码**不计入评分**。评分点：

| 项目 | 占比 |
|------|------|
| 3 个 TODO 函数实现正确 | 40% |
| 实际运行效果（演示） | 30% |
| 代码质量（注释/命名） | 15% |
| 提供的单元测试通过 | 10% |
| README 报告 + 演示视频 | 5% |

#### 🛠️ 通用环境准备

##### 学生宿主机要求

- **Linux/WSL2**：`xhost +local:docker` 启用 GUI 转发
- **Mac**：用 `XQuartz` + `host.docker.internal:0`
- **Windows**：用 WSL2 + WSLg（Win11 自带）

```bash
# 一次性配置（Linux/WSL2）
xhost +local:docker
echo 'xhost +local:docker' >> ~/.bashrc
```

##### 验证 Docker 与 GUI

```bash
# 测试 X11 转发
docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
    osrf/ros:humble-desktop-full \
    bash -c "apt update && apt install -y x11-apps && xeyes"

# 应该弹出一对眼睛跟着鼠标转
```

#### 🐳 通用基础镜像

所有项目都基于 `osrf/ros:humble-desktop-full`，包含：

- **ROS2 Humble** 完整桌面版（RViz / Gazebo / rqt 全套）
- **OpenCV** 4.x + opencv-contrib
- **PyTorch** + Ultralytics YOLOv8
- **语音**：SpeechRecognition / pyttsx3 / gTTS / pyaudio
- **视觉**：MediaPipe / face_recognition / Open3D
- **仿真**：PyBullet / 多机器人 URDF

#### ⚙️ 如果想用 GPU 加速

```yaml
# 在 docker-compose.yml 中加入
services:
  dev:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics
```

需要先在宿主机装好 `nvidia-container-toolkit`。

---

### 12.5.4 项目分组与计划（30分钟）

**分组流程**：
1. 自由组队（2-3人）
2. 选择项目方向
3. 填写项目登记表

**项目登记表**：
```markdown
## 项目信息

- **项目名称**: _______________
- **项目编号**: (1-10)
- **组长**: _______________
- **组员**: _______________, _______________
- **GitHub仓库**: _______________

## 技术栈

- [ ] ROS2
- [ ] OpenCV
- [ ] YOLO
- [ ] 语音识别/合成
- [ ] 其他: _______________

## 时间计划

- **Week 12**: 
  - [ ] 完成环境搭建
  - [ ] 完成基本框架
  
- **Week 13**:
  - [ ] 实现核心功能
  - [ ] 测试与调试
  - [ ] 录制演示视频
  
- **Week 14** (如有):
  - [ ] 完善文档
  - [ ] 准备答辩
```

---

### 12.5.5 技术答疑与资源（20分钟）

**常见问题**：

1. **Q**: 没有真实机器人怎么办？
   **A**: 使用仿真环境（Gazebo/PyBullet/Webots）

2. **Q**: 摄像头/麦克风不可用？
   **A**: 使用录制的视频/音频文件测试

3. **Q**: 项目太难怎么办？
   **A**: 先实现简化版，逐步扩展功能

**推荐资源**：
- [ROS2官方教程](https://docs.ros.org/en/humble/Tutorials.html)
- [OpenCV教程](https://docs.opencv.org/4.x/d9/df8/tutorial_root.html)
- [YOLO文档](https://docs.ultralytics.com/)
- [课程GitHub示例](https://github.com/ai-robot-class/)

---

## 本周作业

### ✅ 必做

| 序号 | 任务 | 截止 | 完成 |
|------|------|------|------|
| 1 | 完成颜色检测实验 | 本周 | ☐ |
| 2 | 测试语音识别/合成 | 本周 | ☐ |
| 3 | 确定项目选题 | 本周五 | ☐ |
| 4 | 提交项目登记表 | 本周五 | ☐ |
| 5 | 创建GitHub仓库 | 本周日 | ☐ |

### 🌟 选做（加分）

- 实现HSV颜色调节工具
- 扩展语音对话功能
- 完成项目原型（Prototype）

---

## 参考文献

[1] Bradski, G. (2000). The OpenCV Library. *Dr. Dobb's Journal*.

[2] SpeechRecognition Documentation. https://pypi.org/project/SpeechRecognition/

[3] pyttsx3 Documentation. https://pyttsx3.readthedocs.io/

---

## 下周预告

> **第13周：四足机器人入门 + 期末项目实施**
> - 四足机器人基础概念
> - PyBullet仿真实战
> - 项目开发辅导

---

*第12周结束！项目正式启动，加油！*

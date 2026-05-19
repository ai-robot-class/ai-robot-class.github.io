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

### 12.5.2 项目选题（10个方向 · 默认无硬件可完成）

> 💯 **重要：所有项目重新设计为「无任何外设也能完成」！**
>
> 不论你电脑是否有摄像头、麦克风、独显，都能用**课程提供的数据集 / ROS bag / 仿真环境**完成项目。

#### 🎯 设计思路

| 数据源 | 项目数 | 来源 |
|--------|-------|------|
| 📹 视频 / 音频文件 | 3 个 | 课程组录制 |
| 🗂️ ROS bag（KITTI 等）| 1 个 | 复用 Week 6 数据 |
| 📊 公开数据集（MOT17、LFW）| 2 个 | 业界基准数据集 |
| 🏗️ 纯仿真（Gazebo / PyBullet）| 4 个 | 完全 CPU 可跑 |

每个项目同时提供 **🟢 默认（无硬件）** 和 **🟡 扩展（有硬件）** 两种模式，扩展模式作为加分项。

#### 📦 初级项目（适合单人或 2 人）

**1. 基于视频的颜色追踪 → ROS bag 输出** 🟢
- **难度**: ⭐⭐ · **数据源**: 课程提供 `colored_ball.mp4`
- **任务**: 视频追踪彩色物体 → 生成 cmd_vel ROS bag → Turtlesim 回放
- **技术**: OpenCV HSV + ROS2 bag
- **模板**: [`p01-color-tracker/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p01-color-tracker)

**2. 基于音频文件的语音命令解析** 🟢
- **难度**: ⭐⭐ · **数据源**: 课程提供 5 个预录中文 `.wav`
- **任务**: 离线语音识别（Vosk）→ 解析 Twist 序列 → 画轨迹 GIF
- **技术**: SpeechRecognition + Vosk **离线**模型 + Turtlesim
- **模板**: [`p02-voice-turtle/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p02-voice-turtle)

**3. KITTI 数据集物体检测可视化** 🟢
- **难度**: ⭐⭐⭐ · **数据源**: Week 6 用过的 KITTI ROS bag
- **任务**: YOLO 检测 → 发布 ROS topic → 生成 CSV 统计报告
- **技术**: YOLOv8 + ROS2 bag + KITTI
- **模板**: [`p03-yolo-detector/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p03-yolo-detector)

#### 🚀 中级项目（适合 2-3 人）

**4. MOT17 多目标追踪 + 指标评估** 🟢
- **难度**: ⭐⭐⭐ · **数据源**: MOT17 行人追踪基准数据集
- **任务**: 实现 SORT 跟踪 → 计算 MOTA / IDF1 / FP / FN / IDsw 五项指标
- **技术**: YOLO + SORT 卡尔曼跟踪 + motmetrics
- **模板**: [`p04-object-tracker/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p04-object-tracker)

**5. Gazebo 仿真 SLAM + Nav2 自主导航** 🟢
- **难度**: ⭐⭐⭐⭐ · **数据源**: TurtleBot3 仿真环境（apt 自带）
- **任务**: 自动建图 → 保存地图 → Nav2 穿越障碍 → 记录 5 次任务指标
- **技术**: Gazebo Classic + slam_toolbox + Nav2
- **模板**: [`p05-nav2-fusion/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p05-nav2-fusion)

**6. 基于视频的手势识别命令** 🟢
- **难度**: ⭐⭐⭐ · **数据源**: 课程提供 6 个手势演示视频
- **任务**: MediaPipe 提取 21 关键点 → 几何分类 5 种手势 → 输出 ROS bag
- **技术**: MediaPipe Hands + 几何规则 + ROS2
- **模板**: [`p06-gesture-control/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p06-gesture-control)

#### 🏆 高级项目（适合 3 人或有基础）

**7. Gazebo 仿真 + YOLO 智能巡检** 🟢
- **难度**: ⭐⭐⭐⭐ · **数据源**: aws_robomaker_hospital_world 仿真医院
- **任务**: 自动巡检 10 个 waypoint → 发现异常停下 → 生成 PDF 报告
- **技术**: Gazebo + Nav2 waypoint + YOLO + PDF 报告
- **模板**: [`p07-patrol-robot/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p07-patrol-robot)

**8. 基于人脸数据集的识别系统** 🟢
- **难度**: ⭐⭐⭐⭐ · **数据源**: LFW 子集 / 课程提供照片
- **任务**: 训练注册库 → 测试集评估 → 输出准确率/召回率/混淆矩阵
- **技术**: face_recognition (dlib) + SQLite + 评估指标
- **模板**: [`p08-face-access/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p08-face-access)

**9. PyBullet 机械臂仿真抓取** 🟢
- **难度**: ⭐⭐⭐⭐⭐ · **数据源**: 纯 PyBullet 仿真
- **任务**: 视觉识别仿真方块 → 逆运动学规划 → 抓取放入箱子
- **技术**: PyBullet + 内置 Kuka URDF + 视觉伺服
- **模板**: [`p09-arm-grasp/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p09-arm-grasp)

**10. PyBullet 四足机器人步态优化** 🟢
- **难度**: ⭐⭐⭐⭐⭐ · **数据源**: PyBullet 自带 Laikago / A1 URDF
- **任务**: 实现 Trot 步态 → 用 CMA-ES 优化步频/步长/抬腿高度
- **技术**: PyBullet + Trot 步态 + CMA-ES
- **模板**: [`p10-quadruped/`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/p10-quadruped)

#### 💪 项目设计亮点

- **复用本课程知识**：KITTI (Week 6)、YOLO (Week 10)、追踪 (Week 11)、Docker (Week 8)、运动学 (Week 5)、路径规划 (Week 9)
- **公开基准数据集**：MOT17、LFW、KITTI 等，便于客观量化评分
- **可量化指标**：mAP、MOTA、准确率、SLAM 误差等都能算出来
- **零硬件门槛**：所有项目用一台普通笔记本（MacBook Air 也行）就能跑
- **可扩展性**：有硬件的同学可以切换"实时模式"作为加分项

#### 🎯 自动评分系统（学生可自查、教师可批量评分）

> 📊 **每个项目都附带自动评分脚本**，可以一键查看自己的完成度！
>
> 📂 详细文档：[`project-templates/grading/README.md`](https://github.com/ai-robot-class/ai-robot-class.github.io/tree/main/project-templates/grading)

##### 学生自查（提交前必跑）

```bash
# 在项目目录下运行
cd p01-color-tracker
python3 ../grading/run_grading.py . --student YOUR_GITHUB_ID
```

会自动打印 5 个维度的得分：

```
📋 评分报告
  总分: 85.0/100  等级: A
  - 项目结构完整      10.0/10  ✅
  - TODO 函数实现     32.0/40  ⚠️
  - 集成测试通过      28.0/30  ✅
  - 代码质量          8.0/10   ✅
  - 文档与提交       7.0/10    ✅
```

##### 评分维度说明（总分 100）

| 维度 | 占比 | 自动检查内容 |
|------|------|--------------|
| 🗂️ 项目结构 | 10% | README/Dockerfile/docker-compose 是否齐全 |
| ✅ TODO 函数实现 | 40% | 3 个 TODO 是否真的实现（不是 pass）|
| 🔄 集成测试 | 30% | 跑通端到端流程，检查输出文件 |
| 🎨 代码质量 | 10% | ruff lint 检查 |
| 📄 文档与提交 | 10% | README 详细度 + Git 提交次数 + 演示输出 |

##### GitHub Actions 自动评分

学生可以在自己的项目仓库加上 `.github/workflows/grade.yml`，
每次 push 都自动跑评分并生成 Markdown 报告（详见 grading/README.md）。

---

### 12.5.3 📁 项目仓库与作业仓库分离（必读）

> 💡 期末项目代码**必须独立存放在新的 GitHub 仓库**，然后在你**作业仓库的 `final-project/` 文件夹**中通过 Git Submodule 引用。

#### 🎯 为什么这么设计？

| 痛点 | 解决方案 |
|------|---------|
| 多人协作时代码冲突 | 项目独立仓库，专门的协作场所 |
| 个人作业仓库太杂 | 作业仓库只放各周习题，期末项目独立 |
| 单人项目也要练习项目化思维 | 强制独立仓库 = 简历可直接用 |
| 评分需要看个人贡献 | submodule + 个人 README 双重展示 |

#### 📂 推荐目录结构

```
你的作业仓库（如 ai-robot-homework-zhangsan）
├── week2/
├── week3/
├── ...
├── week12/
├── week13/
└── final-project/                # 期末项目展示文件夹
    ├── README.md                 # ⭐ 个人贡献说明（你自己写）
    ├── project-repo/             # 🔗 Git Submodule（指向项目仓库）
    └── my_contributions.md       # 详细贡献清单（可选）

期末项目独立仓库（如 ai-robot-final-color-tracker-team1）
├── README.md                     # 项目整体说明
├── Dockerfile
├── docker-compose.yml
├── src/                          # 实际代码
├── demo/
└── test/
```

#### 🚀 Step-by-Step 创建流程

##### Step 1：创建项目仓库（无论单人还是多人）

```bash
# 在 GitHub 网页创建一个新仓库，例如：
# - 单人：     ai-robot-final-color-tracker-zhangsan
# - 多人：     ai-robot-final-color-tracker-team1
# - 推荐命名： ai-robot-final-<项目主题>-<组名或个人>

# 克隆到本地
git clone https://github.com/<your-org>/ai-robot-final-color-tracker-team1.git
cd ai-robot-final-color-tracker-team1

# 复制项目模板内容进来
cp -r /path/to/ai-robot-class.github.io/project-templates/p01-color-tracker/* .

# 提交初始代码
git add . && git commit -m "🎉 初始化项目模板"
git push
```

##### Step 2：在作业仓库中以 submodule 形式引用

```bash
# 切到你的作业仓库
cd ai-robot-homework-zhangsan

# 创建 final-project 文件夹
mkdir -p final-project
cd final-project

# 添加 submodule（关键操作！）
git submodule add https://github.com/<your-org>/ai-robot-final-color-tracker-team1.git project-repo

# 写自己的 README（说明个人贡献，模板见下文）
vim README.md
# 编辑后保存

# 提交
cd ..
git add final-project
git commit -m "🔗 引用期末项目仓库 + 个人贡献说明"
git push
```

##### Step 3：克隆带 submodule 的仓库（评分时教师使用）

```bash
# 教师评分时这样克隆，会同时拉取主仓库 + submodule
git clone --recursive https://github.com/student/ai-robot-homework-zhangsan.git

# 如果已经 clone 了，再拉取 submodule：
git submodule update --init --recursive
```

#### 📝 个人贡献 README 模板

> 把下面这个模板复制到 `final-project/README.md`，按提示填写。

```markdown
# 🎓 期末项目个人贡献说明

## 📌 项目信息

- **项目名称**：基于视频的颜色追踪机器人
- **项目编号**：P01
- **项目仓库**：[ai-robot-final-color-tracker-team1](https://github.com/xxx/ai-robot-final-color-tracker-team1)
- **作业仓库本人路径**：`final-project/project-repo/`（submodule）

## 👥 团队成员（如多人）

| GitHub ID | 角色 | 主要负责 |
|-----------|------|---------|
| @alice | 组长 | 整体架构 + detect_color |
| **@me（本人）** | 组员 | compute_twist + 集成测试 |
| @bob | 组员 | 数据集准备 + README |

> 单人完成填："独立完成所有任务"

## 🎯 我在项目中的具体贡献

### 📝 我负责实现的核心功能

1. **`compute_twist()` 函数**
   - 实现了 PID 式比例控制
   - 代码位置：[`src/color_tracker/color_tracker/tracker_node.py#L45-L72`](https://github.com/xxx/ai-robot-final-color-tracker-team1/blob/main/src/color_tracker/color_tracker/tracker_node.py#L45-L72)
   - 我的相关 commits：
     - [`a1b2c3d`](https://github.com/xxx/ai-robot-final-color-tracker-team1/commit/a1b2c3d) - 初版 PID 实现
     - [`d4e5f6g`](https://github.com/xxx/ai-robot-final-color-tracker-team1/commit/d4e5f6g) - 加入平滑滤波

2. **集成测试**
   - 设计了 5 个测试用例覆盖边界情况
   - 代码位置：`test/test_compute_twist.py`

3. **README 与演示视频**
   - 编写项目 README 的"使用说明"部分
   - 录制并剪辑演示视频

### 📊 我的提交统计

```bash
# 在项目仓库目录运行：
git log --author="<我的 GitHub 邮箱>" --oneline | wc -l
# 输出：例如 12（我提交了 12 次）
```

我的 commit 列表（自动生成）：
```
a1b2c3d feat: PID 式 compute_twist 初版
d4e5f6g fix: 加入平滑滤波避免抖动
b7c8d9e test: 增加 5 个 compute_twist 测试用例
... 
```

### 🧠 学习收获

- 学到了 ROS2 节点的发布订阅模式
- 理解了 PID 控制的基础原理
- 体会到多人协作时分支管理的重要性

### 🐛 遇到的问题与解决方案

1. **问题**：Twist 命令导致小乌龟剧烈抖动
   - **解决**：在 compute_twist 中加入滑动平均滤波（移动窗口 = 5）
   
2. **问题**：本地无法 import cv_bridge
   - **解决**：用 Docker 容器跑，避免环境问题

## 🎬 演示

- 📹 [演示视频（B 站链接）](https://www.bilibili.com/video/xxx)
- 📷 [运行截图](./screenshots/)

## 📊 自评分

```bash
# 我用课程评分系统自查的结果：
$ python3 ../grading/run_grading.py project-repo --student my_github_id
总分: 87.5/100  等级: A
```

详细评分报告：[`grade_report.md`](./grade_report.md)

## 🔗 相关链接

- 项目主仓库：https://github.com/xxx/ai-robot-final-color-tracker-team1
- 我的 PR 列表：https://github.com/xxx/ai-robot-final-color-tracker-team1/pulls?q=author:my_github_id
- 我的所有 commit：https://github.com/xxx/ai-robot-final-color-tracker-team1/commits?author=my_github_id
```

#### 🔍 评分如何识别个人贡献？

教师评分时会：

1. **克隆作业仓库**（`--recursive` 自动拉 submodule）
2. **看 `final-project/README.md`** 了解你的角色
3. **跑评分脚本**：
   ```bash
   python3 grading/run_grading.py final-project/project-repo --student YOUR_ID
   ```
4. **检查 Git 提交记录**，看你在项目仓库中的实际贡献：
   ```bash
   cd final-project/project-repo
   git log --author=YOUR_GITHUB_ID --oneline | wc -l
   ```
5. **核对 README 中的 commit 链接** 是否真的指向你的提交

#### ❓ 常见问题

**Q1：单人完成需要建独立仓库吗？**

A：**需要**。理由：
- 培养工程化思维（简历可直接用）
- 期末项目 = 独立作品集 = 找工作神器
- 命名建议：`ai-robot-final-<主题>-<github_id>`

**Q2：多人项目，每个人都要在自己作业仓库放 submodule？**

A：**是的**。每个组员的作业仓库都要：
1. 引用同一个项目仓库（submodule）
2. 写自己的 `final-project/README.md`（说明自己的具体贡献）

这样评分时每个人都能被独立评估。

**Q3：忘记加 `--recursive` 怎么办？**

A：在已经克隆的仓库里跑：
```bash
git submodule update --init --recursive
```

**Q4：submodule 怎么更新？**

A：项目仓库更新后：
```bash
cd final-project/project-repo
git pull origin main
cd ../..
git add final-project/project-repo
git commit -m "📌 更新项目仓库指针"
git push
```

**Q5：能不能直接复制项目仓库代码而不用 submodule？**

A：**不可以**。理由：
- 代码会脱离原项目，无法追踪更新
- 教师无法验证你的真实贡献（commit 历史丢失）
- submodule 是工业界标准做法，必须掌握

---

### 12.5.4 📦 项目 Docker 模板使用指南

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

### 12.5.5 项目分组与计划（30分钟）

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

### 12.5.6 技术答疑与资源（20分钟）

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

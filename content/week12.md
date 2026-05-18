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

#### 📦 初级项目（适合单人或2人）

**1. 视觉颜色追踪机器人**
- **难度**: ⭐⭐
- **技术**: OpenCV颜色检测 + ROS2
- **目标**: 机器人追踪特定颜色物体移动
- **参考**: 第12周颜色检测代码

**2. 语音控制小乌龟**
- **难度**: ⭐⭐
- **技术**: 语音识别 + ROS2 Turtlesim
- **目标**: 语音命令控制小乌龟运动
- **扩展**: 添加语音反馈

**3. 简单目标检测系统**
- **难度**: ⭐⭐⭐
- **技术**: YOLO + ROS2
- **目标**: 摄像头实时检测并标注物体
- **扩展**: 统计物体数量、发布ROS2话题

#### 🚀 中级项目（适合2-3人）

**4. 物体追踪与跟随**
- **难度**: ⭐⭐⭐
- **技术**: YOLO + Sort追踪 + ROS2
- **目标**: 机器人识别并跟随特定物体
- **扩展**: 保持安全距离

**5. 多传感器融合导航**
- **难度**: ⭐⭐⭐⭐
- **技术**: 相机 + 激光雷达 + ROS2 Nav2
- **目标**: 机器人自主避障导航
- **扩展**: 语音目标点设置

**6. 手势识别控制**
- **难度**: ⭐⭐⭐
- **技术**: MediaPipe手势识别 + ROS2
- **目标**: 手势控制机器人运动
- **扩展**: 自定义手势命令

#### 🏆 高级项目（适合3人或有基础）

**7. 智能巡检机器人**
- **难度**: ⭐⭐⭐⭐
- **技术**: SLAM + 目标检测 + 语音播报
- **目标**: 自主巡检并识别异常
- **扩展**: 生成巡检报告

**8. 人脸识别门禁系统**
- **难度**: ⭐⭐⭐⭐
- **技术**: 人脸检测/识别 + 数据库 + ROS2
- **目标**: 识别授权人员并控制门禁
- **扩展**: 陌生人告警

**9. 机械臂物体抓取**
- **难度**: ⭐⭐⭐⭐⭐
- **技术**: 目标检测 + 逆运动学 + MoveIt
- **目标**: 识别物体位置并抓取
- **扩展**: 物体分类存放

**10. 四足机器人基础控制（第13周专题）**
- **难度**: ⭐⭐⭐⭐⭐
- **技术**: PyBullet仿真 + 步态生成
- **目标**: 四足机器人行走控制
- **扩展**: 地形适应

---

### 12.5.3 项目分组与计划（30分钟）

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

### 12.5.4 技术答疑与资源（20分钟）

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

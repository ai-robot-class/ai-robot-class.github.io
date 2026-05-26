# 第12周：手机摄像头、ArUco 识别与距离测量

**课时**：3 小时（一次课）

---

## 📋 本周课程目标

本周我们不再停留在“看懂图像”层面，而是围绕一个机器人真实问题展开：

> 机器人如何知道一个目标离自己有多远、在什么方向？

为了让大家用最低成本完成这个闭环实验，本周使用：

- **手机摄像头** 作为视觉输入
- **WSL Ubuntu** 作为开发环境
- **Tailscale** 作为手机与 WSL 之间的网络桥梁
- **OpenCV + ArUco** 完成识别与测距

课堂必做部分完成后，可以先打通下面这条基础链路：

```text
手机摄像头 -> WSL 视频输入 -> ArUco 识别
```

进一步的选做拓展链路是：

```text
手机摄像头 -> WSL 视频输入 -> ArUco 识别 -> 相机标定 -> 距离计算
```

---

## 🧭 本周课程结构

| 部分 | 时间 | 主题 | 核心内容 |
|------|------|------|----------|
| Part 1 | 50 分钟 | 手机摄像头接入 WSL | Tailscale 组网、SSH 登录测试、手机视频流、OpenCV 接收 |
| Part 2 | 35 分钟 | ArUco 识别 | ArUco 原理、OpenCV 检测、标记 ID 与角点 |
| Part 3 | 45 分钟 | 相机标定（选做） | 棋盘格、内参矩阵、畸变系数、标定数据保存 |
| Part 4 | 40 分钟 | 利用标定数据测距（选做） | solvePnP、rvec/tvec、距离计算与实时显示 |
| 收尾 | 10 分钟 | 总结与作业 | 环境检查、报告要求、延伸方向 |

---

## 第一部分：将手机摄像头作为输入，连入 WSL 系统

### 12.1.1 为什么不用笔记本内置摄像头？

这节课故意使用手机，是因为它更接近机器人开发中的真实工程思路：

- 学生人手一台，硬件成本几乎为零
- 后续可以直接迁移到“远程摄像头 / 网络摄像头 / 机器人相机”
- 能顺带理解网络视频流、设备接入和系统桥接问题

我们真正要解决的问题不是“打开摄像头”，而是：

> 如何让 **手机** 的视频画面，稳定地进入 **WSL** 里的 Python / OpenCV？

---

### 12.1.2 为什么使用 Tailscale？

在校园网、实验室或者机房环境中，普通局域网方案经常失败，原因通常有两个：

1. **校园网 AP 隔离**
   - 手机和电脑虽然连的是同一个 Wi-Fi
   - 但出于安全考虑，设备之间禁止互相访问

2. **WSL2 NAT 隔离**
   - WSL2 相当于 Windows 内部的一个独立虚拟子网
   - 手机很难直接访问 WSL 的内部地址

Tailscale 的作用就是给 **手机** 和 **WSL** 都分配一个同一虚拟网段下的地址（通常是 `100.x.y.z`），从而绕过校园网限制与 WSL 转发麻烦。

---

### 12.1.3 推荐课堂模式：一人一网（Tailnet）

不要让全班登录同一个 Tailscale 账号。

推荐方式：

- 每位同学使用自己的 **GitHub** 或 **Google** 账号注册 Tailscale
- 每个学生有自己的 Tailnet
- 这个虚拟网络里只包含自己的电脑和自己的手机

这样做的优点：

- IP 不会混乱
- 排错更直接
- 每个学生的实验环境互不干扰

---

### 12.1.4 在 WSL 中命令行安装 Tailscale

在开始 WSL 端安装之前，手机端也要先做一个很简短的准备：

- **iPhone / iPad**：在 `App Store` 安装 `Tailscale`
- **Android**：在应用商店安装 `Tailscale`
- 手机端登录时，使用和电脑端 **同一个账号**
- 第一次打开时允许 `VPN` 或网络扩展权限

手机端这一步不需要复杂配置，先保证两件事即可：

1. 手机上已经安装并登录 `Tailscale`
2. 后面能和 WSL 出现在同一个 Tailnet 中

本课程统一使用 **WSL 命令行** 安装，不依赖图形界面。

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo service tailscaled start
sudo tailscale up
```

执行 `sudo tailscale up` 后，按照终端提示登录自己的账号。

这里登录的账号应当与手机端保持一致。

查看当前网络状态：

```bash
tailscale status
tailscale ip -4
```

---

### 12.1.4.1 加上 SSH 登录学习测试

既然手机和 WSL 已经通过 Tailscale 进入同一个虚拟网络，本周可以顺手做一个很有工程味的验证：

> 除了“拉视频流”，这个网络还能不能让我们对 WSL 进行远程登录？

这一步的目的不是让手机作为主要开发终端，而是让大家理解：

- Tailscale 不只是给摄像头用
- 它本质上是在打通设备与设备之间的网络连接
- 打通之后，视频流、SSH、HTTP 服务都可以复用这条链路

先在 WSL 里安装 SSH 服务：

```bash
sudo apt update
sudo apt install openssh-server -y
sudo service ssh start
```

确认 SSH 服务正在监听：

```bash
sudo service ssh status
ss -tlnp | grep :22
```

然后查看 WSL 在 Tailscale 中的地址：

```bash
tailscale ip -4
```

假设输出为：

```text
100.88.77.66
```

那么在另外一台已经登录同一 Tailnet 的设备上，可以测试：

```bash
ssh robot@100.88.77.66
```

如果只有一台电脑和一部手机，也可以把这一步当作“理解型实验”：

- 先在 WSL 中把 SSH 服务装起来
- 确认 22 端口正常
- 理解 Tailscale 地址可以直接用于远程登录

建议直接使用手机上的 SSH 登录软件，从手机远程登录自己的电脑 / WSL，这样更容易直观理解：

- 手机不仅能当摄像头
- 也能当网络终端
- 同一个 Tailscale 网络既能传视频，也能做远程登录

推荐按手机系统区分：

| 系统 | 推荐 SSH 客户端 | 说明 |
|------|----------------|------|
| iPhone / iPad | **Termius** | 界面友好，比较容易上手 |
| Android | **Termius** / **JuiceSSH** | 都比较常见，连接和保存主机信息方便 |

建议学生在手机端新建一个连接项：

- Host：WSL 的 Tailscale IP，例如 `100.88.77.66`
- Username：自己的 WSL 用户名，例如 `robot`
- Port：`22`

连接命令本质上就是：

```bash
ssh robot@100.88.77.66
```

课堂提示：

- **iPhone / iPad**：先打开 Tailscale，再打开 SSH 客户端，避免 VPN 没连上
- **Android**：注意有些系统会限制后台网络权限，若连接超时，先确认 Tailscale 和 SSH 客户端都没有被系统省电策略挂起
- 第一次连接时看到主机指纹确认提示，选择接受即可

如果学生手机上安装了 SSH 客户端并成功登录，这会是一个很好的加分体验：说明他们已经真正把“手机、网络、WSL、Linux 服务”串起来了。

这一步的意义在于：

- 让大家理解机器人系统经常不是“单机程序”
- 而是多个设备通过网络协同
- 今天的摄像头输入，和将来的远程调试、远程部署，本质上是同一类问题

---

### 12.1.5 WSL 里最容易踩的坑

#### 坑 1：`tailscaled` 没启动

如果出现：

```text
failed to connect to local tailscaled; is tailscaled running?
```

说明守护进程没启动，先执行：

```bash
sudo service tailscaled start
```

#### 坑 2：每次开 WSL 都忘了启动

WSL 默认不像完整 Linux 服务器那样自然地托管所有后台服务。很多同学关掉终端再打开时，Tailscale 服务其实已经没了。

所以课堂习惯应该是：

```bash
sudo service tailscaled start
tailscale status
```

先确认服务和设备可见，再开始视觉实验。

#### 坑 3：Tailscale 通了，但 SSH 没开

很多同学会误以为：

> 只要 `tailscale status` 里看得到设备，就一定能 `ssh` 登录。

但并不是这样。Tailscale 只是把网络打通，SSH 还依赖：

- `openssh-server` 已安装
- `ssh` 服务已启动
- 用户名填写正确，例如 `robot`

所以 SSH 登录测试的最小检查顺序应该是：

```bash
tailscale status
sudo service ssh start
ss -tlnp | grep :22
```

---

### 12.1.6 手机端视频方案：统一使用 HTML5 相机

本周课堂统一采用：

- **手机浏览器**
- **HTML5 摄像头**
- **Tailscale**
- **老师提供的 WSL 接收脚本**

这样安排的目的，是让学生先把整条链路跑通，再逐步理解代码内部发生了什么。

换句话说，本节课前半段的重点不是先讲 Flask、SocketIO 或 WebSocket 细节，而是先让大家完成一个非常明确的操作目标：

> 让手机浏览器打开摄像头，并把画面送到 WSL 里的 OpenCV 窗口。

这样做的好处是：

- iPhone 和 Android 用的是同一套方案
- 学生不需要安装额外的摄像头 App
- 课堂操作步骤更统一
- 更适合先运行，再逐步理解

---

### 12.1.7 学生视角的课堂操作顺序

这一节按下面顺序操作，不必一开始就展开服务端代码细节。

#### 第一步：先把网络打通

在 WSL 中执行：

```bash
sudo service tailscaled start
tailscale status
tailscale ip -4
```

目标：

- 确认 Tailscale 已启动
- 记下 WSL 的 Tailscale IP

例如：

```text
100.88.77.66
```

---

#### 第二步：完成 SSH 学习测试

在 WSL 中确保 SSH 服务已经装好并启动：

```bash
sudo apt update
sudo apt install openssh-server -y
sudo service ssh start
ss -tlnp | grep :22
```

然后鼓励学生用手机上的 SSH 客户端测试连接：

```bash
ssh robot@100.88.77.66
```

这一小步的目的，是让学生先建立一个非常清楚的感受：

- Tailscale 确实把手机和 WSL 放进了同一个网络
- 手机不仅能当摄像头，也能做远程终端

---

#### 第三步：先安装本周需要的 Python 库

在运行相机桥接程序之前，先安装本周需要的依赖。

如果系统里还没有 `pip3`，先安装：

```bash
sudo apt update
sudo apt install python3-pip -y
```

然后安装本周起始代码依赖：

```bash
pip3 install -r week12_starters/requirements.txt
```

这一步完成后，再运行桥接程序。

如果直接运行程序时看到下面这类报错：

```text
No module named 'flask'
```

通常就说明依赖还没有安装完成。

---

#### 第四步：运行老师提供的相机接收脚本

接下来不要求学生先看懂服务端代码，而是先把脚本运行起来。

例如：

```bash
python3 week12_starters/camera_bridge.py
```

此时学生只需要知道两件事：

1. 这个脚本会在 WSL 中启动一个网页服务
2. 这个脚本会接收手机浏览器传回来的图像帧

至于 Flask、SocketIO、HTTPS、自签名证书这些实现细节，可以等链路跑通后再解释。

这一程序在实时实验阶段需要持续运行：

- 只要手机浏览器还在发送视频帧，WSL 端这个程序就不要关闭
- 关闭它之后，手机页面虽然还在，但后端已经没有程序接收图像
- 只有在结束本次实时实验，或者已经把需要的图片保存完毕后，才可以停止

本周课堂统一采用最简单的协调方式：

- **相机接收、图像显示、ArUco 检测写在同一个 Python 程序里**
- 不再额外启动第二个 Python 程序去“再读一次摄像头”
- 这样可以避免多个程序同时争抢同一条实时视频流

运行顺序统一为：

1. 先启动 `week12_starters/camera_bridge.py`
2. 再让手机浏览器接入
3. 程序持续接收最新一帧
4. 在同一个程序内部直接完成显示和识别

--- 

#### 第五步：用手机浏览器访问页面

在手机浏览器中打开：

```text
https://100.88.77.66:5000
```

注意：

- 这里的地址是 **WSL 的 Tailscale IP**
- 不是校园网地址
- 也不是 `192.168.x.x`

如果端口不是 `5000`，就替换成实际端口。

---

#### 第六步：允许浏览器使用摄像头

打开页面后，浏览器会请求摄像头权限。

学生此时要做的是：

- 允许浏览器访问摄像头
- 将后置摄像头对准 ArUco 或棋盘格
- 保持页面停留在前台

如果一切正常，此时 WSL 端应该已经能收到图像。

---

#### 本节课的最小成功流程

学生先装依赖：

```bash
pip3 install -r week12_starters/requirements.txt
```

再启动程序：

```bash
python3 week12_starters/camera_bridge.py
```

手机浏览器打开：

```text
https://<WSL的Tailscale_IP>:5000
```

成功标志是同时看到下面三件事：

1. **手机本地画面**
2. **服务端处理结果**
3. **ArUco ID 6 被识别**

---

### 12.1.8 推荐调试顺序

在这一步里，最常见的问题不是算法，而是链路没有打通。建议统一按下面顺序排查：

```text
先查网络 -> 再查服务 -> 再查浏览器权限 -> 最后查代码
```

#### 1. 先查网络

```bash
tailscale status
tailscale ip -4
ping <手机的Tailscale_IP>
```

目标：

- 看得到手机
- WSL 和手机在同一个 Tailnet 中

#### 2. 再查服务

确认老师提供的脚本是否真的启动了网页服务：

```bash
ss -tlnp | grep 5000
```

#### 3. 再查手机浏览器

看这三件事：

- 页面能不能打开
- 摄像头权限有没有给
- 页面是否保持在前台

#### 4. 最后再查代码

只有在网络、端口、权限都正常后，才去怀疑：

- 帧是否真的发出去了
- Python 是否成功解码
- OpenCV 是否成功显示

最常见的基础报错之一是：

```text
No module named 'flask'
```

这通常不是程序逻辑问题，而是还没有先执行：

```bash
pip3 install -r week12_starters/requirements.txt
```

#### 最推荐的课堂拆分验证法

把这一步拆成四个最小成功点：

1. 手机能访问 WSL 页面
2. 手机浏览器能成功打开摄像头
3. WSL 能收到一帧图像
4. OpenCV 能成功显示这一帧图像

---

### 12.1.9 OpenCV 测试手机视频流

这一小节要确认的是：

> 手机画面能够稳定出现在 WSL 的 OpenCV 窗口里。

这一部分可以分成两层理解：

#### 学生层面

学生先安装依赖：

```bash
pip3 install -r week12_starters/requirements.txt
```

然后运行：

```bash
python3 week12_starters/camera_bridge.py
```

然后在手机浏览器中打开：

```text
https://<WSL的Tailscale_IP>:5000
```

看到画面成功进入 WSL，就说明这一段链路已经打通。

#### 进一步理解

等链路跑通之后，再向学生解释老师提供的接收端脚本在做什么。下面给一个极简的参考实现。思路是：

- WSL 中起一个 HTTPS 页面
- 手机浏览器打开页面
- 页面调用摄像头
- 页面把 JPEG 帧通过 WebSocket 发回 Python
- Python 用 OpenCV 解码并显示

```python
import cv2
import numpy as np
from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

HTML = """
<!doctype html>
<html>
<body>
  <h3>HTML5 Camera Bridge</h3>
  <video id="video" autoplay playsinline style="width: 90vw;"></video>
  <canvas id="canvas" style="display:none;"></canvas>
  <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
  <script>
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const socket = io();

    async function main() {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 1280,
          height: 720,
          facingMode: "environment"
        },
        audio: false
      });
      video.srcObject = stream;

      setInterval(() => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);
        canvas.toBlob(async (blob) => {
          const arrayBuffer = await blob.arrayBuffer();
          socket.emit("video_frame", arrayBuffer);
        }, "image/jpeg", 0.8);
      }, 100);
    }

    main();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@socketio.on("video_frame")
def handle_frame(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is not None:
        cv2.imshow("HTML5 Camera Test", frame)
        cv2.waitKey(1)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, ssl_context="adhoc")
```

运行后，手机浏览器访问：

```text
https://<WSL的Tailscale_IP>:5000
```

首次访问时如果浏览器提示证书风险，可以指导学生点击“继续访问”，因为这里使用的是临时自签名证书。

---

### 12.1.10 手机摄像头实验前的铁律

做标定和测距之前，必须要求学生在手机浏览器侧尽量固定：

- **分辨率**
- **对焦模式**

推荐设置：

- 分辨率：`1280x720` 或 `1920x1080`
- 对焦：尽量锁定，不要自动来回跳

原因：

1. **自动对焦会改变焦距**
   - 相机标定默认认为焦距是固定的
   - 如果手机自动变焦，前面算出的内参矩阵会失效

2. **动态分辨率会破坏像素坐标系**
   - 如果浏览器传回来的分辨率中途变化
   - 角点位置和标定结果都不再对应

这一步是后面“测距是否准确”的前提。

---

## 第二部分：ArUco 识别

### 12.2.1 什么是 ArUco 码？

ArUco 可以理解为：

> 专门给机器人看的二维码 / 条形码。

它由两部分组成：

- **外圈粗黑边框**
- **内部黑白二值编码**

内部编码对应一个 **marker id**。本周课堂统一使用 `ID 6`。

不同 ID 对应不同的图案。

先建立一个非常直接的认识：

- 机器人首先不是“理解图片内容”
- 而是先找到一个**规则、可计算、容易稳定识别**的目标

ArUco 正好就是这样的目标。

---

### 12.2.2 为什么不用普通二维码？

普通二维码适合存很多信息，例如网址、文本、支付信息。

但机器人视觉里更重要的是：

- 检测快
- 定位准
- 抗干扰强
- 姿态估计方便

ArUco 的优势就在这里：

- 边框规整，容易定位
- 编码简单，识别速度快
- 特别适合做位姿估计和导航地标

这也是为什么 ArUco 在机器人、无人机降落、机械臂抓取引导里非常常见。

---

### 12.2.3 结合基础教程理解 ArUco 的读取与检测

这一部分可以直接按一个很自然的四步流程讲：

1. **生成 marker**
2. **打印并拍摄 marker**
3. **检测 marker**
4. **读取检测结果**

本周统一使用在线生成网站 [ArUco markers generator!](https://chev.me/arucogen/)。

生成参数统一为：

- `Dictionary`: `4x4 (50, 100, 250, 1000)`
- `Marker ID`: `6`
- `Marker size, mm`: `100`

这里要特别注意一件事：

> 识别程序里使用的字典，必须和生成 marker 时使用的具体字典完全一致。

也就是说，`ID 6` 本身还不够，程序还必须知道这个 `ID 6` 是属于哪一个字典的。

例如：

- 如果生成时用的是 `DICT_4X4_50`，程序里也必须写 `DICT_4X4_50`
- 如果生成时用的是 `DICT_4X4_250`，程序里就要改成 `DICT_4X4_250`

不能只看到“4x4”就直接互相混用。

这和基础教程里的思路是一致的：

- 先选择一个字典
- 再生成并打印 marker 图
- 然后对真实照片做检测
- 最后在图像中把 marker 框出来，并读取它的 id 和四个角点

为了让课堂代码统一，本讲义下面的示例固定写成 `DICT_4X4_50`。如果实际生成的 marker 来自别的具体字典，就要把代码中的这一行改成对应字典：

```python
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
```

这里的含义是：

- `4X4`：内部编码矩阵是 4×4
- `50`：这个字典里一共有 50 个可用 marker
- `ID 6`：本周课堂要求识别出的就是 6 号 marker
- 只有当 marker 本身也是按这个字典生成时，程序才能正确解码

---

### 12.2.4 OpenCV 中的识别思路

ArUco 的检测过程可以拆成四步：

1. **图像灰度化 / 二值化**
   - 先把彩色图像变成更适合识别的黑白图

2. **轮廓检测**
   - 寻找可能的方形边框

3. **透视变换**
   - 把倾斜的方块“拉正”

4. **查字典解码**
   - 比对 ArUco 字典，例如 `DICT_4X4_50`
   - 这里的字典必须与生成 marker 时的具体字典一致
   - 判断这个方块对应哪个 ID

---

### 12.2.5 安装依赖

ArUco 相关模块通常在 `opencv-contrib-python` 中。

```bash
pip install opencv-python opencv-contrib-python numpy
```

验证：

```bash
python3 -c "import cv2; print(cv2.__version__)"
```

---

### 12.2.6 实时检测 ArUco

```python
import cv2

# 这一行必须与生成 marker 时使用的具体字典一致
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

# 这里假设 frame 来自前面 HTML5 相机桥接程序收到的最新一帧
while True:
    frame = get_latest_frame()
    if frame is None:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        for i, marker_id in enumerate(ids.flatten()):
            c = corners[i][0]
            cx = int(c[:, 0].mean())
            cy = int(c[:, 1].mean())
            cv2.putText(
                frame,
                f"ID: {marker_id}",
                (cx, cy),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

    cv2.imshow("ArUco Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
```

说明：

- `get_latest_frame()` 表示“从 HTML5 摄像头接收端拿到最新一帧图像”
- 本周课堂直接把 HTML5 接收、ArUco 检测和结果显示写在同一个 Python 程序里
- `week12_starters/camera_bridge.py` 在实时识别期间保持运行，识别逻辑就在这个运行中的程序内部完成
- 这样整条输入链路始终只有一套，不会出现两个程序重复接收视频流的冲突

---

### 12.2.7 检测结果到底读到了什么？

这一段除了跑通代码，还要理解三个输出：

- `ids`
  - 表示识别出了哪个 ArUco 标记

- `corners`
  - 表示这个标记在图像中的四个角点位置

- `rejected`
  - 表示“看起来像 marker，但最后没有通过字典验证”的候选框

后面的标定和测距，全都要依赖这些角点。

也就是说：

> ArUco 的本质不只是“认出来了”，而是“把一个可计算的几何目标找出来了”。

还有一个非常实用的小观察：

- `corners[i][0]` 里有 4 个顶点
- 取这 4 个顶点的平均值，就可以近似得到这个 marker 在图像中的中心位置

这也是很多基础教程中会直接把 marker 中心点画出来的原因。

---

## 第三部分：相机标定（Calibration，选做）

### 12.3.1 为什么要标定？

这是本节数学味最重，但也是最关键的一部分。

不标定，后面的测距通常不准，原因主要有两个：

#### 1. 畸变（Distortion）

手机摄像头为了获得更大视角，边缘通常会出现桶形畸变。

直线在图像边缘可能会看起来向外鼓。

如果不做畸变校正，几何计算会被系统性拉偏。

#### 2. 内参矩阵（Intrinsic Matrix）

我们必须知道：

- 相机焦距在像素坐标里是多少
- 光学中心在哪里

这由内参矩阵 `K` 表示：

```text
K = [ fx   0  cx
       0  fy  cy
       0   0   1 ]
```

其中：

- `fx`, `fy`：焦距（像素单位）
- `cx`, `cy`：主点坐标

---

### 12.3.2 为什么手机相机尤其需要标定？

这一点对本科生非常重要，要讲得直白一些：

手机相机并不是一个“理想针孔相机”，它常常同时带着下面几种复杂因素：

- 广角镜头，边缘畸变更明显
- 自动对焦，焦距可能变化
- 不同手机型号，镜头参数差异很大
- 有些系统还会做额外的图像处理或电子防抖

所以同样一个 ArUco：

- 在一台手机上看起来可能更扁
- 在另一台手机上可能边缘拉伸更明显
- 如果不先标定，后面算出来的距离和姿态就很容易系统性偏掉

这一句可以直接记住：

> 相机标定不是“锦上添花”，而是把像素坐标变成可信几何测量的前提。

---

### 12.3.3 标定的直观理解

可以这样理解：

> 标定，就是给这台摄像头做一次“体检”，得到它的个体参数。

输出结果主要有两类：

1. **内参矩阵 K**
2. **畸变系数 D**

这相当于拿到了这台手机摄像头的“身份证”。

---

### 12.3.4 课堂里的标定方案：简单讲清楚就够

本节课不需要把标定讲成一堂完整数学课，重点是让学生知道：

1. 我们使用一个**已知几何结构**的棋盘格
2. 从多个角度采集图像
3. 在图像中找到棋盘格内角点
4. 用这些“真实世界点 - 图像点”的对应关系反推出相机参数

对应到 OpenCV，大致是：

- `findChessboardCorners()`：找到角点
- `cornerSubPix()`：把角点定位得更精细
- `calibrateCamera()`：计算相机内参和畸变系数

这一套流程已经足够让学生建立起“标定在做什么”的理解。

---

### 12.3.5 棋盘格标定法

本课程使用最经典的 **张正友标定法**。

需要准备：

- 一张打印好的棋盘格
- 或在平板 / iPad 上稳定显示棋盘格

采集要求：

- 从不同角度拍 10-20 张图
- 棋盘格要覆盖画面不同区域
- 远近都要有
- 保持**固定焦距**和**固定分辨率**

---

### 12.3.6 采集棋盘格图片

可以单独写一个小脚本，把 HTML5 摄像头桥接收到的当前帧保存下来。

```python
import cv2
import os

save_dir = "calib_images"
os.makedirs(save_dir, exist_ok=True)

idx = 0

while True:
    frame = get_latest_frame()
    if frame is None:
        break

    cv2.imshow("Calibration Capture", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        path = os.path.join(save_dir, f"img_{idx:02d}.jpg")
        cv2.imwrite(path, frame)
        print(f"saved: {path}")
        idx += 1
    elif key == ord("q"):
        break

cv2.destroyAllWindows()
```

操作建议：

- `s` 保存图片
- `q` 退出
- 每个学生至少采集 10 张

---

### 12.3.7 执行标定

下面给出一个适合课堂的批量标定脚本。

```python
import cv2
import numpy as np
import glob

# 棋盘格内角点数量，例如 9x6
pattern_size = (9, 6)

# 世界坐标中的棋盘格点
objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)

objpoints = []
imgpoints = []

images = glob.glob("calib_images/*.jpg")

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        cv2.drawChessboardCorners(img, pattern_size, corners, ret)
        cv2.imshow("Corners", img)
        cv2.waitKey(200)

cv2.destroyAllWindows()

ret, K, D, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

print("RMS error:", ret)
print("Intrinsic matrix K:\n", K)
print("Distortion coefficients D:\n", D)

np.savez("camera_calib.npz", K=K, D=D)
print("saved to camera_calib.npz")
```

这里要重点看三件事：

1. `findChessboardCorners()` 找到的是**图像里的角点**
2. `cornerSubPix()` 会继续提高角点精度
3. `calibrateCamera()` 会输出 `K` 和 `D`

---

### 12.3.8 标定后要告诉学生什么？

一定要强调：

- 标定结果**只对当前这台手机、当前分辨率、当前焦距设置有效**
- 如果切换了浏览器请求分辨率
- 或重新自动对焦、变焦
- 或换了一台手机

那么之前的 `K` 和 `D` 可能就不适用了。

这也是机器人系统中“传感器一致性”非常重要的原因。

---

## 第四部分：利用标定数据计算 ArUco 距离（选做）

### 12.4.1 已知什么？要算什么？

走到这一步，我们已经有了三类关键信息：

#### 已知条件 1：ArUco 的真实大小

例如我们打印出来的是：

```text
100 mm × 100 mm
```

即边长 `0.10 m`。

#### 已知条件 2：相机标定结果

也就是：

- `K`
- `D`

#### 观测条件：图像中的四个角点

这来自 ArUco 检测输出的 `corners`。

到这里，信息关系可以概括成一句话：

> ArUco 给我们提供了图像中的 4 个点，标定给我们提供了相机参数，而 marker 的真实尺寸提供了世界坐标尺度。

---

### 12.4.2 核心问题：PnP

这一部分的核心是 **Perspective-n-Point** 问题。

可以直观地说：

> 我知道这个正方形在真实世界里长什么样，也知道它在图像里看起来变成了什么样，那么我就能反推出它相对于摄像头的位置和姿态。

OpenCV 会输出两个非常重要的量：

- `rvec`：旋转向量
- `tvec`：平移向量

其中 `tvec = [x, y, z]^T` 就是 ArUco 相对于摄像头的三维位置。

---

### 12.4.3 为什么标定之后就能算空间位置？

这是本节课最关键的“融会贯通”处。

在没有标定之前，我们只有：

- 图像像素位置

这只能说明“它在画面哪里”，不能可靠说明“它在空间哪里”。

而在标定之后，我们又知道了：

- 相机的内参矩阵 `K`
- 畸变系数 `D`
- ArUco 的真实物理尺寸

于是 OpenCV 可以把：

- **真实世界里的 4 个角点**
- **图像中的 4 个角点**

对应起来，求出 marker 相对于摄像头的三维位姿。

所以标定之后，ArUco 不再只是一个“被识别出的图案”，而是一个真正带有空间意义的几何目标。

---

### 12.4.4 真实世界中的 ArUco 角点

假设 ArUco 边长为 `marker_size`，则它在自身坐标系中的四个角点可以写为：

```python
obj_points = np.array([
    [-marker_size/2,  marker_size/2, 0],
    [ marker_size/2,  marker_size/2, 0],
    [ marker_size/2, -marker_size/2, 0],
    [-marker_size/2, -marker_size/2, 0],
], dtype=np.float32)
```

这些点是“真实世界坐标”。

而 ArUco 检测得到的 `corners` 是“图像像素坐标”。

PnP 就是在把这两者对上。

---

### 12.4.5 实时测距代码

```python
import cv2
import numpy as np

data = np.load("camera_calib.npz")
K = data["K"]
D = data["D"]

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

marker_size = 0.10  # 100 mm
obj_points = np.array([
    [-marker_size/2,  marker_size/2, 0],
    [ marker_size/2,  marker_size/2, 0],
    [ marker_size/2, -marker_size/2, 0],
    [-marker_size/2, -marker_size/2, 0],
], dtype=np.float32)

# 这里假设 frame 来自前面 HTML5 相机桥接程序收到的最新一帧
while True:
    frame = get_latest_frame()
    if frame is None:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        for i, marker_id in enumerate(ids.flatten()):
            img_points = corners[i][0].astype(np.float32)

            success, rvec, tvec = cv2.solvePnP(
                obj_points, img_points, K, D
            )

            if success:
                x, y, z = tvec.flatten()
                distance = np.sqrt(x**2 + y**2 + z**2)

                cv2.drawFrameAxes(frame, K, D, rvec, tvec, 0.05)

                text = f"ID:{marker_id} Dist:{distance:.3f} m Z:{z:.3f} m"
                px = int(img_points[0][0])
                py = int(img_points[0][1]) - 10
                cv2.putText(
                    frame,
                    text,
                    (px, py),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

    cv2.imshow("ArUco Distance", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cv2.destroyAllWindows()
```

在实际代码里，可以把：

- HTML5 相机接收
- ArUco 检测
- 距离计算

写在同一个 Python 程序中，这样 `get_latest_frame()` 只是一个逻辑上的占位符，代表“取到手机浏览器刚刚发送来的最新图像”。

---

### 12.4.6 如何理解 `tvec`

`tvec = [x, y, z]^T` 表示：

- `x`：目标相对摄像头左右方向偏移
- `y`：目标相对摄像头上下方向偏移
- `z`：目标沿着摄像头朝前方向的深度

如果只关心“正前方有多远”，很多时候直接看 `z` 就够了。

如果要看真正的欧氏距离，则使用：

```text
distance = sqrt(x² + y² + z²)
```

这里可以直接记住：

- 如果你主要关心“离镜头前后有多远”，最常看的是 `z`
- 如果你关心“总体距离”，就看欧氏距离 `sqrt(x² + y² + z²)`

---

### 12.4.7 选做部分的观察重点

这一部分的观察重点是：

- 把 ArUco 靠近摄像头，距离数字变小
- 把 ArUco 远离摄像头，距离数字变大
- 改变角度时，姿态轴也会变化

这时候学生会第一次真正意识到：

> 机器人视觉不是“看图”，而是在从图像中恢复三维空间关系。

---

## 12.5 HTML5 摄像头方案的工程意义

本周课堂主线已经统一采用 HTML5 摄像头方案。

从工程角度看，它的优势非常明显：

- 手机浏览器调用 `getUserMedia()`
- 通过 `WebSocket` 把帧推给 WSL
- WSL 中 Python 服务器接收 JPEG 帧
- OpenCV 继续做 ArUco / 标定 / 测距

它的实际优点是：

- 学生不必额外安装 App
- iPhone / Android 统一性更强
- 很适合做“浏览器 + 机器人”的全栈实验

它仍然会带来一些工程约束：

- HTTPS / 安全上下文
- WebSocket 服务
- 浏览器权限和兼容性

但这些约束本身也是课程价值的一部分，因为它们正好能帮助学生理解：

- 为什么现代设备权限越来越严格
- 为什么机器人系统经常要跨前端、网络和后端
- 为什么“能跑起来”和“能稳定使用”是两件不同的事

---

## 12.6 课堂避坑清单

### 网络侧

- 确认手机和 WSL 登录的是同一个 Tailscale 账号
- 用的是 `100.x.y.z`，不是校园网 IP
- 如果画面完全打不开，先检查手机浏览器页面是否还保持打开状态

### 系统侧

- 先执行 `sudo service tailscaled start`
- 再执行 `tailscale status`
- 浏览器访问前先确认 WSL 服务端口已经在监听

### 摄像头侧

- 固定分辨率
- 固定对焦
- 采集标定图时不要中途切换浏览器标签页或刷新设置

### 数学侧

- 标定结果只对当前摄像头配置有效
- `marker_size` 单位要统一，建议用米
- 测距误差往往来自：标定差、角点抖动、打印尺寸不准

---

## 12.7 本周总结

本周的课堂必做部分完成的是：

1. **手机摄像头接入 WSL**
2. **ArUco 识别**

在此基础上，讲义还给出了两个选做方向：

3. **相机标定**
4. **利用标定数据进行距离计算**

这套流程并不是“课堂小玩具”，而是很多真实机器人任务的基础模块，例如：

- 机械臂抓取前的目标定位
- 无人机降落引导
- 移动机器人近距离视觉导航
- 相机辅助测量与校准

换句话说：

> 今天做的不是一个孤立实验，而是机器人视觉系统的基本骨架。

---

## 12.8 课后作业

### 必做

1. 在 WSL 中完成 Tailscale 安装与连接
2. 使用手机浏览器成功打开 HTML5 相机页面，并将视频送入 WSL
3. 完成至少一个 ArUco 的实时识别

### 选做

4. 完成相机标定，并保存 `camera_calib.npz`
5. 在视频画面中实时显示 ArUco 距离或空间位置

### 提交内容

- GitHub 仓库代码
- 一份 `README.md`
- 至少 3 张截图：
  - 手机视频流进入 WSL
  - ArUco 检测结果
  - 如果完成了选做，可附上距离实时显示结果

### README 建议包含

- 你的手机型号和系统
- 使用的手机浏览器
- Tailscale 连接方式
- 必做部分的运行过程与结果
- 如果完成了选做，再补充：
  - 标定使用的棋盘格参数
  - ArUco 实际尺寸
  - 测得的距离结果与误差分析

---

## 12.9 延伸思考

如果把本周内容继续往前推进，可以自然走向：

- 多个 ArUco 的同时定位
- 相机位姿估计
- ArUco 引导机器人停靠
- 与 ROS2 节点打通，发布目标相对位姿
- 将 HTML5 摄像头页面做成专用机器人控制面板

这也是从“视觉实验”走向“机器人系统集成”的关键一步。

---

## 12.10 第 14 周小组项目预告

第 14 周的小组项目统一围绕下面这条链路展开：

```text
手机控制输入 -> Tailscale 局域网 -> WSL / ROS / 仿真程序 -> 机器人运动
```

每组从下面两个方向中选择一个完成。

### 方向 A：通信交互控制机器狗

- 场景：`PyBullet` 中的三维迷宫
- 对象：四足机器人
- 目标：用手机遥控器网页控制机器人完成迷宫探索

### 方向 B：通信交互控制 turtlesim 乌龟

- 场景：`turtlesim` 的二维平面
- 对象：ROS 乌龟
- 目标：用手机遥控器网页控制乌龟完成迷宫探索

### 统一要求

1. 手机作为控制手柄输入
2. 自己实现一个简单的遥控器网页
3. 手机和电脑通过 `Tailscale` 进入同一个虚拟局域网
4. 能够控制四足机器人 / `turtlesim` 乌龟完成：
   - 前进
   - 后退
   - 左转
   - 右转
5. 最终需要在迷宫环境中完成基本探索任务

### 起始代码位置

本仓库已经准备了两套起始代码：

- `week14_starters/pybullet_dog/`
- `week14_starters/turtlesim_remote/`

这两套起始代码都遵循同一个组织原则：

- 桥接程序在实验期间需要持续运行
- 手机网页只负责发送控制指令
- 网络接收与机器人控制逻辑放在同一个 Python 程序中
- 不再额外启动第二个程序去重复接管同一条控制链路

完成起始代码跑通后，再继续补充：

- 迷宫地图
- 自动探索策略
- 碰撞处理
- 路径记录或结果展示

---

*第 12 周结束！这一周我们第一次让机器人视觉真正落到“可计算的空间关系”上。*

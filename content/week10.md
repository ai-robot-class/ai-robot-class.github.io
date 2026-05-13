# Week 10：Docker 概念与 OpenCV 实验

本周学习 Docker 的核心概念和基础操作，并进行 OpenCV 图像处理实验。

## 课堂内容

1. Docker 是什么？
2. Docker 基础概念。
3. Docker 基础指令。
4. 容器与本地文件交互。
5. OpenCV 介绍与安装实验。

## Docker 是什么？

"Docker" 一词指代了多个概念：

- 开源社区项目
- 开源项目使用的工具
- 主导支持此类项目的公司 Docker Inc.
- 该公司官方支持的工具

**简单理解**：Docker 是支持创建和使用 Linux 容器的容器化技术。

- 开源 Docker 社区致力于改进这类技术，并免费提供给所有用户。
- Docker Inc. 公司凭借 Docker 社区产品起步，主要负责提升社区版本的安全性，并将技术进步与广大技术社区分享。
- 它还专门对这些技术产品进行完善和安全固化，以服务于企业客户。

参考资料：

```text
https://www.redhat.com/zh-cn/topics/containers/what-is-docker
```

## Docker 基础概念

### Image 镜像

只读的模板，包含了运行应用程序所需的所有文件、依赖项、配置、库和运行环境。可以将其理解为轻量级的、可执行的"安装包"，用于在 Docker 容器中运行代码，确保应用程序在不同环境中保持一致性。

**核心特性**：

- **只读模板**：镜像在运行后不会被改变。
- **分层结构**：基于联合文件系统（UnionFS），通过分层叠加生成最终的文件系统。
- **可移植性**："一次构建，随处运行"，可在任意安装了 Docker 的服务器上启动。

**形象类比**：

- 镜像 (Image) 就像是面向对象编程中的 **类（Class）** 或软件安装光盘（ISO 文件）。
- 容器 (Container) 则是类的 **实例（Instance）** 或运行中的安装程序。

### Container 容器

软件运行环境，一个基于沙盒隔离的可执行进程，运行在宿主机上，但不依赖独立操作系统。

**与镜像关系**：

- 容器是镜像的运行实例。
- 镜像是只读的，容器是在镜像基础上增加了一个可读可写层。

## Docker 基础指令

```bash
# 拉取镜像
docker pull <镜像名>

# 运行容器
docker run <镜像名>

# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 停止容器
docker stop <容器ID>

# 删除容器/其他资源
docker rm <容器ID>

# 删除镜像
docker rmi <镜像ID>

# 构建镜像
docker build .

# 保存容器为新镜像
docker commit <容器ID> <新镜像名>
```

## 容器与本地文件交互

### 使用 -v 进行本地目录挂载

`docker run` 命令首先在指定的镜像上创建一个可写的容器层，然后使用指定的命令启动。

使用参数 `-v` 允许你绑定一个本地目录：

```bash
docker run -p 6080:80 --security-opt seccomp=unconfined --shm-size=512m \
  -v "$(pwd)/:/home/ws" \
  ghcr.io/tiryoh/ros2-desktop-vnc:humble
```

**说明**：

- `-v "$(pwd)/:/home/ws"`：将当前目录挂载到容器内的 `/home/ws` 目录
- 容器内对 `/home/ws` 的修改会反映到本地当前目录

### VNC 是什么？

VNC 是开源远程桌面控制技术。它允许用户通过网络远程操作另一台计算机的桌面环境，实现像在本地操作一样的图形化界面交互。

某种意义上：免费的向日葵远程控制。

**端口映射**：

- `-p 6080:80`：将容器的 80 端口映射到本地的 6080 端口
- 本地的 6080 端口在浏览器打开：`http://127.0.0.1:6080/`

### 在 Docker 环境中使用本地目录运行程序

```bash
# 进入要使用的目录
cd C:\具体要使用的目录

# 运行 Docker 容器，挂载当前目录
docker run -p 6080:80 --security-opt seccomp=unconfined --shm-size=512m \
  -v "$(pwd)/:/home/ws" \
  ghcr.io/tiryoh/ros2-desktop-vnc:humble
```

### 参考资料

```text
https://zhuanlan.zhihu.com/p/1896525993486812302
好玩的 docker 项目合集

https://www.freecodecamp.org/chinese/news/docker-mount-volume-guide-how-to-mount-a-local-directory/
Docker 挂载卷——如何挂载一个本地目录
```

## OpenCV

### OpenCV 是什么？

OpenCV (Open Source Computer Vision Library) 是一个开源的跨平台计算机视觉和机器学习软件库，致力于提供通用的计算机视觉基础架构，加速机器感知在商业产品中的应用。

它由英特尔公司发起并参与开发，以 BSD 许可证授权发行，因此可以在学术和商业领域中免费使用。

**支持语言**：

- C++ 调用
- Python 调用

### 安装 OpenCV

```bash
# 基础安装
pip install opencv-python opencv-contrib-python

# Ubuntu 24 安装
pip3 install opencv-python opencv-contrib-python --break-system-packages

# 如果出现 numpy 版本问题
pip install "numpy<2"
```

### OpenCV 基本使用

```python
import cv2
import matplotlib.pyplot as plt

# 读取图像（彩色）
img_basic = cv2.imread('cat.jpg', cv2.IMREAD_COLOR)

# 显示图像（注意 OpenCV 使用 BGR，需要转换为 RGB）
plt.imshow(cv2.cvtColor(img_basic, cv2.COLOR_BGR2RGB))
plt.show()

# 转换为灰度图像
img_basic = cv2.cvtColor(img_basic, cv2.COLOR_BGR2GRAY)

# 显示灰度图像
plt.imshow(cv2.cvtColor(img_basic, cv2.COLOR_GRAY2RGB))
plt.show()
```

### 参考教程

```text
https://github.com/ndb796/Python-Data-Analysis-and-Image-Processing-Tutorial/blob/master/06.%20OpenCV%20소개%20및%20기본%20사용법/OpenCV%20소개%20및%20기본%20사용법.ipynb
OpenCV 介绍及基本使用方法
```

## 扩展学习

### ArUco 空间定位

ArUco 标记可以用于空间定位（需要摄像头）。

参考资料：

```text
https://www.guyuehome.com/wap/detail?id=1825476719146790913
```

## 常见问题

**Docker 容器无法启动？**

- 检查 Docker Desktop 是否正在运行
- 确认端口 6080 没有被其他程序占用

**OpenCV 导入失败？**

- 确认已正确安装：`pip list | grep opencv`
- 尝试重新安装：`pip install --upgrade opencv-python`

**图像颜色显示不正确？**

- OpenCV 默认使用 BGR 格式，显示时需要转换为 RGB
- 使用 `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`

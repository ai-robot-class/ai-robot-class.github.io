# Week 11：Docker 进阶与 GitHub Pages 网页部署

本周学习 Docker 的进阶操作，重点学习如何将 GitHub 作业仓库转换为可浏览的网页。

## 课堂内容

1. Docker 进阶指令。
2. Docker 镜像更新与保存。
3. **GitHub Pages 网页部署完整指引**。
4. 轮式机器人介绍。

## Docker 进阶操作

### 获得 Docker 容器 ID

查看正在运行的容器：

```bash
docker ps
```

输出示例：

```text
CONTAINER ID   IMAGE                                    COMMAND
abc123def456   ghcr.io/tiryoh/ros2-desktop-vnc:humble   "/bin/bash"
```

其中 `abc123def456` 就是容器 ID（通常只需要前几位即可，如 `abc123`）。

查看所有容器（包括已停止的）：

```bash
docker ps -a
```

### 停止 Docker 容器

```bash
# 方法 1：优雅停止（推荐）
docker stop <容器ID>

# 方法 2：强制停止
docker kill <容器ID>
```

**示例**：

```bash
docker stop abc123
```

### Docker 镜像更新保存

如果在 Docker 镜像中进行了系统程序安装，需要保存安装的环境时：

```bash
docker commit -m "更新描述" -a "作者" <容器ID> <新镜像名>:<标签>
```

**示例**：

```bash
# 在容器中安装了 opencv 和 pybullet 后保存
docker commit -m "install opencv and pybullet" -a "myname" abc123 my-ros2-env:v1.0
```

**参数说明**：

- `-m`：提交信息，描述这次更新做了什么
- `-a`：作者信息
- `<容器ID>`：要保存的容器 ID
- `<新镜像名>:<标签>`：新镜像的名称和版本标签

**查看保存的镜像**：

```bash
docker images
```

## 课堂任务 1：Docker 环境配置

在 Docker 环境中安装配置第四周的 pybullet 库和上周的 opencv 库后保存新的 docker 镜像。

### 操作步骤

1. 运行 ROS2 Docker 容器：

```bash
docker run -p 6080:80 --security-opt seccomp=unconfined --shm-size=512m \
  -v "$(pwd)/:/home/ws" \
  ghcr.io/tiryoh/ros2-desktop-vnc:humble
```

2. 在容器内安装库（在浏览器 VNC 终端中）：

```bash
# 安装 pybullet
pip3 install pybullet --break-system-packages

# 安装 opencv
pip3 install opencv-python opencv-contrib-python --break-system-packages

# 如果需要，安装 numpy
pip3 install "numpy<2" --break-system-packages
```

3. 打开新终端，查看容器 ID：

```bash
docker ps
```

4. 保存容器为新镜像：

```bash
docker commit -m "install pybullet and opencv" -a "your-name" <容器ID> my-ros2-full:v1.0
```

5. 验证镜像已保存：

```bash
docker images
```

## 课堂任务 2：将 GitHub 作业仓库转为网页

本节提供详细的指引，帮助你将普通的 GitHub 公开仓库转换为可以浏览的 GitHub Pages 网页。

参考示例：

```text
https://course.a-real.me/content/week1.html
```

### 什么是 GitHub Pages？

GitHub Pages 是 GitHub 提供的免费静态网页托管服务。它可以直接将你的 GitHub 仓库中的 Markdown 文件、HTML 文件等转换为可访问的网页。

**优势**：

- 完全免费
- 自动部署，推送代码即更新网页
- 支持自定义域名
- 非常适合展示作业、笔记、项目文档

### 前置准备

确保你的 GitHub 作业仓库满足以下条件：

1. ✅ 仓库是**公开的**（Public）
2. ✅ 仓库中有 `README.md` 文件
3. ✅ 已按照周次整理好目录结构（参考 Week 7 期中作业要求）

**推荐目录结构**：

```text
ai-robotics-homework/
├── README.md           # 首页，介绍整体作业
├── week2/
│   ├── README.md      # Week 2 作业说明
│   └── img/           # Week 2 图片
├── week3/
│   ├── README.md      # Week 3 作业说明
│   └── img/           # Week 3 图片
├── week4/
│   ├── README.md
│   └── img/
└── ...
```

### 步骤 1：开启 GitHub Pages

1. 打开你的 GitHub 作业仓库页面
2. 点击仓库顶部的 **Settings（设置）**

<img src="../images/course-ppt/week7/slide103-01.png" alt="GitHub Settings 位置示意" width="720">

3. 在左侧菜单中找到并点击 **Pages**

4. 在 "Source" 部分，选择：
   - **Source（源）**：`Deploy from a branch`
   - **Branch（分支）**：`main`（或 `master`）
   - **Folder（文件夹）**：`/ (root)`

5. 点击 **Save（保存）**

6. 等待约 1-3 分钟，页面会显示：

```text
Your site is live at https://<你的用户名>.github.io/<仓库名>/
```

**示例**：

- 如果你的用户名是 `zhangsan`
- 仓库名是 `ai-robotics-homework`
- 网页地址就是：`https://zhangsan.github.io/ai-robotics-homework/`

### 步骤 2：配置 Jekyll 主题（可选）

GitHub Pages 默认使用 Jekyll 静态网站生成器来渲染 Markdown 文件。你可以选择一个主题来美化网页。

#### 方法 1：在 Settings 中选择主题（最简单）

1. 在 **Settings → Pages** 页面
2. 找到 **Theme Chooser** 或 **Choose a theme**
3. 选择一个你喜欢的主题（如 Cayman、Minimal、Slate 等）
4. 点击 **Select theme**

系统会自动在你的仓库根目录创建 `_config.yml` 文件。

#### 方法 2：手动创建配置文件

在仓库根目录创建 `_config.yml` 文件：

```yaml
# 网站标题
title: 我的机器人课程作业

# 网站描述
description: AI Robotics 课程作业整理

# 主题选择（可选以下主题）
theme: jekyll-theme-cayman
# theme: jekyll-theme-minimal
# theme: jekyll-theme-slate
# theme: jekyll-theme-architect

# 显示下载按钮（可选）
show_downloads: false
```

**推荐主题**：

- `jekyll-theme-cayman`：现代简洁，适合技术文档
- `jekyll-theme-minimal`：极简风格，适合笔记
- `jekyll-theme-slate`：深色背景，适合代码展示

### 步骤 3：优化首页 README.md

你的 `README.md` 会成为网站首页，建议包含以下内容：

```markdown
# AI 机器人课程作业

本仓库整理了 AI Robotics 课程的每周作业和实验笔记。

## 课程作业目录

- [Week 2：WSL、Ubuntu 与 ROS2 环境配置](week2/)
- [Week 3：GitHub SSH、VS Code 与 ROS2 交互](week3/)
- [Week 4：命令行、机器人基础与 Python 仿真](week4/)
- [Week 5：Linux 目录操作与机器人运动学](week5/)
- [Week 6：传感器介绍与 ROS2 KITTI 实验](week6/)
- [Week 7：Markdown 与 GitHub 作业整理](week7/)
- [Week 8：Docker 安装与 ROS2 桌面容器](week8/)
- [Week 10：Docker 概念与 OpenCV 实验](week10/)

## 关于我

- 姓名：张三
- 学号：2024xxxxx
- 专业：计算机科学与技术

## 项目说明

本项目使用 GitHub Pages 自动部署。

在线访问：[https://你的用户名.github.io/仓库名/](https://你的用户名.github.io/仓库名/)
```

**链接格式说明**：

- `[Week 2：标题](week2/)`：会自动找到 `week2/README.md`
- 确保每个周次文件夹都有 `README.md`

### 步骤 4：优化每周作业 README.md

每个周次的 `README.md` 应该包含：

1. **标题**：清晰的周次标题
2. **作业内容**：简要说明本周做了什么
3. **截图**：嵌入实验截图
4. **代码**：如有代码，使用代码块展示
5. **总结**：学习心得或遇到的问题

**示例**（`week2/README.md`）：

```markdown
# Week 2：WSL、Ubuntu 与 ROS2 环境配置

## 实验内容

本周完成了以下任务：

1. 安装 WSL Ubuntu 22.04
2. 配置 ROS2 Humble 环境
3. 运行 turtlesim 小乌龟节点

## 实验截图

### Ubuntu 安装成功

<img src="img/ubuntu-install.png" alt="Ubuntu 安装" width="600">

### 小乌龟仿真运行

<img src="img/turtlesim.png" alt="小乌龟" width="600">

## 运行命令

\`\`\`bash
# 启动小乌龟节点
ros2 run turtlesim turtlesim_node

# 启动键盘控制
ros2 run turtlesim turtle_teleop_key
\`\`\`

## 遇到的问题

1. **问题**：运行 `ros2` 命令提示 command not found
   **解决**：运行 `source /opt/ros/humble/setup.bash`

## 学习心得

通过本周学习，我掌握了 WSL 的基本使用和 ROS2 的安装配置...

## 返回

[← 返回首页](../)
```

### 步骤 5：图片处理建议

#### 图片路径

确保图片路径正确：

```markdown
<!-- 正确：相对路径 -->
<img src="img/screenshot.png" alt="描述" width="600">

<!-- 或者使用 Markdown 语法 -->
![描述](img/screenshot.png)

<!-- 错误：不要使用绝对路径 -->
<img src="C:\Users\...\screenshot.png" alt="描述">
```

#### 图片大小优化

GitHub Pages 加载速度受图片大小影响，建议：

- 截图控制在 **1MB 以内**
- 宽度设置为 **600-800px**
- 使用 PNG 或 JPG 格式

### 步骤 6：提交更改并等待部署

1. 提交所有更改：

```bash
git add .
git commit -m "配置 GitHub Pages"
git push
```

2. 等待 1-3 分钟，GitHub Actions 会自动部署

3. 访问你的网页：`https://<用户名>.github.io/<仓库名>/`

### 步骤 7：查看部署状态

1. 在仓库页面点击 **Actions** 标签

2. 查看最新的 workflow run：
   - ✅ 绿色对勾：部署成功
   - ❌ 红色叉号：部署失败，点击查看错误日志

3. 如果失败，常见原因：
   - `_config.yml` 格式错误（检查缩进）
   - 仓库不是 Public
   - 文件名大小写错误（Linux 区分大小写）

## 常见问题排查

### 网页显示 404

**原因 1**：GitHub Pages 还未部署完成

- **解决**：等待 3-5 分钟后重新访问

**原因 2**：仓库设置问题

- **解决**：确认 Settings → Pages 中 Source 已设置为 `main` 分支

**原因 3**：仓库是私有的

- **解决**：将仓库改为 Public（Settings → General → Danger Zone → Change visibility）

### 网页样式混乱

**原因**：主题配置问题

- **解决**：检查 `_config.yml` 格式是否正确，确保没有多余空格或缩进错误

### 图片无法显示

**原因 1**：图片路径错误

- **解决**：使用相对路径，如 `img/pic.png` 而不是 `C:\Users\...`

**原因 2**：图片未提交到仓库

- **解决**：确认 `git add .` 包含了图片文件，运行 `git status` 检查

### 链接跳转错误

**原因**：Markdown 链接格式问题

- **解决**：
  - 文件夹链接：`[Week 2](week2/)` 结尾加 `/`
  - 文件链接：`[说明](week2/README.md)`
  - 返回上级：`[返回](../)`

## 进阶技巧

### 自定义域名（可选）

如果你有自己的域名，可以在 Settings → Pages → Custom domain 中配置。

### 添加 Google Analytics（可选）

在 `_config.yml` 中添加：

```yaml
google_analytics: UA-XXXXXXXX-X
```

### 添加网站图标（可选）

在仓库根目录添加 `favicon.ico` 文件。

## 提交作业

完成 GitHub Pages 配置后：

1. 确认网页可以正常访问
2. 在你的作业仓库 `README.md` 中添加网页链接
3. 将网页链接提交到课程作业系统

**示例**：

```markdown
## 在线访问

本作业已部署到 GitHub Pages：

🔗 [https://zhangsan.github.io/ai-robotics-homework/](https://zhangsan.github.io/ai-robotics-homework/)
```

## 轮式机器人介绍

### 轮式机器人分类

轮式机器人（Wheeled Mobile Robots, WMRs）按照轮子配置和运动约束的不同分类：

- 差速驱动机器人（Differential Drive）
- 全向移动机器人（Omnidirectional）
- 阿克曼转向机器人（Ackermann Steering）
- 履带式机器人（Tracked）

### Micromouse 竞赛

Micromouse 是一个经典的机器人迷宫竞赛项目。

参考资料：

```text
https://github.com/kmakise/Micromouse
```

### 轮趣科技 - 阿克曼小车

阿克曼转向机制广泛应用于汽车和四轮机器人。

## 课程后续安排

根据 Slide 140-141：

- **第九周**：网课，理论性的基础知识（包括机器人运动学、控制建模等数学模型）
  - 上传时间：5.18 前

- **第十二周**：视觉/语音交互，小组项目分组和主题确定
- **第十三周**：强化学习用于机器人控制
- **第十四周**：小组项目指导
- **第十五周**：笔试、报告书提交

## 本周作业总结

1. ✅ 掌握 Docker 镜像保存和管理
2. ✅ 完成 pybullet 和 opencv 环境配置
3. ✅ **将 GitHub 作业仓库转换为网页**
4. ✅ 了解轮式机器人基础概念

提交前检查清单：

- [ ] Docker 镜像已保存并测试
- [ ] GitHub Pages 网页可以正常访问
- [ ] 所有周次作业都有 README.md
- [ ] 图片正常显示
- [ ] 链接跳转正确

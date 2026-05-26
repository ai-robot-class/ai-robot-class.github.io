# PyBullet 机器狗迷宫起始代码

这一套代码用于第 14 周项目的 3D 版本：

- 手机作为控制手柄
- `Tailscale` 负责手机和电脑之间的网络通信
- `PyBullet` 中运行四足机器人与迷宫

## 目录

```text
pybullet_dog/
├── server.py
├── index.html
└── requirements.txt
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动方式

在 WSL 中运行：

```bash
python3 server.py
```

默认监听地址：

```text
http://0.0.0.0:8765
```

手机和电脑连入同一个 `Tailscale` 网络后，在手机浏览器中打开：

```text
http://<WSL的Tailscale_IP>:8765
```

## 代码分工

- `server.py`
  - 启动 `PyBullet`
  - 创建一个简单三维迷宫
  - 加载四足机器人
  - 接收网页发送的控制命令
- `index.html`
  - 提供手机遥控器页面
  - 通过 `WebSocket` 向 `server.py` 发送前进、后退、左转、右转、停止命令

## 运行时的协调方式

这一套 starter 采用最简单的单程序结构：

- `server.py` 需要在实验期间持续运行
- 网页控制器只发送控制命令
- 机器人控制与网络接收都在 `server.py` 内部完成

因此不需要再另外启动第二个“读取控制器”的程序。

## 建议学生继续补充的内容

1. 让迷宫结构更复杂
2. 记录探索轨迹
3. 加入终点判定
4. 优化四足机器人动作方式

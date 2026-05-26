# Week 12 起始代码

本目录提供第 12 周课堂的手机摄像头桥接程序。

## 文件

```text
week12_starters/
├── camera_bridge.py
└── requirements.txt
```

## 安装依赖

```bash
pip install -r week12_starters/requirements.txt
```

如果直接运行程序时出现：

```text
No module named 'flask'
```

通常说明这一步还没有执行。

## 运行方式

在仓库根目录运行：

```bash
python3 week12_starters/camera_bridge.py
```

然后在手机浏览器中打开：

```text
https://<WSL的Tailscale_IP>:5000
```

## 课堂中的使用方式

- 这个程序在实验期间需要持续运行
- 手机网页负责调用摄像头并发送视频帧
- 程序内部负责接收图像、显示图像并实时检测 ArUco
- 停止程序时，在终端按 `Ctrl+C`

## 默认 ArUco 设置

- 字典：`DICT_4X4_50`
- 课堂统一 marker：`ID 6`

如果生成 marker 时改用了别的具体字典，程序中的字典常量也要改成对应值。

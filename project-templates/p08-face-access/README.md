# 项目 8：人脸识别门禁系统

> ⭐⭐⭐⭐ · 技术：face_recognition (dlib) + SQLite + ROS2

## 🎯 项目目标

摄像头识别人脸 → 比对数据库 → 已注册=开门，陌生人=报警

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
# 注册人脸
ros2 run face_access enroll --name "张三" --image alice.jpg

# 启动识别
ros2 run face_access recognizer_node
```

## ✍️ 你要做的（TODO 列表）

### TODO 1：`enroll_face`

从图片提取人脸 encoding，写入 SQLite 数据库（id, name, encoding）

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 2：`recognize_face`

实时摄像头帧 → 提取 encoding → 与数据库比对，返回 name 或 "stranger"

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 3：`control_door`

识别成功发布 "/door/open" 话题；陌生人发布 "/alarm" 并保存抓拍照片

```python
# 在源码中找到这个函数，按注释提示实现
```



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

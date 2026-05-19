# 项目 9：PyBullet 机械臂仿真抓取

> ⭐⭐⭐⭐⭐ · 技术：PyBullet + 内置 Kuka/Franka URDF + 视觉伺服

## 🎯 项目目标

在 PyBullet 仿真中：机械臂识别桌面方块位置 → 规划抓取 → 放入指定箱子

## 📦 数据来源（无需任何硬件）

✅ **完全仿真**：
- 机械臂：PyBullet 自带 Kuka iiwa（7 DoF）/ Franka Panda
- 物体：随机放置的彩色方块（红/绿/蓝各 3 个）
- 仿真相机：PyBullet 内置（不需要真实摄像头）

## ⚙️ 运行模式

| 模式 | 工具 |
|------|------|
| 🟢 **默认** | PyBullet 仿真（CPU 跑得动） |
| 🟢 **可选** | MoveIt2 + Gazebo（更高保真，需更多 CPU/RAM） |

## 🚀 快速启动

```bash
# 1. 启动容器（首次约 2-5 分钟）
docker compose up -d
docker compose exec dev bash

# 2. 下载数据集（如有）
bash demo/download_data.sh 2>/dev/null || true

# 3. 编译
colcon build && source install/setup.bash

# 4. 默认无硬件模式运行
python -m arm_grasp.run --robot kuka --target_color red \
    --save_video grasp.mp4
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`detect_blocks`

从 PyBullet 仿真相机获取 RGB+depth，用 OpenCV 阈值分割检测彩色方块的世界坐标

### TODO 2：`inverse_kinematics`

用 `p.calculateInverseKinematics` 给定目标位姿，求 7 DoF 关节角

### TODO 3：`pick_and_place`

编排完整流程：靠近 → 闭合夹爪 → 抬起 → 移到箱子 → 释放



## 🧪 测试

```bash
pytest test/

# 项目特定的端到端测试
bash test/integration_test.sh
```

## 📊 评分要点

| 评分点 | 占比 |
|--------|------|
| 3 个 TODO 实现正确性 | 40% |
| 在提供数据集上的运行效果 | 30% |
| 代码质量（注释、命名、模块化）| 15% |
| 文档完整度 + 演示视频 | 10% |
| **加分**：自己采集额外数据/改进算法 | +5% |

## 💡 提示

- 把 `templates/` 下的骨架代码读一遍，理解整体流程
- 不会写时去看 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) 或官方教程
- **卡住超过 30 分钟立即在课程群提问**，不要硬磕

## 🌟 加分项

- 录制 2-3 分钟的演示视频上传
- 在 README 中写技术博客式的开发记录
- 测试自己的算法在更多数据上的效果
- 提供完整的可视化（matplotlib/rviz）

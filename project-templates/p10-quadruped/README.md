# 项目 10：四足机器人基础控制

> ⭐⭐⭐⭐⭐ · 技术：PyBullet + 步态生成 + 控制算法

## 🎯 项目目标

在 PyBullet 中让四足机器人（Laikago）实现 Trot 步态走直线

## 🚀 快速启动

```bash
# 启动容器
docker compose up -d
docker compose exec dev bash

# 编译
colcon build && source install/setup.bash

# 运行
python -m quadruped.run_trot --frequency 1.5
```

## ✍️ 你要做的（TODO 列表）

### TODO 1：`compute_leg_phase`

为 4 条腿生成 Trot 步态的相位（对角腿同步，相差半周期）

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 2：`inverse_kinematics_leg`

给定目标足端位置 (x, y, z)，反解出髋/大腿/小腿 3 个关节角度

```python
# 在源码中找到这个函数，按注释提示实现
```

### TODO 3：`gait_step`

在每个仿真步：根据时间 t 计算每条腿当前应在的足端位置 → IK → 发关节指令

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

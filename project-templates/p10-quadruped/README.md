# 项目 10：PyBullet 四足机器人步态优化

> ⭐⭐⭐⭐⭐ · 技术：PyBullet + Trot 步态 + CMA-ES 参数优化

## 🎯 项目目标

让 Laikago 四足机器人在仿真中实现 Trot 步态走直线，并用 CMA-ES 自动调参提升速度

## 📦 数据来源（无需任何硬件）

✅ **完全仿真**：
- 模型：PyBullet 自带 Laikago URDF（也支持 A1、Anymal）
- 地形：平地 / 斜坡 / 阶梯（来自 pybullet_data）

## ⚙️ 运行模式

| 模式 | 资源 |
|------|------|
| 🟢 **默认** | PyBullet 仿真，CPU 单核可跑 |
| 🟢 **加速可选** | 关闭 GUI 渲染（headless）跑参数搜索更快 |

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
# 默认参数走一遍
python -m quadruped.run_trot --duration 10

# 用 CMA-ES 自动调参（headless 模式更快）
python -m quadruped.optimize --headless --iters 50

# 用最优参数跑并录像
python -m quadruped.run_trot --params best_params.npy --save_video trot.mp4
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`trot_phase_generator`

生成 4 条腿的 Trot 步态相位（对角线腿同步，相位相差 π）

### TODO 2：`inverse_kinematics_leg`

给定足端目标位置 (x,y,z)，反解出髋/大腿/小腿关节角度

### TODO 3：`optimize_gait_params`

用 CMA-ES 优化 [步频, 步长, 抬腿高度] 三个参数，目标是 10 秒内走得最远



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

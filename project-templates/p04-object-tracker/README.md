# 项目 4：MOT17 / KITTI Tracking 多目标追踪

> ⭐⭐⭐ · 技术：YOLOv8 + SORT + ROS2 bag

## 🎯 项目目标

在 MOT17 行人追踪数据集上跑 YOLO + SORT，输出带 track_id 的视频，计算 MOTA/IDF1 指标

## 📦 数据来源（无需任何硬件）

课程提供数据集子集：
- `demo/MOT17-04.mp4` （525 帧行人场景）
- `demo/MOT17-04-gt.txt`（真值标注）

完整 MOT17：https://motchallenge.net/data/MOT17/

## ⚙️ 运行模式

| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认** | `demo/MOT17-04.mp4` | `tracked.mp4` + `metrics.json` |
| 🟡 **扩展（有摄像头）** | `/dev/video0` | 实时追踪可视化 |

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
# 端到端跑通
python -m object_tracker.run --video demo/MOT17-04.mp4 \
    --gt demo/MOT17-04-gt.txt \
    --output tracked.mp4

# 输出
# tracked.mp4 - 带 track ID 的可视化
# metrics.json - MOTA 等指标
# 期末报告: 对比不同 IoU 阈值的 MOTA 变化
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`init_tracker`

初始化 SORT：每个 Track 内置卡尔曼滤波器（状态 = [x, y, s, r, vx, vy, vs]）

### TODO 2：`match_detections`

用匈牙利算法 (`scipy.optimize.linear_sum_assignment`) 关联 detection ↔ track（IoU 阈值 0.3）

### TODO 3：`compute_motrics`

用 `motmetrics` 计算 MOTA / IDF1 / FP / FN / IDsw 五项指标



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

## 🔌 扩展：使用真实硬件

如果你有 `/dev/video0`，把它加到 `docker-compose.yml` 的 `devices:` 字段，然后用 `--source camera` 参数运行。但**不是必须**。

## 💡 提示

- 把 `templates/` 下的骨架代码读一遍，理解整体流程
- 不会写时去看 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) 或官方教程
- **卡住超过 30 分钟立即在课程群提问**，不要硬磕

## 🌟 加分项

- 录制 2-3 分钟的演示视频上传
- 在 README 中写技术博客式的开发记录
- 测试自己的算法在更多数据上的效果
- 提供完整的可视化（matplotlib/rviz）

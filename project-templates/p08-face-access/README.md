# 项目 8：基于人脸数据集的识别系统

> ⭐⭐⭐⭐ · 技术：face_recognition (dlib) + SQLite + ROS2

## 🎯 项目目标

用公开人脸数据集训练注册库，对测试集图片做人脸识别，计算准确率/召回率

## 📦 数据来源（无需任何硬件）

课程提供数据集（已过滤许可允许的子集）：
- `demo/known_faces/`：10 个人，每人 5 张训练照片
- `demo/test_faces/`：50 张测试照片（含已注册和陌生人）
- `demo/test_labels.csv`：测试集真值标注

学生也可用：
- LFW (http://vis-www.cs.umass.edu/lfw/)
- 自己和朋友的照片（合规收集，并签同意书）

## ⚙️ 运行模式

| 模式 | 输入 | 输出 |
|------|------|------|
| 🟢 **默认** | `demo/test_faces/*.jpg` | accuracy_report.json |
| 🟡 **扩展（有摄像头）** | `/dev/video0` | 实时识别+开门信号 |

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
# 1. 注册已知人脸
python -m face_access.enroll --dir demo/known_faces --db faces.db

# 2. 在测试集上评估
python -m face_access.evaluate --test demo/test_faces \
    --labels demo/test_labels.csv --db faces.db

# 输出：accuracy_report.json + confusion_matrix.png
```

## ✍️ 你要做的（3 个 TODO 函数）

### TODO 1：`enroll_known_faces`

遍历 `known_faces/<人名>/*.jpg`，提取 128 维 face encoding，存入 SQLite

### TODO 2：`recognize_image`

加载测试图片，提取 encoding，与数据库比对（threshold=0.6），返回识别结果

### TODO 3：`compute_metrics`

在测试集上跑识别，计算 confusion matrix + 准确率/精度/召回率/F1



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

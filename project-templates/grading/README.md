# 🎯 期末项目自动评分系统

> 自动化评估学生项目完成度，**学生可以自查、老师批量打分**。

## 🚀 快速开始

### 学生自查（最常用）

在你的项目目录下运行：

```bash
# 方法 1：在 Docker 容器内
docker compose exec dev bash -c "
  cd /workspace
  python3 ../grading/run_grading.py . --student YOUR_GITHUB_ID
"

# 方法 2：在本地（需要装好 Python 依赖）
cd p01-color-tracker
python3 ../grading/run_grading.py . --student YOUR_GITHUB_ID
```

输出示例：

```
============================================================
📋 评分报告: 基于视频的颜色追踪
============================================================
  学生: YOUR_GITHUB_ID
  总分: 85.0/100  (85.0%)
  等级: A

  各维度得分:
    ✅ 项目结构完整                10.0/10
    ✅ TODO 函数实现正确            32.0/40
        ✅ TODO `detect_color` 已实现
        ✅ TODO `compute_twist` 已实现
        ❌ TODO `image_callback` 未实现: 函数体过短
    ✅ 集成测试通过                28.0/30
        ✅ 输出视频生成成功 (1234567 bytes)
        ✅ ROS bag 生成成功
    ✅ 代码质量                    8.0/10
        ⚠️  3 个 lint 警告（轻微）
    ✅ 文档与提交规范              7.0/10
        ✅ README 内容充实
        ✅ Git 提交 12 次
        ⚠️  未发现演示视频
============================================================
```

### 教师批量评分

```bash
# 评分单个项目
python3 grading/run_grading.py /path/to/student-repo/p01-color-tracker --student alice

# 批量评分一个学生的所有项目
python3 grading/run_grading.py /path/to/student-repo --all --student alice

# 输出 JSON 报告
python3 grading/run_grading.py . --student alice --output report.json

# 输出 Markdown 报告（便于上传给学生看）
python3 grading/run_grading.py . --student alice --markdown report.md
```

## 📊 评分维度

每个项目满分 100 分，分为 5 个维度：

| 维度 | 占比 | 说明 |
|------|------|------|
| 🗂️ **项目结构** | 10% | README/Dockerfile/docker-compose.yml 是否齐全 |
| ✅ **TODO 函数** | 40% | 3 个核心 TODO 是否真的实现了（非 `pass`）|
| 🔄 **集成测试** | 30% | 跑通端到端流程，检查输出文件质量 |
| 🎨 **代码质量** | 10% | `ruff` lint 检查 |
| 📄 **文档与提交** | 10% | README 详细度、Git 提交次数、演示输出 |

### TODO 函数检测原理

系统会：
1. 加载学生的 `src/PROJECT/MODULE.py`
2. 检查每个必需的函数是否存在
3. 用 `inspect.getsource` 读取函数源码
4. 判断函数体是否只有 `pass` / `raise NotImplementedError` / `...`
5. **不只是写了函数签名就算实现**

### 集成测试

每个项目有不同的端到端测试：

| 项目 | 测试方法 | 通过标准 |
|------|---------|---------|
| P01 颜色追踪 | 跑 demo 视频，看是否输出 mp4/bag | 文件存在且大小 > 10KB |
| P02 语音解析 | 解析 demo wav，画轨迹 | 轨迹图存在 |
| P03 KITTI 检测 | 跑 KITTI 视频，输出 CSV | CSV 含 >10 条检测 |
| P04 MOT17 追踪 | 跑数据集，计算 MOTA | MOTA ≥ 0.3 满分 |
| P05 Nav2 | 检查 nav2_params 配置 | YAML 字段齐全 |
| P06 手势识别 | 处理手势视频 | CSV 含命令记录 |
| P07 巡检 | 检查 waypoints 配置和 PDF | 配置+PDF 都齐 |
| P08 人脸识别 | 跑测试集 | accuracy ≥ 0.8 满分 |
| P09 机械臂 | 仿真抓取 | success=true |
| P10 四足步态 | 5 秒走直线 | distance ≥ 1m 满分 |

## 🤖 GitHub Action 自动评分

学生 push 后，可以让 Action 自动评分。在你的项目仓库 `.github/workflows/grade.yml`：

```yaml
name: 自动评分

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  grade:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: 安装评分依赖
        run: |
          pip install ruff numpy opencv-python pandas pyyaml

      - name: 拉取课程评分系统
        run: |
          git clone --depth 1 https://github.com/ai-robot-class/ai-robot-class.github.io.git /tmp/course
          cp -r /tmp/course/project-templates/grading .

      - name: 运行评分
        run: |
          python3 grading/run_grading.py . --all \
            --student ${{ github.repository_owner }} \
            --output grade_report.json \
            --markdown grade_report.md

      - name: 提交评分报告
        run: |
          git config user.name "Auto Grader"
          git config user.email "grader@bot"
          git add grade_report.*
          git diff --staged --quiet || git commit -m "📊 自动评分报告"
          git push
```

## 🔧 评分系统架构

```
project-templates/
├── grading/
│   ├── __init__.py           # 包入口
│   ├── base_grader.py        # 通用基类（5 个评分维度）
│   ├── run_grading.py        # 统一入口脚本
│   ├── gen_graders.py        # 生成各项目 grader.py 的脚本
│   └── README.md             # 本文档
├── p01-color-tracker/
│   ├── grader.py             # P01 专属评分器（继承 BaseGrader）
│   └── ...
└── ...
```

## 💡 学生最佳实践

1. **本地频繁自查**：每写完一个 TODO 就跑一遍评分脚本
2. **关注每个维度**：不要只追求 TODO 满分，文档/质量也很重要
3. **提交前必查**：push 前确保本地评分 ≥ 60 分（C 等级以上）
4. **完整测试**：让集成测试通过，输出实际的 mp4/csv/json 等
5. **多次 commit**：评分会看 Git 提交次数，建议 ≥ 5 次

## 🛠️ 自定义评分器

如果你的项目有特殊评分需求，编辑对应的 `pXX/grader.py`，
继承 `BaseGrader` 并重写 `grade_xxx` 方法：

```python
from grading.base_grader import BaseGrader

class MyGrader(BaseGrader):
    PROJECT_NAME = "p01-color-tracker"
    PROJECT_TITLE = "颜色追踪"
    REQUIRED_TODOS = ['detect_color', 'compute_twist']
    SRC_MODULE = "color_tracker.tracker_node"

    def grade_integration(self):
        """自定义集成测试逻辑"""
        item = self.items['integration']
        # ... 你的测试代码
```

## ❓ 常见问题

### Q: 评分显示"无法 import 模块"？

A: 确保 `src/PROJECT/__init__.py` 存在，且模块路径正确。

### Q: TODO 函数判定为"未实现"，但我确实写了代码？

A: 系统检查函数体是否只有 `pass` 或 `NotImplementedError`。
如果你的实现确实只有 1 行（比如直接返回），可以加一些注释或拆分逻辑。

### Q: 集成测试运行超时？

A: 默认超时时间在 60-300 秒，可以在 `grader.py` 中调整 `run_command(timeout=N)`。

### Q: 评分系统能识别多人合作的项目吗？

A: 评分是按"项目目录"运行，不区分作者。如果是 2-3 人合作，
   每位学生可以在自己的 fork 仓库里跑相同的评分，得到一样的分数。

---

*📊 让评分公平、透明、可复现*

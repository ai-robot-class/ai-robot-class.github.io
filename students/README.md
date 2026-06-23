# 👥 学生作业实时展示

> 🤖 通过 GitHub Actions 每 24 小时自动评价学生 GitHub 作业仓库

## 🌐 实时展示面板

<div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 40px 20px; border-radius: 16px; text-align: center; margin: 20px 0; color: white; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
  <h2 style="color: white; margin-bottom: 16px;">📊 点击下方链接查看实时展示面板</h2>
  <p style="margin-bottom: 24px; opacity: 0.95;">包含所有学生的成绩卡片、详情表格和统计数据</p>
  <a href="./index.html" style="display: inline-block; padding: 14px 32px; background: white; color: #667eea; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 1.05em; box-shadow: 0 4px 14px rgba(0,0,0,0.15);">
    🚀 打开学生作业展示面板 →
  </a>
</div>

> 直接访问：[https://ai-robot-class.github.io/students/](./index.html)

## 📋 展示面板内容

- 📈 **实时统计**：学生总数、可访问仓库数、平均分、最高分
- 🎯 **学生卡片**：每位学生的 GitHub 头像、ID、等级、总分、各周完成情况
- 📊 **详情表格**：每周作业加权得分一览，颜色编码显示完成质量
- 🏆 **自动排名**：按总分排序，激励学生进步

## 🎯 评分制度（总分 100 分）

### 评分维度

| 维度 | 占比 | 评价标准 |
|-----|------|---------|
| **内容完成度** | 70 分 | README 质量（最高 49 分）、图片（15 分）、代码（15 分）、视频/文档（5 分） |
| **学习态度** | 30 分 | 提交次数（15 分）、提交及时性（15 分） |

### 每周权重

| 周次 | 权重 | 主题 |
|------|------|------|
| Week 2  | 5 分  | ROS2 环境配置 |
| Week 3  | 5 分  | GitHub 与命令行 |
| Week 4  | 8 分  | Python 仿真 |
| Week 5  | 8 分  | 机器人运动学 |
| Week 6  | 8 分  | KITTI 实验 |
| Week 7  | 5 分  | Markdown 整理 |
| Week 8  | 8 分  | Docker 容器 |
| Week 9  | 8 分  | 数学基础（网课）|
| Week 10 | 10 分 | YOLO 检测 |
| Week 11 | 10 分 | 目标追踪 |
| Week 12 | 10 分 | 视觉与语音 |
| Week 13 | 8 分  | 四足机器人入门（`week13_walk/`） |
| Week 14 | 7 分  | 小组项目（手机遥控迷宫，`week14/` + PDF） |
| **总计** | **100 分** | |

### 等级评定

| 分数段 | 等级 | 说明 |
|-------|-----|------|
| 90-100 | A+/A | 卓越 |
| 80-89  | A-/B+ | 优秀 |
| 70-79  | B/B-  | 良好 |
| 60-69  | C+/C  | 合格 |
| 50-59  | C-    | 及格 |
| 30-49  | D     | 待改进 |
| <30    | F     | 不及格 |

## 🔒 隐私保护

- ✅ 仅显示 **GitHub ID** 和 **公开头像**
- ❌ 不存储学生**真实姓名**
- ❌ 不存储学生**学号**
- ❌ 不存储任何**个人隐私信息**

详细规则见 [隐私保护说明](../PRIVACY.md)。

## 📝 提高得分的建议

1. **每周按时提交**：在课后一周内完成本周作业
2. **撰写详细 README**：超过 1500 字符可获得 README 满分
3. **包含问题与思考**：README 中提到"问题/思考/难点"加 3 分
4. **撰写学习总结**：README 中包含"总结/心得/收获"加 3 分
5. **添加运行截图**：建议每个作业 3-5 张关键截图
6. **代码文件齐全**：把可运行代码完整提交
7. **多次提交迭代**：体现持续学习的态度

## 📂 推荐仓库结构

```
your-ai-robot-homework/
├── README.md            # 总说明（推荐写本人简介与作业概览）
├── week2/
│   ├── README.md
│   └── screenshots/
├── week3/
│   ├── README.md
│   └── ...
├── ...
└── week13_walk/
    ├── quadruped_walk.py
    ├── ai_chat_log.md
    └── reflection.md
└── week14/
    ├── week14_组名.pdf
    ├── server.py / turtlesim_web_bridge.py
    └── demo.mp4
```

## 🤖 自动评价工作流

```
每日 22:00（北京时间）
       ↓
GitHub Actions 触发
       ↓
读取 students/roster.json
       ↓
通过 GitHub API 分析每个仓库（文件树 + commit 历史）
       ↓
按维度评分（内容 + 态度，加权计算总分）
       ↓
生成 students/evaluations/latest.json
       ↓
生成 students/index.html（带统计与详情）
       ↓
自动提交到 main 分支 → 部署到 GitHub Pages
```

## ⏰ 运行周期

- **触发频率**：每 24 小时自动运行（北京时间 22:00）
- **截止时间**：2026 年 6 月 22 日
- **手动触发**：可在 GitHub Actions 页面手动运行
- **触发条件**：`students/roster.json` 或 `scripts/*` 修改时也会自动运行

---

*🤖 自动化评价 · Powered by GitHub Actions · 维护者: AI Robot Class*

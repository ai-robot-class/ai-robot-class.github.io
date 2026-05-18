# 👥 学生作业实时展示

> 🤖 本页面通过 GitHub Actions 每24小时自动更新学生作业完成情况

## 🌐 在线展示页面

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0;">

### 📊 [→ 点击查看学生作业实时展示面板 ←](./index.html)

<br>

**或访问**：[https://ai-robot-class.github.io/students/](https://ai-robot-class.github.io/students/)

</div>

展示面板包含：
- 📈 **实时统计**：总人数、可访问仓库数、平均分
- 🎯 **学生卡片**：每位学生的 GitHub 头像、ID、得分、等级
- 📊 **详情表格**：每周作业完成情况一览
- 🏆 **自动排名**：按总分排序，激励学生进步

## 🎯 评价系统说明

### 评分制度（总分100分制）

| 维度 | 占比 | 评价标准 |
|-----|------|---------|
| **内容完成度** | 70% | README质量、代码、图片、文档等 |
| **学习态度** | 30% | 提交频率、及时性 |

### 每周权重分配

| 周次 | 权重 | 主题 |
|------|------|------|
| Week 2 | 5分 | ROS2环境配置 |
| Week 3 | 5分 | GitHub与命令行 |
| Week 4 | 8分 | Python仿真 |
| Week 5 | 8分 | 机器人运动学 |
| Week 6 | 8分 | KITTI实验 |
| Week 7 | 5分 | Markdown整理 |
| Week 8 | 8分 | Docker容器 |
| Week 9 | 8分 | 数学基础（网课）|
| Week 10 | 10分 | YOLO检测 |
| Week 11 | 10分 | 目标追踪 |
| Week 12 | 10分 | 视觉与语音 |
| Week 13 | 15分 | **期末项目** |
| **总计** | **100分** | |

### 等级评定

| 总分 | 等级 |
|------|------|
| 90-100 | A+ |
| 85-89 | A |
| 80-84 | A- |
| 75-79 | B+ |
| 70-74 | B |
| 65-69 | B- |
| 60-64 | C+ |
| 55-59 | C |
| 50-54 | C- |
| <50 | D |

## 📋 学生名单管理

### 添加学生

只需要编辑 `students/roster.json`，添加 GitHub 仓库 URL：

```json
[
  "https://github.com/zhangsan/ai-robot-homework",
  "https://github.com/lisi/ai-robotics-course"
]
```

> 🔒 **隐私保护**：系统仅存储 GitHub 仓库 URL。GitHub ID 从 URL 自动提取。不存储学生姓名、学号等敏感信息。

## 🤖 自动评价系统

### 工作流程

```
GitHub Actions（每24小时）
       ↓
读取 roster.json
       ↓
调用 GitHub API 分析每个仓库
       ↓
评分（内容 + 态度）
       ↓
生成 latest.json
       ↓
生成 index.html
       ↓
自动提交并部署到 GitHub Pages
```

### 运行计划

- **触发时机**：每天北京时间 22:00（UTC 14:00）
- **运行周期**：2026年5月18日 ～ 2026年6月22日
- **手动触发**：在 Actions 页面手动运行 workflow

## 🎯 作业要求

### 推荐仓库结构

```
ai-robot-homework/
├── README.md          # 项目总说明
├── week2/
│   ├── README.md      # 本周作业说明
│   └── screenshots/   # 截图
├── week3/
│   ├── README.md
│   └── ...
├── week4/
│   ├── README.md
│   ├── *.py          # Python代码
│   └── images/
...
└── week13/
    ├── README.md
    ├── code/
    ├── demo.mp4       # 期末项目演示
    └── docs/
```

### 每周 README 应包含

1. **作业内容**：本周学习内容
2. **完成情况**：完成的任务清单
3. **运行截图**：效果展示
4. **遇到的问题**：问题与解决方案（加分项！）
5. **收获总结**：学习心得（加分项！）

### README 示例

```markdown
# Week 2: ROS2环境配置

## 作业内容
完成ROS2 Humble环境搭建和turtlesim测试。

## 完成情况
- [x] 安装WSL2 Ubuntu 22.04
- [x] 安装ROS2 Humble
- [x] 运行turtlesim节点
- [x] 使用命令行控制小乌龟

## 运行截图
![Turtlesim](screenshots/turtlesim.png)

## 遇到的问题
### 问题1: ROS2命令不识别
**解决方案**: 执行 `source /opt/ros/humble/setup.bash`

## 收获总结
通过本周学习，掌握了WSL2的使用...
```

## 💡 高分建议

1. **及时提交**：每周作业按时完成，避免延迟扣分
2. **详细文档**：README 越详细，得分越高（>1500字符可得满分）
3. **包含问题思考**：在 README 中讨论遇到的问题、解决方案
4. **加学习总结**：记录心得体会
5. **多张截图**：包含运行效果图、关键步骤截图
6. **代码注释**：代码文件包含详细注释
7. **多次迭代**：通过多次 commit 改进作业

## 🔒 隐私说明

- ✅ 仅展示 GitHub ID 和头像
- ❌ 不公开学生真实姓名
- ❌ 不公开学生学号
- ❌ 不公开任何个人隐私信息

详见 [隐私保护说明](../PRIVACY.md)

---

*🤖 自动化评价 · Powered by GitHub Actions*

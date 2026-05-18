# 学生作业展示

> 🤖 本页面自动展示所有学生的GitHub作业仓库和完成情况

## 📊 在线查看

访问 [学生作业展示页面](https://areal2025.github.io/students/) 查看实时统计和所有学生的作业情况。

## 📋 学生名单管理

### 添加学生

编辑 `students/roster.json` 文件，添加学生的GitHub仓库URL：

```json
[
  "https://github.com/zhangsan/ai-robot-homework",
  "https://github.com/lisi/ai-robotics-course",
  "https://github.com/wangwu/robot-homework"
]
```

> 💡 **隐私保护**：系统只存储GitHub仓库URL，不存储学生姓名和学号等敏感信息。GitHub ID从URL中自动提取。

## 🤖 自动评价系统

### 工作原理

系统每天自动运行，检查所有学生的GitHub仓库：

1. **检查仓库结构**
   - 每周作业是否有对应的文件夹（week2, week3, ...）
   - README.md是否存在且内容详细
   - 是否包含代码文件和截图

2. **评分标准**（每周100分）
   ```
   ✅ 提交作业文件夹: 基础分
   ✅ README.md存在: +30分
   ✅ README内容详细(>500字): +10分
   ✅ 包含图片/截图: +20分
   ✅ 包含代码文件: +20分
   ✅ 有提交记录: +10分
   ✅ 按时提交: +10分
   ```

3. **生成报告**
   - 每周得分
   - 总分和平均分
   - 作业完成进度
   - 排名情况

### 手动触发评价

访问Actions页面，手动运行"学生作业自动评价"工作流。

## 📈 评价结果文件

评价结果保存在以下位置：

- `students/evaluations/latest.json` - 最新评价结果
- `students/evaluations/evaluation_YYYYMMDD_HHMMSS.json` - 历史记录
- `students/index.html` - 可视化展示页面

## 🎯 作业要求

### 仓库结构

```
ai-robot-homework/
├── README.md          # 总说明
├── week2/
│   ├── README.md      # 本周作业说明
│   └── screenshots/   # 截图
├── week3/
│   ├── README.md
│   ├── code/          # 代码文件
│   └── images/
├── week4/
│   ├── README.md
│   ├── *.py          # Python代码
│   └── images/
...
└── week13/
    ├── README.md
    ├── code/
    ├── demo.mp4      # 演示视频
    └── docs/
```

### 每周README要求

每个week文件夹的README.md应包含：

1. **作业内容**：简要说明本周学习内容
2. **完成情况**：列出完成的任务
3. **运行截图**：展示运行效果
4. **遇到的问题**：记录问题和解决方案
5. **收获总结**：学习心得

### 示例README

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
![Terminal](screenshots/terminal.png)

## 遇到的问题

### 问题1: ROS2命令不识别
**解决方案**: 执行`source /opt/ros/humble/setup.bash`

### 问题2: turtlesim窗口不显示
**解决方案**: 安装VcXsrv，配置DISPLAY变量

## 收获总结

通过本周学习，掌握了WSL2的使用，成功搭建了ROS2环境...
```

## 🏆 排名规则

- 按总分排序
- 总分 = 所有周次得分之和
- 平均分 = 总分 / 周次数量
- 考虑提交及时性

## 📱 查看个人成绩

访问展示页面，找到自己的卡片（通过GitHub ID识别）查看：
- ✅ 已完成的周次
- 📊 每周得分
- 📈 总分和平均分
- 🏅 当前排名

> 🔒 **隐私说明**：系统仅展示GitHub ID和头像，不公开学生真实姓名和学号。

## 🔧 技术栈

- **GitHub Actions**: 自动化评价
- **PyGithub**: GitHub API交互
- **Python**: 评价脚本
- **HTML/CSS**: 展示页面

## 💡 提示

1. **及时提交**：每周作业建议在截止日期前完成
2. **规范命名**：使用week2, week3等标准命名
3. **详细文档**：README内容越详细，得分越高
4. **展示效果**：多加截图和代码注释
5. **持续改进**：参考高分同学的仓库结构

## 📞 联系方式

如有问题，请：
1. 在课程GitHub仓库提Issue
2. 微信群内提问
3. 课堂答疑时间询问

---

*自动更新 · Powered by GitHub Actions*

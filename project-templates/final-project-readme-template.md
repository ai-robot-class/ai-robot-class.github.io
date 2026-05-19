# 🎓 期末项目 - 个人贡献说明（模板）

> ⚠️ 使用说明：复制这份模板到你**作业仓库**的 `final-project/README.md`，按 `<...>` 提示填写
>
> 📌 项目代码本身放在另一个独立仓库中，通过 Git submodule 引用到 `final-project/project-repo/`

---

## 📌 项目信息

- **项目名称**：<填写：你的项目名称>
- **项目编号**：<填写：P01-P10>
- **项目仓库**：[<项目仓库名>](<填写：项目仓库 URL>)
- **submodule 路径**：`final-project/project-repo/`

## 👥 团队成员

> 单人完成请填："独立完成所有任务"

| GitHub ID | 角色 | 主要负责模块 |
|-----------|------|-------------|
| @<id1> | 组长 | <如：detect_color 函数实现> |
| **@<本人 id>（本人）** | <角色> | <如：compute_twist + 集成测试> |
| @<id3> | 组员 | <如：演示视频、文档撰写> |

## 🎯 我在项目中的具体贡献

### 📝 核心功能实现

> 列出你**亲自完成**的 TODO 函数或模块。每项都要附 commit 链接证明。

#### 1. `<函数名 1>`
- **位置**：[`src/.../xxx.py#LXX-LYY`](<填写文件位置 URL>)
- **思路**：<用一句话说明你的实现思路>
- **关键 commits**：
  - [`<short_sha>`](<填写 commit URL>) - <commit 说明>
  - [`<short_sha>`](<填写 commit URL>) - <commit 说明>

#### 2. `<函数名 2>`
- **位置**：...
- **思路**：...
- **关键 commits**：...

#### 3. `<函数名 3>` 或其他贡献
- ...

### 📊 我的 Git 提交统计

```bash
# 在项目仓库目录运行，统计我的提交数：
git log --author="<我的 GitHub 邮箱>" --oneline | wc -l
```

我的 commit 列表（自动复制粘贴）：

```
<填写：git log --author="..." --oneline 的输出>
```

我的 commit 比例：`<我的 commit 数> / <团队总 commit 数>` = `<比例>%`

### 🧠 学习收获

<填写：3-5 条你在这个项目中学到的具体技能或概念>

- 例如：理解了 ROS2 节点的发布订阅模式
- 学到了 OpenCV HSV 颜色空间的优势
- 体会到 Git submodule 在工程化中的价值
- ...

### 🐛 遇到的问题与解决方案

> 重点写 2-3 个让你"卡了 30 分钟以上"的问题，体现真实开发过程

#### 问题 1：<问题简述>
- **现象**：<具体报错信息或表现>
- **排查过程**：<你试了什么方法>
- **最终方案**：<什么解决的>

#### 问题 2：<问题简述>
- ...

## 🎬 项目演示

- 📹 [演示视频（B 站/YouTube）](<填写视频链接>)
- 📷 运行截图：见 `screenshots/` 文件夹
- 📊 完整运行报告：[`grade_report.md`](./grade_report.md)

## 🔍 评分自查

我用课程评分系统跑出的最终成绩：

```
总分：<X>/100
等级：<等级>

各维度：
  ✅ 项目结构完整        <X>/10
  ✅ TODO 函数实现       <X>/40
  ✅ 集成测试通过        <X>/30
  ✅ 代码质量            <X>/10
  ✅ 文档与提交规范      <X>/10
```

跑分命令：
```bash
cd final-project/project-repo
python3 ../../grading/run_grading.py . --student <github_id>
```

## 🔗 重要链接

- 📦 [项目主仓库](<URL>)
- 📋 [我发起的 PR 列表](https://github.com/<org>/<repo>/pulls?q=author%3A<我的id>)
- 💻 [我的所有 commit](https://github.com/<org>/<repo>/commits?author=<我的id>)
- 🌐 [项目 GitHub Pages（如有）](<URL>)

## 📝 如何使用本作业仓库（给评审教师）

```bash
# 完整克隆（包含 submodule）
git clone --recursive <作业仓库 URL>
cd <作业仓库>

# 进入项目仓库并运行
cd final-project/project-repo
docker compose up -d
docker compose exec dev bash
# 在容器内：
colcon build && source install/setup.bash
# 运行项目（具体命令见 project-repo/README.md）
```

---

*✍️ 本文档严格按真实开发情况填写，所有 commit 链接经过验证*

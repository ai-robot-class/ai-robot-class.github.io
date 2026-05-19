# 🔗 Git Submodule 完全指南（期末项目专用）

> 📌 这份文档专门为期末项目设计：**项目代码在独立仓库，作业仓库通过 submodule 引用**

## 🎯 为什么用 Submodule

| 没用 submodule（❌ 不推荐） | 用 submodule（✅ 推荐） |
|------|------|
| 复制粘贴项目代码到作业仓库 | 作业仓库只放一个"指针" |
| 项目仓库代码无法独立演进 | 项目仓库独立运营、协作、发布 |
| 多人合作时学生 A 改的代码学生 B 看不到 | 多人共享同一个项目仓库 |
| commit 历史会丢失 | 完整保留项目 Git 历史 |

## 🛠️ Submodule 完整命令速查

### 添加 submodule

```bash
# 在作业仓库的 final-project 目录下
cd ai-robot-homework-zhangsan/final-project

# 添加 submodule，会创建 project-repo 文件夹
git submodule add https://github.com/<org>/<project-repo>.git project-repo

# 这一步会自动：
# 1. 把 <project-repo> 克隆到 project-repo/ 文件夹
# 2. 在父仓库根目录创建 .gitmodules 文件
# 3. 把 project-repo 标记为 submodule

# 提交父仓库的变更
cd ..
git add .gitmodules final-project/project-repo
git commit -m "🔗 添加期末项目 submodule"
git push
```

### 克隆带 submodule 的仓库

```bash
# 方法 1：克隆时一次性拉所有 submodule（推荐）
git clone --recursive https://github.com/<student>/ai-robot-homework-xxx.git

# 方法 2：已经克隆过，单独拉 submodule
git clone https://github.com/<student>/ai-robot-homework-xxx.git
cd ai-robot-homework-xxx
git submodule update --init --recursive
```

### 更新 submodule

```bash
# 项目仓库有新提交，作业仓库要更新指针

# 方法 1：从父仓库批量更新
git submodule update --remote --recursive
git add final-project/project-repo
git commit -m "📌 更新项目 submodule 指针"
git push

# 方法 2：进入 submodule 手动更新
cd final-project/project-repo
git pull origin main
cd ../..
git add final-project/project-repo
git commit -m "📌 更新项目 submodule 到最新提交"
git push
```

### 在 submodule 内开发

```bash
# 进入 submodule 像普通仓库一样工作
cd final-project/project-repo

# 看当前分支（默认是 detached HEAD，要先 checkout）
git checkout main

# 写代码、提交、推送
vim src/xxx.py
git add . && git commit -m "实现 detect_color"
git push origin main

# 回到父仓库，提交指针更新
cd ../..
git add final-project/project-repo
git commit -m "📌 推进项目进度"
git push
```

### 删除 submodule

```bash
# 1. 反初始化
git submodule deinit -f final-project/project-repo

# 2. 从 git 中删除（保留文件）
git rm -f final-project/project-repo

# 3. 删除 .git/modules 下的缓存
rm -rf .git/modules/final-project/project-repo

# 4. 提交
git commit -m "🗑️ 移除旧 submodule"
```

## ⚠️ 常见坑

### 坑 1：忘记 `--recursive`

```bash
# 你看到 final-project/project-repo 是空文件夹
ls final-project/project-repo  # 啥都没有

# 修复：
git submodule update --init --recursive
```

### 坑 2：在 submodule 里 commit 后忘记推父仓库

```bash
# submodule 提交了，但作业仓库还指向旧 commit
cd final-project/project-repo && git log -1  # 显示新 commit
cd ../.. && git status                       # 显示 modified

# 修复：
git add final-project/project-repo
git commit -m "📌 推进 submodule"
git push
```

### 坑 3：组员看到的 submodule 是旧版本

```bash
# 组员拉了你的最新作业仓库，但 submodule 还是老版本
git pull              # 父仓库更新
# 但 submodule 没更新！

# 修复：
git submodule update --recursive
# 或：git pull --recurse-submodules
```

### 坑 4：submodule 的 detached HEAD

```bash
# 默认 submodule 处于 detached HEAD，不能 commit
cd final-project/project-repo
git branch  # 显示 (HEAD detached at xxx)

# 修复：
git checkout main  # 或你的开发分支
# 然后才能正常开发提交
```

### 坑 5：CI/CD 上 submodule 不拉

```yaml
# GitHub Actions 默认不拉 submodule，要显式启用：
- uses: actions/checkout@v4
  with:
    submodules: recursive  # ⭐ 关键
```

## 🎨 推荐工作流

### 单人项目

```
1. 在 GitHub 网页创建项目仓库 ai-robot-final-XXX-yourid
2. 在本地克隆，复制 project-templates/p0X-xxx/ 内容进去
3. 开发推进项目仓库
4. 在作业仓库 final-project/ 添加 submodule
5. 提交个人 README.md
```

### 多人项目（2-3 人）

```
组长操作：
1. 创建项目仓库 ai-robot-final-XXX-team1
2. 把组员加为 Collaborator（Settings → Collaborators → Add）
3. 在本地克隆，复制 project-templates/p0X-xxx/ 内容
4. 推送初始版本

每位组员操作：
1. 在自己作业仓库 final-project/ 添加 submodule（指向同一个项目仓库）
2. 各自 clone 项目仓库到工作环境
3. 在项目仓库中创建自己的分支：git checkout -b feat/my-task
4. 完成后发 PR 合并到 main
5. 在作业仓库的 final-project/README.md 中写自己的贡献
```

## 📋 评审脚本

教师批量评分时会用：

```bash
#!/bin/bash
# 批量评分所有学生
for student in alice bob charlie; do
    echo "===== Grading $student ====="

    # 克隆带 submodule 的作业仓库
    git clone --recursive https://github.com/$student/ai-robot-homework-$student.git /tmp/grade-$student

    cd /tmp/grade-$student

    # 找到 final-project/project-repo
    if [ -d "final-project/project-repo" ]; then
        # 跑评分（含 submodule 内的代码）
        python3 grading/run_grading.py final-project/project-repo \
            --student $student \
            --output /tmp/reports/$student.json \
            --markdown /tmp/reports/$student.md
    else
        echo "❌ $student 没有 final-project/project-repo"
    fi

    cd -
done
```

## 🔍 进阶：基于 commit 自动评估个人贡献

```bash
# 统计某学生在项目仓库的贡献占比
cd final-project/project-repo

# 该学生的 commit 数
MY_COMMITS=$(git log --author="$GITHUB_ID" --oneline | wc -l)
# 总 commit 数
TOTAL_COMMITS=$(git log --oneline | wc -l)

# 该学生改的代码行数
MY_INSERTIONS=$(git log --author="$GITHUB_ID" --pretty=tformat: --numstat | awk '{add+=$1} END {print add}')

echo "提交数: $MY_COMMITS/$TOTAL_COMMITS"
echo "新增代码行: $MY_INSERTIONS"
```

---

*🔗 Git Submodule = 工业界标准做法，掌握了就是简历加分项*

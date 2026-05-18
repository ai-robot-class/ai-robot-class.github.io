# 🔒 隐私保护说明

## 设计理念

本系统遵循**最小化数据收集**原则，保护学生隐私。

## 数据处理

### ✅ 仅存储的信息

```json
[
  "https://github.com/username1/ai-robot-homework",
  "https://github.com/username2/robotics-course"
]
```

- **仅存储**：GitHub仓库URL
- **自动提取**：从URL中解析GitHub ID
- **公开展示**：GitHub ID和头像（GitHub公开信息）

### ❌ 不存储的敏感信息

- 学生真实姓名
- 学号
- 联系方式
- 任何个人身份信息

## 展示页面

### 显示内容

- ✅ GitHub用户名（@username）
- ✅ GitHub头像（来自GitHub API）
- ✅ 作业完成进度
- ✅ 得分统计
- ✅ 仓库链接

### 不显示内容

- ❌ 真实姓名
- ❌ 学号
- ❌ 班级信息
- ❌ 任何可追溯到个人的信息

## 示例对比

### ❌ 旧版本（包含敏感信息）
```json
{
  "student_id": "202401001",
  "name": "张三",
  "github_id": "zhangsan",
  "repo_url": "https://github.com/zhangsan/ai-robot-homework"
}
```

### ✅ 新版本（隐私保护）
```json
"https://github.com/zhangsan/ai-robot-homework"
```

**优势**：
- 🔒 不泄露学生真实身份
- 🎯 GitHub ID已经在URL中
- 📦 数据结构更简洁
- 🚀 处理更高效

## 数据安全

1. **GitHub Pages访问控制**
   - 可设置为私有仓库（需GitHub Pro）
   - 或使用GitHub Secrets保护敏感配置

2. **评价数据隔离**
   - 评价结果仅包含GitHub ID
   - 不与学籍系统直接关联

3. **教师端管理**
   - 教师本地维护学生GitHub ID与学号的映射
   - 映射表不上传到GitHub

## 推荐实践

### 教师端

创建本地映射表（不提交到GitHub）：

```csv
# mapping.csv（仅本地保存）
github_id,student_id,name
zhangsan,202401001,张三
lisi,202401002,李四
```

添加到 `.gitignore`：
```
mapping.csv
students/private/
```

### 学生端

- 使用GitHub账号完成作业
- GitHub用户名可以是匿名的（如: `student001`）
- 不在仓库中包含学号、姓名等敏感信息

## 合规性

✅ 符合GDPR和数据保护法规要求
✅ 最小化数据收集原则
✅ 学生可自主控制GitHub仓库可见性
✅ 教师无需处理敏感个人信息

---

*隐私保护 · 让教学更安全！*

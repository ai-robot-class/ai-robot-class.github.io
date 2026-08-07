# 🧠 强化学习 (Reinforcement Learning)

> 授课：**Frank Zhao (Ruinan Zhao)** · 汉阳大学电气工程博士候选人
> 硕士研究方向：面向机械臂开门任务的强化学习

欢迎来到**强化学习**课程！本课程带你从**数学基础**一步步走到能够训练智能体（Agent）
自己学会决策的**现代强化学习算法**。我们坚持**理论 + 代码并重**，每个概念都配可运行的
Python 示例。

---

## 🎯 课程目标

本课程**自始至终只用一个例子——《王者荣耀》**，从数学一路讲到能打 MOBA 的 AI。学完你将能够：

- 用 **NumPy** 熟练进行向量、矩阵运算，理解"局势=向量、决策=矩阵乘法"的线性代数语言；
- 用**马尔可夫决策过程 (MDP)** 把"打王者"这件事写成数学模型；
- 讲清楚强化学习核心概念：状态、动作、奖励、策略、价值函数、贝尔曼方程——**全部对应到游戏变量**；
- **亲手写一个王者子任务环境**（「鲁班瞄准」），并把大任务拆成可训练的小任务；
- 亲手实现并对比 **Q-Learning、Sarsa、DQN、REINFORCE、Actor-Critic、PPO**，在王者子任务上训练它们；
- 在腾讯开悟的**完整《王者荣耀》1v1** 离线仿真里，跑通并理解工业级 RL。

## 🧩 先修要求

- 会一点 **Python**（变量、循环、函数、类即可，不会也能边学边补）；
- 高中/大一水平的数学（我们会在第一部分补齐线性代数）；
- 一台能装 Python 的电脑（Windows / macOS / Linux 均可）。

## 🛠️ 环境准备

**从[第一课](part0-setup.md)开始**——它会带你建立“概念↔王者荣耀变量”的对照，并**亲手跑通开悟离线仿真的第一局**。

**第二~六课（理论 + 王者子任务）**——本机装个 Python 虚拟环境即可，我们会**自己写「鲁班瞄准」子任务环境**：

```bash
# 推荐使用虚拟环境
python -m venv rl-env
# Windows: rl-env\Scripts\activate
source rl-env/bin/activate

# 安装依赖（纯 CPU 即可）；gymnasium/stable-baselines3 仅用于给鲁班子任务套标准接口
pip install numpy matplotlib torch gymnasium stable-baselines3
```

**开悟《王者荣耀》实战**——用 Docker 一键复现，纯 CPU 起步：

```bash
cd courses/rl/kaiwu_env
docker compose build
KAIWU_GAMECORE=/path/to/hok_env_gamecore/gamecore docker compose up
```

> 详见 [`kaiwu_env/README.md`](kaiwu_env/README.md)（含 WSL2、license 申请、Wine 运行、冒烟测试）。

---

## 🗺️ 课程地图（授课节奏）

本课程以**王者荣耀**为贯穿案例，循序渐进：**每讲一个数学概念，都回到游戏里的具体变量**。

| 课次 | 主题 | 你会学到 | 王者荣耀里对应什么 |
|------|------|---------|------------------|
| **第一课** | [强化学习入门 + 环境搭建](part0-setup.md) | 什么是 RL、概念↔游戏变量词典、跑通第一局 | 建立全课的“词典表” |
| **第二课** | [Python 与线性代数基础](part1-linear-algebra.md) | 向量/矩阵、点积、矩阵乘法、范数 | 局势=向量，决策=矩阵乘法 |
| **第三课** | [马尔可夫决策过程 (MDP)](part2-mdp.md) | 马尔可夫性、转移、奖励、折扣、贝尔曼 | 把 1v1 写成 MDP 五元组 |
| **第四课** | [强化学习基础概念](part3-rl-basics.md) | 交互循环、探索/利用、MC/TD、GPI | 越塔/试连招=探索，逐帧更新=TD |
| **第五课** | [环境与接口](part4-environments.md) | 环境接口、动作/观测空间、亲手写环境 | 写出「鲁班瞄准」子任务，接口与开悟同构 |
| **第六课** | [各式各样的强化学习算法](part5-algorithms.md) | Q-Learning、Sarsa、DQN、PG、PPO | 为何用 PPO+多动作头打 MOBA |
| **第七课** | [开悟《王者荣耀》MOBA 实战](part6-kaiwu-moba.md) | 用 PPO + 自对弈打 1v1；纯 CPU、Docker 复现 | 把前六课全部用起来 |

```
第一课        第二课       第三课        第四课        第五课        第六课        第七课
入门+环境 ─► 线性代数 ─► MDP 建模 ─► RL 核心概念 ─► 环境与实验 ─► RL 算法家族 ─► 开悟 MOBA 实战
(游戏词典)    (数学语言)   (问题建模)    (思想框架)     (动手平台)     (求解方法)     (真实大环境)
```

---

## 🎮 旗舰实战：用「开悟」在真实 MOBA 里学强化学习

本课程的落脚点是一个让人兴奋的真实环境——腾讯 [**开悟（Kaiwu）**](https://aiarena.tencent.com/)
开放的《王者荣耀》**离线本地仿真**。它把前五部分的抽象概念（状态、动作、奖励、策略、价值、PPO）
一次性落到一个亿级玩家验证过的 MOBA 游戏上：

- **无需真机、不连线上服务器、无封号风险**：gamecore 在本地跑完整游戏逻辑，合规用于教学/科研；
- **标准 RL 接口**：环境给出 `observation / legal_action / reward / done`，和你在第四部分学的 Gym 接口同构；
- **纯 CPU 起步**：游戏逻辑本身跑在 CPU，先用 CPU 跑通环境与小规模训练，再按需上 GPU；
- **Docker 一键复现**：环境封装在 [`kaiwu_env/`](kaiwu_env/README.md)，`docker compose up` 即可。

> 教学定位：**跑通环境 → 读懂 baseline → 改奖励/超参做实验 → 小规模自对弈**。
> 我们不追求从零训出顶尖 AI，而是让你在真实复杂环境里**把 RL 概念用起来、看得见**。

---

## 📗 参考教材与参考代码

本课程的推荐**参考教材**与**参考代码**为肖智清《强化学习：原理与 Python 实战》系列，
其配套开源仓库每章都提供 **TensorFlow 2 与 PyTorch 一一对照**的高质量实现，
覆盖从经典到深度强化学习的主流算法，且**无需 GPU、笔记本即可运行**——与本课程理念高度契合。

- 📦 **代码仓库**：[ZhiqingXiao/rl-book](https://github.com/zhiqingxiao/rl-book)
  （在线代码与运行结果：<https://zhiqingxiao.github.io/rl-book/>）
- 📘 **英文版 (2024)**：[en2024](https://github.com/ZhiqingXiao/rl-book/tree/master/en2024) ·
  📕 **中文版 (2023)**：[zh2023](https://github.com/ZhiqingXiao/rl-book/tree/master/zh2023) ·
  中文旧版 (2019)：[zh2019](https://github.com/ZhiqingXiao/rl-book/tree/master/zh2019)

**本课程各部分 ↔ 参考书主题对照**（便于延伸阅读，本课程一律用「鲁班瞄准」与开悟 1v1 做实例）：

| 本课程 | 参考书对应主题 |
|--------|----------------|
| 第一部分 · 线性代数基础 | NumPy 与环境接口入门 |
| 第二部分 · MDP | 贝尔曼方程、动态规划 |
| 第三部分 · RL 基础概念 | 蒙特卡洛、时序差分、Sarsa / Q-Learning |
| 第四部分 · 环境与接口 | 环境接口与自定义环境 |
| 第五部分 · RL 算法 | DQN 系列、策略梯度、Actor-Critic、PPO、DDPG/SAC 等 |

> 💡 建议：先读本课程各部分、在王者子任务上动手；再到参考仓库对照同主题的 `.ipynb` 代码
> （TensorFlow 与 PyTorch 任选其一）加深理解。

---

## 📖 如何学习本课程

1. **按顺序**上完七课，前面是后面的基础；
2. 始终带着[第一课](part0-setup.md)的“概念↔游戏变量”词典——看到公式就想想它在王者里是什么；
3. 每读到代码块，**亲手敲一遍并运行**，改改参数看结果；
4. 每课末尾有**练习**（含王者场景题），动手做完再进入下一课；
5. 遇到数学公式不必死记，先理解**直觉**，再回头看推导。

> 💡 强化学习最迷人的地方在于：你不告诉智能体“怎么做”，只告诉它“做得好不好”，
> 它就能自己摸索出策略。让我们开始吧！

👉 从 [第一课：强化学习入门 + 环境搭建](part0-setup.md) 开始，先跑通开悟的第一局，
最终在 [第七课：开悟《王者荣耀》MOBA 实战](part6-kaiwu-moba.md) 把所学用到真实游戏 AI 上。

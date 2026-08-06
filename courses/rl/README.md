# 🧠 强化学习 (Reinforcement Learning)

> 授课：**Frank Zhao (Ruinan Zhao)** · 汉阳大学电气工程博士候选人
> 硕士研究方向：面向机械臂开门任务的强化学习

欢迎来到**强化学习**课程！本课程带你从**数学基础**一步步走到能够训练智能体（Agent）
自己学会决策的**现代强化学习算法**。我们坚持**理论 + 代码并重**，每个概念都配可运行的
Python 示例。

---

## 🎯 课程目标

学完本课程，你将能够：

- 用 **NumPy** 熟练进行向量、矩阵运算，理解强化学习背后的线性代数语言；
- 用**马尔可夫决策过程 (MDP)** 对一个决策问题进行数学建模；
- 讲清楚强化学习的核心概念：状态、动作、奖励、策略、价值函数、贝尔曼方程；
- 使用 **Gymnasium** 搭建/调用强化学习环境；
- 亲手实现并对比 **Q-Learning、Sarsa、DQN、REINFORCE、Actor-Critic、PPO** 等算法。

## 🧩 先修要求

- 会一点 **Python**（变量、循环、函数、类即可，不会也能边学边补）；
- 高中/大一水平的数学（我们会在第一部分补齐线性代数）；
- 一台能装 Python 的电脑（Windows / macOS / Linux 均可）。

## 🛠️ 环境准备

```bash
# 推荐使用虚拟环境
python -m venv rl-env
# Windows: rl-env\Scripts\activate
source rl-env/bin/activate

# 安装依赖
pip install numpy matplotlib gymnasium torch
```

---

## 🗺️ 课程地图（五个部分）

本课程分为**五个循序渐进**的部分：

| 部分 | 主题 | 你会学到 |
|------|------|---------|
| **第一部分** | [Python 与线性代数基础](part1-linear-algebra.md) | 向量/矩阵、点积、矩阵乘法、范数、特征值，用 NumPy 实现 |
| **第二部分** | [马尔可夫决策过程 (MDP)](part2-mdp.md) | 马尔可夫性、状态转移、奖励、折扣、贝尔曼方程 |
| **第三部分** | [强化学习基础概念](part3-rl-basics.md) | Agent-环境交互、策略、价值函数、探索与利用、GPI |
| **第四部分** | [应用环境示例](part4-environments.md) | Gymnasium、经典控制/网格世界、自定义环境 |
| **第五部分** | [各式各样的强化学习算法](part5-algorithms.md) | Q-Learning、Sarsa、DQN、策略梯度、Actor-Critic、PPO |

```
第一部分            第二部分           第三部分            第四部分            第五部分
线性代数    ──►    MDP 建模   ──►   RL 核心概念   ──►    环境与实验   ──►   RL 算法家族
(数学语言)         (问题建模)        (思想框架)          (动手平台)          (求解方法)
```

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

**本课程各部分 ↔ 参考章节/代码对照**（便于延伸阅读与查代码）：

| 本课程 | 参考书章节与配套代码（环境 / 算法） |
|--------|-------------------------------------|
| 第一部分 · 线性代数基础 | 第 1 章：Gym 入门与环境使用 |
| 第二部分 · MDP | 第 2 章 `CliffWalking`（Bellman）、第 3 章 `FrozenLake`（动态规划 DP） |
| 第三部分 · RL 基础概念 | 第 4 章 `Blackjack`（蒙特卡洛 MC）、第 5 章 `Taxi`（Sarsa / 期望 Sarsa / Q-Learning / Double QL） |
| 第四部分 · 应用环境 | 全书 Gym 环境实例；第 1 章环境安装与自定义扩展 |
| 第五部分 · RL 算法 | 第 6 章 `MountainCar`（DQN / Double / Dueling）、第 7 章 `CartPole`（VPG 策略梯度）、第 8 章 `Acrobot`（Actor-Critic / PPO / TRPO / NPG）、第 9 章 `Pendulum`（DDPG / TD3）、第 10 章 `LunarLander`（SAC）、第 12 章 `Pong`（分布式 DQN）、第 14 章 `TicTacToe`（AlphaZero） |

> 💡 建议：先读本课程各部分建立直觉，再到参考仓库对照运行同主题的 `.ipynb` 代码
> （TensorFlow 与 PyTorch 任选其一）加深理解。

---

## 📖 如何学习本课程

1. **按顺序**阅读五个部分，前面是后面的基础；
2. 每读到代码块，**亲手敲一遍并运行**，改改参数看结果；
3. 每部分末尾有**练习**，动手做完再进入下一部分；
4. 遇到数学公式不必死记，先理解**直觉**，再回头看推导。

> 💡 强化学习最迷人的地方在于：你不告诉智能体“怎么做”，只告诉它“做得好不好”，
> 它就能自己摸索出策略。让我们开始吧！

👉 从 [第一部分：Python 与线性代数基础](part1-linear-algebra.md) 开始。

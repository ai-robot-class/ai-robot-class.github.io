# 第五部分 · 各式各样的强化学习算法

> 目标：把前四部分的知识汇聚起来，**动手实现并理解**主流强化学习算法：
> Q-Learning、Sarsa、DQN、REINFORCE、Actor-Critic、PPO。

这是本课程的“高潮”。我们按**从简单到复杂**、**从表格到神经网络**的顺序展开。

---

## 5.1 算法家族地图

```
                         强化学习算法
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   基于价值 (Value)      基于策略 (Policy)      演员-评论家 (Actor-Critic)
        │                     │                     │
   Q-Learning            REINFORCE               A2C / A3C
   Sarsa                 (策略梯度)               PPO
   DQN 系列                                       DDPG / SAC(连续)
```

| 类别 | 学什么 | 适合 | 代表 |
|------|--------|------|------|
| 基于价值 | 学 `Q(s,a)`，再贪心选动作 | 离散动作 | Q-Learning、DQN |
| 基于策略 | 直接学策略 `π(a|s)` | 离散/连续 | REINFORCE |
| 演员-评论家 | 同时学策略 + 价值 | 通用、主流 | A2C、PPO |

---

## 5.2 Q-Learning（表格型，异策略）

**核心更新公式**（基于第三部分的 TD 思想）：

```
Q(s,a) ← Q(s,a) + α [ r + γ·max_{a'} Q(s',a') − Q(s,a) ]
                         └──────── TD 目标 ────────┘
```

注意目标里用的是 `max`（下一步的最优动作），而不是实际执行的动作——所以 Q-Learning 是**异策略**的。

用第四部分的 `GridWorld` 训练：

```python
import numpy as np
from gridworld import GridWorld   # 用第四部分写的环境

env = GridWorld(size=4)
n_states, n_actions = env.size * env.size, 4
Q = np.zeros((n_states, n_actions))

alpha, gamma = 0.1, 0.95
epsilon = 1.0

for episode in range(2000):
    s = env.reset()
    done = False
    while not done:
        # ε-贪心选动作
        if np.random.rand() < epsilon:
            a = np.random.randint(n_actions)
        else:
            a = int(np.argmax(Q[s]))

        s_next, r, done, _ = env.step(a)
        # Q-Learning 更新
        Q[s, a] += alpha * (r + gamma * np.max(Q[s_next]) - Q[s, a])
        s = s_next

    epsilon = max(0.05, epsilon * 0.999)   # 探索率衰减

# 输出每个状态学到的最优动作
policy = np.argmax(Q, axis=1)
print("学到的策略(每格最优动作):")
print(policy.reshape(env.size, env.size))
```

训练后，智能体会学到从起点走向终点的**最短路径**。

---

## 5.3 Sarsa（表格型，同策略）

Sarsa 与 Q-Learning 几乎一样，唯一区别在 TD 目标用**实际执行的下一个动作** `a'`，
而不是 `max`。名字来自更新用到的五元组 `(S, A, R, S', A')`。

```
Q(s,a) ← Q(s,a) + α [ r + γ·Q(s',a') − Q(s,a) ]
```

```python
s = env.reset()
a = epsilon_greedy(Q[s], epsilon)
done = False
while not done:
    s_next, r, done, _ = env.step(a)
    a_next = epsilon_greedy(Q[s_next], epsilon)   # 先按策略选出 a'
    Q[s, a] += alpha * (r + gamma * Q[s_next, a_next] - Q[s, a])
    s, a = s_next, a_next
```

> **Q-Learning vs Sarsa**：Q-Learning 学“最优”策略但更激进（异策略）；
> Sarsa 学“当前实际执行”的策略，更**保守/安全**（同策略）。经典的“悬崖行走”实验中，
> Sarsa 会绕开悬崖，Q-Learning 会贴着悬崖走。

---

## 5.4 DQN（深度 Q 网络）

当状态太多（如图像）无法用表格时，用**神经网络**近似 `Q(s,a; θ)`。这就是 **DQN**（2015, DeepMind）。

**两大关键技巧**：

1. **经验回放 (Replay Buffer)**：把交互经验存起来随机采样，打破数据相关性；
2. **目标网络 (Target Network)**：用一个更新较慢的网络算 TD 目标，稳定训练。

**损失函数**：

```
L(θ) = ( r + γ·max_{a'} Q(s',a'; θ⁻) − Q(s,a; θ) )²
                                  └ θ⁻: 目标网络参数
```

PyTorch 核心骨架（简化版）：

```python
import torch, torch.nn as nn, random
from collections import deque

class QNet(nn.Module):
    def __init__(self, n_obs, n_act):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_obs, 128), nn.ReLU(),
            nn.Linear(128, n_act)
        )
    def forward(self, x):
        return self.net(x)

q_net, target_net = QNet(4, 2), QNet(4, 2)
target_net.load_state_dict(q_net.state_dict())
optim = torch.optim.Adam(q_net.parameters(), lr=1e-3)
buffer = deque(maxlen=10000)
gamma = 0.99

def train_step(batch_size=64):
    if len(buffer) < batch_size:
        return
    batch = random.sample(buffer, batch_size)
    s, a, r, s2, done = map(lambda x: torch.tensor(x, dtype=torch.float32), zip(*batch))
    q = q_net(s).gather(1, a.long().unsqueeze(1)).squeeze(1)
    with torch.no_grad():
        target = r + gamma * target_net(s2).max(1).values * (1 - done)
    loss = nn.functional.mse_loss(q, target)
    optim.zero_grad(); loss.backward(); optim.step()
```

主循环里：ε-贪心采样 → 存入 buffer → `train_step()` → 定期把 `q_net` 权重同步给 `target_net`。
用它可以让 CartPole 稳稳坚持满 500 步。

---

## 5.5 策略梯度：REINFORCE

不学价值，**直接优化策略** `π(a|s; θ)`。思想：让**带来高回报**的动作，出现概率变大。

**目标与梯度**：

```
maximize  J(θ) = E[ G_t ]
梯度:      ∇J(θ) = E[ G_t · ∇ log π(a_t | s_t; θ) ]
```

直觉：`G_t` 大 → 沿着“提高该动作概率”的方向多走一步。

```python
import torch, torch.nn as nn

class PolicyNet(nn.Module):
    def __init__(self, n_obs, n_act):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(n_obs, 128), nn.ReLU(),
                                 nn.Linear(128, n_act))
    def forward(self, x):
        return torch.softmax(self.net(x), dim=-1)   # 输出动作概率

# 一局结束后，用整局的回报更新
def update(policy, optim, log_probs, rewards, gamma=0.99):
    G, returns = 0, []
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)
    returns = torch.tensor(returns)
    returns = (returns - returns.mean()) / (returns.std() + 1e-8)  # 标准化，降方差
    loss = -(torch.stack(log_probs) * returns).sum()
    optim.zero_grad(); loss.backward(); optim.step()
```

> REINFORCE 简单直观，但**方差大、要跑完整局**才能更新——于是有了 Actor-Critic。

---

## 5.6 演员-评论家 (Actor-Critic)

把“基于策略”和“基于价值”**结合**起来：

- **Actor（演员）**：策略网络 `π(a|s)`，负责**做动作**；
- **Critic（评论家）**：价值网络 `V(s)`，负责**打分**，指导 Actor。

用 **优势 (Advantage)** `A = r + γV(s') − V(s)` 代替 REINFORCE 里的 `G_t`，
既能**每步更新**（TD），又能**大幅降低方差**：

```
Actor 损失  = − log π(a|s) · A
Critic 损失 = ( r + γV(s') − V(s) )²
```

这就是 **A2C (Advantage Actor-Critic)** 的核心。它是当今大多数先进算法的基础骨架。

---

## 5.7 PPO（近端策略优化）

**PPO (Proximal Policy Optimization)** 是目前工业界与研究界**最常用**的算法之一
（ChatGPT 的 RLHF 也用它）。它在 Actor-Critic 基础上，解决“更新步子太大导致训练崩溃”的问题。

核心是**裁剪 (clip)** 目标函数，限制新旧策略的比值 `r_t(θ) = π_new/π_old` 不要偏离太多：

```
L_CLIP(θ) = E[ min( r_t·A_t ,  clip(r_t, 1−ε, 1+ε)·A_t ) ]
```

- 当优势为正时，鼓励提高该动作概率，但**最多提高到 1+ε 倍**；
- 当优势为负时，降低概率，但**最多降到 1−ε 倍**；
- 从而实现**稳定、样本高效**的更新。

> 实践建议：初学时**不必从零实现 PPO**，可用成熟库 `stable-baselines3`：
>
> ```python
> from stable_baselines3 import PPO
> import gymnasium as gym
> model = PPO("MlpPolicy", gym.make("CartPole-v1"), verbose=1)
> model.learn(total_timesteps=50_000)
> ```

---

## 5.8 算法对比与选型

| 算法 | 类别 | 动作空间 | 同/异策略 | 需要神经网络 | 特点 |
|------|------|----------|-----------|--------------|------|
| Q-Learning | 价值 | 离散 | 异策略 | 否（表格） | 简单、经典 |
| Sarsa | 价值 | 离散 | 同策略 | 否（表格） | 更保守/安全 |
| DQN | 价值 | 离散 | 异策略 | 是 | 处理高维状态 |
| REINFORCE | 策略 | 离散/连续 | 同策略 | 是 | 简单但方差大 |
| A2C | 演员-评论家 | 离散/连续 | 同策略 | 是 | 降方差、可并行 |
| **PPO** | 演员-评论家 | 离散/连续 | 同策略 | 是 | **稳定、通用、首选** |

**选型建议**：

- 状态少、离散 → **Q-Learning / Sarsa**（表格）；
- 状态高维、离散动作 → **DQN**；
- 连续动作 / 追求稳定通用 → **PPO**（或 SAC、DDPG）。

---

## 5.9 训练调参小贴士

- **学习率 α**：最关键的超参，先从 `1e-3` 试起；
- **折扣 γ**：常用 `0.95 ~ 0.99`；
- **探索**：ε-贪心要**衰减**；策略方法可加**熵奖励**鼓励探索；
- **回报标准化 / 优势标准化**：显著稳定训练；
- **随机种子**：RL 方差大，多跑几个种子看平均，别被单次结果骗了。

---

## ✅ 小结

- **表格法**（Q-Learning / Sarsa）是理解 RL 的最佳起点；
- 状态复杂时用**神经网络**近似 → DQN（回放 + 目标网络）；
- **策略梯度**直接优化策略；**Actor-Critic** 用优势降方差；
- **PPO** 是稳定、通用、最常用的现代算法；
- 选算法先看**动作空间**和**状态维度**。

## 📝 练习

1. 用 Q-Learning 训练 `FrozenLake-v1`(`is_slippery=False`)，打印学到的策略网格。
2. 在“悬崖行走”场景中对比 Q-Learning 与 Sarsa 的路径差异，解释原因。
3. 用 PyTorch 补全 5.4 的 DQN 主循环，让 `CartPole-v1` 平均回报 > 400。
4. 用 `stable-baselines3` 的 PPO 训练 `LunarLander-v2`，记录学习曲线。
5. 综合题：为你自己第四部分的 `GridWorld`（加了陷阱的版本）选择并实现一个合适算法。

---

## 🎓 课程结语

从**线性代数**到 **PPO**，你已经走完了强化学习的完整入门路径：
数学语言 → MDP 建模 → 核心概念 → 交互环境 → 算法实现。

> 强化学习的魅力在于：我们不教智能体“怎么做”，只告诉它“做得好不好”，
> 它便能在试错中，自己长出智慧。愿你带着这套思维，去解决真正有趣的问题。🚀

⬅️ 上一部分：[第四部分 · 应用环境示例](part4-environments.md)
🏠 返回：[强化学习课程首页](README.md) · [Frank Zhao 主页](/README.md)

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

用[第四部分](part4-environments.md)写的「鲁班瞄准」训练。表格法需要**离散状态**，
我们把"目标所在方向"离散成 16 个扇区，先让目标**站桩**（`target_speed=0`）以便用表格学：

```python
import numpy as np
from luban_aim import LubanAimEnv   # 第四部分写的鲁班瞄准环境

def discretize(obs):
    """把连续观测压成离散状态：目标当前所在的方向扇区(0..15)"""
    ang = np.arctan2(obs[1], obs[0]) % (2 * np.pi)
    return int(ang / (2 * np.pi) * 16) % 16

env = LubanAimEnv(target_speed=0.0, seed=0)   # 站桩目标，适合表格法
n_states, n_actions = 16, 16
Q = np.zeros((n_states, n_actions))
alpha, gamma, epsilon = 0.1, 0.9, 1.0

for episode in range(5000):
    s = discretize(env.reset())
    done = False
    while not done:
        # ε-贪心选发射方向
        if np.random.rand() < epsilon:
            a = np.random.randint(n_actions)
        else:
            a = int(np.argmax(Q[s]))

        obs, r, done, info = env.step(a)
        s_next = discretize(obs)
        # Q-Learning 更新
        Q[s, a] += alpha * (r + gamma * np.max(Q[s_next]) - Q[s, a])
        s = s_next

    epsilon = max(0.05, epsilon * 0.999)      # 探索率衰减

# 学到的瞄准策略：每个方向扇区应朝哪个方向发射
print("学到的瞄准策略:", np.argmax(Q, axis=1))
# [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15]  ——完美的"目标在哪打哪"
```

训练后，鲁班学到了**"目标在哪个方向就朝哪个方向开炮"**的完美映射（策略正好是 `0..15`）：
每回合 20 步能命中 20 个目标、回报 +20，而随机策略每回合才蒙中 1 次左右（回报约 -0.5）。

> 🎮 **为什么完整的王者 1v1 不能用这张表？** 表格 `Q` 要为"每个状态 × 每个动作"存一个数。
> 鲁班瞄准我们把状态硬压成 16 个扇区才能用表格；可完整 1v1 的状态是 **491 维连续量**（血量、坐标、CD…），
> 组合数是天文数字——表格根本存不下，也永远采样不全。**这正是必须换成神经网络（DQN/PPO）的原因**：
> 用一个函数去"压缩"这张无穷大的表。

---

## 5.3 Sarsa（表格型，同策略）

Sarsa 与 Q-Learning 几乎一样，唯一区别在 TD 目标用**实际执行的下一个动作** `a'`，
而不是 `max`。名字来自更新用到的五元组 `(S, A, R, S', A')`。

```
Q(s,a) ← Q(s,a) + α [ r + γ·Q(s',a') − Q(s,a) ]
```

```python
s = discretize(env.reset())
a = epsilon_greedy(Q[s], epsilon)
done = False
while not done:
    obs, r, done, info = env.step(a)
    s_next = discretize(obs)
    a_next = epsilon_greedy(Q[s_next], epsilon)   # 先按策略选出 a'
    Q[s, a] += alpha * (r + gamma * Q[s_next, a_next] - Q[s, a])
    s, a = s_next, a_next
```

> **Q-Learning vs Sarsa**：Q-Learning 学"最优"策略但更激进（异策略）；
> Sarsa 学"当前实际执行"的策略，更**保守/安全**（同策略）。
> 🎮 放到王者里体会：学**越塔强杀**时，Q-Learning 倾向按"理想情况下能成功"去激进走位，
> Sarsa 则会把"我这个 ε 探索有时会乱走、可能被塔打死"也算进去，从而更**保守、留安全余量**。

---

## 5.4 DQN（深度 Q 网络）

表格法要求把状态离散化。可一旦目标会**移动**、还得算**提前量**，只用"方向扇区"就不够了——
我们想直接把 5 维连续观测（含速度 `vx, vz`）喂进去。这时用**神经网络**近似 `Q(s,a; θ)`，就是 **DQN**（2015, DeepMind）。

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

q_net, target_net = QNet(5, 16), QNet(5, 16)   # 鲁班瞄准：5 维观测 → 16 个发射方向
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
在**会移动的鲁班瞄准任务**上，训练后每回合命中数会从随机的约 1 次大幅提升：
网络直接吃进连续观测（含速度 `vx, vz`），学会从目标速度**预判提前量**，朝"目标将要到的位置"开炮。

> 🎮 **DQN 从子任务到完整王者的难点**：DQN 天生适合"**一个**离散动作头"（如鲁班的 16 个发射方向）。
> 但完整 1v1 的动作是**复合的**——同一帧要同时决定"移动方向 + 用哪个技能 + 打谁"。
> 硬把所有组合列成一个巨大的离散动作空间会爆炸。所以工业级 MOBA 更常用 **PPO + 多动作头**（见 5.x）。

---

## 5.5 策略梯度：REINFORCE

不学价值，**直接优化策略** `π(a|s; θ)`。思想：让**带来高回报**的动作，出现概率变大。
（放到鲁班瞄准里：命中那一发对应的"发射方向"概率被调高，乱打的方向被调低。）

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

> 实践建议：初学时**不必从零实现 PPO**，可用成熟库 `stable-baselines3`。
> 只要把我们的「鲁班瞄准」套一层标准 `gymnasium.Env` 接口，就能直接用 SB3 的 PPO 训练：
>
> ```python
> import gymnasium as gym, numpy as np
> from gymnasium import spaces
> from stable_baselines3 import PPO
> from luban_aim import LubanAimEnv
>
> class LubanGym(gym.Env):
>     """把第四部分的鲁班瞄准包装成标准 Gym 接口，供 SB3 使用"""
>     def __init__(self):
>         self.env = LubanAimEnv(target_speed=0.05)
>         self.action_space = spaces.Discrete(16)
>         self.observation_space = spaces.Box(-2, 2, shape=(5,), dtype=np.float32)
>     def reset(self, seed=None, options=None):
>         return self.env.reset(), {}
>     def step(self, action):
>         obs, r, done, info = self.env.step(int(action))
>         return obs, r, done, False, info      # terminated, truncated
>
> model = PPO("MlpPolicy", LubanGym(), verbose=1)
> model.learn(total_timesteps=100_000)          # 纯 CPU 几分钟，鲁班学会瞄准
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

**选型建议**（用王者子任务对照）：

- 状态少、离散 → **Q-Learning / Sarsa**（表格）：如把鲁班瞄准的目标方向离散成扇区；
- 状态高维、离散动作 → **DQN**：如鲁班瞄准的连续观测（含速度、要算提前量）；
- 复合动作 / 大动作空间 / 追求稳定通用 → **PPO**：如完整 1v1 的"按钮+方向+目标"复合动作。

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

1. 用 Q-Learning 训练站桩版「鲁班瞄准」（`target_speed=0`），打印 `np.argmax(Q,axis=1)`，验证它是否≈"朝目标扇区开炮"。
2. 把目标改成会移动（`target_speed=0.05`），观察表格版 Q-Learning 命中率为何下降，解释原因（提示：只用方向扇区丢了速度信息）。
3. 用 PyTorch 补全 5.4 的 DQN 主循环，在会移动的「鲁班瞄准」上把命中率训到 90%+。
4. 用 `stable-baselines3` 的 PPO（5.7 的 `LubanGym`）训练鲁班瞄准，记录命中率随训练步数的曲线。
5. 对比题：在「鲁班瞄准」上分别跑 Q-Learning（表格）与 DQN，说说各自的适用边界。
6. **完整王者题**：解释为什么完整 1v1 选 **PPO + 多动作头** 而不是 DQN；再说说去掉 `legal_action` 掩码后，训练初期会出现什么问题（可参考[第七课](part6-kaiwu-moba.md)论文 H.2 的消融结论）。

---

## 5.x 迈向真实环境：PPO + 自对弈打 MOBA

上面这些算法在玩具环境里已经够用。但当**动作是复合的、状态是高维的、还有对手**时
（正是《王者荣耀》1v1 的情形），最合适的就是 **PPO**——它稳定、能处理复杂动作分布，
配合**自对弈(self-play)** 让智能体和"过去的自己"对打、螺旋上升。

第六部分我们就用 **PPO 思路 + 开悟离线仿真**，把这些算法用到真实 MOBA 上。

### 复合动作 = 多个动作头（对应第一课说的“动作是向量”）

王者一帧的动作不是一个数，而是好几个决定同时做。策略网络因此长出**多个头**，
每个头输出一个子动作的分布，并各自用 `legal_action` 掩码屏蔽非法选择：

```python
import torch, torch.nn as nn

class KingPolicy(nn.Module):
    """把几百维局势向量 → 多个子动作头的打分（对应第一部分的 y = W·s + b）"""
    def __init__(self, n_obs, dims=(8, 4, 8)):   # (移动方向, 用哪个技能, 打谁)
        super().__init__()
        self.body  = nn.Sequential(nn.Linear(n_obs, 256), nn.ReLU())
        self.heads = nn.ModuleList([nn.Linear(256, d) for d in dims])

    def forward(self, s, legal_masks):
        h = self.body(s)
        dists = []
        for head, mask in zip(self.heads, legal_masks):
            logits = head(h)
            logits = logits.masked_fill(mask == 0, -1e9)   # 非法动作打分压到极小
            dists.append(torch.distributions.Categorical(logits=logits))
        return dists   # 每个子动作各采一个，合成这一帧的复合动作
```

- **PPO** 分别对每个头用 5.7 的裁剪目标更新，各头的 `log π` 相加即整个复合动作的对数概率；
- 用多进程在 gamecore 里并行采样（**纯 CPU 也能跑通**），再做 PPO 更新。

### 自对弈 (self-play)：和“过去的自己”对打

王者 1v1 有对手，环境不再固定。做法：**让 AI 的对面坐着它自己（或历史版本）**——
自己越强，对手也越强，形成螺旋上升。这正是 AlphaGo/OpenAI Five 的思路。

> 官方 [hok_env](https://github.com/tencent-ailab/hok_env) 提供现成 PPO + 自对弈 baseline，**先跑通再改**。

👉 [第六部分 · 开悟《王者荣耀》MOBA 实战](part6-kaiwu-moba.md)

---

## 🎓 课程结语

从**线性代数**到 **PPO**，再到**开悟 MOBA 实战**，你已经走完了强化学习的完整路径：
数学语言 → MDP 建模 → 核心概念 → 交互环境 → 算法实现 → 真实大环境落地。

> 强化学习的魅力在于：我们不教智能体“怎么做”，只告诉它“做得好不好”，
> 它便能在试错中，自己长出智慧。愿你带着这套思维，去解决真正有趣的问题。🚀

📗 延伸参考：[ZhiqingXiao/rl-book](https://github.com/zhiqingxiao/rl-book)（各算法的 TensorFlow 2 / PyTorch 双实现，可对照阅读；本课程统一用「鲁班瞄准」与开悟 1v1 作为运行实例）

⬅️ 上一部分：[第四部分 · 应用环境示例](part4-environments.md)
➡️ 下一部分：[第六部分 · 开悟《王者荣耀》MOBA 实战](part6-kaiwu-moba.md)
🏠 返回：[强化学习课程首页](README.md) · [Frank Zhao 主页](/README.md)

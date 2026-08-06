# 第四部分 · 应用环境示例

> 目标：学会使用 **Gymnasium** 标准接口，跑通经典环境，并**自己动手写一个环境**。

有了理论，就该动手了。强化学习需要一个能**交互**的“世界”——即**环境 (Environment)**。
业界标准是 **Gymnasium**（OpenAI Gym 的社区维护版），本部分带你把它用熟。

---

## 4.1 Gymnasium 是什么？

Gymnasium 提供了一套**统一的环境接口**，让你的算法可以无缝切换不同任务。

```bash
pip install gymnasium
```

核心就五个成员：

| 成员 | 作用 |
|------|------|
| `env.reset()` | 重置环境，返回初始观测 `obs` |
| `env.step(action)` | 执行动作，返回 `(obs, reward, terminated, truncated, info)` |
| `env.action_space` | 动作空间（能做哪些动作） |
| `env.observation_space` | 观测空间（状态长什么样） |
| `env.render()` | 可视化 |

---

## 4.2 第一个环境：CartPole（倒立摆）

目标：左右移动小车，让杆子**不要倒下**。是入门 RL 的“Hello World”。

```python
import gymnasium as gym

env = gym.make("CartPole-v1")

print("动作空间:", env.action_space)          # Discrete(2)  -> 0=左, 1=右
print("观测空间:", env.observation_space)     # Box(4,) -> [位置, 速度, 角度, 角速度]

obs, info = env.reset(seed=42)
total_reward = 0
for step in range(500):
    action = env.action_space.sample()        # 先用随机策略
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward
    if terminated or truncated:               # 杆子倒了 或 到达步数上限
        break
env.close()
print("随机策略坚持了", total_reward, "步")
```

> 随机策略通常只能坚持 10~30 步。第五部分我们会训练算法，让它坚持满 500 步！

**关键区分**：

- `terminated=True`：任务**自然结束**（杆子倒了、到达目标）；
- `truncated=True`：**外部截断**（达到最大步数）。

---

## 4.3 常见经典环境一览

| 环境 | 类型 | 目标 | 特点 |
|------|------|------|------|
| `CartPole-v1` | 离散动作 | 平衡杆子 | 入门首选 |
| `MountainCar-v0` | 离散动作 | 小车冲上山顶 | 奖励稀疏，需探索 |
| `FrozenLake-v1` | 离散/网格 | 走到终点不掉冰洞 | 适合表格法 |
| `Pendulum-v1` | 连续动作 | 摆杆立起来 | 连续控制入门 |
| `LunarLander-v2` | 离散/连续 | 平稳着陆 | 综合难度 |

```python
# FrozenLake：最适合配合 Q-Learning（第五部分）
env = gym.make("FrozenLake-v1", is_slippery=False)
print(env.observation_space)   # Discrete(16) -> 4x4 网格共16个格子
print(env.action_space)        # Discrete(4)  -> 左/下/右/上
```

---

## 4.4 动作空间与观测空间

Gymnasium 用 `space` 描述“合法的动作/状态长什么样”：

- **`Discrete(n)`**：离散，取值 `0 ~ n-1`（如上下左右）；
- **`Box(low, high, shape)`**：连续，取值在区间内的实数向量（如速度、角度）。

```python
import gymnasium as gym
env = gym.make("Pendulum-v1")
print(env.action_space)        # Box(-2.0, 2.0, (1,))  连续力矩
print(env.observation_space)   # Box(3,) 连续状态
a = env.action_space.sample()  # 采样一个合法动作
```

算法设计要看**动作空间是离散还是连续**：离散常用 Q-Learning/DQN，连续常用策略梯度/PPO。

---

## 4.5 自己动手写一个环境：GridWorld

理解环境最好的方式是**自己写一个**。我们实现一个 `4×4` 网格世界：
从左上角出发，走到右下角终点（奖励 +1），其余每步小惩罚（-0.01）。

```python
import numpy as np

class GridWorld:
    def __init__(self, size=4):
        self.size = size
        self.goal = (size - 1, size - 1)
        self.reset()

    def reset(self):
        self.pos = (0, 0)
        return self._state()

    def _state(self):
        # 把二维坐标编码成一个整数状态
        return self.pos[0] * self.size + self.pos[1]

    def step(self, action):
        r, c = self.pos
        if   action == 0: r = max(0, r - 1)            # 上
        elif action == 1: r = min(self.size - 1, r + 1) # 下
        elif action == 2: c = max(0, c - 1)            # 左
        elif action == 3: c = min(self.size - 1, c + 1) # 右
        self.pos = (r, c)

        if self.pos == self.goal:
            return self._state(), 1.0, True, {}        # 到达终点
        return self._state(), -0.01, False, {}         # 每走一步小惩罚

    def render(self):
        grid = [["." for _ in range(self.size)] for _ in range(self.size)]
        gr, gc = self.goal; grid[gr][gc] = "G"
        r, c = self.pos;    grid[r][c] = "A"
        print("\n".join(" ".join(row) for row in grid), "\n")

# 试玩
env = GridWorld()
env.reset(); env.render()
for a in [1, 1, 1, 3, 3, 3]:      # 向下三步、向右三步
    s, reward, done, _ = env.step(a)
    print(f"动作={a} 状态={s} 奖励={reward} 结束={done}")
env.render()
```

> 🎯 这个 `GridWorld` 会在第五部分被 Q-Learning 学会“最短路径”。

---

## 4.6 环境包装器 (Wrappers)

Wrapper 可以在**不改动原环境**的情况下增加功能，如限制步数、缩放奖励、记录视频：

```python
import gymnasium as gym
env = gym.make("CartPole-v1")
env = gym.wrappers.TimeLimit(env, max_episode_steps=200)   # 限制每局步数
env = gym.wrappers.RecordEpisodeStatistics(env)            # 自动统计回报
```

---

## ✅ 小结

- 环境是 RL 的“训练场”，**Gymnasium** 提供统一接口：`reset / step / spaces`；
- 分清 `terminated`（自然结束）与 `truncated`（截断）；
- **动作空间**决定算法选型：离散 → Q-Learning/DQN，连续 → 策略梯度/PPO；
- 会读别人的环境，也要会**自己写环境**（GridWorld）；
- **Wrapper** 用来灵活扩展环境功能。

## 📝 练习

1. 跑通 `CartPole-v1` 的随机策略，统计 20 局的平均坚持步数。
2. 把 `GridWorld` 改成 `5×5`，并在某个格子加一个“陷阱”（奖励 -1 且结束）。
3. 打印 `MountainCar-v0` 的动作空间与观测空间，说说它为什么“难探索”。
4. 用 `RecordEpisodeStatistics` 包装任一环境，读取并打印每局回报。

---

📗 参考代码：[ZhiqingXiao/rl-book](https://github.com/zhiqingxiao/rl-book) 全书涵盖 `FrozenLake`、`Taxi`、`MountainCar`、`CartPole`、`Pendulum`、`LunarLander` 等 Gym 环境实例

⬅️ 上一部分：[第三部分 · 强化学习基础概念](part3-rl-basics.md)
➡️ 下一部分：[第五部分 · 各式各样的强化学习算法](part5-algorithms.md)

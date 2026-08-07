# 第四部分 · 环境与接口：亲手写一个王者子任务

> 目标：理解强化学习环境的**统一接口**（`reset / step / 观测 / 动作 / 奖励 / done`），
> 并**亲手写一个可训练的《王者荣耀》子任务环境**——「鲁班瞄准」。

有了理论，就该动手了。强化学习需要一个能**交互**的"世界"——即**环境 (Environment)**。
业界的通用接口只有几个函数，**开悟的 1v1 环境和我们下面要写的子任务，遵循的是同一套接口**。
所以只要把接口吃透，从小任务到大环境都一通百通。

---

## 4.1 强化学习环境的统一接口

无论是我们自己写的小任务，还是开悟的完整 1v1，核心都是这几个成员：

| 成员 | 作用 | 在王者里 |
|------|------|---------|
| `env.reset()` | 重置环境，返回初始观测 `obs` | 开一局新对战，返回开局战场 |
| `env.step(action)` | 执行动作，返回 `(obs, reward, done, info)` | 走一帧：给出新战场、这步奖励、是否结束 |
| 动作空间 | 能做哪些动作 | 移动方向 / 技能 / 目标… |
| 观测空间 | 状态长什么样 | 战场快照向量 `s` |

> 📌 这套接口是[第一课](part0-setup.md)交互循环的代码化。开悟官方 SDK（`HoK1v1`）也是
> `reset()/step()`，业界标准库 Gymnasium 亦然——**接口通用，我们只用王者场景来学它**。

---

## 4.2 第一个可训练任务：亲手写「鲁班瞄准」环境

回忆[第一课 0.45](part0-setup.md)：我们把大任务拆成小任务，第一个就是**鲁班瞄准**——
鲁班站桩不动，地图上有个会移动的目标，训练它**朝正确方向发射炮弹命中目标**。

这个任务小到可以用**几十行纯 Python** 写出来，却五脏俱全（状态/动作/奖励/结束齐全），
是我们后面训练算法的"练兵场"：

```python
import numpy as np

class LubanAimEnv:
    """《王者荣耀》子任务：鲁班站桩，在有限步数里尽量多地命中目标。
    命中一个 +1 并立刻刷新下一个目标；未命中 -0.1，目标继续移动。回合到步数上限结束。
    - 观测 s: [dx, dz, vx, vz, cd] —— 目标相对位置、目标速度、炮弹是否就绪（5 维）
    - 动作 a: Discrete(16) —— 发射方向（把 360° 离散成 16 个扇区，朝扇区中心打）
    - 奖励 r: 命中 +1；未命中 -0.1（鼓励又快又准）
    """
    N_DIR = 16

    def __init__(self, max_steps=20, target_speed=0.05, seed=None):
        self.max_steps = max_steps
        self.target_speed = target_speed
        self.rng = np.random.default_rng(seed)

    def _new_target(self):
        ang = self.rng.uniform(0, 2 * np.pi)          # 目标方向
        r = self.rng.uniform(0.3, 1.0)                # 目标距离
        self.target = np.array([r * np.cos(ang), r * np.sin(ang)])
        v_ang = self.rng.uniform(0, 2 * np.pi)        # 目标移动方向
        self.vel = self.target_speed * np.array([np.cos(v_ang), np.sin(v_ang)])

    def reset(self):
        self.t = 0
        self._new_target()
        return self._obs()

    def _obs(self):
        return np.array([*self.target, *self.vel, 1.0], dtype=np.float32)

    def step(self, action):
        fire_ang = 2 * np.pi * (action + 0.5) / self.N_DIR         # 朝扇区中心发射
        tgt_ang = np.arctan2(self.target[1], self.target[0]) % (2 * np.pi)
        diff = abs((fire_ang - tgt_ang + np.pi) % (2 * np.pi) - np.pi)  # 环形角差
        hit = diff < (np.pi / self.N_DIR)                          # 命中容差=半个扇区
        self.t += 1
        if hit:
            reward = 1.0
            self._new_target()                                     # 命中→刷新下一个目标
        else:
            reward = -0.1
            self.target = self.target + self.vel                   # 未命中→目标继续移动
            if np.linalg.norm(self.target) > 1.2:                  # 简化：撞到边界反弹
                self.vel = -self.vel
        done = self.t >= self.max_steps
        return self._obs(), reward, done, {"hit": hit}
```

先用**随机策略**试玩，感受一下"零基础的鲁班"有多菜（我们统计每回合平均命中数与平均回报）：

```python
env = LubanAimEnv(seed=0)
total_hits = total_return = 0
for episode in range(200):
    obs = env.reset()
    done = False
    while not done:
        action = np.random.randint(env.N_DIR)     # 随机乱打
        obs, reward, done, info = env.step(action)
        total_hits += info["hit"]
        total_return += reward
print(f"随机策略：平均每回合命中 {total_hits/200:.2f} 次，平均回报 {total_return/200:.2f}")
# 随机策略：平均每回合命中 1.39 次，平均回报 -0.48  ——20 步里基本靠蒙
```

> 随机策略每回合才蒙中 1 次左右、回报是负的。**第五课我们训练它后，能做到 20 步命中 20 个、回报 +20！**

---

## 4.3 王者子任务阶梯（我们的"训练场"清单）

「鲁班瞄准」只是第一级。把 1v1 拆开，可以得到一串**由易到难、都能在 CPU 上训**的子任务：

| 子任务 | 状态（示意） | 动作 | 学到的能力 | 难度 |
|--------|------------|------|-----------|------|
| **鲁班瞄准** | 目标相对位置+速度 | 发射方向(离散) | 打得准 | ⭐ |
| **补刀最后一击** | 小兵血量、我方攻击力、弹道时间 | 何时平A(离散) | 拿经济 | ⭐⭐ |
| **残血风筝** | 我/敌血量、距离、技能CD | 移动方向+攻击(复合) | 边打边退不被抓 | ⭐⭐⭐ |
| **塔下生存** | 到塔距离、塔攻击计时、我方血量 | 进/退(离散) | 懂威胁、不越塔送 | ⭐⭐⭐ |
| **完整 1v1** | 491 维战场向量 | 三元组复合动作 | 综合博弈 | ⭐⭐⭐⭐⭐ |

> 💡 每一行都是一个独立的强化学习问题。**学会最上面几个简单的，就理解了下面复杂的。**
> 完整 1v1（最后一行）就是[第七课](part6-kaiwu-moba.md)的开悟环境。

---

## 4.4 动作空间与观测空间（都用王者场景理解）

设计算法前，先看清两件事：**状态长什么样、动作能选什么**。

- **离散动作 `Discrete(n)`**：取值 `0 ~ n-1`。
  - 鲁班瞄准：`Discrete(16)`（16 个发射方向）；
  - 补刀：`Discrete(2)`（平A / 不平A）。
- **连续/向量观测 `Box(shape)`**：实数向量。
  - 鲁班瞄准：`Box(5,)`（相对位置+速度+CD）；
  - 完整 1v1：`Box(491,)`。
- **复合动作**：完整 1v1 的动作不是一个数，而是"按钮 + 方向 + 目标"的**多个子动作头**（见[第七课 6.4](part6-kaiwu-moba.md)）。

```python
env = LubanAimEnv()
print("动作数量:", env.N_DIR)          # 16 个离散发射方向
print("观测维度:", env.reset().shape)  # (5,)
```

> 📌 选型口诀（第五课细讲）：**离散动作 → Q-Learning/DQN；复合/大动作空间 → PPO**。
> 鲁班瞄准是离散动作，正好用来练 Q-Learning 和 DQN。

---

## 4.5 进阶：把子任务变难一点

理解环境最好的方式是**动手改它**。给「鲁班瞄准」加点花样，就得到更难的任务：

- **目标闪现**：每隔几步，目标以一定概率瞬间"闪现"到随机位置（模拟敌方交闪现）；
- **提前量**：目标移动更快时，必须**预判提前量**（朝目标"将要到"的位置打，而不是当前位置）；
- **限定弹药/冷却**：炮弹有冷却，逼迫智能体挑好时机再发射。

```python
def step(self, action):
    # ...命中判定同上...
    if not hit and self.rng.random() < 0.1:        # 10% 概率触发"闪现"
        ang = self.rng.uniform(0, 2 * np.pi)
        r = self.rng.uniform(0.3, 1.0)
        self.target = np.array([r * np.cos(ang), r * np.sin(ang)])
    # ...
```

> 🎯 目标一旦会移动/闪现，**只看当前位置就不够了**——必须用上"速度"信息做预判。
> 这正是为什么我们的观测里放了 `vx, vz`：**状态要足够，才能支撑好决策**（呼应第二部分马尔可夫性）。

---

## 4.6 环境包装 (Wrappers)：不改原环境地加功能

有时想在**不动原环境代码**的前提下加点功能，比如限制每局步数、缩放奖励、统计命中率。
可以写一个"包装器"套在外面：

```python
class ScaleReward:
    """把奖励乘一个系数（奖励缩放常能稳定训练）——包装我们的鲁班环境"""
    def __init__(self, env, scale=1.0):
        self.env, self.scale = env, scale
    def reset(self):
        return self.env.reset()
    def step(self, action):
        obs, r, done, info = self.env.step(action)
        return obs, r * self.scale, done, info

env = ScaleReward(LubanAimEnv(), scale=0.5)   # 奖励缩小一半
```

> 开悟环境同样支持在外层自定义观测/奖励的处理（见[第七课 6.5](part6-kaiwu-moba.md)的奖励塑形）。

---

## 4.7 从子任务到完整开悟：接口不变，难度升级

我们自己写的「鲁班瞄准」和开悟的完整 1v1，**用的是同一套接口**，只是规模不同：

| 概念 | 鲁班瞄准（本部分自写） | 开悟 1v1（[第七课](part6-kaiwu-moba.md)） |
| --- | --- | --- |
| 观测 | `Box(5,)` | `Box(491,)` 战场向量 |
| 动作 | `Discrete(16)` 发射方向 | **三元组复合动作** + `legal_action` 合法掩码 |
| 奖励 | 命中 +1 / 未命中 -0.1 | 5 类多维可塑形（击杀/推塔/补刀/经济…） |
| 一步 | `env.step(action)`（纯 Python） | `env.step(actions)`（经 ZMQ 与 gamecore 通信） |
| 复现 | 几十行代码 | **Docker 一键**（含 Wine 运行 gamecore） |

> 换句话说：**接口不变，难度升级**。先在鲁班瞄准上把接口和算法吃透，
> 第七课去驾驭真实开悟环境自然水到渠成。
> 👉 [第七课 · 开悟《王者荣耀》MOBA 实战](part6-kaiwu-moba.md)

---

## ✅ 小结

- 环境是 RL 的"训练场"，核心接口只有 `reset / step / 动作空间 / 观测空间`；
- 我们**亲手写了「鲁班瞄准」**——一个五脏俱全、纯 CPU 可训的王者子任务；
- 把 1v1 拆成一串**子任务阶梯**：鲁班瞄准 → 补刀 → 风筝 → 塔下生存 → 完整 1v1；
- **动作空间**决定算法选型：离散 → Q-Learning/DQN，复合/大空间 → PPO；
- 会写、会改环境（加闪现/提前量），才算真正理解它；开悟用的是同一套接口。

## 📝 练习

1. 跑通 `LubanAimEnv` 的随机策略，统计 200 回合的**平均命中数与平均回报**（应该很低，为第五课做对照）。
2. 把 `target_speed` 设为 `0`（目标站桩），再统计随机的平均命中数——和会动时相比差别大吗？为什么？（提示：随机策略根本没用到位置信息）
3. 按 4.5 给环境加上"闪现"，观察随机策略的平均回报如何变化，说说为什么变难。
4. 仿照 `ScaleReward`，写一个 `TimeLimit` 包装器，把每局最多步数限制到 20。
5. 思考题：如果把观测里的 `vx, vz`（目标速度）去掉，只留位置，智能体还能学会打**移动**目标吗？为什么？（提示：马尔可夫性）

---

⬅️ 上一部分：[第三部分 · 强化学习基础概念](part3-rl-basics.md)
➡️ 下一部分：[第五部分 · 各式各样的强化学习算法](part5-algorithms.md)
🎮 旗舰实战：[第七课 · 开悟《王者荣耀》MOBA 实战](part6-kaiwu-moba.md)

# 第六部分 · 开悟《王者荣耀》MOBA 强化学习实战

> 目标：把前五部分学到的 **状态 / 动作 / 奖励 / 策略 / 价值 / PPO** 用到一个**真实、复杂、
> 亿级玩家验证过**的 MOBA 环境上——腾讯 [开悟（Kaiwu）](https://aiarena.tencent.com/) 的
> 《王者荣耀》**离线本地仿真**。全程**纯 CPU 起步**、**Docker 一键复现**。

前五部分我们在 CartPole、GridWorld、FrozenLake 这些"玩具环境"里理解了强化学习。
它们简单、直观，非常适合学概念。但真实世界的决策问题要复杂得多：
**巨大的状态空间、复合动作、稀疏且多维的奖励、还有一个会反击的对手**。

《王者荣耀》1v1 就是这样一个环境，而开悟把它**封装成了标准的强化学习接口**，
让我们不需要真机、不连线上服务器，就能在本地安全地做实验。

---

## 6.1 为什么选「开悟」而不是操控真机？

网上有一类项目（如 `wzry_ai`）用截屏 + adb 触控去操作**真机上的线上游戏**。
它很酷，但**不适合教学**：需要每人一台手机和游戏账号、依赖 GPU 做视觉识别、
而且用 AI 自动操作**线上竞技对局违反游戏条款、有封号风险**。

开悟走的是另一条路——**离线本地仿真**：

| 对比 | 操控真机(如 wzry_ai) | 开悟离线仿真(本课程) |
| --- | --- | --- |
| 是否需要真机/账号 | 需要 | **不需要** |
| 是否连线上服务器 | 是（有封号风险） | **否，完全本地** |
| 状态来源 | 截屏 + 目标检测(需 GPU) | **游戏引擎直接给结构化状态** |
| 合规性 | 灰色地带 | **官方面向教学/科研开放** |
| 可复现性 | 差（依赖设备/画面） | **好（Docker 封装）** |

> 一句话：开悟让我们把精力放在**强化学习本身**，而不是"怎么截屏、怎么点屏幕"。

---

## 6.2 环境架构：gamecore 就是我们的「环境」

回忆第四部分：一个强化学习环境的核心是 `reset() / step(action)`，返回
`观测 / 奖励 / 是否结束`。开悟的结构完全对得上：

```
你的策略(Python, CPU/torch)
      │  动作 action
      ▼
  hok_env SDK  ──(ZMQ 通信)──►  gamecore-server ──► (Wine) 游戏逻辑核心 libgamecore
      ▲                                                        │
      │  观测 observation / 合法动作 legal_action / 奖励 reward / done
      └────────────────────────────────────────────────────────┘
```

- **gamecore = 环境**：运行完整的《王者荣耀》游戏逻辑（英雄、技能、小兵、防御塔……）；
- **hok_env SDK = 接口层**：把 gamecore 的原始帧解析成 `numpy` 观测，并把你的动作发回去；
- 游戏逻辑本身**跑在 CPU**——所以"跑环境"不需要 GPU（只有训练神经网络时 GPU 才加速）。

> 🛠️ 环境怎么装、怎么起，见 [`kaiwu_env/README.md`](kaiwu_env/README.md)。
> 本章聚焦"**装好之后，强化学习怎么做**"。

---

## 6.3 状态（Observation）：几百维的战场快照

在 CartPole 里状态只有 4 个数；在开悟 1v1 里，状态是一个**几百维的向量**，
把当前这一帧的战场信息编码了进去：

- **我方英雄**：坐标、朝向、血量(HP)、蓝量(EP)、等级、经济、技能冷却……
- **敌方英雄**：能观测到的位置、血量、状态……
- **小兵 / 防御塔 / 野怪**：位置与血量；
- **全局信息**：时间、经济差、经验差等。

```python
obs, reward, done, state = env.reset(camp_config, use_common_ai=[False, True])
print(state[0].keys())
# dict_keys(['observation', 'legal_action', 'reward', 'done',
#            'sub_action_mask', 'frame_no', 'player_id', ...])
print(state[0]["observation"].shape)   # 形如 (N,) 的浮点向量——这就是"状态 s"
```

> 📌 概念对照（第三部分）：这里的 `observation` 就是 MDP 里的**状态 \(s_t\)**。
> 状态越复杂，越考验函数逼近器（神经网络）的表达能力。

---

## 6.4 动作（Action）：复合动作 + 合法动作掩码

CartPole 的动作只有"左/右"两种。MOBA 的动作是**复合动作**：一次要同时决定
"做什么 + 往哪个方向 + 对谁"。开悟把动作拆成**多个子动作头**，例如：

| 子动作头 | 含义（示意） |
| --- | --- |
| 动作类型 | 移动 / 普攻 / 技能1 / 技能2 / 技能3 / 回城 … |
| 移动方向 | 离散化的方向角 |
| 技能方向 | 技能施放方向 |
| 目标单位 | 攻击/技能指向哪个单位 |

关键点是**合法动作掩码 `legal_action`**：并非任何时候都能放技能（冷却中、蓝不够、
没目标都不行）。环境会告诉你**当前哪些动作合法**，策略只能在合法集合里选：

```python
import numpy as np

# 取出各子动作头的长度，把扁平的 legal_action 切成若干段
shapes = env.action_space()
split = np.cumsum(shapes[:-1])
legal_per_head = np.split(state[0]["legal_action"], split)

# 只在"合法"的取值里选择（这里用随机；换成网络输出即为策略）
action = []
for head in legal_per_head:
    legal_ids = [k for k, ok in enumerate(head) if ok == 1]
    action.append(np.random.choice(legal_ids))
```

> 📌 概念对照：合法动作掩码是 RL 落地的常见工程手段——在策略网络输出的 logits 上
> 对非法动作**置 -∞** 再 softmax，保证采样出的动作一定合法（既加速学习又避免无效探索）。

---

## 6.5 奖励（Reward）：多维、可塑形

在 GridWorld 里奖励只有"到终点 +1、每步 -0.01"。MOBA 的胜负由许多因素累积而成，
所以开悟提供**多维子奖励**，并允许你**自定义权重**（奖励塑形 reward shaping）。
本环境的 `config.json` 示例：

```json
{
  "reward_money": "0.006",        // 经济
  "reward_exp": "0.006",          // 经验
  "reward_hp_point": "2.0",       // 血量变化
  "reward_kill": "-0.6",          // 击杀（符号/权重按训练目标调）
  "reward_dead": "-1.0",          // 阵亡惩罚
  "reward_tower_hp_point": "5.0", // 推塔
  "reward_last_hit": "0.5",       // 补刀
  "log_level": "4"
}
```

> 📌 概念对照（第二部分）：最终目标仍是最大化**累计折扣回报** \(G_t=\sum_k \gamma^k r_{t+k}\)。
> 子奖励是把"赢"这个稀疏目标，拆成"补刀、推塔、少送人头"等**密集信号**，让学习更快。
> ⚠️ 奖励塑形是把双刃剑：权重设不好，智能体会学到"钻空子"的怪异策略。这正是好实验题。

---

## 6.6 最小交互骨架：一局随机智能体

把 6.3~6.5 串起来，就是强化学习最基本的**交互循环**（和第四部分的 Gym 循环同构）：

```python
obs, reward, done, state = env.reset(camp_config, use_common_ai=[False, True])
step = 0
while not (done[0] or done[1]):
    actions = random_legal_action(env, state, common_ai=[False, True])  # 随机合法动作
    obs, reward, done, state = env.step(actions)
    step += 1
env.close_game()
```

完整可运行脚本见 [`kaiwu_env/test_1v1_random.py`](kaiwu_env/test_1v1_random.py)，
在环境里一条命令即可跑通一局：

```bash
docker exec -it kaiwu-rl-cpu python3 /rl_framework/test_1v1_random.py
```

> 这就是 baseline 的"零分选手"。**把 `random_legal_action` 换成一个神经网络策略，
> 就正式进入训练。**

---

## 6.7 从随机到学习：策略网络 + PPO + 自对弈

开悟 1v1 的动作是复合的、状态是高维的，最适合的算法是**策略梯度类**，
尤其是第五部分讲过的 **PPO**（稳定、样本效率尚可、工业界主力）。整体框架：

1. **策略网络 \(\pi_\theta(a\mid s)\)**：输入几百维状态，输出每个子动作头的概率分布
   （对非法动作用掩码屏蔽）；同时输出价值 \(V(s)\) 供 PPO 的优势估计。
2. **采样（Actor）**：用当前策略在 gamecore 里跑很多局，收集 `(s, a, r, s')` 轨迹。
3. **训练（Learner）**：用 PPO 的裁剪目标更新 \(\theta\)。
4. **自对弈（Self-Play）**：让智能体和"过去的自己/内置 AI"对打，逐步变强。

```
   ┌── Actor：用 πθ 在 gamecore 采样轨迹 ──┐   （CPU 多进程并行开多局）
   │                                      ▼
   │                              经验缓冲区 (s,a,r,...)
   │                                      │
   └──── 更新后的 θ ◄── Learner：PPO 更新 πθ、V ◄┘   （神经网络，GPU 可加速）
```

> 📌 开悟官方仓库 [hok_env](https://github.com/tencent-ailab/hok_env) 提供了
> **PPO baseline + actor-learner 分布式框架**；
> [Unakar/AI_Game_KingGlory](https://github.com/Unakar/AI_Game_KingGlory) 是一份 1v1 参考实现。
> 学习路线建议：**先跑通官方 baseline，读懂它的网络/reward/采样，再动手改**。

---

## 6.8 纯 CPU 训练：现实与建议

游戏逻辑在 CPU，**跑通环境、单局对战、baseline 推理、小规模训练都能纯 CPU 完成**。
但要清醒认识 MOBA 的训练成本——顶尖 AI 是用大规模 GPU 集群、跑海量对局训出来的。
课堂上我们**务实定位**：

| 目标 | 是否适合纯 CPU | 说明 |
| --- | --- | --- |
| 跑通环境 / 看懂接口 | ✅ 很合适 | 本章重点 |
| 随机/规则 baseline 对局、看回放 | ✅ | 秒级~分钟级 |
| 小规模 PPO、改 reward 看行为变化 | ✅ 可行 | 用多核并行采样，耐心等 |
| 训出强 1v1 AI | ❌ 不现实 | 需要 GPU 集群 + 长时间 |

**纯 CPU 提速小技巧**：

- **多进程并行采样**：开多个 gamecore 对局同时采样（瓶颈在采样而非训练）；
- **降采样频率**：不必每帧都推理决策（如每 3 帧决策一次）；
- **缩小网络 / 简化任务**：先固定同一个英雄、镜像对局，降低泛化难度；
- 需要加速再上 GPU（[`kaiwu_env/README.md`](kaiwu_env/README.md) 第 8 节有 GPU 档说明）。

---

## ✅ 小结

- 开悟把《王者荣耀》做成了**离线、合规、可复现**的强化学习环境，接口与第四部分的 Gym 同构；
- **状态**是几百维战场向量，**动作**是带合法掩码的复合动作，**奖励**是可塑形的多维信号；
- 最小交互骨架 = `reset → (在合法动作里选) → step → 直到 done`；把"随机选"换成策略网络即开始训练；
- 高维复合动作最适合 **PPO + 自对弈**，官方有 baseline 可直接起步；
- **纯 CPU** 足以跑通与做小规模实验，训强 AI 才需要 GPU 集群。

## 📝 练习

1. 跑通 [`test_1v1_random.py`](kaiwu_env/test_1v1_random.py)，统计一局的总帧数与随机策略的胜负。
2. 打印 `state[0]["observation"].shape` 与 `env.action_space()`，说说 1v1 的状态维度、动作有几个子动作头。
3. 修改 `config.json`：把 `reward_tower_hp_point` 调大、`reward_dead` 惩罚加重，重跑并观察行为差异（可看回放 `.abs`）。
4. 阅读官方 [hok_env](https://github.com/tencent-ailab/hok_env) 的 1v1 PPO baseline，画出它的"采样→训练"数据流，指出哪一步能在 CPU 上并行。
5. 思考题：为什么 MOBA 要用**合法动作掩码**而不是让智能体"自己学会不放非法技能"？（提示：探索效率与安全约束）

---

📗 参考：
- 开悟平台：<https://aiarena.tencent.com/>
- 论文《Honor of Kings Arena》：<https://arxiv.org/abs/2209.08483>
- 官方 SDK / baseline：<https://github.com/tencent-ailab/hok_env>
- 1v1 参考实现：<https://github.com/Unakar/AI_Game_KingGlory>

⬅️ 上一部分：[第五部分 · 各式各样的强化学习算法](part5-algorithms.md)
🏠 返回：[强化学习课程首页](README.md)

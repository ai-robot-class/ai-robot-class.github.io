# 开悟《王者荣耀》1v1 · 纯 CPU 强化学习环境（Docker / WSL2）

本目录提供一套**可复现的 Docker 环境**，在 **WSL2 + Docker** 上用 **Wine** 运行
腾讯 [开悟（Kaiwu）](https://aiarena.tencent.com/) 的《王者荣耀》**离线本地仿真** gamecore，
并配好 [hok_env](https://github.com/tencent-ailab/hok_env) SDK 与 **PyTorch(CPU)**，
让学生在**不需要真机、不连线上服务器、无封号风险**的前提下动手做 MOBA 强化学习。

> 先用**纯 CPU** 跑通环境与小规模训练；需要加速时再切换 GPU 档（见文末）。

---

## 0. 你需要准备什么

| 项 | 说明 | 是否必需 |
| --- | --- | --- |
| WSL2 + Docker | Windows 上装 WSL2，并让 Docker 使用 WSL2 后端 | ✅ |
| 开悟 gamecore | 已解压的 `hok_env_gamecore/gamecore/` 目录（含 `gamecore-server-linux-amd64`、`bin/`、`lib/`、`scene/`、`core_assets/`） | ✅ |
| **`license.dat`** | 从[开悟平台](https://aiarena.tencent.com/aiarena/zh/open-gamecore)申请，放到 `gamecore/core_assets/license.dat` | ✅（否则只能启动 server，无法完整开局） |
| NVIDIA GPU | 仅在需要加速训练时 | ⬜ 可选 |

> ⚠️ **合规提醒**：gamecore 与 license 受开悟平台授权约束，仅用于非商业的教学/科研；
> 请勿将 gamecore、`license.dat` 或对局数据提交到任何公开仓库。

---

## 1. 架构一图看懂

```
┌──────────────────────── Docker 容器 (Linux) ───────────────────────┐
│                                                                    │
│   Python 训练脚本 ── hok_env SDK ──(ZMQ)──┐                         │
│   (你的策略/PPO, CPU/torch)               │                         │
│                                          ▼                         │
│                              gamecore-server-linux-amd64 (Go)      │
│                                          │  调度对局                 │
│                                          ▼                         │
│                    Wine ── sgame_simulator_remote_zmq.exe          │
│                            + libgamecore.dll  (游戏逻辑核心, CPU)   │
│                                          │                         │
│                              scene/*.abs + core_assets(+license)   │
└────────────────────────────────────────────────────────────────────┘
             对局回放 .abs → 用 replay_tool 在 Windows 查看
```

- **gamecore = 环境**：给出观测(observation)、合法动作(legal_action)、奖励(reward)、结束(done)；
- **hok_env SDK**：把 gamecore 的 protobuf 帧解析成 numpy 观测，并把你的动作发回去；
- 一切在 **CPU** 上运行，游戏逻辑本身不需要 GPU。

---

## 2. 放置 gamecore 与 license

假设开悟包已解压到宿主机（WSL 内）某处，例如：

```bash
# 目录形如：
#   /home/you/hok_env_gamecore/gamecore/gamecore-server-linux-amd64
#   /home/you/hok_env_gamecore/gamecore/core_assets/
export KAIWU_GAMECORE=/home/you/hok_env_gamecore/gamecore

# 把申请到的 license.dat 放进 core_assets
cp /path/to/license.dat "$KAIWU_GAMECORE/core_assets/license.dat"
```

---

## 3. 构建镜像

```bash
cd courses/rl/kaiwu_env
docker compose build          # 或： docker build -t kaiwu-rl-cpu .
```

镜像内装了：Ubuntu 20.04 + **便携 Wine（wow64 纯 64 位，打进镜像）** + Python3 + PyTorch(CPU) + hok_env SDK + 启动脚本。

> - 采用 [Kron4ek](https://github.com/Kron4ek/Wine-Builds) 的 **wow64** 便携构建：**无需 32 位库、免系统级安装**，
>   构建时下载解压到 `/opt/wine` 即用，并已在构建阶段 `wineboot --init` 预初始化 prefix（首局更快）。
> - **离线/内网构建**：把 `wine-<版本>-amd64-wow64.tar.xz` 放到本目录，将 Dockerfile 里的 `wget` 改为 `COPY` 即可。
> - 首次构建会下载 Wine 与依赖，需几分钟；PyTorch 用 CPU 轮子，体积较小。

> ✅ 该 Wine 便携构建 + 本包 gamecore + license 已在纯 CPU 上实测跑通一整局 1v1（内置 AI 自对弈）。

---

## 4. 启动 gamecore server

```bash
# 前台启动（Ctrl+C 退出）
KAIWU_GAMECORE=$KAIWU_GAMECORE docker compose up

# 或后台
KAIWU_GAMECORE=$KAIWU_GAMECORE docker compose up -d
docker logs -f kaiwu-rl-cpu
```

看到 gamecore-server 打印 `POST /v1/newGame ...` 且监听 `:23432`，即表示就绪。

---

## 5. 冒烟测试：跑一局随机智能体

另开一个终端进入容器（或直接把 compose 的 `command` 改成 `["test"]`）：

```bash
docker exec -it kaiwu-rl-cpu python3 /rl_framework/test_1v1_random.py
```

预期输出（节选）：

```
gamecore=127.0.0.1:23432  ai_server=127.0.0.1
开始对局： {'mode': '1v1', 'heroes': [[{'hero_id': ...}], [{'hero_id': ...}]]}
---- frame 0  step 0
---- frame ... step 100
...
对局结束，共 XXXX 步。回放 .abs 文件已写入 gamecore/simulator_output/。
```

这条脚本就是**强化学习的最小交互骨架**：把「随机选合法动作」替换成神经网络策略即可开始训练。

也可只验证 server 本身（用内置规则 AI 对打一局，不经过 Python 策略）：

```bash
docker exec -it kaiwu-rl-cpu python3 /rl_framework/remote-gc-server/test_client.py
# Success {'X-Request-ID': '...'}
```

---

## 6. 查看对局回放

对局会在 `./simulator_output/` 生成 `.abs` 回放文件（已挂载到宿主机）。
把它拷到 Windows，用开悟包内的 `replay_tool/ABSTool.exe` 打开即可观看画面。

---

## 7. 调整奖励与超参

- **奖励塑形**：编辑本目录 `config.json`（击杀/死亡/推塔/补刀/经济/经验等子奖励权重）。
  该文件在创建环境实例时读取一次，修改后需重建环境（重跑脚本）。
- **英雄/对阵**：在训练脚本里改 `camp_config`（`hero_id`）。当前 gamecore 支持 20+ 英雄
  （鲁班/后羿/貂蝉/李白/花木兰/韩信/吕布……见 `gamecore/scene/`）。

---

## 8.（可选）GPU 加速档

纯 CPU 足以**跑通环境 + 小规模训练/调参**。要加速大规模训练：

1. 宿主机（WSL2）装好 NVIDIA 驱动 + [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)；
2. 把 `Dockerfile` 里的 PyTorch 换成 CUDA 版（如 `--index-url https://download.pytorch.org/whl/cu121`）；
3. `docker compose` 增加 GPU：
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: all
             capabilities: [gpu]
   ```
   注意：**gamecore（游戏逻辑）始终在 CPU**，GPU 只加速神经网络的训练/推理。

---

## 9. 常见问题

- **`未发现 license.dat`**：请按第 2 步放置 `core_assets/license.dat`。
- **`/lib/ld-linux.so.2: could not open`**：说明用到了需要 32 位库的普通 Wine。本镜像已改用 **wow64** 便携 Wine 规避；若你自行改 Wine，请务必用 wow64/纯 64 位构建。
- **`Couldn't compute FAST_CWD pointer`（Cygwin 警告）**：Wine 下常见，可忽略，不影响对局。
- **端口占用 / 连不上 23432**：确认 compose 使用 `network_mode: host`，且宿主没有别的进程占用 23432。
- **SDK 包名 / 版本**：新版 SDK 的 PyPI 包名是 **`hok`**（旧的 `hok_env` 已过时、且没有 `hok.hok1v1`）。
  它要求 **Python ≤ 3.9**（内含 py3.6~3.9 预编译扩展），并需与 gamecore 版本匹配——本包 gamecore 为
  `v45_1450123`，对应 `hok==45.1.5`（已在纯 CPU 上实测端到端跑通：新 SDK 随机策略控制一整局 1v1）。

---

## 参考

- 开悟平台：<https://aiarena.tencent.com/>
- hok_env（官方 SDK/框架/PPO baseline）：<https://github.com/tencent-ailab/hok_env>
- 在 Linux 上用 Wine 跑 Windows gamecore：<https://github.com/tencent-ailab/hok_env/blob/master/docs/run_windows_gamecore_on_linux.md>
- 1v1 参考实现：[Unakar/AI_Game_KingGlory](https://github.com/Unakar/AI_Game_KingGlory)

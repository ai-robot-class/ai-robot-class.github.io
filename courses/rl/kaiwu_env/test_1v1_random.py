"""开悟《王者荣耀》1v1 · 随机智能体冒烟测试 / 教学入门脚本

作用：
  1. 连接已启动的 gamecore server（默认 127.0.0.1:23432）；
  2. 用 hok_env SDK 创建一个 1v1 环境；
  3. 让「我方英雄」在每一帧的合法动作中**随机**选择动作，对手用内置规则 AI；
  4. 跑完一整局并打印进度，验证「环境 → 观测/合法动作 → 动作 → 下一帧」闭环是否通畅。

这就是强化学习最小的交互骨架：把其中的「随机选动作」换成神经网络策略，即可开始训练。

运行前提：gamecore server 已在本机启动（见 README / entrypoint.sh 的 serve 模式）。
    python3 test_1v1_random.py
"""
import os
import random

import numpy as np
from hok.hok1v1 import HoK1v1
from hok.common.gamecore_client import GamecoreClient
from hok.hok1v1.env1v1 import interface_default_config
from hok.hok1v1.hero_config import get_default_hero_config
import hok.hok1v1.lib.interface as interface
from hok.common.camp import HERO_DICT, camp_iterator_1v1_roundrobin_camp_heroes


def random_legal_action(env, states, common_ai):
    """在当前帧的合法动作(legal_action)里，为每个子动作头随机采样一个合法值。

    王者 1v1 的动作是「复合动作」：由多个子动作(如 是否移动/技能/方向/目标 等)组成，
    每个子动作都有自己的合法掩码。这里演示如何只在合法项中随机选择。
    """
    actions = []
    shapes = env.action_space()

    # 将各子动作的长度累加成分割点，便于把扁平的 legal_action 切成若干段
    split_array = shapes.copy()[:-1]
    for i in range(1, len(split_array)):
        split_array[i] = split_array[i - 1] + split_array[i]

    for i in range(2):
        if common_ai[i]:
            # 该 camp 交给内置规则 AI，无需我们出动作
            actions.append(tuple([0] * 6))
            continue

        legal_action = np.split(states[i]["legal_action"], split_array)
        act = []
        for j, _ in enumerate(shapes):
            # 收集第 j 个子动作头中所有「合法」的取值
            legal_ids = [k for k, la in enumerate(legal_action[j]) if la == 1]
            a = random.choice(legal_ids)
            act.append(a)
            if j == 0:
                # 特殊处理：动作类型选定后，方向/目标掩码要按所选类型重排
                if legal_action[0][8]:
                    act[0] = 8
                    a = 8
                legal_action[5] = legal_action[5].reshape(-1, shapes[-1])[a]
        actions.append(tuple(act))
    return actions


def main():
    # 1) 初始化 protobuf 特征处理器（把 gamecore 的原始帧解析成观测/合法动作/奖励）
    lib_processor = interface.Interface()
    lib_processor.Init(interface_default_config)

    # 2) gamecore server 地址 & 本机 AI server 地址（可用环境变量覆盖）
    gc_server_addr = os.getenv("GAMECORE_SERVER_ADDR", "127.0.0.1:23432")
    ai_server_addr = os.getenv("AI_SERVER_ADDR", "127.0.0.1")
    print(f"gamecore={gc_server_addr}  ai_server={ai_server_addr}")

    # 3) 两名玩家各开一个 ZMQ 端口用于收发帧
    addrs = [f"tcp://0.0.0.0:{35150 + i}" for i in range(2)]

    game_launcher = GamecoreClient(
        server_addr=gc_server_addr,
        gamecore_req_timeout=3000,
        default_hero_config=get_default_hero_config(),
    )

    env = HoK1v1(
        "kaiwu-demo",
        game_launcher,
        lib_processor,
        addrs,
        aiserver_ip=ai_server_addr,
    )

    # 4) 选择对阵英雄（这里轮询选取一组镜像/非镜像对局）
    camp_iter = camp_iterator_1v1_roundrobin_camp_heroes(HERO_DICT.values())
    camp_config = next(camp_iter)

    # camp0 = 我方(随机策略)，camp1 = 内置规则 AI
    common_ai = [False, True]

    print("开始对局：", camp_config)
    obs, reward, done, state = env.reset(camp_config, use_common_ai=common_ai, eval=False)

    step = 0
    while True:
        if step % 100 == 0:
            print(f"---- frame {env.cur_frame_no}  step {step}")
        actions = random_legal_action(env, state, common_ai)
        obs, reward, done, state = env.step(actions)
        if done[0] or done[1]:
            break
        step += 1

    env.close_game()
    print(f"对局结束，共 {step} 步。回放 .abs 文件已写入 gamecore/simulator_output/。")


if __name__ == "__main__":
    main()

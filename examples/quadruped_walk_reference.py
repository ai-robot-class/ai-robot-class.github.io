"""
四足机器人步态控制 —— 参考实现（Reference）
====================================================

这是 examples/quadruped_walk_starter.py 经过【AI 辅助迭代调试】
最终调通的版本。Laikago 在 PyBullet 仿真里可以稳定向前 "爬行小跑"。

本版本由学生与 AI 共同迭代得到（详细对话过程见 content/week13.md §13.7.4），
踩过的坑 / 解决方案对应关系：

| 现象                          | 修复方法                                     |
|------------------------------|---------------------------------------------|
| 启动 PID 爆炸、机器狗瞬间弹飞 | resetJointState 强制就位 + 前 2 秒站立缓冲   |
| 关节索引硬编码导致控制错误     | 动态扫描 JOINT_REVOLUTE，自动找出 12 个电机  |
| 力矩太小，膝盖瞬间软掉         | force 提高到 150~180、positionGain 0.05~0.08 |
| 摔倒：trot 慢速时仅 2 腿撑地  | 改为 Creep 步态：单腿轮换 (4 拍 25%/75%)     |
| 脚打滑 / 走不动               | plane 和机身 lateralFriction 提到 1.5        |
| 向后走（moonwalk）            | 由于初始 Euler，把 thigh 摆动方向符号翻转    |
| 想走快一些                    | frequency 0.4 → 1.0, step_length 0.08→0.16  |

运行方法：
    python3 examples/quadruped_walk_reference.py

可选参数：
    --fast      使用更快的步态（frequency=1.0）
    --no-gui    headless 模式（用于课堂自动评分）
"""

import argparse
import math
import time

import numpy as np
import pybullet as p
import pybullet_data


# ============================================================
# 1. 控制器
# ============================================================
class QuadrupedController:
    """
    Creep（爬行）步态 + 关节扫描 + 启动缓冲 + 高摩擦四足控制器。

    设计要点：
        • Creep gait：4 拍循环，每条腿摆动 25%、支撑 75%
          → 任意时刻至少 3 条腿在地，静态稳定
        • 关节动态映射：扫描 URDF，自动选出 12 个 REVOLUTE 电机
          → 不依赖硬编码索引，更换 URDF 也能跑
        • 启动前先把关节 reset 到目标姿态，避免 PID 爆炸
    """

    # 4 条腿的相位偏移（保证一次只抬一条腿）
    PHASES = [0.00, 0.25, 0.50, 0.75]

    # 基础站立姿态（弧度）
    HIP_BIAS = 0.0
    THIGH_BIAS = 0.7
    CALF_BIAS = -1.4

    def __init__(self, robot_id, step_length=0.16, step_height=0.18):
        self.robot_id = robot_id
        self.step_length = step_length
        self.step_height = step_height

        # 步骤 1：动态扫描可驱动的旋转电机
        self.legs = self._discover_legs()
        if len(self.legs) < 4:
            raise RuntimeError(
                f"只找到 {len(self.legs)} 条腿，URDF 似乎不是四足机器人。"
            )

        # 步骤 2：提高机身所有 link 的摩擦力，防止打滑
        for link_id in range(-1, p.getNumJoints(self.robot_id)):
            p.changeDynamics(self.robot_id, link_id, lateralFriction=1.5)

    def _discover_legs(self):
        """扫描 URDF，把 12 个 REVOLUTE 关节按腿分组：[hip, thigh, calf]×4"""
        legs, leg = [], []
        for j in range(p.getNumJoints(self.robot_id)):
            jtype = p.getJointInfo(self.robot_id, j)[2]
            if jtype != p.JOINT_REVOLUTE:
                continue
            leg.append(j)
            if len(leg) == 3:
                legs.append(leg)
                leg = []
        return legs

    # ------- 姿态生成 ----------------------------------------------------
    def init_pose(self):
        """物理引擎开始 step 之前，强制把关节摆到站立姿态。"""
        for hip, thigh, calf in self.legs:
            p.resetJointState(self.robot_id, hip, self.HIP_BIAS)
            p.resetJointState(self.robot_id, thigh, self.THIGH_BIAS)
            p.resetJointState(self.robot_id, calf, self.CALF_BIAS)

    def stand_targets(self):
        return [self.HIP_BIAS, self.THIGH_BIAS, self.CALF_BIAS]

    def creep_targets(self, t, leg_index, frequency=1.0):
        """
        生成第 leg_index 条腿在时刻 t 的关节目标角。

        - 25% 摆动相：腿先向前摆，calf 收起以抬脚
        - 75% 支撑相：脚踩地面、腿向后推驱动身体前进
        """
        cycle = (t * frequency + self.PHASES[leg_index]) % 1.0
        hip = self.HIP_BIAS

        if cycle < 0.25:
            progress = cycle / 0.25
            thigh = self.THIGH_BIAS + self.step_length * np.cos(progress * np.pi)
            calf = self.CALF_BIAS - self.step_height * np.sin(progress * np.pi)
        else:
            progress = (cycle - 0.25) / 0.75
            thigh = self.THIGH_BIAS - self.step_length * np.cos(progress * np.pi)
            calf = self.CALF_BIAS

        return [hip, thigh, calf]

    # ------- 控制接口 ----------------------------------------------------
    def step(self, t, state="walk", frequency=1.0, force=180, gain=0.08):
        for i, leg_motors in enumerate(self.legs):
            targets = (
                self.stand_targets()
                if state == "stand"
                else self.creep_targets(t, i, frequency)
            )
            for motor_id, angle in zip(leg_motors, targets):
                p.setJointMotorControl2(
                    self.robot_id, motor_id, p.POSITION_CONTROL,
                    targetPosition=angle,
                    force=force,
                    positionGain=gain,
                )


# ============================================================
# 2. 主程序
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true",
                        help="使用更快的步态（frequency=1.0）")
    parser.add_argument("--no-gui", action="store_true",
                        help="无 GUI 模式（用于自动评分 / CI）")
    parser.add_argument("--seconds", type=float, default=20.0,
                        help="仿真总时长，默认 20 秒；设 0 表示一直跑")
    args = parser.parse_args()

    # ---- 物理引擎初始化 ----
    p.connect(p.DIRECT if args.no_gui else p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)
    plane = p.loadURDF("plane.urdf")
    p.changeDynamics(plane, -1, lateralFriction=1.5)

    # ---- 加载机器人 ----
    # 注意：保留学生原始的初始朝向（face forward）
    start_orientation = p.getQuaternionFromEuler(
        [math.pi / 2, 0, math.pi / 2]
    )
    robot_id = p.loadURDF(
        "laikago/laikago_toes.urdf", [0, 0, 0.65], start_orientation,
    )

    controller = QuadrupedController(robot_id)
    controller.init_pose()      # ★ 关键：避免启动 PID 爆炸

    # ---- 仿真主循环 ----
    t, dt = 0.0, 1.0 / 240.0
    warmup_t = 2.0              # 前 2 秒静止站立缓冲
    frequency = 1.0 if args.fast else 0.5

    print(f"启动仿真 | warmup={warmup_t}s | walk freq={frequency} Hz")

    try:
        while True:
            if t < warmup_t:
                controller.step(t, state="stand")
            else:
                controller.step(t - warmup_t, state="walk", frequency=frequency)

            p.stepSimulation()
            if not args.no_gui:
                time.sleep(dt)
            t += dt

            if args.seconds > 0 and t >= args.seconds:
                break
    except KeyboardInterrupt:
        pass
    finally:
        # 简单评估：报告机器人在 X 方向走了多远（注意坐标轴被旋转过）
        pos, _ = p.getBasePositionAndOrientation(robot_id)
        print(f"\n仿真结束。机身最终位置 = {tuple(round(x, 3) for x in pos)}")
        print(f"沿世界 +Y 方向位移 ≈ {pos[1]:.3f} m  （正数表示向前走）")
        p.disconnect()


if __name__ == '__main__':
    main()

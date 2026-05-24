"""
四足机器人步态控制 —— 起点代码（Starter）
====================================================

目标：让 Laikago 机器狗在 PyBullet 仿真里向前小跑（trot）。

🚨 这段代码是【故意有问题的初始版本】，学生拿到后会发现：
   - 机器狗一启动就摔倒
   - 即使能站住也走不动 / 走错方向

课堂任务：用 AI 辅助编程（Cursor / Copilot / ChatGPT / Claude / Gemini ...）
        把这段代码改造成稳定向前行走的版本。

提交要求：
   1. 一段最终可运行的 quadruped_walk.py
   2. 一段你与 AI 对话的截图或文本（>= 3 轮）
   3. 一段简短反思：你给 AI 哪些「物理观察」让它最终调通？

运行方法：
   python3 examples/quadruped_walk_starter.py
"""

import math
import time

import numpy as np
import pybullet as p
import pybullet_data


class QuadrupedController:
    """简单的四足控制器（起点版本）"""

    def __init__(self, robot_id):
        self.robot_id = robot_id

        # 关节 ID（这里硬编码了 0~11，可能与实际 URDF 不一致！）
        self.leg_joints = {
            'LF': [0, 1, 2],
            'RF': [3, 4, 5],
            'LH': [6, 7, 8],
            'RH': [9, 10, 11],
        }

        # 步态参数
        self.stance_height = 0.3
        self.step_height = 0.05
        self.step_length = 0.1

    def trot_gait(self, t, leg_name, frequency=1.0):
        """对角同步的 Trot 步态生成器"""
        # 对角腿同相位
        phase = 0.0 if leg_name in ('LF', 'RH') else np.pi
        cycle_phase = (2 * np.pi * frequency * t + phase) % (2 * np.pi)

        if cycle_phase < np.pi:                # 摆动相
            progress = cycle_phase / np.pi
            x = self.step_length * (progress - 0.5)
            z = self.step_height * np.sin(np.pi * progress)
        else:                                  # 支撑相
            progress = (cycle_phase - np.pi) / np.pi
            x = self.step_length * (0.5 - progress)
            z = 0.0

        # 简化逆运动学（精度有限）
        target_height = self.stance_height + z
        thigh = np.arctan2(x, target_height)
        calf = -2 * thigh
        hip = 0.0
        return [hip, thigh, calf]

    def step(self, t, frequency=1.0):
        for leg_name, joint_ids in self.leg_joints.items():
            angles = self.trot_gait(t, leg_name, frequency)
            for jid, ang in zip(joint_ids, angles):
                p.setJointMotorControl2(
                    self.robot_id, jid, p.POSITION_CONTROL,
                    targetPosition=ang, force=20,
                )


def main():
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)
    p.loadURDF("plane.urdf")

    # 注意：这里的 Euler 角让 Laikago 「面向前方」，但坐标轴会被颠倒
    start_orientation = p.getQuaternionFromEuler(
        [math.pi / 2, 0, math.pi / 2]
    )
    robot_id = p.loadURDF(
        "laikago/laikago_toes.urdf", [0, 0, 0.5], start_orientation,
    )

    controller = QuadrupedController(robot_id)
    t, dt = 0.0, 1.0 / 240.0

    print("开始仿真，按 Ctrl+C 停止...")
    try:
        while True:
            controller.step(t, frequency=0.5)
            p.stepSimulation()
            time.sleep(dt)
            t += dt
    except KeyboardInterrupt:
        print("仿真结束")
    finally:
        p.disconnect()


if __name__ == '__main__':
    main()

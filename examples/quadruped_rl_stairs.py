"""
四足机器人爬楼梯强化学习示例（多机器人并排训练 + CMA-ES）
======================================================

教学版：用进化策略 (CMA-ES) 优化参数化步态，
让一群四足机器人**同时**学习爬上楼梯。

特点：
- ✅ 完全 CPU 可跑（不需要 GPU）
- ✅ 一群机器狗并排显示，视觉震撼
- ✅ 每个机器人独立 PyBullet 仿真，物理隔离
- ✅ 多进程并行（--num_envs N）加速训练
- ✅ 训练全过程录 GIF，呈现"从摔倒到爬上"的演化
- ✅ 训练 50 代 ~ 1-3 分钟

依赖：
    pip install pybullet numpy cma matplotlib imageio

用法：
    # 单进程训练
    python quadruped_rl_stairs.py train --generations 50

    # 6 个并行 worker
    python quadruped_rl_stairs.py train --generations 50 --num_envs 6

    # 同时录训练过程 GIF（一群机器狗）
    python quadruped_rl_stairs.py train --generations 50 --num_envs 6 \\
        --record_progress training.gif

    # 用训练好的参数演示一群机器狗爬楼梯
    python quadruped_rl_stairs.py demo --num_robots 9 --record swarm_demo.gif

关于 GPU：
    PyBullet 物理引擎不支持 GPU。要用 GPU 加速大规模并行，
    请切换到 NVIDIA Isaac Lab / MuJoCo MJX / Google Brax。
"""

import os
import math
import time
import json
import argparse
import multiprocessing as mp
import numpy as np
import pybullet as p
import pybullet_data


# ============================================================
# 1. 楼梯场景
# ============================================================

STAIR_STEP_HEIGHT = 0.05    # 每级 5 cm
STAIR_STEP_DEPTH = 0.40     # 每级深 40 cm
STAIR_NUM_STEPS = 4         # 共 4 级
STAIR_X_START = 0.6         # 楼梯起点距机器人 60cm（近一些）
STAIR_WIDTH = 5.0           # 楼梯左右宽 5 m（容纳 12+ 机器人）


def build_stairs(client_id, num_steps=STAIR_NUM_STEPS,
                 step_h=STAIR_STEP_HEIGHT, step_d=STAIR_STEP_DEPTH,
                 width=STAIR_WIDTH, x_start=STAIR_X_START):
    """用一堆 box 拼成楼梯（彩虹渐变色，对比鲜明）"""
    # 渐变色：从橙红 → 黄 → 绿 → 蓝 → 紫
    palette = [
        [0.95, 0.40, 0.30, 1.0],  # 橙红
        [0.98, 0.75, 0.20, 1.0],  # 金黄
        [0.55, 0.85, 0.35, 1.0],  # 草绿
        [0.30, 0.65, 0.90, 1.0],  # 天蓝
        [0.65, 0.45, 0.90, 1.0],  # 淡紫
        [0.95, 0.55, 0.75, 1.0],  # 樱粉
        [0.45, 0.85, 0.85, 1.0],  # 青色
    ]
    stairs = []
    for i in range(num_steps):
        half_size = [step_d / 2, width / 2, step_h * (i + 1) / 2]
        col = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_size,
                                     physicsClientId=client_id)
        color = palette[i % len(palette)]
        vis = p.createVisualShape(p.GEOM_BOX, halfExtents=half_size,
                                  rgbaColor=color,
                                  physicsClientId=client_id)
        pos = [x_start + step_d / 2 + i * step_d, 0, step_h * (i + 1) / 2]
        body = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=col,
            baseVisualShapeIndex=vis,
            basePosition=pos,
            physicsClientId=client_id,
        )
        stairs.append(body)

    # 起点标线（深绿）
    start_line_half = [0.02, width / 2, 0.005]
    sl_col = p.createCollisionShape(p.GEOM_BOX, halfExtents=start_line_half,
                                     physicsClientId=client_id)
    sl_vis = p.createVisualShape(p.GEOM_BOX, halfExtents=start_line_half,
                                  rgbaColor=[0.1, 0.5, 0.1, 1.0],
                                  physicsClientId=client_id)
    p.createMultiBody(baseMass=0, baseCollisionShapeIndex=sl_col,
                      baseVisualShapeIndex=sl_vis,
                      basePosition=[0, 0, 0.005],
                      physicsClientId=client_id)
    return stairs


# ============================================================
# 2. 单个机器人环境（用于训练时的物理仿真）
# ============================================================

class StairsEnv:
    """单个机器人在楼梯场景上"""

    SIM_DT = 1.0 / 240.0
    CTRL_DT = 1.0 / 50.0
    EPISODE_T = 6.0
    # Laikago nominal 站立高度约 0.40m（thigh=0.65, calf=-1.20）
    # 略高一点点让机器人轻轻落地，避免穿模
    INIT_HEIGHT = 0.42
    NOMINAL_THIGH = 0.65
    NOMINAL_CALF = -1.20

    def __init__(self, gui=False):
        self.gui = gui
        self.client_id = p.connect(p.GUI if gui else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath(),
                                  physicsClientId=self.client_id)
        p.setGravity(0, 0, -9.81, physicsClientId=self.client_id)
        p.setTimeStep(self.SIM_DT, physicsClientId=self.client_id)
        p.loadURDF('plane.urdf', physicsClientId=self.client_id)
        build_stairs(self.client_id)
        self.robot = None
        self.leg_joints = {
            'RF': [0, 1, 2], 'LF': [4, 5, 6],
            'RH': [8, 9, 10], 'LH': [12, 13, 14],
        }
        self._spawn_robot()

    def _spawn_robot(self, y_offset=0.0):
        if self.robot is not None:
            p.removeBody(self.robot, physicsClientId=self.client_id)
        start_pos = [0, y_offset, self.INIT_HEIGHT]
        start_orn = p.getQuaternionFromEuler([math.pi / 2, 0, math.pi / 2])
        self.robot = p.loadURDF('laikago/laikago_toes.urdf',
                                start_pos, start_orn,
                                physicsClientId=self.client_id)
        for joint_ids in self.leg_joints.values():
            for joint_id, target in zip(joint_ids,
                                        [0.0, self.NOMINAL_THIGH, self.NOMINAL_CALF]):
                p.resetJointState(self.robot, joint_id, target,
                                  physicsClientId=self.client_id)
        # 稳定姿态
        for _ in range(100):
            for joint_ids in self.leg_joints.values():
                for joint_id, target in zip(joint_ids,
                                            [0.0, self.NOMINAL_THIGH, self.NOMINAL_CALF]):
                    p.setJointMotorControl2(
                        self.robot, joint_id, p.POSITION_CONTROL,
                        targetPosition=target, force=120,
                        positionGain=1.0, velocityGain=0.5,
                        physicsClientId=self.client_id,
                    )
            p.stepSimulation(physicsClientId=self.client_id)
        pos, _ = p.getBasePositionAndOrientation(self.robot,
                                                  physicsClientId=self.client_id)
        self.start_x = pos[0]
        self.start_z = pos[2]
        self.t = 0.0

    def reset(self):
        self._spawn_robot()

    def step(self, params):
        freq, lift, duty, stance_thigh, stance_calf = params[:5]
        phase_lf, phase_rf, phase_lh, phase_rh = params[5:9]
        forward_bias = params[9]
        leg_phases = {
            'LF': phase_lf, 'RF': phase_rf,
            'LH': phase_lh, 'RH': phase_rh,
        }
        sub_steps = int(self.CTRL_DT / self.SIM_DT)
        for _ in range(sub_steps):
            self.t += self.SIM_DT
            for leg_name, joint_ids in self.leg_joints.items():
                phase = leg_phases[leg_name]
                phi = (self.t * freq + phase) % 1.0
                stride = 0.30
                # 注意 Laikago thigh 关节方向：增大 = 大腿往前摆（推机身向前）
                if phi < duty:
                    # 支撑相：脚已经着地，thigh 从后往前扫，推机身前进
                    s = phi / duty
                    thigh_sway = stride * (s - 0.5)  # -stride/2 → +stride/2
                    z_lift = 0.0
                else:
                    # 摆动相：抬脚 + thigh 往后摆（准备下一步）
                    s = (phi - duty) / max(1.0 - duty, 1e-3)
                    z_lift = lift * math.sin(math.pi * s)
                    thigh_sway = stride * (0.5 - s)  # +stride/2 → -stride/2
                hip = 0.0
                # 摆动时把腿收紧（thigh +z_lift），同时小腿弯曲
                thigh = stance_thigh + thigh_sway + z_lift * 1.2 + forward_bias
                calf = stance_calf - z_lift * 1.5

                for joint_id, target in zip(joint_ids, [hip, thigh, calf]):
                    p.setJointMotorControl2(
                        self.robot, joint_id, p.POSITION_CONTROL,
                        targetPosition=target, force=200,
                        positionGain=1.2, velocityGain=0.6,
                        physicsClientId=self.client_id,
                    )
            p.stepSimulation(physicsClientId=self.client_id)
            if self.gui:
                time.sleep(self.SIM_DT)
        reward, done, info = self._compute_reward()
        return reward, done, info

    def _compute_reward(self):
        pos, orn = p.getBasePositionAndOrientation(self.robot,
                                                    physicsClientId=self.client_id)
        forward_dist = pos[0] - self.start_x
        climbed_height = max(0, pos[2] - self.start_z)

        # 用 base 的"上方向"判断翻车（更准确，不依赖 Euler）
        rot_mat = p.getMatrixFromQuaternion(orn)
        # rot_mat 是 3x3 旋转矩阵的 flatten，base 局部 +Y 在世界的方向就是机身上方
        # （因为初始 orn = [π/2, 0, π/2]，机器人 y 轴朝上）
        body_up_world_z = rot_mat[7]  # 第 7 个元素 = Y-axis 在世界 Z 上的分量
        tilt = 1.0 - body_up_world_z  # 0 = 直立，2 = 完全倒立

        # 奖励：前进 + 爬升 + 直立
        reward = forward_dist * 1.0 + climbed_height * 5.0
        reward -= tilt * 1.0

        done = False
        info = {'forward_dist': forward_dist, 'climbed_height': climbed_height,
                'height': pos[2], 'tilt': tilt}
        # 翻车 = 上方向偏离 > 60°（cos60°=0.5，tilt=0.5）
        if pos[2] < 0.20 or tilt > 0.7:
            done = True
            reward -= 3.0
            info['terminated'] = 'fell'
        if self.t >= self.EPISODE_T:
            done = True
            info['terminated'] = 'timeout'
        return reward, done, info

    def close(self):
        if p.isConnected(self.client_id):
            p.disconnect(self.client_id)


# ============================================================
# 3. Swarm 渲染环境：一群机器人在同一仿真中（仅用于演示和录 GIF）
# ============================================================

class SwarmStairsEnv:
    """多个机器人并排在同一物理仿真中爬楼梯（用于可视化）"""

    SIM_DT = 1.0 / 240.0
    CTRL_DT = 1.0 / 50.0
    EPISODE_T = 6.0
    NOMINAL_THIGH = 0.65
    NOMINAL_CALF = -1.20

    def __init__(self, num_robots=5, y_spacing=0.6):
        self.client_id = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath(),
                                  physicsClientId=self.client_id)
        p.setGravity(0, 0, -9.81, physicsClientId=self.client_id)
        p.setTimeStep(self.SIM_DT, physicsClientId=self.client_id)
        p.loadURDF('plane.urdf', physicsClientId=self.client_id)
        # 楼梯加宽以容纳多个机器人
        build_stairs(self.client_id, width=max(2.0, num_robots * y_spacing + 1.0))

        self.num_robots = num_robots
        self.y_spacing = y_spacing
        self.robots = []
        self.leg_joints = {
            'RF': [0, 1, 2], 'LF': [4, 5, 6],
            'RH': [8, 9, 10], 'LH': [12, 13, 14],
        }
        # 机器人左右排开（用 nominal 高度 0.42 让机器狗稳稳着地）
        y0 = -(num_robots - 1) * y_spacing / 2
        for i in range(num_robots):
            y = y0 + i * y_spacing
            r = p.loadURDF('laikago/laikago_toes.urdf',
                           [0, y, 0.42],
                           p.getQuaternionFromEuler([math.pi / 2, 0, math.pi / 2]),
                           physicsClientId=self.client_id)
            self.robots.append(r)
            # 初始关节
            for joint_ids in self.leg_joints.values():
                for jid, target in zip(joint_ids,
                                       [0.0, self.NOMINAL_THIGH, self.NOMINAL_CALF]):
                    p.resetJointState(r, jid, target,
                                      physicsClientId=self.client_id)

        # 稳定
        for _ in range(150):
            for r in self.robots:
                for joint_ids in self.leg_joints.values():
                    for jid, target in zip(joint_ids,
                                           [0.0, self.NOMINAL_THIGH, self.NOMINAL_CALF]):
                        p.setJointMotorControl2(
                            r, jid, p.POSITION_CONTROL,
                            targetPosition=target, force=120,
                            positionGain=1.0, velocityGain=0.5,
                            physicsClientId=self.client_id,
                        )
            p.stepSimulation(physicsClientId=self.client_id)
        self.t = 0.0

    def respawn(self):
        """把所有机器人重置回起点，重新稳定"""
        y0 = -(self.num_robots - 1) * self.y_spacing / 2
        for i, r in enumerate(self.robots):
            y = y0 + i * self.y_spacing
            p.resetBasePositionAndOrientation(
                r, [0, y, 0.42],   # nominal 站立高度
                p.getQuaternionFromEuler([math.pi / 2, 0, math.pi / 2]),
                physicsClientId=self.client_id,
            )
            p.resetBaseVelocity(r, [0, 0, 0], [0, 0, 0],
                                physicsClientId=self.client_id)
            for joint_ids in self.leg_joints.values():
                for jid, target in zip(joint_ids,
                                       [0.0, self.NOMINAL_THIGH, self.NOMINAL_CALF]):
                    p.resetJointState(r, jid, target,
                                      physicsClientId=self.client_id)
        # 充分稳定，让机器狗轻轻坐到地上
        for _ in range(200):
            for r in self.robots:
                for joint_ids in self.leg_joints.values():
                    for jid, target in zip(joint_ids,
                                           [0.0, self.NOMINAL_THIGH, self.NOMINAL_CALF]):
                        p.setJointMotorControl2(
                            r, jid, p.POSITION_CONTROL,
                            targetPosition=target, force=120,
                            positionGain=1.0, velocityGain=0.5,
                            physicsClientId=self.client_id,
                        )
            p.stepSimulation(physicsClientId=self.client_id)
        self.t = 0.0

    def step_all(self, params_list):
        """每个机器人用各自的参数走一步"""
        sub_steps = int(self.CTRL_DT / self.SIM_DT)
        for _ in range(sub_steps):
            self.t += self.SIM_DT
            for r_idx, (robot, params) in enumerate(zip(self.robots, params_list)):
                freq, lift, duty, stance_thigh, stance_calf = params[:5]
                phase_lf, phase_rf, phase_lh, phase_rh = params[5:9]
                forward_bias = params[9]
                leg_phases = {
                    'LF': phase_lf, 'RF': phase_rf,
                    'LH': phase_lh, 'RH': phase_rh,
                }
                for leg_name, joint_ids in self.leg_joints.items():
                    phase = leg_phases[leg_name]
                    phi = (self.t * freq + phase) % 1.0
                    stride = 0.30
                    if phi < duty:
                        s = phi / duty
                        thigh_sway = stride * (s - 0.5)
                        z_lift = 0.0
                    else:
                        s = (phi - duty) / max(1.0 - duty, 1e-3)
                        z_lift = lift * math.sin(math.pi * s)
                        thigh_sway = stride * (0.5 - s)
                    hip = 0.0
                    thigh = stance_thigh + thigh_sway + z_lift * 1.2 + forward_bias
                    calf = stance_calf - z_lift * 1.5

                    for joint_id, target in zip(joint_ids, [hip, thigh, calf]):
                        p.setJointMotorControl2(
                            robot, joint_id, p.POSITION_CONTROL,
                            targetPosition=target, force=200,
                            positionGain=1.2, velocityGain=0.6,
                            physicsClientId=self.client_id,
                        )
            p.stepSimulation(physicsClientId=self.client_id)

    def render(self, width=720, height=400):
        """渲染当前 swarm 状态（电影感视角）"""
        p.configureDebugVisualizer(
            p.COV_ENABLE_SHADOWS, 1, physicsClientId=self.client_id
        )

        # 视角：从机器人左后方斜俯视，能看清楼梯阶梯感和机器狗群
        view = p.computeViewMatrixFromYawPitchRoll(
            cameraTargetPosition=[1.0, 0, 0.25],   # 看机器人和楼梯起点
            distance=4.0,
            yaw=40,                                # 左后方角度
            pitch=-28,                             # 偏俯视
            roll=0,
            upAxisIndex=2,
            physicsClientId=self.client_id,
        )
        proj = p.computeProjectionMatrixFOV(
            45, width / height, 0.1, 20,
            physicsClientId=self.client_id,
        )

        _, _, rgb, _, _ = p.getCameraImage(
            width, height, view, proj,
            lightDirection=[1.5, 1.0, 4.0],        # 斜上方光源
            lightColor=[1.0, 0.95, 0.88],          # 暖色调
            lightAmbientCoeff=0.55,
            lightDiffuseCoeff=0.85,
            lightSpecularCoeff=0.4,
            renderer=p.ER_TINY_RENDERER,
            flags=p.ER_NO_SEGMENTATION_MASK,
            physicsClientId=self.client_id,
        )
        return np.array(rgb, dtype=np.uint8).reshape(height, width, 4)[:, :, :3]

    def get_climbed(self, robot_idx):
        """获取某机器人爬升的高度"""
        pos, _ = p.getBasePositionAndOrientation(self.robots[robot_idx],
                                                  physicsClientId=self.client_id)
        return pos[2], pos[0]

    def close(self):
        if p.isConnected(self.client_id):
            p.disconnect(self.client_id)


# ============================================================
# 4. 策略评估
# ============================================================

def evaluate_policy(env, params, max_steps=300):
    env.reset()
    total_reward = 0.0
    last_dist = 0.0
    last_height = 0.0
    for _ in range(max_steps):
        reward, done, info = env.step(params)
        total_reward += reward
        last_dist = info.get('forward_dist', last_dist)
        last_height = info.get('climbed_height', last_height)
        if done:
            break
    return total_reward, last_dist, last_height


_worker_env = None


def _worker_init():
    global _worker_env
    _worker_env = StairsEnv(gui=False)


def _worker_evaluate(params):
    global _worker_env
    return evaluate_policy(_worker_env, params)


def parallel_evaluate(pool, params_list):
    if pool is None:
        global _worker_env
        if _worker_env is None:
            _worker_env = StairsEnv(gui=False)
        return [evaluate_policy(_worker_env, p) for p in params_list]
    return list(pool.map(_worker_evaluate, params_list))


# ============================================================
# 5. CMA-ES 训练
# ============================================================

def train(generations=50, sigma=0.3, popsize=12, num_envs=1,
          log_file='train_log_stairs.json', record_progress=None):
    try:
        import cma
    except ImportError:
        print("❌ 缺少 cma: pip install cma")
        return None

    # 参数空间（更保守，避免狂跳）
    bounds_low = np.array([1.0, 0.05, 0.5, 0.5, -1.4, 0.0, 0.0, 0.0, 0.0, -0.1])
    bounds_high = np.array([2.2, 0.18, 0.7, 0.85, -0.9, 1.0, 1.0, 1.0, 1.0, 0.3])

    def unnormalize(z):
        z = np.clip(z, -1, 1)
        return bounds_low + (z + 1) / 2 * (bounds_high - bounds_low)

    # 初始：稳定的 Trot 步态
    init_params = np.array([1.4, 0.10, 0.60, 0.65, -1.20, 0.0, 0.5, 0.5, 0.0, 0.1])
    z0 = (init_params - bounds_low) / (bounds_high - bounds_low) * 2 - 1

    es = cma.CMAEvolutionStrategy(
        z0.tolist(), sigma,
        {'popsize': popsize, 'verbose': -9, 'bounds': [[-1] * 10, [1] * 10]}
    )

    pool = None
    if num_envs > 1:
        ctx = mp.get_context('spawn')
        pool = ctx.Pool(num_envs, initializer=_worker_init)
        print(f"🚀 {num_envs} 个 worker 并行训练")

    # 录制 GIF 的多机器人环境（与 popsize 同样数量 → 整代机器狗一起跑）
    rec_env = None
    rec_frames = []
    if record_progress:
        rec_env = SwarmStairsEnv(num_robots=popsize, y_spacing=0.5)
        print(f"📹 录制训练过程（{popsize} 只机器狗同时上）: {record_progress}")

    history = []
    best_params = None
    best_reward = -np.inf

    t_start = time.time()
    record_every = max(1, generations // 25)

    try:
        for gen in range(generations):
            solutions = es.ask()
            params_list = [unnormalize(np.array(z)) for z in solutions]
            results = parallel_evaluate(pool, params_list)
            rewards = [-r for r, _, _ in results]
            dists = [d for _, d, _ in results]
            heights = [h for _, _, h in results]
            es.tell(solutions, rewards)

            best_idx = int(np.argmin(rewards))
            gen_best_reward = -rewards[best_idx]
            gen_best_dist = dists[best_idx]
            gen_best_height = heights[best_idx]
            if gen_best_reward > best_reward:
                best_reward = gen_best_reward
                best_params = params_list[best_idx]

            history.append({
                'gen': gen,
                'best_reward': float(gen_best_reward),
                'best_dist': float(gen_best_dist),
                'best_height': float(gen_best_height),
                'mean_reward': float(-np.mean(rewards)),
                'mean_dist': float(np.mean(dists)),
            })
            elapsed = time.time() - t_start
            print(f"Gen {gen+1:3d}/{generations} | "
                  f"best dist = {gen_best_dist:5.2f}m  "
                  f"best climbed = {gen_best_height:.2f}m  "
                  f"reward = {gen_best_reward:6.2f}  "
                  f"t = {elapsed:.0f}s")

            # 录 GIF：每代用全部 popsize 个候选让所有机器狗同时跑
            # （即使训练失败的也保留 → 学生能看到一群里有的摔、有的爬、有的进步）
            if rec_env is not None and (gen % record_every == 0 or gen == generations - 1):
                # 重新生成一群机器狗（重置位置和姿态）
                rec_env.respawn()
                # 跑 80 步（约 1.6 秒物理时间）让动作充分展开
                num_capture = 4  # 每代采 4 帧形成小动画
                steps_per_capture = 20
                for capture_step in range(num_capture):
                    for _ in range(steps_per_capture):
                        rec_env.step_all(params_list)
                    frame = rec_env.render()
                    rec_frames.append(_add_label(frame, gen + 1, gen_best_height,
                                                  gen_best_dist, popsize))
    finally:
        if pool is not None:
            pool.close()
            pool.join()
        if rec_env is not None:
            for _ in range(15):
                rec_frames.append(rec_frames[-1])
            if rec_frames:
                import imageio.v2 as imageio
                imageio.mimsave(record_progress, rec_frames, fps=8, loop=0)
                print(f"📹 训练 GIF 保存: {record_progress} ({len(rec_frames)} 帧)")
            rec_env.close()

    with open(log_file, 'w') as f:
        json.dump({
            'history': history,
            'best_params': best_params.tolist() if best_params is not None else None,
            'best_reward': float(best_reward),
            'config': {'generations': generations, 'popsize': popsize,
                       'num_envs': num_envs, 'sigma': sigma},
        }, f, indent=2)
    print(f"💾 日志: {log_file}")

    return best_params, history


def _add_label(frame, gen, climbed, dist, popsize=None):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
        font_m = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
        font_s = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
    except OSError:
        font = font_m = font_s = ImageFont.load_default()
    h, w = frame.shape[:2]
    # 顶部半透明白底
    draw.rectangle([(0, 0), (w, 38)], fill=(255, 255, 255, 235))
    draw.text((12, 7), f"Gen {gen}", fill=(20, 30, 80), font=font)
    if popsize:
        draw.text((105, 13), f"({popsize} robots evolving)",
                  fill=(100, 100, 110), font=font_s)
    # 右侧绩效
    text = f"best climb: {climbed:.2f}m   forward: {dist:.2f}m"
    draw.text((w - 320, 12), text, fill=(60, 25, 25), font=font_m)
    return np.array(img)


# ============================================================
# 6. Demo（一群机器狗）
# ============================================================

def demo_swarm(params, num_robots=9, record_path=None):
    """让 N 个机器人用同一组参数（或加点噪声）爬楼梯，可录 GIF"""
    env = SwarmStairsEnv(num_robots=num_robots)
    # 给每个机器人加点小噪声让动作不完全同步（更有趣）
    rng = np.random.default_rng(42)
    params_list = []
    for i in range(num_robots):
        noise = rng.normal(0, 0.05, size=10)
        noise[5:9] = rng.normal(0, 0.1, size=4)  # 相位噪声大点
        p_i = np.array(params) + noise
        params_list.append(p_i)

    frames = []
    print(f"🎬 演示 {num_robots} 只机器狗爬楼梯...")
    for step in range(200):
        env.step_all(params_list)
        if record_path:
            frames.append(env.render())
        if step % 50 == 0:
            heights = [env.get_climbed(i)[0] for i in range(num_robots)]
            print(f"  step {step}: 机器狗高度 {np.mean(heights):.2f}m (max {max(heights):.2f}m)")

    if record_path and frames:
        import imageio.v2 as imageio
        imageio.mimsave(record_path, frames, fps=25, loop=0)
        print(f"📹 演示 GIF: {record_path}")
    env.close()


# ============================================================
# 7. CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__)
    parser.add_argument('mode', choices=['train', 'demo'])
    parser.add_argument('--generations', type=int, default=50)
    parser.add_argument('--popsize', type=int, default=12)
    parser.add_argument('--num_envs', type=int, default=1,
                        help='并行 worker 数（建议 = CPU 核数）')
    parser.add_argument('--num_robots', type=int, default=9,
                        help='演示时的机器狗数量')
    parser.add_argument('--gpu', action='store_true',
                        help='GPU 加速（PyBullet 不支持，提示替代方案）')
    parser.add_argument('--params_file', default='train_log_stairs.json')
    parser.add_argument('--record', help='演示 GIF 输出路径')
    parser.add_argument('--record_progress', help='训练过程 GIF 路径')
    args = parser.parse_args()

    if args.gpu:
        print("⚠️  PyBullet 不支持 GPU。要真正用 GPU 大规模并行：")
        print("    - NVIDIA Isaac Lab / Isaac Gym (需 RTX 显卡)")
        print("    - MuJoCo MJX 或 Brax (JAX, 支持 GPU/TPU)")
        print("    本示例用 CPU 多进程 --num_envs 已足够\n")

    if args.mode == 'train':
        best_params, history = train(
            generations=args.generations,
            popsize=args.popsize,
            num_envs=args.num_envs,
            log_file=args.params_file,
            record_progress=args.record_progress,
        )
        if best_params is not None:
            print(f"\n✅ 训练完成！climbed {history[-1]['best_height']:.2f}m, "
                  f"forward {history[-1]['best_dist']:.2f}m")

    elif args.mode == 'demo':
        if not os.path.exists(args.params_file):
            print(f"❌ 参数文件不存在: {args.params_file}")
            print(f"   先训练: python {__file__} train")
            return
        with open(args.params_file) as f:
            data = json.load(f)
        if not data.get('best_params'):
            print("❌ 没有 best_params")
            return
        params = np.array(data['best_params'])
        demo_swarm(params, num_robots=args.num_robots, record_path=args.record)


if __name__ == '__main__':
    main()

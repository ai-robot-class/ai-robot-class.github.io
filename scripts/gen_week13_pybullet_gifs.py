"""
用 PyBullet 仿真生成 Week 13 步态动画

输出（headless 渲染，无需显卡，CPU 可跑）：
- images/week13/pybullet_trot.gif - Trot 步态
- images/week13/pybullet_walk.gif - Walk 步态
- images/week13/pybullet_bound.gif - Bound 兔跳步态
- images/week13/pybullet_compare.gif - 三种步态并排对比
"""
import os
import math
import numpy as np
import pybullet as p
import pybullet_data
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = '/home/robot/areal2025.github.io/images/week13'
os.makedirs(OUT_DIR, exist_ok=True)

# 渲染参数
WIDTH = 480
HEIGHT = 320
FPS = 20
SECONDS = 4  # 每段动画时长


# ============================================================
# Trot/Walk/Bound 步态参数（相位偏移）
# 一个周期 [0, 1]，每条腿 [0, duty_factor] 段为支撑相，其余为摆动相
# 参考真实四足生物步态
# ============================================================
GAITS = {
    'walk': {
        # 静态步态：4 拍轮流，duty 0.75
        'phase': {'LF': 0.0,  'RF': 0.5, 'LH': 0.25, 'RH': 0.75},
        'duty': 0.75,
        'freq': 1.0,
        'step_height': 0.06,
        'step_length': 0.07,
        'desc': 'Walk',
    },
    'trot': {
        # 对角腿同相
        'phase': {'LF': 0.0, 'RF': 0.5, 'LH': 0.5, 'RH': 0.0},
        'duty': 0.5,
        'freq': 1.8,
        'step_height': 0.08,
        'step_length': 0.10,
        'desc': 'Trot',
    },
    'bound': {
        # 前后腿同相
        'phase': {'LF': 0.0, 'RF': 0.0, 'LH': 0.5, 'RH': 0.5},
        'duty': 0.45,
        'freq': 2.0,
        'step_height': 0.10,
        'step_length': 0.12,
        'desc': 'Bound',
    },
}


def setup_simulation():
    """初始化 PyBullet 仿真（headless 模式）"""
    if p.isConnected():
        p.disconnect()
    p.connect(p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.81)
    p.setTimeStep(1.0 / 240.0)

    plane = p.loadURDF('plane.urdf')

    # 加载 Laikago。它的默认朝向需要绕 X 轴旋转 -π/2 才能"狗式"站立
    start_pos = [0, 0, 0.55]
    start_orn = p.getQuaternionFromEuler([math.pi / 2, 0, math.pi / 2])
    robot = p.loadURDF('laikago/laikago_toes.urdf', start_pos, start_orn,
                       useFixedBase=False)

    return robot


def get_leg_joints(robot):
    """Laikago 关节映射（基于实际 URDF：FR=RF, FL=LF, RR=RH, RL=LH）

    每条腿 3 个 revolute 关节：
    - hip_motor_2_chassis: 髋关节（左右摆）
    - upper_leg_2_hip:    大腿（前后摆）
    - lower_leg_2_upper:  小腿（弯曲）
    """
    return {
        'RF': [0, 1, 2],     # Front-Right
        'LF': [4, 5, 6],     # Front-Left
        'RH': [8, 9, 10],    # Rear-Right
        'LH': [12, 13, 14],  # Rear-Left
    }


def leg_ik_simple(phi, duty, step_height, step_length, is_front):
    """简化足端轨迹 → 关节角度。

    Laikago URDF 默认姿态：
    - thigh 静止约 0.65 rad
    - calf  静止约 -1.2 rad (弯曲)
    """
    if phi < duty:
        # 支撑相：腿向后推
        s = phi / duty
        foot_x = step_length * (0.5 - s)
        foot_z = 0.0
    else:
        # 摆动相：抬腿向前
        s = (phi - duty) / max(1.0 - duty, 1e-3)
        foot_x = step_length * (s - 0.5)
        foot_z = step_height * math.sin(math.pi * s)

    # Laikago 默认蹲姿
    base_hip = 0.0
    base_thigh = 0.65
    base_calf = -1.20

    # 通过 foot_z 调整 thigh/calf（抬高 = thigh 收缩，calf 弯曲更紧）
    delta_z = foot_z / max(step_height, 1e-3)  # 0~1
    # 通过 foot_x 调整 thigh 摆动
    delta_x = foot_x / max(step_length, 1e-3) * 0.4

    # 前腿和后腿摆动方向相反更稳
    direction = 1.0 if is_front else -1.0

    hip = base_hip
    thigh = base_thigh + delta_x * direction - delta_z * 0.3
    calf = base_calf + delta_z * 0.6

    return hip, thigh, calf


def run_gait(gait_name, robot, leg_joints, n_frames):
    """跑一段步态仿真，返回每帧的渲染图像"""
    g = GAITS[gait_name]
    images = []
    t = 0.0
    dt = 1.0 / FPS
    sub_steps = max(1, int(240 / FPS))  # 仿真比渲染快

    # 初始平稳一会儿
    for _ in range(120):
        p.stepSimulation()

    for frame in range(n_frames):
        t_step = (t * g['freq']) % 1.0

        for leg_name, joint_ids in leg_joints.items():
            phase = g['phase'][leg_name]
            phi = (t * g['freq'] + phase) % 1.0
            is_front = leg_name in ('LF', 'RF')
            hip, thigh, calf = leg_ik_simple(
                phi, g['duty'], g['step_height'], g['step_length'], is_front
            )
            for joint_id, target in zip(joint_ids, [hip, thigh, calf]):
                p.setJointMotorControl2(
                    robot, joint_id, p.POSITION_CONTROL,
                    targetPosition=target, force=80,
                    positionGain=0.6, velocityGain=0.5,
                )

        for _ in range(sub_steps):
            p.stepSimulation()

        img = render_frame(robot, gait_name, t_step, g['desc'])
        images.append(img)
        t += dt

    return images


def render_frame(robot, gait_name, phase, label_text):
    """渲染当前仿真状态为 numpy 图像"""
    # 摄像头跟随机器人
    pos, _ = p.getBasePositionAndOrientation(robot)
    cam_target = [pos[0], pos[1], 0.3]
    view = p.computeViewMatrixFromYawPitchRoll(
        cameraTargetPosition=cam_target,
        distance=1.5, yaw=45, pitch=-20, roll=0, upAxisIndex=2,
    )
    proj = p.computeProjectionMatrixFOV(fov=50, aspect=WIDTH / HEIGHT,
                                         nearVal=0.1, farVal=10.0)

    _, _, rgb, _, _ = p.getCameraImage(
        WIDTH, HEIGHT, view, proj,
        renderer=p.ER_TINY_RENDERER,  # CPU 渲染
        flags=p.ER_NO_SEGMENTATION_MASK,
    )
    rgb = np.array(rgb, dtype=np.uint8).reshape(HEIGHT, WIDTH, 4)[:, :, :3]

    # 在图像上添加文字
    img = Image.fromarray(rgb)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    except OSError:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 步态名（顶部）
    draw.rectangle([(0, 0), (WIDTH, 35)], fill=(255, 255, 255, 220))
    draw.text((10, 6), f"Gait: {label_text}", fill=(30, 30, 80), font=font)

    # 相位条（底部）
    bar_y = HEIGHT - 25
    draw.rectangle([(0, bar_y - 5), (WIDTH, HEIGHT)], fill=(255, 255, 255, 220))
    draw.text((10, bar_y - 3), f"Cycle: {phase:.2f}", fill=(80, 30, 30), font=font_small)
    # 进度条
    bar_x0 = 110
    bar_x1 = WIDTH - 20
    draw.rectangle([(bar_x0, bar_y), (bar_x1, bar_y + 12)], outline=(80, 80, 80), width=1)
    fill_w = max(2, int((bar_x1 - bar_x0) * max(phase, 0.01)))
    draw.rectangle([(bar_x0 + 1, bar_y + 1),
                    (bar_x0 + fill_w + 1, bar_y + 11)], fill=(50, 150, 50))

    return np.array(img)


def save_gif(images, filename, fps=FPS):
    """保存为 GIF"""
    out_path = os.path.join(OUT_DIR, filename)
    imageio.mimsave(out_path, images, fps=fps, loop=0)
    size_kb = os.path.getsize(out_path) / 1024
    print(f"  ✅ {filename}: {size_kb:.1f} KB ({len(images)} 帧)")
    return out_path


def main():
    print(f"📁 输出: {OUT_DIR}\n")
    n_frames = SECONDS * FPS

    print(f"🎬 渲染 3 种步态（每段 {SECONDS}s, {n_frames} 帧）...\n")

    # 三种步态各自生成
    all_frames = {}
    for gait_name in ['walk', 'trot', 'bound']:
        print(f"▶ {gait_name.upper()} 步态...")
        robot = setup_simulation()
        leg_joints = get_leg_joints(robot)
        frames = run_gait(gait_name, robot, leg_joints, n_frames)
        all_frames[gait_name] = frames
        save_gif(frames, f'pybullet_{gait_name}.gif')

    # 三步态横向拼接对比
    print("\n▶ 生成三步态对比 GIF...")
    h, w = HEIGHT, WIDTH
    combined = []
    for i in range(n_frames):
        canvas = Image.new('RGB', (w * 3 + 20, h + 20), color=(245, 245, 250))
        for j, gait_name in enumerate(['walk', 'trot', 'bound']):
            frame = Image.fromarray(all_frames[gait_name][i])
            canvas.paste(frame, (j * (w + 10) + 10, 10))
        combined.append(np.array(canvas))
    save_gif(combined, 'pybullet_compare.gif', fps=FPS)

    print("\n✨ 全部完成！")

    p.disconnect()


if __name__ == '__main__':
    main()

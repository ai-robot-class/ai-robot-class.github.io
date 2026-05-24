"""
Week 9 数学动画生成器
=========================
生成 week9.md 中所有数学概念的高质量教学动画 GIF。

输出目录: images/week9/

运行方法:
    python3 scripts/gen_week9_animations.py [animation_name ...]
    python3 scripts/gen_week9_animations.py all          # 生成全部
    python3 scripts/gen_week9_animations.py --list        # 列出所有动画

依赖: numpy, matplotlib, pillow, imageio
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

# ---- 修复 user site 的 mpl_toolkits 被系统包屏蔽的问题 ----
# 系统 /usr/lib/python3/dist-packages/mpl_toolkits 与新版 matplotlib 不兼容
import site
_user_site = site.getusersitepackages()
_user_mp3d = os.path.join(_user_site, "mpl_toolkits")
if os.path.exists(_user_mp3d):
    import mpl_toolkits  # noqa: F401（先 import 系统版，再覆盖路径）
    import mpl_toolkits as _mp
    _mp.__path__.insert(0, _user_mp3d)

import imageio.v2 as imageio
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch, Rectangle, Circle
from matplotlib.lines import Line2D
# matplotlib >= 3.2 自动注册 3d 投影，不需要 import Axes3D（避免与系统旧包冲突）

OUT_DIR = Path(__file__).resolve().parent.parent / "images" / "week9"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- 中文字体注册（兼容只有用户级字体的环境）----
_USER_FONTS = Path.home() / ".fonts"
if _USER_FONTS.exists():
    for f in _USER_FONTS.iterdir():
        if f.suffix.lower() in (".otf", ".ttf"):
            try:
                fm.fontManager.addfont(str(f))
            except Exception:
                pass

# 统一配色（柔和、可读性强）
COLORS = {
    "blue": "#1F77B4",
    "orange": "#FF7F0E",
    "green": "#2CA02C",
    "red": "#D62728",
    "purple": "#9467BD",
    "brown": "#8C564B",
    "pink": "#E377C2",
    "gray": "#7F7F7F",
    "olive": "#BCBD22",
    "cyan": "#17BECF",
}

plt.rcParams.update({
    "figure.dpi": 100,
    "savefig.dpi": 100,
    "font.family": ["Noto Sans CJK SC", "DejaVu Sans"],
    "font.sans-serif": ["Noto Sans CJK SC", "DejaVu Sans"],
    "font.monospace": ["Noto Sans CJK SC", "DejaVu Sans Mono"],
    "axes.unicode_minus": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


# ============================================================
# 工具函数
# ============================================================
def fig_to_frame(fig):
    """matplotlib figure → numpy array (uint8 RGB)。"""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    buf.seek(0)
    img = imageio.imread(buf)
    if img.shape[2] == 4:
        img = img[..., :3]
    return img


def save_gif(frames, name, fps=20, optimize=True):
    """保存帧序列为 GIF。"""
    path = OUT_DIR / name
    duration = max(0.04, 1.0 / fps)
    imageio.mimsave(
        path,
        frames,
        format="GIF",
        duration=duration,
        loop=0,
    )
    size_kb = path.stat().st_size / 1024
    print(f"  ✅ {name}  ({len(frames)} frames, {size_kb:.0f} KB)")
    return path


def skew(omega):
    """3D 向量 → 反对称矩阵 [ω]×。"""
    wx, wy, wz = omega
    return np.array([[0, -wz, wy], [wz, 0, -wx], [-wy, wx, 0]])


def rodrigues(omega):
    """so(3) → SO(3)。"""
    theta = np.linalg.norm(omega)
    if theta < 1e-10:
        return np.eye(3)
    K = skew(omega / theta)
    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)


# ============================================================
# 1. 向量运算（加法、点积、叉积）
# ============================================================
def gen_vector_ops():
    """演示向量加法、点积、叉积的几何意义。"""
    print("→ vector_ops.gif")
    a = np.array([3.0, 1.0])
    b = np.array([1.0, 2.5])

    frames = []
    n = 60

    # 阶段1：显示两个向量
    for i in range(n // 3):
        fig, ax = plt.subplots(figsize=(7, 6))
        s = i / (n // 3 - 1)
        ax.annotate("", xy=a * s, xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=COLORS["blue"], lw=3))
        ax.text(a[0] * 0.5 + 0.1, a[1] * 0.5 + 0.2, "a", color=COLORS["blue"],
                fontsize=18, fontweight="bold")
        if s > 0.5:
            ax.annotate("", xy=b * (s - 0.5) * 2, xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=COLORS["orange"], lw=3))
            ax.text(b[0] * 0.3, b[1] * 0.5 + 0.2, "b", color=COLORS["orange"],
                    fontsize=18, fontweight="bold")
        ax.set_xlim(-1, 5)
        ax.set_ylim(-1, 5)
        ax.set_aspect("equal")
        ax.set_title("向量加法 / 点积 / 叉积  — 几何意义", fontsize=14)
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    # 阶段2：向量加法 - 平行四边形法则
    for i in range(n // 3):
        fig, ax = plt.subplots(figsize=(7, 6))
        s = (i + 1) / (n // 3)
        # 原始向量
        ax.annotate("", xy=a, xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=COLORS["blue"], lw=3))
        ax.annotate("", xy=b, xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=COLORS["orange"], lw=3))
        # 平行四边形虚线
        ax.plot([a[0], a[0] + b[0] * s], [a[1], a[1] + b[1] * s],
                "--", color=COLORS["orange"], alpha=0.5, lw=1.5)
        ax.plot([b[0], b[0] + a[0] * s], [b[1], b[1] + a[1] * s],
                "--", color=COLORS["blue"], alpha=0.5, lw=1.5)
        # 合成向量 a+b
        ax.annotate("", xy=(a + b) * s, xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=COLORS["green"], lw=3.5))
        ax.text(a[0] * 0.5 + 0.1, a[1] * 0.5 + 0.2, "a", color=COLORS["blue"],
                fontsize=18, fontweight="bold")
        ax.text(b[0] * 0.3, b[1] * 0.5 + 0.2, "b", color=COLORS["orange"],
                fontsize=18, fontweight="bold")
        if s > 0.3:
            ax.text((a + b)[0] * 0.55, (a + b)[1] * 0.55 - 0.4, "a+b",
                    color=COLORS["green"], fontsize=18, fontweight="bold")
        ax.set_xlim(-1, 5)
        ax.set_ylim(-1, 5)
        ax.set_aspect("equal")
        ax.set_title("向量加法：平行四边形法则", fontsize=14)
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    # 阶段3：点积 - 投影
    for i in range(n // 3):
        fig, ax = plt.subplots(figsize=(7, 6))
        s = (i + 1) / (n // 3)
        # a, b
        ax.annotate("", xy=a, xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=COLORS["blue"], lw=3))
        ax.annotate("", xy=b, xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=COLORS["orange"], lw=3))
        ax.text(a[0] * 0.5 + 0.1, a[1] * 0.5 + 0.2, "a", color=COLORS["blue"],
                fontsize=18, fontweight="bold")
        ax.text(b[0] * 0.3, b[1] * 0.5 + 0.2, "b", color=COLORS["orange"],
                fontsize=18, fontweight="bold")
        # b 在 a 方向的投影
        proj_len = np.dot(b, a) / np.linalg.norm(a)
        proj = (proj_len / np.linalg.norm(a)) * a * s
        ax.annotate("", xy=proj, xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=COLORS["red"], lw=4))
        # 虚线从 b 到投影
        ax.plot([b[0], proj[0]], [b[1], proj[1]], ":", color=COLORS["gray"], lw=1.5)
        cos_theta = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        ax.text(0.5, 4.3, f"a · b = |a||b|cos(θ) = {np.dot(a, b):.2f}",
                fontsize=13, bbox=dict(boxstyle="round", facecolor="lightyellow"))
        ax.text(0.5, 3.8, f"cos(θ) = {cos_theta:.3f}, θ ≈ {np.degrees(np.arccos(cos_theta)):.1f}°",
                fontsize=12, color=COLORS["red"])
        ax.set_xlim(-1, 5)
        ax.set_ylim(-1, 5)
        ax.set_aspect("equal")
        ax.set_title("点积：b 在 a 方向的投影长度 × |a|", fontsize=14)
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames + frames[-5:] * 6, "vector_ops.gif", fps=20)


# ============================================================
# 2. 2D 旋转矩阵
# ============================================================
def gen_rotation_2d():
    """2D 旋转矩阵的连续作用动画。"""
    print("→ rotation_2d.gif")
    # 一个有方向的"L 形"图形
    shape = np.array([
        [0, 0], [1.5, 0], [1.5, 0.3], [0.3, 0.3], [0.3, 1.2], [0, 1.2], [0, 0]
    ]).T

    frames = []
    n_frames = 90
    for i in range(n_frames):
        theta = 2 * np.pi * i / n_frames
        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])
        rotated = R @ shape

        fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                                 gridspec_kw={"width_ratios": [1.5, 1]})
        ax = axes[0]
        # 原始（虚线）
        ax.plot(shape[0], shape[1], "--", color=COLORS["gray"], lw=1.5,
                label="原始位置")
        # 旋转后
        ax.fill(rotated[0], rotated[1], color=COLORS["blue"], alpha=0.3)
        ax.plot(rotated[0], rotated[1], color=COLORS["blue"], lw=2.5,
                label=f"旋转后 (θ={np.degrees(theta):.0f}°)")
        # 坐标轴
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
        # 角度弧
        if theta > 0.05:
            arc = Arc((0, 0), 0.8, 0.8, angle=0, theta1=0,
                      theta2=np.degrees(theta), color=COLORS["red"], lw=2)
            ax.add_patch(arc)
            ax.text(0.5 * np.cos(theta / 2), 0.5 * np.sin(theta / 2),
                    "θ", color=COLORS["red"], fontsize=14, fontweight="bold")

        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal")
        ax.set_title("2D 旋转：每个点都被旋转矩阵 R(θ) 作用", fontsize=14)
        ax.legend(loc="upper right", fontsize=10)

        # 右侧显示矩阵
        ax2 = axes[1]
        ax2.axis("off")
        ax2.text(0.5, 0.85, "R(θ) =", fontsize=20, ha="center")
        mat_str = (f"⎡ {np.cos(theta):+.2f}  {-np.sin(theta):+.2f} ⎤\n"
                   f"⎣ {np.sin(theta):+.2f}  {np.cos(theta):+.2f} ⎦")
        ax2.text(0.5, 0.55, mat_str, fontsize=24, ha="center",
                 family="monospace",
                 bbox=dict(boxstyle="round", facecolor="lightyellow",
                           edgecolor=COLORS["blue"], lw=2))
        ax2.text(0.5, 0.18, "性质：R·Rᵀ = I,  det(R) = +1\n这就是李群 SO(2)",
                 fontsize=12, ha="center", style="italic")

        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames, "rotation_2d.gif", fps=20)


# ============================================================
# 3. 齐次变换矩阵
# ============================================================
def gen_homogeneous_transform():
    """齐次变换：旋转 + 平移 = 4×4 矩阵的几何意义。"""
    print("→ homogeneous_transform.gif")
    shape = np.array([
        [0, 0, 1], [1, 0, 1], [1, 0.3, 1], [0.2, 0.3, 1],
        [0.2, 0.8, 1], [0, 0.8, 1], [0, 0, 1]
    ]).T

    frames = []
    n = 80
    for i in range(n):
        t = i / (n - 1)
        # 先旋转再平移
        theta = (np.pi / 3) * t      # 60°
        tx, ty = 2.5 * t, 1.5 * t

        R = np.array([[np.cos(theta), -np.sin(theta), 0],
                      [np.sin(theta), np.cos(theta), 0],
                      [0, 0, 1]])
        T = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]])
        H = T @ R                    # 齐次变换矩阵
        transformed = H @ shape

        fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                                 gridspec_kw={"width_ratios": [1.5, 1]})
        ax = axes[0]
        ax.fill(shape[0], shape[1], color=COLORS["gray"], alpha=0.15)
        ax.plot(shape[0], shape[1], "--", color=COLORS["gray"], lw=1.5,
                label="原始位置")
        ax.fill(transformed[0], transformed[1], color=COLORS["green"], alpha=0.4)
        ax.plot(transformed[0], transformed[1], color=COLORS["green"], lw=2.5,
                label="变换后")

        # 标出新原点
        ax.plot(tx, ty, "o", color=COLORS["red"], markersize=10)
        # 平移箭头
        if tx > 0.05:
            ax.annotate("", xy=(tx, ty), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->",
                                        color=COLORS["red"], lw=2.5, alpha=0.7))

        ax.set_xlim(-1, 5)
        ax.set_ylim(-1, 4)
        ax.set_aspect("equal")
        ax.set_title("齐次变换 T = 平移 × 旋转  ⇒  T·p̃", fontsize=14)
        ax.legend(loc="upper left", fontsize=11)
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)

        ax2 = axes[1]
        ax2.axis("off")
        ax2.text(0.5, 0.9, "T (4×4 齐次矩阵) =", fontsize=14, ha="center")
        mat_str = (
            f"⎡ {np.cos(theta):+.2f}  {-np.sin(theta):+.2f}   0  {tx:+.2f} ⎤\n"
            f"⎢ {np.sin(theta):+.2f}   {np.cos(theta):+.2f}   0  {ty:+.2f} ⎥\n"
            f"⎢   0.00   0.00  1.00   0.00 ⎥\n"
            f"⎣   0.00   0.00  0.00   1.00 ⎦"
        )
        ax2.text(0.5, 0.5, mat_str, fontsize=14, ha="center", family="monospace",
                 bbox=dict(boxstyle="round", facecolor="lightyellow",
                           edgecolor=COLORS["green"], lw=2))
        ax2.text(0.5, 0.12,
                 f"T = [R  t]    R: 旋转 θ={np.degrees(theta):.0f}°\n    [0  1]    t: 平移 ({tx:.1f}, {ty:.1f})",
                 fontsize=11, ha="center", family="monospace")
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames + frames[-1:] * 10, "homogeneous_transform.gif", fps=20)


# ============================================================
# 4. 欧拉角万向锁
# ============================================================
def gen_gimbal_lock():
    """演示 pitch=90° 时两个旋转环重合，自由度丢失。"""
    print("→ gimbal_lock.gif")

    def gimbal_ring(theta_axis_angle, ring_axis, color, ax, radius=1.0, lw=3):
        """绘制一个旋转环（圆）。
        theta_axis_angle: 该环已被前面的旋转转动了多少度
        ring_axis: 该环最初是绕哪个轴 ('x', 'y', 'z')
        """
        phi = np.linspace(0, 2 * np.pi, 60)
        if ring_axis == "z":
            pts = np.array([radius * np.cos(phi), radius * np.sin(phi), np.zeros_like(phi)])
        elif ring_axis == "y":
            pts = np.array([radius * np.cos(phi), np.zeros_like(phi), radius * np.sin(phi)])
        else:
            pts = np.array([np.zeros_like(phi), radius * np.cos(phi), radius * np.sin(phi)])
        pts = theta_axis_angle @ pts
        ax.plot(pts[0], pts[1], pts[2], color=color, lw=lw)
        return pts

    frames = []
    n = 60
    for i in range(n):
        t = i / (n - 1)
        # 阶段：yaw 0→90，pitch 0→90 同步
        yaw = np.radians(30) * (1 - abs(t - 0.5) * 2)        # 在中间到 0
        pitch = np.radians(90) * t                            # 0→90
        roll = np.radians(60) * (1 - abs(t - 0.5) * 2)        # 中间为 0

        Rz = rodrigues(np.array([0, 0, yaw]))
        Rxy = rodrigues(np.array([0, pitch, 0]))             # 绕被 yaw 旋转后的 Y' 轴

        # 简化：先 Z，再 Y'（已被 Z 转过），再 X''（已被两次转过）
        R_total = Rz @ Rxy

        fig = plt.figure(figsize=(13, 6))
        ax = fig.add_subplot(121, projection="3d")
        # 外环（绕 Z 轴，红色）
        gimbal_ring(np.eye(3), "z", COLORS["red"], ax, radius=1.3, lw=4)
        # 中环（被外环旋转，绕新 Y'，绿色）
        gimbal_ring(Rz, "y", COLORS["green"], ax, radius=1.05, lw=3.5)
        # 内环（被两次旋转，绕新 X''，蓝色）
        gimbal_ring(R_total, "x", COLORS["blue"], ax, radius=0.8, lw=3)

        # 标注物体（小箭头表示朝向）
        body = R_total @ np.array([0.5, 0, 0])
        ax.quiver(0, 0, 0, body[0], body[1], body[2],
                  color=COLORS["orange"], lw=4, arrow_length_ratio=0.2)

        ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_zlim(-1.5, 1.5)
        ax.set_box_aspect([1, 1, 1])
        title = f"欧拉角 (yaw={np.degrees(yaw):.0f}°, pitch={np.degrees(pitch):.0f}°)"
        if abs(pitch - np.pi / 2) < np.radians(5):
            title += "  ⚠️ 万向锁！"
        ax.set_title(title, fontsize=13)

        # 右侧：可用 DOF
        ax2 = fig.add_subplot(122)
        ax2.axis("off")
        is_locked = abs(pitch - np.pi / 2) < np.radians(10)
        col = COLORS["red"] if is_locked else COLORS["green"]
        status = "❌ 自由度丢失 1\n（yaw 与 roll 轴重合）" if is_locked else "✅ 3 DOF 正常"
        ax2.text(0.5, 0.85, "欧拉角 (ZYX)", fontsize=18, ha="center", fontweight="bold")
        ax2.text(0.1, 0.65, f"yaw   (绕 Z)  = {np.degrees(yaw):+6.1f}°",
                 fontsize=14, color=COLORS["red"], family="monospace")
        ax2.text(0.1, 0.55, f"pitch (绕 Y') = {np.degrees(pitch):+6.1f}°",
                 fontsize=14, color=COLORS["green"], family="monospace")
        ax2.text(0.1, 0.45, f"roll  (绕 X'')= {np.degrees(roll):+6.1f}°",
                 fontsize=14, color=COLORS["blue"], family="monospace")
        ax2.text(0.5, 0.22, status, fontsize=18, ha="center", color=col,
                 fontweight="bold",
                 bbox=dict(boxstyle="round", facecolor="lightyellow"
                                          if not is_locked else "mistyrose",
                           edgecolor=col, lw=2))
        if is_locked:
            ax2.text(0.5, 0.05,
                     "→ 必须用四元数 / 李代数避开此问题",
                     fontsize=11, ha="center", style="italic")
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    # 正反播放但不重复完整序列，保持简洁
    save_gif(frames + frames[::-2], "gimbal_lock.gif", fps=15)


# ============================================================
# 5. Rodrigues 公式：so(3) → SO(3)
# ============================================================
def gen_rodrigues_axis_angle():
    """单一旋转轴 + 角度逐渐增大的 3D 旋转动画。"""
    print("→ rodrigues_axis_angle.gif")
    # 旋转轴
    axis = np.array([1, 1, 0.5])
    axis = axis / np.linalg.norm(axis)

    # 待旋转的"机器人"——简单立方体
    cube = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
    ]).T - 0.5
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]

    frames = []
    n = 80
    for i in range(n):
        theta = 2 * np.pi * i / (n - 1)
        omega = axis * theta
        R = rodrigues(omega)
        rotated = R @ cube

        fig = plt.figure(figsize=(13, 6))
        ax = fig.add_subplot(121, projection="3d")

        # 旋转轴（绿色长箭头）
        ax.quiver(-axis[0] * 1.5, -axis[1] * 1.5, -axis[2] * 1.5,
                  axis[0] * 3, axis[1] * 3, axis[2] * 3,
                  color=COLORS["green"], lw=2.5, arrow_length_ratio=0.05, alpha=0.7)

        # 原始立方体（灰虚线）
        for (a, b) in edges:
            ax.plot([cube[0, a], cube[0, b]], [cube[1, a], cube[1, b]],
                    [cube[2, a], cube[2, b]], "--", color=COLORS["gray"],
                    alpha=0.3, lw=1)
        # 旋转后（蓝色实线）
        for (a, b) in edges:
            ax.plot([rotated[0, a], rotated[0, b]],
                    [rotated[1, a], rotated[1, b]],
                    [rotated[2, a], rotated[2, b]],
                    color=COLORS["blue"], lw=2.5)

        ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_zlim(-1.5, 1.5)
        ax.set_box_aspect([1, 1, 1])
        ax.set_title(f"Rodrigues 公式：R = exp([ω]×)\nω = {axis.round(2)} · {np.degrees(theta):.0f}°",
                     fontsize=12)

        # 右侧公式 + 数值
        ax2 = fig.add_subplot(122)
        ax2.axis("off")
        ax2.text(0.5, 0.92, "so(3) → SO(3) 指数映射", fontsize=15,
                 ha="center", fontweight="bold")
        ax2.text(0.5, 0.78,
                 "R = I + sin(θ)/θ · [ω]×\n       + (1-cos(θ))/θ² · [ω]×²",
                 fontsize=14, ha="center", family="monospace",
                 bbox=dict(boxstyle="round", facecolor="lightyellow",
                           edgecolor=COLORS["blue"], lw=2))
        ax2.text(0.5, 0.55, "数值实例", fontsize=13, ha="center", fontweight="bold")
        ax2.text(0.5, 0.40,
                 f"轴 k = ({axis[0]:.2f}, {axis[1]:.2f}, {axis[2]:.2f})\n"
                 f"角 θ = {np.degrees(theta):.1f}°\n"
                 f"|ω| = {theta:.3f} rad",
                 fontsize=12, ha="center", family="monospace")
        # 旋转矩阵
        mat_str = (f"R = ⎡ {R[0, 0]:+.2f}  {R[0, 1]:+.2f}  {R[0, 2]:+.2f} ⎤\n"
                   f"    ⎢ {R[1, 0]:+.2f}  {R[1, 1]:+.2f}  {R[1, 2]:+.2f} ⎥\n"
                   f"    ⎣ {R[2, 0]:+.2f}  {R[2, 1]:+.2f}  {R[2, 2]:+.2f} ⎦")
        ax2.text(0.5, 0.18, mat_str, fontsize=11, ha="center", family="monospace")

        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames, "rodrigues_axis_angle.gif", fps=20)


# ============================================================
# 6. 四元数 SLERP vs 欧拉角线性插值
# ============================================================
def gen_quaternion_slerp():
    """对比四元数 SLERP 和欧拉角线性插值的轨迹差异。"""
    print("→ quaternion_slerp.gif")
    from scipy.spatial.transform import Rotation, Slerp

    r0 = Rotation.from_euler("xyz", [0, 0, 0], degrees=True)
    r1 = Rotation.from_euler("xyz", [120, 60, 90], degrees=True)
    key_rots = Rotation.concatenate([r0, r1])
    slerp = Slerp([0, 1], key_rots)

    euler0 = r0.as_euler("xyz", degrees=True)
    euler1 = r1.as_euler("xyz", degrees=True)

    # 待旋转物体：箭头束（"鞋盒")
    arrows = np.array([[1.5, 0, 0], [0, 1, 0], [0, 0, 0.7]]).T  # 3 列 = X/Y/Z 轴
    arrow_colors = [COLORS["red"], COLORS["green"], COLORS["blue"]]

    frames = []
    n = 70
    for i in range(n):
        t = i / (n - 1)
        # 四元数 SLERP
        R_slerp = slerp(t).as_matrix()
        # 欧拉角线性插值
        e_lerp = (1 - t) * euler0 + t * euler1
        R_lerp = Rotation.from_euler("xyz", e_lerp, degrees=True).as_matrix()

        fig = plt.figure(figsize=(13, 6))
        ax1 = fig.add_subplot(121, projection="3d")
        ax2 = fig.add_subplot(122, projection="3d")

        for ax, R, title in [
            (ax1, R_slerp, f"四元数 SLERP  (t={t:.2f})"),
            (ax2, R_lerp, f"欧拉角线性插值  (t={t:.2f})"),
        ]:
            rot_arrows = R @ arrows
            for k, c in enumerate(arrow_colors):
                ax.quiver(0, 0, 0, rot_arrows[0, k], rot_arrows[1, k], rot_arrows[2, k],
                          color=c, lw=4, arrow_length_ratio=0.15)
            ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_zlim(-1.5, 1.5)
            ax.set_box_aspect([1, 1, 1])
            ax.set_title(title, fontsize=12)

        fig.suptitle("SLERP 沿球面最短弧（平滑） vs 欧拉角直接相加（路径扭曲）",
                     fontsize=13, y=1.02)
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames + frames[::-1], "quaternion_slerp.gif", fps=18)


# ============================================================
# 7. 机械臂正运动学（FK）
# ============================================================
def gen_forward_kinematics():
    """2-DOF 机械臂正运动学：关节角度 → 末端位置。"""
    print("→ forward_kinematics.gif")
    L1, L2 = 1.0, 1.0

    # 走一段 (θ1, θ2) 轨迹
    n = 80
    t_arr = np.linspace(0, 2 * np.pi, n)
    theta1_arr = np.pi / 2 + 0.7 * np.sin(t_arr)
    theta2_arr = -np.pi / 3 + np.pi / 3 * np.sin(2 * t_arr)

    trajectory = []
    frames = []
    for i in range(n):
        th1, th2 = theta1_arr[i], theta2_arr[i]
        # 正运动学
        x1, y1 = L1 * np.cos(th1), L1 * np.sin(th1)
        x2, y2 = x1 + L2 * np.cos(th1 + th2), y1 + L2 * np.sin(th1 + th2)
        trajectory.append((x2, y2))

        fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                                 gridspec_kw={"width_ratios": [1.2, 1]})
        ax = axes[0]
        # 工作空间（虚线圆）
        circle = plt.Circle((0, 0), L1 + L2, fill=False,
                            linestyle="--", color=COLORS["gray"], alpha=0.5)
        ax.add_patch(circle)
        # 末端轨迹（轨迹尾巴）
        if trajectory:
            tr = np.array(trajectory)
            ax.plot(tr[:, 0], tr[:, 1], "-", color=COLORS["orange"],
                    lw=2, alpha=0.6, label="末端轨迹")
        # 连杆 1
        ax.plot([0, x1], [0, y1], color=COLORS["blue"], lw=8, solid_capstyle="round")
        # 连杆 2
        ax.plot([x1, x2], [y1, y2], color=COLORS["green"], lw=8, solid_capstyle="round")
        # 关节
        ax.plot(0, 0, "o", color="black", markersize=14, zorder=5)
        ax.plot(x1, y1, "o", color="black", markersize=12, zorder=5)
        ax.plot(x2, y2, "o", color=COLORS["red"], markersize=16, zorder=5)
        # 角度弧
        arc1 = Arc((0, 0), 0.3, 0.3, angle=0, theta1=0,
                   theta2=np.degrees(th1), color=COLORS["blue"], lw=2)
        ax.add_patch(arc1)
        arc2 = Arc((x1, y1), 0.3, 0.3, angle=np.degrees(th1), theta1=0,
                   theta2=np.degrees(th2), color=COLORS["green"], lw=2)
        ax.add_patch(arc2)

        ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal")
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
        ax.legend(loc="upper right", fontsize=10)
        ax.set_title("正运动学：从关节角度计算末端位置", fontsize=14)

        # 右侧：数值
        ax2 = axes[1]
        ax2.axis("off")
        ax2.text(0.5, 0.85, "输入（关节空间）", fontsize=14,
                 ha="center", fontweight="bold")
        ax2.text(0.5, 0.72,
                 f"θ₁ = {np.degrees(th1):+6.1f}°\n"
                 f"θ₂ = {np.degrees(th2):+6.1f}°",
                 fontsize=16, ha="center", family="monospace",
                 color=COLORS["blue"])

        ax2.text(0.5, 0.5, "↓ FK 公式 ↓", fontsize=14, ha="center")
        ax2.text(0.5, 0.40,
                 "x = L₁cos θ₁ + L₂cos(θ₁+θ₂)\n"
                 "y = L₁sin θ₁ + L₂sin(θ₁+θ₂)",
                 fontsize=11, ha="center", family="monospace",
                 bbox=dict(boxstyle="round", facecolor="lightyellow"))

        ax2.text(0.5, 0.22, "输出（笛卡尔空间）", fontsize=14,
                 ha="center", fontweight="bold")
        ax2.text(0.5, 0.09,
                 f"x = {x2:+.3f}\n"
                 f"y = {y2:+.3f}",
                 fontsize=16, ha="center", family="monospace",
                 color=COLORS["red"])
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames, "forward_kinematics.gif", fps=20)


# ============================================================
# 8. 机械臂逆运动学（IK）：跟踪圆形轨迹
# ============================================================
def gen_inverse_kinematics():
    """逆运动学：给定末端目标，反求关节角度。"""
    print("→ inverse_kinematics.gif")
    L1, L2 = 1.0, 1.0

    # 目标：画一个心形或圆
    n = 80
    t_arr = np.linspace(0, 2 * np.pi, n)
    cx, cy, r = 1.0, 0.5, 0.6
    target_x = cx + r * np.cos(t_arr)
    target_y = cy + r * np.sin(t_arr)

    def ik_analytical(x, y, elbow_up=True):
        D = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
        D = np.clip(D, -1, 1)
        th2 = np.arccos(D) * (1 if elbow_up else -1)
        th1 = np.arctan2(y, x) - np.arctan2(L2 * np.sin(th2), L1 + L2 * np.cos(th2))
        return th1, th2

    drawn_path = []
    frames = []
    for i in range(n):
        tx, ty = target_x[i], target_y[i]
        th1, th2 = ik_analytical(tx, ty, elbow_up=True)
        x1, y1 = L1 * np.cos(th1), L1 * np.sin(th1)
        x2, y2 = x1 + L2 * np.cos(th1 + th2), y1 + L2 * np.sin(th1 + th2)
        drawn_path.append((x2, y2))

        fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                                 gridspec_kw={"width_ratios": [1.2, 1]})
        ax = axes[0]
        circle = plt.Circle((0, 0), L1 + L2, fill=False,
                            linestyle="--", color=COLORS["gray"], alpha=0.4)
        ax.add_patch(circle)

        # 目标轨迹（全部）
        ax.plot(target_x, target_y, "--", color=COLORS["orange"],
                lw=1.5, alpha=0.5, label="目标轨迹")
        # 已画过的路径（实线）
        if len(drawn_path) > 1:
            dp = np.array(drawn_path)
            ax.plot(dp[:, 0], dp[:, 1], "-", color=COLORS["red"], lw=2.5,
                    label="末端实际轨迹")

        # 连杆
        ax.plot([0, x1], [0, y1], color=COLORS["blue"], lw=8, solid_capstyle="round")
        ax.plot([x1, x2], [y1, y2], color=COLORS["green"], lw=8, solid_capstyle="round")
        ax.plot(0, 0, "o", color="black", markersize=14, zorder=5)
        ax.plot(x1, y1, "o", color="black", markersize=12, zorder=5)
        ax.plot(x2, y2, "o", color=COLORS["red"], markersize=16, zorder=5)
        # 目标点
        ax.plot(tx, ty, "x", color=COLORS["orange"], markersize=18, mew=4)

        ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal")
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
        ax.legend(loc="upper right", fontsize=10)
        ax.set_title("逆运动学：给定末端轨迹，反求关节角度", fontsize=14)

        ax2 = axes[1]
        ax2.axis("off")
        ax2.text(0.5, 0.85, "目标（笛卡尔空间）", fontsize=14, ha="center",
                 fontweight="bold")
        ax2.text(0.5, 0.74, f"(x, y) = ({tx:+.3f}, {ty:+.3f})", fontsize=14,
                 ha="center", family="monospace", color=COLORS["orange"])
        ax2.text(0.5, 0.58, "↓ 余弦定理 IK ↓", fontsize=13, ha="center")
        ax2.text(0.5, 0.48,
                 "cos θ₂ = (x²+y²−L₁²−L₂²)/(2L₁L₂)\n"
                 "θ₁ = atan2(y,x) − atan2(L₂s₂, L₁+L₂c₂)",
                 fontsize=10, ha="center", family="monospace",
                 bbox=dict(boxstyle="round", facecolor="lightyellow"))
        ax2.text(0.5, 0.27, "输出（关节空间）", fontsize=14, ha="center",
                 fontweight="bold")
        ax2.text(0.5, 0.12,
                 f"θ₁ = {np.degrees(th1):+6.1f}°\n"
                 f"θ₂ = {np.degrees(th2):+6.1f}°",
                 fontsize=16, ha="center", family="monospace",
                 color=COLORS["blue"])

        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames, "inverse_kinematics.gif", fps=20)


# ============================================================
# 9. 雅可比矩阵：关节速度 → 末端速度
# ============================================================
def gen_jacobian():
    """演示雅可比矩阵把关节速度映射到末端速度。"""
    print("→ jacobian.gif")
    L1, L2 = 1.0, 1.0

    n = 80
    t_arr = np.linspace(0, 2 * np.pi, n)
    th1_arr = np.pi / 2 + 0.4 * np.sin(t_arr)
    th2_arr = -np.pi / 3 + 0.5 * np.sin(2 * t_arr)
    dth1_arr = 0.4 * np.cos(t_arr)
    dth2_arr = 1.0 * np.cos(2 * t_arr)

    frames = []
    for i in range(n):
        th1, th2 = th1_arr[i], th2_arr[i]
        dth1, dth2 = dth1_arr[i], dth2_arr[i]
        x1, y1 = L1 * np.cos(th1), L1 * np.sin(th1)
        x2, y2 = x1 + L2 * np.cos(th1 + th2), y1 + L2 * np.sin(th1 + th2)
        # 雅可比
        J = np.array([
            [-L1 * np.sin(th1) - L2 * np.sin(th1 + th2), -L2 * np.sin(th1 + th2)],
            [L1 * np.cos(th1) + L2 * np.cos(th1 + th2), L2 * np.cos(th1 + th2)],
        ])
        v_end = J @ np.array([dth1, dth2])
        det_J = np.linalg.det(J)

        fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                                 gridspec_kw={"width_ratios": [1.2, 1]})
        ax = axes[0]
        ax.plot([0, x1], [0, y1], color=COLORS["blue"], lw=8, solid_capstyle="round")
        ax.plot([x1, x2], [y1, y2], color=COLORS["green"], lw=8, solid_capstyle="round")
        ax.plot(0, 0, "o", color="black", markersize=14, zorder=5)
        ax.plot(x1, y1, "o", color="black", markersize=12, zorder=5)
        ax.plot(x2, y2, "o", color=COLORS["red"], markersize=16, zorder=5)
        # 末端速度（红色箭头）
        scale = 0.5
        if np.linalg.norm(v_end) > 1e-3:
            ax.annotate("", xy=(x2 + v_end[0] * scale, y2 + v_end[1] * scale),
                        xytext=(x2, y2),
                        arrowprops=dict(arrowstyle="->", color=COLORS["red"], lw=3))
            ax.text(x2 + v_end[0] * scale * 1.2, y2 + v_end[1] * scale * 1.2,
                    f"v = ({v_end[0]:+.2f}, {v_end[1]:+.2f})",
                    fontsize=11, color=COLORS["red"])

        # 关节角速度（弧形箭头）
        ax.text(0.05, -0.3, f"ω₁ = {dth1:+.2f} rad/s",
                fontsize=12, color=COLORS["blue"])
        ax.text(x1 + 0.1, y1 - 0.3, f"ω₂ = {dth2:+.2f} rad/s",
                fontsize=12, color=COLORS["green"])

        ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal")
        ax.set_title("雅可比矩阵：关节速度 → 末端速度", fontsize=14)
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)

        ax2 = axes[1]
        ax2.axis("off")
        ax2.text(0.5, 0.9, "v = J(θ) · θ̇", fontsize=20, ha="center",
                 fontweight="bold")
        mat_str = (f"J = ⎡ {J[0, 0]:+.2f}   {J[0, 1]:+.2f} ⎤\n"
                   f"    ⎣ {J[1, 0]:+.2f}   {J[1, 1]:+.2f} ⎦")
        ax2.text(0.5, 0.7, mat_str, fontsize=15, ha="center",
                 family="monospace",
                 bbox=dict(boxstyle="round", facecolor="lightyellow",
                           edgecolor=COLORS["red"], lw=2))
        ax2.text(0.5, 0.45,
                 f"θ̇ = [{dth1:+.2f}, {dth2:+.2f}]ᵀ\n"
                 f"↓\n"
                 f"v = [{v_end[0]:+.3f}, {v_end[1]:+.3f}]ᵀ",
                 fontsize=13, ha="center", family="monospace")
        # 奇异性
        is_singular = abs(det_J) < 0.05
        col = COLORS["red"] if is_singular else COLORS["green"]
        status = ("⚠️ 接近奇异位形！" if is_singular else "✅ 远离奇异")
        ax2.text(0.5, 0.15, f"det(J) = {det_J:+.3f}\n{status}",
                 fontsize=13, ha="center", color=col, fontweight="bold")
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames, "jacobian.gif", fps=18)


# ============================================================
# 10. 卷积（滑动窗口动画）
# ============================================================
def gen_convolution():
    """动画演示 2D 卷积的滑动窗口过程。"""
    print("→ convolution.gif")
    np.random.seed(7)
    # 输入图像（6×6）
    img = np.array([
        [10, 10, 10, 80, 80, 80],
        [10, 10, 10, 80, 80, 80],
        [10, 10, 10, 80, 80, 80],
        [80, 80, 80, 10, 10, 10],
        [80, 80, 80, 10, 10, 10],
        [80, 80, 80, 10, 10, 10],
    ], dtype=float)
    # 边缘检测核
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])

    H, W = img.shape
    kh, kw = kernel.shape
    out_h, out_w = H - kh + 1, W - kw + 1
    output = np.zeros((out_h, out_w))

    frames = []
    for i in range(out_h):
        for j in range(out_w):
            window = img[i:i + kh, j:j + kw]
            output[i, j] = np.sum(window * kernel)

            fig, axes = plt.subplots(1, 3, figsize=(13, 5))
            # 输入图像 + 滑动窗口
            ax = axes[0]
            ax.imshow(img, cmap="gray", vmin=0, vmax=100)
            rect = Rectangle((j - 0.5, i - 0.5), kw, kh,
                             linewidth=4, edgecolor=COLORS["red"], facecolor="none")
            ax.add_patch(rect)
            for r in range(H):
                for c in range(W):
                    ax.text(c, r, f"{int(img[r, c])}",
                            ha="center", va="center",
                            color="red" if (i <= r < i + kh and j <= c < j + kw)
                            else "white", fontsize=11)
            ax.set_title("输入图像（红框 = 当前窗口）", fontsize=12)
            ax.set_xticks([]); ax.set_yticks([])
            ax.grid(False)

            # 卷积核
            ax = axes[1]
            ax.imshow(kernel, cmap="RdBu", vmin=-2, vmax=8)
            for r in range(kh):
                for c in range(kw):
                    ax.text(c, r, f"{int(kernel[r, c])}",
                            ha="center", va="center", fontsize=18, fontweight="bold")
            ax.set_title("卷积核 (边缘检测)", fontsize=12)
            ax.set_xticks([]); ax.set_yticks([])
            ax.grid(False)

            # 输出特征图
            ax = axes[2]
            out_show = output.copy()
            ax.imshow(out_show, cmap="hot", vmin=-100, vmax=300)
            for r in range(out_h):
                for c in range(out_w):
                    if (r < i) or (r == i and c <= j):
                        ax.text(c, r, f"{int(output[r, c])}",
                                ha="center", va="center", color="white", fontsize=11)
            # 当前格子的红框
            curr_rect = Rectangle((j - 0.5, i - 0.5), 1, 1,
                                  linewidth=4, edgecolor=COLORS["red"], facecolor="none")
            ax.add_patch(curr_rect)
            ax.set_title(f"输出特征图：当前值 = {int(output[i, j])}", fontsize=12)
            ax.set_xticks([]); ax.set_yticks([])
            ax.grid(False)
            fig.suptitle("2D 卷积：滑动窗口 × 加权求和", fontsize=14, y=1.0)
            frames.append(fig_to_frame(fig))
            plt.close(fig)

    save_gif(frames + frames[-1:] * 10, "convolution.gif", fps=6)


# ============================================================
# 11. 边缘检测（Sobel）
# ============================================================
def gen_edge_detection():
    """动态展示 Sobel 边缘检测在合成图像上的效果。"""
    print("→ edge_detection.gif")
    # 合成图像：含多个简单几何
    H = W = 80
    img = np.full((H, W), 60.0)
    img[15:35, 15:35] = 200    # 方块
    # 圆
    yy, xx = np.mgrid[:H, :W]
    img[(xx - 55)**2 + (yy - 25)**2 < 12**2] = 220
    # 三角
    for r in range(45, 70):
        img[r, 20 + (r - 45):60 - (r - 45)] = 180

    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = sobel_x.T

    def conv2d(im, k):
        out = np.zeros_like(im)
        kh, kw = k.shape
        pad_h, pad_w = kh // 2, kw // 2
        padded = np.pad(im, ((pad_h, pad_h), (pad_w, pad_w)))
        for i in range(im.shape[0]):
            for j in range(im.shape[1]):
                out[i, j] = np.sum(padded[i:i + kh, j:j + kw] * k)
        return out

    gx = conv2d(img, sobel_x)
    gy = conv2d(img, sobel_y)
    grad_mag = np.sqrt(gx**2 + gy**2)

    frames = []
    # 阶段1：渐显原图
    for i in range(15):
        alpha = (i + 1) / 15
        fig, axes = plt.subplots(1, 4, figsize=(15, 4))
        axes[0].imshow(img, cmap="gray", vmin=0, vmax=255)
        axes[0].set_title("原图", fontsize=12)
        for a in axes:
            a.set_xticks([]); a.set_yticks([]); a.grid(False)
        axes[1].imshow(np.zeros_like(img), cmap="gray")
        axes[1].set_title("∂I/∂x (Sobel X)", fontsize=12)
        axes[2].imshow(np.zeros_like(img), cmap="gray")
        axes[2].set_title("∂I/∂y (Sobel Y)", fontsize=12)
        axes[3].imshow(np.zeros_like(img), cmap="gray")
        axes[3].set_title("|∇I| 梯度幅值", fontsize=12)
        fig.suptitle("边缘检测：用 Sobel 算子估算图像梯度", fontsize=14)
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    # 阶段2：依次显示 Gx, Gy, |∇I|
    for stage in range(3):
        for i in range(15):
            alpha = (i + 1) / 15
            fig, axes = plt.subplots(1, 4, figsize=(15, 4))
            axes[0].imshow(img, cmap="gray", vmin=0, vmax=255)
            axes[0].set_title("原图", fontsize=12)
            axes[1].imshow(gx * (alpha if stage >= 0 else 0),
                           cmap="RdBu", vmin=-400, vmax=400)
            axes[1].set_title("∂I/∂x (Sobel X)", fontsize=12)
            axes[2].imshow(gy * (alpha if stage >= 1 else 0),
                           cmap="RdBu", vmin=-400, vmax=400)
            axes[2].set_title("∂I/∂y (Sobel Y)", fontsize=12)
            axes[3].imshow(grad_mag * (alpha if stage >= 2 else 0),
                           cmap="hot", vmin=0, vmax=500)
            axes[3].set_title("|∇I| 梯度幅值", fontsize=12)
            for a in axes:
                a.set_xticks([]); a.set_yticks([]); a.grid(False)
            fig.suptitle("边缘检测：用 Sobel 算子估算图像梯度", fontsize=14)
            frames.append(fig_to_frame(fig))
            plt.close(fig)

    save_gif(frames + frames[-1:] * 15, "edge_detection.gif", fps=15)


# ============================================================
# 12 / 13. BFS 和 A* 搜索（并排对比）
# ============================================================
def _build_grid_map(seed=42):
    """构造一个 20×20 的带障碍栅格地图。"""
    np.random.seed(seed)
    H, W = 20, 20
    grid = np.zeros((H, W), dtype=int)
    # 几堵墙
    grid[5:15, 8] = 1
    grid[3, 4:12] = 1
    grid[12:18, 12] = 1
    grid[15, 5:13] = 1
    grid[7, 12:18] = 1
    start = (1, 1)
    goal = (18, 18)
    grid[start] = 0; grid[goal] = 0
    return grid, start, goal


def _bfs(grid, start, goal):
    from collections import deque
    H, W = grid.shape
    visited = {start: None}
    order = [start]
    q = deque([start])
    found = False
    while q:
        cur = q.popleft()
        if cur == goal:
            found = True
            break
        r, c = cur
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < H and 0 <= nc < W and grid[nr, nc] == 0 \
                    and (nr, nc) not in visited:
                visited[(nr, nc)] = cur
                order.append((nr, nc))
                q.append((nr, nc))
    path = []
    if found:
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = visited[cur]
        path = path[::-1]
    return order, path


def _astar(grid, start, goal):
    import heapq
    H, W = grid.shape
    open_set = [(0, start)]
    came_from = {start: None}
    gscore = {start: 0}
    order = [start]
    found = False
    while open_set:
        _, cur = heapq.heappop(open_set)
        if cur == goal:
            found = True
            break
        r, c = cur
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < H and 0 <= nc < W and grid[nr, nc] == 0:
                tentative_g = gscore[cur] + 1
                if tentative_g < gscore.get((nr, nc), 1e9):
                    came_from[(nr, nc)] = cur
                    gscore[(nr, nc)] = tentative_g
                    h = abs(nr - goal[0]) + abs(nc - goal[1])
                    heapq.heappush(open_set, (tentative_g + h, (nr, nc)))
                    if (nr, nc) not in order:
                        order.append((nr, nc))
    path = []
    if found:
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = came_from[cur]
        path = path[::-1]
    return order, path


def gen_bfs_vs_astar():
    """BFS vs A* 扩展节点过程对比动画。"""
    print("→ bfs_vs_astar.gif")
    grid, start, goal = _build_grid_map()
    bfs_order, bfs_path = _bfs(grid, start, goal)
    astar_order, astar_path = _astar(grid, start, goal)

    max_steps = max(len(bfs_order), len(astar_order))
    n_frames = 60
    step_indices = np.linspace(0, max_steps, n_frames, dtype=int)

    frames = []
    for k, n_show in enumerate(step_indices):
        fig, axes = plt.subplots(1, 2, figsize=(13, 6))
        for ax, order, path, title, alg_color in [
            (axes[0], bfs_order, bfs_path, "BFS（广度优先搜索）", COLORS["blue"]),
            (axes[1], astar_order, astar_path, "A* 算法（曼哈顿启发式）", COLORS["green"]),
        ]:
            # 障碍
            ax.imshow(grid, cmap="Greys", vmin=0, vmax=1)
            # 已扩展节点（小圆点）
            for (r, c) in order[:min(n_show, len(order))]:
                ax.plot(c, r, "s", color=alg_color, markersize=10, alpha=0.55)
            # 起点
            ax.plot(start[1], start[0], "o", color=COLORS["orange"], markersize=18)
            ax.text(start[1], start[0], "S", ha="center", va="center",
                    fontweight="bold", fontsize=12)
            # 终点
            ax.plot(goal[1], goal[0], "*", color=COLORS["red"], markersize=22)
            # 当找到路径时（最后阶段）绘制
            if n_show >= len(order) and path:
                pr = [p[0] for p in path]; pc = [p[1] for p in path]
                ax.plot(pc, pr, "-", color=COLORS["red"], lw=4)
            ax.set_title(
                f"{title}\n已扩展 {min(n_show, len(order))} 个节点",
                fontsize=12,
            )
            ax.set_xticks([]); ax.set_yticks([])
            ax.grid(False)
        fig.suptitle("BFS 无差别扩展 vs A* 朝目标方向扩展", fontsize=14, y=1.02)
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames + frames[-1:] * 10, "bfs_vs_astar.gif", fps=15)


# ============================================================
# 14. RRT 树扩展动画
# ============================================================
def gen_rrt():
    """RRT 随机采样建树过程。"""
    print("→ rrt_planning.gif")
    np.random.seed(7)
    # 障碍
    obstacles = [(3, 3, 2, 5), (6, 6, 3, 2), (1, 7, 2, 2)]   # (x, y, w, h)
    start = np.array([0.5, 0.5])
    goal = np.array([9.5, 9.5])

    def in_collision(p):
        for (ox, oy, ow, oh) in obstacles:
            if ox <= p[0] <= ox + ow and oy <= p[1] <= oy + oh:
                return True
        return False

    def line_collision(a, b, n=8):
        for s in np.linspace(0, 1, n):
            if in_collision(a + s * (b - a)):
                return True
        return False

    tree_nodes = [start]
    tree_edges = []
    parent = {0: -1}
    step_size = 0.5
    found = False

    snapshots = []

    for it in range(300):
        if np.random.rand() < 0.1:
            q_rand = goal
        else:
            q_rand = np.array([np.random.uniform(0, 10), np.random.uniform(0, 10)])
        # 找最近
        dists = [np.linalg.norm(q_rand - n) for n in tree_nodes]
        nearest_idx = int(np.argmin(dists))
        q_near = tree_nodes[nearest_idx]
        # 延伸
        d = q_rand - q_near
        if np.linalg.norm(d) > step_size:
            d = d / np.linalg.norm(d) * step_size
        q_new = q_near + d
        if line_collision(q_near, q_new):
            continue
        new_idx = len(tree_nodes)
        tree_nodes.append(q_new)
        tree_edges.append((nearest_idx, new_idx))
        parent[new_idx] = nearest_idx

        if it % 5 == 0 or np.linalg.norm(q_new - goal) < step_size:
            snapshots.append((list(tree_nodes), list(tree_edges), q_rand.copy(), q_new.copy()))
        if np.linalg.norm(q_new - goal) < step_size and not line_collision(q_new, goal):
            tree_nodes.append(goal)
            tree_edges.append((new_idx, len(tree_nodes) - 1))
            parent[len(tree_nodes) - 1] = new_idx
            found = True
            snapshots.append((list(tree_nodes), list(tree_edges), q_rand.copy(), goal.copy()))
            break

    # 路径回溯
    path = []
    if found:
        idx = len(tree_nodes) - 1
        while idx != -1:
            path.append(tree_nodes[idx])
            idx = parent[idx]
        path = path[::-1]

    frames = []
    for nodes, edges, q_rand, q_new in snapshots:
        fig, ax = plt.subplots(figsize=(8, 7))
        for (ox, oy, ow, oh) in obstacles:
            ax.add_patch(Rectangle((ox, oy), ow, oh,
                                   facecolor=COLORS["gray"], alpha=0.7,
                                   edgecolor="black"))
        # 树边
        for (a, b) in edges:
            pa, pb = nodes[a], nodes[b]
            ax.plot([pa[0], pb[0]], [pa[1], pb[1]], "-",
                    color=COLORS["blue"], lw=0.8, alpha=0.6)
        # 树节点
        if len(nodes) > 1:
            arr = np.array(nodes)
            ax.plot(arr[:, 0], arr[:, 1], ".",
                    color=COLORS["blue"], markersize=4, alpha=0.7)
        # 采样点
        ax.plot(q_rand[0], q_rand[1], "x", color=COLORS["orange"],
                markersize=14, mew=2)
        ax.plot(q_new[0], q_new[1], "o", color=COLORS["green"], markersize=8)
        ax.plot(start[0], start[1], "o", color=COLORS["orange"], markersize=18)
        ax.text(start[0], start[1], "S", ha="center", va="center", fontweight="bold")
        ax.plot(goal[0], goal[1], "*", color=COLORS["red"], markersize=22)
        ax.set_xlim(0, 10); ax.set_ylim(0, 10)
        ax.set_aspect("equal")
        ax.set_title(f"RRT：随机采样建树（树大小 = {len(nodes)}）", fontsize=13)
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    # 最后展示最终路径
    if path:
        for _ in range(20):
            fig, ax = plt.subplots(figsize=(8, 7))
            for (ox, oy, ow, oh) in obstacles:
                ax.add_patch(Rectangle((ox, oy), ow, oh,
                                       facecolor=COLORS["gray"], alpha=0.7,
                                       edgecolor="black"))
            for (a, b) in snapshots[-1][1]:
                pa, pb = snapshots[-1][0][a], snapshots[-1][0][b]
                ax.plot([pa[0], pb[0]], [pa[1], pb[1]], "-",
                        color=COLORS["blue"], lw=0.6, alpha=0.4)
            arr = np.array(path)
            ax.plot(arr[:, 0], arr[:, 1], "-", color=COLORS["red"], lw=4)
            ax.plot(start[0], start[1], "o", color=COLORS["orange"], markersize=18)
            ax.text(start[0], start[1], "S", ha="center", va="center", fontweight="bold")
            ax.plot(goal[0], goal[1], "*", color=COLORS["red"], markersize=22)
            ax.set_xlim(0, 10); ax.set_ylim(0, 10)
            ax.set_aspect("equal")
            ax.set_title("RRT 找到路径（红色实线 = 最终路径）", fontsize=13)
            frames.append(fig_to_frame(fig))
            plt.close(fig)
    save_gif(frames, "rrt_planning.gif", fps=15)


# ============================================================
# 15. DWA 速度采样
# ============================================================
def gen_dwa():
    """DWA 动态窗口法：在速度空间采样 + 模拟轨迹打分。"""
    print("→ dwa_planning.gif")
    # 机器人在 (0,0), goal 在 (5, 2)，障碍物
    robot = np.array([0.0, 0.0])
    heading = 0.0
    goal = np.array([6.0, 2.5])
    obstacles = np.array([[3.0, 0.0], [3.0, 0.5], [3.5, 0.0],
                          [4.5, 2.0], [4.5, 2.5]])

    # 速度空间窗口
    v_min, v_max = 0.0, 1.0
    w_min, w_max = -1.2, 1.2
    n_v, n_w = 9, 11
    T = 1.5    # 模拟时长
    dt = 0.05

    v_samples = np.linspace(v_min, v_max, n_v)
    w_samples = np.linspace(w_min, w_max, n_w)

    trajs = []
    scores = []
    for v in v_samples:
        for w in w_samples:
            traj = [robot.copy()]
            h = heading
            p = robot.copy()
            collision = False
            for _ in range(int(T / dt)):
                h += w * dt
                p = p + np.array([v * np.cos(h), v * np.sin(h)]) * dt
                traj.append(p.copy())
                # 碰撞检测
                if np.any(np.linalg.norm(obstacles - p, axis=1) < 0.5):
                    collision = True
                    break
            traj = np.array(traj)
            # 评分：朝目标 + 远离障碍 + 速度大
            if collision:
                score = -100
            else:
                end = traj[-1]
                heading_score = -np.linalg.norm(end - goal)
                obs_dist = np.min([np.linalg.norm(obstacles - p, axis=1).min()
                                   for p in traj])
                score = heading_score * 2 + obs_dist * 0.5 + v * 0.3
            trajs.append(traj)
            scores.append(score)

    scores = np.array(scores)
    norm_scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)
    best_idx = int(np.argmax(scores))

    # 动画：逐渐显示候选轨迹
    n_show_steps = 35
    indices = np.linspace(1, len(trajs), n_show_steps, dtype=int)

    frames = []
    for n_show in indices:
        fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                                 gridspec_kw={"width_ratios": [1.4, 1]})
        ax = axes[0]
        # 障碍
        ax.scatter(obstacles[:, 0], obstacles[:, 1], s=400,
                   marker="s", color=COLORS["gray"], edgecolor="black")
        # 候选轨迹
        for k in range(min(n_show, len(trajs))):
            t = trajs[k]
            if scores[k] < -50:
                ax.plot(t[:, 0], t[:, 1], "-", color=COLORS["red"], lw=0.5, alpha=0.3)
            else:
                ax.plot(t[:, 0], t[:, 1], "-",
                        color=plt.cm.viridis(norm_scores[k]), lw=1.2, alpha=0.7)
        # 最优轨迹高亮（最后阶段）
        if n_show >= len(trajs):
            best = trajs[best_idx]
            ax.plot(best[:, 0], best[:, 1], "-", color=COLORS["green"], lw=4,
                    label="最优轨迹 ★")
            ax.legend(loc="upper left", fontsize=11)
        # 机器人 & 目标
        ax.plot(robot[0], robot[1], "o", color=COLORS["blue"], markersize=18)
        ax.plot(goal[0], goal[1], "*", color=COLORS["red"], markersize=25)
        ax.set_xlim(-1, 7); ax.set_ylim(-2, 4)
        ax.set_aspect("equal")
        ax.set_title("DWA：在速度空间采样 → 模拟轨迹 → 打分", fontsize=13)

        ax2 = axes[1]
        # 速度空间窗口
        sc = ax2.scatter(
            np.repeat(v_samples, n_w),
            np.tile(w_samples, n_v),
            c=scores, cmap="viridis", s=200, vmin=scores.min(), vmax=scores.max(),
            edgecolor="black",
        )
        if n_show >= len(trajs):
            bv = v_samples[best_idx // n_w]
            bw = w_samples[best_idx % n_w]
            ax2.plot(bv, bw, "*", color=COLORS["red"], markersize=30,
                     markeredgecolor="white", mew=2)
        ax2.set_xlabel("线速度 v (m/s)")
        ax2.set_ylabel("角速度 ω (rad/s)")
        ax2.set_title("速度空间（颜色 = 评分）", fontsize=12)
        fig.colorbar(sc, ax=ax2, label="评分")
        frames.append(fig_to_frame(fig))
        plt.close(fig)

    save_gif(frames + frames[-1:] * 15, "dwa_planning.gif", fps=10)


# ============================================================
# 调度
# ============================================================
ANIMATIONS = {
    "vector_ops": gen_vector_ops,
    "rotation_2d": gen_rotation_2d,
    "homogeneous_transform": gen_homogeneous_transform,
    "gimbal_lock": gen_gimbal_lock,
    "rodrigues_axis_angle": gen_rodrigues_axis_angle,
    "quaternion_slerp": gen_quaternion_slerp,
    "forward_kinematics": gen_forward_kinematics,
    "inverse_kinematics": gen_inverse_kinematics,
    "jacobian": gen_jacobian,
    "convolution": gen_convolution,
    "edge_detection": gen_edge_detection,
    "bfs_vs_astar": gen_bfs_vs_astar,
    "rrt_planning": gen_rrt,
    "dwa_planning": gen_dwa,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*",
                        help="要生成的动画名称（不指定则全部生成）")
    parser.add_argument("--list", action="store_true", help="列出所有动画")
    args = parser.parse_args()

    if args.list:
        print("可用动画：")
        for name in ANIMATIONS:
            print(f"  - {name}")
        return

    if not args.names or "all" in args.names:
        names = list(ANIMATIONS)
    else:
        names = args.names

    print(f"将生成 {len(names)} 个动画到 {OUT_DIR}\n")
    for name in names:
        if name not in ANIMATIONS:
            print(f"  ⚠️ 跳过未知动画: {name}")
            continue
        try:
            ANIMATIONS[name]()
        except Exception as e:
            import traceback
            print(f"  ❌ {name} 失败: {e}")
            traceback.print_exc()
    print("\n✅ 全部完成")


if __name__ == "__main__":
    main()

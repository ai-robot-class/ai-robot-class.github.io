#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""方向 A 常驻程序：PyBullet 迷宫 + 四足机器人 + WebSocket 遥控服务。

一个程序里同时做三件事（本周的核心工程原则——单一常驻程序）：
  1) 监听网络（WebSocket），接收手机网页发来的控制命令；
  2) 推进 PyBullet 仿真，并做墙体碰撞检测、终点判定；
  3) 把机器人状态 + 迷宫信息回传给网页，让网页画出俯视图。

迷宫本身在 maze.py 里定义；想换地图只改 maze.py。
"""
import asyncio
import json
import math
import os
from pathlib import Path

from aiohttp import WSMsgType, web
import pybullet as p
import pybullet_data

import maze as maze_module


HOST = "0.0.0.0"
PORT = 8765
ROBOT_HEIGHT = 0.45
DOG_RADIUS = 0.30          # 机器狗碰撞半径（用于撞墙检测）
MOVE_SPEED = 0.9           # 前进速度（米/秒）
TURN_SPEED = 1.6           # 转向速度（弧度/秒）


class MazeDogServer:
    def __init__(self):
        # 优先开 GUI 窗口（noVNC 桌面 / 本机有显示时）；无显示则退回 DIRECT 无头模式
        self.gui = False
        want_gui = os.environ.get("PYBULLET_GUI", "1") != "0"
        if want_gui:
            try:
                self.physics_client = p.connect(p.GUI)
                self.gui = True
            except Exception:
                self.physics_client = p.connect(p.DIRECT)
        else:
            self.physics_client = p.connect(p.DIRECT)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.setTimeStep(1.0 / 120.0)
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)

        self.maze = maze_module.build_maze()
        self.wall_aabbs = self.maze["aabbs"]
        self.goal = self.maze["goal"]                       # (x, y, r)
        sx, sy = self.maze["start"]
        self.start_pose = (sx, sy, ROBOT_HEIGHT)

        self.robot_id = None
        self.command = {"move": 0.0, "turn": 0.0}
        self.blocked = False
        self.goal_reached = False

        self._build_world()

        if self.gui:
            center = self.maze["size"] / 2.0
            p.resetDebugVisualizerCamera(
                cameraDistance=self.maze["size"] * 0.95,
                cameraYaw=45, cameraPitch=-55,
                cameraTargetPosition=[center, center, 0],
            )

    def _build_world(self):
        p.loadURDF("plane.urdf")
        self._build_maze()
        self._build_markers()
        self.robot_id = self._load_robot()
        self.reset_robot()

    def _build_maze(self):
        color = [0.27, 0.40, 0.62, 1.0]
        h = self.maze["wall_height"]
        for cx, cy, hx, hy in self.maze["walls"]:
            half = [hx, hy, h]
            collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=half)
            visual = p.createVisualShape(p.GEOM_BOX, halfExtents=half, rgbaColor=color)
            p.createMultiBody(
                baseMass=0,
                baseCollisionShapeIndex=collision,
                baseVisualShapeIndex=visual,
                basePosition=[cx, cy, h],
            )

    def _build_markers(self):
        gx, gy, gr = self.goal
        # 终点：绿色圆盘
        goal_vis = p.createVisualShape(
            p.GEOM_CYLINDER, radius=gr, length=0.04, rgbaColor=[0.13, 0.77, 0.37, 0.9]
        )
        p.createMultiBody(baseMass=0, baseVisualShapeIndex=goal_vis,
                          basePosition=[gx, gy, 0.02])
        # 起点：橙色圆盘
        sx, sy = self.maze["start"]
        start_vis = p.createVisualShape(
            p.GEOM_CYLINDER, radius=gr * 0.8, length=0.04, rgbaColor=[0.96, 0.62, 0.07, 0.85]
        )
        p.createMultiBody(baseMass=0, baseVisualShapeIndex=start_vis,
                          basePosition=[sx, sy, 0.02])

    def _load_robot(self):
        for urdf in ("laikago/laikago_toes.urdf", "laikago/laikago.urdf"):
            try:
                return p.loadURDF(urdf, list(self.start_pose), useFixedBase=False)
            except Exception:
                continue
        raise RuntimeError("无法在 pybullet_data 中加载四足机器人 URDF。")

    def reset_robot(self):
        quat = p.getQuaternionFromEuler([0.0, 0.0, 0.0])
        p.resetBasePositionAndOrientation(self.robot_id, self.start_pose, quat)
        p.resetBaseVelocity(self.robot_id, [0, 0, 0], [0, 0, 0])
        self.command = {"move": 0.0, "turn": 0.0}
        self.blocked = False
        self.goal_reached = False

    def set_command(self, move, turn):
        self.command["move"] = float(move)
        self.command["turn"] = float(turn)

    def stop(self):
        self.set_command(0.0, 0.0)

    def _hits_wall(self, x, y):
        """点 (x,y) 加上机器狗半径后，是否与任何墙体包围盒相交。"""
        r = DOG_RADIUS
        for min_x, min_y, max_x, max_y in self.wall_aabbs:
            if (min_x - r) <= x <= (max_x + r) and (min_y - r) <= y <= (max_y + r):
                return True
        return False

    def step(self, dt):
        position, orientation = p.getBasePositionAndOrientation(self.robot_id)
        yaw = p.getEulerFromQuaternion(orientation)[2]

        # 终点到达后锁定，不再移动
        if self.goal_reached:
            p.stepSimulation()
            return

        # 先更新朝向（转向永远允许）
        yaw += self.command["turn"] * TURN_SPEED * dt

        # 再尝试前进/后退，撞墙则原地不动
        nx = position[0] + self.command["move"] * MOVE_SPEED * math.cos(yaw) * dt
        ny = position[1] + self.command["move"] * MOVE_SPEED * math.sin(yaw) * dt
        lo, hi = DOG_RADIUS, self.maze["size"] - DOG_RADIUS
        nx = min(max(nx, lo), hi)
        ny = min(max(ny, lo), hi)

        if self.command["move"] != 0.0 and self._hits_wall(nx, ny):
            self.blocked = True
            nx, ny = position[0], position[1]   # 撞墙：保持原位
        else:
            self.blocked = False

        quat = p.getQuaternionFromEuler([0.0, 0.0, yaw])
        p.resetBasePositionAndOrientation(self.robot_id, [nx, ny, ROBOT_HEIGHT], quat)

        gx, gy, gr = self.goal
        if (nx - gx) ** 2 + (ny - gy) ** 2 <= gr ** 2:
            self.goal_reached = True
            self.stop()

        p.stepSimulation()

    def get_state(self):
        position, orientation = p.getBasePositionAndOrientation(self.robot_id)
        yaw = p.getEulerFromQuaternion(orientation)[2]
        return {
            "position": {
                "x": round(position[0], 3),
                "y": round(position[1], 3),
                "z": round(position[2], 3),
            },
            "yaw": round(yaw, 3),
            "command": dict(self.command),
            "blocked": self.blocked,
            "goal_reached": self.goal_reached,
            "maze": {
                "size": self.maze["size"],
                "walls": [
                    {"cx": cx, "cy": cy, "hx": hx, "hy": hy}
                    for (cx, cy, hx, hy) in self.maze["walls"]
                ],
                "goal": {"x": self.goal[0], "y": self.goal[1], "r": self.goal[2]},
                "start": {"x": self.maze["start"][0], "y": self.maze["start"][1]},
                "robot_radius": DOG_RADIUS,
            },
        }

    def close(self):
        p.disconnect(self.physics_client)


async def index(request):
    html = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
    return web.Response(text=html, content_type="text/html")


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    app = request.app
    sim = app["sim"]
    app["clients"].add(ws)
    await ws.send_json({"type": "state", "data": sim.get_state()})

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue
            data = json.loads(msg.data)
            msg_type = data.get("type")
            if msg_type == "command":
                sim.set_command(data.get("move", 0.0), data.get("turn", 0.0))
            elif msg_type == "stop":
                sim.stop()
            elif msg_type == "reset":
                sim.reset_robot()
            await ws.send_json({"type": "state", "data": sim.get_state()})
    finally:
        app["clients"].discard(ws)
    return ws


async def simulation_loop(app):
    sim = app["sim"]
    while True:
        sim.step(1.0 / 60.0)
        payload = json.dumps({"type": "state", "data": sim.get_state()})
        stale = []
        for ws in app["clients"]:
            if ws.closed:
                stale.append(ws)
                continue
            await ws.send_str(payload)
        for ws in stale:
            app["clients"].discard(ws)
        await asyncio.sleep(1.0 / 10.0)


async def on_startup(app):
    app["sim"] = MazeDogServer()
    app["clients"] = set()
    app["sim_task"] = asyncio.create_task(simulation_loop(app))


async def on_cleanup(app):
    app["sim_task"].cancel()
    try:
        await app["sim_task"]
    except asyncio.CancelledError:
        pass
    app["sim"].close()


def main():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    print(f"PyBullet starter listening on http://{HOST}:{PORT}")
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import asyncio
import json
import math
from pathlib import Path

from aiohttp import WSMsgType, web
import pybullet as p
import pybullet_data


HOST = "0.0.0.0"
PORT = 8765
ROBOT_HEIGHT = 0.45


class MazeDogServer:
    def __init__(self):
        self.physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.setTimeStep(1.0 / 120.0)
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)

        self.robot_id = None
        self.clients = set()
        self.command = {"move": 0.0, "turn": 0.0}
        self.start_pose = (0.8, 0.8, ROBOT_HEIGHT)

        self._build_world()

    def _build_world(self):
        p.loadURDF("plane.urdf")
        self._build_maze()
        self.robot_id = self._load_robot()
        self.reset_robot()

    def _build_maze(self):
        wall_specs = [
            ((4.0, 0.0, 0.3), (4.0, 0.1, 0.3)),
            ((4.0, 8.0, 0.3), (4.0, 0.1, 0.3)),
            ((0.0, 4.0, 0.3), (0.1, 4.0, 0.3)),
            ((8.0, 4.0, 0.3), (0.1, 4.0, 0.3)),
            ((2.5, 2.0, 0.3), (1.5, 0.1, 0.3)),
            ((5.5, 2.0, 0.3), (1.5, 0.1, 0.3)),
            ((2.0, 5.0, 0.3), (0.1, 1.5, 0.3)),
            ((6.0, 5.0, 0.3), (0.1, 1.5, 0.3)),
            ((4.0, 6.0, 0.3), (1.5, 0.1, 0.3)),
        ]
        color = [0.2, 0.5, 0.9, 1.0]

        for position, half_extents in wall_specs:
            collision = p.createCollisionShape(
                p.GEOM_BOX, halfExtents=half_extents
            )
            visual = p.createVisualShape(
                p.GEOM_BOX, halfExtents=half_extents, rgbaColor=color
            )
            p.createMultiBody(
                baseMass=0,
                baseCollisionShapeIndex=collision,
                baseVisualShapeIndex=visual,
                basePosition=position,
            )

    def _load_robot(self):
        candidates = [
            "laikago/laikago_toes.urdf",
            "laikago/laikago.urdf",
        ]
        for urdf in candidates:
            try:
                return p.loadURDF(
                    urdf,
                    [self.start_pose[0], self.start_pose[1], self.start_pose[2]],
                    useFixedBase=False,
                )
            except Exception:
                continue
        raise RuntimeError("无法在 pybullet_data 中加载四足机器人 URDF。")

    def reset_robot(self):
        quat = p.getQuaternionFromEuler([0.0, 0.0, 0.0])
        p.resetBasePositionAndOrientation(self.robot_id, self.start_pose, quat)
        p.resetBaseVelocity(self.robot_id, [0, 0, 0], [0, 0, 0])
        self.command = {"move": 0.0, "turn": 0.0}

    def set_command(self, move, turn):
        self.command["move"] = float(move)
        self.command["turn"] = float(turn)

    def stop(self):
        self.set_command(0.0, 0.0)

    def step(self, dt):
        position, orientation = p.getBasePositionAndOrientation(self.robot_id)
        yaw = p.getEulerFromQuaternion(orientation)[2]

        yaw += self.command["turn"] * 1.4 * dt
        x = position[0] + self.command["move"] * 0.8 * math.cos(yaw) * dt
        y = position[1] + self.command["move"] * 0.8 * math.sin(yaw) * dt

        x = min(max(x, 0.4), 7.6)
        y = min(max(y, 0.4), 7.6)

        quat = p.getQuaternionFromEuler([0.0, 0.0, yaw])
        p.resetBasePositionAndOrientation(self.robot_id, [x, y, ROBOT_HEIGHT], quat)
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

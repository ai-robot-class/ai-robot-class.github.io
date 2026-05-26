#!/usr/bin/env python3
import asyncio
import json
import threading
from pathlib import Path

from aiohttp import WSMsgType, web
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


HOST = "0.0.0.0"
PORT = 8080


class TurtleWebBridge(Node):
    def __init__(self):
        super().__init__("turtlesim_web_bridge")
        self.publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.subscription = self.create_subscription(
            Pose, "/turtle1/pose", self.on_pose, 10
        )
        self.current_linear = 0.0
        self.current_angular = 0.0
        self.current_pose = {"x": 0.0, "y": 0.0, "theta": 0.0}
        self.timer = self.create_timer(0.1, self.publish_command)

    def on_pose(self, msg):
        self.current_pose = {
            "x": round(msg.x, 3),
            "y": round(msg.y, 3),
            "theta": round(msg.theta, 3),
        }

    def set_command(self, linear, angular):
        self.current_linear = float(linear)
        self.current_angular = float(angular)

    def stop(self):
        self.set_command(0.0, 0.0)

    def publish_command(self):
        msg = Twist()
        msg.linear.x = self.current_linear
        msg.angular.z = self.current_angular
        self.publisher.publish(msg)

    def get_state(self):
        return {
            "pose": dict(self.current_pose),
            "command": {
                "linear": self.current_linear,
                "angular": self.current_angular,
            },
        }


def spin_ros(node):
    rclpy.spin(node)


async def index(request):
    html = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
    return web.Response(text=html, content_type="text/html")


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    app = request.app
    bridge = app["bridge"]
    app["clients"].add(ws)
    await ws.send_json({"type": "state", "data": bridge.get_state()})

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue

            data = json.loads(msg.data)
            msg_type = data.get("type")

            if msg_type == "command":
                bridge.set_command(data.get("linear", 0.0), data.get("angular", 0.0))
            elif msg_type == "stop":
                bridge.stop()

            await ws.send_json({"type": "state", "data": bridge.get_state()})
    finally:
        app["clients"].discard(ws)
    return ws


async def broadcast_loop(app):
    while True:
        state_json = json.dumps({"type": "state", "data": app["bridge"].get_state()})
        stale = []
        for ws in app["clients"]:
            if ws.closed:
                stale.append(ws)
                continue
            await ws.send_str(state_json)
        for ws in stale:
            app["clients"].discard(ws)
        await asyncio.sleep(0.2)


async def on_startup(app):
    rclpy.init()
    bridge = TurtleWebBridge()
    app["bridge"] = bridge
    app["clients"] = set()
    ros_thread = threading.Thread(target=spin_ros, args=(bridge,), daemon=True)
    ros_thread.start()
    app["ros_thread"] = ros_thread
    app["broadcast_task"] = asyncio.create_task(broadcast_loop(app))


async def on_cleanup(app):
    app["broadcast_task"].cancel()
    try:
        await app["broadcast_task"]
    except asyncio.CancelledError:
        pass

    app["bridge"].destroy_node()
    rclpy.shutdown()
    app["ros_thread"].join(timeout=1.0)


def main():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    print(f"Turtlesim starter listening on http://{HOST}:{PORT}")
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动走迷宫（方向 A）——用路径搜索算法求解，而不是“沿墙走”。

学了机器人课，就该用算法解决问题。本周的迷宫是带环路的网格图（多条通路），
要找最优路线必须用第 9 周学过的 **BFS / Dijkstra / A\*** 在图上搜索。
下面给出一个 **A\*** 参考实现：在迷宫格点图上搜出从起点格到终点格的最短
格序列，再把每个格中心当成路标依次行驶。

接到 server.py 的自动模式里：
    from explorer import Planner
    self.explorer = Planner()
    # 自动模式下：
    move, turn = self.explorer.decide(self.get_state())   # move/turn ∈ [-1,1]
    self.set_command(move, turn)

★ 建议自学并实现：把 A\* 换成 BFS / Dijkstra 对比扩展节点数；加“代价地图”
  让路线远离墙；若假设地图未知，改写成前沿探索 (frontier exploration)。
"""
import heapq
import math
from maze import build_maze

K_TURN = 2.5         # 比例转向增益（归一化）
TURN_FIRST = 0.6     # 朝向误差大于此值时先原地转
REACH_TOL = 0.18     # 到达路标的距离容差（米）


def astar(neighbors, start, goal):
    openq = [(0, start)]
    came = {start: None}
    g = {start: 0}
    h = lambda c: abs(c[0] - goal[0]) + abs(c[1] - goal[1])
    while openq:
        _, cur = heapq.heappop(openq)
        if cur == goal:
            break
        for nxt in neighbors(cur):
            ng = g[cur] + 1
            if nxt not in g or ng < g[nxt]:
                g[nxt] = ng
                came[nxt] = cur
                heapq.heappush(openq, (ng + h(nxt), nxt))
    if goal not in came:
        return []
    path, c = [], goal
    while c is not None:
        path.append(c)
        c = came[c]
    return path[::-1]


class Planner:
    def __init__(self):
        self.m = build_maze()
        self.grid = self.m["grid"]
        self.waypoints = None
        self.idx = 0

    def _to_cell(self, x, y):
        cell = self.grid["cell"]
        ci = min(self.grid["cols"] - 1, max(0, round((x / cell - 1.5) / 2.0)))
        cj = min(self.grid["rows"] - 1, max(0, round((y / cell - 1.5) / 2.0)))
        return (ci, cj)

    def _plan(self, x, y):
        cells = astar(self.m["neighbors"], self._to_cell(x, y), self.m["goal_cell"])
        cc = self.m["cell_center"]
        self.waypoints = [cc(i, j) for (i, j) in cells]
        self.idx = 1 if len(self.waypoints) > 1 else 0

    def decide(self, state):
        if state.get("goal_reached"):
            return 0.0, 0.0
        x, y = state["position"]["x"], state["position"]["y"]
        yaw = state["yaw"]
        if self.waypoints is None:
            self._plan(x, y)
        if not self.waypoints or self.idx >= len(self.waypoints):
            return 0.0, 0.0
        tx, ty = self.waypoints[self.idx]
        if math.hypot(tx - x, ty - y) < REACH_TOL:
            self.idx += 1
            return 0.0, 0.0
        desired = math.atan2(ty - y, tx - x)
        err = math.atan2(math.sin(desired - yaw), math.cos(desired - yaw))
        turn = max(-1.0, min(1.0, K_TURN * err))
        move = 0.0 if abs(err) > TURN_FIRST else 1.0
        return move, turn


if __name__ == "__main__":
    p = Planner()
    p._plan(p.m["start"][0], p.m["start"][1])
    print("planned cells:", len(p.waypoints))

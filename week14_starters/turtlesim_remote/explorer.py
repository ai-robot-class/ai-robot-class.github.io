#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动走迷宫（方向 B）——用路径搜索算法求解，而不是“沿墙走”。

本周对小乌龟的要求是：**用你在第 9 周学过的路径搜索算法自动走出迷宫**。
迷宫是带环路的网格图（多条通路），所以要找“最优/最短”路线，就必须用
BFS / Dijkstra / A* 这类算法在图上搜索——“沿墙走”在有环迷宫里会绕远甚至打转。

下面给出一个 **A\*** 的参考实现：在迷宫的格点图上搜出从起点格到终点格的
最短格序列，再把每个格中心当成路标依次行驶。把它接到桥接程序的自动模式即可。

接入方式（在 turtlesim_web_bridge.py 里）：
    from explorer import Planner
    self.explorer = Planner()
    self.auto = False                       # 自动/手动开关（网页按钮切换）
    # 在控制循环里，若 self.auto:
    lin, ang = self.explorer.decide(self.get_state())
    self.set_command(lin, ang)

★ 你的任务（建议自学并实现）：
  - 把 A\* 换成 BFS / Dijkstra，对比扩展节点数与路径长度；
  - 加入“代价地图”（离墙越近代价越高）让路线更安全；
  - 若假设地图未知，改写成**前沿探索 (frontier exploration)**：边走边建图。
"""
import heapq
import math
from maze import build_maze

LIN = 1.6
ANG_MAX = 2.2
K_ANG = 3.0          # 比例转向增益
TURN_FIRST = 0.6     # 朝向误差大于此值时先原地转
REACH_TOL = 0.12


def astar(neighbors, start, goal):
    """在格图上做 A*（曼哈顿启发）。neighbors(cell)->[cell]，返回格序列。"""
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
        self.m = build_maze()                 # 与桥接程序同一张地图
        self.grid = self.m["grid"]
        self.waypoints = None                 # 规划得到的世界坐标路标列表
        self.idx = 0

    def _to_cell(self, x, y):
        o, c = self.grid["origin"], self.grid["cell"]
        ci = min(self.grid["cols"] - 1, max(0, round((x - o - c / 2) / c)))
        cj = min(self.grid["rows"] - 1, max(0, round((y - o - c / 2) / c)))
        return (ci, cj)

    def _plan(self, x, y):
        start = self._to_cell(x, y)
        cells = astar(self.m["neighbors"], start, self.m["goal_cell"])
        cc = self.m["cell_center"]
        self.waypoints = [(cc(i), cc(j)) for (i, j) in cells]
        self.idx = 1 if len(self.waypoints) > 1 else 0

    def decide(self, state):
        if state.get("rule", {}).get("goal_reached"):
            return 0.0, 0.0
        x, y = state["pose"]["x"], state["pose"]["y"]
        theta = state["pose"]["theta"]
        if x == 0.0 and y == 0.0:
            return 0.0, 0.0
        if self.waypoints is None:
            self._plan(x, y)
        if not self.waypoints or self.idx >= len(self.waypoints):
            return 0.0, 0.0
        tx, ty = self.waypoints[self.idx]
        if math.hypot(tx - x, ty - y) < REACH_TOL:
            self.idx += 1
            return 0.0, 0.0
        desired = math.atan2(ty - y, tx - x)
        err = math.atan2(math.sin(desired - theta), math.cos(desired - theta))
        ang = max(-ANG_MAX, min(ANG_MAX, K_ANG * err))
        lin = 0.0 if abs(err) > TURN_FIRST else LIN   # 误差大先转，对准再走且持续纠偏
        return lin, ang


if __name__ == "__main__":
    p = Planner()
    p._plan(p.m["start"]["x"], p.m["start"]["y"])
    print("planned cells:", len(p.waypoints))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""迷宫配置与生成模块（方向 A：PyBullet 机器狗）。

这是项目里一个**独立的配置/工具文件**，server.py 会 import 它。
把“迷宫长什么样”从“仿真怎么跑”里分离出来，是工程上常见的做法——
你想换地图，只改这一个文件即可，不用动 server.py 的网络/控制逻辑。

核心函数 build_maze() 返回：
  walls : 墙体列表，每堵墙是 (cx, cy, half_x, half_y)  —— 给 PyBullet 建模用
  aabbs : 墙体的轴对齐包围盒 (min_x, min_y, max_x, max_y) —— 给碰撞检测用
  start : 机器狗出生点 (x, y)
  goal  : 终点 (x, y, radius)
  size  : 迷宫边长（米），外边界是 [0, size] x [0, size]

迷宫用“递归回溯法”先生成生成树，再随机“编织(braid)”打通一部分墙，制造
**多条通路与环路**——这样最短路径不唯一，需要 BFS / Dijkstra / A* 等
路径搜索算法才能求最优解。固定随机种子保证每次运行、每次截图都一致。
"""
import random

# ---- 可调参数：想要更大/更难的迷宫，改这里即可 ----
COLS = 6            # 横向格子数
ROWS = 6            # 纵向格子数
CELL = 1.0          # 每格边长（米）
WALL_HEIGHT = 0.45  # 墙体半高（实际墙高 = 2 * WALL_HEIGHT）
SEED = 20260614     # 固定随机种子 -> 迷宫可复现
BRAID = 0.22        # 额外打通墙体的比例（0=无环完美迷宫，越大环路越多）


def _carve_grid(cols, rows, seed):
    """递归回溯法生成完美迷宫，返回 (2*rows+1) x (2*cols+1) 的布尔网格。

    True = 墙，False = 通路。
    """
    gw, gh = 2 * cols + 1, 2 * rows + 1
    grid = [[True] * gw for _ in range(gh)]
    rng = random.Random(seed)
    visited = [[False] * cols for _ in range(rows)]

    def cell_to_grid(cx, cy):
        return 2 * cx + 1, 2 * cy + 1

    stack = [(0, 0)]
    visited[0][0] = True
    gx, gy = cell_to_grid(0, 0)
    grid[gy][gx] = False

    while stack:
        cx, cy = stack[-1]
        neighbors = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx]:
                neighbors.append((nx, ny, dx, dy))
        if not neighbors:
            stack.pop()
            continue
        nx, ny, dx, dy = rng.choice(neighbors)
        visited[ny][nx] = True
        cgx, cgy = cell_to_grid(cx, cy)
        grid[cgy + dy][cgx + dx] = False        # 打通中间的墙
        ngx, ngy = cell_to_grid(nx, ny)
        grid[ngy][ngx] = False                  # 邻居格变通路
        stack.append((nx, ny))

    # braid：随机再打通一些“格间墙”，制造环路（不动外边界与立柱）
    for gy in range(1, gh - 1):
        for gx in range(1, gw - 1):
            if (gx % 2) == (gy % 2):
                continue                         # 跳过格中心与立柱
            if grid[gy][gx] and rng.random() < BRAID:
                grid[gy][gx] = False
    return grid


def _merge_row_runs(grid, cell):
    """把每一行里连续的墙块合并成一堵长墙，减少物体数量、外观更整洁。"""
    gh = len(grid)
    gw = len(grid[0])
    walls, aabbs = [], []
    for gy in range(gh):
        gx = 0
        while gx < gw:
            if grid[gy][gx]:
                run_start = gx
                while gx < gw and grid[gy][gx]:
                    gx += 1
                run_end = gx  # exclusive
                min_x, max_x = run_start * cell, run_end * cell
                min_y, max_y = gy * cell, (gy + 1) * cell
                walls.append(((min_x + max_x) / 2.0, (min_y + max_y) / 2.0,
                              (max_x - min_x) / 2.0, (max_y - min_y) / 2.0))
                aabbs.append((min_x, min_y, max_x, max_y))
            else:
                gx += 1
    return walls, aabbs


def build_maze(cols=COLS, rows=ROWS, cell=CELL, seed=SEED):
    """生成迷宫，返回一个字典。"""
    grid = _carve_grid(cols, rows, seed)
    walls, aabbs = _merge_row_runs(grid, cell)
    size = (2 * cols + 1) * cell

    def cell_center(cx, cy):
        return ((2 * cx + 1) * cell + cell / 2.0, (2 * cy + 1) * cell + cell / 2.0)

    def neighbors(c):
        cx, cy = c
        out = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                wgx, wgy = 2 * cx + 1 + dx, 2 * cy + 1 + dy   # 两格之间的墙格
                if not grid[wgy][wgx]:
                    out.append((nx, ny))
        return out

    start = cell_center(0, 0)
    gxc, gyc = cell_center(cols - 1, rows - 1)
    goal = (gxc, gyc, cell * 0.45)
    return {
        "walls": walls,
        "aabbs": aabbs,
        "start": start,
        "goal": goal,
        "size": size,
        "wall_height": WALL_HEIGHT,
        "grid": {"cols": cols, "rows": rows, "cell": cell},
        "start_cell": (0, 0),
        "goal_cell": (cols - 1, rows - 1),
        "neighbors": neighbors,
        "cell_center": cell_center,
    }


if __name__ == "__main__":
    m = build_maze()
    print(f"迷宫边长 {m['size']}m, 墙体 {len(m['walls'])} 段")
    print("起点", m["start"], "终点", m["goal"])
    # 简单连通性校验
    from collections import deque
    q = deque([m["start_cell"]]); seen = {m["start_cell"]}
    while q:
        c = q.popleft()
        for n in m["neighbors"](c):
            if n not in seen:
                seen.add(n); q.append(n)
    print("可达格子", len(seen), "/", COLS * ROWS,
          "到终点可达:", m["goal_cell"] in seen)

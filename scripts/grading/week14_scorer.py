"""第 14 周小组项目专项评分（手机遥控 + 迷宫探索）。"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .config import CODE_EXTS, DOC_EXTS, IMAGE_EXTS, VIDEO_EXTS
from .rule_scorer import analyze_screenshots

WEEK14_PDF_RE = re.compile(r"^week14_[^/\\]+\.pdf$", re.IGNORECASE)

PYBULLET_CORE = {"server.py", "maze.py", "explorer.py", "index.html"}
TURTLE_CORE = {"turtlesim_web_bridge.py", "index.html"}
TURTLE_OPTIONAL = {"explorer.py", "maze.py"}

ADVANCED_KEYWORDS = [
    "bfs", "astar", "a_star", "dijkstra", "path", "explore", "explorer",
    "collision", "撞墙", "路径", "自动", "agent", "openclaw", "wall_follow",
    "right_hand", "右手法则", "visited", "frontier", "queue",
]

LINK_KEYWORDS = [
    "forward", "backward", "left", "right", "stop",
    "前进", "后退", "左转", "右转", "停止",
    "fetch(", "websocket", "socket", "tailscale", "http.server",
]


def _basename(path: str) -> str:
    return path.split("/")[-1].lower()


def _collect_blobs(files: list[dict]) -> list[dict]:
    return [f for f in files if f.get("type") == "blob"]


def _detect_direction(basenames: set[str], all_paths: list[str]) -> str:
    pybullet_hits = sum(1 for n in PYBULLET_CORE if n in basenames)
    turtle_hits = sum(1 for n in TURTLE_CORE if n in basenames)
    joined = " ".join(all_paths).lower()
    if "pybullet" in joined or "laikago" in joined or pybullet_hits >= 2:
        return "pybullet"
    if "turtle" in joined or "ros2" in joined or turtle_hits >= 1:
        return "turtlesim"
    if pybullet_hits >= turtle_hits:
        return "pybullet"
    return "turtlesim"


def _scan_code_signals(
    blobs: list[dict],
    owner: str,
    repo: str,
    fetch_file_content,
    *,
    max_files: int = 8,
) -> dict:
    signals = {
        "link_keywords": 0,
        "advanced_keywords": 0,
        "has_explorer_logic": False,
        "has_maze_logic": False,
        "has_html_controls": False,
        "files_scanned": 0,
    }
    candidates = []
    for f in blobs:
        name = _basename(f["path"])
        if not name.endswith(CODE_EXTS) and name != "index.html":
            continue
        priority = 0
        if name in {"server.py", "turtlesim_web_bridge.py", "explorer.py", "maze.py", "index.html"}:
            priority = 3
        elif name.endswith(".py") or name.endswith(".html"):
            priority = 2
        candidates.append((priority, f))
    candidates.sort(key=lambda x: (-x[0], x[1]["path"]))

    for _, f in candidates[:max_files]:
        content = fetch_file_content(owner, repo, f["path"]) or ""
        if not content:
            continue
        signals["files_scanned"] += 1
        lower = content.lower()
        name = _basename(f["path"])
        if name == "index.html":
            if any(k in lower for k in ["button", "touch", "onclick", "keydown", "addEventListener"]):
                signals["has_html_controls"] = True
        if name == "explorer.py" and len(content.strip()) > 80:
            signals["has_explorer_logic"] = True
        if name == "maze.py" and len(content.strip()) > 50:
            signals["has_maze_logic"] = True
        for kw in LINK_KEYWORDS:
            if kw.lower() in lower:
                signals["link_keywords"] += 1
        for kw in ADVANCED_KEYWORDS:
            if kw.lower() in lower:
                signals["advanced_keywords"] += 1
    return signals


def analyze_week14(
    week_info: dict,
    files: list[dict],
    anchor: str | None,
    owner: str,
    repo: str,
    path_commits: list,
    fallback_commits: list,
    fetch_file_content,
) -> dict:
    result = {
        "submitted": False,
        "actual_path": anchor,
        "content_score": 0,
        "attitude_score": 0,
        "rule_content_score": 0,
        "rule_attitude_score": 0,
        "ai_content_score": None,
        "ai_attitude_score": None,
        "readme_excerpt": "",
        "details": {},
        "comments": [],
        "improvement_suggestions": [],
        "week14_project": {
            "direction": None,
            "rubric": {},
            "project_score": 0,
            "pdf_files": [],
            "pdf_valid": False,
            "videos": [],
            "images": [],
            "code_files": [],
            "missing_core": [],
        },
    }

    if not files:
        result["comments"].append("❌ 未提交第14周小组项目")
        result["improvement_suggestions"].append(
            "请在仓库根目录创建 week14/ 文件夹，提交代码、演示视频和 PDF 报告书。"
        )
        result["improvement_suggestions"].append(
            "报告书命名规范：week14_组名或学号.pdf（例如 week14_team3.pdf）。"
        )
        return result

    blobs = _collect_blobs(files)
    basenames = {_basename(f["path"]) for f in blobs}
    all_paths = [f["path"] for f in blobs]

    pdf_in_week14 = []
    pdf_wrong_name = []
    for f in blobs:
        name = f["path"].split("/")[-1]
        if not name.lower().endswith(".pdf"):
            continue
        rel = f["path"]
        if anchor and rel.startswith(anchor + "/"):
            rel = rel[len(anchor) + 1 :]
        elif anchor and rel == anchor:
            continue
        if WEEK14_PDF_RE.match(name):
            pdf_in_week14.append(f["path"])
        else:
            pdf_wrong_name.append(name)

    videos = [f["path"] for f in blobs if _basename(f["path"]).endswith(VIDEO_EXTS)]
    images = [f["path"] for f in blobs if _basename(f["path"]).endswith(IMAGE_EXTS)]
    code_files = [
        f["path"] for f in blobs
        if _basename(f["path"]).endswith(CODE_EXTS) or _basename(f["path"]) == "index.html"
    ]

    direction = _detect_direction(basenames, all_paths)
    core_set = PYBULLET_CORE if direction == "pybullet" else TURTLE_CORE | TURTLE_OPTIONAL
    missing_core = sorted(n for n in (PYBULLET_CORE if direction == "pybullet" else TURTLE_CORE) if n not in basenames)

    result["submitted"] = True
    result["comments"].append(f"✅ 已提交 week14 小组项目（路径: {anchor}）")
    result["comments"].append(
        f"📌 检测到方向: {'A PyBullet 机器狗' if direction == 'pybullet' else 'B turtlesim 小乌龟'}"
    )

    img_stats = analyze_screenshots(files)
    code_signals = _scan_code_signals(blobs, owner, repo, fetch_file_content)

    rubric = {
        "link_chain": 0,      # /30
        "maze_explore": 0,  # /25
        "advanced": 0,      # /25
        "engineering": 0,   # /10
        "report_demo": 0,   # /10
    }
    suggestions: list[str] = []

    # --- 链路打通 30 ---
    link = 0
    if "index.html" in basenames:
        link += 8
        result["comments"].append("🌐 有遥控器网页 index.html (+8)")
    else:
        suggestions.append("缺少 index.html：需实现手机遥控网页（前进/后退/左转/右转/停止）。")
    bridge = "server.py" if direction == "pybullet" else "turtlesim_web_bridge.py"
    if bridge in basenames:
        link += 10
        result["comments"].append(f"🔗 有桥接程序 {bridge} (+10)")
    else:
        suggestions.append(f"缺少 {bridge}：网络接收与机器人控制应写在同一常驻程序中。")
    if code_signals["has_html_controls"]:
        link += 6
        result["comments"].append("🎮 网页含交互控件 (+6)")
    elif "index.html" in basenames:
        suggestions.append("index.html 建议加入按钮或触摸事件，松手时发送 stop 命令。")
    if code_signals["link_keywords"] >= 3:
        link += 6
        result["comments"].append("📡 代码含控制/网络关键词 (+6)")
    elif bridge in basenames:
        suggestions.append("建议在桥接程序中实现 forward/backward/left/right/stop 四类动作。")
    rubric["link_chain"] = min(link, 30)

    # --- 迷宫探索 25 ---
    maze = 0
    if "maze.py" in basenames or code_signals["has_maze_logic"]:
        maze += 12
        result["comments"].append("🗺️ 有迷宫模块 maze.py (+12)")
    else:
        suggestions.append("缺少 maze.py 或迷宫配置：需自定义迷宫地图并支持探索任务。")
    if "explorer.py" in basenames or code_signals["has_explorer_logic"]:
        maze += 8
        result["comments"].append("🧭 有 explorer.py 探索逻辑 (+8)")
    else:
        if direction == "turtlesim":
            suggestions.append("方向 B 必须实现自动探索：在 explorer.py 中用 BFS/A* 或 Agent 走出迷宫。")
        else:
            suggestions.append("建议添加 explorer.py 或在 server.py 中实现迷宫探索/到达终点。")
    if img_stats["total"] >= 1 or len(videos) >= 1:
        maze += 5
        result["comments"].append("📷 有运行截图或演示视频 (+5)")
    rubric["maze_explore"] = min(maze, 25)

    # --- 进阶功能 25 ---
    adv = 0
    if code_signals["advanced_keywords"] >= 4:
        adv += 15
        result["comments"].append("🚀 代码含路径规划/自动探索关键词 (+15)")
    elif code_signals["advanced_keywords"] >= 1:
        adv += 8
        result["comments"].append("🔍 有部分进阶探索实现 (+8)")
        suggestions.append("进阶加分：实现 BFS/A* 自动探索、碰撞处理或路径可视化记录。")
    else:
        suggestions.append("进阶功能不足：小乌龟方向必须自动走出迷宫；4人及以上机器狗组也必须自动探索。")
    if any(k in " ".join(all_paths).lower() for k in ["collision", "crash", "撞墙", "碰撞"]):
        adv += 5
        result["comments"].append("💥 含碰撞处理 (+5)")
    if any(k in " ".join(all_paths).lower() for k in ["path", "trail", "轨迹", "record"]):
        adv += 5
        result["comments"].append("📈 含路径记录 (+5)")
    rubric["advanced"] = min(adv, 25)

    # --- 工程规范 10 ---
    eng = 0
    if anchor and anchor.lower().replace("\\", "/").rstrip("/").endswith("week14"):
        eng += 4
        result["comments"].append("📁 目录规范 week14/ (+4)")
    else:
        suggestions.append("请将项目放在 week14/ 目录下（当前路径可能不规范）。")
    if len(missing_core) == 0:
        eng += 4
        result["comments"].append("✅ 核心文件齐全 (+4)")
    else:
        suggestions.append(f"缺少核心文件: {', '.join(missing_core)}")
    if len(code_files) >= 3:
        eng += 2
        result["comments"].append("💻 代码结构完整 (+2)")
    rubric["engineering"] = min(eng, 10)

    # --- 报告与展示 10 ---
    rep = 0
    if pdf_in_week14:
        rep += 7
        result["comments"].append(f"📄 PDF 报告命名规范 ({len(pdf_in_week14)} 份) (+7)")
    elif pdf_wrong_name:
        rep += 3
        result["comments"].append("⚠️  有 PDF 但命名不规范 (+3)")
        suggestions.append(
            f"报告书应命名为 week14_XXXX.pdf，当前: {', '.join(pdf_wrong_name[:3])}"
        )
    else:
        suggestions.append("缺少 PDF 报告书：按讲义 14.9 节撰写，命名为 week14_组名.pdf。")
    if videos:
        rep += 3
        result["comments"].append(f"🎬 有演示视频 ({len(videos)} 个) (+3)")
    else:
        suggestions.append("缺少演示视频：建议 1–2 分钟，展示手机遥控 + 迷宫探索全过程。")
    rubric["report_demo"] = min(rep, 10)

    project_score = sum(rubric.values())
    content_score = round(project_score * 0.70)
    content_score = min(content_score, 70)

    # 态度分：提交完整性 + commit + 时效
    attitude = 8
    if pdf_in_week14 and videos and len(missing_core) == 0:
        attitude += 8
        result["comments"].append("⭐ 交付物较完整 (+8)")
    elif pdf_in_week14 or videos:
        attitude += 5
        result["comments"].append("⭐ 部分交付物齐全 (+5)")
    else:
        suggestions.append("交付清单：代码 + 演示视频 + week14_XXXX.pdf 报告 + 分工说明。")

    related_commits = path_commits or []
    if not related_commits and fallback_commits:
        related_commits = [
            {"commit": {"author": {"date": c["commit"]["author"]["date"]}}, "sha": c["sha"]}
            for c in fallback_commits[:5]
            if isinstance(c, dict)
        ]
    commit_count = len(related_commits)
    if commit_count >= 3:
        attitude += 8
        result["comments"].append(f"⭐ 多次迭代提交 ({commit_count} 次, +8)")
    elif commit_count >= 1:
        attitude += 5
        result["comments"].append(f"⭐ 有提交记录 ({commit_count} 次, +5)")
    else:
        suggestions.append("建议分阶段 commit：链路打通 → 迷宫 → 自动探索 → 报告。")

    if related_commits:
        try:
            last_date = related_commits[0]["commit"]["author"]["date"]
            last = datetime.fromisoformat(last_date.replace("Z", "+00:00"))
            due = datetime.fromisoformat(week_info["due_date"]).replace(tzinfo=timezone.utc)
            days_diff = (due - last).days
            if days_diff >= 0:
                attitude += 6
                result["comments"].append("✅ 按时或提前完成 (+6)")
            elif days_diff >= -7:
                attitude += 4
                result["comments"].append(f"⏰ 稍延迟 {-days_diff} 天 (+4)")
            else:
                attitude += 2
        except (KeyError, ValueError, TypeError):
            pass

    attitude_score = min(attitude, 30)

    result["rule_content_score"] = content_score
    result["rule_attitude_score"] = attitude_score
    result["content_score"] = content_score
    result["attitude_score"] = attitude_score
    result["improvement_suggestions"] = suggestions[:8]
    result["week14_project"] = {
        "direction": direction,
        "rubric": rubric,
        "project_score": project_score,
        "pdf_files": pdf_in_week14,
        "pdf_valid": bool(pdf_in_week14),
        "pdf_wrong_names": pdf_wrong_name,
        "videos": videos,
        "images": images[:20],
        "code_files": code_files,
        "missing_core": missing_core,
        "code_signals": code_signals,
    }
    result["details"] = {
        "project_score": project_score,
        "direction": direction,
        "pdf_count": len(pdf_in_week14),
        "video_count": len(videos),
        "image_count": img_stats["total"],
        "image_paths": img_stats.get("paths", []),
        "code_count": len(code_files),
        "commit_count": commit_count,
        "total_files": len(blobs),
    }
    return result


def build_week14_rankings(students: list[dict]) -> list[dict]:
    """按 week14 项目分排名（仅已提交且仓库可访问的学生）。"""
    ranked = []
    for s in students:
        if not s.get("repo_exists"):
            continue
        wk = (s.get("weeks") or {}).get("week14") or {}
        if not wk.get("submitted"):
            continue
        proj = wk.get("week14_project") or {}
        ranked.append(
            {
                "github_id": s["github_id"],
                "repo_url": s.get("repo_url", ""),
                "raw_score": wk.get("raw_score", 0),
                "project_score": proj.get("project_score", wk.get("raw_score", 0)),
                "direction": proj.get("direction"),
                "rubric": proj.get("rubric", {}),
                "pdf_valid": proj.get("pdf_valid", False),
                "improvement_suggestions": wk.get("improvement_suggestions", []),
            }
        )
    ranked.sort(key=lambda x: (-x["project_score"], -x["raw_score"], x["github_id"]))
    for i, item in enumerate(ranked, 1):
        item["rank"] = i
    return ranked

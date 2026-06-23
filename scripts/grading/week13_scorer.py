"""第 13 周专项评分：四足机器人入门（PyBullet 步态 / week13_walk）。"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .config import CODE_EXTS, DOC_EXTS, IMAGE_EXTS, VIDEO_EXTS
from .rule_scorer import analyze_screenshots

WEEK13_ANCHOR_NAMES = ("week13_walk", "week13")

WALK_CORE = {"quadruped_walk.py", "ai_chat_log.md", "reflection.md"}
WALK_OPTIONAL = {"readme.md"}

PYBULLET_KEYWORDS = [
    "pybullet", "laikago", "trot", "gait", "quadruped", "步态", "机器狗", "四足",
    "inverse kinematics", "ik", "stance", "swing", "foot", "leg_joints",
]


def _basename(path: str) -> str:
    return path.split("/")[-1].lower()


def _collect_blobs(files: list[dict]) -> list[dict]:
    return [f for f in files if f.get("type") == "blob"]


def _scan_code_content(
    blobs: list[dict],
    owner: str,
    repo: str,
    fetch_file_content,
    *,
    max_files: int = 6,
) -> dict:
    signals = {"pybullet_hits": 0, "has_walk_logic": False, "files_scanned": 0}
    candidates = []
    for f in blobs:
        name = _basename(f["path"])
        if not name.endswith(CODE_EXTS):
            continue
        priority = 3 if "quadruped" in name or name.endswith("_walk.py") else 1
        candidates.append((priority, f))
    candidates.sort(key=lambda x: (-x[0], x[1]["path"]))

    for _, f in candidates[:max_files]:
        content = fetch_file_content(owner, repo, f["path"]) or ""
        if not content:
            continue
        signals["files_scanned"] += 1
        lower = content.lower()
        for kw in PYBULLET_KEYWORDS:
            if kw.lower() in lower:
                signals["pybullet_hits"] += 1
        if len(content) > 200 and any(k in lower for k in ["step(", "gait", "trot", "walk", "leg"]):
            signals["has_walk_logic"] = True
    return signals


def analyze_week13(
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
        "week13_lab": {
            "anchor_kind": None,
            "has_walk_py": False,
            "has_ai_log": False,
            "has_reflection": False,
            "missing_core": [],
        },
    }

    if not files:
        result["comments"].append("❌ 未提交第13周四足机器人作业")
        result["improvement_suggestions"].append(
            "请在 week13_walk/ 目录提交：quadruped_walk.py、ai_chat_log.md、reflection.md（见讲义 13.7）。"
        )
        result["improvement_suggestions"].append(
            "可选：将 fork 后的 week13 仓库作为 submodule 添加到 week13/，用于强化学习拓展。"
        )
        return result

    blobs = _collect_blobs(files)
    basenames = {_basename(f["path"]) for f in blobs}
    anchor_kind = None
    if anchor:
        low = anchor.lower().replace("\\", "/").rstrip("/")
        if low.endswith("week13_walk") or "/week13_walk" in low or low == "week13_walk":
            anchor_kind = "week13_walk"
        elif low.endswith("week13") or "/week13" in low or low == "week13":
            anchor_kind = "week13"

    result["submitted"] = True
    result["comments"].append(f"✅ 已提交第13周作业（路径: {anchor}）")

    img_stats = analyze_screenshots(files)
    code_signals = _scan_code_content(blobs, owner, repo, fetch_file_content)

    has_walk_py = any(
        n.endswith(".py") and ("quadruped" in n or "walk" in n or "trot" in n or "gait" in n)
        for n in basenames
    ) or any(n.endswith(".py") for n in basenames)
    has_ai_log = "ai_chat_log.md" in basenames or any("ai" in n and n.endswith(".md") for n in basenames)
    has_reflection = "reflection.md" in basenames or any("reflection" in n for n in basenames)
    videos = [f["path"] for f in blobs if _basename(f["path"]).endswith(VIDEO_EXTS)]
    missing_core = [n for n in WALK_CORE if n not in basenames and anchor_kind == "week13_walk"]

    content = 20
    result["comments"].append("✅ 有第13周提交 (+20)")

    if anchor_kind == "week13_walk":
        content += 8
        result["comments"].append("📁 目录规范 week13_walk/ (+8)")
    elif anchor_kind == "week13":
        content += 5
        result["comments"].append("📁 使用 week13/ 目录（submodule/拓展） (+5)")
    else:
        result["improvement_suggestions"].append(
            "建议按讲义使用 week13_walk/ 目录存放必做作业（quadruped_walk.py 等）。"
        )

    if has_walk_py:
        content += 15
        result["comments"].append("🐕 有四足机器人 Python 代码 (+15)")
    else:
        result["improvement_suggestions"].append(
            "缺少 quadruped_walk.py：完成 PyBullet Trot/行走调试并保存最终代码。"
        )

    if code_signals["pybullet_hits"] >= 3 or code_signals["has_walk_logic"]:
        content += 10
        result["comments"].append("⚙️ 代码含步态/PyBullet 实现 (+10)")
    elif has_walk_py:
        result["improvement_suggestions"].append(
            "代码可继续完善：关节映射、IK、Trot 步态相位、站立/行走阶段切换。"
        )

    if has_ai_log:
        content += 8
        result["comments"].append("💬 有 AI 对话记录 ai_chat_log.md (+8)")
    else:
        result["improvement_suggestions"].append(
            "补充 ai_chat_log.md：记录与 AI 协作调试的完整对话（≥5 轮）。"
        )

    if has_reflection:
        content += 7
        result["comments"].append("📝 有 reflection.md 反思 (+7)")
    else:
        result["improvement_suggestions"].append(
            "补充 reflection.md（≥300 字）：回答讲义中的 3 个必答反思问题。"
        )

    if img_stats["total"] >= 2 or videos:
        content += 5
        result["comments"].append("📷 有运行截图或演示视频 (+5)")
    elif img_stats["total"] >= 1:
        content += 3
        result["comments"].append("📷 有截图 (+3)")
    else:
        result["improvement_suggestions"].append("添加机器狗站立/行走的 GIF 或截图作为运行证据。")

    readme_blob = next((f for f in blobs if _basename(f["path"]) == "readme.md"), None)
    if readme_blob:
        excerpt = fetch_file_content(owner, repo, readme_blob["path"]) or ""
        result["readme_excerpt"] = excerpt[:2500]
        if len(excerpt) > 500:
            content += 2
            result["comments"].append("📄 README 较完整 (+2)")

    content_score = min(content, 70)

    attitude = 8
    if has_walk_py and has_ai_log and has_reflection:
        attitude += 10
        result["comments"].append("⭐ 必做三件套较齐全 (+10)")
    elif has_walk_py:
        attitude += 6
        result["comments"].append("⭐ 有核心代码 (+6)")

    related_commits = path_commits or []
    if not related_commits and fallback_commits:
        related_commits = [
            {"commit": {"author": {"date": c["commit"]["author"]["date"]}}, "sha": c["sha"]}
            for c in fallback_commits[:5]
            if isinstance(c, dict)
        ]
    commit_count = len(related_commits)
    if commit_count >= 3:
        attitude += 6
        result["comments"].append(f"⭐ 多次迭代 ({commit_count} 次, +6)")
    elif commit_count >= 1:
        attitude += 4
        result["comments"].append(f"⭐ 有提交 ({commit_count} 次, +4)")

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
    result["week13_lab"] = {
        "anchor_kind": anchor_kind,
        "has_walk_py": has_walk_py,
        "has_ai_log": has_ai_log,
        "has_reflection": has_reflection,
        "missing_core": missing_core,
        "video_count": len(videos),
        "image_count": img_stats["total"],
    }
    result["details"] = {
        "anchor_kind": anchor_kind,
        "has_walk_py": has_walk_py,
        "has_ai_log": has_ai_log,
        "has_reflection": has_reflection,
        "video_count": len(videos),
        "image_count": img_stats["total"],
        "code_signals": code_signals,
        "commit_count": commit_count,
        "total_files": len(blobs),
    }
    return result

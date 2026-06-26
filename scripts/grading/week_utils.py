from __future__ import annotations

import re

from .config import IMAGE_EXTS, WEEKS

CN_DIGITS = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "十一": 11, "十二": 12, "十三": 13, "十四": 14,
}

WEEK_TOPIC_KEYWORDS = {
    "week2": (
        "ros2", "ubuntu", "wsl", "install", "环境", "安装", "配置",
    ),
    "week3": (
        "git", "github", "command", "terminal", "命令", "仓库",
    ),
    "week4": (
        "python", "turtle", "turtlesim", "simulation", "仿真",
        "小乌龟",
    ),
    "week5": (
        "kinematic", "kinematics", "square", "circle", "move", "运动学",
        "正方形", "圆形", "轨迹",
    ),
    "week6": (
        "kitti", "sensor", "lidar", "velodyne", "rviz", "rqt", "传感器",
        "点云",
    ),
    "week7": (
        "markdown", "整理", "笔记",
    ),
    "week8": (
        "docker", "container", "容器",
    ),
    "week10": (
        "opencv", "cv", "image", "vision", "颜色", "图像",
    ),
    "week11": (
        "pages", "githubpage", "githubpages", "website", "web", "网页",
        "部署",
    ),
    "week12": (
        "aruco", "camera", "voice", "speech", "audio", "摄像头", "语音",
        "识别", "距离",
    ),
    "week13": (
        "quadruped", "laikago", "dog", "pybullet", "gait", "trot",
        "四足", "机器狗", "步态",
    ),
    "week14": (
        "maze", "remote", "server", "explorer", "bridge", "迷宫", "遥控",
        "项目",
    ),
}

COURSE_DATE_TO_WEEK = {
    "2026-03-11": "week2",
    "2026-03-18": "week3",
    "2026-03-25": "week4",
    "2026-04-01": "week5",
    "2026-04-08": "week6",
    "2026-04-15": "week7",
    "2026-04-22": "week8",
    "2026-05-06": "week10",
    "2026-05-13": "week11",
    "2026-05-20": "week12",
    "2026-05-27": "week13",
    "2026-06-03": "week14",
    "2026-06-10": "week14",
}


def infer_week_from_date(name: str | None) -> str | None:
    if not name:
        return None
    s = name.lower()
    patterns = [
        r"(2026)[-_\.年 ](0?[3-6])[-_\.月 ](3[01]|[12]\d|0?[1-9])",
        r"\b(0?[3-6])[-_\.月 ](3[01]|[12]\d|0?[1-9])\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, s)
        if not m:
            continue
        if len(m.groups()) == 3:
            year, month, day = m.groups()
        else:
            year = "2026"
            month, day = m.groups()
        date_key = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        if date_key in COURSE_DATE_TO_WEEK:
            return COURSE_DATE_TO_WEEK[date_key]
    return None


def normalize_week_id(name: str | None) -> str | None:
    if not name:
        return None
    s = name.lower()

    m = re.search(r"week[\s_\-]*?(\d+)", s)
    if m:
        return f"week{int(m.group(1))}"

    m = re.search(r"(\d+)[\s_\-]*?week", s)
    if m:
        return f"week{int(m.group(1))}"

    m = re.search(r"homework[\s_\-]*?(\d+)", s)
    if m:
        return f"week{int(m.group(1))}"

    m = re.search(r"\bhw[\s_\-]*?(\d+)", s)
    if m:
        return f"week{int(m.group(1))}"

    m = re.search(r"\bw(\d+)\b", s)
    if m:
        return f"week{int(m.group(1))}"

    m = re.search(r"第\s*(\d+)\s*周", name)
    if m:
        return f"week{int(m.group(1))}"

    m = re.search(r"\b(\d+)\s*周\b", name)
    if m:
        return f"week{int(m.group(1))}"

    m = re.search(r"(?:第\s*(\d+)\s*章|chapter[\s_\-]*?(\d+))", s)
    if m:
        n = m.group(1) or m.group(2)
        if n:
            return f"week{int(n)}"

    m = re.search(r"第([一二三四五六七八九十]+)周", name)
    if m and m.group(1) in CN_DIGITS:
        return f"week{CN_DIGITS[m.group(1)]}"

    return None


def group_files_by_week(tree: list[dict]):
    week_files = {wk: [] for wk in WEEKS}
    week_anchor = {wk: None for wk in WEEKS}
    assigned_paths = set()

    for item in tree:
        path = item.get("path", "")
        if not path:
            continue
        parts = path.split("/")
        for i, segment in enumerate(parts):
            wk = normalize_week_id(segment)
            if wk and wk in week_files:
                week_files[wk].append(item)
                assigned_paths.add(path)
                anchor = "/".join(parts[: i + 1])
                cur = week_anchor[wk]
                if cur is None or len(anchor) < len(cur):
                    week_anchor[wk] = anchor
                break

    topic_groups: dict[tuple[str, str], list[dict]] = {}
    for item in tree:
        path = item.get("path", "")
        if not path or path in assigned_paths:
            continue
        date_wk = infer_week_from_date(path)
        if date_wk in WEEKS:
            parts = path.split("/")
            anchor = parts[0] if len(parts) > 1 else "."
            topic_groups.setdefault((date_wk, anchor), []).append(item)
            continue
        path_lower = path.lower()
        for wk, keywords in WEEK_TOPIC_KEYWORDS.items():
            if any(keyword in path_lower for keyword in keywords):
                parts = path.split("/")
                anchor = parts[0] if len(parts) > 1 else "."
                topic_groups.setdefault((wk, anchor), []).append(item)
                break

    for (wk, anchor), items in topic_groups.items():
        if not items:
            continue
        has_evidence = any(
            item.get("type") == "blob"
            and (
                item.get("path", "").lower().endswith(IMAGE_EXTS)
                or item.get("path", "").lower().endswith((".md", ".py", ".ipynb", ".pdf", ".mp4"))
            )
            for item in items
        )
        if not has_evidence:
            continue
        week_files[wk].extend(items)
        cur = week_anchor[wk]
        if cur is None or (anchor != "." and len(anchor) < len(cur)):
            week_anchor[wk] = anchor

    return week_files, week_anchor


def find_readme_in_files(files: list[dict], anchor: str | None):
    best = None
    for f in files:
        if f.get("type") != "blob":
            continue
        path = f["path"]
        name = path.split("/")[-1].lower()
        if name != "readme.md":
            continue
        if best is None:
            best = f
        elif anchor and path.startswith(anchor):
            if path.count("/") < best["path"].count("/"):
                best = f
    return best

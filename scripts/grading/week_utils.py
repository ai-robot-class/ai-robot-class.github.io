from __future__ import annotations

import re

from .config import WEEKS

CN_DIGITS = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "十一": 11, "十二": 12, "十三": 13, "十四": 14,
}


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

    for item in tree:
        path = item.get("path", "")
        if not path:
            continue
        parts = path.split("/")
        for i, segment in enumerate(parts):
            wk = normalize_week_id(segment)
            if wk and wk in week_files:
                week_files[wk].append(item)
                anchor = "/".join(parts[: i + 1])
                cur = week_anchor[wk]
                if cur is None or len(anchor) < len(cur):
                    week_anchor[wk] = anchor
                break

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

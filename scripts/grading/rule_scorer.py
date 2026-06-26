from __future__ import annotations

import re
from datetime import datetime, timezone

import requests

from .config import (
    CODE_EXTS,
    DOC_EXTS,
    IMAGE_EXTS,
    SCREENSHOT_KEYWORDS,
    VIDEO_EXTS,
)
from .week_utils import find_readme_in_files


def check_pages_alive(url: str | None):
    if not url:
        return False, None
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True)
        if resp.status_code == 200 and len(resp.text) > 200:
            return True, resp.text
    except requests.RequestException:
        pass
    return False, None


def audit_pages_health(pages_url: str, html: str | None, owner: str, repo: str):
    report = {
        "total_images": 0,
        "broken_images": [],
        "broken_links": [],
        "has_title": False,
        "has_style": False,
        "has_content": False,
        "word_count": 0,
        "issues": [],
        "suggestions": [],
        "score": 0,
    }
    if not html:
        return report

    title_match = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    if title_match and len(title_match.group(1).strip()) > 3:
        report["has_title"] = True
    else:
        report["issues"].append("缺少有意义的 <title> 标签")

    if "<style" in html.lower() or "stylesheet" in html.lower():
        report["has_style"] = True
    else:
        report["suggestions"].append("可以加入 CSS 美化页面")

    text_only = re.sub(r"<[^>]+>", " ", html)
    text_only = re.sub(r"\s+", " ", text_only).strip()
    report["word_count"] = len(text_only)
    if len(text_only) > 200:
        report["has_content"] = True

    img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    md_imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", html)
    pages_host = f"https://{owner}.github.io/{repo}/"
    base = pages_url.rstrip("/") + "/"

    image_sources = [(src, pages_url) for src in img_tags + md_imgs]
    checked = 0
    for src, from_url in image_sources[:10]:
        if src.startswith("data:"):
            continue
        if src.startswith("http://") or src.startswith("https://"):
            full = src
        elif src.startswith("//"):
            full = "https:" + src
        elif src.startswith("/"):
            full = f"https://{owner}.github.io" + src
        else:
            from_dir = from_url.rsplit("/", 1)[0] + "/"
            full = from_dir + src
        checked += 1
        try:
            rr = requests.head(full, timeout=6, allow_redirects=True)
            if rr.status_code >= 400:
                rr = requests.get(full, timeout=6, stream=True, allow_redirects=True)
                rr.close()
            if rr.status_code >= 400:
                report["broken_images"].append(
                    {"src": src, "resolved": full, "status": rr.status_code}
                )
        except requests.RequestException as exc:
            report["broken_images"].append(
                {"src": src, "resolved": full, "error": str(exc)[:60]}
            )

    report["total_images"] = len(image_sources)
    if report["broken_images"]:
        report["issues"].append(
            f"有 {len(report['broken_images'])} 张图片无法加载（共检查 {checked} 张）"
        )
    if not report["has_content"]:
        report["issues"].append(f"页面内容过少（仅 {report['word_count']} 字符）")

    score = 60
    if report["has_title"]:
        score += 5
    if report["has_style"]:
        score += 5
    if report["has_content"]:
        score += 10
    if report["total_images"] > 0:
        broken_ratio = len(report["broken_images"]) / max(checked, 1)
        score += int(20 * (1 - broken_ratio))
    else:
        score += 10
    report["score"] = min(score, 100)
    return report


def analyze_screenshots(files: list[dict]):
    total_images = 0
    meaningful_images = 0
    image_in_subdir = 0
    sizes = []
    image_paths = []

    for f in files:
        if f.get("type") != "blob":
            continue
        path = f["path"]
        name = path.split("/")[-1].lower()
        size = f.get("size", 0)
        if not name.endswith(IMAGE_EXTS):
            continue
        total_images += 1
        image_paths.append(path)
        sizes.append(size)
        if size > 10240:
            meaningful_images += 1
        if any(kw in name for kw in SCREENSHOT_KEYWORDS):
            meaningful_images = max(meaningful_images, total_images)
        path_lower = path.lower()
        if any(
            d in path_lower
            for d in (
                "/img/", "/images/", "/screenshots/", "/screenshot/",
                "/截图/", "/figures/", "/figs/", "/pics/", "/photos/",
            )
        ):
            image_in_subdir += 1

    avg_size = sum(sizes) / len(sizes) if sizes else 0
    return {
        "total": total_images,
        "meaningful": meaningful_images,
        "in_subdir": image_in_subdir,
        "avg_size_kb": round(avg_size / 1024, 1) if avg_size else 0,
        "paths": image_paths[:20],
    }


def analyze_week(
    week_id: str,
    week_info: dict,
    files: list[dict],
    anchor: str | None,
    owner: str,
    repo: str,
    path_commits: list,
    fallback_commits: list,
    fetch_file_content,
    *,
    fetch_readme: bool = True,
):
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
        "improvement_suggestions": [],
        "comments": [],
    }

    if not files:
        result["comments"].append("❌ 未提交作业")
        result["improvement_suggestions"].append(
            f"请在 week 对应目录提交当周作业（参考讲义 {week_id}）。"
        )
        return result

    result["submitted"] = True
    result["comments"].append(f"✅ 已提交（路径: {anchor}）")

    code_count = doc_count = video_count = 0
    readme_blob = find_readme_in_files(files, anchor)
    readme_size = readme_blob.get("size", 0) if readme_blob else 0
    readme_content = ""

    for f in files:
        if f.get("type") != "blob":
            continue
        name = f["path"].split("/")[-1].lower()
        if name.endswith(CODE_EXTS):
            code_count += 1
        elif name.endswith(DOC_EXTS):
            doc_count += 1
        elif name.endswith(VIDEO_EXTS):
            video_count += 1

    img_stats = analyze_screenshots(files)
    content_score = 25
    result["comments"].append("✅ 完成本周作业 (+25 基础分)")

    if readme_blob:
        if readme_size > 3000:
            content_score += 20
            result["comments"].append("📝 README非常详细 (+20)")
        elif readme_size > 1500:
            content_score += 17
            result["comments"].append("📝 README很详细 (+17)")
        elif readme_size > 500:
            content_score += 14
            result["comments"].append("📝 README较详细 (+14)")
        elif readme_size > 100:
            content_score += 10
            result["comments"].append("📝 README较简单 (+10)")
        else:
            content_score += 6
            result["comments"].append("📝 有简短README (+6)")

        readme_content = ""
        if fetch_readme:
            readme_content = fetch_file_content(owner, repo, readme_blob["path"]) or ""
            result["readme_excerpt"] = readme_content[:2500]
        if readme_content:
            depth = 0
            if any(k in readme_content for k in ["问题", "思考", "难点", "错误", "bug", "挑战"]):
                depth += 2
                result["comments"].append("💡 包含问题/思考 (+2)")
            if any(k in readme_content for k in ["总结", "心得", "收获", "反思", "体会"]):
                depth += 2
                result["comments"].append("💡 包含学习总结 (+2)")
            if any(k in readme_content for k in ["步骤", "流程", "## ", "- [x]", "- [ ]"]):
                depth += 2
                result["comments"].append("💡 结构化记录 (+2)")
            if any(k in readme_content for k in ["![", "[图", "图1", "图2", "截图", "图片"]):
                depth += 2
                result["comments"].append("💡 README中引用了图片 (+2)")
            content_score += depth
    else:
        result["comments"].append("⚠️  缺少 README")

    img_score = 0
    total_imgs = img_stats["total"]
    img_count = img_stats["meaningful"]
    if img_count >= 5 or total_imgs >= 8:
        img_score = 18
        result["comments"].append(f"📷 丰富截图（{total_imgs}张, +18）")
    elif img_count >= 3 or total_imgs >= 5:
        img_score = 15
        result["comments"].append(f"📷 较多截图（{total_imgs}张，+15）")
    elif img_count >= 1 or total_imgs >= 2:
        img_score = 12
        result["comments"].append(f"📷 有截图（{total_imgs}张，+12）")
    elif total_imgs >= 1:
        img_score = 8
        result["comments"].append(f"📷 有图片（{total_imgs}张，+8）")
    if img_stats["in_subdir"] > 0:
        img_score = min(img_score + 2, 18)
        result["comments"].append("📁 图片组织规范")
    content_score += img_score

    code_score = 0
    if code_count >= 5:
        code_score = 12
        result["comments"].append(f"💻 完整代码（{code_count}个，+12）")
    elif code_count >= 3:
        code_score = 10
        result["comments"].append(f"💻 多个代码文件（{code_count}个，+10）")
    elif code_count >= 1:
        code_score = 7
        result["comments"].append(f"💻 有代码（{code_count}个，+7）")
    content_score += code_score

    if video_count > 0:
        content_score += 4
        result["comments"].append("🎬 包含视频演示 (+4)")
    if doc_count > 0:
        content_score += 2
        result["comments"].append("📄 包含额外文档 (+2)")

    attitude_score = 10
    result["comments"].append("✅ 完成作业的态度分 (+10)")

    related_commits = path_commits or []
    if not related_commits and fallback_commits:
        related_commits = [
            {"commit": {"author": {"date": c["commit"]["author"]["date"]}}, "sha": c["sha"]}
            for c in fallback_commits[:5]
        ]
    commit_count = len(related_commits)
    if commit_count >= 5:
        attitude_score += 10
        result["comments"].append(f"⭐ 多次提交迭代（{commit_count}次，+10）")
    elif commit_count >= 3:
        attitude_score += 8
        result["comments"].append(f"⭐ 多次提交（{commit_count}次，+8）")
    elif commit_count >= 1:
        attitude_score += 6
        result["comments"].append(f"⭐ 有提交（{commit_count}次，+6）")

    if related_commits:
        try:
            last_date = related_commits[0]["commit"]["author"]["date"]
            last = datetime.fromisoformat(last_date.replace("Z", "+00:00"))
            due = datetime.fromisoformat(week_info["due_date"]).replace(tzinfo=timezone.utc)
            days_diff = (due - last).days
            if days_diff >= 7:
                attitude_score += 10
                result["comments"].append("🎉 提前一周完成 (+10)")
            elif days_diff >= 3:
                attitude_score += 9
                result["comments"].append("🎉 提前完成 (+9)")
            elif days_diff >= 0:
                attitude_score += 8
                result["comments"].append("✅ 按时完成 (+8)")
            elif days_diff >= -7:
                attitude_score += 5
                result["comments"].append(f"⏰ 稍延迟{-days_diff}天 (+5)")
            elif days_diff >= -30:
                attitude_score += 3
                result["comments"].append(f"⏰ 延迟{-days_diff}天 (+3)")
            else:
                attitude_score += 1
        except (KeyError, ValueError, TypeError):
            pass

    result["rule_content_score"] = min(content_score, 70)
    result["rule_attitude_score"] = min(attitude_score, 30)
    result["content_score"] = result["rule_content_score"]
    result["attitude_score"] = result["rule_attitude_score"]
    result["details"] = {
        "readme_size": readme_size,
        "total_images": img_stats["total"],
        "meaningful_images": img_stats["meaningful"],
        "images_in_subdir": img_stats["in_subdir"],
        "image_paths": img_stats.get("paths", []),
        "code_count": code_count,
        "video_count": video_count,
        "doc_count": doc_count,
        "commit_count": commit_count,
        "total_files": sum(1 for f in files if f.get("type") == "blob"),
    }

    suggestions = []
    if not readme_blob:
        suggestions.append("补充 README.md：写清操作步骤、遇到的问题与解决思路。")
    elif readme_size < 500:
        suggestions.append("README 偏短，建议增加截图引用、步骤清单与学习总结。")
    if img_stats["total"] == 0:
        suggestions.append("添加运行截图或效果图，便于展示作业完成情况。")
    elif img_stats["meaningful"] < 2:
        suggestions.append("截图较少，建议多放几张关键步骤或运行结果。")
    if code_count == 0 and week_id not in {"week7"}:
        suggestions.append("本周通常需要代码或配置文件，请检查是否遗漏提交。")
    if video_count == 0 and week_id in {"week10", "week11", "week12"}:
        suggestions.append("建议补充演示视频，展示功能运行过程。")
    if commit_count <= 1:
        suggestions.append("建议分阶段 commit，体现迭代过程。")
    if content_score < 55:
        suggestions.append("内容分偏低：对照当周讲义检查是否遗漏必做项。")
    result["improvement_suggestions"] = suggestions[:6]
    return result

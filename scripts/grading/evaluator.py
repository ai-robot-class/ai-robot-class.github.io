from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import ROOT, WEEKS, ai_scoring_enabled
from .deepseek_scorer import apply_ai_scores, score_student_with_ai
from .github_api import GitHubClient, GitHubRateLimitError, load_students, require_github_token
from .rule_scorer import analyze_week, audit_pages_health, check_pages_alive
from .week13_scorer import analyze_week13
from .week14_scorer import analyze_week14, build_week14_rankings
from .week_utils import group_files_by_week


LENIENT_SUBMISSION_CREDIT = 20
SCORING_SYSTEM = (
    "总分 100 分（内容 70 + 态度 30；规则分 + DeepSeek AI 融合；"
    "宽松评分：已提交周次给予额外完成度分；总分为各周加权得分之和）"
)
MANUAL_SCORE_REVIEWS = {
    "yaokai0928-glitch": {
        "score": 65.0,
        "grade": "B-",
        "reason": "人工复核：能确认参与课堂实验，但主要证据为日期截图和非标准目录，按最低 B- 记录。",
    },
}


def _grade(total_score: float) -> str:
    if total_score >= 95:
        return "A+"
    if total_score >= 88:
        return "A"
    if total_score >= 82:
        return "A-"
    if total_score >= 76:
        return "B+"
    if total_score >= 70:
        return "B"
    if total_score >= 65:
        return "B-"
    if total_score >= 60:
        return "C+"
    if total_score >= 55:
        return "C"
    if total_score >= 50:
        return "C-"
    if total_score >= 35:
        return "D"
    return "F"


def apply_lenient_week_standard(weeks_result: dict, week_info_map: dict) -> None:
    """Make the weekly rubric forgiving before weighted totals are computed."""
    for week_id, wk_result in weeks_result.items():
        if not isinstance(wk_result, dict) or not wk_result.get("submitted"):
            continue
        original_raw = wk_result.get(
            "raw_score",
            wk_result.get("content_score", 0) + wk_result.get("attitude_score", 0),
        )
        adjusted_raw = min(100, original_raw + LENIENT_SUBMISSION_CREDIT)
        delta = adjusted_raw - original_raw
        if delta > 0:
            content_room = max(0, 70 - wk_result.get("content_score", 0))
            content_delta = min(delta, content_room)
            attitude_delta = min(delta - content_delta, max(0, 30 - wk_result.get("attitude_score", 0)))
            wk_result["content_score"] = wk_result.get("content_score", 0) + content_delta
            wk_result["attitude_score"] = wk_result.get("attitude_score", 0) + attitude_delta
            wk_result["lenient_raw_before"] = original_raw
            wk_result["lenient_raw_after"] = adjusted_raw
            wk_result["lenient_scoring"] = (
                f"宽松评分：已提交周次额外完成度分 +{LENIENT_SUBMISSION_CREDIT}。"
            )
        wk_result["raw_score"] = adjusted_raw
        wk_result["final_score"] = round(adjusted_raw * week_info_map[week_id]["weight"] / 100, 2)


def weighted_total_from_weeks(weeks_result: dict, now: datetime) -> tuple[float, float, float]:
    weighted_sum = 0.0
    completed_weight = 0.0
    for week_id, week_info in WEEKS.items():
        wk_result = weeks_result[week_id]
        raw = wk_result.get("raw_score", wk_result.get("content_score", 0) + wk_result.get("attitude_score", 0))
        final = raw * week_info["weight"] / 100
        wk_result["raw_score"] = raw
        wk_result["final_score"] = round(final, 2)
        due = datetime.fromisoformat(week_info["due_date"]).replace(tzinfo=timezone.utc)
        if due <= now or wk_result.get("submitted"):
            weighted_sum += final
            completed_weight += week_info["weight"]
    total_score = weighted_sum / completed_weight * 100 if completed_weight > 0 else 0.0
    return weighted_sum, completed_weight, total_score


def apply_manual_score_review(result: dict) -> None:
    review = MANUAL_SCORE_REVIEWS.get(result.get("github_id"))
    if not review or not result.get("repo_exists"):
        return
    target = float(review["score"])
    current = float(result.get("total_score", 0))
    if current <= 0 or current <= target:
        return

    weeks = result.get("weeks") or {}
    current_sum = sum(
        w.get("final_score", 0)
        for w in weeks.values()
        if isinstance(w, dict) and w.get("submitted")
    )
    if current_sum <= 0:
        return

    factor = target / current_sum
    submitted = [
        (wk, w)
        for wk, w in weeks.items()
        if isinstance(w, dict) and w.get("submitted") and wk in WEEKS
    ]
    running = 0.0
    for index, (week_id, week_data) in enumerate(submitted):
        if index == len(submitted) - 1:
            final = round(target - running, 2)
        else:
            final = round(week_data.get("final_score", 0) * factor, 2)
            running += final
        raw = round(final * 100 / WEEKS[week_id]["weight"])
        week_data["raw_score"] = max(0, min(100, raw))
        week_data["final_score"] = final
        week_data["manual_review"] = review["reason"]

    result["weighted_sum"] = round(sum(w.get("final_score", 0) for _, w in submitted), 1)
    result["base_total_score"] = target
    result["total_score"] = target
    result["grade"] = review["grade"]
    result["manual_review"] = review["reason"]


def evaluate_student(student: dict, gh: GitHubClient, *, use_ai: bool = True) -> dict:
    github_id = student["github_id"]
    repo_url = student["repo_url"]
    repo_name = student["repo_name"]
    print(f"\n📊 评估学生: @{github_id}")

    owner = github_id
    exists, repo_or_error = gh.fetch_repo_info(owner, repo_name)
    if not exists:
        print(f"  ❌ 仓库不可访问: {repo_or_error}")
        return {
            "github_id": github_id,
            "repo_url": repo_url,
            "repo_exists": False,
            "error": str(repo_or_error),
            "weeks": {},
            "total_score": 0,
            "grade": "N/A",
            "evaluation_date": datetime.now().isoformat(),
        }

    repo_info = repo_or_error
    default_branch = repo_info.get("default_branch", "main")
    print(f"  ✅ 仓库: {repo_info.get('name')} (分支: {default_branch})")

    pages_info = gh.fetch_pages_info(owner, repo_name)
    pages_url = pages_info["url"]
    pages_alive, pages_html = check_pages_alive(pages_url)
    pages_audit = None
    if pages_alive:
        pages_audit = audit_pages_health(pages_url, pages_html, owner, repo_name)
        print(f"  🌐 GitHub Pages: {pages_url} ✅ (健康度: {pages_audit['score']}/100)")
    else:
        print("  🌐 GitHub Pages: 未启用或不可访问")

    tree, truncated = gh.fetch_repo_tree(owner, repo_name, default_branch)
    if not tree:
        tree, truncated = gh.fetch_repo_tree(owner, repo_name, "master")
    if truncated:
        print("  ⚠️  仓库较大，文件树已截断")

    commits = gh.fetch_commits(owner, repo_name, per_page=100)
    week_files, week_anchor = group_files_by_week(tree)

    matched_count = sum(1 for files in week_files.values() if files)
    if matched_count == 0 and tree:
        root_files = [f for f in tree if f.get("type") == "blob" and "/" not in f["path"]]
        if root_files:
            print(f"  ⚠️  未识别 week 文件夹，根目录 {len(root_files)} 个文件，按时间分配")
            now = datetime.now(timezone.utc)
            past_weeks = [
                (wk, info)
                for wk, info in WEEKS.items()
                if datetime.fromisoformat(info["due_date"]).replace(tzinfo=timezone.utc) <= now
            ]
            if past_weeks:
                per_week = max(1, len(root_files) // len(past_weeks))
                for i, (wk, _info) in enumerate(past_weeks):
                    start = i * per_week
                    end = (i + 1) * per_week if i < len(past_weeks) - 1 else len(root_files)
                    chunk = root_files[start:end]
                    if chunk:
                        week_files[wk] = chunk
                        week_anchor[wk] = "."

    weeks_result = {}
    weighted_sum = 0.0
    completed_weight = 0.0
    ai_comment = None
    now = datetime.now(timezone.utc)

    for week_id, week_info in WEEKS.items():
        anchor = week_anchor.get(week_id)
        files = week_files.get(week_id, [])
        path_commits = gh.fetch_commits_for_path(owner, repo_name, anchor) if anchor and files else []

        wk_result = (
            analyze_week14(
                week_info,
                files,
                anchor,
                owner,
                repo_name,
                path_commits,
                commits,
                gh.fetch_file_content,
            )
            if week_id == "week14"
            else analyze_week13(
                week_info,
                files,
                anchor,
                owner,
                repo_name,
                path_commits,
                commits,
                gh.fetch_file_content,
            )
            if week_id == "week13"
            else analyze_week(
                week_id,
                week_info,
                files,
                anchor,
                owner,
                repo_name,
                path_commits,
                commits,
                gh.fetch_file_content,
                fetch_readme=use_ai,
            )
        )
        raw = wk_result["content_score"] + wk_result["attitude_score"]
        final = raw * week_info["weight"] / 100
        wk_result["raw_score"] = raw
        wk_result["final_score"] = round(final, 2)
        weeks_result[week_id] = wk_result

        due = datetime.fromisoformat(week_info["due_date"]).replace(tzinfo=timezone.utc)
        is_past = due <= now
        wk_result["is_past"] = is_past
        if is_past or wk_result["submitted"]:
            weighted_sum += final
            completed_weight += week_info["weight"]
            mark = ""
        else:
            mark = " (未到截止日期，不计入总分)"
        print(
            f"  📝 {week_id} ({week_info['title']}): {raw}/100 → "
            f"{final:.1f}/{week_info['weight']}{mark}"
        )

    if use_ai and ai_scoring_enabled():
        print("  🤖 DeepSeek AI 评分中...")
        ai_result = score_student_with_ai(github_id, weeks_result)
        if ai_result:
            ai_comment = apply_ai_scores(weeks_result, ai_result)
            weighted_sum = 0.0
            completed_weight = 0.0
            for week_id, week_info in WEEKS.items():
                wk_result = weeks_result[week_id]
                raw = wk_result["content_score"] + wk_result["attitude_score"]
                final = raw * week_info["weight"] / 100
                wk_result["raw_score"] = raw
                wk_result["final_score"] = round(final, 2)
                due = datetime.fromisoformat(week_info["due_date"]).replace(tzinfo=timezone.utc)
                if due <= now or wk_result["submitted"]:
                    weighted_sum += final
                    completed_weight += week_info["weight"]
            print("  ✅ AI 评分已融合")

    if completed_weight > 0:
        total_score = weighted_sum / completed_weight * 100
    else:
        total_score = 0.0

    apply_lenient_week_standard(weeks_result, WEEKS)
    weighted_sum, completed_weight, total_score = weighted_total_from_weeks(weeks_result, now)

    grade = _grade(total_score)
    print(f"  🎯 基础总分: {total_score:.1f}/100  等级: {grade}")

    result = {
        "github_id": github_id,
        "repo_url": repo_url,
        "repo_exists": True,
        "repo_name": repo_info.get("name"),
        "repo_description": repo_info.get("description") or "",
        "stars": repo_info.get("stargazers_count", 0),
        "forks": repo_info.get("forks_count", 0),
        "default_branch": default_branch,
        "pages_url": pages_url if pages_alive else None,
        "pages_enabled": pages_alive,
        "pages_audit": pages_audit,
        "total_files": sum(1 for f in tree if f.get("type") == "blob"),
        "total_commits": len(commits),
        "weeks": weeks_result,
        "base_total_score": round(total_score, 1),
        "total_score": round(total_score, 1),
        "weighted_sum": round(weighted_sum, 1),
        "completed_weight": completed_weight,
        "grade": grade,
        "evaluation_date": datetime.now().isoformat(),
        "scoring_mode": "rule+deepseek" if use_ai and ai_scoring_enabled() else "rule",
    }
    if ai_comment:
        result["ai_overall_comment"] = ai_comment
    apply_manual_score_review(result)
    return result


def run_evaluation(*, use_ai: bool = True, limit: int | None = None) -> dict:
    token = require_github_token()
    gh = GitHubClient(token=token)
    print("🚀 开始自动评价学生作业 (v3 DeepSeek)...")
    print("📊 评分: 总分 100 分（内容 70% + 态度 30%）")
    print("🔑 GitHub Token: 已配置✅")
    print(f"🤖 DeepSeek: {'已配置✅' if ai_scoring_enabled() and use_ai else '未启用（仅规则评分）'}\n")

    students = load_students()
    if not students:
        print("❌ 未找到学生")
        return {}

    if limit:
        students = students[:limit]
    print(f"📋 共 {len(students)} 名学生\n")

    results = []
    for student in students:
        try:
            results.append(evaluate_student(student, gh, use_ai=use_ai))
        except Exception as exc:
            print(f"  ⚠️  评估异常: {exc}")
            if isinstance(exc, GitHubRateLimitError):
                raise
            results.append(
                {
                    "github_id": student["github_id"],
                    "repo_url": student["repo_url"],
                    "repo_exists": False,
                    "error": f"评估异常: {exc}",
                    "weeks": {},
                    "total_score": 0,
                    "grade": "N/A",
                    "evaluation_date": datetime.now().isoformat(),
                }
            )

    output_dir = ROOT / "students" / "evaluations"
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "evaluation_date": datetime.now().isoformat(),
        "scoring_system": SCORING_SYSTEM,
        "scoring_mode": "rule+deepseek" if use_ai and ai_scoring_enabled() else "rule",
        "weeks": {
            wk: {"title": info["title"], "weight": info["weight"], "due_date": info["due_date"]}
            for wk, info in WEEKS.items()
        },
        "students": results,
    }
    payload["week14_rankings"] = build_week14_rankings(results)

    latest = output_dir / "latest.json"
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 评价完成: {latest}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history = output_dir / f"evaluation_{timestamp}.json"
    with open(history, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"📚 历史: {history}")

    active = [r for r in results if r.get("repo_exists")]
    submitted = [r for r in active if r.get("total_score", 0) > 0]
    print("\n" + "=" * 60)
    print("📊 评价统计")
    print("=" * 60)
    if active:
        avg = sum(r["total_score"] for r in active) / len(active)
        avg_sub = sum(r["total_score"] for r in submitted) / max(len(submitted), 1)
        print(f"总学生: {len(results)}  可访问: {len(active)}  有作业: {len(submitted)}")
        print(f"平均分(全部): {avg:.1f}  平均分(有作业): {avg_sub:.1f}")
    else:
        print("无可访问仓库")
    print("\n✨ 评价结束\n")
    return payload

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


def _has_submission(result: dict) -> bool:
    weeks = result.get("weeks", {})
    return any(isinstance(w, dict) and w.get("submitted") for w in weeks.values())


def apply_score_curve(results: list[dict], *, bonus: float = 3.0, max_a_plus: int = 5) -> None:
    """Apply the course display curve after individual scoring."""
    eligible = [
        r for r in results
        if r.get("repo_exists") and _has_submission(r) and r.get("total_score", 0) > 0
    ]
    for result in eligible:
        before = float(result.get("total_score", 0))
        curved = min(before + bonus, 100.0)
        result["total_score"] = round(curved, 1)
        result["grade"] = _grade(curved)
        result["score_curve_adjustment"] = f"课程曲线加分 +{bonus:g}。"

    ranked = sorted(eligible, key=lambda x: x.get("total_score", 0), reverse=True)
    for rank, result in enumerate(ranked, start=1):
        if rank <= max_a_plus:
            if result.get("total_score", 0) < 95:
                result["total_score"] = 95.0
            result["grade"] = "A+"
            result["score_curve_adjustment"] = (
                f"课程曲线加分 +{bonus:g}；总分前 {max_a_plus} 名保底 A+。"
            )
        elif result.get("grade") == "A+":
            result["total_score"] = min(result.get("total_score", 0), 94.9)
            result["grade"] = "A"
            result["score_curve_adjustment"] = (
                f"课程曲线加分 +{bonus:g}；A+ 名额上限为 {max_a_plus} 名。"
            )


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

    submitted_weeks = [
        w for w in weeks_result.values()
        if isinstance(w, dict) and w.get("submitted")
    ]
    if submitted_weeks:
        submitted_avg = sum(w["raw_score"] for w in submitted_weeks) / len(submitted_weeks)
        alt_score = submitted_avg * 0.8
        if alt_score > total_score:
            total_score = alt_score
            print(f"  📐 使用'已提交周次平均'打分: {submitted_avg:.0f}×0.8 = {alt_score:.1f}")
        if total_score < 65:
            total_score = 65.0
            print("  🛟 保底 65 分（有提交内容，最低 B-）")

    grade = _grade(total_score)
    print(f"  🎯 总分: {total_score:.1f}/100  等级: {grade}")

    if pages_alive:
        bonus = 3
        if pages_audit and pages_audit["score"] >= 85:
            bonus = 5
        elif pages_audit and pages_audit["score"] >= 70:
            bonus = 4
        total_score = min(total_score + bonus, 100)
        grade = _grade(total_score)

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
        "total_score": round(total_score, 1),
        "weighted_sum": round(weighted_sum, 1),
        "completed_weight": completed_weight,
        "grade": grade,
        "evaluation_date": datetime.now().isoformat(),
        "scoring_mode": "rule+deepseek" if use_ai and ai_scoring_enabled() else "rule",
    }
    if ai_comment:
        result["ai_overall_comment"] = ai_comment
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
        "scoring_system": "总分 100 分（内容 70 + 态度 30；规则分 + DeepSeek AI 融合；最低 B-，课程曲线 +3，A+ 最多 5 名）",
        "scoring_mode": "rule+deepseek" if use_ai and ai_scoring_enabled() else "rule",
        "weeks": {
            wk: {"title": info["title"], "weight": info["weight"], "due_date": info["due_date"]}
            for wk, info in WEEKS.items()
        },
        "students": results,
    }
    apply_score_curve(results)
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

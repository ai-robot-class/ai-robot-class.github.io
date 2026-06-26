from __future__ import annotations

import json
import re
import time

import requests

from .config import DEEPSEEK_API_URL, DEEPSEEK_MODEL, WEEKS, get_deepseek_api_key


RUBRIC = """
你是 AI 机器人课程助教。请根据仓库客观证据评分，不要臆造未出现的内容。
评分标准（每周 raw 分 0-100 = 内容分 0-70 + 态度分 0-30）：
- 内容 70：README 质量、截图/代码/视频/文档是否齐全、是否体现理解与思考
- 态度 30：是否提交、commit 次数、是否接近截止日期完成
宽松原则：只要提交了实质内容，内容分通常 >= 45；README+截图+代码齐全通常 >= 75。
若目录没有按 weekX 命名，但文件夹名、图片路径、README 摘要能对应课程实验主题，应视为有效课程参与证据。
注意：你只能根据提供的文件名、图片路径、README 摘要和统计信息判断；不要声称已经看到了图片像素内容。
未提交的作业 content_score=0, attitude_score=0。
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def build_student_prompt(github_id: str, weeks_payload: list[dict]) -> str:
    lines = [
        RUBRIC,
        f"学生 GitHub ID: {github_id}",
        "请仅对已提交周次给出 AI 评分，输出 JSON：",
        "{",
        '  "weeks": {',
        '    "week2": {"content_score": 0-70, "attitude_score": 0-30, "comment": "一句中文评语"},',
        "    ...",
        "  },",
        '  "overall_comment": "总体一句中文评价"',
        "}",
        "",
        "各周证据如下：",
    ]
    for item in weeks_payload:
        lines.append(
            f"- {item['week_id']} {item['title']} (权重{item['weight']}, 截止{item['due_date']})"
        )
        if not item["submitted"]:
            lines.append("  状态: 未提交")
            continue
        lines.append(f"  路径: {item.get('actual_path')}")
        lines.append(
            "  规则分: 内容 {rule_content}/70, 态度 {rule_attitude}/30".format(**item)
        )
        details = item.get("details") or {}
        lines.append(
            "  文件统计: README {readme_size}B, 图片 {total_images}, 代码 {code_count}, "
            "视频 {video_count}, commit {commit_count}".format(
                readme_size=details.get("readme_size", 0),
                total_images=details.get("total_images", 0),
                code_count=details.get("code_count", 0),
                video_count=details.get("video_count", 0),
                commit_count=details.get("commit_count", 0),
            )
        )
        image_paths = details.get("image_paths") or []
        if image_paths:
            lines.append("  图片/截图路径样本（用于判断非标准目录下的课程参与证据）:")
            for path in image_paths[:12]:
                lines.append(f"    - {path}")
        excerpt = (item.get("readme_excerpt") or "").strip()
        if excerpt:
            lines.append("  README 摘要:")
            lines.append(excerpt[:1800])
        if item.get("week_id") == "week14":
            proj = item.get("week14_project") or {}
            rubric = proj.get("rubric") or {}
            if rubric:
                lines.append(
                    "  第14周项目rubric: 链路 {link}/30, 迷宫 {maze}/25, 进阶 {adv}/25, "
                    "规范 {eng}/10, 报告 {rep}/10".format(
                        link=rubric.get("link_chain", 0),
                        maze=rubric.get("maze_explore", 0),
                        adv=rubric.get("advanced", 0),
                        eng=rubric.get("engineering", 0),
                        rep=rubric.get("report_demo", 0),
                    )
                )
        lines.append("")
    return "\n".join(lines)


def score_student_with_ai(github_id: str, weeks_result: dict) -> dict | None:
    api_key = get_deepseek_api_key()
    if not api_key:
        return None

    submitted = [wk for wk, data in weeks_result.items() if isinstance(data, dict) and data.get("submitted")]
    if not submitted:
        return None

    weeks_payload = []
    for week_id in submitted:
        data = weeks_result[week_id]
        info = WEEKS[week_id]
        weeks_payload.append(
            {
                "week_id": week_id,
                "title": info["title"],
                "weight": info["weight"],
                "due_date": info["due_date"],
                "submitted": True,
                "actual_path": data.get("actual_path"),
                "rule_content": data.get("rule_content_score", data.get("content_score", 0)),
                "rule_attitude": data.get("rule_attitude_score", data.get("attitude_score", 0)),
                "details": data.get("details", {}),
                "readme_excerpt": data.get("readme_excerpt", ""),
                "week14_project": data.get("week14_project"),
            }
        )

    prompt = build_student_prompt(github_id, weeks_payload)
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "你是严格、公正的课程作业评分助手，只返回 JSON。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    last_error = None
    for attempt in range(3):
        try:
            resp = requests.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120,
            )
            if resp.status_code in {429, 500, 502, 503} and attempt < 2:
                time.sleep(2 ** attempt * 3)
                continue
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return _extract_json(content)
        except (requests.RequestException, KeyError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** attempt * 2)
    print(f"  ⚠️  DeepSeek 评分失败 @{github_id}: {last_error}")
    return None


def _iter_week_data(weeks_result: dict):
    """只遍历各周评分 dict，跳过 AI 附加字段等非 dict 项。"""
    for week_id, data in weeks_result.items():
        if isinstance(data, dict):
            yield week_id, data


def apply_ai_scores(weeks_result: dict, ai_result: dict | None) -> str | None:
    if not ai_result:
        return None

    ai_weeks = ai_result.get("weeks") or {}
    if not isinstance(ai_weeks, dict):
        ai_weeks = {}

    for week_id, wk_data in _iter_week_data(weeks_result):
        if not wk_data.get("submitted"):
            continue
        ai_wk = ai_weeks.get(week_id)
        if not isinstance(ai_wk, dict):
            continue

        try:
            ai_content = max(0, min(70, int(ai_wk.get("content_score", 0))))
            ai_attitude = max(0, min(30, int(ai_wk.get("attitude_score", 0))))
        except (TypeError, ValueError):
            continue

        rule_content = wk_data.get("rule_content_score", wk_data.get("content_score", 0))
        rule_attitude = wk_data.get("rule_attitude_score", wk_data.get("attitude_score", 0))

        wk_data["ai_content_score"] = ai_content
        wk_data["ai_attitude_score"] = ai_attitude
        wk_data["content_score"] = round(rule_content * 0.35 + ai_content * 0.65)
        wk_data["attitude_score"] = round(rule_attitude * 0.35 + ai_attitude * 0.65)

        comment = str(ai_wk.get("comment", "")).strip()
        if comment:
            wk_data["comments"].append(f"🤖 AI: {comment}")

    overall = str(ai_result.get("overall_comment", "")).strip()
    return overall or None

#!/usr/bin/env python3
"""
生成学生作业展示页面（适配新评价数据格式）
"""

import json
from pathlib import Path
from datetime import datetime


def load_evaluation_results():
    results_file = Path('students/evaluations/latest.json')
    if not results_file.exists():
        return None
    with open(results_file, 'r', encoding='utf-8') as f:
        return json.load(f)


GRADE_COLORS = {
    'A+': '#10b981', 'A': '#10b981', 'A-': '#22c55e',
    'B+': '#3b82f6', 'B': '#3b82f6', 'B-': '#60a5fa',
    'C+': '#f59e0b', 'C': '#f59e0b', 'C-': '#fbbf24',
    'D': '#f97316', 'F': '#ef4444', 'N/A': '#9ca3af',
}


def grade_color(grade):
    return GRADE_COLORS.get(grade, '#9ca3af')


def generate_student_card(student, week_keys):
    github_id = student['github_id']
    repo_url = student['repo_url']
    repo_exists = student.get('repo_exists', False)

    if not repo_exists:
        return f"""
        <div class="student-card">
            <div class="card-header" style="background: linear-gradient(135deg, #9ca3af, #6b7280);">
                <img src="https://github.com/{github_id}.png" alt="@{github_id}" class="avatar" onerror="this.src='https://github.com/identicons/{github_id}.png'">
                <div class="header-info">
                    <h3>@{github_id}</h3>
                    <span class="status-badge">⚠️ 仓库不可访问</span>
                </div>
            </div>
            <div class="card-body">
                <p style="text-align:center; color:#999; padding:20px 0;">{student.get('error', '仓库未创建或为私有')}</p>
                <a href="{repo_url}" target="_blank" class="repo-link">📂 查看仓库</a>
            </div>
        </div>
        """

    total_score = student['total_score']
    grade = student.get('grade', 'N/A')
    color = grade_color(grade)
    weeks = student['weeks']
    submitted_count = sum(1 for w in weeks.values() if w.get('submitted'))
    total_weeks = len(weeks)
    repo_name = student.get('repo_name', '')
    repo_desc = student.get('repo_description', '')

    week_cells = []
    for wk in week_keys:
        wkd = weeks.get(wk, {})
        if wkd.get('submitted'):
            raw = wkd.get('raw_score', 0)
            if raw >= 75:
                cls = 'excellent'
            elif raw >= 55:
                cls = 'good'
            elif raw >= 30:
                cls = 'pass'
            else:
                cls = 'weak'
            final = wkd.get("final_score", 0)
            week_cells.append(
                f'<span class="week-pill {cls}" title="{wk}: 原始分{raw}/100, 加权{final:.1f}">'
                f'<span class="pill-w">W{wk[4:]}</span><span class="pill-s">{final:.1f}</span></span>')
        else:
            week_cells.append(
                f'<span class="week-pill empty" title="{wk}: 未提交">'
                f'<span class="pill-w">W{wk[4:]}</span><span class="pill-s">—</span></span>')

    return f"""
    <div class="student-card">
        <div class="card-header" style="background: linear-gradient(135deg, {color}, {color}cc);">
            <img src="https://github.com/{github_id}.png" alt="@{github_id}" class="avatar" onerror="this.src='https://github.com/identicons/{github_id}.png'">
            <div class="header-info">
                <h3>@{github_id}</h3>
                <span class="status-badge">📦 {repo_name}</span>
            </div>
            <div class="grade-badge" style="background:{color}">{grade}</div>
        </div>
        <div class="card-body">
            <div class="score-row">
                <div class="score-main">
                    <div class="score-value">{total_score}</div>
                    <div class="score-label">总分 / 100</div>
                </div>
                <div class="score-detail">
                    <div>已提交 <strong>{submitted_count}/{total_weeks}</strong> 周</div>
                    <div>提交数: <strong>{student.get('total_commits', 0)}</strong></div>
                    <div>文件数: <strong>{student.get('total_files', 0)}</strong></div>
                </div>
            </div>
            <div class="week-pills">{''.join(week_cells)}</div>
            <a href="{repo_url}" target="_blank" class="repo-link">📂 查看仓库 →</a>
        </div>
    </div>
    """


def _escape_html(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate_week_improvements(students, week_keys, week_info):
    """各周作业详情：按学生展开评语与改进建议。"""
    blocks = []
    active = [s for s in students if s.get("repo_exists")]
    for s in active:
        github_id = s["github_id"]
        weeks = s.get("weeks") or {}
        week_sections = []

        for wk in week_keys:
            wkd = weeks.get(wk, {})
            info = week_info.get(wk, {})
            title = info.get("title", wk)
            weight = info.get("weight", 0)

            if not wkd.get("submitted"):
                week_sections.append(
                    f'<div class="improve-week improve-missing">'
                    f'<div class="improve-week-head"><strong>W{wk[4:]}</strong> {title} '
                    f'<span class="improve-tag tag-missing">未提交</span></div>'
                    f'<p class="improve-empty">暂无提交内容。权重 {weight} 分。</p>'
                    f"</div>"
                )
                continue

            raw = wkd.get("raw_score", 0)
            final = wkd.get("final_score", 0)
            comments = wkd.get("comments") or []
            suggestions = wkd.get("improvement_suggestions") or []

            if raw >= 75:
                tag_cls, tag = "tag-excellent", "优秀"
            elif raw >= 55:
                tag_cls, tag = "tag-good", "良好"
            elif raw >= 30:
                tag_cls, tag = "tag-pass", "及格"
            else:
                tag_cls, tag = "tag-weak", "待加强"

            comment_items = "".join(f"<li>{_escape_html(c)}</li>" for c in comments[:12])
            suggest_items = "".join(
                f"<li class='suggest-li'>{_escape_html(t)}</li>" for t in suggestions[:8]
            )

            extra = ""
            if wk == "week14":
                proj = wkd.get("week14_project") or {}
                rubric = proj.get("rubric") or {}
                if rubric:
                    extra = (
                        '<div class="week14-rubric-mini">'
                        f'项目分 {proj.get("project_score", raw)}/100 · '
                        f'链路 {rubric.get("link_chain", 0)}/30 · '
                        f'迷宫 {rubric.get("maze_explore", 0)}/25 · '
                        f'进阶 {rubric.get("advanced", 0)}/25 · '
                        f'规范 {rubric.get("engineering", 0)}/10 · '
                        f'报告 {rubric.get("report_demo", 0)}/10'
                        "</div>"
                    )
                if not suggestions:
                    suggest_items = (
                        "<li class='suggest-li'>请对照讲义 14.10 节检查："
                        "week14/ 目录、week14_XXXX.pdf、演示视频、自动探索（如适用）。</li>"
                    )

            week_sections.append(
                f'<details class="improve-week">'
                f'<summary class="improve-week-head">'
                f'<strong>W{wk[4:]}</strong> {title} '
                f'<span class="improve-score">{final:.1f}/{weight}</span> '
                f'<span class="improve-tag {tag_cls}">{tag} {raw:.0f}</span>'
                f"</summary>"
                f"{extra}"
                f'<div class="improve-grid">'
                f'<div><h4>📋 评分说明</h4><ul class="improve-list">{comment_items or "<li>暂无</li>"}</ul></div>'
                f'<div><h4>💡 改进建议</h4><ul class="improve-list">{suggest_items or "<li>继续保持，可打磨进阶功能与报告质量。</li>"}</ul></div>'
                f"</div></details>"
            )

        ai_overall = s.get("ai_overall_comment")
        ai_block = ""
        if ai_overall:
            ai_block = f'<div class="ai-overall-comment">🤖 总评：{_escape_html(ai_overall)}</div>'

        blocks.append(
            f'<div class="improve-student-card" id="student-{github_id}">'
            f'<div class="improve-student-head">'
            f'<img src="https://github.com/{github_id}.png" alt="@{github_id}" class="improve-avatar" '
            f'onerror="this.src=\'https://github.com/identicons/{github_id}.png\'">'
            f'<div><h3><a href="{s["repo_url"]}" target="_blank">@{github_id}</a></h3>'
            f'<span class="improve-meta">总分 {s.get("total_score", 0)} · {s.get("grade", "N/A")}</span></div>'
            f"</div>{ai_block}{''.join(week_sections)}</div>"
        )

    if not blocks:
        return ""

    return f"""
    <div class="week-improvements-section" id="week-improvements">
        <h2>📝 各周作业详情（按学生 · 改进提示）</h2>
        <p style="text-align:center; color:#666; margin-bottom: 20px;">
            展开每位学生的各周卡片，查看评分说明与<strong>具体改进建议</strong>。第 14 周为小组项目专项评分。
        </p>
        <div class="improve-students-list">
            {''.join(blocks)}
        </div>
    </div>
    """


def generate_week14_ranking(data):
    """第 14 周小组项目排名表。"""
    rankings = data.get("week14_rankings") or []
    if not rankings:
        return """
        <div class="week14-ranking-section" id="week14-ranking">
            <h2>🏁 第 14 周小组项目排名</h2>
            <p style="text-align:center; color:#666;">暂无 week14/ 目录提交记录。请按规范提交至 <code>week14/</code>，报告命名为 <code>week14_XXXX.pdf</code>。</p>
        </div>
        """

    rows = []
    for item in rankings:
        rubric = item.get("rubric") or {}
        direction = item.get("direction") or "?"
        dir_label = "机器狗 A" if direction == "pybullet" else "小乌龟 B" if direction == "turtlesim" else direction
        pdf_ok = "✅" if item.get("pdf_valid") else "❌"
        top_suggest = (item.get("improvement_suggestions") or ["—"])[0]
        short = top_suggest[:48] + ("…" if len(top_suggest) > 48 else "")
        rows.append(
            f"<tr>"
            f'<td class="rank-col"><strong>#{item.get("rank", "—")}</strong></td>'
            f'<td class="name-col"><a href="{item.get("repo_url", "#")}" target="_blank">@{item["github_id"]}</a></td>'
            f'<td><strong>{item.get("project_score", 0)}</strong></td>'
            f'<td>{item.get("raw_score", 0)}</td>'
            f'<td>{dir_label}</td>'
            f'<td>{rubric.get("link_chain", 0)}/30</td>'
            f'<td>{rubric.get("maze_explore", 0)}/25</td>'
            f'<td>{rubric.get("advanced", 0)}/25</td>'
            f'<td>{rubric.get("engineering", 0)}/10</td>'
            f'<td>{rubric.get("report_demo", 0)}/10</td>'
            f'<td>{pdf_ok}</td>'
            f'<td class="suggest-col" title="{_escape_html(top_suggest)}">{_escape_html(short)}</td>'
            f"</tr>"
        )

    return f"""
    <div class="week14-ranking-section" id="week14-ranking">
        <h2>🏁 第 14 周小组项目排名</h2>
        <p style="text-align:center; color:#666; margin-bottom: 16px;">
            按项目 rubric 总分排序（链路30 + 迷宫25 + 进阶25 + 规范10 + 报告10）。
            交付规范：<code>week14/</code> 目录 + <code>week14_XXXX.pdf</code> 报告 + 演示视频。
        </p>
        <div class="table-scroll">
            <table class="week-table week14-table">
                <thead><tr>
                    <th>排名</th><th>学生</th><th>项目分</th><th>Raw</th><th>方向</th>
                    <th>链路</th><th>迷宫</th><th>进阶</th><th>规范</th><th>报告</th><th>PDF</th><th>首要改进</th>
                </tr></thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
        </div>
    </div>
    """


def generate_week_table(students, week_keys, week_info):
    rows = []
    for s in students:
        if not s.get('repo_exists'):
            continue
        github_id = s['github_id']
        cells = [f'<td class="name-col"><a href="{s["repo_url"]}" target="_blank">@{github_id}</a></td>']
        for wk in week_keys:
            wkd = s['weeks'].get(wk, {})
            if wkd.get('submitted'):
                raw = wkd.get('raw_score', 0)
                final = wkd.get('final_score', 0)
                if raw >= 75:
                    cls = 'cell-excellent'
                elif raw >= 55:
                    cls = 'cell-good'
                elif raw >= 30:
                    cls = 'cell-pass'
                else:
                    cls = 'cell-weak'
                cells.append(f'<td class="{cls}" title="原始{raw}/100">{final:.1f}</td>')
            else:
                cells.append('<td class="cell-empty">—</td>')
        cells.append(f'<td class="total-col"><strong>{s["total_score"]}</strong></td>')
        cells.append(f'<td class="grade-col" style="color:{grade_color(s["grade"])}"><strong>{s["grade"]}</strong></td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')

    headers = ['<th>学生</th>']
    for wk in week_keys:
        info = week_info.get(wk, {})
        title = info.get('title', wk)
        weight = info.get('weight', 0)
        headers.append(f'<th title="{title}（{weight}分）">W{wk[4:]}<br><small>{weight}</small></th>')
    headers.append('<th>总分</th>')
    headers.append('<th>等级</th>')

    return f"""
    <div class="week-table-wrapper" id="week-scores">
        <h2>📊 各周作业详情（按学生）</h2>
        <p style="text-align:center; color:#666; margin-bottom: 20px;">表格中显示加权得分（已乘以权重）。原始分见单元格 tooltip。</p>
        <div class="table-scroll">
            <table class="week-table">
                <thead><tr>{''.join(headers)}</tr></thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
        </div>
        <div class="legend">
            <span class="legend-item legend-excellent">■ 优秀 (≥75)</span>
            <span class="legend-item legend-good">■ 良好 (55-74)</span>
            <span class="legend-item legend-pass">■ 及格 (30-54)</span>
            <span class="legend-item legend-weak">■ 较弱 (1-29)</span>
            <span class="legend-item legend-empty">■ 未提交</span>
        </div>
    </div>
    """


def generate_pages_carousel(students):
    """生成学生 GitHub Pages 的滑窗预览，包含健康度反馈"""
    pages_students = [s for s in students if s.get('pages_enabled') and s.get('pages_url')]
    if not pages_students:
        return ""

    slides = []
    for s in pages_students:
        github_id = s['github_id']
        pages_url = s['pages_url']
        score = s.get('total_score', 0)
        grade = s.get('grade', 'N/A')
        repo_url = s['repo_url']
        repo_name = s.get('repo_name', '')
        color = grade_color(grade)

        # 健康度反馈
        audit = s.get('pages_audit') or {}
        health = audit.get('score', 0)
        broken_imgs = audit.get('broken_images', [])
        issues = audit.get('issues', [])
        suggestions = audit.get('suggestions', [])

        if health >= 85:
            health_label = "✨ 优秀"
            health_color = "#10b981"
        elif health >= 70:
            health_label = "👍 良好"
            health_color = "#3b82f6"
        elif health >= 50:
            health_label = "⚠️  有问题"
            health_color = "#f59e0b"
        else:
            health_label = "❌ 待修复"
            health_color = "#ef4444"

        # 反馈面板
        feedback_html = ""
        if issues or suggestions or broken_imgs:
            issue_items = ""
            for issue in issues:
                issue_items += f'<li class="issue-item">⚠️ {issue}</li>'
            for sug in suggestions:
                issue_items += f'<li class="suggestion-item">💡 {sug}</li>'

            # 显示前 3 张失败的图片
            broken_html = ""
            if broken_imgs:
                items = []
                for b in broken_imgs[:3]:
                    src = b.get('src', '')
                    status = b.get('status', '')
                    err = b.get('error', '')
                    if status:
                        items.append(f'<li><code>{src[:60]}</code> → HTTP {status}</li>')
                    else:
                        items.append(f'<li><code>{src[:60]}</code> → {err[:40]}</li>')
                more = f'<li>... 还有 {len(broken_imgs) - 3} 张</li>' if len(broken_imgs) > 3 else ''
                broken_html = f'<div class="broken-images-list"><strong>无法加载的图片：</strong><ul>{"".join(items)}{more}</ul></div>'

            feedback_html = f"""
            <div class="pages-feedback">
                <details>
                    <summary>📋 页面健康度反馈（{health}/100，{len(issues)} 个问题 / {len(suggestions)} 条建议）</summary>
                    <ul class="feedback-list">{issue_items}</ul>
                    {broken_html}
                </details>
            </div>
            """
        else:
            feedback_html = f"""
            <div class="pages-feedback">
                <div class="feedback-perfect">✨ 页面无明显问题（{health}/100）</div>
            </div>
            """

        slides.append(f"""
        <div class="pages-slide">
            <div class="pages-slide-header" style="background: linear-gradient(135deg, {color}, {color}dd);">
                <img src="https://github.com/{github_id}.png" alt="@{github_id}" class="pages-avatar" onerror="this.src='https://github.com/identicons/{github_id}.png'">
                <div class="pages-slide-info">
                    <h3>@{github_id}</h3>
                    <div class="pages-meta">
                        <span class="pages-score" style="color:{color};">{score} 分 / {grade}</span>
                        <span class="health-pill" style="background:{health_color};">{health_label} {health}</span>
                    </div>
                </div>
                <div class="pages-actions">
                    <a href="{pages_url}" target="_blank" class="pages-action-btn" title="新窗口打开">🔗</a>
                    <a href="{repo_url}" target="_blank" class="pages-action-btn" title="查看仓库">📂</a>
                </div>
            </div>
            <div class="pages-iframe-wrap">
                <iframe src="{pages_url}" loading="lazy" sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
                        referrerpolicy="no-referrer" title="@{github_id} 的作业页面"></iframe>
                <div class="pages-iframe-overlay">
                    <a href="{pages_url}" target="_blank" class="pages-open-btn">🚀 在新窗口打开</a>
                </div>
            </div>
            {feedback_html}
        </div>
        """)

    return f"""
    <div class="pages-carousel-section">
        <h2>🌐 学生 GitHub Pages 作品展（{len(pages_students)} 个已部署）</h2>
        <p style="text-align:center; color:#666; margin-bottom: 16px;">
            横向滚动浏览同学们的作业页面 · 系统自动检测图片加载与页面健康度 · 点击 🔗 在新窗口打开完整版
        </p>
        <div class="pages-carousel-wrap">
            <button class="carousel-nav prev" onclick="scrollCarousel(-1)" aria-label="上一个">‹</button>
            <div class="pages-carousel" id="pagesCarousel">
                {''.join(slides)}
            </div>
            <button class="carousel-nav next" onclick="scrollCarousel(1)" aria-label="下一个">›</button>
        </div>
    </div>
    """


def generate_stats(students):
    total = len(students)
    active = [s for s in students if s.get('repo_exists')]
    submitted = [s for s in active if s['total_score'] > 0]

    if not active:
        return "<div class='stats-grid'><p>暂无可访问的学生仓库</p></div>"

    avg_all = sum(s['total_score'] for s in active) / len(active)
    avg_sub = sum(s['total_score'] for s in submitted) / max(len(submitted), 1)
    top = max(active, key=lambda x: x['total_score'])
    max_score = top['total_score']

    return f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-value">{total}</div>
            <div class="stat-label">总学生数</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-value">{len(active)}</div>
            <div class="stat-label">仓库可访问</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-value">{len(submitted)}</div>
            <div class="stat-label">已开始作业</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-value">{avg_sub:.1f}</div>
            <div class="stat-label">平均分（已提交）</div>
        </div>
        <div class="stat-card highlight">
            <div class="stat-icon">🏆</div>
            <div class="stat-value">{max_score:.1f}</div>
            <div class="stat-label">最高分 @{top['github_id']}</div>
        </div>
    </div>
    """


def generate_html(data):
    students = data['students']
    eval_date = data['evaluation_date']
    eval_time = datetime.fromisoformat(eval_date).strftime('%Y-%m-%d %H:%M')
    week_info = data.get('weeks', {})
    week_keys = list(week_info.keys()) or [f'week{i}' for i in range(2, 14)]

    students_sorted = sorted(students,
                             key=lambda x: x['total_score'] if x.get('repo_exists') else -1,
                             reverse=True)

    stats_html = generate_stats(students_sorted)
    carousel_html = generate_pages_carousel(students_sorted)
    cards_html = "\n".join(generate_student_card(s, week_keys) for s in students_sorted)
    table_html = generate_week_table(students_sorted, week_keys, week_info)
    improvements_html = generate_week_improvements(students_sorted, week_keys, week_info)
    week14_ranking_html = generate_week14_ranking(data)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学生作业展示 - AI机器人课程</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
            min-height: 100vh;
            color: #1f2937;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 24px;
            border-bottom: 3px solid #667eea;
        }}

        h1 {{ color: #1f2937; font-size: 2.2em; margin-bottom: 10px; }}
        .subtitle {{ color: #6b7280; font-size: 1em; }}
        .update-time {{ color: #9ca3af; font-size: 0.85em; margin-top: 8px; }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: white;
            border: 1px solid #e5e7eb;
            padding: 20px;
            border-radius: 14px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: transform 0.2s;
        }}
        .stat-card:hover {{ transform: translateY(-3px); }}
        .stat-card.highlight {{
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            color: white;
            border: none;
        }}
        .stat-icon {{ font-size: 1.8em; margin-bottom: 6px; }}
        .stat-value {{ font-size: 1.8em; font-weight: 700; }}
        .stat-label {{ font-size: 0.85em; color: inherit; opacity: 0.85; margin-top: 4px; }}

        .scoring-info {{
            background: #f3f4f6;
            border-left: 4px solid #667eea;
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .scoring-info p {{ font-size: 0.9em; color: #4b5563; margin: 2px 0; }}
        .scoring-info strong {{ color: #1f2937; }}

        h2 {{
            text-align: center;
            color: #1f2937;
            margin: 30px 0 20px;
            font-size: 1.5em;
        }}

        .students-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
            margin-bottom: 50px;
        }}

        .student-card {{
            background: white;
            border-radius: 14px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
            overflow: hidden;
            border: 1px solid #e5e7eb;
        }}
        .student-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}

        .card-header {{
            display: flex;
            align-items: center;
            padding: 18px;
            color: white;
            position: relative;
        }}

        .avatar {{
            width: 56px;
            height: 56px;
            border-radius: 50%;
            border: 3px solid white;
            margin-right: 14px;
            background: white;
        }}

        .header-info {{ flex: 1; min-width: 0; }}
        .header-info h3 {{
            font-size: 1.1em;
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .status-badge {{
            display: inline-block;
            padding: 3px 10px;
            background: rgba(255,255,255,0.25);
            border-radius: 12px;
            font-size: 0.78em;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .grade-badge {{
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.05em;
            border: 3px solid white;
            margin-left: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}

        .card-body {{ padding: 18px; }}

        .score-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
            padding-bottom: 14px;
            border-bottom: 1px dashed #e5e7eb;
        }}
        .score-main {{ text-align: left; }}
        .score-value {{ font-size: 2.2em; font-weight: 700; color: #1f2937; line-height: 1; }}
        .score-label {{ font-size: 0.8em; color: #6b7280; margin-top: 2px; }}
        .score-detail {{ text-align: right; font-size: 0.82em; color: #6b7280; }}
        .score-detail strong {{ color: #1f2937; }}

        .week-pills {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-bottom: 14px;
        }}
        .week-pill {{
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-width: 38px;
            height: 34px;
            padding: 2px 4px;
            font-weight: 600;
            border-radius: 6px;
            color: white;
            line-height: 1.1;
        }}
        .week-pill .pill-w {{ font-size: 0.62em; opacity: 0.9; }}
        .week-pill .pill-s {{ font-size: 0.78em; }}
        .week-pill.excellent {{ background: #10b981; }}
        .week-pill.good {{ background: #3b82f6; }}
        .week-pill.pass {{ background: #f59e0b; }}
        .week-pill.weak {{ background: #f97316; }}
        .week-pill.empty {{ background: #e5e7eb; color: #9ca3af; }}

        .repo-link {{
            display: block;
            text-align: center;
            padding: 10px;
            background: #f3f4f6;
            color: #4b5563;
            text-decoration: none;
            border-radius: 8px;
            font-size: 0.9em;
            font-weight: 500;
            transition: background 0.2s;
        }}
        .repo-link:hover {{
            background: #667eea;
            color: white;
        }}

        .week-table-wrapper {{
            margin: 28px 0 40px;
            padding: 24px 0 10px;
            border-top: 2px solid #e5e7eb;
            border-bottom: 2px solid #e5e7eb;
        }}

        .table-scroll {{
            overflow-x: auto;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
        }}

        .week-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}

        .week-table th {{
            background: #667eea;
            color: white;
            padding: 12px 6px;
            text-align: center;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        .week-table th small {{ display: block; font-weight: 400; opacity: 0.85; font-size: 0.85em; }}

        .week-table td {{
            padding: 10px 8px;
            text-align: center;
            border-bottom: 1px solid #f3f4f6;
        }}
        .week-table tr:hover td {{ background: #f9fafb; }}
        .name-col {{ text-align: left !important; padding-left: 14px !important; font-weight: 500; }}
        .name-col a {{ color: #4b5563; text-decoration: none; }}
        .name-col a:hover {{ color: #667eea; }}

        .cell-excellent {{ background: rgba(16, 185, 129, 0.15); color: #047857; font-weight: 600; }}
        .cell-good {{ background: rgba(59, 130, 246, 0.12); color: #1d4ed8; font-weight: 600; }}
        .cell-pass {{ background: rgba(245, 158, 11, 0.15); color: #b45309; font-weight: 600; }}
        .cell-weak {{ background: rgba(249, 115, 22, 0.15); color: #c2410c; font-weight: 600; }}
        .cell-empty {{ color: #d1d5db; }}

        .total-col {{ background: #f3f4f6; font-size: 1.05em; }}
        .grade-col {{ background: #f3f4f6; font-size: 1.1em; }}

        .legend {{
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        .legend-item {{
            font-size: 0.85em;
            padding: 4px 10px;
            border-radius: 6px;
        }}
        .legend-excellent {{ background: rgba(16, 185, 129, 0.15); color: #047857; }}
        .legend-good {{ background: rgba(59, 130, 246, 0.12); color: #1d4ed8; }}
        .legend-pass {{ background: rgba(245, 158, 11, 0.15); color: #b45309; }}
        .legend-weak {{ background: rgba(249, 115, 22, 0.15); color: #c2410c; }}
        .legend-empty {{ background: #f3f4f6; color: #6b7280; }}

        .week-improvements-section, .week14-ranking-section {{
            margin: 40px 0;
            padding: 24px 0;
            border-top: 2px solid #e5e7eb;
        }}

        .improve-students-list {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .improve-student-card {{
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px 18px;
            background: #fafbfc;
        }}

        .improve-student-head {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px dashed #e5e7eb;
        }}

        .improve-avatar {{
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: 2px solid #667eea;
        }}

        .improve-student-head h3 {{ font-size: 1.05em; margin-bottom: 2px; }}
        .improve-student-head a {{ color: #1f2937; text-decoration: none; }}
        .improve-student-head a:hover {{ color: #667eea; }}
        .improve-meta {{ font-size: 0.85em; color: #6b7280; }}

        .ai-overall-comment {{
            background: #eff6ff;
            border-left: 3px solid #3b82f6;
            padding: 10px 12px;
            border-radius: 6px;
            margin-bottom: 12px;
            font-size: 0.9em;
            color: #1e40af;
        }}

        .improve-week {{
            margin: 8px 0;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            background: white;
            overflow: hidden;
        }}

        .improve-week.improve-missing {{
            padding: 10px 12px;
            background: #f9fafb;
        }}

        .improve-week-head {{
            cursor: pointer;
            padding: 10px 12px;
            font-size: 0.92em;
            list-style: none;
        }}

        details.improve-week > summary {{
            list-style: none;
        }}
        details.improve-week > summary::-webkit-details-marker {{ display: none; }}

        .improve-score {{
            margin-left: 8px;
            color: #667eea;
            font-weight: 600;
        }}

        .improve-tag {{
            display: inline-block;
            margin-left: 8px;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.78em;
            font-weight: 600;
        }}
        .tag-excellent {{ background: #d1fae5; color: #047857; }}
        .tag-good {{ background: #dbeafe; color: #1d4ed8; }}
        .tag-pass {{ background: #fef3c7; color: #b45309; }}
        .tag-weak {{ background: #ffedd5; color: #c2410c; }}
        .tag-missing {{ background: #f3f4f6; color: #6b7280; }}

        .improve-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            padding: 0 12px 12px;
        }}

        @media (max-width: 768px) {{
            .improve-grid {{ grid-template-columns: 1fr; }}
        }}

        .improve-grid h4 {{
            font-size: 0.85em;
            color: #4b5563;
            margin-bottom: 6px;
        }}

        .improve-list {{
            margin: 0;
            padding-left: 18px;
            font-size: 0.84em;
            color: #374151;
        }}
        .improve-list li {{ margin: 4px 0; }}
        .suggest-li {{ color: #1d4ed8 !important; }}

        .week14-rubric-mini {{
            margin: 0 12px 8px;
            padding: 8px 10px;
            background: #f0fdf4;
            border-radius: 6px;
            font-size: 0.82em;
            color: #166534;
        }}

        .week14-table .rank-col {{ font-size: 1.1em; color: #667eea; }}
        .week14-table .suggest-col {{
            text-align: left !important;
            font-size: 0.82em;
            color: #4b5563;
            max-width: 220px;
        }}

        .improve-empty {{ font-size: 0.85em; color: #9ca3af; padding: 4px 0; }}

        footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 24px;
            border-top: 2px solid #e5e7eb;
            color: #6b7280;
            font-size: 0.9em;
        }}
        footer a {{ color: #667eea; text-decoration: none; margin: 0 6px; }}
        footer a:hover {{ text-decoration: underline; }}

        /* ===== Pages Carousel ===== */
        .pages-carousel-section {{
            margin: 50px 0;
            padding: 30px;
            background: linear-gradient(135deg, #f8f9fa, #ffffff);
            border-radius: 16px;
            border: 1px solid #e5e7eb;
        }}

        .pages-carousel-wrap {{
            position: relative;
            margin: 20px 0;
        }}

        .pages-carousel {{
            display: flex;
            gap: 20px;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            scroll-behavior: smooth;
            padding: 10px 4px 20px;
            scrollbar-width: thin;
            scrollbar-color: #667eea #e5e7eb;
        }}

        .pages-carousel::-webkit-scrollbar {{
            height: 8px;
        }}
        .pages-carousel::-webkit-scrollbar-track {{
            background: #f3f4f6;
            border-radius: 4px;
        }}
        .pages-carousel::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 4px;
        }}

        .pages-slide {{
            flex: 0 0 480px;
            scroll-snap-align: start;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid #e5e7eb;
        }}
        .pages-slide:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }}

        .pages-slide-header {{
            display: flex;
            align-items: center;
            padding: 14px 16px;
            color: white;
        }}
        .pages-avatar {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            border: 2px solid white;
            background: white;
            margin-right: 12px;
        }}
        .pages-slide-info {{
            flex: 1;
            min-width: 0;
        }}
        .pages-slide-info h3 {{
            font-size: 1em;
            margin-bottom: 2px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .pages-meta {{
            display: flex;
            gap: 8px;
            font-size: 0.78em;
            opacity: 0.95;
        }}
        .pages-score {{
            background: white;
            padding: 2px 8px;
            border-radius: 8px;
            font-weight: 700;
        }}
        .pages-repo {{
            background: rgba(255,255,255,0.25);
            padding: 2px 8px;
            border-radius: 8px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 180px;
        }}
        .pages-actions {{
            display: flex;
            gap: 6px;
        }}
        .pages-action-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background: rgba(255,255,255,0.25);
            border-radius: 8px;
            text-decoration: none;
            color: white;
            font-size: 1em;
            transition: background 0.2s;
        }}
        .pages-action-btn:hover {{
            background: rgba(255,255,255,0.45);
        }}

        .pages-iframe-wrap {{
            position: relative;
            width: 100%;
            height: 320px;
            background: #f9fafb;
            overflow: hidden;
        }}
        .pages-iframe-wrap iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
            transform: scale(0.85);
            transform-origin: 0 0;
            width: 117.6%;
            height: 117.6%;
        }}
        .pages-iframe-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            padding: 16px;
            background: linear-gradient(to top, rgba(0,0,0,0.6), transparent 30%);
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
        }}
        .pages-slide:hover .pages-iframe-overlay {{
            opacity: 1;
        }}
        .pages-open-btn {{
            display: inline-block;
            padding: 8px 18px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            pointer-events: auto;
        }}
        .pages-open-btn:hover {{
            transform: scale(1.05);
        }}

        .carousel-nav {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: none;
            background: white;
            color: #667eea;
            font-size: 1.6em;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 5;
            transition: transform 0.2s, background 0.2s;
        }}
        .carousel-nav:hover {{
            transform: translateY(-50%) scale(1.1);
            background: #667eea;
            color: white;
        }}
        .carousel-nav.prev {{ left: -10px; }}
        .carousel-nav.next {{ right: -10px; }}

        .health-pill {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            font-size: 0.78em;
        }}

        .pages-feedback {{
            padding: 12px 16px;
            background: #fafbfc;
            border-top: 1px solid #e5e7eb;
            font-size: 0.85em;
        }}

        .pages-feedback details summary {{
            cursor: pointer;
            font-weight: 600;
            color: #4b5563;
            outline: none;
            user-select: none;
            padding: 4px 0;
        }}
        .pages-feedback details summary:hover {{ color: #667eea; }}
        .pages-feedback details[open] summary {{ margin-bottom: 8px; }}

        .feedback-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .feedback-list li {{
            padding: 4px 0;
            color: #4b5563;
            line-height: 1.5;
        }}
        .issue-item {{ color: #b45309 !important; }}
        .suggestion-item {{ color: #1d4ed8 !important; }}

        .feedback-perfect {{
            color: #10b981;
            font-weight: 600;
            padding: 4px 0;
        }}

        .broken-images-list {{
            margin-top: 10px;
            padding: 10px;
            background: #fef2f2;
            border-left: 3px solid #ef4444;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .broken-images-list strong {{
            color: #991b1b;
            display: block;
            margin-bottom: 4px;
        }}
        .broken-images-list ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .broken-images-list li {{
            padding: 2px 0;
            color: #4b5563;
        }}
        .broken-images-list code {{
            background: white;
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 0.85em;
            color: #b91c1c;
        }}

        @media (max-width: 768px) {{
            .container {{ padding: 20px; }}
            h1 {{ font-size: 1.6em; }}
            .students-grid {{ grid-template-columns: 1fr; }}
            .pages-slide {{ flex: 0 0 calc(100vw - 100px); }}
            .pages-iframe-wrap {{ height: 240px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 学生作业展示</h1>
            <p class="subtitle">AI机器人课程 · 自动化评价系统</p>
            <p class="update-time">最后更新: {eval_time} · 每24小时自动更新</p>
        </header>

        {stats_html}

        <div class="scoring-info">
            <p><strong>📊 评分制度</strong>：{data.get('scoring_system', '总分100分（内容70% + 态度30%）')}</p>
            <p><strong>🔒 隐私保护</strong>：仅显示 GitHub ID 与头像，不公开学生姓名、学号等敏感信息。</p>
            <p><strong>ℹ️ 说明</strong>：每周得分按权重加权后计入总分。卡片上的彩色标签直接显示 W 周次 + 加权分；下方表格可看全员对比。
            <a href="#week-improvements" style="color:#667eea;font-weight:600;">改进提示 ↓</a> ·
            <a href="#week14-ranking" style="color:#667eea;font-weight:600;">第14周排名 ↓</a> ·
            <a href="#week-scores" style="color:#667eea;font-weight:600;">得分表 ↓</a></p>
        </div>

        {table_html}

        {week14_ranking_html}

        {improvements_html}

        {carousel_html}

        <h2>📚 学生排名（按总分）</h2>
        <div class="students-grid">
            {cards_html}
        </div>

        <footer>
            <p>AI 机器人课程 · 信韩大学 软件学院 · 2026</p>
            <p style="margin-top: 8px;">
                <a href="https://ai-robot-class.github.io/">课程主页</a> |
                <a href="https://github.com/ai-robot-class">GitHub组织</a>
            </p>
        </footer>
    </div>

    <script>
        function scrollCarousel(direction) {{
            const carousel = document.getElementById('pagesCarousel');
            if (!carousel) return;
            const slideWidth = carousel.querySelector('.pages-slide')?.offsetWidth || 500;
            carousel.scrollBy({{ left: direction * (slideWidth + 20), behavior: 'smooth' }});
        }}

        // 监听键盘左右键控制滑窗
        document.addEventListener('keydown', (e) => {{
            const carousel = document.getElementById('pagesCarousel');
            if (!carousel) return;
            if (e.key === 'ArrowLeft') scrollCarousel(-1);
            if (e.key === 'ArrowRight') scrollCarousel(1);
        }});
    </script>
</body>
</html>
"""


def main():
    print("📄 生成学生作业展示页面...")
    data = load_evaluation_results()
    if not data:
        print("❌ 未找到评价结果文件")
        return

    html = generate_html(data)

    output = Path('students/index.html')
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 展示页面已生成: {output}")
    print(f"📊 共展示 {len(data['students'])} 名学生")


if __name__ == '__main__':
    main()

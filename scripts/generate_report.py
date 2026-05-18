#!/usr/bin/env python3
"""
生成学生作业展示页面
"""

import json
from pathlib import Path
from datetime import datetime


def load_evaluation_results():
    """加载最新评价结果"""
    results_file = Path('students/evaluations/latest.json')
    if not results_file.exists():
        return None
    
    with open(results_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_student_card(student):
    """生成单个学生的卡片HTML"""
    repo_exists = student['repo_exists']
    github_id = student['github_id']
    repo_url = student['repo_url']
    
    if not repo_exists:
        status_badge = "🔴 仓库未创建"
        progress_html = ""
        score_html = "<p class='score error'>N/A</p>"
    else:
        total_score = student['total_score']
        avg_score = student['average_score']
        weeks = student['weeks']
        completed = sum(1 for w in weeks.values() if w['score'] > 50)
        total_weeks = len(weeks)
        
        status_badge = "🟢 进行中" if completed < total_weeks else "🎉 已完成"
        
        # 进度条
        progress_pct = (completed / total_weeks * 100) if total_weeks > 0 else 0
        progress_html = f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_pct}%"></div>
        </div>
        <p class="progress-text">{completed}/{total_weeks} 周完成</p>
        """
        
        score_html = f"<p class='score'>{avg_score:.1f}/100</p>"
    
    return f"""
    <div class="student-card">
        <div class="student-header">
            <img src="https://github.com/{github_id}.png" alt="@{github_id}" class="avatar">
            <div class="student-info">
                <h3>@{github_id}</h3>
                <span class="status-badge">{status_badge}</span>
            </div>
        </div>
        <div class="student-body">
            {progress_html}
            <div class="score-section">
                <label>平均分</label>
                {score_html}
            </div>
            <a href="{repo_url}" target="_blank" class="repo-link">
                📂 查看仓库 →
            </a>
        </div>
    </div>
    """


def generate_week_details_table(students):
    """生成各周详情表格"""
    weeks = ['week2', 'week3', 'week4', 'week5', 'week6', 'week7', 'week8', 
             'week9', 'week10', 'week11', 'week12', 'week13']
    
    html = """
    <div class="week-details">
        <h2>📊 各周作业完成情况</h2>
        <div class="table-responsive">
            <table class="details-table">
                <thead>
                    <tr>
                        <th>学生</th>
    """
    
    for week in weeks:
        html += f"<th>{week.replace('week', 'W')}</th>"
    
    html += "<th>平均分</th></tr></thead><tbody>"
    
    for student in students:
        if not student['repo_exists']:
            continue
        
        html += f"""
        <tr>
            <td><a href="{student['repo_url']}" target="_blank">@{student['github_id']}</a></td>
        """
        
        for week in weeks:
            week_data = student['weeks'].get(week, {})
            score = week_data.get('score', 0)
            
            # 颜色编码
            if score >= 80:
                color_class = "excellent"
            elif score >= 60:
                color_class = "good"
            elif score > 0:
                color_class = "pass"
            else:
                color_class = "not-submitted"
            
            html += f'<td class="{color_class}">{score}</td>'
        
        avg = student['average_score']
        avg_class = "excellent" if avg >= 80 else "good" if avg >= 60 else "pass"
        html += f'<td class="{avg_class}"><strong>{avg:.0f}</strong></td>'
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
        </div>
        <div class="legend">
            <span class="legend-item excellent">■ 优秀 (80+)</span>
            <span class="legend-item good">■ 良好 (60-79)</span>
            <span class="legend-item pass">■ 及格 (1-59)</span>
            <span class="legend-item not-submitted">■ 未提交 (0)</span>
        </div>
    </div>
    """
    
    return html


def generate_stats_summary(students):
    """生成统计摘要"""
    total = len(students)
    active = sum(1 for s in students if s['repo_exists'])
    
    if active == 0:
        return "<div class='stats-summary'><p>暂无学生提交作业</p></div>"
    
    active_students = [s for s in students if s['repo_exists']]
    avg_score = sum(s['average_score'] for s in active_students) / len(active_students)
    
    # 最高分学生
    top_student = max(active_students, key=lambda x: x['total_score'])
    
    html = f"""
    <div class="stats-summary">
        <div class="stat-card">
            <div class="stat-value">{total}</div>
            <div class="stat-label">总学生数</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{active}</div>
            <div class="stat-label">已提交</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{avg_score:.1f}</div>
            <div class="stat-label">平均分</div>
        </div>
        <div class="stat-card highlight">
            <div class="stat-value">🏆 @{top_student['github_id']}</div>
            <div class="stat-label">第一名 ({top_student['total_score']:.0f}分)</div>
        </div>
    </div>
    """
    
    return html


def generate_html_page(data):
    """生成完整HTML页面"""
    students = data['students']
    eval_date = data['evaluation_date']
    eval_time = datetime.fromisoformat(eval_date).strftime('%Y年%m月%d日 %H:%M')
    
    # 按总分排序
    students_sorted = sorted(
        students, 
        key=lambda x: x.get('total_score', 0) if x['repo_exists'] else -1, 
        reverse=True
    )
    
    stats_html = generate_stats_summary(students_sorted)
    cards_html = "\n".join(generate_student_card(s) for s in students_sorted)
    table_html = generate_week_details_table(students_sorted)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学生作业展示 - AI机器人课程</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
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
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        
        h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .update-time {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .stats-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .stat-card.highlight {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1em;
            opacity: 0.9;
        }}
        
        .students-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
            margin-bottom: 50px;
        }}
        
        .student-card {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            overflow: hidden;
        }}
        
        .student-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .student-header {{
            display: flex;
            align-items: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .avatar {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: 3px solid white;
            margin-right: 15px;
        }}
        
        .student-info h3 {{
            font-size: 1.2em;
            margin-bottom: 5px;
        }}
        
        .github-id {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            font-size: 0.85em;
            margin-top: 5px;
        }}
        
        .student-body {{
            padding: 20px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 10px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s;
        }}
        
        .progress-text {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        
        .score-section {{
            text-align: center;
            margin: 15px 0;
        }}
        
        .score-section label {{
            display: block;
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        
        .score {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .score.error {{
            color: #999;
        }}
        
        .repo-link {{
            display: block;
            text-align: center;
            padding: 12px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: background 0.3s;
        }}
        
        .repo-link:hover {{
            background: #764ba2;
        }}
        
        .week-details {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #e0e0e0;
        }}
        
        .week-details h2 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }}
        
        .table-responsive {{
            overflow-x: auto;
        }}
        
        .details-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        
        .details-table th,
        .details-table td {{
            padding: 12px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        
        .details-table th {{
            background: #667eea;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
        }}
        
        .details-table td {{
            font-weight: 500;
        }}
        
        .details-table tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        
        .details-table tr:hover {{
            background: #f0f0f0;
        }}
        
        .excellent {{ background: #4caf50 !important; color: white; }}
        .good {{ background: #8bc34a !important; color: white; }}
        .pass {{ background: #ffc107 !important; color: #333; }}
        .not-submitted {{ background: #f5f5f5 !important; color: #999; }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        .legend-item {{
            font-size: 0.9em;
            padding: 5px 10px;
            border-radius: 5px;
        }}
        
        footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #e0e0e0;
            color: #666;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 1.8em;
            }}
            
            .students-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats-summary {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 学生作业展示</h1>
            <p class="update-time">最后更新: {eval_time} | 自动评价系统</p>
        </header>
        
        {stats_html}
        
        <h2 style="text-align: center; margin-bottom: 30px; color: #333;">📚 学生列表</h2>
        <div class="students-grid">
            {cards_html}
        </div>
        
        {table_html}
        
        <footer>
            <p>AI机器人课程 · 神韩大学校 · 2026</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                <a href="https://course.a-real.me" style="color: #667eea; text-decoration: none;">课程主页</a> | 
                <a href="https://github.com/ai-robot-class" style="color: #667eea; text-decoration: none;">GitHub</a>
            </p>
        </footer>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """主函数"""
    print("📄 生成学生作业展示页面...")
    
    # 加载评价结果
    data = load_evaluation_results()
    if not data:
        print("❌ 未找到评价结果文件")
        return
    
    # 生成HTML
    html = generate_html_page(data)
    
    # 保存文件
    output_file = Path('students/index.html')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 展示页面已生成: {output_file}")
    print(f"🌐 可通过GitHub Pages访问: https://your-username.github.io/your-repo/students/")


if __name__ == '__main__':
    main()

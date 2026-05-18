#!/usr/bin/env python3
"""
学生作业自动评价脚本 - 高效版
- 总分100分制（内容70% + 态度30%）
- 使用Git Trees API一次获取整个仓库结构（大幅减少API调用）
"""

import os
import json
import base64
import requests
import subprocess
import re
from datetime import datetime, timezone
from pathlib import Path


def get_github_token():
    """从环境变量或gh hosts.yml获取token"""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        try:
            hosts_file = Path.home() / '.config' / 'gh' / 'hosts.yml'
            if hosts_file.exists():
                with open(hosts_file) as f:
                    for line in f:
                        if 'oauth_token' in line:
                            token = line.split(':', 1)[1].strip()
                            break
        except Exception:
            pass
    return token


GITHUB_TOKEN = get_github_token()
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}

WEEKS = {
    'week2':  {'title': 'ROS2环境配置',     'weight': 5,  'due_date': '2026-03-15'},
    'week3':  {'title': 'GitHub与命令行',   'weight': 5,  'due_date': '2026-03-22'},
    'week4':  {'title': 'Python仿真',       'weight': 8,  'due_date': '2026-03-29'},
    'week5':  {'title': '机器人运动学',     'weight': 8,  'due_date': '2026-04-05'},
    'week6':  {'title': 'KITTI实验',        'weight': 8,  'due_date': '2026-04-12'},
    'week7':  {'title': 'Markdown整理',     'weight': 5,  'due_date': '2026-04-19'},
    'week8':  {'title': 'Docker容器',       'weight': 8,  'due_date': '2026-04-26'},
    'week9':  {'title': '数学基础',         'weight': 8,  'due_date': '2026-05-03'},
    'week10': {'title': 'YOLO检测',         'weight': 10, 'due_date': '2026-05-10'},
    'week11': {'title': '目标追踪',         'weight': 10, 'due_date': '2026-05-17'},
    'week12': {'title': '视觉与语音',       'weight': 10, 'due_date': '2026-05-24'},
    'week13': {'title': '期末项目',         'weight': 15, 'due_date': '2026-06-22'},
}

IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp')
CODE_EXTS = ('.py', '.cpp', '.c', '.h', '.hpp', '.java', '.js', '.ts',
             '.launch.py', '.sh', '.yaml', '.yml', '.cmake')
DOC_EXTS = ('.pdf', '.doc', '.docx', '.txt', '.markdown')
VIDEO_EXTS = ('.mp4', '.avi', '.mov', '.mkv', '.webm')


def load_students():
    """从 students/roster.json 加载学生列表"""
    roster_file = Path('students/roster.json')
    if not roster_file.exists():
        print("⚠️  学生名单文件不存在")
        return []

    with open(roster_file, 'r', encoding='utf-8') as f:
        repo_urls = json.load(f)

    students = []
    for url in repo_urls:
        parts = url.rstrip('/').replace('.git', '').split('/')
        if len(parts) >= 4:
            students.append({
                'github_id': parts[-2],
                'repo_url': url.rstrip('/').replace('.git', ''),
                'repo_name': parts[-1].replace('.git', '')
            })
    return students


def fetch_repo_info(owner, repo_name):
    """获取仓库基本信息"""
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code == 200:
        return True, response.json()
    return False, f"HTTP {response.status_code}: {response.json().get('message', 'Unknown')}"


def fetch_repo_tree(owner, repo_name, default_branch):
    """一次性获取仓库完整文件树"""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/{default_branch}?recursive=1"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code == 200:
        return response.json().get('tree', [])
    return []


def fetch_recent_commits(owner, repo_name, per_page=100):
    """获取最近的提交"""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page={per_page}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code == 200:
        return response.json()
    return []


def fetch_file_content(owner, repo_name, path):
    """获取单个文件内容"""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code == 200:
        data = response.json()
        try:
            return base64.b64decode(data.get('content', '')).decode('utf-8', errors='ignore')
        except Exception:
            return None
    return None


def normalize_week_id(name):
    """从路径名中识别 week 编号"""
    m = re.match(r'^[Ww]eek[_-]?(\d+)', name)
    if m:
        return f"week{int(m.group(1))}"
    m = re.match(r'^(\d+)[_-]?[Ww]eek', name)
    if m:
        return f"week{int(m.group(1))}"
    return None


def group_files_by_week(tree):
    """根据文件路径将文件按周分组"""
    week_files = {wk: [] for wk in WEEKS}
    week_paths = {wk: None for wk in WEEKS}

    for item in tree:
        path = item.get('path', '')
        if not path:
            continue
        parts = path.split('/')
        top = parts[0]
        wk = normalize_week_id(top)
        if wk and wk in week_files:
            week_files[wk].append(item)
            if week_paths[wk] is None:
                week_paths[wk] = top

    return week_files, week_paths


def analyze_week(week_id, week_info, files, actual_folder,
                 commits_by_path, owner, repo_name):
    """分析单周作业"""
    result = {
        'submitted': False,
        'content_score': 0,
        'attitude_score': 0,
        'details': {},
        'comments': []
    }

    if not files:
        result['comments'].append("❌ 未提交作业")
        return result

    result['submitted'] = True
    result['comments'].append(f"✅ 已提交（路径: {actual_folder}）")

    readme_size = 0
    readme_path = None
    image_count = 0
    code_count = 0
    doc_count = 0
    video_count = 0
    total_files = 0

    for f in files:
        if f.get('type') != 'blob':
            continue
        total_files += 1
        path = f['path']
        name = path.split('/')[-1].lower()
        size = f.get('size', 0)

        if name == 'readme.md':
            readme_size = max(readme_size, size)
            readme_path = path
        elif name.endswith(IMAGE_EXTS):
            image_count += 1
        elif name.endswith(CODE_EXTS):
            code_count += 1
        elif name.endswith(DOC_EXTS):
            doc_count += 1
        elif name.endswith(VIDEO_EXTS):
            video_count += 1

    content_score = 0

    if readme_path:
        if readme_size > 3000:
            content_score += 40
            result['comments'].append("📝 README非常详细（>3000字符）")
        elif readme_size > 1500:
            content_score += 35
            result['comments'].append("📝 README很详细")
        elif readme_size > 500:
            content_score += 25
            result['comments'].append("📝 README较详细")
        else:
            content_score += 15
            result['comments'].append("📝 README较简单")

        try:
            content = fetch_file_content(owner, repo_name, readme_path)
            if content:
                depth_bonus = 0
                if any(k in content for k in ['问题', '思考', '难点', '错误']):
                    depth_bonus += 3
                    result['comments'].append("💡 包含问题/思考")
                if any(k in content for k in ['总结', '心得', '收获', '反思']):
                    depth_bonus += 3
                    result['comments'].append("💡 包含学习总结")
                if any(k in content for k in ['步骤', '过程', '流程', '## ']):
                    depth_bonus += 2
                    result['comments'].append("💡 结构化记录")
                content_score += depth_bonus
        except Exception:
            pass
    else:
        result['comments'].append("❌ 缺少README")

    if image_count >= 5:
        content_score += 15
        result['comments'].append(f"📷 丰富的图片（{image_count}张）")
    elif image_count >= 3:
        content_score += 12
        result['comments'].append(f"📷 较多图片（{image_count}张）")
    elif image_count >= 1:
        content_score += 8
        result['comments'].append(f"📷 有图片（{image_count}张）")

    if code_count >= 3:
        content_score += 15
        result['comments'].append(f"💻 多个代码文件（{code_count}个）")
    elif code_count >= 1:
        content_score += 10
        result['comments'].append(f"💻 有代码（{code_count}个）")

    if video_count > 0:
        content_score += 3
        result['comments'].append("🎬 包含视频演示")
    if doc_count > 0:
        content_score += 2
        result['comments'].append("📄 包含额外文档")

    result['content_score'] = min(content_score, 70)

    related_commits = commits_by_path.get(actual_folder, [])
    commit_count = len(related_commits)
    attitude_score = 0

    if commit_count >= 5:
        attitude_score += 15
        result['comments'].append(f"⭐ 多次提交迭代（{commit_count}次）")
    elif commit_count >= 3:
        attitude_score += 12
        result['comments'].append(f"⭐ 多次提交（{commit_count}次）")
    elif commit_count >= 1:
        attitude_score += 8
        result['comments'].append(f"⭐ 有提交（{commit_count}次）")

    if related_commits:
        try:
            last_commit_str = related_commits[0]
            last_commit = datetime.fromisoformat(last_commit_str.replace('Z', '+00:00'))
            due_date = datetime.fromisoformat(week_info['due_date']).replace(tzinfo=timezone.utc)
            days_diff = (due_date - last_commit).days

            if days_diff >= 7:
                attitude_score += 15
                result['comments'].append("🎉 提前一周以上完成")
            elif days_diff >= 3:
                attitude_score += 13
                result['comments'].append("🎉 提前3天以上完成")
            elif days_diff >= 0:
                attitude_score += 10
                result['comments'].append("✅ 按时完成")
            elif days_diff >= -7:
                attitude_score += 5
                result['comments'].append(f"⏰ 稍延迟（{-days_diff}天）")
            else:
                result['comments'].append(f"⏰ 延迟{-days_diff}天")
        except Exception:
            pass

    result['attitude_score'] = min(attitude_score, 30)
    result['details'] = {
        'readme_size': readme_size,
        'image_count': image_count,
        'code_count': code_count,
        'video_count': video_count,
        'doc_count': doc_count,
        'commit_count': commit_count,
        'total_files': total_files,
    }
    return result


def group_commits_by_top_folder(commits):
    """按顶层文件夹分组提交日期（基于 commit message 启发式判断）"""
    by_folder = {}
    for c in commits:
        date = c['commit']['author']['date']
        msg = (c['commit'].get('message') or '').lower()
        for wk in WEEKS:
            num = wk[4:]
            patterns = [wk, f'week {num}', f'第{num}周', f'w{num}', f'_{wk}_', f'{wk}/']
            if any(p in msg for p in patterns):
                by_folder.setdefault(wk, []).append(date)
    return by_folder


def evaluate_student(student):
    github_id = student['github_id']
    repo_url = student['repo_url']
    repo_name = student['repo_name']
    print(f"\n📊 评估学生: @{github_id}")

    owner = github_id
    exists, repo_or_error = fetch_repo_info(owner, repo_name)

    if not exists:
        print(f"  ❌ 仓库不可访问: {repo_or_error}")
        return {
            'github_id': github_id,
            'repo_url': repo_url,
            'repo_exists': False,
            'error': str(repo_or_error),
            'weeks': {},
            'total_score': 0,
            'grade': 'N/A',
            'evaluation_date': datetime.now().isoformat()
        }

    repo_info = repo_or_error
    default_branch = repo_info.get('default_branch', 'main')
    print(f"  ✅ 仓库: {repo_info.get('name')} (默认分支: {default_branch})")

    tree = fetch_repo_tree(owner, repo_name, default_branch)
    if not tree:
        tree = fetch_repo_tree(owner, repo_name, 'master')

    commits = fetch_recent_commits(owner, repo_name, per_page=100)

    week_files, week_paths = group_files_by_week(tree)

    commits_by_folder = {}
    for c in commits:
        date = c['commit']['author']['date']
        msg = (c['commit'].get('message') or '').lower()
        for wk in WEEKS:
            num = wk[4:]
            if (wk in msg or f'week {num}' in msg or f'第{num}周' in msg
                    or f'w{num} ' in msg or msg.startswith(f'week{num}')):
                if week_paths.get(wk):
                    commits_by_folder.setdefault(week_paths[wk], []).append(date)

    fallback_dates = [c['commit']['author']['date'] for c in commits]

    weeks_result = {}
    total_score = 0.0

    for week_id, week_info in WEEKS.items():
        actual_path = week_paths.get(week_id)
        files = week_files.get(week_id, [])
        related = commits_by_folder.get(actual_path, []) if actual_path else []

        if not related and files:
            related = fallback_dates[:5]

        wk_result = analyze_week(week_id, week_info, files, actual_path or week_id,
                                 commits_by_folder, owner, repo_name)
        if not commits_by_folder.get(actual_path) and related:
            commit_count = len(related)
            try:
                last = datetime.fromisoformat(related[0].replace('Z', '+00:00'))
                due = datetime.fromisoformat(week_info['due_date']).replace(tzinfo=timezone.utc)
                days_diff = (due - last).days
                attitude = wk_result['attitude_score']
                if commit_count >= 3 and 'commit_count' in wk_result['details'] and wk_result['details']['commit_count'] == 0:
                    attitude = max(attitude, 8)
                wk_result['attitude_score'] = attitude
                wk_result['details']['commit_count'] = max(wk_result['details'].get('commit_count', 0), commit_count)
            except Exception:
                pass

        raw_score = wk_result['content_score'] + wk_result['attitude_score']
        final_score = raw_score * week_info['weight'] / 100
        wk_result['raw_score'] = raw_score
        wk_result['final_score'] = round(final_score, 2)
        weeks_result[week_id] = wk_result
        total_score += final_score

        print(f"  📝 {week_id} ({week_info['title']}): {raw_score}/100 → {final_score:.1f}/{week_info['weight']}")

    grade = (
        'A+' if total_score >= 90 else
        'A'  if total_score >= 85 else
        'A-' if total_score >= 80 else
        'B+' if total_score >= 75 else
        'B'  if total_score >= 70 else
        'B-' if total_score >= 65 else
        'C+' if total_score >= 60 else
        'C'  if total_score >= 55 else
        'C-' if total_score >= 50 else
        'D'  if total_score >= 30 else
        'F'
    )
    print(f"  🎯 总分: {total_score:.1f}/100  等级: {grade}")

    return {
        'github_id': github_id,
        'repo_url': repo_url,
        'repo_exists': True,
        'repo_name': repo_info.get('name'),
        'repo_description': repo_info.get('description') or '',
        'stars': repo_info.get('stargazers_count', 0),
        'forks': repo_info.get('forks_count', 0),
        'default_branch': default_branch,
        'total_files': len(tree),
        'total_commits': len(commits),
        'weeks': weeks_result,
        'total_score': round(total_score, 1),
        'grade': grade,
        'evaluation_date': datetime.now().isoformat()
    }


def main():
    print("🚀 开始自动评价学生作业...")
    print(f"📊 评分制度: 总分100分（内容70% + 态度30%）")
    print(f"🔑 GitHub Token: {'已配置✅' if GITHUB_TOKEN else '未配置❌'}\n")

    students = load_students()
    if not students:
        print("❌ 未找到学生")
        return

    print(f"📋 共 {len(students)} 名学生\n")

    results = []
    for student in students:
        try:
            result = evaluate_student(student)
        except Exception as e:
            print(f"  ⚠️  评估异常: {e}")
            result = {
                'github_id': student['github_id'],
                'repo_url': student['repo_url'],
                'repo_exists': False,
                'error': f"评估异常: {e}",
                'weeks': {},
                'total_score': 0,
                'grade': 'N/A',
                'evaluation_date': datetime.now().isoformat()
            }
        results.append(result)

    output_dir = Path('students/evaluations')
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        'evaluation_date': datetime.now().isoformat(),
        'scoring_system': '总分100分（内容70% + 态度30%）',
        'weeks': {wk: {'title': info['title'], 'weight': info['weight'],
                       'due_date': info['due_date']} for wk, info in WEEKS.items()},
        'students': results
    }

    latest_file = output_dir / 'latest.json'
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 评价完成: {latest_file}")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    history_file = output_dir / f'evaluation_{timestamp}.json'
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"📚 历史: {history_file}")

    print("\n" + "="*60)
    print("📊 评价统计")
    print("="*60)

    active = [r for r in results if r['repo_exists']]
    submitted = [r for r in active if r['total_score'] > 0]
    if active:
        avg = sum(r['total_score'] for r in active) / len(active)
        avg_sub = sum(r['total_score'] for r in submitted) / max(len(submitted), 1)
        print(f"总学生: {len(results)}  仓库可访问: {len(active)}  有作业: {len(submitted)}")
        print(f"平均分(全部): {avg:.1f}  平均分(有作业): {avg_sub:.1f}")

        print("\n📈 成绩分布:")
        grade_dist = {}
        for r in active:
            grade_dist[r['grade']] = grade_dist.get(r['grade'], 0) + 1
        for g in ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F', 'N/A']:
            if g in grade_dist:
                print(f"  {g:3s}: {grade_dist[g]}人")

        top = sorted(active, key=lambda x: x['total_score'], reverse=True)[:10]
        print("\n🏆 前10名:")
        for i, s in enumerate(top, 1):
            print(f"  {i:2d}. @{s['github_id']:30s}  {s['total_score']:5.1f}分  {s['grade']}")
    else:
        print("无可访问的仓库")

    print("\n✨ 评价结束\n")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
学生作业自动评价脚本 - 总分100分制
评价重点：内容完成度和学习态度
"""

import os
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# 获取GitHub Token
def get_github_token():
    """从环境变量或gh cli获取token"""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        try:
            result = subprocess.run(['gh', 'auth', 'token'], 
                                  capture_output=True, text=True, check=True)
            token = result.stdout.strip()
        except:
            pass
    return token

GITHUB_TOKEN = get_github_token()
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}

# 课程周次配置
WEEKS = {
    'week2': {'title': 'ROS2环境配置', 'weight': 5, 'due_date': '2026-03-15'},
    'week3': {'title': 'GitHub与命令行', 'weight': 5, 'due_date': '2026-03-22'},
    'week4': {'title': 'Python仿真', 'weight': 8, 'due_date': '2026-03-29'},
    'week5': {'title': '机器人运动学', 'weight': 8, 'due_date': '2026-04-05'},
    'week6': {'title': 'KITTI实验', 'weight': 8, 'due_date': '2026-04-12'},
    'week7': {'title': 'Markdown整理', 'weight': 5, 'due_date': '2026-04-19'},
    'week8': {'title': 'Docker容器', 'weight': 8, 'due_date': '2026-04-26'},
    'week9': {'title': '数学基础', 'weight': 8, 'due_date': '2026-05-03'},
    'week10': {'title': 'YOLO检测', 'weight': 10, 'due_date': '2026-05-10'},
    'week11': {'title': '目标追踪', 'weight': 10, 'due_date': '2026-05-17'},
    'week12': {'title': '视觉与语音', 'weight': 10, 'due_date': '2026-05-24'},
    'week13': {'title': '期末项目', 'weight': 15, 'due_date': '2026-05-31'},
}

TOTAL_WEIGHT = sum(w['weight'] for w in WEEKS.values())  # 100分


def load_students():
    """加载学生名单"""
    roster_file = Path('students/roster.json')
    if not roster_file.exists():
        print("⚠️  学生名单文件不存在: students/roster.json")
        return []
    
    with open(roster_file, 'r', encoding='utf-8') as f:
        repo_urls = json.load(f)
    
    students = []
    for url in repo_urls:
        parts = url.rstrip('/').split('/')
        if len(parts) >= 4:
            github_id = parts[-2]
            students.append({
                'github_id': github_id,
                'repo_url': url
            })
    
    return students


def check_repo_exists(repo_url):
    """检查仓库是否存在"""
    try:
        parts = repo_url.rstrip('/').split('/')
        owner, repo_name = parts[-2], parts[-1]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        response = requests.get(api_url, headers=HEADERS)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)


def get_readme_content(owner, repo_name, path):
    """获取README内容"""
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}/readme/{path}"
        response = requests.get(api_url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            # 解码base64内容
            import base64
            content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
            return content
        return None
    except:
        return None


def analyze_week_content(owner, repo_name, week_id, week_info):
    """分析单周作业内容质量和态度"""
    result = {
        'submitted': False,
        'content_score': 0,  # 内容完成度（0-70%）
        'attitude_score': 0,  # 学习态度（0-30%）
        'details': {},
        'comments': []
    }
    
    try:
        # 检查是否有作业提交（支持多种文件夹命名）
        possible_paths = [week_id, week_id.upper(), f"Week{week_id[4:]}", 
                         week_info['title'], week_info['title'].lower()]
        
        contents = None
        actual_path = None
        
        for path in possible_paths:
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
            response = requests.get(api_url, headers=HEADERS)
            if response.status_code == 200:
                contents = response.json()
                actual_path = path
                break
        
        if not contents:
            result['comments'].append("❌ 未提交作业")
            return result
        
        result['submitted'] = True
        result['comments'].append(f"✅ 已提交（路径: {actual_path}）")
        
        # 分析文件内容
        has_readme = False
        readme_size = 0
        readme_content = None
        image_count = 0
        code_count = 0
        doc_count = 0
        video_count = 0
        
        for item in contents:
            name_lower = item['name'].lower()
            
            # README分析
            if name_lower == 'readme.md':
                has_readme = True
                readme_size = item['size']
                readme_content = get_readme_content(owner, repo_name, f"{actual_path}/README.md")
            
            # 图片
            elif name_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')):
                image_count += 1
            
            # 代码
            elif name_lower.endswith(('.py', '.cpp', '.c', '.h', '.java', '.js', '.launch.py')):
                code_count += 1
            
            # 文档
            elif name_lower.endswith(('.pdf', '.doc', '.docx', '.txt')):
                doc_count += 1
            
            # 视频
            elif name_lower.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_count += 1
        
        # 内容完成度评分（70%）
        content_score = 0
        
        # 1. README质量（最高40分）
        if has_readme:
            if readme_size > 3000:
                content_score += 40
                result['comments'].append("📝 README非常详细（>3000字符）")
            elif readme_size > 1500:
                content_score += 35
                result['comments'].append("📝 README很详细（1500-3000字符）")
            elif readme_size > 500:
                content_score += 25
                result['comments'].append("📝 README较详细（500-1500字符）")
            else:
                content_score += 15
                result['comments'].append("📝 README较简单（<500字符）")
            
            # 分析README内容深度
            if readme_content:
                depth_bonus = 0
                if '问题' in readme_content or '思考' in readme_content:
                    depth_bonus += 3
                    result['comments'].append("💡 包含问题思考")
                if '总结' in readme_content or '心得' in readme_content:
                    depth_bonus += 3
                    result['comments'].append("💡 包含学习总结")
                if '步骤' in readme_content or '过程' in readme_content:
                    depth_bonus += 2
                    result['comments'].append("💡 记录了操作步骤")
                content_score += depth_bonus
        else:
            result['comments'].append("❌ 缺少README文档")
        
        # 2. 图片和截图（最高15分）
        if image_count >= 5:
            content_score += 15
            result['comments'].append(f"📷 丰富的图片资料（{image_count}张）")
        elif image_count >= 3:
            content_score += 12
            result['comments'].append(f"📷 较多图片（{image_count}张）")
        elif image_count >= 1:
            content_score += 8
            result['comments'].append(f"📷 有图片说明（{image_count}张）")
        
        # 3. 代码文件（最高15分）
        if code_count >= 3:
            content_score += 15
            result['comments'].append(f"💻 多个代码文件（{code_count}个）")
        elif code_count >= 1:
            content_score += 10
            result['comments'].append(f"💻 有代码文件（{code_count}个）")
        
        # 4. 额外资料（视频、文档等，最高5分）
        if video_count > 0:
            content_score += 3
            result['comments'].append(f"🎬 包含视频演示")
        if doc_count > 0:
            content_score += 2
            result['comments'].append(f"📄 包含额外文档")
        
        result['content_score'] = min(content_score, 70)
        
        # 学习态度评分（30%）
        attitude_score = 0
        
        # 获取提交记录
        commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?path={actual_path}"
        commits_response = requests.get(commits_url, headers=HEADERS)
        
        if commits_response.status_code == 200:
            commits = commits_response.json()
            commit_count = len(commits)
            
            # 1. 提交频率（最高15分）
            if commit_count >= 5:
                attitude_score += 15
                result['comments'].append(f"⭐ 多次提交迭代（{commit_count}次）")
            elif commit_count >= 3:
                attitude_score += 12
                result['comments'].append(f"⭐ 多次提交（{commit_count}次）")
            elif commit_count >= 1:
                attitude_score += 8
                result['comments'].append(f"⭐ 有提交记录（{commit_count}次）")
            
            # 2. 及时性（最高15分）
            if len(commits) > 0:
                last_commit_date = commits[0]['commit']['author']['date']
                from datetime import timezone
                due_date = datetime.fromisoformat(WEEKS[week_id]['due_date']).replace(tzinfo=timezone.utc)
                submit_date = datetime.fromisoformat(last_commit_date.replace('Z', '+00:00'))
                
                days_diff = (due_date - submit_date).days
                if days_diff >= 0:
                    if days_diff >= 3:
                        attitude_score += 15
                        result['comments'].append("🎉 提前3天以上完成")
                    elif days_diff >= 1:
                        attitude_score += 12
                        result['comments'].append("🎉 提前完成")
                    else:
                        attitude_score += 10
                        result['comments'].append("✅ 按时完成")
                elif days_diff >= -3:
                    attitude_score += 5
                    result['comments'].append("⏰ 稍有延迟（3天内）")
                else:
                    result['comments'].append(f"⏰ 延迟{-days_diff}天")
        
        result['attitude_score'] = min(attitude_score, 30)
        result['details'] = {
            'readme_size': readme_size,
            'image_count': image_count,
            'code_count': code_count,
            'doc_count': doc_count,
            'video_count': video_count,
            'commit_count': commit_count if commits_response.status_code == 200 else 0
        }
        
    except Exception as e:
        result['comments'].append(f"⚠️  分析出错: {str(e)}")
    
    return result


def evaluate_student(student):
    """评估单个学生 - 总分100分"""
    github_id = student['github_id']
    print(f"\n📊 评估学生: @{github_id}")
    
    repo_url = student['repo_url']
    exists, repo_or_error = check_repo_exists(repo_url)
    
    if not exists:
        print(f"  ❌ 仓库不存在或无法访问: {repo_or_error}")
        return {
            'github_id': github_id,
            'repo_url': repo_url,
            'repo_exists': False,
            'error': repo_or_error,
            'weeks': {},
            'total_score': 0,
            'grade': 'N/A',
            'evaluation_date': datetime.now().isoformat()
        }
    
    repo_data = repo_or_error
    print(f"  ✅ 仓库存在: {repo_data.get('name', '')}")
    
    # 提取owner和repo_name
    parts = repo_url.rstrip('/').split('/')
    owner, repo_name = parts[-2], parts[-1]
    
    # 分析每周作业，按权重计算得分
    weeks_result = {}
    total_score = 0
    
    for week_id, week_info in WEEKS.items():
        print(f"  📝 分析 {week_id}: {week_info['title']}（权重{week_info['weight']}分）")
        result = analyze_week_content(owner, repo_name, week_id, week_info)
        
        # 计算该周得分：(内容分 + 态度分) * 权重 / 100
        week_raw_score = result['content_score'] + result['attitude_score']
        week_final_score = week_raw_score * week_info['weight'] / 100
        result['raw_score'] = week_raw_score
        result['final_score'] = week_final_score
        
        weeks_result[week_id] = result
        total_score += week_final_score
        
        print(f"    原始得分: {week_raw_score}/100")
        print(f"    加权得分: {week_final_score:.1f}/{week_info['weight']}")
        for comment in result['comments']:
            print(f"    {comment}")
    
    # 评级
    if total_score >= 90:
        grade = 'A+'
    elif total_score >= 85:
        grade = 'A'
    elif total_score >= 80:
        grade = 'A-'
    elif total_score >= 75:
        grade = 'B+'
    elif total_score >= 70:
        grade = 'B'
    elif total_score >= 65:
        grade = 'B-'
    elif total_score >= 60:
        grade = 'C+'
    elif total_score >= 55:
        grade = 'C'
    elif total_score >= 50:
        grade = 'C-'
    else:
        grade = 'D'
    
    print(f"\n  🎯 总分: {total_score:.1f}/100  等级: {grade}")
    
    return {
        'github_id': github_id,
        'repo_url': repo_url,
        'repo_exists': True,
        'weeks': weeks_result,
        'total_score': round(total_score, 1),
        'grade': grade,
        'evaluation_date': datetime.now().isoformat()
    }


def main():
    """主函数"""
    print("🚀 开始自动评价学生作业...")
    print(f"📊 评分制度: 总分100分（内容70% + 态度30%）")
    print(f"🔑 GitHub Token: {'已配置✅' if GITHUB_TOKEN else '未配置❌'}\n")
    
    # 加载学生名单
    students = load_students()
    if not students:
        print("❌ 没有找到学生信息")
        return
    
    print(f"📋 找到 {len(students)} 名学生\n")
    
    # 评估所有学生
    results = []
    for student in students:
        result = evaluate_student(student)
        results.append(result)
    
    # 保存结果
    output_dir = Path('students/evaluations')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    latest_file = output_dir / 'latest.json'
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump({
            'evaluation_date': datetime.now().isoformat(),
            'scoring_system': '总分100分（内容70% + 态度30%）',
            'students': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 评价完成！结果保存到: {latest_file}")
    
    # 保存历史记录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    history_file = output_dir / f'evaluation_{timestamp}.json'
    with open(latest_file, 'r', encoding='utf-8') as f:
        with open(history_file, 'w', encoding='utf-8') as f2:
            f2.write(f.read())
    
    print(f"📚 历史记录保存到: {history_file}")
    
    # 统计信息
    print("\n" + "="*60)
    print("📊 评价统计")
    print("="*60)
    
    active_students = [r for r in results if r['repo_exists']]
    total_students = len(results)
    active_count = len(active_students)
    
    if active_count > 0:
        avg_score = sum(r['total_score'] for r in active_students) / active_count
        
        print(f"总学生数: {total_students}")
        print(f"可访问仓库: {active_count}")
        print(f"平均分数: {avg_score:.1f}/100")
        
        # 分数分布
        grade_dist = {}
        for r in active_students:
            grade = r.get('grade', 'N/A')
            grade_dist[grade] = grade_dist.get(grade, 0) + 1
        
        print(f"\n📈 成绩分布:")
        for grade in ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D']:
            if grade in grade_dist:
                print(f"  {grade}: {grade_dist[grade]}人")
        
        # 前5名
        top_students = sorted(active_students, 
                            key=lambda x: x['total_score'], 
                            reverse=True)[:5]
        
        print("\n🏆 作业完成前5名:")
        for i, student in enumerate(top_students, 1):
            print(f"  {i}. @{student['github_id']} - {student['total_score']:.1f}分 ({student['grade']})")
    else:
        print("暂无可访问的学生仓库")
    
    print("\n✨ 评价流程结束\n")


if __name__ == '__main__':
    main()

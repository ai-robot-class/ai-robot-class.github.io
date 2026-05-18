#!/usr/bin/env python3
"""
学生作业自动评价脚本 v2
- 总分 100 分制（内容 70% + 态度 30%）
- 支持任意层级目录、自定义命名（中文/日期/前缀）
- 使用 Git Trees API 递归获取整个仓库
- 没有 README 时基于截图、代码等内容评分
"""

import os
import re
import json
import base64
import requests
from datetime import datetime, timezone
from pathlib import Path


def get_github_token():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        try:
            hosts = Path.home() / '.config' / 'gh' / 'hosts.yml'
            if hosts.exists():
                for line in hosts.read_text().splitlines():
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
             '.launch.py', '.sh', '.yaml', '.yml', '.cmake', '.ipynb')
DOC_EXTS = ('.pdf', '.doc', '.docx', '.txt', '.markdown')
VIDEO_EXTS = ('.mp4', '.avi', '.mov', '.mkv', '.webm')

SCREENSHOT_KEYWORDS = ['screenshot', 'capture', 'result', 'output', 'demo',
                       'show', 'preview', '截图', '结果', '运行', '效果',
                       '演示', '示例', 'final']

CN_DIGITS = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
             '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
             '十一': 11, '十二': 12, '十三': 13}


def normalize_week_id(name):
    """从单个目录名提取 week 编号，支持多种格式"""
    if not name:
        return None
    s = name.lower()

    # 1) week\d+ / week_2 / week-2 / week 2
    m = re.search(r'week[\s_\-]*?(\d+)', s)
    if m:
        return f"week{int(m.group(1))}"

    # 2) \d+week 数字在前：1week, 10week, 2_week
    m = re.search(r'(\d+)[\s_\-]*?week', s)
    if m:
        return f"week{int(m.group(1))}"

    # 3) homework\d+: homework1, homework10
    m = re.search(r'homework[\s_\-]*?(\d+)', s)
    if m:
        return f"week{int(m.group(1))}"

    # 4) hw\d+
    m = re.search(r'\bhw[\s_\-]*?(\d+)', s)
    if m:
        return f"week{int(m.group(1))}"

    # 5) w\d+
    m = re.search(r'\bw(\d+)\b', s)
    if m:
        return f"week{int(m.group(1))}"

    # 4) 第N周
    m = re.search(r'第\s*(\d+)\s*周', name)
    if m:
        return f"week{int(m.group(1))}"

    # 5) 第N章 / chapter N
    m = re.search(r'(?:第\s*(\d+)\s*章|chapter[\s_\-]*?(\d+))', s)
    if m:
        n = m.group(1) or m.group(2)
        if n:
            return f"week{int(n)}"

    # 6) 中文数字: 第一周、第十二周
    m = re.search(r'第([一二三四五六七八九十]+)周', name)
    if m and m.group(1) in CN_DIGITS:
        return f"week{CN_DIGITS[m.group(1)]}"

    return None


def load_students():
    roster_file = Path('students/roster.json')
    if not roster_file.exists():
        print("⚠️  学生名单文件不存在")
        return []

    with open(roster_file, 'r', encoding='utf-8') as f:
        repo_urls = json.load(f)

    students = []
    for url in repo_urls:
        clean = url.rstrip('/').replace('.git', '')
        parts = clean.split('/')
        if len(parts) >= 4:
            students.append({
                'github_id': parts[-2],
                'repo_url': clean,
                'repo_name': parts[-1]
            })
    return students


def fetch_repo_info(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        return True, r.json()
    return False, f"HTTP {r.status_code}: {r.json().get('message', '')}"


def fetch_pages_info(owner, repo):
    """检测仓库是否启用 GitHub Pages"""
    url = f"https://api.github.com/repos/{owner}/{repo}/pages"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        data = r.json()
        return {
            'enabled': True,
            'url': data.get('html_url') or data.get('url'),
            'status': data.get('status'),
        }
    return {'enabled': False, 'url': f"https://{owner}.github.io/{repo}/"}


def check_pages_alive(url):
    """检测 Pages URL 是否能正常返回 200，并返回 HTML 内容"""
    if not url:
        return False, None
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        if r.status_code == 200 and len(r.text) > 200:
            return True, r.text
    except Exception:
        pass
    return False, None


def audit_pages_health(pages_url, html, owner, repo):
    """检测 Pages 页面的健康度：图片加载、链接有效、样式应用等"""
    report = {
        'total_images': 0,
        'broken_images': [],
        'broken_links': [],
        'has_title': False,
        'has_style': False,
        'has_content': False,
        'word_count': 0,
        'issues': [],
        'suggestions': [],
        'score': 0,  # 0-100
    }
    if not html:
        return report

    # 标题检测
    title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
    if title_match and len(title_match.group(1).strip()) > 3:
        report['has_title'] = True
    else:
        report['issues'].append("缺少有意义的 <title> 标签")

    # 样式检测
    if '<style' in html.lower() or 'stylesheet' in html.lower() or '_config.yml' in html.lower():
        report['has_style'] = True
    else:
        report['suggestions'].append("可以加入 CSS 美化页面")

    # 主体内容检测（去掉 HTML 标签后的文字量）
    text_only = re.sub(r'<[^>]+>', ' ', html)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    report['word_count'] = len(text_only)
    if len(text_only) > 200:
        report['has_content'] = True

    # 收集首页图片
    img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    md_imgs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', html)

    # 收集首页内的子页面链接（同域，.html 或目录路径）
    sub_pages = set()
    base = pages_url.rstrip('/') + '/'
    pages_host = f"https://{owner}.github.io/{repo}/"
    for href in re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE):
        if href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
            continue
        if href.startswith('http://') or href.startswith('https://'):
            if pages_host.rstrip('/') in href and href != pages_url:
                sub_pages.add(href)
        elif href.startswith('/'):
            sub_pages.add(f"https://{owner}.github.io" + href)
        else:
            sub_pages.add(base + href)
        if len(sub_pages) >= 6:
            break

    # 抓取前 4 个子页面，收集更多图片
    sub_pages_to_check = list(sub_pages)[:4]
    image_sources = []  # [(src, from_url)]
    for src in img_tags + md_imgs:
        image_sources.append((src, pages_url))

    for sub_url in sub_pages_to_check:
        try:
            r = requests.get(sub_url, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                sub_imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', r.text, re.IGNORECASE)
                sub_md = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', r.text)
                for src in sub_imgs + sub_md:
                    image_sources.append((src, sub_url))
        except Exception:
            continue

    # 去重（基于 src+from_url）
    seen = set()
    unique_imgs = []
    for src, from_url in image_sources:
        key = (src, from_url)
        if key not in seen:
            seen.add(key)
            unique_imgs.append((src, from_url))

    report['total_images'] = len(unique_imgs)

    # 检查每张图片是否能加载（最多 30 张）
    checked = 0
    for src, from_url in unique_imgs:
        if checked >= 30:
            break
        if src.startswith('data:'):
            continue
        # 解析相对路径（基于该图片所在的页面 URL）
        if src.startswith('http://') or src.startswith('https://'):
            full = src
            if 'github.com' in src and '/avatars/' in src:
                continue
        elif src.startswith('//'):
            full = 'https:' + src
        elif src.startswith('/'):
            full = f"https://{owner}.github.io" + src
        else:
            # 相对于 from_url 的路径
            from_dir = from_url.rsplit('/', 1)[0] + '/'
            full = from_dir + src

        checked += 1
        try:
            rr = requests.head(full, timeout=6, allow_redirects=True)
            if rr.status_code >= 400:
                rr = requests.get(full, timeout=6, stream=True, allow_redirects=True)
                rr.close()
            if rr.status_code >= 400:
                report['broken_images'].append({
                    'src': src, 'resolved': full,
                    'page': from_url.replace(pages_host, '/'),
                    'status': rr.status_code
                })
        except Exception as e:
            report['broken_images'].append({
                'src': src, 'resolved': full,
                'page': from_url.replace(pages_host, '/'),
                'error': str(e)[:60]
            })

    # 构造 issues 列表
    if report['broken_images']:
        n = len(report['broken_images'])
        report['issues'].append(f"有 {n} 张图片无法加载（共检查 {checked} 张，总图数 {report['total_images']}）")
    if not report['has_content']:
        report['issues'].append(f"页面内容过少（仅 {report['word_count']} 字符）")

    # 计算健康度分数
    score = 60  # 基础分（有 Pages 就算有努力）
    if report['has_title']:
        score += 5
    if report['has_style']:
        score += 5
    if report['has_content']:
        score += 10
    if report['total_images'] > 0:
        broken_ratio = len(report['broken_images']) / max(checked, 1)
        score += int(20 * (1 - broken_ratio))
    else:
        # 没有图片不是错，给中间分
        score += 10
    report['score'] = min(score, 100)

    # 推荐建议
    if report['broken_images']:
        report['suggestions'].append(
            "图片路径错误：检查 README 中的图片相对路径，或将图片放入仓库后用相对路径引用"
        )
    if report['total_images'] == 0:
        report['suggestions'].append("添加运行截图和效果图能让作业更加生动")
    if not report['has_style']:
        report['suggestions'].append("可以选择 GitHub Pages 主题（Settings → Pages → Theme chooser）")

    return report


def fetch_repo_tree(owner, repo, branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        return data.get('tree', []), data.get('truncated', False)
    return [], False


def fetch_commits(owner, repo, per_page=100):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={per_page}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        return r.json()
    return []


def fetch_commits_for_path(owner, repo, path):
    """获取某个路径下的提交记录"""
    if not path:
        return []
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={path}&per_page=30"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        return r.json()
    return []


def fetch_file_content(owner, repo, path):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        try:
            return base64.b64decode(data.get('content', '')).decode('utf-8', errors='ignore')
        except Exception:
            return None
    return None


def group_files_by_week(tree):
    """遍历整个仓库的所有路径，按 week 分类
    支持任意层级目录（多级嵌套）和各种命名方式"""
    week_files = {wk: [] for wk in WEEKS}
    week_anchor = {wk: None for wk in WEEKS}  # 该周作业的"锚定"路径

    for item in tree:
        path = item.get('path', '')
        if not path:
            continue
        parts = path.split('/')
        for i, segment in enumerate(parts):
            wk = normalize_week_id(segment)
            if wk and wk in week_files:
                week_files[wk].append(item)
                anchor = '/'.join(parts[:i + 1])
                cur = week_anchor[wk]
                if cur is None or len(anchor) < len(cur):
                    week_anchor[wk] = anchor
                break

    return week_files, week_anchor


def find_readme_in_files(files, anchor):
    """在该 week 文件中查找最合适的 README"""
    best = None
    for f in files:
        if f.get('type') != 'blob':
            continue
        path = f['path']
        name = path.split('/')[-1].lower()
        if name == 'readme.md':
            if best is None:
                best = f
            else:
                # 优先选择更靠近 anchor 的 README
                if anchor and path.startswith(anchor):
                    parent_depth = path.count('/')
                    best_depth = best['path'].count('/')
                    if parent_depth < best_depth:
                        best = f
    return best


def analyze_screenshots(files):
    """分析截图的质量和数量"""
    total_images = 0
    meaningful_images = 0  # 有意义的截图（基于大小和文件名）
    image_in_subdir = 0    # 放在 img/screenshots 子目录的
    avg_size = 0
    sizes = []

    for f in files:
        if f.get('type') != 'blob':
            continue
        path = f['path']
        name = path.split('/')[-1].lower()
        size = f.get('size', 0)

        if not name.endswith(IMAGE_EXTS):
            continue
        total_images += 1
        sizes.append(size)

        # 大小 > 10KB 视为有内容的截图
        if size > 10240:
            meaningful_images += 1

        # 文件名包含截图相关关键词
        if any(kw in name for kw in SCREENSHOT_KEYWORDS):
            meaningful_images = max(meaningful_images, total_images)

        # 在 img/images/screenshots 等子目录中
        path_lower = path.lower()
        if any(d in path_lower for d in ['/img/', '/images/', '/screenshots/',
                                          '/screenshot/', '/截图/', '/figures/',
                                          '/figs/', '/pics/', '/photos/']):
            image_in_subdir += 1

    if sizes:
        avg_size = sum(sizes) / len(sizes)

    return {
        'total': total_images,
        'meaningful': meaningful_images,
        'in_subdir': image_in_subdir,
        'avg_size_kb': round(avg_size / 1024, 1) if avg_size else 0,
    }


def analyze_week(week_id, week_info, files, anchor, owner, repo,
                 path_commits, fallback_commits):
    """评分宽松，原则：
       - 只要提交了内容，基础分至少 50（C 等级起步）
       - README + 截图 + 代码三者俱全 → 80+
       - 全面优秀 → 95+
    """
    result = {
        'submitted': False,
        'actual_path': anchor,
        'content_score': 0,
        'attitude_score': 0,
        'details': {},
        'comments': []
    }

    if not files:
        result['comments'].append("❌ 未提交作业")
        return result

    result['submitted'] = True
    result['comments'].append(f"✅ 已提交（路径: {anchor}）")

    code_count = 0
    doc_count = 0
    video_count = 0
    readme_blob = find_readme_in_files(files, anchor)
    readme_size = readme_blob.get('size', 0) if readme_blob else 0

    for f in files:
        if f.get('type') != 'blob':
            continue
        name = f['path'].split('/')[-1].lower()
        if name.endswith(CODE_EXTS):
            code_count += 1
        elif name.endswith(DOC_EXTS):
            doc_count += 1
        elif name.endswith(VIDEO_EXTS):
            video_count += 1

    img_stats = analyze_screenshots(files)

    # ===== 内容评分（满分 70） =====
    # 1. 基础完成分：只要提交了作业 +25
    content_score = 25
    result['comments'].append("✅ 完成本周作业 (+25 基础分)")

    # 2. README 质量（最高 20 分）
    if readme_blob:
        if readme_size > 3000:
            content_score += 20
            result['comments'].append("📝 README非常详细 (+20)")
        elif readme_size > 1500:
            content_score += 17
            result['comments'].append("📝 README很详细 (+17)")
        elif readme_size > 500:
            content_score += 14
            result['comments'].append("📝 README较详细 (+14)")
        elif readme_size > 100:
            content_score += 10
            result['comments'].append("📝 README较简单 (+10)")
        else:
            content_score += 6
            result['comments'].append("📝 有简短README (+6)")

        content = fetch_file_content(owner, repo, readme_blob['path'])
        if content:
            depth = 0
            if any(k in content for k in ['问题', '思考', '难点', '错误', 'bug', '挑战']):
                depth += 2
                result['comments'].append("💡 包含问题/思考 (+2)")
            if any(k in content for k in ['总结', '心得', '收获', '反思', '体会']):
                depth += 2
                result['comments'].append("💡 包含学习总结 (+2)")
            if any(k in content for k in ['步骤', '流程', '## ', '- [x]', '- [ ]']):
                depth += 2
                result['comments'].append("💡 结构化记录 (+2)")
            if any(k in content for k in ['![', '[图', '图1', '图2', '截图', '图片']):
                depth += 2
                result['comments'].append("💡 README中引用了图片 (+2)")
            content_score += depth
    else:
        result['comments'].append("⚠️  缺少 README")

    # 3. 截图与图片（最高 18 分）—— 截图也算重要内容
    img_score = 0
    img_count = img_stats['meaningful']
    total_imgs = img_stats['total']
    if img_count >= 5 or total_imgs >= 8:
        img_score = 18
        result['comments'].append(f"📷 丰富截图（{total_imgs}张, {img_count}张有效，+18）")
    elif img_count >= 3 or total_imgs >= 5:
        img_score = 15
        result['comments'].append(f"📷 较多截图（{total_imgs}张，+15）")
    elif img_count >= 1 or total_imgs >= 2:
        img_score = 12
        result['comments'].append(f"📷 有截图（{total_imgs}张，+12）")
    elif total_imgs >= 1:
        img_score = 8
        result['comments'].append(f"📷 有图片（{total_imgs}张，+8）")

    if img_stats['in_subdir'] > 0:
        img_score = min(img_score + 2, 18)
        result['comments'].append("📁 图片组织规范")

    content_score += img_score

    # 4. 代码文件（最高 12 分）
    code_score = 0
    if code_count >= 5:
        code_score = 12
        result['comments'].append(f"💻 完整代码（{code_count}个，+12）")
    elif code_count >= 3:
        code_score = 10
        result['comments'].append(f"💻 多个代码文件（{code_count}个，+10）")
    elif code_count >= 1:
        code_score = 7
        result['comments'].append(f"💻 有代码（{code_count}个，+7）")
    content_score += code_score

    # 5. 额外资料（最高 5 分）
    if video_count > 0:
        content_score += 4
        result['comments'].append("🎬 包含视频演示 (+4)")
    if doc_count > 0:
        content_score += 2
        result['comments'].append("📄 包含额外文档 (+2)")

    result['content_score'] = min(content_score, 70)

    # ===== 态度评分（满分 30）—— 提交了就有基础分 =====
    # 1. 基础态度分：完成了作业就 +10
    attitude_score = 10
    result['comments'].append("✅ 完成作业的态度分 (+10)")

    related_commits = path_commits or []
    if not related_commits and fallback_commits:
        related_commits = [{'commit': {'author': {'date': c['commit']['author']['date']}},
                            'sha': c['sha']}
                           for c in fallback_commits[:5]]

    commit_count = len(related_commits)
    # 2. 提交频率（最高 10 分）
    if commit_count >= 5:
        attitude_score += 10
        result['comments'].append(f"⭐ 多次提交迭代（{commit_count}次，+10）")
    elif commit_count >= 3:
        attitude_score += 8
        result['comments'].append(f"⭐ 多次提交（{commit_count}次，+8）")
    elif commit_count >= 1:
        attitude_score += 6
        result['comments'].append(f"⭐ 有提交（{commit_count}次，+6）")

    # 3. 及时性（最高 10 分）—— 即使延迟也给一些分
    if related_commits:
        try:
            last_date = related_commits[0]['commit']['author']['date']
            last = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
            due = datetime.fromisoformat(week_info['due_date']).replace(tzinfo=timezone.utc)
            days_diff = (due - last).days
            if days_diff >= 7:
                attitude_score += 10
                result['comments'].append("🎉 提前一周完成 (+10)")
            elif days_diff >= 3:
                attitude_score += 9
                result['comments'].append("🎉 提前完成 (+9)")
            elif days_diff >= 0:
                attitude_score += 8
                result['comments'].append("✅ 按时完成 (+8)")
            elif days_diff >= -7:
                attitude_score += 5
                result['comments'].append(f"⏰ 稍延迟{-days_diff}天 (+5)")
            elif days_diff >= -30:
                attitude_score += 3
                result['comments'].append(f"⏰ 延迟{-days_diff}天 (+3)")
            else:
                attitude_score += 1
        except Exception:
            pass

    result['attitude_score'] = min(attitude_score, 30)
    result['details'] = {
        'readme_size': readme_size,
        'total_images': img_stats['total'],
        'meaningful_images': img_stats['meaningful'],
        'images_in_subdir': img_stats['in_subdir'],
        'code_count': code_count,
        'video_count': video_count,
        'doc_count': doc_count,
        'commit_count': commit_count,
        'total_files': sum(1 for f in files if f.get('type') == 'blob'),
    }
    return result


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
    print(f"  ✅ 仓库: {repo_info.get('name')} (分支: {default_branch})")

    # 检测 GitHub Pages
    pages_info = fetch_pages_info(owner, repo_name)
    pages_url = pages_info['url']
    pages_alive, pages_html = check_pages_alive(pages_url)
    pages_audit = None
    if pages_alive:
        pages_audit = audit_pages_health(pages_url, pages_html, owner, repo_name)
        print(f"  🌐 GitHub Pages: {pages_url} ✅ (健康度: {pages_audit['score']}/100)")
        if pages_audit['broken_images']:
            print(f"    ⚠️  {len(pages_audit['broken_images'])} 张图片加载失败")
        for issue in pages_audit['issues']:
            print(f"    ⚠️  {issue}")
    else:
        print(f"  🌐 GitHub Pages: 未启用或不可访问")

    tree, truncated = fetch_repo_tree(owner, repo_name, default_branch)
    if not tree:
        tree, truncated = fetch_repo_tree(owner, repo_name, 'master')
    if truncated:
        print("  ⚠️  仓库较大，文件树已截断")

    commits = fetch_commits(owner, repo_name, per_page=100)
    week_files, week_anchor = group_files_by_week(tree)

    # 兜底：如果一周都没识别出来，但根目录有内容（图片/代码/README）
    # 将根目录的内容按 commit 时间分配给"已结束的周次"
    matched_count = sum(1 for files in week_files.values() if files)
    if matched_count == 0 and tree:
        root_files = [f for f in tree if f.get('type') == 'blob' and '/' not in f['path']]
        if root_files:
            print(f"  ⚠️  未识别到 week 文件夹，但根目录有 {len(root_files)} 个文件，按时间分配")
            # 按文件名中的日期或 commit 顺序分配
            now = datetime.now(timezone.utc)
            past_weeks = [(wk, info) for wk, info in WEEKS.items()
                          if datetime.fromisoformat(info['due_date']).replace(tzinfo=timezone.utc) <= now]
            # 平均分给已经过去的周次
            if past_weeks:
                per_week = max(1, len(root_files) // len(past_weeks))
                for i, (wk, info) in enumerate(past_weeks):
                    start = i * per_week
                    end = (i + 1) * per_week if i < len(past_weeks) - 1 else len(root_files)
                    chunk = root_files[start:end]
                    if chunk:
                        week_files[wk] = chunk
                        week_anchor[wk] = '.'  # 根目录

    # 为每个 week 获取该路径下的真实提交
    weeks_result = {}
    weighted_sum = 0.0
    completed_weight = 0.0  # 已上课周次的权重总和
    now = datetime.now(timezone.utc)

    for week_id, week_info in WEEKS.items():
        anchor = week_anchor.get(week_id)
        files = week_files.get(week_id, [])
        path_commits = []
        if anchor:
            path_commits = fetch_commits_for_path(owner, repo_name, anchor)

        wk_result = analyze_week(week_id, week_info, files, anchor,
                                 owner, repo_name, path_commits, commits)
        raw = wk_result['content_score'] + wk_result['attitude_score']
        final = raw * week_info['weight'] / 100
        wk_result['raw_score'] = raw
        wk_result['final_score'] = round(final, 2)
        weeks_result[week_id] = wk_result

        # 判断该 week 是否已经上课（截止日期已过 或 已提交）
        due = datetime.fromisoformat(week_info['due_date']).replace(tzinfo=timezone.utc)
        is_past = due <= now
        wk_result['is_past'] = is_past
        if is_past or wk_result['submitted']:
            weighted_sum += final
            completed_weight += week_info['weight']
            mark = ""
        else:
            mark = " (未到截止日期，不计入总分)"
        print(f"  📝 {week_id} ({week_info['title']}): {raw}/100 → {final:.1f}/{week_info['weight']}{mark}")

    # 归一化总分：已上课部分按 100 分制
    if completed_weight > 0:
        total_score = weighted_sum / completed_weight * 100
    else:
        total_score = 0.0

    grade = (
        'A+' if total_score >= 95 else
        'A'  if total_score >= 88 else
        'A-' if total_score >= 82 else
        'B+' if total_score >= 76 else
        'B'  if total_score >= 70 else
        'B-' if total_score >= 65 else
        'C+' if total_score >= 60 else
        'C'  if total_score >= 55 else
        'C-' if total_score >= 50 else
        'D'  if total_score >= 35 else
        'F'
    )
    print(f"  🎯 总分: {total_score:.1f}/100  等级: {grade}（按已上课部分归一化）")

    # GitHub Pages 加分（最多 +5：基础 +3，健康度高再 +2）
    if pages_alive:
        bonus = 3
        if pages_audit and pages_audit['score'] >= 85:
            bonus = 5
        elif pages_audit and pages_audit['score'] >= 70:
            bonus = 4
        total_score = min(total_score + bonus, 100)
        grade = (
            'A+' if total_score >= 95 else
            'A'  if total_score >= 88 else
            'A-' if total_score >= 82 else
            'B+' if total_score >= 76 else
            'B'  if total_score >= 70 else
            'B-' if total_score >= 65 else
            'C+' if total_score >= 60 else
            'C'  if total_score >= 55 else
            'C-' if total_score >= 50 else
            'D'  if total_score >= 35 else
            'F'
        )

    return {
        'github_id': github_id,
        'repo_url': repo_url,
        'repo_exists': True,
        'repo_name': repo_info.get('name'),
        'repo_description': repo_info.get('description') or '',
        'stars': repo_info.get('stargazers_count', 0),
        'forks': repo_info.get('forks_count', 0),
        'default_branch': default_branch,
        'pages_url': pages_url if pages_alive else None,
        'pages_enabled': pages_alive,
        'pages_audit': pages_audit,
        'total_files': sum(1 for f in tree if f.get('type') == 'blob'),
        'total_commits': len(commits),
        'weeks': weeks_result,
        'total_score': round(total_score, 1),
        'weighted_sum': round(weighted_sum, 1),
        'completed_weight': completed_weight,
        'grade': grade,
        'evaluation_date': datetime.now().isoformat()
    }


def main():
    print("🚀 开始自动评价学生作业 (v2)...")
    print(f"📊 评分: 总分 100 分（内容 70% + 态度 30%）")
    print(f"🔑 GitHub Token: {'已配置✅' if GITHUB_TOKEN else '未配置❌'}\n")

    students = load_students()
    if not students:
        print("❌ 未找到学生")
        return

    print(f"📋 共 {len(students)} 名学生\n")

    results = []
    for student in students:
        try:
            results.append(evaluate_student(student))
        except Exception as e:
            print(f"  ⚠️  评估异常: {e}")
            results.append({
                'github_id': student['github_id'],
                'repo_url': student['repo_url'],
                'repo_exists': False,
                'error': f"评估异常: {e}",
                'weeks': {},
                'total_score': 0,
                'grade': 'N/A',
                'evaluation_date': datetime.now().isoformat()
            })

    output_dir = Path('students/evaluations')
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        'evaluation_date': datetime.now().isoformat(),
        'scoring_system': '总分 100 分（内容 70% + 态度 30%，按已上课周次归一化）',
        'weeks': {wk: {'title': info['title'], 'weight': info['weight'],
                       'due_date': info['due_date']} for wk, info in WEEKS.items()},
        'students': results
    }

    latest = output_dir / 'latest.json'
    with open(latest, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 评价完成: {latest}")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    history = output_dir / f'evaluation_{timestamp}.json'
    with open(history, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"📚 历史: {history}")

    print("\n" + "=" * 60)
    print("📊 评价统计")
    print("=" * 60)

    active = [r for r in results if r['repo_exists']]
    submitted = [r for r in active if r['total_score'] > 0]
    if active:
        avg = sum(r['total_score'] for r in active) / len(active)
        avg_sub = sum(r['total_score'] for r in submitted) / max(len(submitted), 1)
        print(f"总学生: {len(results)}  可访问: {len(active)}  有作业: {len(submitted)}")
        print(f"平均分(全部): {avg:.1f}  平均分(有作业): {avg_sub:.1f}")

        print("\n📈 成绩分布:")
        gd = {}
        for r in active:
            gd[r['grade']] = gd.get(r['grade'], 0) + 1
        for g in ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F', 'N/A']:
            if g in gd:
                print(f"  {g:3s}: {gd[g]}人")

        top = sorted(active, key=lambda x: x['total_score'], reverse=True)[:10]
        print("\n🏆 前10名:")
        for i, s in enumerate(top, 1):
            print(f"  {i:2d}. @{s['github_id']:30s}  {s['total_score']:5.1f}分  {s['grade']}")
    else:
        print("无可访问仓库")

    print("\n✨ 评价结束\n")


if __name__ == '__main__':
    main()

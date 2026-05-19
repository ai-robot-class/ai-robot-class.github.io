#!/usr/bin/env python3
"""
学生 / 教师统一评分入口

学生用法（在某个项目目录下）:
    cd p01-color-tracker
    python ../grading/run_grading.py .

教师用法（评分单个仓库）:
    python grading/run_grading.py /path/to/student/p01-color-tracker --student alice

教师用法（评分整个学生仓库的所有项目）:
    python grading/run_grading.py /path/to/student/repo --all --student alice
"""
import sys
import json
import argparse
import importlib.util
from pathlib import Path
from datetime import datetime

# 把本目录加入 sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent))


def load_project_grader(project_dir: Path):
    """加载项目专属 grader（grader.py），如果没有则用默认基类"""
    grader_file = project_dir / 'grader.py'
    if not grader_file.exists():
        # 用默认 base grader
        from grading.base_grader import BaseGrader
        return BaseGrader

    spec = importlib.util.spec_from_file_location('student_grader', grader_file)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"⚠️  加载 grader.py 失败: {e}，使用默认 grader")
        from grading.base_grader import BaseGrader
        return BaseGrader

    # 在模块里找继承 BaseGrader 的类
    from grading.base_grader import BaseGrader
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, BaseGrader) and obj is not BaseGrader:
            return obj
    return BaseGrader


def detect_project_type(project_dir: Path) -> str:
    """根据目录名识别项目"""
    name = project_dir.name
    if name.startswith('p0') or name.startswith('p1'):
        return name
    return ''


def grade_one_project(project_dir: Path, student_id: str = "unknown") -> dict:
    """评分单个项目"""
    # 检查是否在 submodule 目录中
    if project_dir.name == 'final-project':
        # 自动切换到 submodule
        submodule = project_dir / 'project-repo'
        if submodule.exists():
            print(f"🔗 检测到 final-project，自动切换到 submodule: {submodule}")
            project_dir = submodule

    GraderClass = load_project_grader(project_dir)
    grader = GraderClass(str(project_dir), student_id)
    report = grader.grade()

    from grading.base_grader import print_report
    print_report(report)

    return report


def grade_all_projects(repo_root: Path, student_id: str = "unknown") -> dict:
    """批量评分一个仓库中的所有项目"""
    reports = {}
    total_projects = 0

    for project_dir in sorted(repo_root.iterdir()):
        if not project_dir.is_dir():
            continue
        proj_type = detect_project_type(project_dir)
        if not proj_type:
            continue
        total_projects += 1
        try:
            reports[proj_type] = grade_one_project(project_dir, student_id)
        except Exception as e:
            reports[proj_type] = {
                'error': str(e),
                'project': proj_type,
                'student_id': student_id,
            }

    return {
        'student_id': student_id,
        'timestamp': datetime.now().isoformat(),
        'total_projects': total_projects,
        'projects': reports,
    }


def main():
    parser = argparse.ArgumentParser(description='AI 机器人课程项目自动评分')
    parser.add_argument('path', help='项目目录或学生仓库根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    parser.add_argument('--all', action='store_true', help='批量评分整个仓库')
    parser.add_argument('--output', help='将结果输出为 JSON 文件')
    parser.add_argument('--markdown', help='将结果输出为 Markdown 文件')
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"❌ 路径不存在: {target}")
        sys.exit(1)

    if args.all:
        result = grade_all_projects(target, args.student)
    else:
        result = grade_one_project(target, args.student)

    # 输出 JSON
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"💾 JSON 报告已保存: {args.output}")

    # 输出 Markdown
    if args.markdown:
        md = generate_markdown_report(result)
        Path(args.markdown).write_text(md)
        print(f"📝 Markdown 报告已保存: {args.markdown}")

    # 也输出到标准输出（便于 CI 解析）
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def generate_markdown_report(result: dict) -> str:
    """生成 Markdown 格式的评分报告"""
    if 'projects' in result:  # 批量模式
        lines = [f"# 📊 评分报告 - @{result['student_id']}\n"]
        lines.append(f"**生成时间**: {result['timestamp']}\n")
        lines.append(f"**评估项目数**: {result['total_projects']}\n\n")
        lines.append("## 各项目得分\n")
        lines.append("| 项目 | 总分 | 百分比 | 等级 |")
        lines.append("|------|------|--------|------|")
        for proj_name, report in result['projects'].items():
            if 'error' in report:
                lines.append(f"| {proj_name} | - | - | ❌ 评分异常 |")
            else:
                lines.append(f"| {report['project_title']} | "
                             f"{report['total_score']}/{report['total_max']} | "
                             f"{report['percentage']}% | "
                             f"{report['grade']} |")
        return '\n'.join(lines)
    else:  # 单项目
        lines = [f"# 📊 评分报告: {result['project_title']}\n"]
        lines.append(f"**学生**: @{result['student_id']}")
        lines.append(f"**评分时间**: {result['timestamp']}")
        lines.append(f"**总分**: {result['total_score']}/{result['total_max']} ({result['percentage']}%)")
        lines.append(f"**等级**: **{result['grade']}**\n")
        lines.append("## 各维度得分\n")
        lines.append("| 维度 | 得分 | 满分 | 通过 |")
        lines.append("|------|------|------|------|")
        for name, dim in result['dimensions'].items():
            passed = "✅" if dim['passed'] else "❌"
            lines.append(f"| {dim['name']} | {dim['score']:.1f} | {dim['max_score']} | {passed} |")
        lines.append("\n## 详细评分细节\n")
        for name, dim in result['dimensions'].items():
            lines.append(f"### {dim['name']}")
            for note in dim['notes']:
                lines.append(f"- {note}")
            lines.append("")
        return '\n'.join(lines)


if __name__ == '__main__':
    main()

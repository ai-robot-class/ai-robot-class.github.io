"""
智能巡检机器人 - 自动评分器

用法：
    # 学生自查
    python ../grading/run_grading.py .

    # 教师批量评分
    python ../grading/run_grading.py /path/to/student --student github_id
"""
import sys
from pathlib import Path

# 把通用 grading 框架加入 path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from grading.base_grader import BaseGrader


class PatrolRobotGrader(BaseGrader):
    PROJECT_NAME = "p07-patrol-robot"
    PROJECT_TITLE = "智能巡检机器人"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['waypoints_publisher', 'detect_and_log', 'generate_pdf_report']
    SRC_MODULE = "patrol_robot.mission"

    DIMENSIONS = {
        'structure': {'max': 10, 'desc': '项目结构完整'},
        'todos': {'max': 40, 'desc': 'TODO 函数实现正确'},
        'integration': {'max': 30, 'desc': '集成测试通过'},
        'code_quality': {'max': 10, 'desc': '代码质量'},
        'documentation': {'max': 10, 'desc': '文档与提交规范'},
    }

    def grade_integration(self):
        """集成测试：实际运行项目，检查输出"""
        item = self.items['integration']
        # 检查 waypoints 配置
        waypoints = self.project_dir / 'config' / 'waypoints.yaml'
        if waypoints.exists():
            item.score += item.max_score * 0.3
            item.add_note(f"✅ 找到 waypoints.yaml")

        # 检查报告生成（不实际跑 Nav2）
        cmd = ['python3', '-c', 'from patrol_robot import generate_pdf_report; print("OK")']
        rc, out, err = self.run_command(cmd, timeout=10)
        if rc == 0:
            item.score += item.max_score * 0.3
            item.add_note("✅ generate_pdf_report 可导入")

        # 检查是否能生成报告样本
        sample = self.project_dir / 'patrol_report.pdf'
        if sample.exists():
            item.score = min(item.score + item.max_score * 0.4, item.max_score)
            item.add_note(f"✅ 找到样本 PDF 报告 ({sample.stat().st_size} bytes)")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_dir', default='.', help='项目根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    args = parser.parse_args()

    grader = PatrolRobotGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

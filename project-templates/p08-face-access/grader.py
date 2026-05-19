"""
人脸识别系统 - 自动评分器

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


class FaceAccessGrader(BaseGrader):
    PROJECT_NAME = "p08-face-access"
    PROJECT_TITLE = "人脸识别系统"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['enroll_known_faces', 'recognize_image', 'compute_metrics']
    SRC_MODULE = "face_access.evaluate"

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
        # 检查注册库
        db = self.project_dir / 'faces.db'
        if db.exists() and db.stat().st_size > 100:
            item.score += item.max_score * 0.3
            item.add_note(f"✅ 注册库存在 ({db.stat().st_size} bytes)")

        # 检查评估报告
        report = self.project_dir / 'accuracy_report.json'
        if report.exists():
            import json as _j
            try:
                data = _j.loads(report.read_text())
                acc = data.get('accuracy', 0)
                if acc >= 0.8:
                    item.score = min(item.score + item.max_score * 0.7, item.max_score)
                    item.add_note(f"✅ 准确率 {acc:.2%}")
                elif acc >= 0.5:
                    item.score = min(item.score + item.max_score * 0.5, item.max_score)
                    item.add_note(f"⚠️  准确率 {acc:.2%}")
                else:
                    item.score = min(item.score + item.max_score * 0.2, item.max_score)
                    item.add_note(f"⚠️  准确率 {acc:.2%}")
            except Exception:
                item.add_note("⚠️  accuracy_report.json 解析失败")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_dir', default='.', help='项目根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    args = parser.parse_args()

    grader = FaceAccessGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

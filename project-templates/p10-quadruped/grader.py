"""
PyBullet 四足步态 - 自动评分器

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


class QuadrupedGrader(BaseGrader):
    PROJECT_NAME = "p10-quadruped"
    PROJECT_TITLE = "PyBullet 四足步态"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['trot_phase_generator', 'inverse_kinematics_leg', 'optimize_gait_params']
    SRC_MODULE = "quadruped.run_trot"

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
        cmd = ['python3', '-m', 'quadruped.run_trot',
               '--duration', '5', '--headless',
               '--report', '/tmp/trot_result.json']
        rc, out, err = self.run_command(cmd, timeout=180)
        if rc == 0 and Path('/tmp/trot_result.json').exists():
            import json as _j
            try:
                data = _j.loads(Path('/tmp/trot_result.json').read_text())
                distance = data.get('distance', 0)
                if distance > 1.0:
                    item.set_score(item.max_score)
                    item.add_note(f"✅ 走了 {distance:.2f}m (≥1m)")
                elif distance > 0.3:
                    item.set_score(item.max_score * 0.6)
                    item.add_note(f"⚠️  走了 {distance:.2f}m")
                elif distance > 0:
                    item.set_score(item.max_score * 0.3)
                    item.add_note(f"⚠️  仅走了 {distance:.2f}m")
                else:
                    item.add_note(f"❌ 没动: {distance:.2f}m")
            except Exception:
                item.add_note("⚠️  结果文件解析失败")
        else:
            item.add_note(f"❌ 运行失败: {err[:200]}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_dir', default='.', help='项目根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    args = parser.parse_args()

    grader = QuadrupedGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

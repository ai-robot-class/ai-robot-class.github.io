"""
PyBullet 机械臂抓取 - 自动评分器

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


class ArmGraspGrader(BaseGrader):
    PROJECT_NAME = "p09-arm-grasp"
    PROJECT_TITLE = "PyBullet 机械臂抓取"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['detect_blocks', 'inverse_kinematics', 'pick_and_place']
    SRC_MODULE = "arm_grasp.run"

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
        cmd = ['python3', '-m', 'arm_grasp.run',
               '--robot', 'kuka', '--target_color', 'red',
               '--headless', '--max_steps', '1000',
               '--report', '/tmp/grasp_result.json']
        rc, out, err = self.run_command(cmd, timeout=300)
        if rc == 0 and Path('/tmp/grasp_result.json').exists():
            import json as _j
            try:
                data = _j.loads(Path('/tmp/grasp_result.json').read_text())
                if data.get('success', False):
                    item.set_score(item.max_score)
                    item.add_note("✅ 抓取成功")
                else:
                    item.set_score(item.max_score * 0.4)
                    item.add_note(f"⚠️  仿真完成但抓取失败")
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

    grader = ArmGraspGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

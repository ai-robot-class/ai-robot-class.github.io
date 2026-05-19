"""
MOT17 多目标追踪 - 自动评分器

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


class ObjectTrackerGrader(BaseGrader):
    PROJECT_NAME = "p04-object-tracker"
    PROJECT_TITLE = "MOT17 多目标追踪"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['init_tracker', 'match_detections', 'compute_motrics']
    SRC_MODULE = "object_tracker.tracker"

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
        cmd = ['python3', '-m', 'object_tracker.run',
               '--video', 'demo/MOT17-04.mp4',
               '--gt', 'demo/MOT17-04-gt.txt',
               '--output', '/tmp/metrics.json']
        rc, out, err = self.run_command(cmd, timeout=300)
        if rc == 0 and Path('/tmp/metrics.json').exists():
            import json as _j
            try:
                metrics = _j.loads(Path('/tmp/metrics.json').read_text())
                mota = metrics.get('MOTA', 0)
                if mota >= 0.3:
                    item.set_score(item.max_score)
                    item.add_note(f"✅ MOTA={mota:.3f} (≥0.3)")
                elif mota >= 0.1:
                    item.set_score(item.max_score * 0.7)
                    item.add_note(f"⚠️  MOTA={mota:.3f} (0.1-0.3)")
                else:
                    item.set_score(item.max_score * 0.3)
                    item.add_note(f"⚠️  MOTA={mota:.3f} (<0.1)")
            except Exception:
                item.add_note("⚠️  metrics.json 格式异常")
        else:
            item.add_note(f"❌ 运行失败")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_dir', default='.', help='项目根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    args = parser.parse_args()

    grader = ObjectTrackerGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

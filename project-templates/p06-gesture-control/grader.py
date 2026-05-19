"""
视频手势识别 - 自动评分器

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


class GestureControlGrader(BaseGrader):
    PROJECT_NAME = "p06-gesture-control"
    PROJECT_TITLE = "视频手势识别"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['extract_landmarks', 'classify_gesture', 'gesture_to_twist_sequence']
    SRC_MODULE = "gesture_control.gesture_node"

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
        cmd = ['python3', '-m', 'gesture_control.run',
               '--video', 'demo/gesture_mixed.mp4',
               '--output', '/tmp/commands.csv']
        rc, out, err = self.run_command(cmd, timeout=120)
        if rc == 0 and Path('/tmp/commands.csv').exists():
            import pandas as pd
            try:
                df = pd.read_csv('/tmp/commands.csv')
                if len(df) > 0:
                    item.set_score(item.max_score)
                    item.add_note(f"✅ 识别出 {len(df)} 条手势命令")
                else:
                    item.set_score(item.max_score * 0.3)
                    item.add_note("⚠️  无识别结果")
            except Exception:
                item.add_note("⚠️  CSV 格式异常")
        else:
            item.add_note(f"❌ 运行失败: {err[:200]}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_dir', default='.', help='项目根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    args = parser.parse_args()

    grader = GestureControlGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

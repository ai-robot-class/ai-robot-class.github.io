"""
基于视频的颜色追踪 - 自动评分器

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


class ColorTrackerGrader(BaseGrader):
    PROJECT_NAME = "p01-color-tracker"
    PROJECT_TITLE = "基于视频的颜色追踪"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['detect_color', 'compute_twist', 'image_callback']
    SRC_MODULE = "color_tracker.tracker_node"

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
        # 集成测试：跑通 demo 视频，检查输出文件
        cmd = ['python3', '-m', 'color_tracker.run',
               '--video', 'demo/colored_ball.mp4',
               '--output', '/tmp/output.mp4',
               '--bag', '/tmp/cmd_vel.bag', '--quiet']
        rc, out, err = self.run_command(cmd, timeout=120)

        if rc == 0:
            output = Path('/tmp/output.mp4')
            bag = Path('/tmp/cmd_vel.bag')
            if output.exists() and output.stat().st_size > 10000:
                item.score += item.max_score * 0.6
                item.add_note(f"✅ 输出视频生成成功 ({output.stat().st_size} bytes)")
            if bag.exists():
                item.score += item.max_score * 0.4
                item.add_note("✅ ROS bag 生成成功")
        else:
            item.add_note(f"❌ 运行失败: {err[:200]}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_dir', default='.', help='项目根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    args = parser.parse_args()

    grader = ColorTrackerGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

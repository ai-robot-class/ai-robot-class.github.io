"""
语音命令解析 - 自动评分器

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


class VoiceTurtleGrader(BaseGrader):
    PROJECT_NAME = "p02-voice-turtle"
    PROJECT_TITLE = "语音命令解析"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['load_and_recognize', 'parse_command', 'execute_and_record']
    SRC_MODULE = "voice_turtle.voice_node"

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
        cmd = ['python3', '-m', 'voice_turtle.run',
               '--audio', 'demo/circle.wav',
               '--output', '/tmp/trajectory.png']
        rc, out, err = self.run_command(cmd, timeout=60)
        if rc == 0 and Path('/tmp/trajectory.png').exists():
            item.set_score(item.max_score)
            item.add_note("✅ 轨迹图生成成功")
        else:
            item.add_note(f"❌ 运行失败: {err[:200]}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_dir', default='.', help='项目根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    args = parser.parse_args()

    grader = VoiceTurtleGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

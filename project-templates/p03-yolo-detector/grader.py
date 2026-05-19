"""
KITTI 物体检测 - 自动评分器

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


class YoloDetectorGrader(BaseGrader):
    PROJECT_NAME = "p03-yolo-detector"
    PROJECT_TITLE = "KITTI 物体检测"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['detect_objects', 'publish_to_ros', 'generate_stats']
    SRC_MODULE = "yolo_detector.detector_node"

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
        cmd = ['python3', '-m', 'yolo_detector.run',
               '--video', 'demo/kitti_sample.mp4',
               '--output', '/tmp/detections.csv']
        rc, out, err = self.run_command(cmd, timeout=180)
        if rc == 0 and Path('/tmp/detections.csv').exists():
            # 检查 CSV 内容
            import pandas as pd
            try:
                df = pd.read_csv('/tmp/detections.csv')
                if len(df) > 10:
                    item.set_score(item.max_score)
                    item.add_note(f"✅ 检测出 {len(df)} 条记录")
                else:
                    item.set_score(item.max_score * 0.5)
                    item.add_note(f"⚠️  仅检测出 {len(df)} 条")
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

    grader = YoloDetectorGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

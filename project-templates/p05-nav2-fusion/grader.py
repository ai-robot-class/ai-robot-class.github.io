"""
Gazebo SLAM + Nav2 - 自动评分器

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


class Nav2FusionGrader(BaseGrader):
    PROJECT_NAME = "p05-nav2-fusion"
    PROJECT_TITLE = "Gazebo SLAM + Nav2"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = ['configure_nav_params', 'write_goal_sender', 'measure_metrics']
    SRC_MODULE = "nav2_fusion.goal_sender"

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
        # Nav2 集成测试需要长时间，这里只检查配置文件正确性
        params_file = self.project_dir / 'config' / 'nav2_params.yaml'
        if params_file.exists():
            import yaml
            try:
                content = yaml.safe_load(params_file.read_text())
                # 检查关键字段
                if 'controller_server' in str(content) and 'planner_server' in str(content):
                    item.set_score(item.max_score * 0.7)
                    item.add_note("✅ nav2_params.yaml 包含必需配置项")
                else:
                    item.set_score(item.max_score * 0.4)
                    item.add_note("⚠️  nav2_params.yaml 缺少关键配置")
            except Exception as e:
                item.add_note(f"❌ YAML 解析失败: {e}")
        else:
            item.add_note("❌ 未找到 config/nav2_params.yaml")

        # 检查 launch 文件
        launch_files = list((self.project_dir / 'src').rglob('*.launch.py'))
        if launch_files:
            item.score = min(item.score + item.max_score * 0.3, item.max_score)
            item.add_note(f"✅ 找到 {len(launch_files)} 个 launch 文件")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_dir', default='.', help='项目根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    args = parser.parse_args()

    grader = Nav2FusionGrader(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)

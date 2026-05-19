"""批量生成 10 个项目的 grader.py"""
from pathlib import Path

PROJECTS = {
    'p01-color-tracker': {
        'class': 'ColorTrackerGrader',
        'title': '基于视频的颜色追踪',
        'module': 'color_tracker.tracker_node',
        'todos': ['detect_color', 'compute_twist', 'image_callback'],
        'integration_test': '''        # 集成测试：跑通 demo 视频，检查输出文件
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
            item.add_note(f"❌ 运行失败: {err[:200]}")''',
    },
    'p02-voice-turtle': {
        'class': 'VoiceTurtleGrader',
        'title': '语音命令解析',
        'module': 'voice_turtle.voice_node',
        'todos': ['load_and_recognize', 'parse_command', 'execute_and_record'],
        'integration_test': '''        cmd = ['python3', '-m', 'voice_turtle.run',
               '--audio', 'demo/circle.wav',
               '--output', '/tmp/trajectory.png']
        rc, out, err = self.run_command(cmd, timeout=60)
        if rc == 0 and Path('/tmp/trajectory.png').exists():
            item.set_score(item.max_score)
            item.add_note("✅ 轨迹图生成成功")
        else:
            item.add_note(f"❌ 运行失败: {err[:200]}")''',
    },
    'p03-yolo-detector': {
        'class': 'YoloDetectorGrader',
        'title': 'KITTI 物体检测',
        'module': 'yolo_detector.detector_node',
        'todos': ['detect_objects', 'publish_to_ros', 'generate_stats'],
        'integration_test': '''        cmd = ['python3', '-m', 'yolo_detector.run',
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
            item.add_note(f"❌ 运行失败: {err[:200]}")''',
    },
    'p04-object-tracker': {
        'class': 'ObjectTrackerGrader',
        'title': 'MOT17 多目标追踪',
        'module': 'object_tracker.tracker',
        'todos': ['init_tracker', 'match_detections', 'compute_motrics'],
        'integration_test': '''        cmd = ['python3', '-m', 'object_tracker.run',
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
            item.add_note(f"❌ 运行失败")''',
    },
    'p05-nav2-fusion': {
        'class': 'Nav2FusionGrader',
        'title': 'Gazebo SLAM + Nav2',
        'module': 'nav2_fusion.goal_sender',
        'todos': ['configure_nav_params', 'write_goal_sender', 'measure_metrics'],
        'integration_test': '''        # Nav2 集成测试需要长时间，这里只检查配置文件正确性
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
            item.add_note(f"✅ 找到 {len(launch_files)} 个 launch 文件")''',
    },
    'p06-gesture-control': {
        'class': 'GestureControlGrader',
        'title': '视频手势识别',
        'module': 'gesture_control.gesture_node',
        'todos': ['extract_landmarks', 'classify_gesture', 'gesture_to_twist_sequence'],
        'integration_test': '''        cmd = ['python3', '-m', 'gesture_control.run',
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
            item.add_note(f"❌ 运行失败: {err[:200]}")''',
    },
    'p07-patrol-robot': {
        'class': 'PatrolRobotGrader',
        'title': '智能巡检机器人',
        'module': 'patrol_robot.mission',
        'todos': ['waypoints_publisher', 'detect_and_log', 'generate_pdf_report'],
        'integration_test': '''        # 检查 waypoints 配置
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
            item.add_note(f"✅ 找到样本 PDF 报告 ({sample.stat().st_size} bytes)")''',
    },
    'p08-face-access': {
        'class': 'FaceAccessGrader',
        'title': '人脸识别系统',
        'module': 'face_access.evaluate',
        'todos': ['enroll_known_faces', 'recognize_image', 'compute_metrics'],
        'integration_test': '''        # 检查注册库
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
                item.add_note("⚠️  accuracy_report.json 解析失败")''',
    },
    'p09-arm-grasp': {
        'class': 'ArmGraspGrader',
        'title': 'PyBullet 机械臂抓取',
        'module': 'arm_grasp.run',
        'todos': ['detect_blocks', 'inverse_kinematics', 'pick_and_place'],
        'integration_test': '''        cmd = ['python3', '-m', 'arm_grasp.run',
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
            item.add_note(f"❌ 运行失败: {err[:200]}")''',
    },
    'p10-quadruped': {
        'class': 'QuadrupedGrader',
        'title': 'PyBullet 四足步态',
        'module': 'quadruped.run_trot',
        'todos': ['trot_phase_generator', 'inverse_kinematics_leg', 'optimize_gait_params'],
        'integration_test': '''        cmd = ['python3', '-m', 'quadruped.run_trot',
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
            item.add_note(f"❌ 运行失败: {err[:200]}")''',
    },
}


GRADER_TEMPLATE = '''"""
{title} - 自动评分器

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


class {class_name}(BaseGrader):
    PROJECT_NAME = "{project_name}"
    PROJECT_TITLE = "{title}"

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = {todos}
    SRC_MODULE = "{module}"

    DIMENSIONS = {{
        'structure': {{'max': 10, 'desc': '项目结构完整'}},
        'todos': {{'max': 40, 'desc': 'TODO 函数实现正确'}},
        'integration': {{'max': 30, 'desc': '集成测试通过'}},
        'code_quality': {{'max': 10, 'desc': '代码质量'}},
        'documentation': {{'max': 10, 'desc': '文档与提交规范'}},
    }}

    def grade_integration(self):
        """集成测试：实际运行项目，检查输出"""
        item = self.items['integration']
{integration_test}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_dir', default='.', help='项目根目录')
    parser.add_argument('--student', default='unknown', help='学生 GitHub ID')
    args = parser.parse_args()

    grader = {class_name}(args.project_dir, args.student)
    report = grader.grade()
    from grading.base_grader import print_report
    print_report(report)
'''


def main():
    base = Path(__file__).resolve().parent.parent
    for name, cfg in PROJECTS.items():
        proj_dir = base / name
        if not proj_dir.exists():
            print(f"⚠️  {name} 目录不存在，跳过")
            continue
        grader_file = proj_dir / 'grader.py'
        content = GRADER_TEMPLATE.format(
            project_name=name,
            title=cfg['title'],
            class_name=cfg['class'],
            module=cfg['module'],
            todos=cfg['todos'],
            integration_test=cfg['integration_test'],
        )
        grader_file.write_text(content)
        print(f"✅ {name}/grader.py")


if __name__ == '__main__':
    main()

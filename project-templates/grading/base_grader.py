"""
通用自动评分基类
所有项目的 grader.py 都继承这个基类，提供统一的评分接口
"""
import os
import sys
import json
import time
import subprocess
import importlib.util
import inspect
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime


class GradeItem:
    """单个评分项"""
    def __init__(self, name: str, max_score: float, weight: float = 1.0):
        self.name = name
        self.max_score = max_score
        self.weight = weight
        self.score = 0.0
        self.passed = False
        self.notes = []
        self.error = None

    def add_note(self, note: str):
        self.notes.append(note)

    def set_score(self, score: float, passed: bool = None):
        self.score = min(max(score, 0), self.max_score)
        self.passed = passed if passed is not None else (self.score >= self.max_score * 0.6)

    def to_dict(self):
        return {
            'name': self.name,
            'score': round(self.score, 2),
            'max_score': self.max_score,
            'passed': self.passed,
            'notes': self.notes,
            'error': self.error,
        }


class BaseGrader:
    """评分基类 - 所有项目的评分器都继承这个"""
    PROJECT_NAME = "base"
    PROJECT_TITLE = "Base Project"

    # 评分维度（每个项目可以重写）
    DIMENSIONS = {
        'structure': {'max': 10, 'desc': '项目结构完整'},
        'todos': {'max': 40, 'desc': 'TODO 函数实现正确'},
        'integration': {'max': 30, 'desc': '集成测试通过'},
        'code_quality': {'max': 10, 'desc': '代码质量'},
        'documentation': {'max': 10, 'desc': '文档与提交规范'},
    }

    REQUIRED_FILES = ['README.md', 'Dockerfile', 'docker-compose.yml']
    REQUIRED_TODOS = []  # 学生需要实现的 TODO 函数名列表
    SRC_MODULE = ""  # 主模块路径，如 'color_tracker.tracker_node'

    def __init__(self, project_dir: str, student_id: str = "unknown"):
        self.project_dir = Path(project_dir).resolve()
        self.student_id = student_id
        self.items: dict[str, GradeItem] = {}
        self.start_time = datetime.now()

        # 为每个维度创建评分项
        for dim, info in self.DIMENSIONS.items():
            self.items[dim] = GradeItem(info['desc'], info['max'])

    # ===== 各维度评分函数（子类可以重写） =====

    def grade_structure(self):
        """评分维度 1：项目结构"""
        item = self.items['structure']
        missing = []
        for f in self.REQUIRED_FILES:
            if not (self.project_dir / f).exists():
                missing.append(f)
                item.add_note(f"❌ 缺少 {f}")
            else:
                item.add_note(f"✅ {f}")
        if not missing:
            item.set_score(item.max_score)
            item.add_note(f"🎉 全部必需文件齐全")
        else:
            ratio = (len(self.REQUIRED_FILES) - len(missing)) / len(self.REQUIRED_FILES)
            item.set_score(item.max_score * ratio)

    def grade_todos(self):
        """评分维度 2：TODO 函数实现"""
        item = self.items['todos']
        if not self.REQUIRED_TODOS or not self.SRC_MODULE:
            item.set_score(item.max_score)
            item.add_note("⚠️  未配置 TODO 检查，默认满分")
            return

        # 尝试加载模块
        module = self._import_student_module()
        if module is None:
            item.error = "无法加载学生代码模块"
            item.add_note(f"❌ 无法 import {self.SRC_MODULE}")
            return

        per_todo_score = item.max_score / len(self.REQUIRED_TODOS)
        total = 0
        for todo_name in self.REQUIRED_TODOS:
            result = self._check_todo_implemented(module, todo_name)
            if result['implemented']:
                total += per_todo_score
                item.add_note(f"✅ TODO `{todo_name}` 已实现")
            else:
                item.add_note(f"❌ TODO `{todo_name}` 未实现: {result['reason']}")
        item.set_score(total)

    def grade_integration(self):
        """评分维度 3：集成测试 - 子类必须重写"""
        item = self.items['integration']
        item.add_note("⚠️  基类没有集成测试，子类需重写")
        item.set_score(0)

    def grade_code_quality(self):
        """评分维度 4：代码质量（用 ruff 检查）"""
        item = self.items['code_quality']
        try:
            result = subprocess.run(
                ['ruff', 'check', '--exit-zero', '--quiet', 'src/'],
                cwd=self.project_dir, capture_output=True, text=True, timeout=30
            )
            output = result.stdout + result.stderr
            error_count = output.count('\n') if output.strip() else 0

            if error_count == 0:
                item.set_score(item.max_score)
                item.add_note(f"✅ 无 lint 警告")
            elif error_count <= 5:
                item.set_score(item.max_score * 0.8)
                item.add_note(f"⚠️  {error_count} 个 lint 警告（轻微）")
            elif error_count <= 20:
                item.set_score(item.max_score * 0.5)
                item.add_note(f"⚠️  {error_count} 个 lint 警告（较多）")
            else:
                item.set_score(item.max_score * 0.2)
                item.add_note(f"❌ {error_count} 个 lint 警告（过多）")
        except FileNotFoundError:
            item.set_score(item.max_score * 0.6)
            item.add_note("⚠️  ruff 未安装，跳过代码质量检查")
        except subprocess.TimeoutExpired:
            item.set_score(item.max_score * 0.5)
            item.add_note("⚠️  代码质量检查超时")

    def grade_documentation(self):
        """评分维度 5：文档与提交（含个人贡献检测）"""
        item = self.items['documentation']
        score = 0

        # 检查 README
        readme = self.project_dir / 'README.md'
        if readme.exists() and readme.stat().st_size > 500:
            score += 3
            item.add_note(f"✅ README 内容充实 ({readme.stat().st_size} bytes)")
        else:
            item.add_note(f"⚠️  README 过简")

        # 检查 git commit 数量
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '--all'],
                cwd=self.project_dir, capture_output=True, text=True, timeout=10
            )
            commits = len(result.stdout.strip().splitlines()) if result.returncode == 0 else 0
            if commits >= 5:
                score += 2
                item.add_note(f"✅ Git 提交 {commits} 次（≥5 次）")
            elif commits >= 2:
                score += 1
                item.add_note(f"⚠️  Git 提交 {commits} 次（建议 ≥5 次）")
            else:
                item.add_note(f"❌ Git 提交过少 ({commits} 次)")

            # 检测个人贡献（如果指定了 student_id）
            if self.student_id and self.student_id != "unknown":
                my_result = subprocess.run(
                    ['git', 'log', f'--author={self.student_id}', '--oneline', '--all'],
                    cwd=self.project_dir, capture_output=True, text=True, timeout=10
                )
                my_commits = len(my_result.stdout.strip().splitlines()) if my_result.returncode == 0 else 0
                if my_commits > 0:
                    ratio = my_commits / max(commits, 1)
                    score += 2
                    item.add_note(f"✅ 个人提交 {my_commits}/{commits} ({ratio:.0%})")
                    self._my_commits = my_commits
                    self._team_commits = commits
                else:
                    item.add_note(f"⚠️  未检测到 @{self.student_id} 的提交（多人项目请确认 GitHub 邮箱）")
        except Exception:
            pass

        # 检查演示视频/输出
        outputs = list(self.project_dir.glob('output.*')) + list(self.project_dir.glob('*.mp4')) \
                + list(self.project_dir.glob('demo*.gif'))
        if outputs:
            score += 3
            item.add_note(f"✅ 提交了演示输出 ({outputs[0].name})")
        else:
            item.add_note(f"⚠️  未发现演示视频/输出")

        item.set_score(min(score, item.max_score))

    # ===== 辅助函数 =====

    def _import_student_module(self):
        """加载学生代码模块"""
        try:
            # 把 src 加入 sys.path
            src_dir = self.project_dir / 'src'
            if not src_dir.exists():
                return None
            sys.path.insert(0, str(src_dir))

            # 找到模块文件
            module_path = src_dir
            for part in self.SRC_MODULE.split('.'):
                module_path = module_path / part
            py_path = module_path.with_suffix('.py')
            if not py_path.exists():
                # 尝试 package/__init__.py
                init_path = module_path / '__init__.py'
                if init_path.exists():
                    py_path = init_path

            if not py_path.exists():
                return None

            spec = importlib.util.spec_from_file_location(self.SRC_MODULE, py_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"  ⚠️  加载模块失败: {e}", file=sys.stderr)
            return None
        finally:
            if str(self.project_dir / 'src') in sys.path:
                sys.path.remove(str(self.project_dir / 'src'))

    def _check_todo_implemented(self, module, todo_name) -> dict:
        """检查某个 TODO 函数是否已实现（不能只是 pass 或 NotImplementedError）"""
        # 在模块中找到函数（可能在类中）
        target = None
        for name, obj in inspect.getmembers(module):
            if name == todo_name and callable(obj):
                target = obj
                break
            if inspect.isclass(obj):
                method = getattr(obj, todo_name, None)
                if method and callable(method):
                    target = method
                    break

        if target is None:
            return {'implemented': False, 'reason': '函数未找到'}

        try:
            src = inspect.getsource(target)
            # 函数体必须超过 3 行（粗略）且不能只是 pass 或 raise NotImplementedError
            body_lines = [l.strip() for l in src.splitlines()[1:] if l.strip() and not l.strip().startswith('#')]
            if len(body_lines) < 2:
                return {'implemented': False, 'reason': '函数体过短'}
            if all(l in ('pass', 'return', '...') or 'NotImplementedError' in l or 'raise' in l for l in body_lines):
                return {'implemented': False, 'reason': '只有 pass / raise'}
            return {'implemented': True, 'reason': 'OK'}
        except (OSError, TypeError):
            return {'implemented': False, 'reason': '无法读取源码'}

    def run_command(self, cmd: list, timeout: int = 60) -> tuple[int, str, str]:
        """执行命令并返回 (returncode, stdout, stderr)"""
        try:
            result = subprocess.run(
                cmd, cwd=self.project_dir, capture_output=True,
                text=True, timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, '', f'TIMEOUT after {timeout}s'
        except FileNotFoundError as e:
            return -2, '', str(e)

    # ===== 主入口 =====

    def grade(self) -> dict:
        """运行所有评分维度"""
        print(f"\n{'='*60}")
        print(f"📊 评分: {self.PROJECT_TITLE}")
        print(f"   学生: {self.student_id}")
        print(f"   目录: {self.project_dir}")
        print(f"{'='*60}\n")

        for dim_name in self.DIMENSIONS:
            method = getattr(self, f'grade_{dim_name}', None)
            if method:
                print(f"▶ 评估维度 [{dim_name}]...")
                try:
                    method()
                except Exception as e:
                    self.items[dim_name].error = str(e)
                    self.items[dim_name].add_note(f"❌ 评分异常: {e}")
                item = self.items[dim_name]
                print(f"   得分: {item.score:.1f}/{item.max_score}")
                for note in item.notes[:3]:
                    print(f"   {note}")

        return self.generate_report()

    def generate_report(self) -> dict:
        """生成评分报告（JSON）"""
        total_score = sum(it.score for it in self.items.values())
        total_max = sum(it.max_score for it in self.items.values())

        if total_score >= 90:
            grade = 'A+'
        elif total_score >= 85:
            grade = 'A'
        elif total_score >= 80:
            grade = 'A-'
        elif total_score >= 75:
            grade = 'B+'
        elif total_score >= 70:
            grade = 'B'
        elif total_score >= 65:
            grade = 'B-'
        elif total_score >= 60:
            grade = 'C+'
        elif total_score >= 55:
            grade = 'C'
        elif total_score >= 50:
            grade = 'C-'
        else:
            grade = 'D' if total_score >= 35 else 'F'

        return {
            'project': self.PROJECT_NAME,
            'project_title': self.PROJECT_TITLE,
            'student_id': self.student_id,
            'timestamp': self.start_time.isoformat(),
            'duration_sec': (datetime.now() - self.start_time).total_seconds(),
            'total_score': round(total_score, 1),
            'total_max': total_max,
            'percentage': round(total_score / total_max * 100, 1),
            'grade': grade,
            'dimensions': {k: v.to_dict() for k, v in self.items.items()},
        }


def print_report(report: dict):
    """美化打印评分报告到终端"""
    print(f"\n{'='*60}")
    print(f"📋 评分报告: {report['project_title']}")
    print(f"{'='*60}")
    print(f"  学生: {report['student_id']}")
    print(f"  总分: {report['total_score']}/{report['total_max']}  ({report['percentage']}%)")
    print(f"  等级: {report['grade']}")
    print(f"  耗时: {report['duration_sec']:.1f} 秒")
    print(f"\n  各维度得分:")
    for dim_name, dim in report['dimensions'].items():
        passed = "✅" if dim['passed'] else "❌"
        print(f"    {passed} {dim['name']:30s} {dim['score']:5.1f}/{dim['max_score']}")
        for note in dim['notes'][:5]:
            print(f"        {note}")
    print(f"{'='*60}\n")

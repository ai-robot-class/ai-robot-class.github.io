#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""学生作业自动评价入口（规则 + DeepSeek AI）。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from grading.config import evaluation_should_run, load_dotenv  # noqa: E402
from grading.evaluator import run_evaluation  # noqa: E402


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="AI 机器人课程学生作业自动评价")
    parser.add_argument("--no-ai", action="store_true", help="仅使用规则评分，不调用 DeepSeek")
    parser.add_argument("--limit", type=int, default=0, help="仅评价前 N 名学生（调试用）")
    parser.add_argument("--skip-report", action="store_true", help="不自动生成展示页面")
    args = parser.parse_args()

    if not evaluation_should_run():
        print("⏰ 已超过评价截止日期，跳过运行")
        return 0

    limit = args.limit or None
    run_evaluation(use_ai=not args.no_ai, limit=limit)

    if not args.skip_report:
        report_script = ROOT / "scripts" / "generate_report.py"
        if report_script.exists():
            subprocess.run([sys.executable, str(report_script)], check=False, cwd=ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

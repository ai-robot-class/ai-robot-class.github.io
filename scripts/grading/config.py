from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

WEEKS = {
    "week2": {"title": "ROS2环境配置", "weight": 5, "due_date": "2026-03-15"},
    "week3": {"title": "GitHub与命令行", "weight": 5, "due_date": "2026-03-22"},
    "week4": {"title": "Python仿真", "weight": 8, "due_date": "2026-03-29"},
    "week5": {"title": "机器人运动学", "weight": 8, "due_date": "2026-04-05"},
    "week6": {"title": "KITTI实验", "weight": 8, "due_date": "2026-04-12"},
    "week7": {"title": "Markdown整理", "weight": 5, "due_date": "2026-04-19"},
    "week8": {"title": "Docker容器", "weight": 8, "due_date": "2026-04-26"},
    "week9": {"title": "数学基础", "weight": 8, "due_date": "2026-05-03"},
    "week10": {"title": "Docker与OpenCV", "weight": 10, "due_date": "2026-05-10"},
    "week11": {"title": "Docker进阶与Pages", "weight": 10, "due_date": "2026-05-17"},
    "week12": {"title": "视觉与语音", "weight": 10, "due_date": "2026-05-24"},
    "week14": {"title": "小组项目（手机遥控迷宫）", "weight": 15, "due_date": "2026-06-22"},
}

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp")
CODE_EXTS = (
    ".py", ".cpp", ".c", ".h", ".hpp", ".java", ".js", ".ts",
    ".launch.py", ".sh", ".yaml", ".yml", ".cmake", ".ipynb",
)
DOC_EXTS = (".pdf", ".doc", ".docx", ".txt", ".markdown")
VIDEO_EXTS = (".mp4", ".avi", ".mov", ".mkv", ".webm")

SCREENSHOT_KEYWORDS = [
    "screenshot", "capture", "result", "output", "demo", "show", "preview",
    "截图", "结果", "运行", "效果", "演示", "示例", "final",
]

DEEPSEEK_API_URL = os.environ.get(
    "DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions"
)
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
EVALUATION_END_DATE = os.environ.get("EVALUATION_END_DATE") or "2026-07-31"


def load_dotenv() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_deepseek_api_key() -> str | None:
    load_dotenv()
    return os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")


def evaluation_should_run(today: datetime | None = None) -> bool:
    today = today or datetime.now()
    end = datetime.strptime(EVALUATION_END_DATE, "%Y-%m-%d").date()
    return today.date() <= end


def ai_scoring_enabled() -> bool:
    if os.environ.get("DISABLE_AI_SCORING", "").lower() in {"1", "true", "yes"}:
        return False
    return bool(get_deepseek_api_key())

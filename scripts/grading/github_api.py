from __future__ import annotations

import base64
import os
import time
from pathlib import Path

import requests

from .config import ROOT


def get_github_token() -> str | None:
    for key in ("GITHUB_TOKEN", "GH_API_TOKEN", "GH_TOKEN"):
        token = os.environ.get(key)
        if token:
            return token
    try:
        hosts = Path.home() / ".config" / "gh" / "hosts.yml"
        if hosts.exists():
            for line in hosts.read_text(encoding="utf-8").splitlines():
                if "oauth_token" in line:
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return None


def require_github_token() -> str:
    """无 Token 时直接退出，提示配置或充值。"""
    token = get_github_token()
    if token:
        return token
    in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    hint = (
        "GitHub Actions 会自动注入 GITHUB_TOKEN，若仍缺失请检查 workflow permissions。"
        if in_ci
        else "本地请在项目根目录 .env 中设置 GITHUB_TOKEN=..."
    )
    print(
        "❌ 未检测到 GitHub Token，无法调用 GitHub API 评价学生仓库。\n"
        f"{hint}\n"
        "若 Token 配额已用尽，请更换或充值后重试。"
    )
    raise SystemExit(1)


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: int = 30):
        self.token = token or require_github_token()
        self.timeout = timeout
        self.session = requests.Session()
        if self.token:
            self.session.headers["Authorization"] = f"token {self.token}"
        self.session.headers.setdefault("Accept", "application/vnd.github+json")

    def _request(self, method: str, url: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        last_error = None
        for attempt in range(4):
            try:
                resp = self.session.request(method, url, **kwargs)
                if resp.status_code in {403, 429} and attempt < 3:
                    try:
                        msg = resp.json().get("message", "")
                    except ValueError:
                        msg = resp.text[:120]
                    if resp.status_code == 429 or "rate limit" in msg.lower():
                        if attempt == 2:
                            print(
                                "\n❌ GitHub API 配额已用尽或触发限流。"
                                "请更换或充值 GITHUB_TOKEN 后重试。"
                            )
                            raise SystemExit(1)
                    elif resp.status_code == 403 and "rate limit" not in msg.lower():
                        return resp
                    wait = min(60, 2 ** attempt * 5)
                    reset = resp.headers.get("X-RateLimit-Reset")
                    if reset and reset.isdigit():
                        wait = max(wait, int(reset) - int(time.time()) + 1)
                    time.sleep(max(wait, 1))
                    continue
                return resp
            except requests.RequestException as exc:
                last_error = exc
                if attempt < 3:
                    time.sleep(2 ** attempt)
        if last_error:
            raise last_error
        raise RuntimeError(f"GitHub request failed: {url}")

    def fetch_repo_info(self, owner: str, repo: str):
        resp = self._request("GET", f"https://api.github.com/repos/{owner}/{repo}")
        if resp.status_code == 200:
            return True, resp.json()
        try:
            message = resp.json().get("message", resp.text[:200])
        except ValueError:
            message = resp.text[:200]
        return False, f"HTTP {resp.status_code}: {message}"

    def fetch_pages_info(self, owner: str, repo: str):
        resp = self._request("GET", f"https://api.github.com/repos/{owner}/{repo}/pages")
        if resp.status_code == 200:
            data = resp.json()
            return {
                "enabled": True,
                "url": data.get("html_url") or data.get("url"),
                "status": data.get("status"),
            }
        return {"enabled": False, "url": f"https://{owner}.github.io/{repo}/"}

    def fetch_repo_tree(self, owner: str, repo: str, branch: str):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        resp = self._request("GET", url)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("tree", []), data.get("truncated", False)
        return [], False

    def fetch_commits(self, owner: str, repo: str, per_page: int = 100):
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={per_page}"
        resp = self._request("GET", url)
        return resp.json() if resp.status_code == 200 else []

    def fetch_commits_for_path(self, owner: str, repo: str, path: str):
        if not path:
            return []
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/commits"
            f"?path={path}&per_page=30"
        )
        resp = self._request("GET", url)
        return resp.json() if resp.status_code == 200 else []

    def fetch_file_content(self, owner: str, repo: str, path: str):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        resp = self._request("GET", url)
        if resp.status_code != 200:
            return None
        data = resp.json()
        try:
            return base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
        except (ValueError, TypeError):
            return None


def load_students() -> list[dict]:
    roster_file = ROOT / "students" / "roster.json"
    if not roster_file.exists():
        print("⚠️  学生名单文件不存在")
        return []

    with open(roster_file, encoding="utf-8") as f:
        repo_urls = __import__("json").load(f)

    students = []
    for url in repo_urls:
        clean = url.rstrip("/").replace(".git", "")
        parts = clean.split("/")
        if len(parts) >= 2:
            students.append(
                {
                    "github_id": parts[-2],
                    "repo_url": clean,
                    "repo_name": parts[-1],
                }
            )
    return students

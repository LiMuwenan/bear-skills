#!/usr/bin/env python3
"""conversation-archive: 会话归档文件管理与索引重建。

用法:
    python archive.py open [--topic TEXT] [--session-id ID] [--new-session]
    python archive.py index
    python archive.py status
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_DIR = Path("docs") / "agent-log"
STATE_NAME = ".current-session.json"
TEMPLATE_REL = Path("templates") / "session.md"


def repo_root() -> Path:
    """优先使用 git 仓库根目录，否则退回当前目录。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except Exception:
        return Path.cwd()


def sanitize(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return cleaned.strip("-") or "session"


def make_session_id(explicit: str | None) -> str:
    if explicit:
        return sanitize(explicit)
    for key in ("TRAE_SESSION_ID", "CLAUDE_SESSION_ID", "CI_SESSION_ID"):
        value = os.environ.get(key)
        if value:
            return sanitize(value)
    return datetime.now().strftime("%H%M%S") + "-" + secrets.token_hex(2)


def load_state(log_dir: Path) -> dict | None:
    path = log_dir / STATE_NAME
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_state(log_dir: Path, state: dict) -> None:
    (log_dir / STATE_NAME).write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def render_template(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def cmd_open(args: argparse.Namespace) -> int:
    root = repo_root()
    log_dir = root / DEFAULT_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    if not args.new_session:
        state = load_state(log_dir)
        if state:
            bound = root / state["file"]
            if bound.exists():
                print(bound.as_posix())
                return 0

    session_id = make_session_id(args.session_id)
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    rel = (DEFAULT_DIR / f"{date}-{session_id}.md").as_posix()
    target = root / rel

    if not target.exists():
        template_path = Path(__file__).resolve().parent.parent / TEMPLATE_REL
        content = render_template(
            template_path.read_text(encoding="utf-8"),
            {
                "DATE": date,
                "SESSION_ID": session_id,
                "TOPIC": args.topic or "（待补充）",
                "STARTED_AT": now.strftime("%Y-%m-%d %H:%M"),
                "LAST_UPDATED": now.strftime("%Y-%m-%d %H:%M"),
            },
        )
        target.write_text(content, encoding="utf-8")

    save_state(
        log_dir,
        {
            "session_id": session_id,
            "file": rel,
            "created_at": now.isoformat(timespec="seconds"),
        },
    )
    print(target.as_posix())
    return 0


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    meta: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not key or key.startswith("#"):
            continue
        meta[key] = value.split(" #", 1)[0].strip()
    return meta


def cmd_index(_: argparse.Namespace) -> int:
    root = repo_root()
    log_dir = root / DEFAULT_DIR
    if not log_dir.exists():
        print("未找到 docs/agent-log/，尚未产生任何归档。", file=sys.stderr)
        return 1

    rows: list[tuple[str, str, str, str, str]] = []
    for path in log_dir.glob("*.md"):
        if path.name == "INDEX.md":
            continue
        meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        rows.append(
            (
                meta.get("date", ""),
                meta.get("topic", "（未填写）"),
                meta.get("session_id", ""),
                meta.get("status", "active"),
                path.name,
            )
        )

    rows.sort(key=lambda row: (row[0], row[1]), reverse=True)

    lines = [
        "# Agent 对话归档索引",
        "",
        "| 日期 | 主题 | 会话 | 状态 | 文件 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for date, topic, session_id, status, name in rows:
        lines.append(f"| {date} | {topic} | {session_id} | {status} | [链接](./{name}) |")
    lines.append("")
    lines.append("<!-- 由 scripts/archive.py index 自动生成，请勿手工编辑 -->")

    (log_dir / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"已更新索引：{(DEFAULT_DIR / 'INDEX.md').as_posix()}（{len(rows)} 条）")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    root = repo_root()
    state = load_state(root / DEFAULT_DIR)
    if not state:
        print("当前无会话归档绑定")
        return 0
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="archive.py",
        description="conversation-archive 归档文件管理",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    open_parser = sub.add_parser("open", help="取得或创建当前会话的归档文件")
    open_parser.add_argument("--topic", default=None, help="会话主题")
    open_parser.add_argument("--session-id", default=None, help="显式指定会话标识")
    open_parser.add_argument(
        "--new-session",
        action="store_true",
        help="强制开始新会话文件，不复用已有绑定",
    )
    open_parser.set_defaults(func=cmd_open)

    index_parser = sub.add_parser("index", help="重建 INDEX.md")
    index_parser.set_defaults(func=cmd_index)

    status_parser = sub.add_parser("status", help="查看当前会话绑定")
    status_parser.set_defaults(func=cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

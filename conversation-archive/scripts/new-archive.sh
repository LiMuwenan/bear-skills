#!/usr/bin/env bash
set -euo pipefail

TOPIC="${1:-}"
SLUG="${2:-}"

if [ -z "$TOPIC" ]; then
  echo "用法: new-archive.sh \"<主题>\" [slug]" >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DIR="$ROOT/docs/agent-log"
TEMPLATE="$(dirname "$0")/../templates/session.md"
DATE="$(date +%F)"
TS="$(date +%H:%M)"

if [ -z "$SLUG" ]; then
  SLUG="$(printf '%s' "$TOPIC" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
  [ -z "$SLUG" ] && SLUG="session"
fi

mkdir -p "$DIR"
FILE="$DIR/${DATE}-${SLUG}.md"

if [ -e "$FILE" ]; then
  echo "已存在: $FILE"
  echo "请改用 append 模式追加到该文件。"
  exit 2
fi

sed -e "s|{{DATE}}|$DATE|g" \
  -e "s|{{TOPIC}}|$TOPIC|g" \
  -e "s|{{MODE}}|snapshot|g" \
  -e "s|{{AGENT_NAME_AND_MODEL}}|unknown|g" \
  "$TEMPLATE" > "$FILE"

INDEX="$DIR/INDEX.md"
if [ ! -f "$INDEX" ]; then
  printf '# Agent 对话归档索引\n\n| 日期 | 主题 | 模式 | 决策 | 需求变更 | 待办 | 状态 | 文件 |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n' > "$INDEX"
fi

echo "已创建: $FILE"
echo "创建时间: $DATE $TS"
echo "下一步: 填充内容并更新 $INDEX"

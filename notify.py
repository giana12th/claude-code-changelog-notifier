#!/usr/bin/env python3
"""
Discord Webhook poster for Claude Code Routines.

Usage:
  python -X utf8 notify.py <<'EOF'
  message text (Markdown supported)
  EOF

  python -X utf8 notify.py --dry-run <<'EOF'
  message text
  EOF

Environment:
  DISCORD_WEBHOOK_URL  (required unless --dry-run)
"""

import json
import os
import sys
import urllib.error
import urllib.request

DISCORD_LIMIT = 2000


def split_message(text: str, limit: int = DISCORD_LIMIT) -> list[str]:
    """2000字制限を超える場合、改行位置で分割して複数チャンクに分ける。"""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        split_at = text.rfind('\n', 0, limit)
        if split_at <= 0:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip('\n')
    return chunks


def build_payload(message: str) -> dict:
    return {"content": message}


def post(webhook_url: str, payload: dict) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Claude-Code-Discord/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status not in (200, 204):
                raise RuntimeError(f"Discord HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Discord error {e.code}: {body}")


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry-run"]

    if args:
        message = args[0]
    else:
        message = sys.stdin.read().strip()

    if not message:
        print("Error: no message provided (pass as arg or stdin)", file=sys.stderr)
        sys.exit(1)

    chunks = split_message(message)

    if dry_run:
        for i, chunk in enumerate(chunks, 1):
            print(f"--- chunk {i}/{len(chunks)} ---")
            print(json.dumps(build_payload(chunk), ensure_ascii=False, indent=2))
        return

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL is not set", file=sys.stderr)
        sys.exit(1)

    try:
        for chunk in chunks:
            post(webhook_url, build_payload(chunk))
    except RuntimeError as e:
        print(f"投稿に失敗しました。本セッションは終了してください。: {e}", file=sys.stderr)
        sys.exit(0)

    print(f"Sent to Discord ({len(chunks)} message(s))")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
superhuman-draft — wrapper around superhuman-cli that correctly handles attachments.

The superhuman-cli binary uses the wrong token for attachment uploads (Google OAuth
instead of the Superhuman JWT), so attachments silently fail. This script:
  1. Creates the draft via the binary (with --attach flags stripped)
  2. Uploads each attachment correctly using the Superhuman JWT

Usage:
  superhuman-draft draft create --account EMAIL --to EMAIL --subject "..." --body "..." [--attach /path]
"""

import sys
import os
import re
import json
import base64
import subprocess
import uuid
import time
import mimetypes
import urllib.request
import urllib.error

SUPERHUMAN_BACKEND = "https://mail.superhuman.com/~backend"
TOKEN_FILE = os.path.expanduser("~/.config/superhuman-cli/tokens.json")
BINARY = os.path.expanduser("~/.bun/bin/superhuman")


def strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def load_tokens(account: str) -> dict:
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    accounts = data.get("accounts", {})
    if account not in accounts:
        print(f"✗ Account '{account}' not found. Available: {list(accounts.keys())}", file=sys.stderr)
        sys.exit(1)
    return accounts[account]


def get_jwt(account_data: dict) -> str:
    sh_token = account_data.get("superhumanToken", {})
    if isinstance(sh_token, dict):
        return sh_token.get("token", "")
    return str(sh_token)


def get_thread_id(account: str, draft_id: str, retries: int = 5):
    """Fetch thread ID for a draft ID, retrying to handle propagation delay."""
    for attempt in range(retries):
        if attempt > 0:
            time.sleep(1.5)
        result = subprocess.run(
            [BINARY, "draft", "list", "--account", account, "--json"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            line = strip_ansi(line).strip()
            if not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
                if obj.get("id") == draft_id:
                    return obj.get("threadId")
            except json.JSONDecodeError:
                continue
    return None


def upload_attachment(token: str, user_id: str, draft_id: str, thread_id: str, file_path: str) -> bool:
    file_path = os.path.expanduser(file_path)
    if not os.path.exists(file_path):
        print(f"  ✗ File not found: {file_path}", file=sys.stderr)
        return False

    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    with open(file_path, "rb") as f:
        file_bytes = f.read()
    b64 = base64.b64encode(file_bytes).decode()
    attachment_uuid = str(uuid.uuid4())

    print(f"  📎 Uploading {filename} ({len(file_bytes):,} bytes)...")

    # Step 1: Upload file content
    payload = {
        "draftMessageId": draft_id,
        "threadId": thread_id,
        "uuid": attachment_uuid,
        "contentType": mime_type,
        "content": b64,
    }
    req = urllib.request.Request(
        f"{SUPERHUMAN_BACKEND}/v3/attachments.upload",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        download_url = result["downloadUrl"]
    except urllib.error.HTTPError as e:
        print(f"  ✗ Upload failed ({e.code}): {e.read().decode()[:200]}", file=sys.stderr)
        if e.code == 401:
            print("  → Token may be expired. Run: superhuman account auth", file=sys.stderr)
        return False

    # Step 2: Write attachment metadata
    metadata = {
        "writes": [{
            "path": f"users/{user_id}/threads/{thread_id}/messages/{draft_id}/attachments/{attachment_uuid}",
            "value": {
                "uuid": attachment_uuid,
                "cid": None,
                "name": filename,
                "type": mime_type,
                "fixedPartId": "0",
                "messageId": draft_id,
                "threadId": thread_id,
                "inline": False,
                "source": {
                    "type": "upload-firebase",
                    "threadId": thread_id,
                    "messageId": draft_id,
                    "uuid": attachment_uuid,
                    "url": download_url,
                },
                "discardedAt": None,
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
                "size": len(file_bytes),
            },
        }]
    }
    req2 = urllib.request.Request(
        f"{SUPERHUMAN_BACKEND}/v3/userdata.writeMessage",
        data=json.dumps(metadata).encode(),
        headers={
            "Content-Type": "text/plain;charset=UTF-8",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req2, timeout=30) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        print(f"  ✗ Metadata write failed ({e.code}): {e.read().decode()[:200]}", file=sys.stderr)
        if e.code == 401:
            print("  → Token may be expired. Run: superhuman account auth", file=sys.stderr)
        return False

    print(f"  ✓ Attached {filename}")
    return True


def main():
    args = sys.argv[1:]

    # Parse --account and --attach flags; pass everything else through to binary
    account = None
    attach_files = []
    binary_args = []
    is_draft_create = False

    i = 0
    while i < len(args):
        if args[i] in ("create",):
            is_draft_create = True
            binary_args.append(args[i])
            i += 1
        elif args[i] == "--account" and i + 1 < len(args):
            account = args[i + 1]
            binary_args += [args[i], args[i + 1]]
            i += 2
        elif args[i].startswith("--account="):
            account = args[i].split("=", 1)[1]
            binary_args.append(args[i])
            i += 1
        elif args[i] == "--attach" and i + 1 < len(args):
            attach_files.append(args[i + 1])
            i += 2  # strip --attach from binary args
        elif args[i].startswith("--attach="):
            attach_files.append(args[i].split("=", 1)[1])
            i += 1  # strip --attach from binary args
        else:
            binary_args.append(args[i])
            i += 1

    # Run the binary (without --attach)
    result = subprocess.run([BINARY] + binary_args, capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(result.returncode)

    # Only handle attachments for draft create
    if not attach_files or not is_draft_create:
        sys.exit(0)

    # Parse draft ID from binary output (strip ANSI codes first)
    clean_output = strip_ansi(result.stdout)
    draft_id = None
    for line in clean_output.splitlines():
        if "Draft ID:" in line:
            draft_id = line.split("Draft ID:")[-1].strip()
            break

    if not draft_id:
        print("✗ Could not parse Draft ID — attachments skipped.", file=sys.stderr)
        sys.exit(1)

    if not account:
        print("✗ --account is required when using --attach.", file=sys.stderr)
        sys.exit(1)

    # Look up thread ID (with retry for propagation delay)
    thread_id = get_thread_id(account, draft_id)
    if not thread_id:
        print(f"✗ Could not find thread ID for {draft_id} — attachments skipped.", file=sys.stderr)
        sys.exit(1)

    # Load credentials
    acc_data = load_tokens(account)
    token = get_jwt(acc_data)
    user_id = acc_data.get("userId", "")

    if not token:
        print("✗ No Superhuman JWT found. Run: superhuman account auth", file=sys.stderr)
        sys.exit(1)

    # Upload each attachment
    all_ok = all(
        upload_attachment(token, user_id, draft_id, thread_id, f)
        for f in attach_files
    )
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()

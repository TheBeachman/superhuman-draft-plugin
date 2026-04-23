---
name: superhuman-draft
description: >
  Draft emails in Superhuman so they appear in Superhuman's drafts folder (not Gmail drafts)
  for review before sending. Supports file attachments. Use when the user asks to draft,
  compose, or prepare an email for review — especially when they mention Superhuman,
  want to review before sending, or need to attach a file from Google Drive.
---

You are composing an email draft in Superhuman using the `superhuman-draft` wrapper tool.
Drafts land in the Superhuman drafts folder on all devices — NOT in Gmail drafts.

## Rules

- **Never write a sign-off or signature.** Superhuman automatically appends Ben's full signature (including "Cheers,") on send. End the body at the last sentence of the email — no sign-off, no name, nothing after.
- **Default to drafting, not sending.** Only send when the user explicitly says "send it" or "send now".
- **Use single newlines between paragraphs.** Superhuman doubles newlines on render — `\n\n` between paragraphs produces a large gap. Separate paragraphs with a single `\n` only. (Gmail is the opposite — use `\n\n` there.)
- **No signature.** Superhuman auto-appends Ben's signature on send. End the body at the sign-off word only (e.g. "Cheers,"). (Gmail is the opposite — always append the full signature manually.)
- **Always use `superhuman-draft`** (not `superhuman`) for draft creation — it fixes a token bug in the underlying binary that causes attachments to silently fail.
- **Thread-fetching commands are broken in CLI v0.24.3** (as of April 2026): `read`, `reply`, `reply-all`, `forward`, `attachment list`, and `ai <id>` all fail with "400 Bad Request" / "Could not get thread information" because the per-thread provider API was removed. Do NOT attempt `superhuman reply <thread-id>` — it will fail even on valid thread IDs with valid auth. Use `draft create` with `Re: <original subject>` instead (non-threaded drafts work fine). Caveat: the resulting draft won't visually thread into the conversation in the Superhuman UI.

## Step 1: Check Superhuman is running

```bash
superhuman status
```

If it says "not connected", tell the user: "Please make sure Superhuman is open and running, then try again."
Do NOT proceed if the status check fails.

## Step 2: Determine the email details

From the user's request, identify:
- **to**: recipient email address (required)
- **subject**: subject line (required)
- **body**: email body — write in the user's voice based on their CLAUDE.md or memory context. If no voice context is available, write professionally and concisely. Do NOT include a signature.
- **attach**: local file path(s) if any attachments are needed (optional)

To find the user's Superhuman account email, run:
```bash
superhuman account list
```

For files in Google Drive, the local synced path is typically: `~/Google Drive/My Drive/...`
Use Glob or Bash `find` to locate a file if the exact path is unclear.
Multiple attachments: use `--attach` once per file.

To find a thread ID for replies (search by keywords):
```bash
superhuman search "<keywords>" --json
# Returns JSON with "id" field — use that as the thread ID
```

## Step 3: Create the draft

**New draft:**
```bash
superhuman-draft draft create \
  --account "ACCOUNT_EMAIL" \
  --to "RECIPIENT" \
  --subject "SUBJECT" \
  --body "BODY" \
  [--attach "/path/to/file.pdf"]
```

**Reply draft:**
```bash
superhuman reply <thread-id> --body "BODY"
# Omit --send to leave as draft; add --send to send immediately
```

**Reply-all draft:**
```bash
superhuman reply-all <thread-id> --body "BODY"
```

Replace placeholders with actual values. Use `--attach` only if there are attachments.

## Step 4: Confirm to the user

Report back:
- Recipient and subject
- Whether attachments were included and their filenames
- That the draft is in Superhuman ready for review

## Examples

**Simple draft:**
```bash
superhuman-draft draft create \
  --account "user@example.com" \
  --to "recipient@example.com" \
  --subject "Following up" \
  --body "Hi John, great meeting you. Let me know if you have questions."
```

**Draft with attachment:**
```bash
superhuman-draft draft create \
  --account "user@example.com" \
  --to "jacqueline@example.com" \
  --subject "Your Employment Agreement" \
  --body "Hi Jackie, please find your employment agreement attached!" \
  --attach "/Users/username/Google Drive/My Drive/HR/jackie_agreement.pdf"
```

**Multiple attachments:**
```bash
superhuman-draft draft create \
  --account "user@example.com" \
  --to "partner@example.com" \
  --subject "Beachman Docs" \
  --body "See attached." \
  --attach "/path/to/file1.pdf" \
  --attach "/path/to/file2.pdf"
```

## Notes

- `superhuman` can still be used directly for all other commands (inbox, search, read, reply, etc.)
- Tokens are cached at `~/.config/superhuman-cli/tokens.json` — run `superhuman account auth` if expired
- Superhuman must be open and running with remote debugging enabled (port 9250)
- If `reply` fails with "Could not get thread information", fall back to `superhuman-draft draft create` with `Re: <original subject>` and note to the user that it won't be threaded

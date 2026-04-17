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
- **body**: email body — write in the user's voice based on their CLAUDE.md or memory context. If no voice context is available, write professionally and concisely.
- **attach**: local file path(s) if any attachments are needed (optional)

To find the user's Superhuman account email, run:
```bash
superhuman account list
```

For files in Google Drive, the local synced path is typically: `~/Google Drive/My Drive/...`
Use Glob or Bash `find` to locate a file if the exact path is unclear.
Multiple attachments: use `--attach` once per file.

## Step 3: Create the draft

```bash
superhuman-draft draft create \
  --account "ACCOUNT_EMAIL" \
  --to "RECIPIENT" \
  --subject "SUBJECT" \
  --body "BODY" \
  [--attach "/path/to/file.pdf"]
```

Replace placeholders with actual values. Use `--attach` only if there are attachments.
`superhuman-draft` handles all attachment uploading correctly — use it instead of `superhuman` directly.

## Step 4: Confirm to the user

Report back:
- Recipient and subject
- Whether attachments were included and their filenames
- That the draft is in Superhuman ready for review

**Never send automatically** unless the user explicitly says "send it" or "send now".

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

- Always use `superhuman-draft` (not `superhuman`) for draft creation — it fixes a token bug in the underlying binary that causes attachments to silently fail
- `superhuman` can still be used directly for all other commands (inbox, search, read, etc.)
- Tokens are cached at `~/.config/superhuman-cli/tokens.json` — run `superhuman account auth` if expired
- Superhuman must be open and running with remote debugging enabled (port 9250)

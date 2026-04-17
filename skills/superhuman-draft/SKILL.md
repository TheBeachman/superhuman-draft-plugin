---
name: superhuman-draft
description: >
  Draft emails in Superhuman so they appear in Superhuman's drafts folder (not Gmail drafts)
  for review before sending. Supports file attachments. Use when the user asks to draft,
  compose, or prepare an email for review — especially when they mention Superhuman,
  want to review before sending, or need to attach a file from Google Drive.
---

You are composing an email draft in Superhuman using the `superhuman` CLI tool.
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
- **body**: email body — write this in Ben's voice: direct, warm, brief. Sign off as "Cheers, Ben"
- **attach**: local file path(s) if any attachments are needed (optional)

For files in Google Drive, the local path is: `/Users/[username]/Google Drive/My Drive/...`
You can use Glob or Bash `find` to locate the file if the exact path is unclear.
Multiple attachments: use `--attach` once per file.

## Step 3: Create the draft

```bash
superhuman draft create \
  --account "ACCOUNT_EMAIL" \
  --to "RECIPIENT" \
  --subject "SUBJECT" \
  --body "BODY" \
  [--attach "/path/to/file.pdf"]
```

Replace placeholders with actual values. Use `--attach` only if there are attachments.

## Step 4: Confirm to the user

Report back:
- Draft ID
- Recipient, subject
- Whether attachments were included
- That it's sitting in Superhuman drafts ready for review

**Never send the email automatically** unless the user explicitly says "send it" or "send now".

## Examples

**Simple draft:**
```bash
superhuman draft create \
  --account "ben@beachman.ca" \
  --to "investor@example.com" \
  --subject "Beachman Series A — Follow Up" \
  --body "Hi John, great meeting you yesterday. I've attached our investor deck for your review. Let me know if you have any questions.\n\nCheers,\nBen"
```

**Draft with attachment from Google Drive:**
```bash
superhuman draft create \
  --account "ben@beachman.ca" \
  --to "jacqueline@example.com" \
  --subject "Your Employment Agreement" \
  --body "Hi Jackie, please find your employment agreement attached. Let me know if you have any questions!\n\nCheers,\nBen" \
  --attach "/Users/ben/Google Drive/My Drive/Beachman/HR/Employees/Active Employees/Jacqueline Vandervaart/Beachman Employment Agreement [Jacqueline Vandervaart].pdf"
```

**Multiple attachments:**
```bash
superhuman draft create \
  --account "ben@beachman.ca" \
  --to "partner@example.com" \
  --subject "Beachman Docs" \
  --body "See attached." \
  --attach "/path/to/file1.pdf" \
  --attach "/path/to/file2.pdf"
```

## Notes

- The `superhuman` binary must be installed at `~/.bun/bin/superhuman` (handled by `setup.sh`)
- Tokens are cached at `~/.config/superhuman-cli/tokens.json` — run `superhuman account auth` if expired
- Superhuman must be open and running with remote debugging enabled (port 9250)
- The `--account` flag should match the email address shown by `superhuman account list`

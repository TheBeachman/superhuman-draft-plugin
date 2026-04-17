# Superhuman Draft — Claude Code Plugin

Draft emails in **Superhuman** (not Gmail) directly from Claude Code — with full attachment support. Drafts land in your Superhuman drafts folder on all devices for review before sending.

> Built for Beachman Motor Company staff.

---

## Why this exists

Superhuman and Gmail **do not sync drafts**. If Claude creates a draft in Gmail, it won't appear in Superhuman. This plugin uses [`superhuman-cli`](https://github.com/edwinhu/superhuman-cli) to talk to your local Superhuman app directly, so drafts show up right where you review them.

---

## Requirements

- macOS (Apple Silicon / ARM64)
- [Superhuman](https://superhuman.com) desktop app installed
- [Bun](https://bun.sh) runtime (installed automatically by `setup.sh` if missing)
- Claude Code

---

## Installation

### 1. Run setup

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/TheBeachman/superhuman-draft-plugin/main/setup.sh)
```

This will:
- Install Bun if needed
- Download and verify the `superhuman-cli` binary (SHA-256 checked)
- Authenticate with your Superhuman account
- Secure your token file (permissions set to `600`)

### 2. Install the Claude Code plugin

In Claude Code, run:

```
/plugin install https://github.com/TheBeachman/superhuman-draft-plugin
```

### 3. (Recommended) Auto-start Superhuman with debugging

By default, Superhuman must be running with remote debugging enabled on port 9250. To have this happen automatically on login:

```bash
cp com.beachman.superhuman-debug.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.beachman.superhuman-debug.plist
```

> **Note:** This replaces the normal Superhuman launcher. You can still use Superhuman normally — the `--remote-debugging-port=9250` flag just opens a local debugging port used by this plugin.

---

## Usage

Just ask Claude naturally:

> "Draft an email to harrison@beachman.ca about the Vancouver Auto Show follow-up"

> "Draft an email to the investor with the pitch deck attached"

> "Compose a message to Jackie with her employment agreement attached from Drive"

Claude will:
1. Check Superhuman is running
2. Write the email in your voice
3. Create the draft in Superhuman with any attachments
4. Report the draft ID so you can find it instantly

**Claude will never send automatically** — it always saves to drafts first.

---

## Google Drive attachments

Claude can attach files directly from your synced Google Drive folder. Just describe the file:

> "attach Jackie's employment agreement"

Claude will locate the file under `~/Google Drive/My Drive/...` and attach it.

---

## Troubleshooting

### "Not connected to Superhuman"

Superhuman needs to be running with remote debugging enabled. Either:

**Manually:**
```bash
/Applications/Superhuman.app/Contents/MacOS/Superhuman --remote-debugging-port=9250
```

**Or install the LaunchAgent** (see Installation step 3 above).

### Token expired

Re-run authentication:
```bash
superhuman account auth
```

### Check which accounts are linked

```bash
superhuman account list
```

---

## Security notes

- **Token storage:** Your Superhuman JWT tokens are cached at `~/.config/superhuman-cli/tokens.json` with permissions `600` (owner read/write only). Never share this file.
- **Local port only:** The debugging port (9250) is bound to `localhost` only — not accessible externally.
- **Binary trust:** The `superhuman-cli` binary is published by [`edwinhu`](https://github.com/edwinhu/superhuman-cli) and is verified with a SHA-256 checksum during setup. Review the checksum in `setup.sh` against the source repo if you have concerns.
- **Binary is not Apple-notarized:** macOS may warn on first run. This is expected for open-source tools distributed outside the App Store. You can allow it in **System Settings → Privacy & Security**.
- **Scope of access:** Once authenticated, the tool can read email, create drafts, and send messages on behalf of your account. Only install this on devices you control.

---

## Updating

To update the binary to a newer version:

1. Check the latest release at [edwinhu/superhuman-cli](https://github.com/edwinhu/superhuman-cli)
2. Update the `EXPECTED_SHA256` in `setup.sh` with the new binary's hash
3. Re-run `setup.sh`

---

## Credits

- CLI tool: [edwinhu/superhuman-cli](https://github.com/edwinhu/superhuman-cli)
- Plugin packaging: Beachman Motor Company

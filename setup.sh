#!/usr/bin/env bash
# setup.sh — Superhuman Draft Plugin for Claude Code
# Installs the superhuman-cli binary and authenticates with Superhuman
set -e

BINARY_URL="https://github.com/edwinhu/superhuman-cli/raw/main/superhuman-arm64"
BINARY_PATH="$HOME/.bun/bin/superhuman"
EXPECTED_SHA256="9bbe1fc9a9bced524b712b6a9d5a3de7cf13c65142c4bc7557e2092090b1d344"
CONFIG_DIR="$HOME/.config/superhuman-cli"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Superhuman Draft Plugin — Setup        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Check Bun is installed ────────────────────────────────────────────────
if ! command -v bun &> /dev/null; then
  echo "⚠️  Bun is not installed. Installing now..."
  curl -fsSL https://bun.sh/install | bash
  export PATH="$HOME/.bun/bin:$PATH"
  echo "✅ Bun installed."
else
  echo "✅ Bun found: $(bun --version)"
fi

# ── 2. Download superhuman-cli binary ────────────────────────────────────────
echo ""
echo "📥 Downloading superhuman-cli binary..."
curl -fsSL -o "$BINARY_PATH" "$BINARY_URL"
chmod +x "$BINARY_PATH"
echo "✅ Binary installed at $BINARY_PATH"

# ── 3. Verify SHA-256 checksum ───────────────────────────────────────────────
echo ""
echo "🔐 Verifying binary integrity..."
ACTUAL_SHA256=$(shasum -a 256 "$BINARY_PATH" | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
  echo ""
  echo "❌ SHA-256 mismatch! Binary may have been tampered with or updated."
  echo "   Expected: $EXPECTED_SHA256"
  echo "   Got:      $ACTUAL_SHA256"
  echo ""
  echo "   If the edwinhu/superhuman-cli repo was legitimately updated,"
  echo "   check the latest SHA and update setup.sh before proceeding."
  rm -f "$BINARY_PATH"
  exit 1
fi
echo "✅ Checksum verified."

# ── 4. Fix token file permissions if they already exist ──────────────────────
if [ -f "$CONFIG_DIR/tokens.json" ]; then
  chmod 600 "$CONFIG_DIR/tokens.json"
  echo "✅ Token file permissions secured (600)."
fi

# ── 5. Check Superhuman is running ───────────────────────────────────────────
echo ""
echo "🔍 Checking Superhuman connection..."
if ! "$BINARY_PATH" status &> /dev/null; then
  echo ""
  echo "⚠️  Superhuman is not running with remote debugging enabled."
  echo "   Please quit Superhuman if it's open, then run:"
  echo ""
  echo "   /Applications/Superhuman.app/Contents/MacOS/Superhuman --remote-debugging-port=9250 &"
  echo ""
  read -p "Press Enter once Superhuman is running with debugging enabled..."
fi

# ── 6. Authenticate ──────────────────────────────────────────────────────────
echo ""
echo "🔑 Authenticating with Superhuman..."
echo "   (This extracts your JWT token from the running app — one-time setup)"
"$BINARY_PATH" account auth

# ── 7. Secure the token file ─────────────────────────────────────────────────
if [ -f "$CONFIG_DIR/tokens.json" ]; then
  chmod 600 "$CONFIG_DIR/tokens.json"
  echo "✅ Token file secured at $CONFIG_DIR/tokens.json (permissions: 600)"
fi

# ── 8. Test connection ───────────────────────────────────────────────────────
echo ""
echo "🧪 Testing connection..."
"$BINARY_PATH" status

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   ✅  Setup complete!                    ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "To use the skill in Claude Code, ask Claude to draft an email in Superhuman."
echo "Claude will use /superhuman-draft automatically."
echo ""
echo "⚠️  IMPORTANT: Superhuman must always be open when using this skill."
echo "   To start it with debugging enabled each time, run:"
echo "   /Applications/Superhuman.app/Contents/MacOS/Superhuman --remote-debugging-port=9250"
echo ""
echo "   Or add the LaunchAgent (see README.md) to have this happen automatically on login."
echo ""

#!/usr/bin/env bash
# ============================================================
# Push to GitHub and configure all Actions secrets automatically
# Usage: bash scripts/push_and_configure.sh
# Requires: gh auth login already done
# ============================================================
set -e
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

echo ""
echo "▶ Checking GitHub auth..."
gh auth status || { echo "❌ Run: gh auth login --web"; exit 1; }

echo "▶ Pushing all commits to GitHub..."
gh repo set-default Luuquilu/argentina-trends 2>/dev/null || true
git push origin main
echo "   ✅ Code pushed"

echo "▶ Setting GitHub Actions secrets from .env..."
source .env

gh secret set SUPABASE_URL      --body "$SUPABASE_URL"
gh secret set SUPABASE_KEY      --body "$SUPABASE_KEY"
gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_API_KEY"

# Optional secrets — only set if they exist
[[ -n "$REDDIT_CLIENT_ID"     ]] && gh secret set REDDIT_CLIENT_ID     --body "$REDDIT_CLIENT_ID"
[[ -n "$REDDIT_CLIENT_SECRET" ]] && gh secret set REDDIT_CLIENT_SECRET --body "$REDDIT_CLIENT_SECRET"
[[ -n "$YOUTUBE_API_KEY"      ]] && gh secret set YOUTUBE_API_KEY      --body "$YOUTUBE_API_KEY"

echo "   ✅ All secrets configured"

echo ""
echo "▶ Triggering first GitHub Actions run..."
gh workflow run collect.yml
echo "   ✅ Workflow triggered"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ GitHub setup complete!                       ║"
echo "║                                                  ║"
echo "║  GitHub Actions will now:                        ║"
echo "║  • Collect data every 1 hour (forever, free)     ║"
echo "║  • Analyze trends every 6 hours (forever, free)  ║"
echo "║                                                  ║"
echo "║  Watch runs at:                                  ║"
echo "║  github.com/Luuquilu/argentina-trends/actions    ║"
echo "╚══════════════════════════════════════════════════╝"

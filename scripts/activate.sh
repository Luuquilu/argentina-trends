#!/usr/bin/env bash
# ============================================================
# Argentina Trends — Full Activation Script
# Run this AFTER filling in .env with real keys
# Usage: bash scripts/activate.sh
# ============================================================
set -e
cd "$(dirname "$0")/.."
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  🇦🇷 Argentina Trends — Activation           ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# 1. Validate .env
echo "▶ Step 1/5 — Checking credentials..."
source .env 2>/dev/null || true

MISSING=""
[[ "$SUPABASE_URL"       == *"supabase.co"* ]] || MISSING="$MISSING SUPABASE_URL"
[[ "$SUPABASE_KEY"       != "PASTE"*        ]] || MISSING="$MISSING SUPABASE_KEY"
[[ "$ANTHROPIC_API_KEY"  != "sk-ant-..."    ]] || MISSING="$MISSING ANTHROPIC_API_KEY"

if [[ -n "$MISSING" ]]; then
  echo "❌ Missing keys in .env:$MISSING"
  echo "   Edit .env and re-run this script."
  exit 1
fi
echo "   ✅ Credentials OK"

# 2. Test Supabase connection + schema
echo ""
echo "▶ Step 2/5 — Testing Supabase connection..."
python3 - <<'PYEOF'
import os, sys
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client
c = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
# Check all 3 required tables exist
tables = ["posts", "trends", "google_trends"]
for t in tables:
    try:
        c.table(t).select("*").limit(1).execute()
        print(f"   ✅ Table '{t}' OK")
    except Exception as e:
        print(f"   ❌ Table '{t}' missing — run storage/migrate.sql in Supabase")
        sys.exit(1)
PYEOF

# 3. First collection run
echo ""
echo "▶ Step 3/5 — Running first data collection (RSS + Google Trends)..."
python3 agent.py --collect-only
echo "   ✅ Collection complete"

# 4. First analysis run
echo ""
echo "▶ Step 4/5 — Running trend analysis..."
python3 agent.py --analyze-only
echo "   ✅ Analysis complete"

# 5. Launch dashboard
echo ""
echo "▶ Step 5/5 — Starting dashboard..."
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  🚀 Dashboard starting at:                   ║"
echo "║     http://localhost:8501                    ║"
echo "║                                              ║"
echo "║  Press Ctrl+C to stop                        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
streamlit run dashboard/app.py

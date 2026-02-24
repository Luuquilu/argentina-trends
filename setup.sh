#!/bin/bash
# ============================================================
# Argentina Trends — One-time setup script
# Run this after filling in your .env file
# Usage: bash setup.sh
# ============================================================
set -e

export PATH="$HOME/Library/Python/3.9/bin:$PATH"

echo ""
echo "🇦🇷 Argentina Trends Setup"
echo "=========================="
echo ""

# 1. Check .env
echo "➤ Checking .env..."
if ! grep -q "supabase.co" .env 2>/dev/null; then
  echo "⚠️  .env is not filled in yet!"
  echo ""
  echo "Please fill in .env with your Supabase + Anthropic credentials first."
  echo "See README.md for how to get these (takes ~5 min)."
  exit 1
fi
echo "   ✅ .env looks configured"

# 2. Load env
set -a; source .env; set +a

# 3. Verify Supabase connection
echo ""
echo "➤ Testing Supabase connection..."
python3 -c "
from supabase import create_client
import os
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
c = create_client(url, key)
r = c.table('posts').select('id').limit(1).execute()
print('   ✅ Supabase connected')
" 2>/dev/null || {
  echo "   ❌ Could not connect to Supabase."
  echo "   → Make sure you ran storage/schema.sql in the Supabase SQL Editor first."
  exit 1
}

# 4. Run a quick collection test
echo ""
echo "➤ Running quick data collection (RSS only)..."
python3 -c "
import sys; sys.path.insert(0,'.')
from collectors import rss_collector
from storage.db import save_posts
posts = rss_collector.collect()
saved = save_posts(posts)
print(f'   ✅ RSS: {saved} posts saved to Supabase')
"

echo ""
echo "✅ Setup complete! Everything is working."
echo ""
echo "Next steps:"
echo "  1. Run a full collection:   python3 agent.py --once"
echo "  2. Launch the dashboard:    streamlit run dashboard/app.py"
echo "  3. Push to GitHub for auto-scheduling (see README.md)"
echo ""

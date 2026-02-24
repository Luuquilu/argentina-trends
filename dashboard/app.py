"""
🇦🇷 Argentina Trend Detection Dashboard
=======================================
Streamlit dashboard that reads from Supabase and visualises trends.

Run locally:
    streamlit run dashboard/app.py

Deploy free on Streamlit Cloud:
    1. Push repo to GitHub
    2. Go to share.streamlit.io
    3. Connect repo, set entry point: dashboard/app.py
    4. Add secrets: SUPABASE_URL, SUPABASE_KEY
"""

import os
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🇦🇷 Argentina Trends",
    page_icon="🇦🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.6rem; }
.stExpander { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Supabase ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("⚠️ Missing SUPABASE_URL / SUPABASE_KEY — add them to .env or Streamlit secrets.")
        st.stop()
    return create_client(url, key)

# ── Fetchers (cached 5 min) ───────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_posts(hours: int = 24) -> pd.DataFrame:
    c = get_supabase()
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    r = c.table("posts").select("*").gte("collected_at", since).limit(5000).execute()
    if not r.data:
        return pd.DataFrame()
    df = pd.DataFrame(r.data)
    df["collected_at"] = pd.to_datetime(df["collected_at"], utc=True, errors="coerce")
    df["published_at"]  = pd.to_datetime(df.get("published_at"), utc=True, errors="coerce")
    df["sentiment_score"] = pd.to_numeric(df.get("sentiment_score", 0), errors="coerce").fillna(0)
    return df

@st.cache_data(ttl=300)
def fetch_trends(limit: int = 20) -> pd.DataFrame:
    c = get_supabase()
    r = c.table("trends").select("*").order("created_at", desc=True).limit(limit).execute()
    if not r.data:
        return pd.DataFrame()
    df = pd.DataFrame(r.data)
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    return df

@st.cache_data(ttl=300)
def fetch_gtrends(limit: int = 100) -> pd.DataFrame:
    c = get_supabase()
    r = c.table("google_trends").select("*").order("captured_at", desc=True).limit(limit).execute()
    if not r.data:
        return pd.DataFrame()
    df = pd.DataFrame(r.data)
    df["captured_at"] = pd.to_datetime(df["captured_at"], utc=True, errors="coerce")
    return df

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🇦🇷 Argentina Trends")
    st.markdown("---")
    time_window = st.selectbox(
        "⏱ Time window",
        [6, 12, 24, 48, 72],
        index=2,
        format_func=lambda x: f"Last {x}h",
    )
    st.markdown("---")
    if st.button("🔄 Refresh now"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.caption(f"Auto-refresh every 5 min")
    st.caption(f"Loaded: {datetime.utcnow().strftime('%d %b %H:%M')} UTC")

# ── Load ──────────────────────────────────────────────────────────────────────
posts_df   = fetch_posts(hours=time_window)
trends_df  = fetch_trends()
gtrends_df = fetch_gtrends()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🇦🇷 Argentina Social Media Trends")
st.markdown(f"*Real-time monitoring of Argentine social media & news · last {time_window}h*")
st.markdown("---")

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
n_posts   = len(posts_df)
n_sources = posts_df["source"].nunique() if not posts_df.empty else 0
n_trends  = len(trends_df)

pos_pct = neg_pct = 0.0
if not posts_df.empty and "sentiment" in posts_df.columns:
    pos_pct = (posts_df["sentiment"] == "positive").mean() * 100
    neg_pct = (posts_df["sentiment"] == "negative").mean() * 100

k1.metric("📰 Posts", f"{n_posts:,}")
k2.metric("📡 Sources", n_sources)
k3.metric("🔥 Trends", n_trends)
k4.metric("😊 Positive", f"{pos_pct:.1f}%")
k5.metric("😠 Negative", f"{neg_pct:.1f}%")

st.markdown("---")

# ── Two-column layout ─────────────────────────────────────────────────────────
col_l, col_r = st.columns([3, 2])

with col_l:
    # Volume over time
    st.subheader("📈 Content volume by source")
    if not posts_df.empty:
        df_v = posts_df.copy()
        df_v["hour"] = df_v["collected_at"].dt.floor("H")
        vol = df_v.groupby(["hour", "source"]).size().reset_index(name="count")
        fig = px.area(
            vol, x="hour", y="count", color="source",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"hour": "", "count": "Posts", "source": "Source"},
        )
        fig.update_layout(
            height=280, margin=dict(l=0, r=0, t=8, b=0),
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No posts yet — run `python agent.py --once` to collect data.")

    # Sentiment bar
    st.subheader("🎭 Sentiment distribution")
    if not posts_df.empty and "sentiment" in posts_df.columns:
        sc = posts_df["sentiment"].value_counts().reset_index()
        sc.columns = ["sentiment", "count"]
        cmap = {"positive": "#00b894", "negative": "#d63031",
                "neutral": "#636e72", "mixed": "#fdcb6e"}
        fig2 = px.bar(
            sc, x="sentiment", y="count", color="sentiment",
            color_discrete_map=cmap,
            labels={"sentiment": "", "count": "Posts"},
        )
        fig2.update_layout(showlegend=False, height=240,
                           margin=dict(l=0, r=0, t=8, b=0))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sentiment data not available yet.")

with col_r:
    # Google Trends
    st.subheader("📊 Google Trends (Argentina)")
    if not gtrends_df.empty:
        latest = (
            gtrends_df.groupby("keyword")["value"]
            .last()
            .sort_values(ascending=False)
            .head(12)
        )
        fig3 = px.bar(
            x=latest.values, y=latest.index,
            orientation="h",
            color=latest.values,
            color_continuous_scale="Blues",
            labels={"x": "Score", "y": ""},
        )
        fig3.update_layout(
            showlegend=False, coloraxis_showscale=False,
            height=280, margin=dict(l=0, r=0, t=8, b=0),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Google Trends data not yet collected.")

    # Source pie
    st.subheader("🥧 Source breakdown")
    if not posts_df.empty:
        sc2 = posts_df["source"].value_counts().reset_index()
        sc2.columns = ["source", "count"]
        fig4 = px.pie(
            sc2, names="source", values="count",
            hole=0.42,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig4.update_layout(height=240, margin=dict(l=0, r=0, t=8, b=0))
        st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── Detected Trends ───────────────────────────────────────────────────────────
st.subheader("🔥 Latest Detected Trends")
if not trends_df.empty:
    for _, row in trends_df.head(8).iterrows():
        label = row.get("topic_label") or "Unnamed trend"
        count = row.get("post_count", 0)
        with st.expander(f"**{label}** — {count} posts"):
            a, b = st.columns([2, 1])
            with a:
                kws = row.get("keywords", [])
                if isinstance(kws, list) and kws:
                    st.markdown("**Keywords:** " + "  ·  ".join(f"`{k}`" for k in kws[:12]))
                summary = row.get("ai_summary") or row.get("aO_summary", "")
                if summary:
                    st.markdown(f"**AI Summary:** {summary}")
            with b:
                avg = row.get("avg_sentiment") or 0
                lbl = "😊 Positive" if avg > 0.2 else ("😠 Negative" if avg < -0.2 else "😐 Neutral")
                st.metric("Sentiment", lbl)
                st.metric("Posts", count)
                ts = row.get("created_at")
                if ts:
                    st.caption(pd.Timestamp(ts).strftime("Detected %d %b %H:%M UTC"))
else:
    st.info("No trends detected yet — analysis runs every 6h after data collection.")

st.markdown("---")

# ── Recent Posts Table ─────────────────────────────────────────────────────────
st.subheader("📋 Recent posts")
if not posts_df.empty:
    cols = [c for c in ["collected_at", "source", "title", "sentiment", "url"] if c in posts_df.columns]
    show = posts_df[cols].copy()
    if "collected_at" in show.columns:
        show["collected_at"] = show["collected_at"].dt.strftime("%d %b %H:%M")
    if "title" in show.columns:
        show["title"] = show["title"].str[:90]
    show = show.rename(columns={
        "collected_at": "Time", "source": "Source",
        "title": "Title", "sentiment": "Sentiment", "url": "URL",
    })
    cfg = {}
    if "URL" in show.columns:
        cfg["URL"] = st.column_config.LinkColumn("URL", display_text="🔗 Open")
    st.dataframe(show.head(100), use_container_width=True,
                 column_config=cfg, hide_index=True)
else:
    st.info("No posts yet.")

st.markdown("---")
st.caption("🇦🇷 Argentina Trends · Streamlit + Supabase + Claude Haiku · ~$1–5/month")

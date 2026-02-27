#!/Users/lucascatsoulieris/Library/Python/3.9/bin/python3
"""
Launcher wrapper for Streamlit in Claude's preview_start sandbox.
The sandbox blocks os.getcwd() / Path.cwd() — this script patches both
to return the project directory as a fallback before Streamlit loads.
"""
import os
import sys

_PROJECT = "/Users/lucascatsoulieris/Desktop/Argentina Trends"

# ── Patch os.getcwd ──────────────────────────────────────────────────────────
_real_getcwd = os.getcwd

def _safe_getcwd():
    try:
        return _real_getcwd()
    except (PermissionError, OSError):
        return _PROJECT

os.getcwd = _safe_getcwd

# ── Patch pathlib.Path.cwd ───────────────────────────────────────────────────
import pathlib

@classmethod
def _safe_cwd(cls):
    try:
        return cls(_real_getcwd())
    except (PermissionError, OSError):
        return cls(_PROJECT)

pathlib.Path.cwd = _safe_cwd

# ── Launch Streamlit ─────────────────────────────────────────────────────────
sys.argv = [
    "streamlit", "run",
    f"{_PROJECT}/dashboard/app.py",
    "--server.port", "8501",
    "--server.headless", "true",
]

from streamlit.web.cli import main
main()

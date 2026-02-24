"""
ui/styles.py
Inject CSS vào Streamlit. Tập trung style ở 1 chỗ.
"""
import streamlit as st

_CSS = """
<style>
    /* ── Nền tối ─────────────────────────────────── */
    .stApp { background-color: #0f1117; }

    /* ── Header ──────────────────────────────────── */
    .recrew-header { text-align: center; padding: 30px 0 10px 0; }
    .recrew-title {
        font-size: 3em; font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .recrew-subtitle { color: #888; font-size: 1em; margin-top: 5px; }

    /* ── Agent cards ──────────────────────────────── */
    .agent-card {
        background: #1a1d27; border: 1px solid #2d3748;
        border-radius: 12px; padding: 16px; text-align: center;
        transition: all 0.3s;
    }
    .agent-card:hover { border-color: #667eea; transform: translateY(-2px); }
    .agent-emoji { font-size: 2em; }
    .agent-name  { color: #e2e8f0; font-weight: 600; font-size: 0.9em; margin: 8px 0 4px 0; }
    .agent-role  { color: #718096; font-size: 0.75em; }

    /* ── Status dots ──────────────────────────────── */
    .status-dot {
        display: inline-block; width: 8px; height: 8px;
        border-radius: 50%; margin-right: 5px;
    }
    .online  { background: #48bb78; box-shadow: 0 0 6px #48bb78; }
    .working { background: #ed8936; box-shadow: 0 0 6px #ed8936; animation: pulse 1s infinite; }
    .idle    { background: #718096; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

    /* ── Agent timeline (khi chạy) ────────────────── */
    .agent-timeline {
        background: #1a1d27; border: 1px solid #2d3748;
        border-radius: 10px; padding: 14px 18px;
        font-family: monospace; font-size: 0.88em;
    }
    .agent-row {
        display: flex; align-items: center; gap: 10px;
        padding: 5px 0; border-bottom: 1px solid #2d374840;
    }
    .agent-row:last-child { border-bottom: none; }
    .agent-row .ar-emoji  { width: 24px; text-align: center; }
    .agent-row .ar-name   { width: 160px; color: #e2e8f0; }
    .agent-row .ar-status { color: #718096; font-size: 0.85em; flex: 1; }
    .ar-done    { color: #48bb78; }
    .ar-active  { color: #ed8936; animation: pulse 1s infinite; }
    .ar-waiting { color: #4a5568; }

    /* ── Log box ──────────────────────────────────── */
    .log-box {
        background: #0d1117; border: 1px solid #2d3748;
        border-radius: 8px; padding: 12px 16px;
        font-family: monospace; font-size: 0.82em;
        color: #718096; max-height: 180px; overflow-y: auto;
        margin-top: 10px;
    }

    /* ── History item sidebar ─────────────────────── */
    .hist-item {
        background: #1a1d27; border: 1px solid #2d3748;
        border-radius: 8px; padding: 8px 10px;
        margin-bottom: 6px; cursor: pointer;
        font-size: 0.8em; transition: border-color 0.2s;
    }
    .hist-item:hover { border-color: #667eea; }
    .hist-task  { color: #e2e8f0; font-weight: 500; }
    .hist-meta  { color: #4a5568; font-size: 0.85em; margin-top: 2px; }

    /* ── Text inputs ──────────────────────────────── */
    .stTextArea textarea {
        background: #1a1d27 !important; color: #e2e8f0 !important;
        border: 1px solid #2d3748 !important; border-radius: 10px !important;
        font-size: 1em !important;
    }
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }
    .stTextInput input {
        background: #1a1d27 !important; color: #e2e8f0 !important;
        border: 1px solid #2d3748 !important; border-radius: 8px !important;
    }

    /* ── Buttons ──────────────────────────────────── */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; border: none; border-radius: 10px;
        padding: 14px; font-size: 1.1em; font-weight: 700;
        cursor: pointer; transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* ── Ẩn Streamlit branding ────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"]     { visibility: hidden; }
    [data-testid="stDeployButton"] { display: none; }
</style>
"""


def inject_css() -> None:
    """Inject toàn bộ custom CSS vào trang."""
    st.markdown(_CSS, unsafe_allow_html=True)

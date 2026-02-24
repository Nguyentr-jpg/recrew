"""
ui/sidebar.py
Render toàn bộ sidebar: API key (với persistence), model selector,
thống kê, và task history.
"""
import streamlit as st
from utils.settings import load_saved_key, save_key, clear_key, load_saved_model, save_model
from utils.history import get_history, load_history_item

_MODELS = [
    "gemini/gemini-2.5-flash",
    "gemini/gemini-2.5-flash-lite",
    "gemini/gemini-2.5-pro",
]

_MODEL_LABELS = {
    "gemini/gemini-2.5-flash":      "Gemini 2.5 Flash (khuyến nghị)",
    "gemini/gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite (nhanh, rẻ)",
    "gemini/gemini-2.5-pro":        "Gemini 2.5 Pro (mạnh nhất)",
}


def render_sidebar() -> tuple[str, str]:
    """
    Render sidebar và trả về (api_key, selected_model).
    Gọi ở đầu app.py trước khi render main content.
    """
    with st.sidebar:
        st.markdown("## ⚙️ Cài đặt")
        st.markdown("---")

        api_key = _render_api_key_section()

        st.markdown("---")
        selected_model = _render_model_selector()

        st.markdown("---")
        _render_stats()

        st.markdown("---")
        _render_history()

        st.markdown("---")
        _render_about()

    return api_key, selected_model


# ── Private helpers ──────────────────────────────────────────────────────────

def _render_api_key_section() -> str:
    """Render ô nhập API key + checkbox lưu key. Trả về api_key string."""
    saved_key = load_saved_key()

    # Nếu đã có saved key → dùng làm default value
    api_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        placeholder="AIzaSy...",
        value=saved_key,
        help="Lấy miễn phí tại aistudio.google.com",
    )

    remember = st.checkbox(
        "💾 Ghi nhớ key trên máy này",
        value=bool(saved_key),
        help="Lưu vào ~/.recrew_settings.json (chỉ trên máy bạn, không lên git)",
    )

    # Xử lý lưu / xóa
    if api_key and remember:
        save_key(api_key)
    elif not remember and saved_key:
        # User bỏ tick → xóa saved key
        clear_key()

    if api_key:
        st.success("✅ API Key đã nhập")
    else:
        st.warning("⚠️ Cần nhập API Key để chạy")
        st.markdown("[Lấy API Key miễn phí →](https://aistudio.google.com)")

    return api_key


def _render_model_selector() -> str:
    """Render dropdown chọn model. Nhớ lựa chọn cuối cùng."""
    st.markdown("### 🤖 Chọn Model")

    saved_model = load_saved_model()
    default_idx = _MODELS.index(saved_model) if saved_model in _MODELS else 0

    selected = st.selectbox(
        "Gemini Model",
        options=_MODELS,
        index=default_idx,
        format_func=lambda m: _MODEL_LABELS.get(m, m),
        label_visibility="collapsed",
    )

    # Lưu lựa chọn
    save_model(selected)

    # Ghi chú nhỏ về model
    notes = {
        "gemini/gemini-2.5-flash":      "⚡ Cân bằng tốc độ & chất lượng",
        "gemini/gemini-2.5-flash-lite": "🚀 Nhanh nhất, ít token nhất",
        "gemini/gemini-2.5-pro":        "🧠 Chất lượng cao nhất, chậm hơn",
    }
    st.caption(notes.get(selected, ""))

    return selected


def _render_stats() -> None:
    """Render thống kê trong session."""
    st.markdown("### 📊 Thống kê phiên này")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Task đã chạy", st.session_state.get("task_count", 0))
    with col2:
        st.metric("Lần sửa lại", st.session_state.get("revision_count", 0))


def _render_history() -> None:
    """Render danh sách task history trong session. Click để load lại."""
    history = get_history()
    if not history:
        return

    st.markdown("### 🕐 Lịch sử phiên này")
    st.caption("Click vào task để load lại kết quả")

    for i, item in enumerate(history):
        task_short = item["task"][:45] + "..." if len(item["task"]) > 45 else item["task"]
        rev_label  = f" · {item['revisions']} lần sửa" if item.get("revisions") else ""
        code_icon  = "🌐" if item.get("code_type") == "html" else ("🐍" if item.get("code_type") == "python" else "📄")

        btn_label = f"{code_icon} {item['date']} {item['timestamp']}{rev_label}\n{task_short}"

        if st.button(btn_label, key=f"hist_{i}", use_container_width=True):
            load_history_item(item)
            st.rerun()


def _render_about() -> None:
    """Render phần giới thiệu nhỏ về ReCrew."""
    with st.expander("ℹ️ Về ReCrew"):
        st.markdown("""
**ReCrew** — AI Development Team

5 agents phối hợp viết code thật:
- 🔎 Researcher → phân tích & đề xuất
- 💻 Developer → viết code hoàn chỉnh
- 🔍 Reviewer → review & tìm bug
- 🧪 QA Tester → test case
- 👑 Team Lead → tổng hợp & trình bày

**Tech:** CrewAI · Gemini · Streamlit
        """)

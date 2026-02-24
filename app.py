"""
app.py — ReCrew Streamlit entry point
Lean orchestration file. Logic thực sự nằm trong:
  crew/   → workflow chạy AI team
  utils/  → code extraction, settings, history
  ui/     → CSS, sidebar, tetris demo
"""
import os
import streamlit as st
import streamlit.components.v1 as components

from utils import extract_code, init_history, add_to_history
from utils.history import update_latest_revision
from crew import run_main_workflow, run_revision_workflow
from ui import inject_css, render_sidebar
from ui.tetris_demo import render_tetris_demo

# ─────────────────────────────────────────
# CẤU HÌNH TRANG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ReCrew - AI Team",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_history()   # khởi tạo tất cả session_state keys 1 lần duy nhất

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
api_key, selected_model = render_sidebar()

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="recrew-header">
    <h1 class="recrew-title">⚡ ReCrew</h1>
    <p class="recrew-subtitle">Your AI Software Development Team</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HIỂN THỊ TEAM
# ─────────────────────────────────────────
_TEAM = [
    ("👑", "Trưởng Nhóm",     "Lên kế hoạch & tổng hợp"),
    ("💻", "Lập Trình Viên",  "Viết code hoàn chỉnh"),
    ("🔍", "Kiểm Duyệt",      "Review & tìm bug"),
    ("🧪", "QA Tester",       "Viết test case"),
    ("🔎", "Nhà Nghiên Cứu",  "Tìm giải pháp kỹ thuật"),
]
cols = st.columns(len(_TEAM))
for i, (emoji, name, role) in enumerate(_TEAM):
    with cols[i]:
        status = "working" if st.session_state.get("is_running") else "online"
        st.markdown(f"""
        <div class="agent-card">
            <div class="agent-emoji">{emoji}</div>
            <div class="agent-name">{name}</div>
            <div class="agent-role">{role}</div>
            <div style="margin-top:8px">
                <span class="status-dot {status}"></span>
                <span style="color:#718096;font-size:0.75em">
                    {"Đang làm" if status == "working" else "Sẵn sàng"}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────
# NHẬP TASK
# ─────────────────────────────────────────
st.markdown("### 📋 Nhập Task")

col1, col2 = st.columns([3, 1])
with col1:
    task_input = st.text_area(
        "Task",
        placeholder=(
            "Ví dụ: Tạo game Snake bằng HTML+JS có tính điểm...\n"
            "Hoặc: Viết API FastAPI quản lý danh sách công việc..."
        ),
        height=130,
        label_visibility="collapsed",
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    goi_y = st.button("💡 Gợi ý")
    chay  = st.button("🚀 Chạy Team", type="primary", disabled=not api_key)

if goi_y:
    st.info("""
**💡 Gợi ý task:**
- Tạo game Snake HTML+JS có điểm số và level tăng dần
- Viết script Python đổi tên hàng loạt file ảnh theo ngày
- Tạo dashboard HTML hiển thị thống kê doanh thu giả lập
- Viết Telegram bot trả lời câu hỏi cơ bản bằng Python
- Tạo tool Python tải ảnh hàng loạt từ danh sách URL
    """)

# ─────────────────────────────────────────
# HELPER: render result tabs
# ─────────────────────────────────────────
def _render_result(result_text: str, game_html, py_code, task: str, rev_num: int = 0) -> None:
    title = "### ✅ Kết quả" + (f" (lần sửa {rev_num})" if rev_num else "")
    st.markdown(title)

    if game_html:
        tab_r, tab_g, tab_dl = st.tabs(["📄 Báo cáo", "▶️ Chạy ngay", "💾 Tải về"])
        with tab_g:
            st.info("💡 Click vào canvas → dùng bàn phím để tương tác.")
            components.html(game_html, height=650, scrolling=False)
    else:
        tab_r, tab_dl = st.tabs(["📄 Báo cáo", "💾 Tải về"])

    with tab_r:
        st.markdown(result_text)

    with tab_dl:
        st.download_button(
            "⬇️ Tải báo cáo (.md)",
            data=f"# Kết quả ReCrew\n\n**Task:** {task}\n\n---\n\n{result_text}",
            file_name="recrew_ket_qua.md",
            mime="text/markdown",
        )
        if game_html:
            fname = f"result_v{rev_num}.html" if rev_num else "result.html"
            st.download_button("⬇️ Tải HTML (chạy được ngay)", data=game_html, file_name=fname, mime="text/html")
            st.success(f"✅ Mở `{fname}` bằng trình duyệt là chạy ngay!")
        elif py_code:
            fname = f"result_v{rev_num}.py" if rev_num else "result.py"
            st.download_button("⬇️ Tải Python (chạy được ngay)", data=py_code, file_name=fname, mime="text/plain")
            st.success(f"✅ Chạy bằng `python {fname}`!")
        st.info("📁 File cũng đã lưu tại thư mục `output/`")


# ─────────────────────────────────────────
# HELPER: agent timeline HTML
# ─────────────────────────────────────────
_AGENTS_INFO = [
    ("🔎", "Nhà Nghiên Cứu"),
    ("💻", "Lập Trình Viên"),
    ("🔍", "Kiểm Duyệt"),
    ("🧪", "QA Tester"),
    ("👑", "Trưởng Nhóm"),
]


def _timeline_html(active_idx: int) -> str:
    rows = ""
    for i, (emoji, name) in enumerate(_AGENTS_INFO):
        if i < active_idx:
            cls, label = "ar-done", "✅ Xong"
        elif i == active_idx:
            cls, label = "ar-active", "⏳ Đang làm..."
        else:
            cls, label = "ar-waiting", "─ Chờ"
        rows += (
            f'<div class="agent-row">'
            f'<span class="ar-emoji">{emoji}</span>'
            f'<span class="ar-name">{name}</span>'
            f'<span class="ar-status {cls}">{label}</span>'
            f'</div>'
        )
    return f'<div class="agent-timeline">{rows}</div>'


# ─────────────────────────────────────────
# CHẠY TEAM (main workflow)
# ─────────────────────────────────────────
if chay and task_input and api_key:
    st.session_state.is_running  = True
    st.session_state.task_count += 1

    st.markdown("---")
    st.markdown("### 🏃 Team đang làm việc...")

    progress_bar = st.progress(0)
    status_text  = st.empty()
    timeline_box = st.empty()
    log_box      = st.empty()
    logs         = []
    _active      = [0]

    _PROGRESS_MAP = [15, 40, 60, 80, 95]
    _STATUS_MAP   = [
        "🔎 Nhà Nghiên Cứu đang phân tích...",
        "💻 Lập Trình Viên đang viết code...",
        "🔍 Kiểm Duyệt đang review...",
        "🧪 QA Tester đang viết test case...",
        "👑 Trưởng Nhóm đang tổng hợp...",
    ]

    def _add_log(msg):
        logs.append(msg)
        log_box.markdown(
            '<div class="log-box">' + "<br>".join(logs[-15:]) + "</div>",
            unsafe_allow_html=True,
        )

    def _on_task_done(step_idx: int):
        _active[0] = step_idx + 1
        timeline_box.markdown(_timeline_html(_active[0]), unsafe_allow_html=True)
        _add_log(f"✅ {_AGENTS_INFO[step_idx][1]} hoàn thành")
        if _active[0] < len(_PROGRESS_MAP):
            progress_bar.progress(_PROGRESS_MAP[_active[0]])
            status_text.markdown(f"**{_STATUS_MAP[_active[0]]}**")

    progress_bar.progress(_PROGRESS_MAP[0])
    status_text.markdown(f"**{_STATUS_MAP[0]}**")
    timeline_box.markdown(_timeline_html(0), unsafe_allow_html=True)
    _add_log("─" * 35)
    _add_log("🚀 Team bắt đầu làm việc...")

    try:
        result = run_main_workflow(
            task_input=task_input,
            api_key=api_key,
            model=selected_model,
            on_task_done=_on_task_done,
        )

        if result["error"]:
            raise RuntimeError(result["error"])

        progress_bar.progress(100)
        status_text.markdown("✅ **Hoàn thành!**")
        timeline_box.markdown(_timeline_html(5), unsafe_allow_html=True)
        _add_log("✅ Team hoàn thành task!")

        extracted = extract_code(result["result_text"], result["dev_raw"])
        game_html = extracted["html"]
        py_code   = extracted["python"]

        os.makedirs("output", exist_ok=True)
        if game_html:
            open("output/result.html", "w", encoding="utf-8").write(game_html)
        elif py_code:
            open("output/result.py",   "w", encoding="utf-8").write(py_code)
        open("output/ket_qua.md", "w", encoding="utf-8").write(
            f"# Kết quả ReCrew\n\n**Task:** {task_input}\n\n---\n\n{result['result_text']}"
        )

        st.session_state.last_result    = result["result_text"]
        st.session_state.last_code      = game_html or py_code
        st.session_state.last_code_type = extracted["code_type"]
        st.session_state.last_task      = task_input
        st.session_state.revision_count = 0
        add_to_history(task_input, result["result_text"], game_html or py_code, extracted["code_type"])

        st.markdown("---")
        _render_result(result["result_text"], game_html, py_code, task_input)

    except Exception as e:
        err = str(e)
        if "404" in err or "not found" in err.lower():
            st.error(f"❌ **Model không tồn tại (404)** — Đổi model khác ở sidebar.\n\n`{err[:200]}`")
        elif "429" in err or "quota" in err.lower() or "rate limit" in err.lower():
            st.error(
                "❌ **Vượt quota Gemini (429)** — Thử:\n"
                "1. Đổi sang `gemini-2.5-flash-lite` ở sidebar\n"
                "2. Chờ vài phút rồi thử lại\n"
                f"\n`{err[:200]}`"
            )
        else:
            st.error(f"❌ Lỗi: {err[:300]}")
        _add_log(f"❌ Lỗi: {err}")

    finally:
        st.session_state.is_running = False

elif chay and not task_input:
    st.warning("⚠️ Vui lòng nhập task trước!")
elif chay and not api_key:
    st.error("❌ Vui lòng nhập API Key ở thanh bên trái!")

# ─────────────────────────────────────────
# HIỂN THỊ KẾT QUẢ TỪ HISTORY
# ─────────────────────────────────────────
loaded = st.session_state.get("loaded_history_item")
if loaded and not chay:
    st.markdown("---")
    st.info(f"📂 Đang xem lại: **{str(loaded.get('task', ''))[:80]}**")
    r_text = st.session_state.get("last_result", "")
    code   = st.session_state.get("last_code")
    c_type = st.session_state.get("last_code_type")
    html_c = code if c_type == "html" else None
    py_c   = code if c_type == "python" else None
    if r_text:
        _render_result(r_text, html_c, py_c, loaded.get("task", ""), loaded.get("revisions", 0))
    st.session_state.loaded_history_item = None

# ─────────────────────────────────────────
# VÒNG LẶP PHẢN HỒI
# ─────────────────────────────────────────
if st.session_state.get("last_result") and not st.session_state.get("is_running"):
    st.markdown("---")
    rev_count = st.session_state.get("revision_count", 0)
    st.markdown("### 💬 Phản hồi với team")
    if rev_count > 0:
        st.caption(f"✏️ Đã sửa {rev_count} lần. Tiếp tục phản hồi nếu chưa ổn.")
    else:
        st.caption("Chưa ưng hoặc có lỗi? Nhập phản hồi — Developer nhận code cũ + phản hồi và sửa lại.")

    fb_col, btn_col = st.columns([4, 1])
    with fb_col:
        feedback_text = st.text_area(
            "Phản hồi",
            placeholder="VD: Nút Start không hoạt động / Thêm tính năng pause / Snake đi quá nhanh",
            height=100,
            key="feedback_text",
            label_visibility="collapsed",
        )
    with btn_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        sua_lai = st.button(
            "🔄 Team sửa lại",
            type="primary",
            key="btn_sua_lai",
            disabled=not api_key,
            use_container_width=True,
        )

    if sua_lai and not feedback_text:
        st.warning("⚠️ Vui lòng nhập phản hồi!")

    elif sua_lai and feedback_text and api_key:
        st.session_state.is_running = True
        st.markdown("---")
        st.markdown("### 🔧 Developer đang đọc phản hồi và sửa...")

        rev_prog = st.progress(0)
        rev_stat = st.empty()
        rev_tl   = st.empty()
        rev_log  = st.empty()
        rlogs    = []

        def _radd(msg):
            rlogs.append(msg)
            rev_log.markdown(
                '<div class="log-box">' + "<br>".join(rlogs[-10:]) + "</div>",
                unsafe_allow_html=True,
            )

        _REV_TL_DONE = (
            '<div class="agent-timeline">'
            '<div class="agent-row"><span class="ar-emoji">💻</span>'
            '<span class="ar-name">Lập Trình Viên</span>'
            '<span class="ar-status ar-done">✅ Xong</span></div>'
            '<div class="agent-row"><span class="ar-emoji">🔍</span>'
            '<span class="ar-name">Kiểm Duyệt</span>'
            '<span class="ar-status ar-done">✅ Xong</span></div>'
            '<div class="agent-row"><span class="ar-emoji">👑</span>'
            '<span class="ar-name">Trưởng Nhóm</span>'
            '<span class="ar-status ar-done">✅ Xong</span></div>'
            '</div>'
        )

        try:
            rev_stat.markdown("⚙️ Khởi tạo team sửa lỗi...")
            rev_prog.progress(10)
            _radd("✅ Developer, Reviewer, Team Lead đã online")
            _radd(f"📋 Task gốc: {str(st.session_state.last_task)[:60]}...")
            _radd(f"💬 Phản hồi: {feedback_text[:60]}...")

            rev_prog.progress(25)
            rev_stat.markdown("🔧 Developer đang sửa code...")
            rev_tl.markdown(
                '<div class="agent-timeline">'
                '<div class="agent-row"><span class="ar-emoji">💻</span>'
                '<span class="ar-name">Lập Trình Viên</span>'
                '<span class="ar-status ar-active">⏳ Đang sửa...</span></div>'
                '<div class="agent-row"><span class="ar-emoji">🔍</span>'
                '<span class="ar-name">Kiểm Duyệt</span>'
                '<span class="ar-status ar-waiting">─ Chờ</span></div>'
                '<div class="agent-row"><span class="ar-emoji">👑</span>'
                '<span class="ar-name">Trưởng Nhóm</span>'
                '<span class="ar-status ar-waiting">─ Chờ</span></div>'
                '</div>',
                unsafe_allow_html=True,
            )

            rev_result = run_revision_workflow(
                prev_task=st.session_state.last_task or "",
                prev_code=st.session_state.last_code or "",
                code_type=st.session_state.last_code_type or "html",
                feedback=feedback_text,
                api_key=api_key,
                model=selected_model,
            )

            if rev_result["error"]:
                raise RuntimeError(rev_result["error"])

            rev_prog.progress(100)
            rev_stat.markdown("✅ **Sửa xong!**")
            rev_tl.markdown(_REV_TL_DONE, unsafe_allow_html=True)
            _radd("✅ Sửa lỗi hoàn thành!")

            extracted = extract_code(rev_result["result_text"], rev_result["dev_raw"])
            new_html  = extracted["html"]
            new_py    = extracted["python"]
            new_type  = extracted["code_type"] or st.session_state.last_code_type

            os.makedirs("output", exist_ok=True)
            if new_html:
                open("output/result.html", "w", encoding="utf-8").write(new_html)
            elif new_py:
                open("output/result.py",   "w", encoding="utf-8").write(new_py)

            new_rev = st.session_state.get("revision_count", 0) + 1
            st.session_state.last_result    = rev_result["result_text"]
            st.session_state.last_code      = new_html or new_py
            st.session_state.last_code_type = new_type
            st.session_state.revision_count = new_rev
            update_latest_revision(new_rev, new_html or new_py, new_type, rev_result["result_text"])

            st.markdown("---")
            _render_result(rev_result["result_text"], new_html, new_py,
                           st.session_state.last_task or "", new_rev)

        except Exception as e:
            st.error(f"❌ Lỗi khi sửa: {str(e)[:300]}")
            _radd(f"❌ Lỗi: {str(e)}")

        finally:
            st.session_state.is_running = False

# ─────────────────────────────────────────
# DEMO GAME
# ─────────────────────────────────────────
render_tetris_demo()

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#4a5568;font-size:0.8em'>"
    "⚡ ReCrew · AI Software Team · Powered by Google Gemini & CrewAI"
    "</p>",
    unsafe_allow_html=True,
)

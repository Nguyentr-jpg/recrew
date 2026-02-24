import streamlit as st
import os
import re
from crewai import Crew, Task, LLM
from agents import (
    create_team_lead,
    create_developer,
    create_reviewer,
    create_qa_tester,
    create_researcher
)

# ─────────────────────────────────────────
# CẤU HÌNH TRANG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ReCrew - AI Team",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CSS CUSTOM
# ─────────────────────────────────────────
st.markdown("""
<style>
    /* Nền tối */
    .stApp { background-color: #0f1117; }

    /* Header */
    .recrew-header {
        text-align: center;
        padding: 30px 0 10px 0;
    }
    .recrew-title {
        font-size: 3em;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .recrew-subtitle {
        color: #888;
        font-size: 1em;
        margin-top: 5px;
    }

    /* Agent cards */
    .agent-card {
        background: #1a1d27;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s;
    }
    .agent-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    .agent-emoji { font-size: 2em; }
    .agent-name {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.9em;
        margin: 8px 0 4px 0;
    }
    .agent-role {
        color: #718096;
        font-size: 0.75em;
    }
    .status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .online  { background: #48bb78; box-shadow: 0 0 6px #48bb78; }
    .working { background: #ed8936; box-shadow: 0 0 6px #ed8936; animation: pulse 1s infinite; }
    .idle    { background: #718096; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.4; }
    }

    /* Task box */
    .stTextArea textarea {
        background: #1a1d27 !important;
        color: #e2e8f0 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 10px !important;
        font-size: 1em !important;
    }
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }

    /* Nút chạy */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px;
        font-size: 1.1em;
        font-weight: 700;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* Log box */
    .log-box {
        background: #1a1d27;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 16px;
        font-family: monospace;
        font-size: 0.85em;
        color: #a0aec0;
        max-height: 300px;
        overflow-y: auto;
    }

    /* Kết quả */
    .result-box {
        background: #1a1d27;
        border: 1px solid #48bb78;
        border-radius: 10px;
        padding: 20px;
        color: #e2e8f0;
    }

    /* Input sidebar */
    .stTextInput input {
        background: #1a1d27 !important;
        color: #e2e8f0 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 8px !important;
    }

    /* Ẩn Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR - API KEY
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Cài đặt")
    st.markdown("---")

    api_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        placeholder="AIzaSy...",
        help="Lấy miễn phí tại aistudio.google.com"
    )

    if api_key:
        st.success("✅ API Key đã nhập")
    else:
        st.warning("⚠️ Cần nhập API Key để chạy")
        st.markdown("[Lấy API Key miễn phí →](https://aistudio.google.com)", unsafe_allow_html=False)

    st.markdown("---")
    st.markdown("### 📊 Thống kê")
    if "task_count" not in st.session_state:
        st.session_state.task_count = 0
    st.metric("Task đã xử lý", st.session_state.task_count)

    st.markdown("---")
    st.markdown("### 🤖 Chọn Model")
    selected_model = st.selectbox(
        "Gemini Model",
        options=[
            "gemini/gemini-2.5-flash",
            "gemini/gemini-2.5-flash-lite",
            "gemini/gemini-2.5-pro",
        ],
        index=0,
        help="Nếu bị lỗi 429 (quota exceeded), thử đổi sang model khác"
    )

    st.markdown("---")
    st.markdown("### ℹ️ Về ReCrew")
    st.markdown("""
    Team AI tự động làm việc với nhau để hoàn thành task phần mềm.

    **Powered by:**
    - Google Gemini 2.5 Flash
    - CrewAI Framework
    """)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="recrew-header">
    <p class="recrew-title">⚡ ReCrew</p>
    <p class="recrew-subtitle">AI Software Development Team · Tự động hóa quy trình phát triển phần mềm</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────
# HIỂN THỊ TEAM
# ─────────────────────────────────────────
st.markdown("### 👥 Team Members")

team_members = [
    ("👑", "Trưởng Nhóm",       "Lên kế hoạch & tổng hợp"),
    ("💻", "Lập Trình Viên",    "Viết code Python"),
    ("🔍", "Kiểm Duyệt Code",   "Review & tìm bug"),
    ("🧪", "QA Tester",         "Viết & chạy test case"),
    ("🔎", "Nhà Nghiên Cứu",    "Tìm tài liệu & giải pháp"),
]

cols = st.columns(5)
for i, (emoji, name, role) in enumerate(team_members):
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
        label="Mô tả task",
        placeholder=(
            "Ví dụ: Tạo một script Python đọc file CSV và tính tổng doanh thu theo tháng...\n"
            "Hoặc: Viết API đơn giản bằng FastAPI có chức năng quản lý danh sách công việc..."
        ),
        height=130,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    goi_y = st.button("💡 Gợi ý task")
    chay = st.button("🚀 Chạy Team", type="primary", disabled=not api_key)

# Gợi ý task nhanh
if goi_y:
    st.info("""
**💡 Gợi ý task:**
- Viết script Python tự động đổi tên hàng loạt file
- Tạo chatbot đơn giản trả lời câu hỏi từ file text
- Viết tool kiểm tra tốc độ kết nối internet mỗi giờ
- Tạo API quản lý danh sách sản phẩm với FastAPI
- Viết script gửi email tự động từ file Excel
    """)

# ─────────────────────────────────────────
# HELPER: trích xuất game HTML từ kết quả
# ─────────────────────────────────────────
def _extract_game_html(result_text: str):
    """
    Tìm code block JavaScript/HTML trong kết quả.
    Nếu là Phaser game → wrap thành HTML hoàn chỉnh để chạy trong iframe.
    Trả về HTML string hoặc None nếu không phát hiện.
    """
    # Tìm tất cả code block javascript / js
    js_blocks = re.findall(r'```(?:javascript|js)\n(.*?)\n```', result_text, re.DOTALL)
    # Tìm code block html
    html_blocks = re.findall(r'```html\n(.*?)\n```', result_text, re.DOTALL)

    if html_blocks:
        # Nếu có sẵn HTML hoàn chỉnh, dùng luôn
        full_html = html_blocks[0]
        if '<html' in full_html.lower() or '<!doctype' in full_html.lower():
            return full_html
        # Nếu chỉ là đoạn HTML, bọc lại
        return f"<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body>{full_html}</body></html>"

    if js_blocks:
        js_code = '\n\n'.join(js_blocks)
        # Chỉ tạo Phaser wrapper nếu code dùng Phaser
        if 'Phaser' in js_code or 'phaser' in js_code.lower():
            return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Game Preview</title>
  <script src="https://cdn.jsdelivr.net/npm/phaser@3/dist/phaser.min.js"></script>
  <style>
    body {{ margin:0; background:#111; display:flex; justify-content:center; align-items:center; height:100vh; }}
    canvas {{ display:block; }}
  </style>
</head>
<body>
  <div id="phaser-game"></div>
  <script>
{js_code}
  </script>
</body>
</html>"""
        # JS thuần (không phải Phaser) – wrap đơn giản
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Preview</title>
<style>body{{margin:0;background:#111;color:#eee;font-family:monospace;}}</style>
</head>
<body><canvas id='gameCanvas'></canvas>
<script>
{js_code}
</script>
</body>
</html>"""
    return None


# ─────────────────────────────────────────
# CHẠY TEAM
# ─────────────────────────────────────────
if chay and task_input and api_key:
    st.session_state.is_running = True
    st.session_state.task_count += 1

    st.markdown("---")
    st.markdown("### 🏃 Team đang làm việc...")

    # Progress bar
    progress_bar = st.progress(0)
    status_text  = st.empty()

    # Log area
    log_container = st.empty()
    logs = []

    def add_log(msg):
        logs.append(msg)
        log_container.markdown(
            f'<div class="log-box">' +
            "<br>".join(logs[-20:]) +
            '</div>',
            unsafe_allow_html=True
        )

    try:
        # Khởi tạo LLM
        status_text.markdown("⚙️ Khởi tạo AI model...")
        progress_bar.progress(5)
        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GOOGLE_API_KEY"] = api_key
        llm = LLM(
            model=selected_model,
            api_key=api_key
        )

        # Tạo agents
        status_text.markdown("👥 Tập hợp team...")
        progress_bar.progress(10)
        add_log("✅ Team Lead đã online")
        add_log("✅ Lập Trình Viên đã online")
        add_log("✅ Kiểm Duyệt đã online")
        add_log("✅ QA Tester đã online")
        add_log("✅ Nhà Nghiên Cứu đã online")

        team_lead  = create_team_lead(llm)
        developer  = create_developer(llm)
        reviewer   = create_reviewer(llm)
        qa_tester  = create_qa_tester(llm)
        researcher = create_researcher(llm)

        task_nghien_cuu = Task(
            description=f"""
            Nghiên cứu và đề xuất giải pháp kỹ thuật tốt nhất cho yêu cầu:
            {task_input}
            Đề xuất: công nghệ/thư viện nên dùng, kiến trúc, lưu ý quan trọng.
            """,
            expected_output="Báo cáo nghiên cứu kỹ thuật chi tiết với khuyến nghị cụ thể",
            agent=researcher
        )

        task_lap_trinh = Task(
            description=f"""
            Dựa trên nghiên cứu, viết code Python hoàn chỉnh cho: {task_input}
            Yêu cầu: chạy được, có comment, xử lý lỗi cơ bản, code sạch.
            """,
            expected_output="Code Python hoàn chỉnh kèm hướng dẫn sử dụng",
            agent=developer,
            context=[task_nghien_cuu]
        )

        task_review = Task(
            description="Review code: tìm bug, lỗ hổng bảo mật, đề xuất cải thiện cụ thể.",
            expected_output="Báo cáo review với danh sách vấn đề và đề xuất",
            agent=reviewer,
            context=[task_lap_trinh]
        )

        task_test = Task(
            description="Viết test case: trường hợp bình thường, edge case, trường hợp lỗi.",
            expected_output="Danh sách test case đầy đủ với kết quả dự kiến",
            agent=qa_tester,
            context=[task_lap_trinh, task_review]
        )

        task_tong_hop = Task(
            description="""
            Tổng hợp kết quả team thành báo cáo cuối:
            1. Tóm tắt giải pháp
            2. Code hoàn chỉnh
            3. Hướng dẫn sử dụng từng bước
            4. Danh sách test case
            5. Điểm cần lưu ý
            """,
            expected_output="Báo cáo tổng hợp hoàn chỉnh",
            agent=team_lead,
            context=[task_nghien_cuu, task_lap_trinh, task_review, task_test]
        )

        # Nhãn hiển thị khi mỗi task hoàn thành và bước tiếp theo
        _done_labels = [
            "✅ Nhà Nghiên Cứu hoàn thành nghiên cứu",
            "✅ Lập Trình Viên hoàn thành viết code",
            "✅ Kiểm Duyệt hoàn thành review",
            "✅ QA Tester hoàn thành test case",
            "✅ Trưởng Nhóm hoàn thành tổng hợp",
        ]
        _next_steps = [
            (40, "💻 Lập Trình Viên đang viết code..."),
            (60, "🔍 Kiểm Duyệt đang review code..."),
            (80, "🧪 QA Tester đang viết test case..."),
            (95, "👑 Trưởng Nhóm đang tổng hợp kết quả..."),
        ]
        _step = [0]  # list để closure có thể ghi

        def on_task_complete(task_output):
            idx = _step[0]
            if idx < len(_done_labels):
                add_log(_done_labels[idx])
            if idx < len(_next_steps):
                pct, msg = _next_steps[idx]
                progress_bar.progress(pct)
                status_text.markdown(f"**{msg}**")
                add_log(msg)
            _step[0] += 1

        crew = Crew(
            agents=[researcher, developer, reviewer, qa_tester, team_lead],
            tasks=[task_nghien_cuu, task_lap_trinh, task_review, task_test, task_tong_hop],
            verbose=False,
            task_callback=on_task_complete,
        )

        # Hiện trạng thái bước 1 trước khi chạy
        progress_bar.progress(15)
        status_text.markdown("**🔎 Nhà Nghiên Cứu đang nghiên cứu...**")
        add_log("─" * 40)
        add_log("🔎 Nhà Nghiên Cứu bắt đầu nghiên cứu...")

        ket_qua = crew.kickoff()

        progress_bar.progress(100)
        status_text.markdown("✅ **Hoàn thành!**")
        add_log("─" * 40)
        add_log("✅ Team hoàn thành task!")

        # Lưu file
        os.makedirs("output", exist_ok=True)
        with open("output/ket_qua.md", "w", encoding="utf-8") as out:
            out.write(f"# Kết quả ReCrew\n\n**Task:** {task_input}\n\n---\n\n{ket_qua}")

        # Hiển thị kết quả
        st.markdown("---")
        st.markdown("### ✅ Kết quả")

        result_text = str(ket_qua)
        game_html = _extract_game_html(result_text)

        if game_html:
            tab_result, tab_game, tab_download = st.tabs(
                ["📄 Kết quả đầy đủ", "🎮 Chạy Game", "💾 Tải về"]
            )
            with tab_game:
                st.info("💡 Nhấn vào canvas rồi dùng bàn phím để chơi. Game chạy trực tiếp trong trình duyệt.")
                import streamlit.components.v1 as components
                components.html(game_html, height=650, scrolling=False)
        else:
            tab_result, tab_download = st.tabs(["📄 Kết quả đầy đủ", "💾 Tải về"])

        with tab_result:
            st.markdown(result_text)

        with tab_download:
            st.download_button(
                label="⬇️ Tải kết quả (.md)",
                data=f"# Kết quả ReCrew\n\n**Task:** {task_input}\n\n---\n\n{ket_qua}",
                file_name="recrew_ket_qua.md",
                mime="text/markdown"
            )
            st.success("✅ File cũng đã lưu tại: `output/ket_qua.md`")

    except Exception as e:
        err_msg = str(e)
        if "404" in err_msg or "not found" in err_msg.lower():
            st.error(
                "❌ **Lỗi 404 - Model không tồn tại**\n\n"
                "Model bạn chọn không được hỗ trợ. Hãy đổi sang model khác ở sidebar.\n\n"
                f"Chi tiết: `{err_msg[:200]}`"
            )
        elif "429" in err_msg or "quota" in err_msg.lower() or "rate limit" in err_msg.lower():
            st.error(
                "❌ **Lỗi 429 - Vượt quota API (Rate Limit)**\n\n"
                "Bạn đã dùng hết quota miễn phí của Google Gemini. Hãy thử:\n"
                "1. **Đổi model** ở sidebar sang `gemini-2.5-flash-lite`\n"
                "2. **Chờ một lúc** rồi thử lại (quota reset theo phút/ngày)\n"
                "3. **Nâng cấp** Google AI Studio lên gói có billing\n\n"
                f"Chi tiết: `{err_msg[:200]}`"
            )
        else:
            st.error(f"❌ Lỗi: {err_msg}")
        add_log(f"❌ Lỗi: {err_msg}")

    finally:
        st.session_state.is_running = False

elif chay and not task_input:
    st.warning("⚠️ Vui lòng nhập task trước khi chạy!")
elif chay and not api_key:
    st.error("❌ Vui lòng nhập API Key ở thanh bên trái!")

# ─────────────────────────────────────────
# DEMO GAME
# ─────────────────────────────────────────
import streamlit.components.v1 as _components

_TETRIS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "games", "tetris.html")

st.markdown("---")
st.markdown("### 🎮 Tetris Demo")
st.caption("Nhấn vào canvas → dùng bàn phím: ← → di chuyển | ↓ soft drop | Space hard drop | X/C xoay phải | Z xoay trái | H giữ | P pause | R restart")
if os.path.exists(_TETRIS_PATH):
    _tetris_html = open(_TETRIS_PATH, encoding="utf-8").read()
    _components.html(_tetris_html, height=720, scrolling=False)
else:
    st.error(f"Không tìm thấy file game tại: {_TETRIS_PATH}")

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#4a5568;font-size:0.8em'>"
    "⚡ ReCrew · AI Software Team · Powered by Google Gemini & CrewAI"
    "</p>",
    unsafe_allow_html=True
)

import streamlit as st
import streamlit.components.v1 as components
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

    /* Ẩn branding Streamlit – KHÔNG ẩn header/toolbar vì chứa sidebar toggle */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# FLOATING SIDEBAR TOGGLE BUTTON (JS)
# Dùng JS inject thay vì CSS selector để không phụ thuộc Streamlit version
# ─────────────────────────────────────────
components.html("""
<script>
(function() {
    function addToggleBtn() {
        var pd = window.parent ? window.parent.document : document;
        if (pd.getElementById('recrew-sidebar-toggle')) return;

        var btn = pd.createElement('button');
        btn.id = 'recrew-sidebar-toggle';
        btn.title = 'Mở / Đóng Cài đặt';
        btn.innerHTML = '&#9776;';
        btn.style.cssText = [
            'position:fixed', 'top:50%', 'left:0',
            'transform:translateY(-50%)',
            'z-index:99999',
            'background:linear-gradient(135deg,#667eea,#764ba2)',
            'color:white', 'border:none',
            'border-radius:0 12px 12px 0',
            'width:36px', 'height:72px',
            'font-size:20px', 'cursor:pointer',
            'box-shadow:3px 0 18px rgba(102,126,234,0.7)',
            'transition:width 0.15s ease',
            'display:flex', 'align-items:center', 'justify-content:center'
        ].join(';');

        btn.onmouseenter = function(){ btn.style.width='48px'; };
        btn.onmouseleave = function(){ btn.style.width='36px'; };

        btn.onclick = function() {
            // Thử tất cả selector có thể của Streamlit sidebar toggle
            var selectors = [
                'button[aria-label="Open sidebar"]',
                'button[aria-label="Close sidebar"]',
                'button[aria-label="open sidebar"]',
                'button[aria-label="close sidebar"]',
                '[data-testid="collapsedControl"] button',
                '[data-testid="stSidebarCollapseButton"] button',
                '[data-testid="stSidebar"] button',
            ];
            for (var i = 0; i < selectors.length; i++) {
                var el = pd.querySelector(selectors[i]);
                if (el) { el.click(); return; }
            }
        };

        pd.body.appendChild(btn);
    }

    // Thử inject ngay + retry sau vài giây (Streamlit load chậm)
    addToggleBtn();
    [300, 800, 1500, 3000].forEach(function(t) {
        setTimeout(addToggleBtn, t);
    });
})();
</script>
""", height=0)

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
# DEMO GAME  (inline – không phụ thuộc file ngoài)
# ─────────────────────────────────────────
import streamlit.components.v1 as _components

_TETRIS_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Tetris – ReCrew</title>
  <script src="https://cdn.jsdelivr.net/npm/phaser@3/dist/phaser.min.js"></script>
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{background:#0f1117;display:flex;flex-direction:column;align-items:center;
         font-family:'Segoe UI',sans-serif;color:#e2e8f0}
    h1{margin:14px 0 3px;font-size:1.6em;background:linear-gradient(135deg,#667eea,#764ba2);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent}
    #controls{margin-bottom:8px;font-size:0.78em;color:#718096;text-align:center}
    #ui-panel{display:flex;gap:20px;align-items:flex-start}
    #score-panel{background:#1a1d27;border:1px solid #2d3748;border-radius:10px;padding:14px 18px;min-width:120px}
    .sl{color:#718096;font-size:0.72em;text-transform:uppercase;letter-spacing:1px}
    .sv{font-size:1.5em;font-weight:700;color:#e2e8f0;margin-bottom:10px}
  </style>
</head>
<body>
  <h1>⚡ Tetris – ReCrew</h1>
  <div id="controls">← → Di chuyển &nbsp;|&nbsp; ↓ Soft drop &nbsp;|&nbsp; Space Hard drop
    &nbsp;|&nbsp; X/C Xoay phải &nbsp;|&nbsp; Z Xoay trái &nbsp;|&nbsp; H Giữ &nbsp;|&nbsp; P Pause &nbsp;|&nbsp; R Restart</div>
  <div id="ui-panel">
    <div id="score-panel">
      <div class="sl">Điểm</div><div class="sv" id="current-score">0</div>
      <div class="sl">Cấp độ</div><div class="sv" id="current-level">1</div>
      <div class="sl">Hàng</div><div class="sv" id="current-lines">0</div>
    </div>
    <div id="phaser-game"></div>
  </div>
<script>
class Tetromino{constructor(scene,x,y,type,shape,color){this.scene=scene;this.type=type;this.color=color;this.originalShape=shape;this.currentShape=JSON.parse(JSON.stringify(shape));this.x=x;this.y=y;this.graphics=null;this.initGraphics()}initGraphics(){this.graphics=this.scene.add.graphics();this.graphics.setDepth(1);this.draw()}draw(){this.graphics.clear();this.graphics.setX(GameBoard.OX+this.x*GameBoard.GS);this.graphics.setY(GameBoard.OY+this.y*GameBoard.GS);this.graphics.fillStyle(this.color,1);for(let r=0;r<this.currentShape.length;r++)for(let c=0;c<this.currentShape[r].length;c++)if(this.currentShape[r][c]===1){this.graphics.fillRect(c*GameBoard.GS,r*GameBoard.GS,GameBoard.GS-1,GameBoard.GS-1);this.graphics.lineStyle(1,0xffffff,0.18);this.graphics.strokeRect(c*GameBoard.GS,r*GameBoard.GS,GameBoard.GS-1,GameBoard.GS-1)}}move(dx,dy){this.x+=dx;this.y+=dy;this.graphics.setX(GameBoard.OX+this.x*GameBoard.GS);this.graphics.setY(GameBoard.OY+this.y*GameBoard.GS)}rotateClockwise(){const s=this.currentShape,N=s.length;for(let i=0;i<N;i++)for(let j=i;j<N;j++)[s[i][j],s[j][i]]=[s[j][i],s[i][j]];for(let i=0;i<N;i++)s[i].reverse();this.draw()}rotateCounterClockwise(){const s=this.currentShape,N=s.length;s.reverse();for(let i=0;i<N;i++)for(let j=i;j<N;j++)[s[i][j],s[j][i]]=[s[j][i],s[i][j]];this.draw()}setShape(ns){this.currentShape=ns;this.draw()}getBlocks(){const b=[];for(let r=0;r<this.currentShape.length;r++)for(let c=0;c<this.currentShape[r].length;c++)if(this.currentShape[r][c]===1)b.push({x:this.x+c,y:this.y+r});return b}getColor(){return this.color}getType(){return this.type}destroy(){if(this.graphics){this.graphics.destroy();this.graphics=null}}}
class GameBoard{static BW=10;static BH=20;static GS=28;static OX=0;static OY=0;static PIECES={'I':{shape:[[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],color:0x00ffff},'J':{shape:[[1,0,0],[1,1,1],[0,0,0]],color:0x3399ff},'L':{shape:[[0,0,1],[1,1,1],[0,0,0]],color:0xffa500},'O':{shape:[[1,1],[1,1]],color:0xffff00},'S':{shape:[[0,1,1],[1,1,0],[0,0,0]],color:0x44dd44},'T':{shape:[[0,1,0],[1,1,1],[0,0,0]],color:0xcc44cc},'Z':{shape:[[1,1,0],[0,1,1],[0,0,0]],color:0xff4444}};static _bag=[];static _fill(){GameBoard._bag=Object.keys(GameBoard.PIECES);for(let i=GameBoard._bag.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[GameBoard._bag[i],GameBoard._bag[j]]=[GameBoard._bag[j],GameBoard._bag[i]]}}static next(){if(!GameBoard._bag.length)GameBoard._fill();return GameBoard._bag.pop()}constructor(scene){this.scene=scene;this.grid=Array(GameBoard.BH).fill(0).map(()=>Array(GameBoard.BW).fill(0));this.lg=[];this.cur=null;this.nxt=GameBoard.next();this.hold=null;this.canHold=true;this.sm=new ScoreManager}initBoard(x,y){GameBoard.OX=x;GameBoard.OY=y;const g=this.scene.add.graphics();g.fillStyle(0x000000,0.6);g.fillRect(x,y,GameBoard.BW*GameBoard.GS,GameBoard.BH*GameBoard.GS);g.lineStyle(1,0x2d3748,1);for(let i=0;i<=GameBoard.BW;i++){g.moveTo(x+i*GameBoard.GS,y);g.lineTo(x+i*GameBoard.GS,y+GameBoard.BH*GameBoard.GS)}for(let i=0;i<=GameBoard.BH;i++){g.moveTo(x,y+i*GameBoard.GS);g.lineTo(x+GameBoard.BW*GameBoard.GS,y+i*GameBoard.GS)}g.strokePath();g.setDepth(0)}spawn(){const type=this.nxt;this.nxt=GameBoard.next();const d=GameBoard.PIECES[type];const sx=Math.floor((GameBoard.BW-d.shape[0].length)/2);this.cur=new Tetromino(this.scene,sx,0,type,d.shape,d.color);if(this.collide(this.cur)){this.cur.destroy();this.cur=null;return null}this.canHold=true;return this.cur}getCur(){return this.cur}collide(t){for(const{x,y}of t.getBlocks()){if(x<0||x>=GameBoard.BW||y>=GameBoard.BH)return true;if(y>=0&&this.grid[y][x]!==0)return true}return false}tryMove(dx,dy){if(!this.cur)return false;this.cur.move(dx,dy);if(this.collide(this.cur)){this.cur.move(-dx,-dy);return false}return true}_kick(t){const ox=t.x,oy=t.y;for(const{dx,dy}of[{dx:1,dy:0},{dx:-1,dy:0},{dx:2,dy:0},{dx:-2,dy:0},{dx:0,dy:-1}]){t.x=ox+dx;t.y=oy+dy;if(!this.collide(t)){t.draw();return true}}t.x=ox;t.y=oy;return false}rotCW(){if(!this.cur)return false;const ss=JSON.parse(JSON.stringify(this.cur.currentShape)),sx=this.cur.x,sy=this.cur.y;this.cur.rotateClockwise();if(this.collide(this.cur)&&!this._kick(this.cur)){this.cur.x=sx;this.cur.y=sy;this.cur.setShape(ss);return false}return true}rotCCW(){if(!this.cur)return false;const ss=JSON.parse(JSON.stringify(this.cur.currentShape)),sx=this.cur.x,sy=this.cur.y;this.cur.rotateCounterClockwise();if(this.collide(this.cur)&&!this._kick(this.cur)){this.cur.x=sx;this.cur.y=sy;this.cur.setShape(ss);return false}return true}hardDrop(){let n=0;while(this.tryMove(0,1))n++;return n}lock(){if(!this.cur)return 0;for(const{x,y}of this.cur.getBlocks())if(y>=0)this.grid[y][x]=this.cur.getColor();this.cur.destroy();this.cur=null;const c=this._clear();this.sm.addLines(c);this.redraw();return c}_clear(){let n=0;for(let y=GameBoard.BH-1;y>=0;y--){if(this.grid[y].every(c=>c!==0)){this.grid.splice(y,1);this.grid.unshift(Array(GameBoard.BW).fill(0));n++;y++}}return n}redraw(){this.lg.forEach(g=>g.destroy());this.lg=[];for(let y=0;y<GameBoard.BH;y++)for(let x=0;x<GameBoard.BW;x++){const color=this.grid[y][x];if(color!==0){const g=this.scene.add.graphics();g.setX(GameBoard.OX+x*GameBoard.GS);g.setY(GameBoard.OY+y*GameBoard.GS);g.fillStyle(color,1);g.fillRect(0,0,GameBoard.GS-1,GameBoard.GS-1);g.lineStyle(1,0xffffff,0.12);g.strokeRect(0,0,GameBoard.GS-1,GameBoard.GS-1);g.setDepth(0);this.lg.push(g)}}}holdPiece(){if(!this.cur||!this.canHold)return;const ct=this.cur.getType();this.cur.destroy();this.cur=null;if(this.hold){const ht=this.hold;this.hold=ct;const d=GameBoard.PIECES[ht];const sx=Math.floor((GameBoard.BW-d.shape[0].length)/2);this.cur=new Tetromino(this.scene,sx,0,ht,d.shape,d.color);if(this.collide(this.cur)){this.cur.destroy();this.cur=null}}else{this.hold=ct;this.spawn()}this.canHold=false}getNxt(){return this.nxt}getHold(){return this.hold}reset(){this.grid=Array(GameBoard.BH).fill(0).map(()=>Array(GameBoard.BW).fill(0));this.lg.forEach(g=>g.destroy());this.lg=[];if(this.cur){this.cur.destroy();this.cur=null}this.nxt=GameBoard.next();this.hold=null;this.canHold=true;this.sm.reset();GameBoard._bag=[]}}
class ScoreManager{constructor(){this.reset()}reset(){this.score=0;this.level=1;this.lines=0}addLines(n){if(!n)return;this.lines+=n;this.level=Math.floor(this.lines/10)+1;const p=[0,40,100,300,1200];this.score+=(p[n]||1200)*this.level}getScore(){return this.score}getLevel(){return this.level}getLines(){return this.lines}}
class BootScene extends Phaser.Scene{constructor(){super({key:'BootScene'})}create(){this.scene.start('GameScene')}}
class GameScene extends Phaser.Scene{constructor(){super({key:'GameScene'});this.board=null;this.isPaused=false;this.isGameOver=false;this.fallTimer=null;this.ghost=null}create(){this.isPaused=false;this.isGameOver=false;const W=this.sys.game.config.width,H=this.sys.game.config.height;const bw=GameBoard.BW*GameBoard.GS,bh=GameBoard.BH*GameBoard.GS;const bx=(W-bw)/2,by=(H-bh)/2;this.board=new GameBoard(this);this.board.initBoard(bx,by);this.ghost=this.add.graphics();this.ghost.setDepth(0);if(!this.board.spawn()){this._gameOver();return}this._input();this._startTimer();this._updateUI();this.add.text(bx+bw+12,by,'NEXT',{fontSize:'12px',fill:'#718096'});this.add.text(bx+bw+12,by+90,'HOLD',{fontSize:'12px',fill:'#718096'});this.nxtTxt=this.add.text(bx+bw+12,by+16,'',{fontSize:'12px',fill:'#e2e8f0'});this.holdTxt=this.add.text(bx+bw+12,by+106,'',{fontSize:'12px',fill:'#e2e8f0'});this.pauseTxt=null}_input(){const kb=this.input.keyboard,cur=kb.createCursorKeys();const K={x:kb.addKey('X'),z:kb.addKey('Z'),c:kb.addKey('C'),p:kb.addKey('P'),h:kb.addKey('H'),r:kb.addKey('R'),sp:kb.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE)};const ok=()=>!this.isPaused&&!this.isGameOver&&!!this.board.getCur();cur.left.on('down',()=>{if(ok())this.board.tryMove(-1,0)});cur.right.on('down',()=>{if(ok())this.board.tryMove(1,0)});cur.down.on('down',()=>{if(!ok())return;if(!this.board.tryMove(0,1))this._land()});const hd=()=>{if(!ok())return;this.board.hardDrop();this._land()};K.sp.on('down',hd);cur.up.on('down',hd);K.x.on('down',()=>{if(ok())this.board.rotCW()});K.c.on('down',()=>{if(ok())this.board.rotCW()});K.z.on('down',()=>{if(ok())this.board.rotCCW()});K.p.on('down',()=>this._pause());K.h.on('down',()=>{if(!ok())return;this.board.holdPiece();this._startTimer();this._updateUI()});K.r.on('down',()=>{if(this.isGameOver){this.board.reset();this.scene.restart()}})}_calcGhost(){const t=this.board.getCur();if(!t)return null;const oy=t.y;while(true){t.y++;if(this.board.collide(t)){t.y--;break}}const gy=t.y;t.y=oy;return{shape:t.currentShape,x:t.x,y:gy}}_drawGhost(){this.ghost.clear();const g=this._calcGhost();if(!g)return;const t=this.board.getCur();if(g.y===t.y)return;this.ghost.lineStyle(1,0xffffff,0.22);for(let r=0;r<g.shape.length;r++)for(let c=0;c<g.shape[r].length;c++)if(g.shape[r][c]===1){const px=GameBoard.OX+(g.x+c)*GameBoard.GS,py=GameBoard.OY+(g.y+r)*GameBoard.GS;this.ghost.strokeRect(px,py,GameBoard.GS-1,GameBoard.GS-1)}}_startTimer(){if(this.fallTimer)this.fallTimer.remove();const iv=Math.max(80,1000-(this.board.sm.getLevel()-1)*80);this.fallTimer=this.time.addEvent({delay:iv,callback:()=>{if(this.isPaused||this.isGameOver)return;if(!this.board.tryMove(0,1))this._land()},loop:true})}_land(){this.board.lock();const n=this.board.spawn();this._updateUI();if(!n){this._gameOver();return}this._startTimer()}_pause(){if(this.isGameOver)return;this.isPaused=!this.isPaused;if(this.isPaused){this.fallTimer.paused=true;if(!this.pauseTxt)this.pauseTxt=this.add.text(this.sys.game.config.width/2,this.sys.game.config.height/2,'PAUSED\n(P tiếp tục)',{fontSize:'32px',fill:'#fff',align:'center'}).setOrigin(0.5).setDepth(20)}else{this.fallTimer.paused=false;if(this.pauseTxt){this.pauseTxt.destroy();this.pauseTxt=null}}}_gameOver(){this.isGameOver=true;if(this.fallTimer)this.fallTimer.remove();const cx=this.sys.game.config.width/2,cy=this.sys.game.config.height/2;this.add.text(cx,cy-40,'GAME OVER',{fontSize:'48px',fill:'#ff4444',fontStyle:'bold'}).setOrigin(0.5).setDepth(20);this.add.text(cx,cy+20,'Điểm: '+this.board.sm.getScore(),{fontSize:'26px',fill:'#fff'}).setOrigin(0.5).setDepth(20);this.add.text(cx,cy+58,'Nhấn R để chơi lại',{fontSize:'20px',fill:'#a0aec0'}).setOrigin(0.5).setDepth(20)}_updateUI(){const sm=this.board.sm;document.getElementById('current-score').innerText=sm.getScore();document.getElementById('current-level').innerText=sm.getLevel();document.getElementById('current-lines').innerText=sm.getLines();if(this.nxtTxt)this.nxtTxt.setText(this.board.getNxt()||'-');if(this.holdTxt)this.holdTxt.setText(this.board.getHold()||'-')}update(){if(!this.isPaused&&!this.isGameOver)this._drawGhost()}}
new Phaser.Game({type:Phaser.AUTO,width:420,height:600,parent:'phaser-game',backgroundColor:'#0f1117',scene:[BootScene,GameScene]});
</script>
</body>
</html>"""

st.markdown("---")
st.markdown("### 🎮 Tetris Demo")
st.caption("Nhấn vào canvas → ← → di chuyển | ↓ soft drop | Space hard drop | X/C xoay phải | Z xoay trái | H giữ | P pause | R restart")
_components.html(_TETRIS_HTML, height=720, scrolling=False)

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

# ReCrew — Project Roadmap

> File này là định hướng phát triển dự án. Mỗi lần hoàn thành một mục, đánh dấu `[x]`.
> Đọc lại file này trước khi bắt đầu bất kỳ session phát triển nào.

---

## Tổng quan dự án

**ReCrew** là nền tảng tự động hóa lập trình bằng AI team. User nhập yêu cầu bằng ngôn ngữ tự nhiên → 5 AI agent (Researcher, Developer, Reviewer, QA, Team Lead) phối hợp → output là code thực chạy được.

**Tech stack hiện tại:** Python · CrewAI · Google Gemini · Streamlit
**Mục tiêu:** Trở thành công cụ AI coding team tốt nhất cho indie dev / startup nhỏ.

---

## Phase 0 — Dọn nhà (nền móng kỹ thuật)

> Làm trước mọi feature. Không có nền tốt thì xây lên sẽ sụp.

- [x] Tách `app.py` (945 dòng) thành các module riêng biệt:
  - [x] `utils/code_extractor.py` — logic trích xuất HTML/Python từ LLM output
  - [x] `utils/settings.py` — lưu/load API key giữa các phiên
  - [x] `utils/history.py` — quản lý lịch sử task trong session
  - [x] `crew/tasks.py` — định nghĩa task descriptions cho main workflow
  - [x] `crew/runner.py` — build LLM, agents, crew và chạy workflow
  - [x] `ui/styles.py` — CSS tập trung, không rải trong app.py
  - [x] `ui/sidebar.py` — toàn bộ sidebar (API key + history + settings)
- [x] Cập nhật `main.py` — sync với capabilities hiện tại của app.py
- [x] Error recovery — nếu workflow fail, log rõ ràng, không crash toàn bộ app

---

## Phase 1 — User Experience cơ bản

> Những thứ làm user quay lại dùng lần 2, lần 3.

- [x] **API Key persistence** — không phải nhập lại mỗi lần mở app (lưu vào `~/.recrew_settings.json`)
- [x] **Task History sidebar** — xem danh sách task đã làm, click để load lại kết quả
- [x] **Agent status timeline** — hiển thị từng agent đang làm gì thay vì chỉ log text
- [ ] **Inline code editor** — sửa code ngay trong app trước khi gửi review (dùng `streamlit-ace`)
  - Thêm `streamlit-ace` vào requirements.txt
  - Sau khi Developer xong, user có thể edit code trước khi Reviewer chạy
  - Nút "Dùng code này" để tiếp tục workflow với code đã chỉnh

---

## Phase 2 — Core Product Features

> Tạo ra giá trị thực, phân biệt với ChatGPT đơn thuần.

- [ ] **Project Context** — nhóm các task liên quan vào 1 project
  - Mỗi project có tên, tech stack, mô tả chung
  - Developer agent nhận project context → code nhất quán giữa các task
  - Lưu project vào file JSON trong `~/.recrew/projects/`

- [ ] **Multi-file output** — tạo cả folder project, không chỉ 1 file
  - Team Lead tạo danh sách file cần thiết
  - Developer viết từng file
  - Zip lại cho user download
  - Preview cấu trúc thư mục trong app

- [ ] **Inline diff view** — khi revision, show đúng phần nào đã thay đổi
  - So sánh code cũ vs code mới
  - Highlight dòng thêm (xanh) / xóa (đỏ) / sửa (vàng)

- [ ] **Export conversation** — xuất toàn bộ quá trình làm việc của team
  - Format: Markdown với từng agent output
  - Dùng để debug hoặc chia sẻ với người khác

---

## Phase 3 — Differentiation (Khác biệt với đối thủ)

- [ ] **Deploy in 1 click**
  - HTML → deploy lên Netlify/Vercel qua API (không cần account)
  - Python → tạo Dockerfile + docker-compose.yml
  - Hiển thị link live ngay trong app

- [ ] **Template Gallery**
  - Bộ template task phổ biến: Snake game, Tetris, Dashboard, REST API, Telegram bot...
  - User click template → task input được điền sẵn
  - Có preview ảnh kết quả mẫu

- [ ] **Share link**
  - Tạo link unique để chia sẻ kết quả
  - Người nhận mở link thấy code + có thể "Fork về làm của mình"
  - Cần backend nhỏ (FastAPI + SQLite) hoặc dùng Gist API

- [ ] **Multi-LLM support**
  - Thêm OpenAI GPT-4o, Claude Sonnet làm lựa chọn bên cạnh Gemini
  - Fallback tự động nếu 1 provider bị rate limit
  - So sánh kết quả từ nhiều model

---

## Phase 4 — Monetization

- [ ] **User authentication** (email + password, hoặc Google OAuth)
- [ ] **Persistent storage** (SQLite lưu task history, project workspace)
- [ ] **Pricing tiers:**
  - Free: 5 task/ngày, model flash-lite, history 7 ngày
  - Pro ($9/tháng): Unlimited, model pro, history 90 ngày, share link
  - Team ($29/tháng): 5 user, project workspace chung, priority support
- [ ] **Analytics dashboard** — task phổ biến nhất, success rate, model so sánh

---

## Ghi chú kỹ thuật

### Cấu trúc thư mục hiện tại (sau Phase 0)
```
recrew/
├── app.py                 # Entry point Streamlit (slim ~150 dòng)
├── main.py                # Terminal mode
├── ROADMAP.md             # File này
├── requirements.txt
├── README.md
├── agents/                # AI agent definitions
│   ├── __init__.py
│   ├── team_lead.py
│   ├── developer.py
│   ├── reviewer.py
│   ├── qa_tester.py
│   └── researcher.py
├── crew/                  # Crew logic
│   ├── __init__.py
│   ├── tasks.py           # Task descriptions
│   └── runner.py          # Build + run crew
├── utils/                 # Pure utility functions
│   ├── __init__.py
│   ├── code_extractor.py  # Trích xuất HTML/Python từ LLM output
│   ├── settings.py        # API key persistence (~/.recrew_settings.json)
│   └── history.py         # Task history (session_state)
├── ui/                    # UI components
│   ├── __init__.py
│   ├── styles.py          # CSS
│   └── sidebar.py         # Sidebar rendering
├── config/
│   └── .env.example
├── .streamlit/
│   └── config.toml
├── .devcontainer/
│   └── devcontainer.json
├── output/                # Generated files (gitignored)
└── games/                 # Example outputs
```

### Quy tắc phát triển
1. **Module mới phải độc lập** — `utils/` không import từ `ui/` hay `crew/`
2. **Không break existing workflow** — test với 1 task trước khi merge
3. **Comment bằng tiếng Việt** — dễ đọc lại sau này
4. **session_state keys** — list đầy đủ ở `ui/sidebar.py`, initialize 1 chỗ duy nhất

### session_state keys (tập trung)
| Key | Kiểu | Mô tả |
|-----|------|-------|
| `task_count` | int | Số task đã chạy trong session |
| `revision_count` | int | Số lần sửa lại của task hiện tại |
| `is_running` | bool | Đang chạy crew hay không |
| `last_result` | str | Kết quả cuối cùng (markdown) |
| `last_code` | str | Code cuối cùng (HTML hoặc Python) |
| `last_code_type` | str | "html" hoặc "python" |
| `last_task` | str | Mô tả task cuối cùng |
| `history` | list | Danh sách task đã làm (xem utils/history.py) |
| `loaded_history_item` | dict | Item đang được load từ history |

---

*Cập nhật lần cuối: Phase 0 + Phase 1 (API key persistence, Task History, Agent timeline)*

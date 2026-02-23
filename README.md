# ⚡ ReCrew — AI Software Development Team

> **Đội ngũ AI tự động làm việc với nhau để phát triển phần mềm**
> Thay vì thuê nhiều người, bạn có một team AI hoạt động 24/7.

---

## 🎯 Mục tiêu dự án

ReCrew được xây dựng với mục tiêu:

1. **Tạo ra nhiều sản phẩm phần mềm nhanh hơn** mà không cần đội ngũ lập trình lớn
2. **Tự động hoá quy trình phát triển phần mềm** từ nghiên cứu → code → review → test
3. **Làm nền tảng thử nghiệm** trước khi đầu tư vào hệ thống AI lớn hơn
4. **Dần dần mở rộng** — dùng chính team AI này để tạo ra các AI agent mới khác

---

## 👥 Thành viên Team

| Emoji | Vai trò | Nhiệm vụ |
|-------|---------|----------|
| 👑 | **Trưởng Nhóm** | Nhận yêu cầu, lên kế hoạch, phân công, tổng hợp kết quả cuối |
| 💻 | **Lập Trình Viên** | Viết code Python sạch, có comment, xử lý lỗi |
| 🔍 | **Kiểm Duyệt Code** | Review code, tìm bug, lỗ hổng bảo mật, đề xuất cải thiện |
| 🧪 | **QA Tester** | Viết test case, kiểm tra edge case, báo cáo lỗi |
| 🔎 | **Nhà Nghiên Cứu** | Tìm tài liệu, thư viện phù hợp, best practices |

**Quy trình làm việc:**
```
Yêu cầu → Nghiên Cứu → Lập Trình → Review → Test → Tổng Hợp → Kết quả
```

---

## 🛠️ Công nghệ sử dụng

| Công nghệ | Vai trò | Ghi chú |
|-----------|---------|---------|
| **Python 3.13** | Ngôn ngữ lập trình chính | Đã cài sẵn trên máy |
| **CrewAI** | Framework quản lý multi-agent | Điều phối các AI agent làm việc với nhau |
| **Google Gemini 1.5 Flash** | Não của các AI agent | Free tier: 1500 req/ngày |
| **Streamlit** | Giao diện web | Chạy trên trình duyệt, dễ dùng |

---

## 📁 Cấu trúc thư mục

```
ReCrew/
│
├── app.py                  ← 🖥️  Giao diện web (CHẠY CÁI NÀY)
├── main.py                 ← ⌨️  Phiên bản chạy Terminal (backup)
├── README.md               ← 📖  File này
│
├── agents/
│   ├── __init__.py         ← Kết nối tất cả agents
│   ├── team_lead.py        ← 👑 Trưởng Nhóm
│   ├── developer.py        ← 💻 Lập Trình Viên
│   ├── reviewer.py         ← 🔍 Kiểm Duyệt
│   ├── qa_tester.py        ← 🧪 QA Tester
│   └── researcher.py       ← 🔎 Nhà Nghiên Cứu
│
├── config/
│   └── .env.example        ← Mẫu cài API key
│
└── output/
    └── ket_qua.md          ← Kết quả sau mỗi task sẽ lưu ở đây
```

---

## 🚀 Cách chạy

### Yêu cầu trước khi chạy
- [ ] Đã cài Python 3.x
- [ ] Đã có Gemini API Key (miễn phí tại [aistudio.google.com](https://aistudio.google.com))
- [ ] Đã cài thư viện (xem phần Cài đặt bên dưới)

### Cài đặt lần đầu
```bash
# Mở Terminal, chạy lần lượt
pip install crewai crewai-tools
pip install "crewai[google-genai]"
pip install streamlit
```

### Chạy giao diện web (khuyến nghị)
```bash
cd /Users/trannguyen/ReCrew
streamlit run app.py
```
Sau đó mở trình duyệt vào: **http://localhost:8501**

### Chạy bằng Terminal (backup)
```bash
cd /Users/trannguyen/ReCrew
python3 main.py
```

---

## 📋 Cách sử dụng

1. **Mở giao diện** tại `http://localhost:8501`
2. **Nhập API Key** vào ô bên trái sidebar
3. **Nhập task** vào ô lớn ở giữa (mô tả càng chi tiết càng tốt)
4. **Bấm 🚀 Chạy Team**
5. **Chờ team làm việc** — xem tiến độ real-time
6. **Nhận kết quả** — đọc trực tiếp hoặc tải file `.md` về

### Ví dụ task hay dùng
```
Viết script Python đọc file CSV và tính tổng doanh thu theo tháng
Tạo API quản lý sản phẩm bằng FastAPI (thêm/xóa/sửa/tìm)
Viết tool tự động đổi tên hàng loạt file trong thư mục
Tạo chatbot đơn giản trả lời từ file văn bản
Viết script theo dõi giá sản phẩm trên web và gửi thông báo
```

---

## 🔑 API Key

### Lấy key miễn phí
1. Truy cập [aistudio.google.com](https://aistudio.google.com)
2. Đăng nhập bằng Google account
3. Click **"Get API key"** → **"Create API key"**
4. Copy key (dạng `AIzaSy...`)

### Giới hạn free tier
| Model | Requests/ngày | Requests/phút |
|-------|--------------|---------------|
| Gemini 1.5 Flash | 1,500 | 15 |
| Gemini 1.5 Flash 8B | 1,500 | 15 |

> ⚠️ **Lưu ý:** Mỗi task chạy ~5 requests (1 per agent). Tức là chạy được ~300 tasks/ngày miễn phí.

---

## 🗺️ Lộ trình phát triển

### ✅ Giai đoạn 1 — Hoàn thành
- [x] Xây dựng team AI cơ bản (5 agents)
- [x] Giao diện web với Streamlit
- [x] Kết nối Google Gemini miễn phí
- [x] Lưu kết quả tự động

### 🔄 Giai đoạn 2 — Tiếp theo
- [ ] Thêm memory — agents nhớ context giữa các task
- [ ] Thêm tool đọc/ghi file thật cho Developer Agent
- [ ] Thêm tool chạy code thật và báo kết quả
- [ ] Lưu lịch sử task vào database
- [ ] Cho phép chọn agent nào tham gia mỗi task

### 🚀 Giai đoạn 3 — Production
- [ ] Chuyển backend sang FastAPI
- [ ] Giao diện web chuyên nghiệp hơn (Next.js)
- [ ] Deploy lên server (AWS / GCP / DigitalOcean)
- [ ] Chuyển sang Claude API (Anthropic) — mạnh hơn Gemini
- [ ] Hỗ trợ nhiều người dùng cùng lúc
- [ ] Thêm billing, authentication nếu làm SaaS

---

## ⚠️ Lỗi thường gặp

| Lỗi | Nguyên nhân | Cách fix |
|-----|-------------|----------|
| `429 RESOURCE_EXHAUSTED` | Hết quota ngày | Chờ sang ngày hôm sau hoặc nâng cấp API |
| `404 NOT_FOUND` | Sai tên model | Kiểm tra tên model trong `app.py` |
| `ImportError: Google Gen AI` | Thiếu thư viện | Chạy `pip install "crewai[google-genai]"` |
| Trang web không mở | Streamlit chưa chạy | Chạy `streamlit run app.py` trong Terminal |

---

## 📌 Thông tin kỹ thuật

- **Ngày khởi tạo:** 23/02/2026
- **Framework:** CrewAI v1.9.3
- **AI Model hiện tại:** Google Gemini 1.5 Flash (free)
- **AI Model tương lai:** Anthropic Claude (production)
- **Vị trí project:** `/Users/trannguyen/ReCrew`
- **Người tạo:** trannguyen

---

## 💡 Triết lý dự án

> *"Thay vì mày làm từng bước một, hãy để một đội làm song song với nhau.
> Mày chỉ cần nói muốn gì — team sẽ lo phần còn lại."*

ReCrew không chỉ là một tool — đây là **nền tảng** để mày xây dựng ngày càng nhiều AI agent hơn,
tự động hoá ngày càng nhiều công việc hơn, và cuối cùng tạo ra sản phẩm với tốc độ chưa từng có.

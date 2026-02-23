"""
╔══════════════════════════════════════════╗
║           ReCrew - AI Agent Team         ║
║   Team làm phần mềm tự động bằng AI     ║
╚══════════════════════════════════════════╝

Thành viên:
  👑 Trưởng Nhóm  - Nhận task, lên kế hoạch, phân công
  💻 Lập Trình Viên - Viết code
  🔍 Kiểm Duyệt   - Review code, tìm bug
  🧪 QA Tester    - Viết test case
  🔎 Nhà Nghiên Cứu - Tìm tài liệu, giải pháp kỹ thuật
"""

import os
from crewai import Crew, Task, LLM
from agents import (
    create_team_lead,
    create_developer,
    create_reviewer,
    create_qa_tester,
    create_researcher
)

# ─────────────────────────────────────────
# BƯỚC 1: Nhập API key
# ─────────────────────────────────────────
print("\n" + "="*50)
print("  🚀 ReCrew AI Team - Khởi động")
print("="*50)

api_key = input("\n🔑 Dán Gemini API key của mày vào đây: ").strip()
os.environ["GEMINI_API_KEY"] = api_key

# ─────────────────────────────────────────
# BƯỚC 2: Khởi tạo AI model (Gemini)
# ─────────────────────────────────────────
llm = LLM(
    model="gemini-1.5-flash",
    api_key=api_key
)

# ─────────────────────────────────────────
# BƯỚC 3: Tạo team
# ─────────────────────────────────────────
print("\n⚙️  Đang khởi tạo team ReCrew...")

team_lead    = create_team_lead(llm)
developer    = create_developer(llm)
reviewer     = create_reviewer(llm)
qa_tester    = create_qa_tester(llm)
researcher   = create_researcher(llm)

print("✅ Team đã sẵn sàng!\n")
print("  👑 Trưởng Nhóm    - Online")
print("  💻 Lập Trình Viên - Online")
print("  🔍 Kiểm Duyệt     - Online")
print("  🧪 QA Tester      - Online")
print("  🔎 Nhà Nghiên Cứu - Online")

# ─────────────────────────────────────────
# BƯỚC 4: Nhận task từ người dùng
# ─────────────────────────────────────────
print("\n" + "="*50)
yeu_cau = input("\n📋 Nhập task mày muốn team xử lý:\n> ").strip()

# ─────────────────────────────────────────
# BƯỚC 5: Định nghĩa các task theo thứ tự
# ─────────────────────────────────────────

task_nghien_cuu = Task(
    description=f"""
    Nghiên cứu và đề xuất giải pháp kỹ thuật tốt nhất cho yêu cầu sau:
    {yeu_cau}

    Cần đưa ra:
    - Công nghệ/thư viện nên dùng và lý do
    - Kiến trúc đề xuất (nếu có)
    - Những lưu ý quan trọng khi thực hiện
    """,
    expected_output="Báo cáo nghiên cứu kỹ thuật chi tiết với khuyến nghị cụ thể",
    agent=researcher
)

task_lap_trinh = Task(
    description=f"""
    Dựa trên kết quả nghiên cứu, viết code Python hoàn chỉnh cho yêu cầu:
    {yeu_cau}

    Yêu cầu:
    - Code phải chạy được
    - Có comment giải thích rõ ràng
    - Xử lý các trường hợp lỗi cơ bản
    - Code sạch, dễ đọc
    """,
    expected_output="Code Python hoàn chỉnh, có thể chạy được, kèm hướng dẫn sử dụng",
    agent=developer,
    context=[task_nghien_cuu]
)

task_review = Task(
    description="""
    Review toàn bộ code vừa được viết. Kiểm tra:
    - Bug hoặc lỗi logic
    - Vấn đề bảo mật
    - Code có rõ ràng, dễ bảo trì không
    - Có thể tối ưu gì không

    Đưa ra nhận xét cụ thể và đề xuất cải thiện nếu cần.
    """,
    expected_output="Báo cáo review chi tiết với danh sách vấn đề (nếu có) và đề xuất cải thiện",
    agent=reviewer,
    context=[task_lap_trinh]
)

task_test = Task(
    description="""
    Dựa trên code và kết quả review, viết test case toàn diện:
    - Test case cho trường hợp bình thường
    - Test case cho edge case
    - Test case cho trường hợp lỗi/ngoại lệ

    Mỗi test case cần có: mô tả, input, expected output.
    """,
    expected_output="Danh sách test case đầy đủ với kết quả dự kiến",
    agent=qa_tester,
    context=[task_lap_trinh, task_review]
)

task_tong_hop = Task(
    description="""
    Tổng hợp toàn bộ kết quả từ team và tạo báo cáo cuối cùng bao gồm:
    1. Tóm tắt giải pháp
    2. Code hoàn chỉnh đã được review
    3. Hướng dẫn sử dụng (từng bước)
    4. Danh sách test case
    5. Những điểm cần lưu ý hoặc cải thiện trong tương lai
    """,
    expected_output="Báo cáo tổng hợp hoàn chỉnh, sẵn sàng để người dùng sử dụng",
    agent=team_lead,
    context=[task_nghien_cuu, task_lap_trinh, task_review, task_test]
)

# ─────────────────────────────────────────
# BƯỚC 6: Chạy team
# ─────────────────────────────────────────
print("\n" + "="*50)
print("  🏃 Team bắt đầu làm việc...")
print("="*50 + "\n")

crew = Crew(
    agents=[researcher, developer, reviewer, qa_tester, team_lead],
    tasks=[task_nghien_cuu, task_lap_trinh, task_review, task_test, task_tong_hop],
    verbose=True
)

ket_qua = crew.kickoff()

# ─────────────────────────────────────────
# BƯỚC 7: Lưu kết quả
# ─────────────────────────────────────────
output_file = "output/ket_qua.md"
os.makedirs("output", exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"# Kết quả ReCrew\n\n")
    f.write(f"**Yêu cầu:** {yeu_cau}\n\n")
    f.write("---\n\n")
    f.write(str(ket_qua))

print("\n" + "="*50)
print(f"  ✅ Hoàn thành! Kết quả đã lưu vào: {output_file}")
print("="*50 + "\n")
print(ket_qua)

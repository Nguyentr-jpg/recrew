"""
crew/tasks.py
Định nghĩa tất cả Task descriptions cho ReCrew.
Tách ra đây để app.py gọn hơn và dễ chỉnh prompt mà không đụng vào UI.
"""
from crewai import Task


def build_main_tasks(
    task_input: str,
    researcher,
    developer,
    reviewer,
    qa_tester,
    team_lead,
) -> list[Task]:
    """
    Tạo danh sách 5 task cho workflow chính.
    Thứ tự: Researcher → Developer → Reviewer → QA → Team Lead
    """
    task_nghien_cuu = Task(
        description=f"""
        Phân tích yêu cầu sau và đề xuất giải pháp kỹ thuật cụ thể:
        {task_input}

        Xác định rõ:
        - Đây là loại task gì? (game/web/UI → HTML+JS | script/API/tool → Python)
        - Công nghệ / thư viện cụ thể nên dùng và lý do
        - Kiến trúc ngắn gọn (không quá 5 gạch đầu dòng)
        - Những lưu ý kỹ thuật quan trọng nhất
        """,
        expected_output="Báo cáo kỹ thuật ngắn gọn: loại task, tech stack, kiến trúc, lưu ý",
        agent=researcher,
    )

    task_lap_trinh = Task(
        description=f"""
        Viết CODE HOÀN CHỈNH cho yêu cầu: {task_input}

        QUY TẮC BẮT BUỘC:
        - Đọc kết quả nghiên cứu để chọn đúng ngôn ngữ / framework
        - Game / web / UI / dashboard → viết 1 file HTML hoàn chỉnh (HTML+CSS+JS trong 1 file)
        - Script / automation / API / data → viết Python hoàn chỉnh với đầy đủ import
        - Code phải CHẠY ĐƯỢC ngay khi copy ra file và mở / chạy
        - KHÔNG viết pseudocode, KHÔNG mô tả dài dòng, KHÔNG placeholder
        - Đặt toàn bộ code trong 1 code block duy nhất
        - Sau code block: viết 2-3 dòng hướng dẫn chạy ngắn gọn
        """,
        expected_output="Một code block hoàn chỉnh chạy được ngay, kèm 2-3 dòng hướng dẫn",
        agent=developer,
        context=[task_nghien_cuu],
    )

    task_review = Task(
        description="""
        Review code vừa được viết. Tập trung vào:
        - Bug hoặc lỗi logic có thể xảy ra
        - Vấn đề bảo mật (nếu có)
        - Code có chạy được không (syntax error, import thiếu...)
        - Đề xuất cải thiện cụ thể (không quá 5 điểm)

        QUAN TRỌNG: Nếu code cần sửa, đưa ra đoạn code sửa cụ thể.
        """,
        expected_output="Danh sách vấn đề (nếu có) + đoạn code sửa cụ thể (nếu cần)",
        agent=reviewer,
        context=[task_lap_trinh],
    )

    task_test = Task(
        description="""
        Dựa trên code đã viết, liệt kê 5-8 test case quan trọng nhất:
        - 3 test case bình thường (happy path)
        - 2-3 edge case
        - 1-2 trường hợp lỗi

        Format mỗi test case: Tên | Input | Expected Output | Pass/Fail dự kiến
        """,
        expected_output="Bảng test case ngắn gọn, rõ ràng",
        agent=qa_tester,
        context=[task_lap_trinh, task_review],
    )

    task_tong_hop = Task(
        description="""
        Tổng hợp kết quả. Output PHẢI theo đúng format sau:

        ## ✅ Kết quả

        ### 📋 Tóm tắt
        [1 đoạn mô tả ngắn về giải pháp]

        ### 💻 Code hoàn chỉnh
        [COPY NGUYÊN XI toàn bộ code từ Lập Trình Viên — KHÔNG rút gọn, KHÔNG thay bằng mô tả]

        ### 🚀 Cách chạy
        [Hướng dẫn từng bước]

        ### 🧪 Test case chính
        [Tóm tắt test case từ QA]

        ### ⚠️ Lưu ý
        [Các điểm cần chú ý từ Reviewer]
        """,
        expected_output="Báo cáo theo đúng format trên, bao gồm code đầy đủ không rút gọn",
        agent=team_lead,
        context=[task_nghien_cuu, task_lap_trinh, task_review, task_test],
    )

    return [task_nghien_cuu, task_lap_trinh, task_review, task_test, task_tong_hop]


def build_revision_tasks(
    prev_task: str,
    prev_code: str,
    code_type: str,
    feedback: str,
    developer,
    reviewer,
    team_lead,
) -> list[Task]:
    """
    Tạo 3 task cho workflow revision (sửa lỗi theo feedback).
    Nhẹ hơn workflow chính — không cần Researcher và QA.
    """
    task_sua = Task(
        description=f"""
        Bạn đã viết code cho task: "{prev_task}"

        === CODE HIỆN TẠI ===
        ```{code_type}
        {prev_code}
        ```

        === PHẢN HỒI CỦA USER ===
        {feedback}

        === NHIỆM VỤ ===
        1. Đọc kỹ phản hồi — xác định chính xác vấn đề cần sửa
        2. Sửa code để giải quyết đúng vấn đề đó
        3. Giữ nguyên các phần khác đang hoạt động tốt
        4. Output: CODE HOÀN CHỈNH ĐÃ SỬA trong 1 code block (không chỉ đoạn sửa)
        5. Sau code block: viết "Đã thay đổi: ..." tóm tắt 2-3 điểm
        """,
        expected_output="Code hoàn chỉnh đã sửa trong 1 code block + tóm tắt thay đổi",
        agent=developer,
    )

    task_review_sua = Task(
        description="""
        Review nhanh code vừa được sửa:
        - Phần được sửa có giải quyết đúng vấn đề từ phản hồi không?
        - Sửa này có gây ra bug mới không?
        - Nếu cần chỉnh thêm: nêu cụ thể điều gì
        """,
        expected_output="Nhận xét ngắn: fix OK hay cần chỉnh thêm gì",
        agent=reviewer,
        context=[task_sua],
    )

    task_present = Task(
        description="""
        Trình bày kết quả sửa lỗi. Format BẮT BUỘC:

        ## 🔧 Đã sửa theo phản hồi

        ### Thay đổi
        [Mô tả ngắn gọn những gì đã được sửa]

        ### 💻 Code cập nhật
        [COPY NGUYÊN XI toàn bộ code đã sửa từ Developer — KHÔNG rút gọn]

        ### Nhận xét Reviewer
        [1-2 câu kết quả review]
        """,
        expected_output="Báo cáo theo format trên với code đầy đủ không rút gọn",
        agent=team_lead,
        context=[task_sua, task_review_sua],
    )

    return [task_sua, task_review_sua, task_present]

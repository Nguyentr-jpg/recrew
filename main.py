"""
main.py — ReCrew terminal mode
Chạy AI team hoàn toàn bằng terminal, không cần Streamlit.
Dùng khi cần tích hợp vào CI/CD, script, hoặc server không có UI.

Cách chạy:
    python main.py
    python main.py --model gemini/gemini-2.5-flash-lite
"""
import os
import sys
import argparse
from crew import run_main_workflow, run_revision_workflow
from utils.settings import load_saved_key, save_key
from utils.code_extractor import extract_code


def _banner():
    print("\n" + "="*52)
    print("  ⚡ ReCrew AI Team — Terminal Mode")
    print("="*52)
    print("  👑 Trưởng Nhóm   · 💻 Lập Trình Viên")
    print("  🔍 Kiểm Duyệt    · 🧪 QA Tester")
    print("  🔎 Nhà Nghiên Cứu")
    print("="*52 + "\n")


def _get_api_key(args_key: str) -> str:
    if args_key:
        return args_key

    saved = load_saved_key()
    if saved:
        use_saved = input(f"🔑 Dùng API key đã lưu? [Y/n]: ").strip().lower()
        if use_saved in ("", "y", "yes"):
            return saved

    key = input("🔑 Nhập Gemini API key: ").strip()
    if not key:
        print("❌ Không có API key. Thoát.")
        sys.exit(1)

    remember = input("💾 Ghi nhớ key này? [y/N]: ").strip().lower()
    if remember in ("y", "yes"):
        save_key(key)
        print("✅ Đã lưu key vào ~/.recrew_settings.json")

    return key


def _on_task_done(step_idx: int):
    labels = [
        "🔎 Nhà Nghiên Cứu",
        "💻 Lập Trình Viên",
        "🔍 Kiểm Duyệt",
        "🧪 QA Tester",
        "👑 Trưởng Nhóm",
    ]
    if step_idx < len(labels):
        print(f"  ✅ {labels[step_idx]} hoàn thành")


def _save_output(task: str, result_text: str, extracted: dict) -> None:
    os.makedirs("output", exist_ok=True)
    md_path = "output/ket_qua.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Kết quả ReCrew\n\n**Task:** {task}\n\n---\n\n{result_text}")
    print(f"\n  📄 Báo cáo: {md_path}")

    if extracted["html"]:
        with open("output/result.html", "w", encoding="utf-8") as f:
            f.write(extracted["html"])
        print("  🌐 HTML code: output/result.html (mở bằng trình duyệt)")
    elif extracted["python"]:
        with open("output/result.py", "w", encoding="utf-8") as f:
            f.write(extracted["python"])
        print("  🐍 Python code: output/result.py (chạy bằng python result.py)")


def main():
    parser = argparse.ArgumentParser(description="ReCrew — AI Software Team")
    parser.add_argument("--key",   help="Gemini API key", default="")
    parser.add_argument("--model", help="Model Gemini", default="gemini/gemini-2.5-flash")
    args = parser.parse_args()

    _banner()

    api_key = _get_api_key(args.key)
    model   = args.model
    print(f"🤖 Model: {model}\n")

    # ── Main loop ─────────────────────────────────────────────
    last_result    = None
    last_code      = None
    last_code_type = None
    last_task      = None

    while True:
        print("─" * 52)
        task_input = input("📋 Nhập task (hoặc 'quit' để thoát):\n> ").strip()
        if task_input.lower() in ("quit", "exit", "q"):
            print("\n👋 Tạm biệt!\n")
            break
        if not task_input:
            continue

        print(f"\n{'─'*52}")
        print("🚀 Team bắt đầu làm việc...\n")

        result = run_main_workflow(
            task_input=task_input,
            api_key=api_key,
            model=model,
            on_task_done=_on_task_done,
        )

        if result["error"]:
            print(f"\n❌ Lỗi: {result['error'][:300]}")
            continue

        extracted = extract_code(result["result_text"], result["dev_raw"])
        _save_output(task_input, result["result_text"], extracted)

        last_result    = result["result_text"]
        last_code      = extracted["html"] or extracted["python"]
        last_code_type = extracted["code_type"]
        last_task      = task_input

        print(f"\n{'='*52}")
        print(result["result_text"])
        print(f"{'='*52}\n")

        # ── Revision loop ──────────────────────────────────────
        rev_count = 0
        while True:
            action = input("🔄 Phản hồi/sửa lỗi (Enter để skip, 'next' cho task mới, 'quit' để thoát):\n> ").strip()

            if action.lower() in ("quit", "exit", "q"):
                print("\n👋 Tạm biệt!\n")
                sys.exit(0)
            if action.lower() in ("next", "n", ""):
                break
            if not action:
                break

            print(f"\n{'─'*52}")
            print("🔧 Developer đang sửa theo phản hồi...\n")

            rev = run_revision_workflow(
                prev_task=last_task or "",
                prev_code=last_code or "",
                code_type=last_code_type or "html",
                feedback=action,
                api_key=api_key,
                model=model,
            )

            if rev["error"]:
                print(f"❌ Lỗi khi sửa: {rev['error'][:300]}")
                continue

            rev_count += 1
            rev_extracted = extract_code(rev["result_text"], rev["dev_raw"])

            os.makedirs("output", exist_ok=True)
            if rev_extracted["html"]:
                with open(f"output/result_v{rev_count}.html", "w", encoding="utf-8") as f:
                    f.write(rev_extracted["html"])
                print(f"  🌐 HTML đã sửa: output/result_v{rev_count}.html")
            elif rev_extracted["python"]:
                with open(f"output/result_v{rev_count}.py", "w", encoding="utf-8") as f:
                    f.write(rev_extracted["python"])
                print(f"  🐍 Python đã sửa: output/result_v{rev_count}.py")

            last_code      = rev_extracted["html"] or rev_extracted["python"] or last_code
            last_code_type = rev_extracted["code_type"] or last_code_type

            print(f"\n{'='*52}")
            print(rev["result_text"])
            print(f"{'='*52}\n")


if __name__ == "__main__":
    main()

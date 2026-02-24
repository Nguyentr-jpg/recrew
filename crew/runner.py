"""
crew/runner.py
Build LLM, agents, crew rồi chạy workflow.
Trả về dict kết quả để app.py / main.py xử lý hiển thị.
"""
import os
from crewai import Crew, LLM
from agents import (
    create_team_lead,
    create_developer,
    create_reviewer,
    create_qa_tester,
    create_researcher,
)
from .tasks import build_main_tasks, build_revision_tasks


def create_llm(api_key: str, model: str) -> LLM:
    """Khởi tạo LLM Gemini với API key và model đã chọn."""
    os.environ["GEMINI_API_KEY"] = api_key
    os.environ["GOOGLE_API_KEY"] = api_key
    return LLM(model=model, api_key=api_key)


def create_all_agents(llm: LLM) -> dict:
    """Tạo tất cả 5 agents, trả về dict để dễ truy cập theo tên."""
    return {
        "researcher": create_researcher(llm),
        "developer":  create_developer(llm),
        "reviewer":   create_reviewer(llm),
        "qa_tester":  create_qa_tester(llm),
        "team_lead":  create_team_lead(llm),
    }


def run_main_workflow(
    task_input: str,
    api_key: str,
    model: str,
    on_task_done=None,   # callback(step_index) sau mỗi task
) -> dict:
    """
    Chạy full 5-agent workflow.

    Returns:
        {
            "result_text": str,     # output của Team Lead (markdown)
            "dev_raw":     str,     # output thô của Developer (để extract code)
            "error":       str|None # mô tả lỗi nếu có
        }
    """
    try:
        llm    = create_llm(api_key, model)
        agents = create_all_agents(llm)

        tasks = build_main_tasks(
            task_input,
            agents["researcher"],
            agents["developer"],
            agents["reviewer"],
            agents["qa_tester"],
            agents["team_lead"],
        )

        _step = [0]

        def _on_complete(task_output):
            if on_task_done:
                on_task_done(_step[0])
            _step[0] += 1

        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            verbose=False,
            task_callback=_on_complete,
        )

        ket_qua = crew.kickoff()

        # Lấy raw output của Developer (task index 1) để extract code chính xác hơn
        dev_raw = ""
        try:
            t_out   = crew.tasks[1].output
            dev_raw = str(t_out.raw) if hasattr(t_out, "raw") and t_out.raw else str(t_out)
        except Exception:
            pass

        return {
            "result_text": str(ket_qua),
            "dev_raw":     dev_raw,
            "error":       None,
        }

    except Exception as e:
        return {
            "result_text": "",
            "dev_raw":     "",
            "error":       str(e),
        }


def run_revision_workflow(
    prev_task:  str,
    prev_code:  str,
    code_type:  str,
    feedback:   str,
    api_key:    str,
    model:      str,
) -> dict:
    """
    Chạy 3-agent revision workflow (Developer + Reviewer + Team Lead).

    Returns:
        {
            "result_text": str,
            "dev_raw":     str,
            "error":       str|None
        }
    """
    try:
        llm       = create_llm(api_key, model)
        developer = create_developer(llm)
        reviewer  = create_reviewer(llm)
        team_lead = create_team_lead(llm)

        tasks = build_revision_tasks(
            prev_task, prev_code, code_type, feedback,
            developer, reviewer, team_lead,
        )

        rev_crew = Crew(
            agents=[developer, reviewer, team_lead],
            tasks=tasks,
            verbose=False,
        )

        ket_qua = rev_crew.kickoff()

        dev_raw = ""
        try:
            t_out   = rev_crew.tasks[0].output
            dev_raw = str(t_out.raw) if hasattr(t_out, "raw") and t_out.raw else str(t_out)
        except Exception:
            pass

        return {
            "result_text": str(ket_qua),
            "dev_raw":     dev_raw,
            "error":       None,
        }

    except Exception as e:
        return {
            "result_text": "",
            "dev_raw":     "",
            "error":       str(e),
        }

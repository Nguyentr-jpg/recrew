"""
utils/history.py
Quản lý lịch sử task trong Streamlit session_state.
Mỗi entry trong history là 1 dict chứa đủ thông tin để load lại kết quả.
"""
import streamlit as st
from datetime import datetime


# Số task tối đa giữ trong history của 1 session
_MAX_HISTORY = 20


def init_history() -> None:
    """Khởi tạo session_state keys liên quan đến history. Gọi 1 lần khi app start."""
    defaults = {
        "history":              [],
        "task_count":           0,
        "revision_count":       0,
        "is_running":           False,
        "last_result":          None,
        "last_code":            None,
        "last_code_type":       None,
        "last_task":            None,
        "loaded_history_item":  None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def add_to_history(
    task: str,
    result: str,
    code: str | None,
    code_type: str | None,
) -> None:
    """
    Thêm 1 task vào đầu danh sách history.
    Giữ tối đa _MAX_HISTORY entries.
    """
    entry = {
        "task":       task,
        "result":     result,
        "code":       code,
        "code_type":  code_type,
        "timestamp":  datetime.now().strftime("%H:%M"),
        "date":       datetime.now().strftime("%d/%m"),
        "revisions":  0,
    }
    history: list = st.session_state.get("history", [])
    history.insert(0, entry)
    st.session_state.history = history[:_MAX_HISTORY]


def update_latest_revision(revision_count: int, code: str | None, code_type: str | None, result: str) -> None:
    """Cập nhật entry mới nhất trong history sau khi revision."""
    history: list = st.session_state.get("history", [])
    if history:
        history[0]["revisions"]  = revision_count
        history[0]["code"]       = code
        history[0]["code_type"]  = code_type
        history[0]["result"]     = result
        st.session_state.history = history


def get_history() -> list:
    """Trả về danh sách task history."""
    return st.session_state.get("history", [])


def load_history_item(item: dict) -> None:
    """
    Load 1 item từ history vào session_state hiện tại,
    để app hiển thị lại kết quả và cho phép tiếp tục feedback.
    """
    st.session_state.last_result    = item.get("result")
    st.session_state.last_code      = item.get("code")
    st.session_state.last_code_type = item.get("code_type")
    st.session_state.last_task      = item.get("task")
    st.session_state.revision_count = item.get("revisions", 0)
    st.session_state.loaded_history_item = item

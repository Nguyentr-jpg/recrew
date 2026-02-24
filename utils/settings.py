"""
utils/settings.py
Lưu / load cài đặt cục bộ (API key, model preference...) vào file JSON
tại ~/.recrew_settings.json — nằm ngoài repo, không bị commit lên git.
"""
import json
import os

_SETTINGS_FILE = os.path.expanduser("~/.recrew_settings.json")


def _load() -> dict:
    try:
        with open(_SETTINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict) -> bool:
    try:
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def load_saved_key() -> str:
    """Trả về API key đã lưu, hoặc chuỗi rỗng nếu chưa có."""
    return _load().get("api_key", "")


def save_key(api_key: str) -> bool:
    """Lưu API key. Trả về True nếu thành công."""
    data = _load()
    data["api_key"] = api_key
    return _save(data)


def clear_key() -> bool:
    """Xóa API key đã lưu."""
    data = _load()
    data.pop("api_key", None)
    return _save(data)


def load_saved_model() -> str:
    """Trả về model đã chọn lần trước, hoặc chuỗi rỗng."""
    return _load().get("model", "")


def save_model(model: str) -> bool:
    """Lưu model preference."""
    data = _load()
    data["model"] = model
    return _save(data)

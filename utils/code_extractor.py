"""
utils/code_extractor.py
Trích xuất HTML / Python code từ LLM output (chuỗi markdown có code block).
Không phụ thuộc vào Streamlit — pure Python, dễ test.
"""
import re


def extract_html(text: str) -> str | None:
    """
    Tìm code block HTML hoặc JS trong text.
    - Nếu tìm được HTML hoàn chỉnh → trả về nguyên
    - Nếu chỉ có đoạn HTML → bọc thành trang hoàn chỉnh
    - Nếu là JS Phaser → bọc với Phaser CDN
    - Nếu là JS thuần → bọc đơn giản
    - Trả về None nếu không tìm thấy
    """
    html_blocks = re.findall(r'```html\n(.*?)\n```', text, re.DOTALL)
    js_blocks   = re.findall(r'```(?:javascript|js)\n(.*?)\n```', text, re.DOTALL)

    if html_blocks:
        full = html_blocks[0]
        if '<html' in full.lower() or '<!doctype' in full.lower():
            return full
        # Đoạn HTML không đầy đủ → bọc lại
        return (
            "<!DOCTYPE html><html><head><meta charset='UTF-8'>"
            "<style>body{margin:0;background:#111;color:#eee;font-family:sans-serif;}</style>"
            f"</head><body>{full}</body></html>"
        )

    if js_blocks:
        js_code = '\n\n'.join(js_blocks)
        if 'Phaser' in js_code or 'phaser' in js_code.lower():
            return _wrap_phaser(js_code)
        return _wrap_js(js_code)

    return None


def extract_python(text: str) -> str | None:
    """Trả về code Python đầu tiên tìm được, hoặc None."""
    blocks = re.findall(r'```(?:python|py)\n(.*?)\n```', text, re.DOTALL)
    return blocks[0] if blocks else None


def extract_code(primary: str, fallback: str = "") -> dict:
    """
    Thử extract HTML trước, sau đó Python.
    Tìm trong `primary` trước, nếu không có thì tìm trong `fallback`.

    Trả về dict:
        {
            "html":      str | None,
            "python":    str | None,
            "code_type": "html" | "python" | None,
        }
    """
    combined = primary + "\n" + fallback

    html = extract_html(primary) or extract_html(fallback)
    if html:
        return {"html": html, "python": None, "code_type": "html"}

    py = extract_python(combined)
    if py:
        return {"html": None, "python": py, "code_type": "python"}

    return {"html": None, "python": None, "code_type": None}


# ── Helpers nội bộ ──────────────────────────────────────────────────────────

def _wrap_phaser(js_code: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Game Preview</title>
  <script src="https://cdn.jsdelivr.net/npm/phaser@3/dist/phaser.min.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #111; display: flex; justify-content: center; align-items: center; height: 100vh; }}
    canvas {{ display: block; }}
  </style>
</head>
<body>
  <div id="phaser-game"></div>
  <script>
{js_code}
  </script>
</body>
</html>"""


def _wrap_js(js_code: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Preview</title>
  <style>
    * {{ margin: 0; padding: 0; }}
    body {{ background: #111; color: #eee; font-family: monospace; }}
    canvas {{ display: block; }}
  </style>
</head>
<body>
  <canvas id="gameCanvas"></canvas>
  <script>
{js_code}
  </script>
</body>
</html>"""

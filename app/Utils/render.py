import re, html
from aiogram.types import Message

# ---------- Markdown -> HTML (безопасно для Telegram) ----------

_f_codeblock = re.compile(r"```(.*?)```", re.S)          # блоки кода
_f_inlinecode = re.compile(r"`([^`]+)`")                 # инлайн код
_f_bold_star = re.compile(r"\*\*(.+?)\*\*", re.S)        # **жирный**
_f_bold_underscore = re.compile(r"__(.+?)__", re.S)      # __жирный__
_f_h3 = re.compile(r"(?m)^\s*###\s+(.*)$")
_f_h2 = re.compile(r"(?m)^\s*##\s+(.*)$")
_f_h1 = re.compile(r"(?m)^\s*#\s+(.*)$")
_f_bullet = re.compile(r"(?m)^\s*[-*]\s+")               # - / * в начале строки

def md_to_html(text: str) -> str:
    """Мини-конвертер markdown -> HTML, совместимый с Telegram."""
    # 0) сохраняем кодовые блоки, чтобы не форматировать их содержимое
    code_blocks = []
    def _save_block(m):
        code_blocks.append(m.group(1))
        return f"__CODEBLOCK_{len(code_blocks)-1}__"
    text = _f_codeblock.sub(_save_block, text)

    # 1) экранируем весь текст
    text = html.escape(text)

    # 2) заголовки -> просто жирная строка (теги h1/h2/h3 Telegram не поддерживает)
    text = _f_h3.sub(lambda m: f"<b>{m.group(1).strip()}</b>", text)
    text = _f_h2.sub(lambda m: f"<b>{m.group(1).strip()}</b>", text)
    text = _f_h1.sub(lambda m: f"<b>{m.group(1).strip()}</b>", text)

    # 3) маркеры списка в начале строки -> буллет «• »
    text = _f_bullet.sub("• ", text)

    # 4) жирный
    text = _f_bold_star.sub(lambda m: f"<b>{m.group(1)}</b>", text)
    text = _f_bold_underscore.sub(lambda m: f"<b>{m.group(1)}</b>", text)

    # 5) инлайн-код
    text = _f_inlinecode.sub(lambda m: f"<code>{m.group(1)}</code>", text)

    # 6) возвращаем кодовые блоки
    for i, raw in enumerate(code_blocks):
        block_html = f"<pre><code>{html.escape(raw)}</code></pre>"
        text = text.replace(f"__CODEBLOCK_{i}__", block_html)

    # ВАЖНО: не вставляем <br>, Telegram сам понимает \n
    return text

# ---------- Отправка длинного HTML текста ----------

async def send_long_html(message: Message, html_text: str, chunk: int = 4000) -> None:
    """Режем длинный текст по \\n/пробелам, отправляем с parse_mode='HTML'."""
    i = 0
    while i < len(html_text):
        part = html_text[i:i + chunk]
        if i + chunk < len(html_text):
            cut = max(part.rfind("\n"), part.rfind(" "))
            if cut > 0:
                part = part[:cut]
        await message.answer(part, parse_mode="HTML")
        i += len(part)
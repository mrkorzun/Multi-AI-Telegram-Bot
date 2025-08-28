from app.models.xai import model_xai
from app.models.llama import model_llama
from app.models.deepseek import model_deepseek
from app.models.anthropic import model_anthropic

# ---- Маппинг “имя модели” -> корутина генерации
MODEL_CALLS = {
    "xai": model_xai,
    "llama": model_llama,
#    "gemini": model_gemini,
    "deepseek": model_deepseek,
    "anthropic": model_anthropic,  
}

# Человеко-читаемые названия/алиасы для подстановки в интро
MODEL_TITLES = {
    "deepseek":  ("DeepSeek-V3", "DeepSeek Chat"),
    "llama":     ("Meta Llama 3.1-70B", "Llama"),
    "anthropic": ("Claude-3.5 Sonnet", "Claude"),
    "xai":       ("Grok-2", "Grok"),
}

# Шаблон запроса для самопрезентации
INTRO_PROMPT_TEMPLATE = (
    "Сделай короткую самопрезентацию **от первого лица** для модели {title} "
    "(обращаться можно как {alias}). Структура: "
    "1–2 строки приветствия; затем маркированный список '•' из 3–5 возможностей; "
    "закончить фразой 'Чем могу помочь? 😊'. Пиши по-русски, до 500 символов, без воды. "
    "Ключевые слова выделяй **жирным**. Не упоминай токены/лимиты."
)

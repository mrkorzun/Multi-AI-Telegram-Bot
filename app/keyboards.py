from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def ai_models():
    models = ['anthropic', 'llama', 'deepseek', 'xai']
    keyboard = InlineKeyboardBuilder()
    for model in models:
        keyboard.add(InlineKeyboardButton(text=model, callback_data=f'model_{model}'))
    return keyboard.adjust(2).as_markup()

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Back to Models', callback_data='back')]
])
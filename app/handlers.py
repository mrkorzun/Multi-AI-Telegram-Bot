import asyncio
import logging


from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.states import Gen
from app.dicts import MODEL_CALLS, MODEL_TITLES, INTRO_PROMPT_TEMPLATE
from app.Utils.render import md_to_html, send_long_html


router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
       f"{message.from_user.first_name} hey and welcome back.\nPlease choose AI model:",
        reply_markup = await kb.ai_models()
        )

@router.message(Command("models"))
async def choose_model_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выберите языковую модель:",
        reply_markup=await kb.ai_models(),
    )

#  выбор модели → сгенерировать интро → показать плейсхолдер
# ---------- Выбор модели (кнопки) ----------
@router.callback_query(F.data.startswith("model_"))
async def pick_model(callback: CallbackQuery, state: FSMContext):

    model_name = callback.data.removeprefix("model_")
    if model_name not in MODEL_CALLS:
        await callback.message.edit_text("Эта модель пока не подключена.")
        return

    # сохраняем выбор
    await state.update_data(model=model_name)
    await callback.answer(f'Модель {model_name.upper()} выбрана')

    # подготавливаем интро-промпт
    title, alias = MODEL_TITLES.get(model_name, (model_name.upper(), model_name))
    intro_prompt = INTRO_PROMPT_TEMPLATE.format(title=title, alias=alias)

    # переключаемся в "идёт генерация", имитируем набор и зовём модель
    await state.set_state(Gen.generating)
    await callback.message.bot.send_chat_action(callback.from_user.id, ChatAction.TYPING)
    await asyncio.sleep(0.5)

    generate = MODEL_CALLS[model_name]
    try:
        intro_md = await generate(intro_prompt)      # <— вызываем ИМЕННО модель
    except Exception as e:
        await callback.message.answer(f"Не удалось получить ответ от модели: {e}")
        await state.clear()
        return

    # рендер в HTML и отправка интро (с кнопкой "Back to Models")
    intro_html = md_to_html(intro_md)
    await callback.message.edit_text(intro_html, parse_mode="HTML", reply_markup=kb.back)
    await state.set_state(Gen.waiting_prompt)

# ---------- Кнопка “Назад к моделям” ----------

@router.callback_query(F.data == "back")
async def back_to_model(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        "Выберите языковую модель:",
        reply_markup = await kb.ai_models(),
    )

# ---------- AI Generations User Prompt ----------

@router.message(Gen.waiting_prompt, F.text)
async def run_generation(message: Message, state: FSMContext):
    data = await state.get_data()
    model_name = data.get("model")
    
    if not model_name:
        # На случай если state потерялся
        await message.answer("Сначала выберите модель:", reply_markup= await kb.ai_models)
        return
    
    # Переключаемся в “генерируется”
    await state.set_state(Gen.generating)
    
        # UX: имитация набора
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(0.5)
        
        # Вызов соответствующей модели
    generate = MODEL_CALLS[model_name]
    try:
        response = await generate(message.text)
        
        safe_html = md_to_html(response)
        await send_long_html(message, safe_html)
        
    except Exception as e:
        await message.answer(f"⚠️ Не удалось сгенерировать ответ: {e}\nПопробуйте ещё раз или выберите другую модель: /models")

        # После ответа остаёмся в состоянии выбора промпта для той же модели
    await state.set_state(Gen.waiting_prompt)

    
# Если пользователь что-то пишет во время генерации — вежливо просим подождать

@router.message(Command("cancel"))
async def cancel_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Окей, сбросил состояние. Можешь снова выбрать модель: /models")
    

@router.message(Gen.generating)
async def stop_flood(message: Message, state: FSMContext):
    data = await state.get_data()
    last = data.get('last_warn_ts', 0)
    now = message.date.timestamp()
    if now - last > 3:
        await message.answer('Подождите ваш запрос генерируется...')
        await state.update_data(last_warn_ts=now)
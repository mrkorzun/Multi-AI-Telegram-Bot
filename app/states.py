from aiogram.fsm.state import StatesGroup, State

class Gen(StatesGroup):
    waiting_prompt = State() # пользователь выбрал модель и мы ждём текст
    generating = State() # идёт генерация (чтобы ловить “подождите...”)
import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.handlers import router

async def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=os.getenv('TG_TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    await dp.start_polling(bot)

async def startup (dispatcher: Dispatcher):
    print('Starting up...')

async def shutdown(dispatcher: Dispatcher):
    print('Shuting down...')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot is stopped by a user...')
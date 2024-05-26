import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import register_command_handlers, register_handlers
from database.models import async_main
from app.commands.command_list import set_commands_list

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


async def main():
    logging.basicConfig(level=logging.INFO)
    await async_main()
    register_command_handlers(dp)
    register_handlers(dp)
    await set_commands_list(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Бот остановлен')

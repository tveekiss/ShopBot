import os
from dotenv import load_dotenv

from aiogram.types import Message
from app.keyboards import start_keyboard


async def start_command(message: Message):
    load_dotenv()
    await message.answer(
        f'Привет, {message.from_user.first_name}! 👋\n Выбери категорию по которой ты хочешь выбрать товар ⤵️',
        reply_markup=start_keyboard
    )
    if str(message.from_user.id) in os.getenv('ADMIN_ID').split(','):
        await message.answer(
            f'Что бы редактировать товары введи /settings'
        )
    print(message.from_user.id)



import os
from dotenv import load_dotenv

from aiogram.types import Message


async def start_command(message: Message):
    load_dotenv()
    await message.answer(
        f'Привет, {message.from_user.first_name}! 👋\n Выбери категорию по которой ты хочешь выбрать товар ⤵️',
    )
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(
            f'Что бы редактировать товары введи /settings'
        )
    print(message.from_user.id)



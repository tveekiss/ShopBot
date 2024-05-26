from aiogram.types import Message


async def get_token(message: Message):
    token = str(message.from_user.id)
    await message.answer(token)

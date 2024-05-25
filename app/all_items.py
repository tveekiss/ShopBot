from aiogram.types import Message
from app.database.requests import get_all_items
from aiogram import Bot
from aiogram.enums import ParseMode


async def all_items(message: Message, bot: Bot):
    items = await get_all_items()
    for item in items:
        print(item.brand.category.name)
        text = (f'<b>{item.name}</b> \n\n'
                f'{item.description}\n\n'
                f'Цена: <b>{item.price}</b>\n'
                f'Категория: <b>{item.brand.category.name}</b>\n'
                f'Бренд: <b>{item.brand.name}</b>')
        await bot.send_photo(chat_id=message.chat.id, photo=item.photo, caption=text, parse_mode=ParseMode.HTML)

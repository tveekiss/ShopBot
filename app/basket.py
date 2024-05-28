import os

from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from app.database.requests import create_basket, delete_basket, get_basket, get_all_baskets, get_item, edit_quantity
from aiogram.enums import ParseMode
from app.keyboards import basket_keyboard, start_keyboard, quantity_keyboard
from app.commands.start import start_command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv


class Quantity(StatesGroup):
    quantity = State()
    edit_quantity = State()


async def choice_quantity(call: CallbackQuery, state: FSMContext):
    item_id = int(call.data.split('_')[1])

    await state.update_data(item_id=item_id)
    await call.message.answer('Введите количество')
    await state.set_state(Quantity.quantity)


async def call_change_quantity(call: CallbackQuery, state: FSMContext):
    basket_id = int(call.data.split('_')[1])
    basket = await get_basket(basket_id)
    await state.update_data(basket_id=basket_id)
    await call.message.answer(f'Введите новое количество: \n\nСтарое количество: <b>{basket.quantity}</b>',
                              parse_mode=ParseMode.HTML)
    await state.set_state(Quantity.edit_quantity)


async def change_quantity(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    baskets = await get_all_baskets(message.from_user.id)
    for basket in baskets:
        builder.button(text=basket.item.name, callback_data=f'ChangeQuantity_{basket.id}')
    await message.answer('Выберите товар количество которого вы хотите изменить:',
                         reply_markup=builder.as_markup())


async def finish_quantity(message: Message, state: FSMContext, bot: Bot):
    try:
        if not 0 < int(message.text) <= 100:
            raise ValueError
    except ValueError:
        await message.answer('Введите число от 1 до 100')
        return
    context_data = await state.get_data()
    basket_id = int(context_data['basket_id'])
    await edit_quantity(basket_id, int(message.text))
    await message.answer('Количество успешно изменено')
    await state.clear()
    await basket_main(message, bot)


async def basket_create(call: CallbackQuery):
    item_id = int(call.data.split('_')[1])
    baskets = await get_all_baskets(call.from_user.id)
    for basket in baskets:
        if basket.item_id == item_id:
            builder = InlineKeyboardBuilder()
            builder.button(text='Изменить количество', callback_data=f'ChangeQuantity_{basket.id}')
            await call.message.answer('У вас уже есть этот товар в корзине', reply_markup=builder.as_markup())
            return
    await create_basket(item_id, call.from_user.id, 1)
    item = await get_item(item_id)
    await call.message.answer(f'Товар <b>{item.name}</b> успешно занесен в корзину',
                              parse_mode=ParseMode.HTML)
    

async def basket_main(message: Message, bot: Bot):
    baskets = await get_all_baskets(message.from_user.id)
    if len(baskets) == 0:
        await bot.send_message(chat_id=message.from_user.id, text='У вас нету товаров в корзине',
                               reply_markup=start_keyboard)
        return
    text = 'Товары которые у вас в корзине:\n\n'
    total_price = 0
    for basket in baskets:
        text += (f'<b>{basket.item.name}</b> - {basket.item.brand.category.name}. {basket.quantity} шт'
                 f' <b>{basket.item.price * basket.quantity}</b> руб\n')
        total_price += basket.item.price * basket.quantity
    text += f'\nПолная стоимость: <b>{total_price}</b>'
    text += '\n\n Желаете ли вы оформить заказ?'
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=basket_keyboard,
                           parse_mode=ParseMode.HTML)


async def basket_all_delete(message: Message):
    baskets = await get_all_baskets(message.from_user.id)
    for basket in baskets:
        await delete_basket(basket.id)
    await message.answer('Все товары в корзине успешно удалены!')
    await start_command(message)


async def basket_item_delete(message: Message):
    baskets = await get_all_baskets(message.from_user.id)
    builder = InlineKeyboardBuilder()
    for basket in baskets:
        builder.button(text=basket.item.name, callback_data=f'BasketDelete_{basket.id}')
    builder.adjust(1)
    await message.answer('Выберите, какой товар вы хотите удалить из корзины', reply_markup=builder.as_markup())


async def basket_delete(call: CallbackQuery, bot: Bot):
    basket_id = int(call.data.split('_')[1])
    basket = await get_basket(basket_id)
    item_name = basket.item.name
    await delete_basket(basket_id)
    await call.message.answer(f'Товар <b>{item_name}</b> успешно удален из корзины', parse_mode=ParseMode.HTML)
    await basket_main(call, bot)


async def basket_complete(message: Message, bot: Bot):
    baskets = await get_all_baskets(message.from_user.id)
    if len(baskets) == 0:
        await message.answer('У вас нету товаров в корзине')
        return
    text = f'Пользователь {message.from_user.full_name} желает сделать покупку на следующие товары:\n\n'
    total_price = 0
    for basket in baskets:
        text += f'<b>{basket.item.name}</b> - {basket.quantity} шт. <b>{basket.item.price * basket.quantity}</b> руб\n'
        total_price += basket.item.price * basket.quantity
        await delete_basket(basket.id)
    text += f'\nОбщая стоимость покупки равна: <b>{total_price}</b> руб'
    load_dotenv()
    await bot.send_message(chat_id=os.getenv('GROUP_ID'), text=text, parse_mode=ParseMode.HTML)
    await message.answer('Запрос на покупку отправлен')
    await start_command(message)

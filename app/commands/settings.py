import os

from aiogram.handlers import CallbackQueryHandler
from dotenv import load_dotenv
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.keyboards import settings_keyboard, settings_choice_keyboard, settings_edit_brand, settings_edit_item
from app.commands.start import start_command
from app.database.requests import (add_category, get_all_categories, add_brand, get_all_brands, add_item,
                                   update_category)
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class AdminAction(StatesGroup):
    action = State()


class AdminChoice(StatesGroup):
    choice = State()


class CategoryAction(StatesGroup):
    name = State()
    edit_name = State()


class BrandAction(StatesGroup):
    name = State()
    edit_name = State()
    category = State()
    edit_category = State()


class ItemAction(StatesGroup):
    name = State()
    edit_name = State()
    photo = State()
    edit_photo = State()
    description = State()
    edit_description = State()
    price = State()
    edit_price = State()
    brand = State()
    edit_brand = State()


class SettingsCallback(CallbackData, prefix='fabset'):
    model: str
    action: Optional[str]
    model_id: Optional[int]


async def settings_command(message: Message, state: FSMContext):
    load_dotenv()
    if message.from_user.id != int(os.getenv('ADMIN_ID')):
        return
    await message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def add_action(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.clear()
        await start_command(message)
        return
    await state.update_data(action=message.text)
    context_data = await state.get_data()
    admin_action = context_data['action']
    await message.answer(
        f'Выберите что вы хотите {admin_action.lower()}',
        reply_markup=settings_choice_keyboard
    )
    await state.set_state(AdminChoice.choice)


async def settings_redirection(message: Message, state: FSMContext):
    context_data = await state.get_data()
    admin_action = context_data['action']
    await state.update_data(model=message.text)
    if message.text == 'Назад':
        await state.clear()
        await settings_command(message, state)
        return
    match admin_action:
        case 'Добавить':
            await start_add(message, state)



# ========== ADD ==========
async def start_add(message: Message, state: FSMContext):
    context_data = await state.get_data()
    model = context_data['model']
    await message.answer('Введите название')
    match model:
        case 'Категория':
            await state.set_state(CategoryAction.name)
        case 'Бренд':
            await state.set_state(BrandAction.name)
        case 'Товар':
            await state.set_state(ItemAction.name)


async def finish_category(message: Message, state: FSMContext):
    await add_category(message.text)
    await message.answer(
        'Категория успешна добавлена!',
    )
    await state.clear()
    await message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def set_brand(message: Message, state: FSMContext):
    await state.update_data(brand_name=message.text)
    await set_category(message, state)


async def finish_brand( call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback):
    context_data = await state.get_data()
    category_id = callback_data.model_id
    name = context_data['brand_name']
    await add_brand(name, category_id)
    await call.message.answer(
        'бренд успешно добавлен!'
    )
    await state.clear()
    await call.message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def set_description(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите описание')
    await state.set_state(ItemAction.description)


async def set_photo(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('Отправьте фото')
    await state.set_state(ItemAction.photo)


async def set_price(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer('Введите цену')
    await state.set_state(ItemAction.price)


async def set_item_category(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await set_category(message, state)


async def set_item_brand(call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback):
    await state.update_data(category=callback_data.model_id)
    context_data = await state.get_data()
    model = context_data['model']
    brands = await get_all_brands(callback_data.model_id)
    builder = InlineKeyboardBuilder()
    for brand in brands:
        builder.button(text=brand.name,
                       callback_data=SettingsCallback(action='Бренд', model=model, model_id=brand.id))
    builder.adjust(2)
    print(5)
    await call.message.answer(
        'Выберите бренд',
        reply_markup=builder.as_markup()
    )


async def finish_item(call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback):
    context_data = await state.get_data()
    name = context_data['name']
    description = context_data['description']
    price = context_data['price']
    brand = callback_data.model_id
    photo = context_data['photo']
    await add_item(name, price, description, brand, photo)
    await call.message.answer('Товар успешно добавлен')
    await state.clear()
    await call.message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def set_category(message: Message, state: FSMContext):
    context_data = await state.get_data()
    model = context_data['model']
    categories = await get_all_categories()
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category.name,
                       callback_data=SettingsCallback(action='Категория', model=model, model_id=category.id))
    builder.adjust(2)
    print(1)
    await message.answer(
        'Выберите категорию',
        reply_markup=builder.as_markup()
    )


# ========= EDIT ==========

async def start_edit_category(message: Message):
    categories = await get_all_categories()
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category.name,
                       callback_data=SettingsCallback(action='Изменить модель категории', model_id=category.id))
    builder.adjust(2)
    await message.answer(
        'Выберите какую категорию вы хотите изменить',
        reply_markup=builder.as_markup()
    )


async def edit_category(call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback):
    await state.update_data(category_id=callback_data.model_id)
    await call.message.answer('Введите новое имя')
    await state.set_state(CategoryAction.edit_name)


async def finish_edit_category(message: Message, state: FSMContext):
    context_data = await state.get_data()
    category_id = context_data['category_id']
    await update_category(category_id, message.text)
    await message.answer('Категория успешно изменена')
    await state.clear()
    await message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def start_brand_edit(message: Message):
    categories = await get_all_categories()

    builder = InlineKeyboardBuilder()
    for category in categories:
        brands = await get_all_brands(category)
        for brand in brands:
            builder.button(text=f'{brand.name} ({category.name})',
                           callback_data=SettingsCallback(action='Изменить модель бренда', model_id=brand.id))
    builder.adjust(2)
    await message.answer(
        'Выберите какой бренд вы хотите изменить',
        reply_markup=builder.as_markup()
    )


async def choice_edit_brand(call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback):
    await state.update_data(brand_id=callback_data.model_id)
    await call.message.answer(
        'Что именно вы хотите изменить?'
    )
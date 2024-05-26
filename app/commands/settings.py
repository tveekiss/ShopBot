import os

from aiogram import Bot
from dotenv import load_dotenv
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.keyboards import (settings_keyboard, settings_choice_keyboard, settings_edit_brand, settings_edit_item,
                           delete_keyboard)
from app.commands.start import start_command
from app.database.requests import (add_category, get_all_categories, add_brand, get_all_brands, add_item,
                                   update_category, update_brand, update_item, get_all_items,
                                   get_item, get_brand, get_category, delete_category, delete_brand, delete_item)
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode


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
    edit_choice = State()


class ItemAction(StatesGroup):
    name = State()
    edit_name = State()
    photo = State()
    edit_photo = State()
    description = State()
    edit_description = State()
    price = State()
    edit_price = State()
    edit_choice = State()

class Delete(StatesGroup):
    confirm = State()


class SettingsCallback(CallbackData, prefix='fabset'):
    model: Optional[str]
    action: str
    model_id: Optional[int]


async def settings_command(message: Message, state: FSMContext):
    load_dotenv()
    if str(message.from_user.id) not in os.getenv('ADMIN_ID').split(','):
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
        case 'Изменить':
            await start_edit(message, state)
        case 'Удалить':
            await start_delete(message, state)


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
    if len(message.text) > 900:
        await message.answer('Длинна описания не может быть больше 900 символов')
        return
    await state.update_data(description=message.text)
    await message.answer('Отправьте фото')
    await state.set_state(ItemAction.photo)


async def set_price(message: Message, state: FSMContext):
    if message.photo is None:
        await message.answer('Нужно отправить именно фотографию')
        return
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer('Введите цену')
    await state.set_state(ItemAction.price)


async def set_item_category(message: Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer('Нужно отправить число')
        return
    else:
        await state.update_data(price=price)
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
async def start_edit(message: Message, state: FSMContext):
    context_data = await state.get_data()
    model = context_data['model']
    match model:
        case 'Категория':
            await start_edit_category(message)
        case 'Бренд':
            await start_edit_brand(message)
        case 'Товар':
            await start_edit_item(message)


async def start_edit_category(message: Message):
    categories = await get_all_categories()
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category.name,
                       callback_data=SettingsCallback(action='Изменить модель категории', model=None, model_id=category.id))
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


async def start_edit_brand(message: Message):
    categories = await get_all_categories()
    builder = InlineKeyboardBuilder()
    for category in categories:
        brands = await get_all_brands(category.id)
        for brand in brands:
            builder.button(text=f'{brand.name} ({category.name})',
                           callback_data=SettingsCallback(action='Изменить модель бренда', model=None, model_id=brand.id))
    builder.adjust(1)
    await message.answer(
        'Выберите какой бренд вы хотите изменить',
        reply_markup=builder.as_markup()
    )


async def choice_edit_brand(call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback):
    await state.update_data(brand_id=callback_data.model_id)
    await call.message.answer(
        'Что именно вы хотите изменить?',
        reply_markup=settings_edit_brand
    )
    await state.set_state(BrandAction.edit_choice)


async def edit_brand(message: Message, state: FSMContext):
    await state.update_data(choice_edit=message.text)
    if message.text == 'Название':
        await edit_name_brand(message, state)
    if message.text == 'Категория':
        await edit_category_brand(message)


async def edit_name_brand(message: Message, state: FSMContext):
    await message.answer('Введите новое название')
    await state.set_state(BrandAction.edit_name)


async def finish_edit_name_brand(message: Message, state: FSMContext):
    context_data = await state.get_data()
    brand_id = context_data['brand_id']
    await update_brand(brand_id, name=message.text)
    await message.answer("Название успешно изменено")
    await state.clear()
    await message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def edit_category_brand(message: Message):
    builder = InlineKeyboardBuilder()
    categories = await get_all_categories()
    for category in categories:
        builder.button(text=category.name,
                       callback_data=SettingsCallback(action='Изменить категорию бренда', model=None, model_id=category.id))
    builder.adjust(2)
    print(1)
    await message.answer(
        'Выберите категорию',
        reply_markup=builder.as_markup()
    )


async def finish_edit_category_brand(call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback):
    context_data = await state.get_data()
    brand_id = context_data['brand_id']
    category_id = callback_data.model_id
    await update_brand(brand_id, category_id=category_id)
    await call.message.answer('Категория бренда успешно изменена')
    await state.clear()
    await call.message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def start_edit_item(message: Message):
    items = await get_all_items()
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=f'{item.name} ({item.brand.name})',
                       callback_data=SettingsCallback(action='Изменить модель товара', model=None,
                                                      model_id=item.id))
    builder.adjust(1)
    await message.answer(
        'Выберите какой товар вы хотите изменить',
        reply_markup=builder.as_markup()
    )


async def choice_edit_item(call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback, bot: Bot):
    await state.update_data(item_id=callback_data.model_id)
    item = await get_item(callback_data.model_id)
    text = (f'<b>{item.name}</b> \n\n'
            f'Цена: <b>{item.price}</b>\n'
            f'Категория: <b>{item.brand.category.name}</b>\n'
            f'Бренд: <b>{item.brand.name}</b>')
    await bot.send_photo(chat_id=call.message.chat.id, photo=item.photo, caption=text, parse_mode=ParseMode.HTML)
    await call.message.answer(
        'Что именно вы хотите изменить?',
        reply_markup=settings_edit_item
    )
    await state.set_state(ItemAction.edit_choice)


async def edit_item(message: Message, state: FSMContext):
    match message.text:
        case 'Название':
            await start_edit_name_item(message, state)
        case 'Описание':
            await start_edit_desc_item(message, state)
        case 'Изображение':
            await start_edit_image_item(message, state)
        case 'Цена':
            await start_edit_price_item(message, state)
        case r'Бренд\Категория':
            await edit_item_category(message)
        case 'Назад':
            await state.clear()
            await settings_command(message, state)


async def start_edit_name_item(message: Message, state: FSMContext):
    await message.answer('Введите новое название')
    await state.set_state(ItemAction.edit_name)


async def finish_edit_name_item(message: Message, state: FSMContext):
    context_data = await state.get_data()
    item_id = context_data['item_id']
    await update_item(name=message.text, item_id=item_id)
    await message.answer('Название товара успешно изменено')
    await state.clear()
    await message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def start_edit_desc_item(message: Message, state: FSMContext):
    await message.answer('Введите новое описание')
    await state.set_state(ItemAction.edit_description)


async def finish_edit_desc_item(message: Message, state: FSMContext):
    if len(message.text) > 900:
        await message.answer('Длинна описания не может быть больше 900 символов')
        return
    context_data = await state.get_data()
    item_id = context_data['item_id']
    await update_item(description=message.text, item_id=item_id)
    await message.answer('Описание товара успешно изменено')
    await state.clear()
    await message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def start_edit_image_item(message: Message, state: FSMContext):
    await message.answer('Отправьте новое изображение')
    await state.set_state(ItemAction.edit_photo)


async def finish_edit_image_item(message: Message, state: FSMContext):
    if message.photo is None:
        await message.answer('Нужно отправить изображение')
        return
    context_data = await state.get_data()
    item_id = context_data['item_id']
    await update_item(photo=message.photo[-1].file_id, item_id=item_id)
    await message.answer('Изображение товара успешно изменено')
    await state.clear()
    await message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


async def start_edit_price_item(message: Message, state: FSMContext):
    await message.answer('Введите новую цену')
    await state.set_state(ItemAction.edit_price)


async def finish_edit_price_item(message: Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer('Нужно ввести число')
    else:
        context_data = await state.get_data()
        item_id = context_data['item_id']
        await update_item(price=price, item_id=item_id)
        await message.answer('Цена успешно обновлена')
        await state.clear()
        await message.answer(
            'Выберите действие',
            reply_markup=settings_keyboard
        )
        await state.set_state(AdminAction.action)


async def edit_item_category(message: Message):
    categories = await get_all_categories()
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category.name,
                       callback_data=SettingsCallback(action='Изменить категорию товара', model=None, model_id=category.id))
    builder.adjust(2)
    print(1)
    await message.answer(
        'Выберите категорию товара',
        reply_markup=builder.as_markup()
    )


async def edit_item_brand(call: CallbackQuery, callback_data: SettingsCallback):
    brands = await get_all_brands(callback_data.model_id)
    builder = InlineKeyboardBuilder()
    for brand in brands:
        builder.button(text=brand.name,
                       callback_data=SettingsCallback(action='Изменить бренд товара', model=None, model_id=brand.id))
    builder.adjust(2)
    await call.message.answer(
        'Выберите бренд товара',
        reply_markup=builder.as_markup()
    )


async def finish_edit_item_brand(call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback):
    context_data = await state.get_data()
    item_id = context_data['item_id']
    await update_item(item_id=item_id, brand_id=callback_data.model_id)
    await call.message.answer('Бренд и категория товара успешно изменена')
    await state.clear()
    await call.message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)


# ========== DELETE ========
async def start_delete(message: Message, state: FSMContext):
    context_data = await state.get_data()
    model = context_data['model']
    if model == 'Категория':
        builder = InlineKeyboardBuilder()
        categories = await get_all_categories()
        for category in categories:
            builder.button(text=category.name,
                           callback_data=SettingsCallback(action='Удаление',
                                                          model=model, model_id=category.id))
        builder.adjust(2)
        await message.answer('Выберите какую категорию вы хотите удалить', reply_markup=builder.as_markup())
    elif model == 'Бренд':
        builder = InlineKeyboardBuilder()
        categories = await get_all_categories()
        for category in categories:
            brands = await get_all_brands(category.id)
            for brand in brands:
                builder.button(text=f'{brand.name} ({category.name})',
                               callback_data=SettingsCallback(action='Удаление', model=model, model_id=brand.id))
        builder.adjust(2)
        await message.answer('Выберите какой бренд вы хотите удалить', reply_markup=builder.as_markup())
    elif model == 'Товар':
        builder = InlineKeyboardBuilder()
        items = await get_all_items()
        for items in items:
            builder.button(text=f'{items.name} ({items.brand.name})',
                           callback_data=SettingsCallback(action='Удаление', model=model, model_id=items.id))
        builder.adjust(2)
        await message.answer('Выберите какой товар вы хотите удалить', reply_markup=builder.as_markup())


async def confirm_delete(call: CallbackQuery, state: FSMContext, callback_data: SettingsCallback, bot: Bot):
    model_id = callback_data.model_id
    await state.update_data(model_id=model_id)
    model = callback_data.model
    if model == 'Категория':
        category = await get_category(model_id)
        await call.message.answer(
            f'Вы уверены что хотите удалить категорию: <b> {category.name} </b>?\n\n'
            f'При удалении категории удаляются <b>ВСЕ</b> бренды и товары которые были причислены к этой категории',
            reply_markup=delete_keyboard,
            parse_mode=ParseMode.HTML
        )
    if model == 'Бренд':
        brand = await get_brand(model_id)
        await call.message.answer(
            f'Вы уверены что хотите удалить бренд <b> {brand.name} ({brand.category.name}) </b>?\n\n'
            f'При удалении бренда удаляются <b>ВСЕ</b> товары которые были причислены к этому бренду',
            reply_markup=delete_keyboard,
            parse_mode=ParseMode.HTML
        )
    if model == 'Товар':
        item = await get_item(model_id)
        text = (f'<b>{item.name}</b> \n\n'
                f'{item.description}\n\n'
                f'Цена: <b>{item.price}</b>\n'
                f'Категория: <b>{item.brand.category.name}</b>\n'
                f'Бренд: <b>{item.brand.name}</b>')
        await bot.send_photo(chat_id=call.message.chat.id, photo=item.photo, caption=text, parse_mode=ParseMode.HTML)
        await call.message.answer(
            'Вы уверены что хотите удалить этот товар?',
            reply_markup=delete_keyboard
        )
    await state.set_state(Delete.confirm)


async def finish_delete(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer('Удаление не будет произведено')
    if message.text == 'Удалить':
        context_data = await state.get_data()
        model = context_data['model']
        model_id = context_data['model_id']
        if model == 'Категория':
            await delete_category(model_id)
        if model == 'Бренд':
            await delete_brand(model_id)
        if model == 'Товар':
            await delete_item(model_id)
        await message.answer('Удаление успешно произведено')
    await state.clear()
    await message.answer(
        'Выберите действие',
        reply_markup=settings_keyboard
    )
    await state.set_state(AdminAction.action)

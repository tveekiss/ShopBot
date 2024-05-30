from aiogram.types import Message, KeyboardButton, CallbackQuery
from app.database.requests import get_all_items, get_all_categories, get_items_by_category, get_item
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from app.commands.start import start_command


class PagesAction(StatesGroup):
    page = State()


class ItemList:
    def __init__(self, list_items):
        self.list_items = self.get_list(list_items)
        self.count_pages = len(self.list_items)
        self.page = 1

    @staticmethod
    def get_list(list_items):
        result_list = []
        page_list = []
        print(len(list_items))
        for item in list_items:
            if len(page_list) == 3:
                result_list.append(page_list)
                page_list = []
            page_list.append(item)
        if len(page_list) > 0:
            result_list.append(page_list)
        return result_list

    def current_page(self):
        return self.list_items[self.page - 1]

    def get_page(self):
        return f'Страница {self.page} из {self.count_pages}'

    def next_page(self, check):
        if self.page + 1 > self.count_pages:
            return False
        if not check:
            self.page += 1
        return True

    def previous_page(self, check):
        if self.page - 1 == 0:
            return False
        if not check:
            self.page -= 1
        return True


async def all_items(message: Message, state: FSMContext, bot: Bot):
    items = await get_all_items()
    list_class = ItemList(items)
    await state.update_data(list_class=list_class)
    await show_items(message, state, bot)


async def catalog(message: Message):
    categories = await get_all_categories()
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category.name, callback_data=f'category_{category.id}')
    builder.adjust(2)
    await message.answer('Выберите категорию', reply_markup=builder.as_markup())


async def catalog_items(call: CallbackQuery, state: FSMContext, bot: Bot):
    items = await get_items_by_category(int(call.data.split('_')[1]))
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=item.name, callback_data=f'ItemShow_{item.id}')
    builder.adjust(1)
    await call.message.answer('Выберите товар', reply_markup=builder.as_markup())


async def show_item(call: CallbackQuery, bot: Bot):
    item_id = int(call.data.split('_')[1])
    item = await get_item(item_id)
    builder_item = InlineKeyboardBuilder()
    builder_item.button(text='Добавить в корзину', callback_data=f'AddItem_{item.id}')
    text = (f'<b>{item.name}</b> \n\n'
            f'{item.description}\n\n'
            f'Цена: <b>{item.price}</b>\n'
            f'Категория: <b>{item.brand.category.name}</b>\n'
            f'Бренд: <b>{item.brand.name}</b>')
    await bot.send_photo(chat_id=call.from_user.id, photo=item.photo, caption=text, parse_mode=ParseMode.HTML,
                         reply_markup=builder_item.as_markup())




async def show_items(message: Message, state: FSMContext, bot: Bot):
    print(message.from_user.id)
    context_data = await state.get_data()
    list_class: ItemList = context_data['list_class']
    for item in list_class.current_page():
        builder_item = InlineKeyboardBuilder()
        builder_item.button(text='Добавить в корзину', callback_data=f'AddItem_{item.id}')
        text = (f'<b>{item.name}</b> \n\n'
                f'{item.description}\n\n'
                f'Цена: <b>{item.price}</b>\n'
                f'Категория: <b>{item.brand.category.name}</b>\n'
                f'Бренд: <b>{item.brand.name}</b>')
        await bot.send_photo(chat_id=message.from_user.id, photo=item.photo, caption=text, parse_mode=ParseMode.HTML,
                             reply_markup=builder_item.as_markup())
    builder = ReplyKeyboardBuilder()
    if list_class.previous_page(check=True):
        builder.add(KeyboardButton(text='Предыдущая'))
    if list_class.next_page(check=True):
        builder.add(KeyboardButton(text='Следующая'))
    builder.row(KeyboardButton(text='Главная'))
    await bot.send_message(chat_id=message.from_user.id, text=list_class.get_page(),
                           reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(PagesAction.page)


async def check_action(message: Message, state: FSMContext, bot: Bot):
    match message.text:
        case 'Следующая':
            context_data = await state.get_data()
            list_class = context_data['list_class']
            list_class.next_page(check=False)
        case 'Предыдущая':
            context_data = await state.get_data()
            list_class = context_data['list_class']
            list_class.previous_page(check=False)
        case 'Главная':
            await state.clear()
            await start_command(message)
            return
    await show_items(message, state, bot)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

settings_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Добавить'
        ),
        KeyboardButton(
            text='Изменить'
        ),
        KeyboardButton(
            text='Удалить'
        )
    ], [
        KeyboardButton(
            text='Назад'
        )
    ]
], resize_keyboard=True)


settings_choice_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Категория'
        ),
        KeyboardButton(
            text='Бренд'
        ),
        KeyboardButton(
            text='Товар'
        )
    ], [
        KeyboardButton(
            text='Назад'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)

settings_edit_brand = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Название'
        ),
        KeyboardButton(
            text='Категория'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)

settings_edit_item = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Название'
        ),
        KeyboardButton(
            text='Описание'
        ),
    ], [
        KeyboardButton(
            text='Изображение'
        ),
        KeyboardButton(
            text='Цена'
        ),
        KeyboardButton(
            text=r'Бренд\Категория'
        )
    ], [
        KeyboardButton(
            text='Назад'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)


delete_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Удалить'
        ),
    ], [
        KeyboardButton(
            text='Отмена'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)


start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Все товары'
        ),
        KeyboardButton(
            text='Каталог'
        )
    ], [
        KeyboardButton(
            text='Корзина'
        )
    ]
], resize_keyboard=True)


basket_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Оформить заказ'
        )
    ], [
        KeyboardButton(
            text='Удалить товар'
        ),
        KeyboardButton(
            text='Изменить количество'
        ),
        KeyboardButton(
            text='Очистить корзину'
        )
    ], [
        KeyboardButton(
            text='Главная'
        )
    ]
], resize_keyboard=True)

quantity_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='1'
        )
    ], [
        KeyboardButton(
            text='2'
        ),
        KeyboardButton(
            text='3'
        )
    ]
], resize_keyboard=True)

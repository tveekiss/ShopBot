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
            text='Бренд'
        )
    ]
])
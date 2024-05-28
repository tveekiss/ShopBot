from aiogram import Router, F
from aiogram.filters import Command

from commands.start import start_command
from commands.settings import (settings_command, AdminAction,
                               add_action, AdminChoice, settings_redirection, finish_category, CategoryAction,
                               BrandAction, set_brand, SettingsCallback, finish_brand, ItemAction, set_description,
                               set_price, set_item_category, set_item_brand, finish_item, set_photo, edit_category,
                               finish_edit_category, choice_edit_brand, edit_brand,
                               finish_edit_name_brand, finish_edit_category_brand,
                               choice_edit_item, edit_item, finish_edit_name_item, finish_edit_desc_item,
                               finish_edit_image_item, finish_edit_price_item, edit_item_brand, finish_edit_item_brand,
                               confirm_delete, finish_delete, Delete)
from app.all_items import all_items, check_action, PagesAction, catalog, catalog_items
from app.commands.token import get_token
from app.basket import (basket_create, basket_main, basket_all_delete, basket_delete, basket_item_delete,
                        Quantity, call_change_quantity, finish_quantity, change_quantity)


def register_handlers(router: Router):
    router.message.register(add_action, AdminAction.action)
    router.message.register(settings_redirection, AdminChoice.choice)

    router.callback_query.register(confirm_delete, SettingsCallback.filter(F.action == 'Удаление'))
    router.message.register(finish_delete, Delete.confirm)

    router.message.register(finish_category, CategoryAction.name)

    router.message.register(set_brand, BrandAction.name)
    router.callback_query.register(finish_brand, SettingsCallback.filter(F.model == 'Бренд'))

    router.message.register(set_description, ItemAction.name)
    router.message.register(set_photo, ItemAction.description)
    router.message.register(set_price, ItemAction.photo)
    router.callback_query.register(finish_item, SettingsCallback.filter(F.action == 'Бренд'))
    router.message.register(set_item_category, ItemAction.price)
    router.callback_query.register(set_item_brand, SettingsCallback.filter(F.model == 'Товар'))

    router.callback_query.register(edit_category, SettingsCallback.filter(F.action == 'Изменить модель категории'))
    router.message.register(finish_edit_category, CategoryAction.edit_name)

    router.callback_query.register(choice_edit_brand, SettingsCallback.filter(F.action == 'Изменить модель бренда'))
    router.message.register(edit_brand, BrandAction.edit_choice)
    router.message.register(finish_edit_name_brand, BrandAction.edit_name)
    router.callback_query.register(finish_edit_category_brand,
                                   SettingsCallback.filter(F.action == 'Изменить категорию бренда'))

    router.callback_query.register(choice_edit_item, SettingsCallback.filter(F.action == 'Изменить модель товара'))
    router.message.register(edit_item, ItemAction.edit_choice)

    router.message.register(finish_edit_name_item, ItemAction.edit_name)

    router.message.register(finish_edit_desc_item, ItemAction.edit_description)

    router.message.register(finish_edit_image_item, ItemAction.edit_photo)

    router.message.register(finish_edit_price_item, ItemAction.edit_price)

    router.callback_query.register(edit_item_brand, SettingsCallback.filter(F.action == 'Изменить категорию товара'))
    router.callback_query.register(finish_edit_item_brand, SettingsCallback.filter(F.action == 'Изменить бренд товара'))

    router.message.register(all_items, F.text == 'Все товары')
    router.message.register(catalog, F.text == 'Каталог')
    router.callback_query.register(catalog_items, F.data.startswith('category_'))
    router.message.register(check_action, PagesAction.page)
    router.message.register(basket_main, F.text == 'Корзина')
    router.message.register(start_command, F.text == 'Главная')
    router.message.register(basket_all_delete, F.text == 'Очистить корзину')
    router.message.register(basket_item_delete, F.text == 'Удалить товар')
    router.callback_query.register(basket_delete, F.data.startswith('BasketDelete_'))
    router.callback_query.register(basket_create, F.data.startswith('AddItem_'))
    router.callback_query.register(call_change_quantity, F.data.startswith('ChangeQuantity_'))
    router.message.register(change_quantity, F.text == 'Изменить количество')
    router.message.register(finish_quantity, Quantity.edit_quantity)
    router.message.register(basket_create, Quantity.quantity)


def register_command_handlers(router: Router):
    router.message.register(start_command, Command(commands=['start']))
    router.message.register(settings_command, Command(commands=['settings']))
    router.message.register(get_token, Command(commands=['token']))

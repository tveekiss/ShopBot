from aiogram import Router, F
from aiogram.filters import Command

from commands.start import start_command
from commands.settings import (settings_command, AdminAction,
                               add_action, AdminChoice, settings_redirection, finish_category, CategoryAction,
                               BrandAction, set_brand, SettingsCallback, finish_brand, ItemAction, set_description,
                               set_price, set_item_category, set_item_brand, finish_item, set_photo)
from app.all_items import all_items


def register_handlers(router: Router):
    router.message.register(add_action, AdminAction.action)
    router.message.register(settings_redirection, AdminChoice.choice)

    router.message.register(finish_category, CategoryAction.name)

    router.message.register(set_brand, BrandAction.name)
    router.callback_query.register(finish_brand, SettingsCallback.filter(F.model == 'Бренд'))

    router.message.register(set_description, ItemAction.name)
    router.message.register(set_photo, ItemAction.description)
    router.message.register(set_price, ItemAction.photo)
    router.callback_query.register(finish_item, SettingsCallback.filter(F.action == 'Бренд'))
    router.message.register(set_item_category, ItemAction.price)
    router.callback_query.register(set_item_brand, SettingsCallback.filter(F.model == 'Товар'))

    router.message.register(all_items, F.text == 'Все товары')


def register_command_handlers(router: Router):
    router.message.register(start_command, Command(commands=['start']))
    router.message.register(settings_command, Command(commands=['settings']))


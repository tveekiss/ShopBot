from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands_list(bot):
    commands = [
        BotCommand(
            command='start',
            description='Запуск бота'
        ),
        BotCommand(
            command='help',
            description='Информация о боте'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())

from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands_list(bot):
    commands = [
        BotCommand(
            command='start',
            description='Запуск бота'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())

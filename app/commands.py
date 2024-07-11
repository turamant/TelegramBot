from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command
from .handlers import command_start_handler, aggregate_handler, echo_handler

def setup_commands(dp: Dispatcher) -> None:
    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(aggregate_handler, Command("aggregate"))
    dp.message.register(echo_handler)

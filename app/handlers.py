import logging
import json
from typing import Dict, List, Any
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import bold
from app.aggregator import aggregate_data


async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение с инструкцией по использованию команды /aggregate.
    Args:
        message (Message): Объект сообщения, содержащий команду /start.
    """
    await message.answer(f"Привет, {bold(message.from_user.full_name)}!\n\n"
                         "Отправь мне JSON сообщение в формате:\n"
                         "```json\n"
                         "/aggregate "
                         "{\n"
                         "  \"dt_from\": \"2022-09-01T00:00:00\",\n"
                         "  \"dt_upto\": \"2022-12-31T23:59:00\",\n"
                         "  \"group_type\": \"month\"\n"
                         "}\n"
                         "```")
                         

async def aggregate_handler(message: Message) -> None:
     """
    Обработчик команды /aggregate.
    Принимает JSON-сообщение с параметрами для агрегации данных, вызывает функцию aggregate_data
    и отправляет результат в виде сообщения.
    Args:
        message (Message): Объект сообщения, содержащий команду /aggregate.
    """
    logging.info("Принял /сгруппировал")
    try:
        input_data = json.loads(message.text.split(" ", 1)[1])
        dt_from = input_data["dt_from"]
        dt_upto = input_data["dt_upto"]
        group_type = input_data["group_type"]
        result = await aggregate_data(dt_from, dt_upto, group_type)

        if not result["labels"]:
            await message.answer("Данные не найдены.")
            return

        chart_data = {
            "dataset": result["dataset"],
            "labels": result["labels"]
        }
        await send_message_parts(message, chart_data)

    except (ValueError, KeyError):
        await message.answer("Неверный формат запроса. Используйте формат, указанный в инструкции.")
    except Exception as e:
        logging.error(f"Ошибка в agregate_handler: {str(e)}")
        await message.answer("Произошла ошибка при обработке запроса. Пробуйте еще раз.")


async def send_message_parts(message: Message, data: Dict[str, List[Any]]) -> None:
    """
    Отправляет сообщение с данными, разбивая его на части, если оно слишком длинное.
    Args:
        message (Message): Объект сообщения, которому нужно отправить данные.
        data (Dict[str, List[Any]]): Словарь с данными для отправки.
    """
    current_part = str(data)
    if len(current_part) > 4096:
        for i in range(0, len(current_part), 4096):
            await message.answer(current_part[i:i+4096])
    else:
        await message.answer(current_part)


async def echo_handler(message: Message) -> None:
    """
    Обработчик эхо-сообщений.
    Отправляет копию полученного сообщения обратно пользователю.
    Args:
        message (Message): Объект сообщения, которое нужно отразить.
    """
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Хорошая попытка!")

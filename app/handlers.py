import logging
import json
from typing import Dict, List, Any

from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import bold

from app.aggregator import aggregate_data

async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {bold(message.from_user.full_name)}!\n\n"
                         "Send me a JSON message with the following format:\n"
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
    This handler receives messages with `/aggregate` command and processes the JSON input
    """
    logging.info("Received /aggregate command")
    try:
        input_data = json.loads(message.text.split(" ", 1)[1])
        dt_from = input_data["dt_from"]
        dt_upto = input_data["dt_upto"]
        group_type = input_data["group_type"]
        result = await aggregate_data(dt_from, dt_upto, group_type)
        logging.info(f"Result from aggregate_data: {result}")

        if not result["labels"]:
            await message.answer("Данные не найдены.")
            return

        chart_data = {
            "dataset": result["dataset"],
            "labels": result["labels"]
        }

        logging.info(f"Final chart data: {chart_data}")
        await send_message_parts(message, chart_data)

    except (ValueError, KeyError):
        await message.answer("Неверный формат запроса. Пожалуйста, используйте формат, указанный в инструкции.")
    except Exception as e:
        logging.error(f"Error in handle_user_request: {str(e)}")
        await message.answer("Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.")

async def send_message_parts(message: Message, data: Dict[str, List[Any]]) -> None:
    """
    Разбивает ответ на части, чтобы не превышать лимит Telegram.
    """
    current_part = str(data)
    if len(current_part) > 4096:
        for i in range(0, len(current_part), 4096):
            await message.answer(current_part[i:i+4096])
    else:
        await message.answer(current_part)

async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")

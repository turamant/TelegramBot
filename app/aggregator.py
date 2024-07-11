import os
import logging
import re
from datetime import datetime
from typing import Dict, List

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URI = f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/{os.getenv('MONGO_DB')}"

client = AsyncIOMotorClient(MONGODB_URI)
db = client['sampleDB']
collection = db['sample_collection']

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

BATCH_SIZE = 20

def parse_datetime(dt_str: str) -> datetime:
    """
    Парсит строку даты и времени в формате ISO 8601 (YYYY-MM-DDThh:mm:ss) и возвращает объект datetime.
    Args:
        dt_str (str): Строка даты и времени в формате ISO 8601.
    Returns:
        datetime: Объект datetime, соответствующий входной строке.
    Raises:
        ValueError: Если входная строка имеет неверный формат.
    """
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})", dt_str)
    if match:
        return datetime(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            int(match.group(4)),
            int(match.group(5)),
            int(match.group(6))
        )
    else:
        raise ValueError(f"Неверная строка даты и времени: {dt_str}")

async def aggregate_data(dt_from: str, dt_upto: str, group_type: str) -> Dict[str, List[float]]:
     """
    Агрегирует данные из коллекции MongoDB в заданном диапазоне дат и времени, группируя их по часам, дням или месяцам.
    Args:
        dt_from (str): Начальная дата и время в формате ISO 8601.
        dt_upto (str): Конечная дата и время в формате ISO 8601.
        group_type (str): Тип группировки: "hour", "day" или "month".
    Returns:
        Dict[str, List[float]]: Словарь с ключами "labels" и "dataset", содержащий метки и агрегированные данные соответственно.
    Raises:
        Exception: Если возникает ошибка при агрегации данных.
    """
    try:
        dt_from_dt = parse_datetime(dt_from)
        dt_upto_dt = parse_datetime(dt_upto)

        pipeline = [
            {
                "$match": {
                    "dt": {
                        "$gte": dt_from_dt,
                        "$lt": dt_upto_dt
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": {
                                "hour": "%Y-%m-%dT%H:00:00",
                                "day": "%Y-%m-%dT00:00:00",
                                "month": "%Y-%m"
                            }[group_type],
                            "date": "$dt"
                        }
                    },
                    "dataset": {"$sum": "$value"}
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            }
        ]

        result = await collection.aggregate(pipeline).to_list(length=None)
        chart_data = {
            "labels": [item["_id"] for item in result],
            "dataset": [item["dataset"] for item in result]
        }
        return chart_data
    except Exception as e:
        logging.error(f"Ошибка аггрегации данных: {e}")
        raise

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
        raise ValueError(f"Invalid datetime string: {dt_str}")

async def aggregate_data(dt_from: str, dt_upto: str, group_type: str) -> Dict[str, List[float]]:
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
        logging.error(f"Error in aggregate_data: {e}")
        raise

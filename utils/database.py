import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "yoyo_db")

if not MONGO_URL:
    raise ValueError("MONGO_URL is missing. Set it in .env")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

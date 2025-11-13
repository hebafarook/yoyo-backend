import os
from motor.motor_asyncio import AsyncIOMotorClient

# ---------------------------
# Load configuration
# ---------------------------

# MongoDB connection string from environment variables
MONGO_URL = os.getenv("MONGO_URL")

# Database name (defaults to yoyo_db if not provided)
DB_NAME = os.getenv("DB_NAME", "yoyo_db")

# ---------------------------
# Validate environment
# ---------------------------

if not MONGO_URL:
    raise ValueError(
        "❌ MONGO_URL is missing. Set it in your .env file or your hosting environment variables."
    )

# ---------------------------
# Initialize MongoDB client
# ---------------------------

# Create async MongoDB client
client = AsyncIOMotorClient(MONGO_URL)

# Select the database you will use
db = client[DB_NAME]

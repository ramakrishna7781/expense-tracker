from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables from backend/.env
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URL or not DB_NAME:
    raise ValueError("Mongo URL or DB_NAME is not set in .env")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
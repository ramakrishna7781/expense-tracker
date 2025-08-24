# import os
# from motor.motor_asyncio import AsyncIOMotorClient

# MONGO_URL = os.getenv("MONGO_URL")
# DB_NAME = os.getenv("DB_NAME")

# client = AsyncIOMotorClient(MONGO_URL)
# db = client[DB_NAME]


from dotenv import load_dotenv # type: ignore
import os
from motor.motor_asyncio import AsyncIOMotorClient

# load_dotenv()  # <-- must be called first
load_dotenv(dotenv_path='backend/.env')

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URL or not DB_NAME:
    raise ValueError("Mongo URL or DB_NAME is not set in .env")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

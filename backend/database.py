from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "FoodHub-SE-MiniProj")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

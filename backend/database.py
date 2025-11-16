from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "FoodHub-SE-MiniProj"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

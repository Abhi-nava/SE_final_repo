"""
Populate Delivery Agents Script
Links delivery_agents with existing users collection (role='delivery')
Ensures password and structure match existing models.
"""

import asyncio
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from security import hash_password

# MongoDB Configuration
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "FoodFlow-SE-MiniProj"

# Use same password hash function from security.py
COMMON_PASSWORD = hash_password("password123")

# Sample delivery agents with full details
DELIVERY_AGENTS_DATA = [
    {
        "email": "delivery1@example.com",
        "phone": "9111111122",
        "full_name": "Ravi Kumar",
        "vehicle_type": "bike",
        "vehicle_number": "KA01AB1234",
        "vehicle_registration": "2023-01-15",
        "license_number": "DL0123456789",
        "insurance_document": "doc123",
        "bank_account": "1234567890",
        "ifsc_code": "SBIN0001234",
        "status": "online",
        "rating": 4.8,
        "total_deliveries": 250,
        "current_location": {"lat": 12.9352, "lng": 77.6245},
        "is_verified": True,
    },
    {
        "email": "delivery2@example.com",
        "phone": "9222222233",
        "full_name": "Sanjay Sharma",
        "vehicle_type": "scooter",
        "vehicle_number": "KA02CD5678",
        "vehicle_registration": "2023-02-20",
        "license_number": "DL9876543210",
        "insurance_document": "doc456",
        "bank_account": "0987654321",
        "ifsc_code": "HDFC0005678",
        "status": "offline",
        "rating": 4.6,
        "total_deliveries": 180,
        "current_location": {"lat": 12.9716, "lng": 77.5946},
        "is_verified": True,
    },
    {
        "email": "delivery3@example.com",
        "phone": "9333333344",
        "full_name": "Arun Mehta",
        "vehicle_type": "bike",
        "vehicle_number": "KA03EF9012",
        "vehicle_registration": "2023-03-10",
        "license_number": "DL5555555555",
        "insurance_document": "doc789",
        "bank_account": "5555555555",
        "ifsc_code": "ICIC0009012",
        "status": "on_delivery",
        "rating": 4.9,
        "total_deliveries": 320,
        "current_location": {"lat": 12.9352, "lng": 77.6245},
        "is_verified": True,
    },
]


async def populate_delivery_agents():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    try:
        print(f"Connected to MongoDB at {MONGODB_URL}")
        await client.admin.command("ping")

        users_col = db["users"]
        agents_col = db["delivery_agents"]

        for agent in DELIVERY_AGENTS_DATA:
            existing_user = await users_col.find_one({"email": agent["email"]})

            # Create user if not present
            if not existing_user:
                user_doc = {
                    "_id": ObjectId(),
                    "email": agent["email"],
                    "phone": agent["phone"],
                    "full_name": agent["full_name"],
                    "password": COMMON_PASSWORD,
                    "role": "delivery",
                    "address": "Bangalore, India",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "is_active": True,
                }
                await users_col.insert_one(user_doc)
                print(f"✅ Created user: {agent['email']}")
            else:
                user_doc = existing_user
                print(f"ℹ️  Existing user found: {agent['email']}")

            # Create corresponding delivery_agent record
            delivery_agent_doc = {
                "_id": ObjectId(),
                "user_id": user_doc["_id"],
                "vehicle_type": agent["vehicle_type"],
                "vehicle_number": agent["vehicle_number"],
                "vehicle_registration": agent["vehicle_registration"],
                "license_number": agent["license_number"],
                "insurance_document": agent["insurance_document"],
                "bank_account": agent["bank_account"],
                "ifsc_code": agent["ifsc_code"],
                "status": agent["status"],
                "rating": agent["rating"],
                "total_deliveries": agent["total_deliveries"],
                "current_location": agent["current_location"],
                "is_verified": agent["is_verified"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "email": agent["email"],
                "password": COMMON_PASSWORD,
                "role": "delivery",
            }

            # Avoid duplicates in delivery_agents
            existing_agent = await agents_col.find_one({"email": agent["email"]})
            if not existing_agent:
                await agents_col.insert_one(delivery_agent_doc)
                print(f"🚴 Added delivery agent: {agent['email']}")
            else:
                print(f"⚠️ Delivery agent already exists: {agent['email']}")

        print("\n✅ Delivery agent population completed successfully!")

    except Exception as e:
        print(f"❌ Error populating delivery agents: {e}")

    finally:
        client.close()
        print("🔒 MongoDB connection closed.")


if __name__ == "__main__":
    asyncio.run(populate_delivery_agents())

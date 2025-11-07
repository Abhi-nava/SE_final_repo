"""
MongoDB Database Population Script for FoodHub-SE-MiniProj
This script creates collections, sets up indexes, and populates sample data
for testing the food delivery application.

Usage: python scripts/populate_db.py
"""

import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from bson import ObjectId
from security import hash_password

hashed = hash_password("your_password")

from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "FoodHub-SE-MiniProj"

# Sample data
SAMPLE_CUSTOMERS = [
    {
        "_id": ObjectId(),
        "email": "customer1@example.com",
        "phone": "9876543210",
        "full_name": "Rajesh Kumar",
        "password": hash_password("password123"),
        "role": "customer",
        "address": "123 MG Road, Bangalore",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "_id": ObjectId(),
        "email": "customer2@example.com",
        "phone": "9876543211",
        "full_name": "Priya Singh",
        "password": hash_password("password123"),
        "role": "customer",
        "address": "456 Brigade Road, Bangalore",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "_id": ObjectId(),
        "email": "customer3@example.com",
        "phone": "9876543212",
        "full_name": "Amit Patel",
        "password": hash_password("password123"),
        "role": "customer",
        "address": "789 Whitefield, Bangalore",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
    },
]

SAMPLE_RESTAURANTS = [
    {
        "_id": ObjectId(),
        "owner_id": ObjectId(),
        "name": "Spice Kitchen",
        "description": "Authentic Indian cuisine with traditional recipes",
        "phone": "9111111111",
        "address": "123 Fort Road, Bangalore",
        "city": "Bangalore",
        "postal_code": "560034",
        "cuisine_types": ["Indian", "North Indian", "South Indian"],
        "image_url": "https://via.placeholder.com/300x200?text=Spice+Kitchen",
        "opening_time": "09:00",
        "closing_time": "23:00",
        "rating": 4.5,
        "total_ratings": 120,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "owner_id": ObjectId(),
        "name": "Pizza Palace",
        "description": "Delicious wood-fired pizzas and Italian pasta",
        "phone": "9222222222",
        "address": "456 Koramangala, Bangalore",
        "city": "Bangalore",
        "postal_code": "560034",
        "cuisine_types": ["Italian", "Pizza", "Pasta"],
        "image_url": "https://via.placeholder.com/300x200?text=Pizza+Palace",
        "opening_time": "11:00",
        "closing_time": "23:30",
        "rating": 4.3,
        "total_ratings": 95,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "owner_id": ObjectId(),
        "name": "Burger Barn",
        "description": "Gourmet burgers with premium quality meat",
        "phone": "9333333333",
        "address": "789 Indiranagar, Bangalore",
        "city": "Bangalore",
        "postal_code": "560038",
        "cuisine_types": ["Fast Food", "Burgers", "American"],
        "image_url": "https://via.placeholder.com/300x200?text=Burger+Barn",
        "opening_time": "10:00",
        "closing_time": "22:00",
        "rating": 4.1,
        "total_ratings": 78,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "owner_id": ObjectId(),
        "name": "Sushi Garden",
        "description": "Fresh Japanese sushi and authentic ramen",
        "phone": "9444444444",
        "address": "321 JP Nagar, Bangalore",
        "city": "Bangalore",
        "postal_code": "560078",
        "cuisine_types": ["Japanese", "Sushi", "Asian"],
        "image_url": "https://via.placeholder.com/300x200?text=Sushi+Garden",
        "opening_time": "12:00",
        "closing_time": "22:30",
        "rating": 4.7,
        "total_ratings": 150,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]

SAMPLE_MENU_ITEMS = {
    0: [  # Spice Kitchen
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[0]["_id"],
            "name": "Butter Chicken",
            "description": "Tender chicken in creamy tomato-butter sauce",
            "price": 320.00,
            "category": "Main Course",
            "image_url": "https://via.placeholder.com/200x150?text=Butter+Chicken",
            "availability": "available",
            "is_vegetarian": False,
            "is_vegan": False,
            "preparation_time": 25,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[0]["_id"],
            "name": "Paneer Tikka",
            "description": "Marinated cottage cheese grilled to perfection",
            "price": 280.00,
            "category": "Appetizer",
            "image_url": "https://via.placeholder.com/200x150?text=Paneer+Tikka",
            "availability": "available",
            "is_vegetarian": True,
            "is_vegan": False,
            "preparation_time": 20,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[0]["_id"],
            "name": "Biryani",
            "description": "Fragrant rice cooked with meat and spices",
            "price": 350.00,
            "category": "Main Course",
            "image_url": "https://via.placeholder.com/200x150?text=Biryani",
            "availability": "available",
            "is_vegetarian": False,
            "is_vegan": False,
            "preparation_time": 30,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[0]["_id"],
            "name": "Dal Makhani",
            "description": "Creamy lentils cooked overnight",
            "price": 200.00,
            "category": "Main Course",
            "image_url": "https://via.placeholder.com/200x150?text=Dal+Makhani",
            "availability": "available",
            "is_vegetarian": True,
            "is_vegan": False,
            "preparation_time": 20,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ],
    1: [  # Pizza Palace
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[1]["_id"],
            "name": "Margherita Pizza",
            "description": "Classic pizza with tomato, mozzarella, and basil",
            "price": 350.00,
            "category": "Pizza",
            "image_url": "https://via.placeholder.com/200x150?text=Margherita",
            "availability": "available",
            "is_vegetarian": True,
            "is_vegan": False,
            "preparation_time": 25,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[1]["_id"],
            "name": "Pepperoni Pizza",
            "description": "Spicy pepperoni with cheese",
            "price": 400.00,
            "category": "Pizza",
            "image_url": "https://via.placeholder.com/200x150?text=Pepperoni",
            "availability": "available",
            "is_vegetarian": False,
            "is_vegan": False,
            "preparation_time": 25,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[1]["_id"],
            "name": "Pasta Carbonara",
            "description": "Creamy pasta with bacon and parmesan",
            "price": 320.00,
            "category": "Pasta",
            "image_url": "https://via.placeholder.com/200x150?text=Carbonara",
            "availability": "available",
            "is_vegetarian": False,
            "is_vegan": False,
            "preparation_time": 20,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ],
    2: [  # Burger Barn
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[2]["_id"],
            "name": "Classic Burger",
            "description": "Premium beef patty with lettuce and tomato",
            "price": 250.00,
            "category": "Burgers",
            "image_url": "https://via.placeholder.com/200x150?text=Classic+Burger",
            "availability": "available",
            "is_vegetarian": False,
            "is_vegan": False,
            "preparation_time": 15,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[2]["_id"],
            "name": "Cheese Burger",
            "description": "Double patty with cheddar cheese",
            "price": 300.00,
            "category": "Burgers",
            "image_url": "https://via.placeholder.com/200x150?text=Cheese+Burger",
            "availability": "available",
            "is_vegetarian": False,
            "is_vegan": False,
            "preparation_time": 18,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[2]["_id"],
            "name": "French Fries",
            "description": "Crispy golden fries with seasoning",
            "price": 120.00,
            "category": "Sides",
            "image_url": "https://via.placeholder.com/200x150?text=Fries",
            "availability": "available",
            "is_vegetarian": True,
            "is_vegan": True,
            "preparation_time": 10,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ],
    3: [  # Sushi Garden
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[3]["_id"],
            "name": "California Roll",
            "description": "Crab, avocado, and cucumber roll",
            "price": 280.00,
            "category": "Sushi",
            "image_url": "https://via.placeholder.com/200x150?text=California+Roll",
            "availability": "available",
            "is_vegetarian": False,
            "is_vegan": False,
            "preparation_time": 15,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[3]["_id"],
            "name": "Vegetable Roll",
            "description": "Fresh vegetables in a crispy roll",
            "price": 180.00,
            "category": "Sushi",
            "image_url": "https://via.placeholder.com/200x150?text=Veg+Roll",
            "availability": "available",
            "is_vegetarian": True,
            "is_vegan": False,
            "preparation_time": 12,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "_id": ObjectId(),
            "restaurant_id": SAMPLE_RESTAURANTS[3]["_id"],
            "name": "Chicken Ramen",
            "description": "Hearty noodle soup with chicken",
            "price": 320.00,
            "category": "Ramen",
            "image_url": "https://via.placeholder.com/200x150?text=Ramen",
            "availability": "available",
            "is_vegetarian": False,
            "is_vegan": False,
            "preparation_time": 20,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ],
}

SAMPLE_DELIVERY_AGENTS = [
    {
        "_id": ObjectId(),
        "user_id": ObjectId(),
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "user_id": ObjectId(),
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "user_id": ObjectId(),
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]

SAMPLE_ORDERS = [
    {
        "_id": ObjectId(),
        "customer_id": SAMPLE_CUSTOMERS[0]["_id"],
        "restaurant_id": SAMPLE_RESTAURANTS[0]["_id"],
        "items": [
            {
                "menu_item_id": str(SAMPLE_MENU_ITEMS[0][0]["_id"]),
                "name": "Butter Chicken",
                "quantity": 1,
                "price": 320.00,
            },
            {
                "menu_item_id": str(SAMPLE_MENU_ITEMS[0][3]["_id"]),
                "name": "Dal Makhani",
                "quantity": 1,
                "price": 200.00,
            },
        ],
        "subtotal": 520.00,
        "delivery_fee": 50.00,
        "discount": 0.0,
        "total": 570.00,
        "status": "delivered",
        "delivery_address": "123 MG Road, Bangalore",
        "delivery_phone": "9876543210",
        "payment_method": "card",
        "delivery_agent_id": str(SAMPLE_DELIVERY_AGENTS[0]["_id"]),
        "estimated_delivery_time": 45,
        "created_at": datetime.utcnow() - timedelta(hours=2),
        "updated_at": datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "customer_id": SAMPLE_CUSTOMERS[1]["_id"],
        "restaurant_id": SAMPLE_RESTAURANTS[1]["_id"],
        "items": [
            {
                "menu_item_id": str(SAMPLE_MENU_ITEMS[1][0]["_id"]),
                "name": "Margherita Pizza",
                "quantity": 1,
                "price": 350.00,
            },
        ],
        "subtotal": 350.00,
        "delivery_fee": 40.00,
        "discount": 50.00,
        "total": 340.00,
        "status": "confirmed",
        "delivery_address": "456 Brigade Road, Bangalore",
        "delivery_phone": "9876543211",
        "payment_method": "upi",
        "delivery_agent_id": None,
        "estimated_delivery_time": None,
        "created_at": datetime.utcnow() - timedelta(minutes=15),
        "updated_at": datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "customer_id": SAMPLE_CUSTOMERS[2]["_id"],
        "restaurant_id": SAMPLE_RESTAURANTS[2]["_id"],
        "items": [
            {
                "menu_item_id": str(SAMPLE_MENU_ITEMS[2][1]["_id"]),
                "name": "Cheese Burger",
                "quantity": 2,
                "price": 300.00,
            },
            {
                "menu_item_id": str(SAMPLE_MENU_ITEMS[2][2]["_id"]),
                "name": "French Fries",
                "quantity": 1,
                "price": 120.00,
            },
        ],
        "subtotal": 720.00,
        "delivery_fee": 50.00,
        "discount": 0.0,
        "total": 770.00,
        "status": "in_transit",
        "delivery_address": "789 Whitefield, Bangalore",
        "delivery_phone": "9876543212",
        "payment_method": "wallet",
        "delivery_agent_id": str(SAMPLE_DELIVERY_AGENTS[2]["_id"]),
        "estimated_delivery_time": 20,
        "created_at": datetime.utcnow() - timedelta(minutes=30),
        "updated_at": datetime.utcnow(),
    },
]

SAMPLE_RATINGS = [
    {
        "_id": ObjectId(),
        "order_id": str(SAMPLE_ORDERS[0]["_id"]),
        "customer_id": str(SAMPLE_CUSTOMERS[0]["_id"]),
        "restaurant_id": str(SAMPLE_RESTAURANTS[0]["_id"]),
        "delivery_agent_id": str(SAMPLE_DELIVERY_AGENTS[0]["_id"]),
        "restaurant_rating": 5,
        "delivery_rating": 5,
        "restaurant_review": "Excellent food and service! Highly recommended.",
        "delivery_review": "Very fast delivery, agent was polite.",
        "food_quality": 5,
        "delivery_speed": 5,
        "packaging_quality": 4,
        "created_at": datetime.utcnow(),
    },
]


async def create_indexes(db):
    """Create all necessary indexes for optimal query performance"""
    print("Creating indexes...")
    
    # Users collection indexes
    await db["users"].create_index("email", unique=True)
    await db["users"].create_index("phone")
    await db["users"].create_index("role")
    
    # Restaurants collection indexes
    await db["restaurants"].create_index("owner_id")
    await db["restaurants"].create_index("city")
    await db["restaurants"].create_index("cuisine_types")
    
    # Menu items collection indexes
    await db["menu_items"].create_index("restaurant_id")
    await db["menu_items"].create_index("category")
    await db["menu_items"].create_index([("restaurant_id", 1), ("category", 1)])
    
    # Orders collection indexes
    await db["orders"].create_index("customer_id")
    await db["orders"].create_index("restaurant_id")
    await db["orders"].create_index("delivery_agent_id")
    await db["orders"].create_index("status")
    await db["orders"].create_index("created_at")
    
    # Delivery agents collection indexes
    await db["delivery_agents"].create_index("user_id")
    await db["delivery_agents"].create_index("status")
    
    # Ratings collection indexes
    await db["ratings"].create_index("order_id")
    await db["ratings"].create_index("customer_id")
    await db["ratings"].create_index("restaurant_id")
    await db["ratings"].create_index("delivery_agent_id")
    
    print("Indexes created successfully!")


async def populate_database():
    """Main function to populate the database"""
    client = AsyncIOMotorClient(MONGODB_URL)
    
    try:
        # Connect to database
        db = client[DATABASE_NAME]
        
        # Test connection
        await client.admin.command("ping")
        print(f"Connected to MongoDB at {MONGODB_URL}")
        print(f"Using database: {DATABASE_NAME}")
        
        # Drop existing collections for fresh start
        print("\nDropping existing collections...")
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].drop()
            print(f"  Dropped {collection}")
        
        # Create indexes
        await create_indexes(db)
        
        # Insert users
        print("\nInserting sample users...")
        users_result = await db["users"].insert_many(SAMPLE_CUSTOMERS)
        print(f"  Inserted {len(users_result.inserted_ids)} customers")
        
        # Insert restaurants
        print("\nInserting sample restaurants...")
        restaurants_result = await db["restaurants"].insert_many(SAMPLE_RESTAURANTS)
        print(f"  Inserted {len(restaurants_result.inserted_ids)} restaurants")
        
        # Insert menu items
        print("\nInserting menu items...")
        menu_items = []
        for restaurant_idx, items in SAMPLE_MENU_ITEMS.items():
            menu_items.extend(items)
        menu_items_result = await db["menu_items"].insert_many(menu_items)
        print(f"  Inserted {len(menu_items_result.inserted_ids)} menu items")
        
        # Insert delivery agents
        print("\nInserting delivery agents...")
        delivery_agents_result = await db["delivery_agents"].insert_many(
            SAMPLE_DELIVERY_AGENTS
        )
        print(f"  Inserted {len(delivery_agents_result.inserted_ids)} delivery agents")
        
        # Insert orders
        print("\nInserting sample orders...")
        orders_result = await db["orders"].insert_many(SAMPLE_ORDERS)
        print(f"  Inserted {len(orders_result.inserted_ids)} orders")
        
        # Insert ratings
        print("\nInserting ratings...")
        ratings_result = await db["ratings"].insert_many(SAMPLE_RATINGS)
        print(f"  Inserted {len(ratings_result.inserted_ids)} ratings")
        
        # Print summary
        print("\n" + "=" * 50)
        print("DATABASE POPULATION COMPLETE!")
        print("=" * 50)
        print(f"Database: {DATABASE_NAME}")
        print(f"Customers: {len(SAMPLE_CUSTOMERS)}")
        print(f"Restaurants: {len(SAMPLE_RESTAURANTS)}")
        print(f"Menu Items: {len(menu_items)}")
        print(f"Delivery Agents: {len(SAMPLE_DELIVERY_AGENTS)}")
        print(f"Orders: {len(SAMPLE_ORDERS)}")
        print(f"Ratings: {len(SAMPLE_RATINGS)}")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error populating database: {str(e)}")
        raise
    finally:
        client.close()
        print("\nMongoDB connection closed")


if __name__ == "__main__":
    asyncio.run(populate_database())

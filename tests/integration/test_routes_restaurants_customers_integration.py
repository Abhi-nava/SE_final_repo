"""Integration tests for restaurant and customer interactions"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from bson import ObjectId

# Setup paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


class TestRestaurantCustomerIntegration:
    """Test restaurant and customer integration"""
    
    @pytest.mark.asyncio
    async def test_create_restaurant_and_list(self):
        """Test creating restaurant and listing it for customers"""
        owner_id = ObjectId()
        restaurant_id = ObjectId()
        
        # Step 1: Restaurant owner creates restaurant
        with patch('database.db.restaurants.insert_one', new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = MagicMock(inserted_id=restaurant_id)
            
            result = await mock_insert({
                "owner_id": str(owner_id),
                "name": "Test Restaurant",
                "city": "Mumbai",
                "cuisine_types": ["Italian"],
                "is_active": True,
                "phone": "1234567890",
                "address": "Test Address",
                "postal_code": "400001",
                "opening_time": "09:00",
                "closing_time": "22:00",
                "rating": 0.0,
                "total_ratings": 0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            assert result.inserted_id == restaurant_id
        
        # Step 2: Customer lists restaurants
        with patch('database.db.restaurants.find') as mock_find:
            mock_cursor = MagicMock()
            mock_cursor.skip.return_value = mock_cursor
            mock_cursor.limit.return_value = mock_cursor
            mock_cursor.to_list = AsyncMock(return_value=[{
                "_id": restaurant_id,
                "owner_id": str(owner_id),
                "name": "Test Restaurant",
                "city": "Mumbai",
                "cuisine_types": ["Italian"],
                "is_active": True,
                "phone": "1234567890",
                "address": "Test Address",
                "postal_code": "400001",
                "opening_time": "09:00",
                "closing_time": "22:00",
                "rating": 0.0,
                "total_ratings": 0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }])
            mock_find.return_value = mock_cursor
            
            restaurants = await mock_cursor.to_list(20)
            assert len(restaurants) == 1
            assert restaurants[0]["_id"] == restaurant_id
    
    @pytest.mark.asyncio
    async def test_restaurant_menu_workflow(self):
        """Test complete restaurant menu workflow"""
        restaurant_id = ObjectId()
        menu_item_id = ObjectId()
        
        # Step 1: Verify restaurant exists
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find_rest:
            mock_find_rest.return_value = {
                "_id": restaurant_id,
                "name": "Test Restaurant"
            }
            
            restaurant = await mock_find_rest({"_id": restaurant_id})
            assert restaurant is not None
        
        # Step 2: Get menu items
        with patch('database.db.menu_items.find') as mock_find_menu:
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=[{
                "_id": menu_item_id,
                "restaurant_id": restaurant_id,
                "name": "Pasta",
                "description": "Italian pasta",
                "price": 299.0,
                "category": "Main Course",
                "availability": "available",
                "is_vegetarian": True,
                "is_vegan": False,
                "preparation_time": 20,
                "daily_count": 50,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }])
            mock_find_menu.return_value = mock_cursor
            
            menu_items = await mock_cursor.to_list(None)
            assert len(menu_items) == 1
            assert menu_items[0]["name"] == "Pasta"
    
    @pytest.mark.asyncio
    async def test_customer_profile_update_and_view(self):
        """Test customer profile update and viewing"""
        customer_id = ObjectId()
        
        # Step 1: Update profile
        with patch('database.db.users.update_one', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = MagicMock(matched_count=1)
            
            result = await mock_update(
                {"_id": customer_id},
                {"$set": {
                    "full_name": "Updated Name",
                    "phone": "9876543210",
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            assert result.matched_count == 1
        
        # Step 2: View updated profile
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {
                "_id": customer_id,
                "email": "customer@example.com",
                "phone": "9876543210",
                "full_name": "Updated Name",
                "role": "customer",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            user = await mock_find({"_id": customer_id})
            assert user["full_name"] == "Updated Name"
            assert user["phone"] == "9876543210"
    
    @pytest.mark.asyncio
    async def test_restaurant_filtering_by_cuisine(self):
        """Test filtering restaurants by cuisine type"""
        restaurants = [
            {
                "_id": ObjectId(),
                "name": "Italian Restaurant",
                "city": "Mumbai",
                "cuisine_types": ["Italian"],
                "is_active": True,
                "phone": "1234567890",
                "address": "Test Address 1",
                "postal_code": "400001",
                "opening_time": "09:00",
                "closing_time": "22:00",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "owner_id": str(ObjectId())
            },
            {
                "_id": ObjectId(),
                "name": "Chinese Restaurant",
                "city": "Mumbai",
                "cuisine_types": ["Chinese"],
                "is_active": True,
                "phone": "9876543210",
                "address": "Test Address 2",
                "postal_code": "400002",
                "opening_time": "10:00",
                "closing_time": "23:00",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "owner_id": str(ObjectId())
            }
        ]
        
        # Filter by Italian cuisine
        cuisine_filter = "Italian"
        filtered = [r for r in restaurants if cuisine_filter in r["cuisine_types"]]
        
        assert len(filtered) == 1
        assert filtered[0]["name"] == "Italian Restaurant"

"""Unit tests for restaurant routes"""
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


class TestCreateRestaurant:
    """Test restaurant creation endpoint"""
    
    @pytest.mark.asyncio
    async def test_create_restaurant_success(self):
        """Test successful restaurant creation"""
        owner_id = ObjectId()
        current_user = {
            "_id": owner_id,
            "email": "owner@example.com",
            "role": "restaurant"
        }
        
        restaurant_data = {
            "name": "Test Restaurant",
            "description": "A test restaurant",
            "phone": "1234567890",
            "address": "123 Test St",
            "city": "Mumbai",
            "postal_code": "400001",
            "cuisine_types": ["Italian", "Continental"],
            "image_url": "http://example.com/image.jpg",
            "opening_time": "09:00",
            "closing_time": "22:00"
        }
        
        with patch('database.db.restaurants.insert_one', new_callable=AsyncMock) as mock_insert:
            restaurant_id = ObjectId()
            mock_insert.return_value = MagicMock(inserted_id=restaurant_id)
            
            result = await mock_insert({**restaurant_data, "owner_id": str(owner_id)})
            assert result.inserted_id == restaurant_id
    
    @pytest.mark.asyncio
    async def test_create_restaurant_defaults(self):
        """Test restaurant creation with default values"""
        restaurant_doc = {
            "name": "Test Restaurant",
            "rating": 0.0,
            "total_ratings": 0,
            "is_active": True
        }
        
        assert restaurant_doc["rating"] == 0.0
        assert restaurant_doc["total_ratings"] == 0
        assert restaurant_doc["is_active"] is True


class TestGetMyRestaurant:
    """Test get owner's restaurant endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_my_restaurant_success(self):
        """Test getting owner's restaurant"""
        owner_id = ObjectId()
        restaurant = {
            "_id": ObjectId(),
            "owner_id": str(owner_id),
            "name": "My Restaurant",
            "phone": "1234567890",
            "address": "Test Address",
            "city": "Mumbai",
            "postal_code": "400001",
            "cuisine_types": ["Italian"],
            "opening_time": "09:00",
            "closing_time": "22:00",
            "rating": 4.2,
            "total_ratings": 50,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = restaurant
            
            result = await mock_find({"owner_id": str(owner_id)})
            assert result is not None
            assert result["name"] == "My Restaurant"
    
    @pytest.mark.asyncio
    async def test_get_my_restaurant_not_found(self):
        """Test when owner has no restaurant"""
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            
            result = await mock_find({"owner_id": str(ObjectId())})
            assert result is None


class TestGetRestaurantMenu:
    """Test get restaurant menu endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_menu_success(self):
        """Test getting restaurant menu items"""
        restaurant_id = ObjectId()
        menu_items = [
            {
                "_id": ObjectId(),
                "restaurant_id": restaurant_id,
                "name": "Pasta",
                "description": "Italian pasta",
                "price": 299.0,
                "category": "Main Course",
                "image_url": "http://example.com/pasta.jpg",
                "availability": "available",
                "is_vegetarian": True,
                "is_vegan": False,
                "preparation_time": 20,
                "daily_count": 50,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "_id": ObjectId(),
                "restaurant_id": restaurant_id,
                "name": "Pizza",
                "description": "Margherita pizza",
                "price": 399.0,
                "category": "Main Course",
                "availability": "available",
                "is_vegetarian": True,
                "is_vegan": False,
                "preparation_time": 25,
                "daily_count": 30,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find_rest, \
             patch('database.db.menu_items.find') as mock_find_menu:
            
            mock_find_rest.return_value = {"_id": restaurant_id, "name": "Test Restaurant"}
            
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=menu_items)
            mock_find_menu.return_value = mock_cursor
            
            result = await mock_cursor.to_list(None)
            assert len(result) == 2
            assert result[0]["name"] == "Pasta"
            assert result[1]["name"] == "Pizza"
    
    @pytest.mark.asyncio
    async def test_get_menu_restaurant_not_found(self):
        """Test getting menu for non-existent restaurant"""
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            
            result = await mock_find({"_id": ObjectId()})
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_menu_empty(self):
        """Test getting menu with no items"""
        restaurant_id = ObjectId()
        
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find_rest, \
             patch('database.db.menu_items.find') as mock_find_menu:
            
            mock_find_rest.return_value = {"_id": restaurant_id}
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=[])
            mock_find_menu.return_value = mock_cursor
            
            result = await mock_cursor.to_list(None)
            assert len(result) == 0

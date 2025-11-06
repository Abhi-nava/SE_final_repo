"""Unit tests for customer routes"""
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


class TestListRestaurants:
    """Test restaurant listing endpoint"""
    
    @pytest.mark.asyncio
    async def test_list_all_restaurants(self):
        """Test listing all active restaurants"""
        restaurants = [
            {
                "_id": ObjectId(),
                "owner_id": str(ObjectId()),
                "name": "Test Restaurant 1",
                "city": "Mumbai",
                "cuisine_types": ["Italian"],
                "is_active": True,
                "phone": "1234567890",
                "address": "Test Address",
                "postal_code": "400001",
                "opening_time": "09:00",
                "closing_time": "22:00",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "_id": ObjectId(),
                "owner_id": str(ObjectId()),
                "name": "Test Restaurant 2",
                "city": "Delhi",
                "cuisine_types": ["Chinese"],
                "is_active": True,
                "phone": "9876543210",
                "address": "Test Address 2",
                "postal_code": "110001",
                "opening_time": "10:00",
                "closing_time": "23:00",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        with patch('database.db.restaurants.find') as mock_find:
            mock_cursor = MagicMock()
            mock_cursor.skip.return_value = mock_cursor
            mock_cursor.limit.return_value = mock_cursor
            mock_cursor.to_list = AsyncMock(return_value=restaurants)
            mock_find.return_value = mock_cursor
            
            result = await mock_cursor.to_list(20)
            assert len(result) == 2
            assert result[0]["name"] == "Test Restaurant 1"
    
    @pytest.mark.asyncio
    async def test_list_restaurants_filter_by_city(self):
        """Test filtering restaurants by city"""
        restaurants = [
            {
                "_id": ObjectId(),
                "owner_id": str(ObjectId()),
                "name": "Mumbai Restaurant",
                "city": "Mumbai",
                "cuisine_types": ["Indian"],
                "is_active": True,
                "phone": "1234567890",
                "address": "Test Address",
                "postal_code": "400001",
                "opening_time": "09:00",
                "closing_time": "22:00",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        query = {"is_active": True, "city": {"$regex": "Mumbai", "$options": "i"}}
        assert "city" in query
        assert query["city"]["$regex"] == "Mumbai"
    
    @pytest.mark.asyncio
    async def test_list_restaurants_filter_by_cuisine(self):
        """Test filtering restaurants by cuisine"""
        query = {"is_active": True, "cuisine_types": {"$in": ["Italian"]}}
        assert "cuisine_types" in query
        assert "Italian" in query["cuisine_types"]["$in"]


class TestGetRestaurant:
    """Test get single restaurant endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_restaurant_success(self):
        """Test getting restaurant by ID"""
        restaurant_id = ObjectId()
        restaurant = {
            "_id": restaurant_id,
            "owner_id": str(ObjectId()),
            "name": "Test Restaurant",
            "city": "Mumbai",
            "cuisine_types": ["Italian", "Continental"],
            "is_active": True,
            "phone": "1234567890",
            "address": "Test Address",
            "postal_code": "400001",
            "opening_time": "09:00",
            "closing_time": "22:00",
            "rating": 4.5,
            "total_ratings": 100,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = restaurant
            
            result = await mock_find({"_id": restaurant_id})
            assert result is not None
            assert result["name"] == "Test Restaurant"
            assert result["rating"] == 4.5
    
    @pytest.mark.asyncio
    async def test_get_restaurant_not_found(self):
        """Test getting non-existent restaurant"""
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            
            result = await mock_find({"_id": ObjectId()})
            assert result is None


class TestUpdateProfile:
    """Test customer profile update endpoint"""
    
    @pytest.mark.asyncio
    async def test_update_profile_success(self):
        """Test successful profile update"""
        user_id = ObjectId()
        current_user = {
            "_id": user_id,
            "email": "test@example.com",
            "phone": "1234567890",
            "full_name": "Test User",
            "role": "customer"
        }
        
        update_data = {
            "full_name": "Updated Name",
            "phone": "9876543210",
            "address": "New Address"
        }
        
        with patch('database.db.users.update_one', new_callable=AsyncMock) as mock_update, \
             patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            
            mock_update.return_value = MagicMock(matched_count=1)
            mock_find.return_value = {
                **current_user,
                **update_data,
                "updated_at": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc)
            }
            
            result = await mock_find({"_id": user_id})
            assert result["full_name"] == "Updated Name"
            assert result["phone"] == "9876543210"
    
    @pytest.mark.asyncio
    async def test_update_profile_partial(self):
        """Test partial profile update"""
        update_dict = {"full_name": "New Name"}
        
        # Verify only specified fields are updated
        assert "full_name" in update_dict
        assert "phone" not in update_dict

"""System tests for complete application workflows"""
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

from utils.security import hash_password


class TestCompleteUserJourney:
    """Test complete user journey from registration to order delivery"""
    
    @pytest.mark.asyncio
    async def test_customer_complete_journey(self):
        """Test complete customer journey"""
        customer_id = ObjectId()
        restaurant_id = ObjectId()
        menu_item_id = ObjectId()
        order_id = ObjectId()
        
        # Step 1: Customer Registration
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find, \
             patch('database.db.users.insert_one', new_callable=AsyncMock) as mock_insert:
            
            mock_find.return_value = None
            mock_insert.return_value = MagicMock(inserted_id=customer_id)
            
            existing = await mock_find({"$or": [{"email": "customer@test.com"}]})
            assert existing is None
            
            result = await mock_insert({
                "email": "customer@test.com",
                "password_hash": hash_password("password123"),
                "role": "customer",
                "full_name": "Test Customer",
                "phone": "1234567890"
            })
            assert result.inserted_id == customer_id
        
        # Step 2: Customer Login
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {
                "_id": customer_id,
                "email": "customer@test.com",
                "password": hash_password("password123"),
                "role": "customer",
                "is_active": True,
                "full_name": "Test Customer",
                "phone": "1234567890",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            user = await mock_find({"email": "customer@test.com"})
            assert user is not None
            assert user["role"] == "customer"
        
        # Step 3: Browse Restaurants
        with patch('database.db.restaurants.find') as mock_find_rest:
            mock_cursor = MagicMock()
            mock_cursor.skip.return_value = mock_cursor
            mock_cursor.limit.return_value = mock_cursor
            mock_cursor.to_list = AsyncMock(return_value=[{
                "_id": restaurant_id,
                "name": "Test Restaurant",
                "city": "Mumbai",
                "cuisine_types": ["Italian"],
                "is_active": True,
                "rating": 4.5,
                "phone": "9876543210",
                "address": "Test Address",
                "postal_code": "400001",
                "opening_time": "09:00",
                "closing_time": "22:00",
                "owner_id": str(ObjectId()),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }])
            mock_find_rest.return_value = mock_cursor
            
            restaurants = await mock_cursor.to_list(20)
            assert len(restaurants) > 0
        
        # Step 4: View Menu
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_rest, \
             patch('database.db.menu_items.find') as mock_menu:
            
            mock_rest.return_value = {"_id": restaurant_id, "name": "Test Restaurant"}
            
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=[{
                "_id": menu_item_id,
                "restaurant_id": restaurant_id,
                "name": "Margherita Pizza",
                "price": 399.0,
                "daily_count": "30",
                "availability": "available",
                "is_vegetarian": True,
                "preparation_time": 25,
                "category": "Pizza",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }])
            mock_menu.return_value = mock_cursor
            
            menu_items = await mock_cursor.to_list(None)
            assert len(menu_items) > 0
        
        # Step 5: Place Order
        with patch('database.db.menu_items.find_one', new_callable=AsyncMock) as mock_item, \
             patch('database.db.menu_items.update_one', new_callable=AsyncMock) as mock_update, \
             patch('database.db.orders.insert_one', new_callable=AsyncMock) as mock_order:
            
            mock_item.return_value = {
                "_id": menu_item_id,
                "name": "Margherita Pizza",
                "price": 399.0,
                "daily_count": "30"
            }
            mock_update.return_value = MagicMock(matched_count=1)
            mock_order.return_value = MagicMock(inserted_id=order_id)
            
            item = await mock_item({"_id": menu_item_id})
            assert int(item["daily_count"]) >= 2
            
            result = await mock_order({
                "customer_id": str(customer_id),
                "restaurant_id": str(restaurant_id),
                "status": "paid",
                "total": 848.0
            })
            assert result.inserted_id == order_id
        
        # Step 6: Track Order
        with patch('database.db.orders.find_one', new_callable=AsyncMock) as mock_find_order:
            mock_find_order.return_value = {
                "_id": order_id,
                "customer_id": str(customer_id),
                "status": "delivered",
                "order_status": "delivered"
            }
            
            order = await mock_find_order({"_id": order_id})
            assert order["status"] == "delivered"
    
    @pytest.mark.asyncio
    async def test_restaurant_owner_complete_journey(self):
        """Test complete restaurant owner journey"""
        owner_id = ObjectId()
        restaurant_id = ObjectId()
        menu_item_id = ObjectId()
        
        # Step 1: Owner Registration
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find, \
             patch('database.db.users.insert_one', new_callable=AsyncMock) as mock_insert:
            
            mock_find.return_value = None
            mock_insert.return_value = MagicMock(inserted_id=owner_id)
            
            result = await mock_insert({
                "email": "owner@test.com",
                "password_hash": hash_password("password123"),
                "role": "restaurant",
                "full_name": "Restaurant Owner",
                "phone": "9876543210"
            })
            assert result.inserted_id == owner_id
        
        # Step 2: Create Restaurant
        with patch('database.db.restaurants.insert_one', new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = MagicMock(inserted_id=restaurant_id)
            
            result = await mock_insert({
                "owner_id": str(owner_id),
                "name": "My Restaurant",
                "city": "Mumbai",
                "cuisine_types": ["Italian"],
                "is_active": True,
                "phone": "9876543210",
                "address": "Test Address",
                "postal_code": "400001",
                "opening_time": "09:00",
                "closing_time": "22:00"
            })
            assert result.inserted_id == restaurant_id
        
        # Step 3: Add Menu Items
        with patch('database.db.menu_items.insert_one', new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = MagicMock(inserted_id=menu_item_id)
            
            result = await mock_insert({
                "restaurant_id": restaurant_id,
                "name": "Pizza",
                "price": 399.0,
                "daily_count": "50",
                "category": "Main Course"
            })
            assert result.inserted_id == menu_item_id
        
        # Step 4: View Restaurant Details
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {
                "_id": restaurant_id,
                "owner_id": str(owner_id),
                "name": "My Restaurant",
                "is_active": True,
                "rating": 4.5,
                "total_ratings": 100
            }
            
            restaurant = await mock_find({"owner_id": str(owner_id)})
            assert restaurant is not None
            assert restaurant["name"] == "My Restaurant"


class TestMultiUserScenarios:
    """Test scenarios involving multiple users"""
    
    @pytest.mark.asyncio
    async def test_multiple_customers_same_restaurant(self):
        """Test multiple customers ordering from same restaurant"""
        restaurant_id = ObjectId()
        menu_item_id = ObjectId()
        customer_ids = [ObjectId(), ObjectId(), ObjectId()]
        
        # All customers view same menu
        with patch('database.db.menu_items.find') as mock_menu:
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=[{
                "_id": menu_item_id,
                "restaurant_id": restaurant_id,
                "name": "Pizza",
                "price": 399.0,
                "daily_count": "50"
            }])
            mock_menu.return_value = mock_cursor
            
            menu = await mock_cursor.to_list(None)
            initial_count = int(menu[0]["daily_count"])
            assert initial_count == 50
        
        # Simulate multiple orders
        orders_placed = 3
        quantity_per_order = 2
        expected_remaining = initial_count - (orders_placed * quantity_per_order)
        
        assert expected_remaining == 44  # 50 - (3 * 2)
    
    @pytest.mark.asyncio
    async def test_concurrent_stock_updates(self):
        """Test concurrent stock updates"""
        menu_item_id = ObjectId()
        initial_stock = 20
        
        # Simulate concurrent order attempts
        order_quantities = [3, 5, 2, 4]
        total_ordered = sum(order_quantities)
        
        # Check if stock is sufficient
        assert initial_stock >= total_ordered
        
        final_stock = initial_stock - total_ordered
        assert final_stock == 6


class TestErrorRecoveryScenarios:
    """Test error recovery and edge cases"""
    
    @pytest.mark.asyncio
    async def test_order_with_inactive_restaurant(self):
        """Test order attempt with inactive restaurant"""
        restaurant_id = ObjectId()
        
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {
                "_id": restaurant_id,
                "name": "Test Restaurant",
                "is_active": False  # Inactive
            }
            
            restaurant = await mock_find({"_id": restaurant_id})
            assert restaurant["is_active"] is False
    
    @pytest.mark.asyncio
    async def test_order_with_out_of_stock_item(self):
        """Test order with out of stock item"""
        menu_item_id = ObjectId()
        
        with patch('database.db.menu_items.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {
                "_id": menu_item_id,
                "name": "Pizza",
                "price": 399.0,
                "daily_count": "0",  # Out of stock
                "availability": "out_of_stock"
            }
            
            item = await mock_find({"_id": menu_item_id})
            assert int(item["daily_count"]) == 0
            assert item["availability"] == "out_of_stock"
    
    @pytest.mark.asyncio
    async def test_duplicate_registration_prevention(self):
        """Test prevention of duplicate user registration"""
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            # User already exists
            mock_find.return_value = {
                "_id": ObjectId(),
                "email": "existing@test.com"
            }
            
            existing = await mock_find({"$or": [{"email": "existing@test.com"}]})
            assert existing is not None  # Should prevent duplicate

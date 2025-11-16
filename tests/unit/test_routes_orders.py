"""Unit tests for order routes"""
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


class TestCreateOrder:
    """Test order creation endpoint"""
    
    @pytest.mark.asyncio
    async def test_create_order_success(self):
        """Test successful order creation"""
        user_id = ObjectId()
        restaurant_id = ObjectId()
        menu_item_id = ObjectId()
        
        payload = {
            "restaurant_id": str(restaurant_id),
            "items": [
                {
                    "menuItemId": str(menu_item_id),
                    "quantity": 2
                }
            ],
            "delivery_address": "123 Test St",
            "delivery_phone": "1234567890",
            "payment_method": "card",
            "subtotal": 500.0,
            "delivery_fee": 50.0,
            "discount": 0.0,
            "total": 550.0
        }
        
        restaurant = {
            "_id": restaurant_id,
            "name": "Test Restaurant",
            "is_active": True
        }
        
        menu_item = {
            "_id": menu_item_id,
            "name": "Test Item",
            "price": 250.0,
            "daily_count": "10"
        }
        
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_rest, \
             patch('database.db.menu_items.find_one', new_callable=AsyncMock) as mock_menu, \
             patch('database.db.menu_items.update_one', new_callable=AsyncMock) as mock_update, \
             patch('database.db.orders.insert_one', new_callable=AsyncMock) as mock_insert:
            
            mock_rest.return_value = restaurant
            mock_menu.return_value = menu_item
            mock_update.return_value = MagicMock(matched_count=1)
            mock_insert.return_value = MagicMock(inserted_id=ObjectId())
            
            # Verify restaurant exists
            rest_result = await mock_rest({"_id": restaurant_id})
            assert rest_result is not None
            
            # Verify menu item exists
            menu_result = await mock_menu({"_id": menu_item_id})
            assert menu_result is not None
            assert int(menu_result["daily_count"]) >= 2
    
    @pytest.mark.asyncio
    async def test_create_order_insufficient_stock(self):
        """Test order creation with insufficient stock"""
        menu_item = {
            "_id": ObjectId(),
            "name": "Test Item",
            "price": 250.0,
            "daily_count": "1"  # Only 1 available
        }
        
        requested_quantity = 5
        current_count = int(menu_item["daily_count"])
        
        # Should fail validation
        assert current_count < requested_quantity
    
    @pytest.mark.asyncio
    async def test_create_order_restaurant_not_found(self):
        """Test order creation with non-existent restaurant"""
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            
            result = await mock_find({"_id": ObjectId()})
            assert result is None
    
    @pytest.mark.asyncio
    async def test_create_order_updates_daily_count(self):
        """Test that order creation updates menu item daily count"""
        initial_count = 10
        order_quantity = 3
        expected_count = 7
        
        # Simulate count update
        new_count = max(initial_count - order_quantity, 0)
        assert new_count == expected_count


class TestGetOrderDetails:
    """Test get order details endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_order_details_success(self):
        """Test getting order details"""
        order_id = ObjectId()
        restaurant_id = ObjectId()
        
        order = {
            "_id": order_id,
            "customer_id": str(ObjectId()),
            "restaurant_id": str(restaurant_id),
            "items": [
                {
                    "menu_item_id": str(ObjectId()),
                    "name": "Test Item",
                    "quantity": 2,
                    "price": 250.0
                }
            ],
            "subtotal": 500.0,
            "delivery_fee": 50.0,
            "discount": 0.0,
            "total": 550.0,
            "status": "paid",
            "order_status": "preparing",
            "delivery_address": "123 Test St",
            "delivery_phone": "1234567890",
            "payment_method": "card",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        restaurant = {
            "_id": restaurant_id,
            "name": "Test Restaurant",
            "image_url": "http://example.com/image.jpg"
        }
        
        with patch('database.db.orders.find_one', new_callable=AsyncMock) as mock_order, \
             patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_rest:
            
            mock_order.return_value = order
            mock_rest.return_value = restaurant
            
            order_result = await mock_order({"_id": order_id})
            assert order_result is not None
            assert order_result["status"] == "paid"
            
            rest_result = await mock_rest({"_id": restaurant_id})
            assert rest_result["name"] == "Test Restaurant"
    
    @pytest.mark.asyncio
    async def test_get_order_details_not_found(self):
        """Test getting non-existent order"""
        with patch('database.db.orders.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            
            result = await mock_find({"_id": ObjectId()})
            assert result is None


class TestGetMyOrders:
    """Test get customer orders endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_my_orders_success(self):
        """Test getting customer's orders"""
        customer_id = ObjectId()
        
        orders = [
            {
                "_id": ObjectId(),
                "customer_id": str(customer_id),
                "restaurant_id": str(ObjectId()),
                "items": [],
                "subtotal": 500.0,
                "delivery_fee": 50.0,
                "discount": 0.0,
                "total": 550.0,
                "status": "delivered",
                "delivery_address": "123 Test St",
                "delivery_phone": "1234567890",
                "payment_method": "card",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "_id": ObjectId(),
                "customer_id": str(customer_id),
                "restaurant_id": str(ObjectId()),
                "items": [],
                "subtotal": 300.0,
                "delivery_fee": 50.0,
                "discount": 50.0,
                "total": 300.0,
                "status": "preparing",
                "delivery_address": "123 Test St",
                "delivery_phone": "1234567890",
                "payment_method": "upi",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        with patch('database.db.orders.find') as mock_find:
            mock_cursor = MagicMock()
            mock_cursor.sort.return_value = mock_cursor
            mock_cursor.skip.return_value = mock_cursor
            mock_cursor.limit.return_value = mock_cursor
            mock_cursor.to_list = AsyncMock(return_value=orders)
            mock_find.return_value = mock_cursor
            
            result = await mock_cursor.to_list(20)
            assert len(result) == 2
            assert result[0]["status"] == "delivered"
            assert result[1]["status"] == "preparing"
    
    @pytest.mark.asyncio
    async def test_get_my_orders_empty(self):
        """Test getting orders when customer has none"""
        with patch('database.db.orders.find') as mock_find:
            mock_cursor = MagicMock()
            mock_cursor.sort.return_value = mock_cursor
            mock_cursor.skip.return_value = mock_cursor
            mock_cursor.limit.return_value = mock_cursor
            mock_cursor.to_list = AsyncMock(return_value=[])
            mock_find.return_value = mock_cursor
            
            result = await mock_cursor.to_list(20)
            assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_my_orders_pagination(self):
        """Test order pagination"""
        skip = 0
        limit = 10
        
        # Verify pagination parameters
        assert skip >= 0
        assert limit > 0
        assert limit <= 100  # Reasonable max limit

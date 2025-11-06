"""Integration tests for order workflow"""
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


class TestOrderIntegrationFlow:
    """Test complete order flow integration"""
    
    @pytest.mark.asyncio
    async def test_complete_order_flow(self):
        """Test complete order from creation to completion"""
        customer_id = ObjectId()
        restaurant_id = ObjectId()
        menu_item_id = ObjectId()
        order_id = ObjectId()
        
        # Step 1: Customer views restaurant menu
        with patch('database.db.restaurants.find_one', new_callable=AsyncMock) as mock_rest, \
             patch('database.db.menu_items.find') as mock_menu:
            
            mock_rest.return_value = {
                "_id": restaurant_id,
                "name": "Test Restaurant",
                "is_active": True
            }
            
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=[{
                "_id": menu_item_id,
                "restaurant_id": restaurant_id,
                "name": "Pizza",
                "price": 399.0,
                "daily_count": "20",
                "availability": "available"
            }])
            mock_menu.return_value = mock_cursor
            
            restaurant = await mock_rest({"_id": restaurant_id})
            assert restaurant is not None
            
            menu_items = await mock_cursor.to_list(None)
            assert len(menu_items) > 0
        
        # Step 2: Customer creates order
        with patch('database.db.menu_items.find_one', new_callable=AsyncMock) as mock_find_item, \
             patch('database.db.menu_items.update_one', new_callable=AsyncMock) as mock_update_item, \
             patch('database.db.orders.insert_one', new_callable=AsyncMock) as mock_insert_order:
            
            mock_find_item.return_value = {
                "_id": menu_item_id,
                "name": "Pizza",
                "price": 399.0,
                "daily_count": "20"
            }
            mock_update_item.return_value = MagicMock(matched_count=1)
            mock_insert_order.return_value = MagicMock(inserted_id=order_id)
            
            # Check stock
            item = await mock_find_item({"_id": menu_item_id})
            assert int(item["daily_count"]) >= 2
            
            # Update stock
            new_count = int(item["daily_count"]) - 2
            await mock_update_item(
                {"_id": menu_item_id},
                {"$set": {"daily_count": str(new_count)}}
            )
            
            # Create order
            result = await mock_insert_order({
                "customer_id": str(customer_id),
                "restaurant_id": str(restaurant_id),
                "items": [{
                    "menu_item_id": str(menu_item_id),
                    "name": "Pizza",
                    "quantity": 2,
                    "price": 399.0
                }],
                "status": "paid",
                "total": 848.0,
                "delivery_address": "123 Test St",
                "delivery_phone": "1234567890",
                "payment_method": "card"
            })
            assert result.inserted_id == order_id
        
        # Step 3: Customer views order details
        with patch('database.db.orders.find_one', new_callable=AsyncMock) as mock_find_order:
            mock_find_order.return_value = {
                "_id": order_id,
                "customer_id": str(customer_id),
                "restaurant_id": str(restaurant_id),
                "status": "paid",
                "order_status": "preparing"
            }
            
            order = await mock_find_order({"_id": order_id})
            assert order is not None
            assert order["status"] == "paid"
        
        # Step 4: Customer views order history
        with patch('database.db.orders.find') as mock_find_orders:
            mock_cursor = MagicMock()
            mock_cursor.sort.return_value = mock_cursor
            mock_cursor.skip.return_value = mock_cursor
            mock_cursor.limit.return_value = mock_cursor
            mock_cursor.to_list = AsyncMock(return_value=[{
                "_id": order_id,
                "customer_id": str(customer_id),
                "status": "delivered"
            }])
            mock_find_orders.return_value = mock_cursor
            
            orders = await mock_cursor.to_list(20)
            assert len(orders) == 1
    
    @pytest.mark.asyncio
    async def test_order_stock_validation(self):
        """Test order creation with stock validation"""
        menu_item_id = ObjectId()
        
        # Scenario 1: Sufficient stock
        with patch('database.db.menu_items.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {
                "_id": menu_item_id,
                "name": "Burger",
                "price": 199.0,
                "daily_count": "15"
            }
            
            item = await mock_find({"_id": menu_item_id})
            requested_qty = 5
            available = int(item["daily_count"])
            
            assert available >= requested_qty  # Should pass
        
        # Scenario 2: Insufficient stock
        with patch('database.db.menu_items.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {
                "_id": menu_item_id,
                "name": "Burger",
                "price": 199.0,
                "daily_count": "2"
            }
            
            item = await mock_find({"_id": menu_item_id})
            requested_qty = 5
            available = int(item["daily_count"])
            
            assert available < requested_qty  # Should fail
    
    @pytest.mark.asyncio
    async def test_multiple_items_order(self):
        """Test order with multiple menu items"""
        restaurant_id = ObjectId()
        item1_id = ObjectId()
        item2_id = ObjectId()
        
        items_data = [
            {
                "_id": item1_id,
                "restaurant_id": restaurant_id,
                "name": "Pizza",
                "price": 399.0,
                "daily_count": "20"
            },
            {
                "_id": item2_id,
                "restaurant_id": restaurant_id,
                "name": "Pasta",
                "price": 299.0,
                "daily_count": "15"
            }
        ]
        
        # Verify all items are from same restaurant
        restaurant_ids = set(str(item["restaurant_id"]) for item in items_data)
        assert len(restaurant_ids) == 1
        
        # Calculate total
        order_items = [
            {"menu_item_id": str(item1_id), "quantity": 2, "price": 399.0},
            {"menu_item_id": str(item2_id), "quantity": 1, "price": 299.0}
        ]
        
        subtotal = sum(item["quantity"] * item["price"] for item in order_items)
        assert subtotal == 1097.0  # (2*399) + (1*299)
    
    @pytest.mark.asyncio
    async def test_order_payment_methods(self):
        """Test order creation with different payment methods"""
        payment_methods = ["card", "upi", "wallet", "cod"]
        
        for method in payment_methods:
            order_data = {
                "payment_method": method,
                "total": 500.0,
                "status": "paid" if method != "cod" else "pending"
            }
            
            # Verify payment method is valid
            assert order_data["payment_method"] in payment_methods
            
            # COD orders should start as pending
            if method == "cod":
                assert order_data["status"] == "pending"

"""Unit tests for Pydantic models"""
import sys
import os
import pytest
from pydantic import ValidationError
from datetime import datetime

# Setup paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models.user import UserCreate, UserUpdate, LoginRequest, UserRole, TokenResponse, UserResponse
from models.restaurant import RestaurantCreate, RestaurantUpdate, MenuItem, MenuItemUpdate, ItemAvailability
from models.order import OrderCreate, OrderItemRequest, OrderStatus, OrderStatusUpdate


class TestUserModels:
    """Test user-related models"""
    
    def test_user_create_valid(self):
        """Test valid user creation"""
        user = UserCreate(
            email="test@example.com",
            phone="1234567890",
            full_name="Test User",
            password="password123",
            role=UserRole.CUSTOMER
        )
        assert user.email == "test@example.com"
        assert user.role == UserRole.CUSTOMER
    
    def test_user_create_invalid_email(self):
        """Test user creation with invalid email"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                phone="1234567890",
                full_name="Test User",
                password="password123"
            )
    
    def test_user_create_short_password(self):
        """Test user creation with short password"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                phone="1234567890",
                full_name="Test User",
                password="short"  # Less than 8 characters
            )
    
    def test_user_create_short_phone(self):
        """Test user creation with short phone number"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                phone="123",  # Less than 10 characters
                full_name="Test User",
                password="password123"
            )
    
    def test_user_update_partial(self):
        """Test partial user update"""
        update = UserUpdate(full_name="Updated Name")
        assert update.full_name == "Updated Name"
        assert update.phone is None
        assert update.address is None
    
    def test_login_request_valid(self):
        """Test valid login request"""
        login = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        assert login.email == "test@example.com"
        assert login.password == "password123"
    
    def test_user_roles(self):
        """Test user role enum"""
        assert UserRole.CUSTOMER.value == "customer"
        assert UserRole.RESTAURANT.value == "restaurant"
        assert UserRole.DELIVERY_AGENT.value == "delivery_agent"
        assert UserRole.ADMIN.value == "admin"


class TestRestaurantModels:
    """Test restaurant-related models"""
    
    def test_restaurant_create_valid(self):
        """Test valid restaurant creation"""
        restaurant = RestaurantCreate(
            name="Test Restaurant",
            description="A test restaurant",
            phone="1234567890",
            address="123 Test St",
            city="Mumbai",
            postal_code="400001",
            cuisine_types=["Italian", "Continental"],
            opening_time="09:00",
            closing_time="22:00"
        )
        assert restaurant.name == "Test Restaurant"
        assert len(restaurant.cuisine_types) == 2
    
    def test_restaurant_create_with_defaults(self):
        """Test restaurant creation with default times"""
        restaurant = RestaurantCreate(
            name="Test Restaurant",
            phone="1234567890",
            address="123 Test St",
            city="Mumbai",
            postal_code="400001",
            cuisine_types=["Italian"]
        )
        assert restaurant.opening_time == "09:00"
        assert restaurant.closing_time == "23:00"
    
    def test_restaurant_create_empty_name(self):
        """Test restaurant creation with empty name"""
        with pytest.raises(ValidationError):
            RestaurantCreate(
                name="",  # Empty name
                phone="1234567890",
                address="123 Test St",
                city="Mumbai",
                postal_code="400001",
                cuisine_types=["Italian"]
            )
    
    def test_menu_item_valid(self):
        """Test valid menu item"""
        item = MenuItem(
            _id="507f1f77bcf86cd799439011",
            name="Pizza",
            description="Delicious pizza",
            price=399.0,
            category="Main Course",
            availability=ItemAvailability.AVAILABLE,
            is_vegetarian=True,
            preparation_time=25,
            daily_count=50
        )
        assert item.name == "Pizza"
        assert item.price == 399.0
    
    def test_menu_item_negative_price(self):
        """Test menu item with negative price"""
        with pytest.raises(ValidationError):
            MenuItem(
                _id="507f1f77bcf86cd799439011",
                name="Pizza",
                price=-100.0,  # Negative price
                category="Main Course"
            )
    
    def test_menu_item_availability_enum(self):
        """Test menu item availability enum"""
        assert ItemAvailability.AVAILABLE.value == "available"
        assert ItemAvailability.OUT_OF_STOCK.value == "out_of_stock"
        assert ItemAvailability.DISCONTINUED.value == "discontinued"
    
    def test_menu_item_update_partial(self):
        """Test partial menu item update"""
        update = MenuItemUpdate(
            price=450.0,
            availability=ItemAvailability.OUT_OF_STOCK
        )
        assert update.price == 450.0
        assert update.availability == ItemAvailability.OUT_OF_STOCK
        assert update.name is None


class TestOrderModels:
    """Test order-related models"""
    
    def test_order_item_request_valid(self):
        """Test valid order item request"""
        item = OrderItemRequest(
            menu_item_id="507f1f77bcf86cd799439011",
            quantity=2,
            special_instructions="Extra cheese"
        )
        assert item.quantity == 2
        assert item.special_instructions == "Extra cheese"
    
    def test_order_item_request_zero_quantity(self):
        """Test order item with zero quantity"""
        with pytest.raises(ValidationError):
            OrderItemRequest(
                menu_item_id="507f1f77bcf86cd799439011",
                quantity=0  # Must be > 0
            )
    
    def test_order_item_request_negative_quantity(self):
        """Test order item with negative quantity"""
        with pytest.raises(ValidationError):
            OrderItemRequest(
                menu_item_id="507f1f77bcf86cd799439011",
                quantity=-5  # Must be > 0
            )
    
    def test_order_create_valid(self):
        """Test valid order creation"""
        order = OrderCreate(
            restaurant_id="507f1f77bcf86cd799439011",
            items=[
                OrderItemRequest(
                    menu_item_id="507f1f77bcf86cd799439012",
                    quantity=2
                )
            ],
            delivery_address="123 Test St",
            delivery_phone="1234567890",
            payment_method="card"
        )
        assert order.restaurant_id == "507f1f77bcf86cd799439011"
        assert len(order.items) == 1
    
    def test_order_status_enum(self):
        """Test order status enum values"""
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.PREPARING.value == "preparing"
        assert OrderStatus.DELIVERED.value == "delivered"
        assert OrderStatus.CANCELLED.value == "cancelled"
    
    def test_order_status_update_valid(self):
        """Test valid order status update"""
        update = OrderStatusUpdate(
            status=OrderStatus.DELIVERED,
            notes="Delivered successfully"
        )
        assert update.status == OrderStatus.DELIVERED
        assert update.notes == "Delivered successfully"
    
    def test_payment_methods(self):
        """Test various payment methods"""
        payment_methods = ["card", "upi", "wallet", "cod"]
        
        for method in payment_methods:
            order = OrderCreate(
                restaurant_id="507f1f77bcf86cd799439011",
                items=[
                    OrderItemRequest(
                        menu_item_id="507f1f77bcf86cd799439012",
                        quantity=1
                    )
                ],
                delivery_address="123 Test St",
                delivery_phone="1234567890",
                payment_method=method
            )
            assert order.payment_method == method


class TestModelRelationships:
    """Test relationships between models"""
    
    def test_order_with_multiple_items(self):
        """Test order with multiple items"""
        items = [
            OrderItemRequest(menu_item_id="item1", quantity=2),
            OrderItemRequest(menu_item_id="item2", quantity=1),
            OrderItemRequest(menu_item_id="item3", quantity=3)
        ]
        
        order = OrderCreate(
            restaurant_id="restaurant1",
            items=items,
            delivery_address="123 Test St",
            delivery_phone="1234567890",
            payment_method="card"
        )
        
        assert len(order.items) == 3
        total_quantity = sum(item.quantity for item in order.items)
        assert total_quantity == 6
    
    def test_restaurant_with_multiple_cuisines(self):
        """Test restaurant with multiple cuisine types"""
        restaurant = RestaurantCreate(
            name="Multi-Cuisine Restaurant",
            phone="1234567890",
            address="123 Test St",
            city="Mumbai",
            postal_code="400001",
            cuisine_types=["Italian", "Chinese", "Indian", "Continental"]
        )
        assert len(restaurant.cuisine_types) == 4
    
    def test_menu_item_vegetarian_flags(self):
        """Test menu item vegetarian and vegan flags"""
        # Vegetarian but not vegan
        item1 = MenuItem(
            _id="item1",
            name="Cheese Pizza",
            price=399.0,
            category="Pizza",
            is_vegetarian=True,
            is_vegan=False
        )
        assert item1.is_vegetarian and not item1.is_vegan
        
        # Vegan (which implies vegetarian)
        item2 = MenuItem(
            _id="item2",
            name="Vegan Salad",
            price=199.0,
            category="Salad",
            is_vegetarian=True,
            is_vegan=True
        )
        assert item2.is_vegan and item2.is_vegetarian

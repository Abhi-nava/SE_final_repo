"""
Pytest configuration for unit tests.
Sets up global database mocking for all unit tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(scope="function", autouse=True)
def mock_db():
    """Automatically mock the database for all unit tests"""
    # Create mock collections
    mock_orders = MagicMock()
    mock_orders.find_one = AsyncMock()
    mock_orders.update_one = AsyncMock()
    mock_orders.insert_one = AsyncMock()
    mock_orders.delete_one = AsyncMock()
    mock_orders.find = AsyncMock()
    
    mock_users = MagicMock()
    mock_restaurants = MagicMock()
    mock_menu_items = MagicMock()
    mock_delivery_agents = MagicMock()
    mock_ratings = MagicMock()
    
    # Create mock database
    mock_database = MagicMock()
    mock_database.orders = mock_orders
    mock_database.users = mock_users
    mock_database.restaurants = mock_restaurants
    mock_database.menu_items = mock_menu_items
    mock_database.delivery_agents = mock_delivery_agents
    mock_database.ratings = mock_ratings
    
    # Patch database in all relevant modules
    with patch('routes.orders.db', mock_database):
        with patch('database.db', mock_database):
            yield mock_database


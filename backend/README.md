# Food Delivery System - Backend API

## Overview
FastAPI-based backend for a multi-role food delivery application (like Zomato/Swiggy).

## Features
- User authentication with JWT and role-based access control
- Restaurant menu management system
- Order management with real-time status updates
- Delivery agent assignment and tracking
- Rating and review system
- MongoDB integration
- Security features: password hashing, OTP verification, RBAC

## Installation

1. Create virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

2. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Configure environment variables:
\`\`\`bash
cp .env.example .env
# Edit .env with your settings
\`\`\`

4. Run the server:
\`\`\`bash
uvicorn main:app --reload
\`\`\`

API will be available at: http://localhost:8000
Swagger UI: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/me` - Get current user
- `POST /api/auth/request-otp` - Request password reset OTP
- `POST /api/auth/reset-password` - Reset password

### Customers
- `GET /api/customers/restaurants` - List restaurants
- `GET /api/customers/restaurants/{id}` - Get restaurant details
- `PUT /api/customers/profile` - Update profile

### Restaurants
- `POST /api/restaurants/create` - Create restaurant
- `GET /api/restaurants/my-restaurant` - Get my restaurant
- `PUT /api/restaurants/my-restaurant` - Update restaurant
- `POST /api/restaurants/menu-items` - Add menu item
- `GET /api/restaurants/menu-items` - Get menu items
- `PUT /api/restaurants/menu-items/{id}` - Update menu item
- `DELETE /api/restaurants/menu-items/{id}` - Delete menu item

### Orders
- `POST /api/orders/create` - Create order
- `GET /api/orders/{id}` - Get order details
- `GET /api/orders/my-orders` - Get my orders
- `POST /api/orders/{id}/cancel` - Cancel order
- `GET /api/orders/restaurant/incoming` - Get restaurant orders
- `PUT /api/orders/{id}/status` - Update order status

### Delivery
- `POST /api/delivery/register` - Register as delivery agent
- `GET /api/delivery/profile` - Get agent profile
- `PUT /api/delivery/profile` - Update agent profile
- `POST /api/delivery/location` - Update location
- `GET /api/delivery/available-orders` - Get available orders
- `POST /api/delivery/{id}/accept` - Accept delivery
- `PUT /api/delivery/{id}/status` - Update delivery status
- `GET /api/delivery/my-deliveries` - Get my deliveries

### Ratings
- `POST /api/ratings/create` - Submit rating
- `GET /api/ratings/restaurant/{id}` - Get restaurant ratings
- `GET /api/ratings/delivery-agent/{id}` - Get agent ratings

## Database Schema

### Users Collection
- email (unique)
- phone (unique)
- password_hash
- role (customer, restaurant, delivery_agent)
- created_at, updated_at

### Restaurants Collection
- owner_id (foreign key to users)
- name, description, phone, address
- cuisine_types, opening_time, closing_time
- rating, total_ratings
- is_active

### Menu Items Collection
- restaurant_id
- name, description, price, category
- availability, is_vegetarian, is_vegan
- preparation_time

### Orders Collection
- customer_id, restaurant_id, delivery_agent_id
- items (array of order items)
- subtotal, delivery_fee, discount, total
- status, payment_method
- delivery_address, delivery_phone
- estimated_delivery_time

### Delivery Agents Collection
- user_id
- vehicle_type, vehicle_number, license_number
- status, rating, total_deliveries
- is_verified

### Ratings Collection
- order_id, customer_id, restaurant_id, delivery_agent_id
- restaurant_rating, delivery_rating
- reviews

## Security Features
- Bcrypt password hashing
- JWT token authentication
- Role-based access control (RBAC)
- OTP verification for password reset
- Input validation with Pydantic
- CORS protection
- TLS/HTTPS ready

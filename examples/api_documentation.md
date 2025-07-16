# Example API Documentation

## User Management API

### Overview
The User Management API allows you to create, read, update, and delete user accounts in your application. This RESTful API provides comprehensive user management capabilities.

### Base URL
```
https://api.example.com/v1
```

### Authentication
All API requests require authentication using an API key in the header:

```http
Authorization: Bearer YOUR_API_KEY
```

### Endpoints

#### Create User
Create a new user account.

**Endpoint:** `POST /users`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

**Example (Python):**
```python
import requests

url = "https://api.example.com/v1/users"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "email": "user@example.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user"
}

response = requests.post(url, json=data, headers=headers)
user = response.json()
print(f"Created user: {user['id']}")
```

#### Get User
Retrieve user information by ID.

**Endpoint:** `GET /users/{user_id}`

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-20T14:22:00Z",
  "status": "active"
}
```

**Example (JavaScript):**
```javascript
async function getUser(userId) {
    const response = await fetch(`https://api.example.com/v1/users/${userId}`, {
        headers: {
            'Authorization': 'Bearer YOUR_API_KEY'
        }
    });
    
    if (response.ok) {
        const user = await response.json();
        console.log('User data:', user);
        return user;
    } else {
        throw new Error(`Error: ${response.status}`);
    }
}
```

#### Update User
Update user information.

**Endpoint:** `PUT /users/{user_id}`

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "admin"
}
```

#### Delete User
Delete a user account.

**Endpoint:** `DELETE /users/{user_id}`

**Response:** `204 No Content`

### Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  }
}
```

**Common Error Codes:**
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (user doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

### Rate Limiting
The API enforces rate limits:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated requests

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Pagination
List endpoints support pagination using query parameters:

**Example:** `GET /users?page=2&limit=20`

**Response includes pagination metadata:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

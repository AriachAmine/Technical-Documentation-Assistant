# Python SDK Documentation

## Installation

Install the SDK using pip:

```bash
pip install example-api-sdk
```

## Quick Start

```python
from example_api import Client

# Initialize the client
client = Client(api_key="your_api_key_here")

# Create a user
user = client.users.create(
    email="user@example.com",
    password="secure_password",
    first_name="John",
    last_name="Doe"
)

print(f"Created user: {user.id}")
```

## Authentication

The SDK handles authentication automatically using your API key:

```python
from example_api import Client

# Method 1: Pass API key directly
client = Client(api_key="your_api_key")

# Method 2: Use environment variable
import os
os.environ['EXAMPLE_API_KEY'] = 'your_api_key'
client = Client()  # Will automatically use the environment variable
```

## User Management

### Creating Users

```python
# Basic user creation
user = client.users.create(
    email="user@example.com",
    password="secure_password123",
    first_name="John",
    last_name="Doe"
)

# Create user with additional options
admin_user = client.users.create(
    email="admin@example.com",
    password="admin_password123",
    first_name="Admin",
    last_name="User",
    role="admin"
)
```

### Retrieving Users

```python
# Get a specific user by ID
user = client.users.get(user_id=123)
print(f"User: {user.first_name} {user.last_name}")

# List all users
users = client.users.list()
for user in users:
    print(f"ID: {user.id}, Email: {user.email}")

# List users with pagination
users = client.users.list(page=2, limit=50)
print(f"Total users: {users.pagination.total}")
```

### Updating Users

```python
# Update user information
updated_user = client.users.update(
    user_id=123,
    first_name="Jane",
    last_name="Smith",
    role="moderator"
)

# Partial updates are supported
user = client.users.update(user_id=123, role="admin")
```

### Deleting Users

```python
# Delete a user
client.users.delete(user_id=123)
print("User deleted successfully")
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from example_api import Client, APIError, ValidationError, NotFoundError

client = Client(api_key="your_api_key")

try:
    user = client.users.create(
        email="invalid-email",  # This will cause a validation error
        password="123",         # Too short password
        first_name="John",
        last_name="Doe"
    )
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Field errors: {e.details}")
except APIError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

### Exception Types

- `APIError` - Base exception for all API errors
- `ValidationError` - Raised for validation failures (400 status)
- `AuthenticationError` - Raised for authentication failures (401 status)
- `PermissionError` - Raised for permission failures (403 status)
- `NotFoundError` - Raised when resource is not found (404 status)
- `RateLimitError` - Raised when rate limit is exceeded (429 status)

## Configuration

### Custom Configuration

```python
from example_api import Client, Config

# Custom configuration
config = Config(
    base_url="https://custom-api.example.com/v1",
    timeout=30,
    max_retries=3,
    retry_delay=1.0
)

client = Client(api_key="your_api_key", config=config)
```

### Environment Variables

The SDK supports the following environment variables:

- `EXAMPLE_API_KEY` - Your API key
- `EXAMPLE_API_BASE_URL` - Custom base URL
- `EXAMPLE_API_TIMEOUT` - Request timeout in seconds

## Advanced Features

### Batch Operations

```python
# Create multiple users at once
users_data = [
    {"email": "user1@example.com", "password": "pass1", "first_name": "User", "last_name": "One"},
    {"email": "user2@example.com", "password": "pass2", "first_name": "User", "last_name": "Two"},
]

# Batch create (if supported by API)
results = client.users.batch_create(users_data)
for result in results:
    if result.success:
        print(f"Created user: {result.user.id}")
    else:
        print(f"Failed to create user: {result.error}")
```

### Async Support

The SDK also supports async operations:

```python
import asyncio
from example_api import AsyncClient

async def main():
    async with AsyncClient(api_key="your_api_key") as client:
        # Async user creation
        user = await client.users.create(
            email="async_user@example.com",
            password="secure_password",
            first_name="Async",
            last_name="User"
        )
        print(f"Created user: {user.id}")
        
        # Async user retrieval
        users = await client.users.list()
        print(f"Total users: {len(users)}")

# Run the async function
asyncio.run(main())
```

### Pagination Helpers

```python
# Iterate through all users automatically
for user in client.users.iter_all():
    print(f"Processing user: {user.email}")

# Get all users as a list (be careful with large datasets)
all_users = client.users.get_all()
print(f"Total users loaded: {len(all_users)}")
```

## Models and Data Types

### User Model

```python
from example_api.models import User

# User object properties
user = client.users.get(123)
print(user.id)          # int
print(user.email)       # str
print(user.first_name)  # str
print(user.last_name)   # str
print(user.role)        # str ("user", "admin", "moderator")
print(user.status)      # str ("active", "inactive", "suspended")
print(user.created_at)  # datetime
print(user.last_login)  # datetime or None

# User methods
print(user.full_name)   # Property: f"{first_name} {last_name}"
print(user.is_admin)    # Property: role == "admin"
user.activate()         # Method to activate user
user.deactivate()       # Method to deactivate user
```

## Best Practices

### 1. Use Environment Variables for API Keys

```python
import os
from example_api import Client

# Don't hardcode API keys
api_key = os.getenv('EXAMPLE_API_KEY')
if not api_key:
    raise ValueError("API key not found in environment variables")

client = Client(api_key=api_key)
```

### 2. Handle Rate Limits

```python
import time
from example_api import RateLimitError

def create_user_with_retry(client, user_data, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.users.create(**user_data)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = e.retry_after or 60  # Wait time from headers
                print(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
```

### 3. Use Context Managers for Resource Management

```python
from example_api import Client

# Automatically handles connection cleanup
with Client(api_key="your_api_key") as client:
    users = client.users.list()
    # Process users...
# Connection is automatically closed here
```

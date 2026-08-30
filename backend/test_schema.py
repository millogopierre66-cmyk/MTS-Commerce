from app.schemas.user import UserCreate

user = UserCreate(
    username="Pierre",
    email="pierre@example.com",
    password="Admin123!"
)

print(user)
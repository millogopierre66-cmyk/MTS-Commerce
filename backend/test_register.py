from app.schemas.user import UserCreate

user = UserCreate(
    username="pierre",
    email="pierre@gmail.com",
    password="Admin123!"
)

print(user)
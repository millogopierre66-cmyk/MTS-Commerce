from app.database.session import SessionLocal
from app.models.user import User

db = SessionLocal()

users = db.query(User).all()

for user in users:
    print("--------------------")
    print("ID :", user.id)
    print("Username :", user.username)
    print("Email :", user.email)
    print("Role :", user.role)
    print("Hash :", user.password)
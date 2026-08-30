from app.models.user import User
from app.security.hashing import hash_password


def create_admin(db):

    admin = (
        db.query(User)
        .filter(User.username == "admin")
        .first()
    )

    if admin:
        return

    admin = User(
        username="admin",
        email="admin@mts.local",
        password=hash_password("Admin123!"),
    )

    db.add(admin)
    db.commit()

    print("Administrateur créé.")
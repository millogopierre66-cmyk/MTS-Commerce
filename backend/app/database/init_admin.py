from app.core.config import settings
from app.models.user import User
from app.security.hashing import hash_password


def create_admin(db):
    """Cr?e l'administrateur initial uniquement s'il n'existe pas."""

    admin = (
        db.query(User)
        .filter(User.username == "admin")
        .first()
    )

    # Ne pas remplacer le mot de passe d'un administrateur existant.
    if admin:
        return admin

    configured_password = settings.ADMIN_INITIAL_PASSWORD

    if configured_password is None:
        raise RuntimeError(
            "Compte administrateur absent. Configurez "
            "ADMIN_INITIAL_PASSWORD dans .env avant de cr?er le compte."
        )

    initial_password = configured_password.get_secret_value()

    if not initial_password.strip():
        raise RuntimeError(
            "ADMIN_INITIAL_PASSWORD est vide. "
            "Configurez un mot de passe initial non vide dans .env."
        )

    admin = User(
        username="admin",
        email="admin@mts.local",
        password=hash_password(initial_password),
        role="admin",
        is_active=True,
    )

    db.add(admin)
    db.commit()

    print("Administrateur initial cr??.")
    return admin

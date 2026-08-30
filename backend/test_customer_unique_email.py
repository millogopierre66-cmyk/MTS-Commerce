from app.database.session import SessionLocal
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerUpdate
from fastapi import HTTPException

db = SessionLocal()

try:
    print("TEST UNICITE EMAIL - MODIFICATION")
    print("=" * 70)

    try:
        CustomerService.update(
            db,
            3,
            CustomerUpdate(
                email="jean.ouedraogo@test.com"
            )
        )

        print("TEST: ERREUR - modification acceptee")

    except HTTPException as e:
        print("Exception = HTTPException")
        print(f"Statut HTTP = {e.status_code}")
        print(f"Detail = {e.detail}")

        if (
            e.status_code == 400
            and e.detail == "Cette adresse email est déjà utilisée."
        ):
            print("TEST: OK")
        else:
            print("TEST: ERREUR")

finally:
    db.close()

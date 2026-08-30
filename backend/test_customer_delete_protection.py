from app.database.session import SessionLocal
from app.services.customer_service import CustomerService
from app.models.customer import Customer
from fastapi import HTTPException


db = SessionLocal()

try:
    customer_id = 3

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    print("TEST PROTECTION SUPPRESSION CLIENT")
    print("=" * 70)

    if not customer:
        print("ERREUR : client introuvable.")

    else:
        print(f"Client ID = {customer.id}")
        print(
            f"Nom = "
            f"{customer.first_name} {customer.last_name}"
        )

        try:
            CustomerService.delete(
                db,
                customer_id
            )

            print("TEST: ERREUR - client supprime")

        except HTTPException as e:

            print("Exception = HTTPException")
            print(f"Statut HTTP = {e.status_code}")
            print(f"Detail = {e.detail}")

            customer_after = (
                db.query(Customer)
                .filter(Customer.id == customer_id)
                .first()
            )

            print(
                "Client toujours present = "
                f"{customer_after is not None}"
            )

            if (
                e.status_code == 400
                and customer_after is not None
            ):
                print(
                    "TEST: OK - SUPPRESSION BLOQUEE"
                )
            else:
                print("TEST: ERREUR")

finally:
    db.close()

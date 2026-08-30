from app.database.session import SessionLocal
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerUpdate

db = SessionLocal()

try:
    print("TEST AUTO-MODIFICATION CLIENT")
    print("=" * 70)

    customer = CustomerService.update(
        db,
        3,
        CustomerUpdate(
            first_name="Client Modifie",
            phone="70000002",
            email="client.test.vente2@example.com"
        )
    )

    print(f"ID = {customer.id}")
    print(f"Nom = {customer.first_name} {customer.last_name}")
    print(f"Telephone = {customer.phone}")
    print(f"Email = {customer.email}")

    print("=" * 70)

    if (
        customer.id == 3
        and customer.first_name == "Client Modifie"
        and customer.phone == "70000002"
        and customer.email == "client.test.vente2@example.com"
    ):
        print("TEST: OK")
    else:
        print("TEST: ERREUR")

finally:
    db.close()

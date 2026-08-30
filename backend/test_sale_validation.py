from pydantic import ValidationError
from app.schemas.sale import SaleCreate


print("TEST VALIDATION DES VENTES")
print("=" * 70)

tests_ok = 0

# ==========================================================
# TEST 1 : quantité négative
# ==========================================================

try:
    SaleCreate(
        items=[
            {
                "product_id": 5,
                "quantity": -2
            }
        ]
    )

    print("TEST 1: ERREUR - quantité négative acceptée")

except ValidationError:
    print("TEST 1: OK - quantité négative refusée")
    tests_ok += 1


# ==========================================================
# TEST 2 : quantité zéro
# ==========================================================

try:
    SaleCreate(
        items=[
            {
                "product_id": 5,
                "quantity": 0
            }
        ]
    )

    print("TEST 2: ERREUR - quantité zéro acceptée")

except ValidationError:
    print("TEST 2: OK - quantité zéro refusée")
    tests_ok += 1


# ==========================================================
# TEST 3 : aucun article
# ==========================================================

try:
    SaleCreate(
        items=[]
    )

    print("TEST 3: ERREUR - vente vide acceptée")

except ValidationError:
    print("TEST 3: OK - vente sans article refusée")
    tests_ok += 1


# ==========================================================
# RESULTAT
# ==========================================================

print("=" * 70)
print(
    f"RESULTAT: {tests_ok}/3 TESTS OK"
)

print(
    "TEST GLOBAL:",
    "OK" if tests_ok == 3 else "ERREUR"
)
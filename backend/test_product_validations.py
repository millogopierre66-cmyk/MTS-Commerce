from pydantic import ValidationError

from app.schemas.product import (
    ProductCreate,
    ProductUpdate
)


def test_validation(name, func):
    try:
        func()
        print(f"{name}: ERREUR - valeur acceptee")

    except ValidationError:
        print(f"{name}: OK - valeur refusee")


print("TEST GLOBAL DES VALIDATIONS PRODUIT")
print("=" * 70)

# ==========================================================
# TEST 1 : PRIX D'ACHAT NEGATIF
# ==========================================================

test_validation(
    "TEST 1 - Prix achat negatif",
    lambda: ProductCreate(
        reference="TEST-NEG-001",
        barcode="100000000001",
        name="Produit test",
        category="Test",
        purchase_price=-100,
        selling_price=100
    )
)

# ==========================================================
# TEST 2 : PRIX DE VENTE NEGATIF
# ==========================================================

test_validation(
    "TEST 2 - Prix vente negatif",
    lambda: ProductCreate(
        reference="TEST-NEG-002",
        barcode="100000000002",
        name="Produit test",
        category="Test",
        purchase_price=100,
        selling_price=-100
    )
)

# ==========================================================
# TEST 3 : QUANTITE NEGATIVE
# ==========================================================

test_validation(
    "TEST 3 - Quantite negative",
    lambda: ProductCreate(
        reference="TEST-NEG-003",
        barcode="100000000003",
        name="Produit test",
        category="Test",
        purchase_price=100,
        selling_price=200,
        quantity=-10
    )
)

# ==========================================================
# TEST 4 : ALERTE STOCK NEGATIVE
# ==========================================================

test_validation(
    "TEST 4 - Alerte stock negative",
    lambda: ProductCreate(
        reference="TEST-NEG-004",
        barcode="100000000004",
        name="Produit test",
        category="Test",
        purchase_price=100,
        selling_price=200,
        alert_stock=-1
    )
)

# ==========================================================
# TEST 5 : STOCK MINIMUM NEGATIF
# ==========================================================

test_validation(
    "TEST 5 - Stock minimum negatif",
    lambda: ProductCreate(
        reference="TEST-NEG-005",
        barcode="100000000005",
        name="Produit test",
        category="Test",
        purchase_price=100,
        selling_price=200,
        minimum_stock=-5
    )
)

# ==========================================================
# TEST 6 : MODIFICATION PRIX NEGATIF
# ==========================================================

test_validation(
    "TEST 6 - Modification prix negatif",
    lambda: ProductUpdate(
        selling_price=-5000
    )
)

# ==========================================================
# TEST 7 : MODIFICATION ALERTE NEGATIVE
# ==========================================================

test_validation(
    "TEST 7 - Modification alerte negative",
    lambda: ProductUpdate(
        alert_stock=-1
    )
)

# ==========================================================
# TEST 8 : MODIFICATION DIRECTE DU STOCK
# ==========================================================

test_validation(
    "TEST 8 - Modification directe quantity",
    lambda: ProductUpdate(
        quantity=999
    )
)

print("=" * 70)
print("FIN DES TESTS")


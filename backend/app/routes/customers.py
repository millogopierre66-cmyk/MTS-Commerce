from sqlalchemy.orm import Session

from fastapi import APIRouter
from fastapi import Depends

from app.database.session import SessionLocal

from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)

from app.services.customer_service import CustomerService

from app.security.auth import require_roles


router = APIRouter(
    prefix="/customers",
    tags=["Clients"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================================
# CRÉER UN CLIENT
# ==========================================================

@router.post(
    "/",
    response_model=CustomerResponse
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "admin",
            "manager",
            "vendeur"
        )
    )
):
    return CustomerService.create(
        db,
        customer
    )


# ==========================================================
# LISTE DES CLIENTS
# ==========================================================

@router.get(
    "/",
    response_model=list[CustomerResponse]
)
def get_customers(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "admin",
            "manager",
            "vendeur"
        )
    )
):
    return CustomerService.get_all(db)


# ==========================================================
# RECHERCHE CLIENT
# ==========================================================

@router.get(
    "/search/{keyword}",
    response_model=list[CustomerResponse]
)
def search_customer(
    keyword: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "admin",
            "manager",
            "vendeur"
        )
    )
):
    return CustomerService.search(
        db,
        keyword
    )


# ==========================================================
# CLIENTS ACTIFS
# ==========================================================

@router.get(
    "/active",
    response_model=list[CustomerResponse]
)
def active_customers(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "admin",
            "manager",
            "vendeur"
        )
    )
):
    return CustomerService.active(db)


# ==========================================================
# CLIENT PAR ID
# ==========================================================

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "admin",
            "manager",
            "vendeur"
        )
    )
):
    return CustomerService.get_by_id(
        db,
        customer_id
    )


# ==========================================================
# MODIFIER UN CLIENT
# ==========================================================

@router.put(
    "/{customer_id}",
    response_model=CustomerResponse
)
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "admin",
            "manager",
            "vendeur"
        )
    )
):
    return CustomerService.update(
        db,
        customer_id,
        customer
    )


# ==========================================================
# SUPPRIMER UN CLIENT
# ==========================================================

@router.delete(
    "/{customer_id}"
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "admin",
            "manager"
        )
    )
):
    return CustomerService.delete(
        db,
        customer_id
    )


from app.models.sale import Sale
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer

from app.repositories.customer_repository import CustomerRepository

from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
)


class CustomerService:

    @staticmethod
    def create(
        db: Session,
        data: CustomerCreate
    ):

        if CustomerRepository.get_by_phone(db, data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce numéro de téléphone est déjà utilisé."
            )

        if (
            data.email
            and CustomerRepository.get_by_email(db, data.email)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette adresse email est déjà utilisée."
            )

        customer = Customer(
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            email=data.email,
            address=data.address,
            city=data.city
        )

        return CustomerRepository.create(
            db,
            customer
        )

    @staticmethod
    def get_all(db: Session):
        return CustomerRepository.get_all(db)

    @staticmethod
    def get_by_id(
        db: Session,
        customer_id: int
    ):

        customer = CustomerRepository.get_by_id(
            db,
            customer_id
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client introuvable."
            )

        return customer

    @staticmethod
    def update(
        db: Session,
        customer_id: int,
        data: CustomerUpdate
    ):

        customer = CustomerRepository.get_by_id(
            db,
            customer_id
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client introuvable."
            )

        if (
            data.phone
            and data.phone != customer.phone
        ):
            existing = CustomerRepository.get_by_phone(
                db,
                data.phone
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce numéro de téléphone est déjà utilisé."
                )

        if (
            data.email
            and data.email != customer.email
        ):
            existing = CustomerRepository.get_by_email(
                db,
                data.email
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cette adresse email est déjà utilisée."
                )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(customer, field, value)

        return CustomerRepository.update(
            db,
            customer
        )

    @staticmethod
    def delete(
        db: Session,
        customer_id: int
    ):

        customer = CustomerRepository.get_by_id(
            db,
            customer_id
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client introuvable."
            )

        # Vérifier si le client possède des ventes
        sales_count = (
            db.query(Sale)
            .filter(Sale.customer_id == customer_id)
            .count()
        )

        if sales_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Impossible de supprimer ce client : "
                    f"{sales_count} vente(s) sont liées à ce client."
                )
            )

        CustomerRepository.delete(
            db,
            customer
        )

        return {
            "message": "Client supprimé avec succès."
        }

    @staticmethod
    def search(
        db: Session,
        keyword: str
    ):
        return CustomerRepository.search(
            db,
            keyword
        )


    @staticmethod
    def active(
        db: Session
    ):
        return CustomerRepository.get_active(db)
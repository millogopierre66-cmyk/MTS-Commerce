from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
 
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.schemas.sale import (
    SaleCreate,
    SaleResponse,
)

from app.repositories.sale_repository import SaleRepository
from app.services.sale_service import SaleService

from app.security.auth import (
    get_current_admin,
    require_roles
)

router = APIRouter(
    prefix="/sales",
    tags=["Ventes"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=SaleResponse
)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "manager", "vendeur")
    )
):
    return SaleService.create_sale(
        db,
        sale
    )


@router.get(
    "/",
    response_model=list[SaleResponse]
)
def get_sales(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "manager")
    )
):
    return SaleRepository.get_all(db)


@router.get(
    "/{sale_id}",
    response_model=SaleResponse
)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "manager")
    )
):

    sale = SaleRepository.get_by_id(
        db,
        sale_id
    )

    if not sale:
        raise HTTPException(
            status_code=404,
            detail="Vente introuvable."
        )

    return sale


@router.delete(
    "/{sale_id}"
    )
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return SaleService.delete_sale(
    db,
    sale_id
    )
 
@router.get("/{sale_id}/invoice")
def invoice(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "manager", "vendeur")
    )
):
    sale = SaleRepository.get_by_id(
        db,
        sale_id
    )

    if not sale:
        raise HTTPException(
            status_code=404,
            detail="Vente introuvable."
        )

    from app.reports.invoice_generator import InvoiceGenerator

    filename = f"invoice_{sale.invoice_number}.pdf"

    InvoiceGenerator.generate(
        filename,
        sale
    )

    return FileResponse(
        path=filename,
        media_type="application/pdf",
        filename=filename
    )
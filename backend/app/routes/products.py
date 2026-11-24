from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductCatalogueResponse,
)
from app.services.product_service import ProductService
from app.security.auth import (
    get_current_user,
    get_current_admin,
    require_roles,
)


router = APIRouter(
    prefix="/products",
    tags=["Produits"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=ProductResponse,
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "manager")),
):
    return ProductService.create(db, product)


@router.get(
    "/",
    response_model=list[ProductResponse],
)
def list_products(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ProductService.get_all(db)


@router.get(
    "/archived",
    response_model=list[ProductResponse],
)
def list_archived_products(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return ProductService.get_archived(db)


@router.get(
    "/catalogue",
    response_model=ProductCatalogueResponse,
)
def search_products(
    q: str | None = Query(default=None, max_length=200),
    category: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ProductService.get_catalogue(
        db=db,
        q=q,
        category=category,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ProductService.get_one(
        db,
        product_id,
        current_user=current_user,
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "manager")),
):
    return ProductService.update(db, product_id, product)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return ProductService.delete(
        db,
        product_id,
        current_user=current_user,
    )

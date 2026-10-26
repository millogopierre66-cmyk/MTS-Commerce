from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import STOCK_IN, STOCK_OUT
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.stock_repository import StockRepository
from app.schemas.sale import SaleCreate
from app.services.audit_log_service import AuditLogService
from app.services.invoice_number_service import InvoiceNumberService


class SaleService:

    @staticmethod
    def create_sale(
        db: Session,
        data: SaleCreate,
        current_user,
    ) -> Sale:
        """
        Cr?e une vente dans une transaction unique.
        Le num?ro de facture est r?serv? s?par?ment pour ?viter
        les collisions entre ventes concurrentes.
        """
        try:
            if data.customer_id is not None:
                customer = db.get(Customer, data.customer_id)
                if customer is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Client introuvable.",
                    )

            invoice_number = InvoiceNumberService.reserve_invoice_number()

            sale = Sale(
                invoice_number=invoice_number,
                customer_id=data.customer_id,
                user_id=current_user.id,
                total=0,
                status="completed",
            )

            SaleRepository.create_sale(db, sale)

            total = 0.0

            for item in data.items:
                product = ProductRepository.get_by_id(
                    db,
                    item.product_id,
                )

                if product is None:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Produit {item.product_id} introuvable.",
                    )

                if not product.active:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Le produit {product.name} est inactif.",
                    )

                if product.quantity < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuffisant pour {product.name}.",
                    )

                # Mise ? jour atomique : prot?ge contre un stock
                # insuffisant si une autre vente intervient en parall?le.
                stock_updated = StockRepository.decrement_stock_atomic(
                    db,
                    product.id,
                    item.quantity,
                )

                if not stock_updated:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            f"Le stock de {product.name} a chang?. "
                            "Actualisez le stock et recommencez."
                        ),
                    )

                unit_price = float(product.selling_price)
                purchase_unit_price = (
                    float(product.purchase_price)
                    if product.purchase_price is not None
                    else None
                )
                subtotal = unit_price * item.quantity
                total += subtotal

                SaleRepository.add_item(
                    db,
                    SaleItem(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=item.quantity,
                        unit_price=unit_price,
                        purchase_unit_price=purchase_unit_price,
                        subtotal=subtotal,
                    ),
                )

                StockRepository.create_movement(
                    db,
                    StockMovement(
                        product_id=product.id,
                        user_id=current_user.id,
                        movement_type=STOCK_OUT,
                        quantity=item.quantity,
                        description=f"Vente {sale.invoice_number}",
                    ),
                )

            sale.total = total

            # Le journal est ajout? ? la m?me transaction :
            # aucun commit n'est effectu? ? l'int?rieur du service d'audit.
            AuditLogService.log(
                db,
                action="SALE_CREATED",
                user_id=current_user.id,
                username=getattr(current_user, "username", None),
                entity_type="Sale",
                entity_id=sale.id,
                description=(
                    f"Cr?ation de la vente {sale.invoice_number}."
                ),
                commit=False,
            )

            db.commit()
            db.refresh(sale)
            return sale

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def cancel_sale(
        db: Session,
        sale_id: int,
        current_user,
    ) -> dict:
        """
        Annule une vente sans la supprimer.
        Le changement conditionnel de statut emp?che la restauration
        r?p?t?e du stock en cas de demandes concurrentes.
        """
        try:
            sale = SaleRepository.get_by_id(db, sale_id)

            if sale is None:
                raise HTTPException(
                    status_code=404,
                    detail="Vente introuvable.",
                )

            if sale.status != "completed":
                raise HTTPException(
                    status_code=409,
                    detail="Cette vente est d?j? annul?e ou n'est plus annulable.",
                )

            cancelled_at = datetime.now(UTC).replace(tzinfo=None)

            # Cette modification conditionnelle doit pr?c?der
            # toute restauration du stock.
            cancelled = SaleRepository.cancel_if_completed(
                db,
                sale_id=sale.id,
                cancelled_at=cancelled_at,
                cancelled_by=current_user.id,
            )

            if not cancelled:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "La vente a d?j? ?t? annul?e par une autre op?ration."
                    ),
                )

            # Synchroniser aussi l'objet ORM d?j? charg?.
            sale.status = "cancelled"
            sale.cancelled_at = cancelled_at
            sale.cancelled_by = current_user.id

            for item in sale.items:
                stock_updated = StockRepository.increment_stock_atomic(
                    db,
                    item.product_id,
                    item.quantity,
                )

                if not stock_updated:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Produit {item.product_id} introuvable "
                            "lors de la restauration du stock."
                        ),
                    )

                StockRepository.create_movement(
                    db,
                    StockMovement(
                        product_id=item.product_id,
                        user_id=current_user.id,
                        movement_type=STOCK_IN,
                        quantity=item.quantity,
                        description=(
                            f"Annulation vente {sale.invoice_number}"
                        ),
                    ),
                )

            AuditLogService.log(
                db,
                action="SALE_CANCELLED",
                user_id=current_user.id,
                username=getattr(current_user, "username", None),
                entity_type="Sale",
                entity_id=sale.id,
                description=(
                    f"Annulation de la vente {sale.invoice_number}."
                ),
                commit=False,
            )

            # Vente, statut, mouvements, stock et audit sont valid?s ensemble.
            db.commit()

            return {
                "sale_id": sale.id,
                "invoice_number": sale.invoice_number,
                "status": sale.status,
                "cancelled_by": sale.cancelled_by,
                "message": "Vente annul?e ; le stock a ?t? restaur?.",
            }

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise

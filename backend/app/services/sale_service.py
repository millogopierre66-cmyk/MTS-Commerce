from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement

from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository

from app.schemas.sale import SaleCreate
from app.core.constants import STOCK_OUT
from app.core.constants import STOCK_IN, STOCK_OUT


class SaleService:

    @staticmethod
    def generate_invoice_number(db: Session):

        count = len(SaleRepository.get_all(db)) + 1

        return (
            f"FAC-"
            f"{datetime.now():%Y%m%d}-"
            f"{count:04d}"
        )

    @staticmethod
    def create_sale(
        db: Session,
        data: SaleCreate
    ):

        try:
            # ======================================================
            # CREATION DE LA VENTE
            # ======================================================

            sale = Sale(
                invoice_number=SaleService.generate_invoice_number(db),
                customer_id=data.customer_id,
                total=0
            )

            # flush uniquement :
            # la vente n'est PAS encore définitivement enregistrée
            SaleRepository.create_sale(
                db,
                sale
            )

            total = 0

            # ======================================================
            # PARCOURS DES PRODUITS
            # ======================================================

            for item in data.items:

                product = ProductRepository.get_by_id(
                    db,
                    item.product_id
                )

                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Produit {item.product_id} introuvable."
                    )

                if product.quantity < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuffisant pour {product.name}"
                    )

                # ==================================================
                # CALCUL DU SOUS-TOTAL
                # ==================================================

                subtotal = (
                    product.selling_price
                    * item.quantity
                )

                total += subtotal

                # ==================================================
                # LIGNE DE VENTE
                # ==================================================

                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    unit_price=product.selling_price,
                    subtotal=subtotal
                )

                SaleRepository.add_item(
                    db,
                    sale_item
                )

                # ==================================================
                # MISE A JOUR DU STOCK
                # ==================================================

                product.quantity -= item.quantity

                # ==================================================
                # HISTORIQUE DU MOUVEMENT
                # ==================================================

                movement = StockMovement(
                    product_id=product.id,
                    movement_type=STOCK_OUT,
                    quantity=item.quantity,
                    description=f"Vente {sale.invoice_number}"
                )

                db.add(movement)

            # ======================================================
            # TOTAL DE LA VENTE
            # ======================================================

            sale.total = total

            # ======================================================
            # VALIDATION DE LA TRANSACTION
            # ======================================================

            SaleRepository.commit(db)

            SaleRepository.refresh(
                db,
                sale
            )

            return sale

        except HTTPException:
            # Annule toutes les modifications de cette transaction
            db.rollback()
            raise

        except Exception:
            # Annule également toute modification en cas
            # d'erreur inattendue
            db.rollback()
            raise
    
    @staticmethod
    def delete_sale(
        db: Session,
        sale_id: int
    ):

        try:
            # ==================================================
            # RECUPERATION DE LA VENTE
            # ==================================================

            sale = SaleRepository.get_by_id(
                db,
                sale_id
            )

            if not sale:
                raise HTTPException(
                    status_code=404,
                    detail="Vente introuvable."
                )

            # ==================================================
            # RESTAURATION DU STOCK
            # ==================================================

            for item in sale.items:

                product = ProductRepository.get_by_id(
                    db,
                    item.product_id
                )

                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Produit {item.product_id} "
                            "introuvable lors de l'annulation."
                        )
                    )

                # Restaurer la quantite vendue
                product.quantity += item.quantity

                # Historique de l'annulation
                movement = StockMovement(
                    product_id=product.id,
                    movement_type=STOCK_IN,
                    quantity=item.quantity,
                    description=(
                        f"Annulation vente "
                        f"{sale.invoice_number}"
                    )
                )

                db.add(movement)

            # ==================================================
            # SUPPRESSION DE LA VENTE
            # Les SaleItem sont supprimes grace au cascade
            # ==================================================

            db.delete(sale)

            # ==================================================
            # VALIDATION DE LA TRANSACTION
            # ==================================================

            db.commit()

            return {
                "message": (
                    "Vente annulee avec succes. "
                    "Le stock a ete restaure."
                )
            }

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise

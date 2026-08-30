from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class InvoiceGenerator:

    @staticmethod
    def generate(filepath: str, sale):

        pdf = canvas.Canvas(
            filepath,
            pagesize=A4
        )

        width, height = A4

        # ==========================================================
        # EN-TETE
        # ==========================================================

        pdf.setFont("Helvetica-Bold", 20)

        pdf.drawString(
            50,
            height - 50,
            "MTS COMMERCE"
        )

        pdf.setFont("Helvetica", 12)

        pdf.drawString(
            50,
            height - 90,
            f"Facture : {sale.invoice_number}"
        )

        # ==========================================================
        # INFORMATIONS CLIENT
        # ==========================================================

        if sale.customer:

            customer = sale.customer

            pdf.drawString(
                50,
                height - 110,
                f"Client : {customer.first_name} {customer.last_name}"
            )

            pdf.drawString(
                50,
                height - 130,
                f"Telephone : {customer.phone}"
            )

            pdf.drawString(
                50,
                height - 150,
                f"Adresse : {customer.address or '-'}"
            )

            pdf.drawString(
                50,
                height - 170,
                f"Ville : {customer.city or '-'}"
            )

            y = height - 220

        else:

            pdf.drawString(
                50,
                height - 110,
                "Client : Client non renseigne"
            )

            y = height - 160

        # ==========================================================
        # TOTAL
        # ==========================================================

        pdf.setFont("Helvetica-Bold", 12)

        pdf.drawString(
            50,
            y,
            f"Total : {sale.total:,.2f} FCFA"
        )

        y -= 50

        # ==========================================================
        # TITRE DU TABLEAU
        # ==========================================================

        pdf.setFont("Helvetica-Bold", 12)

        pdf.drawString(
            50,
            y,
            "Produits"
        )

        pdf.drawRightString(
            350,
            y,
            "Quantite"
        )

        pdf.drawRightString(
            500,
            y,
            "Sous-total"
        )

        y -= 25

        # ==========================================================
        # ARTICLES
        # ==========================================================

        pdf.setFont("Helvetica", 12)

        for item in sale.items:

            pdf.drawString(
                50,
                y,
                item.product.name
            )

            pdf.drawRightString(
                350,
                y,
                str(item.quantity)
            )

            pdf.drawRightString(
                500,
                y,
                f"{item.subtotal:,.2f}"
            )

            y -= 20

        # ==========================================================
        # PIED DE PAGE
        # ==========================================================

        y -= 30

        pdf.setFont("Helvetica-Bold", 12)

        pdf.drawRightString(
            500,
            y,
            f"TOTAL : {sale.total:,.2f} FCFA"
        )

        pdf.setFont("Helvetica", 10)

        pdf.drawString(
            50,
            50,
            "Merci pour votre confiance."
        )

        pdf.save()


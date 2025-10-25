"""
Service de facturation avec génération de PDF
Génération automatique de factures professionnelles
"""

from typing import Dict, Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io
import os

from subscription_helpers import get_invoice_by_id
from db_helpers import get_user_by_id


class InvoiceService:
    """Service de génération de factures"""

    @staticmethod
    def generate_invoice_pdf(invoice_id: str) -> Optional[bytes]:
        """Génère un PDF pour une facture"""
        try:
            # Récupérer les données de la facture
            invoice = get_invoice_by_id(invoice_id)
            if not invoice:
                print(f"Invoice {invoice_id} not found")
                return None

            # Récupérer les données utilisateur
            user = get_user_by_id(invoice["user_id"])
            if not user:
                print(f"User {invoice['user_id']} not found")
                return None

            # Créer le buffer PDF
            buffer = io.BytesIO()

            # Créer le document PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2563eb'),
                spaceAfter=30,
                alignment=TA_CENTER
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1f2937'),
                spaceAfter=12
            )

            normal_style = styles['Normal']
            normal_style.fontSize = 10

            # Construire le contenu
            content = []

            # En-tête avec logo (si disponible)
            content.append(Paragraph("FACTURE", title_style))
            content.append(Spacer(1, 0.5*cm))

            # Informations de l'entreprise
            company_info = f"""
            <b>ShareYourSales</b><br/>
            123 Avenue Mohammed V<br/>
            Casablanca, Maroc<br/>
            Email: billing@shareyoursales.com<br/>
            Tél: +212 5XX-XXXXXX
            """
            content.append(Paragraph(company_info, normal_style))
            content.append(Spacer(1, 1*cm))

            # Informations client et facture côte à côte
            client_invoice_data = [
                [
                    Paragraph("<b>FACTURÉ À:</b>", heading_style),
                    Paragraph("<b>DÉTAILS FACTURE:</b>", heading_style)
                ],
                [
                    Paragraph(f"{user.get('email', 'N/A')}<br/>{user.get('phone', 'N/A')}", normal_style),
                    Paragraph(
                        f"<b>Numéro:</b> {invoice['invoice_number']}<br/>"
                        f"<b>Date:</b> {datetime.fromisoformat(invoice['issue_date'].replace('Z', '+00:00')).strftime('%d/%m/%Y')}<br/>"
                        f"<b>Échéance:</b> {datetime.fromisoformat(invoice['due_date'].replace('Z', '+00:00')).strftime('%d/%m/%Y')}<br/>"
                        f"<b>Statut:</b> {InvoiceService._format_status(invoice['status'])}",
                        normal_style
                    )
                ]
            ]

            client_invoice_table = Table(client_invoice_data, colWidths=[8*cm, 8*cm])
            client_invoice_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            content.append(client_invoice_table)
            content.append(Spacer(1, 1.5*cm))

            # Tableau des items
            content.append(Paragraph("DÉTAILS", heading_style))
            content.append(Spacer(1, 0.3*cm))

            # En-tête du tableau
            items_data = [
                ['Description', 'Quantité', 'Prix unitaire', 'Total']
            ]

            # Ajouter les items
            items = invoice.get('items', [])
            if isinstance(items, list):
                for item in items:
                    items_data.append([
                        item.get('description', 'N/A'),
                        str(item.get('quantity', 1)),
                        f"{item.get('amount', 0):.2f} {invoice.get('currency', 'MAD')}",
                        f"{item.get('amount', 0) * item.get('quantity', 1):.2f} {invoice.get('currency', 'MAD')}"
                    ])

            items_table = Table(items_data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
            items_table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

                # Corps du tableau
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),

                # Bordures
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2563eb')),

                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))

            content.append(items_table)
            content.append(Spacer(1, 1*cm))

            # Totaux
            subtotal = float(invoice.get('subtotal', 0))
            discount = float(invoice.get('discount', 0))
            tax = float(invoice.get('tax', 0))
            total = float(invoice.get('total', 0))
            currency = invoice.get('currency', 'MAD')

            totals_data = []

            if subtotal > 0:
                totals_data.append(['Sous-total:', f"{subtotal:.2f} {currency}"])

            if discount > 0:
                totals_data.append(['Réduction:', f"-{discount:.2f} {currency}"])

            if tax > 0:
                totals_data.append(['TVA (20%):', f"{tax:.2f} {currency}"])

            totals_data.append(['', ''])  # Ligne vide
            totals_data.append([Paragraph('<b>TOTAL:</b>', normal_style), Paragraph(f'<b>{total:.2f} {currency}</b>', normal_style)])

            totals_table = Table(totals_data, colWidths=[14*cm, 3*cm])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2563eb')),
                ('TOPPADDING', (0, -1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ]))

            content.append(totals_table)
            content.append(Spacer(1, 2*cm))

            # Notes et pied de page
            if invoice.get('notes'):
                content.append(Paragraph("<b>Notes:</b>", heading_style))
                content.append(Paragraph(invoice['notes'], normal_style))
                content.append(Spacer(1, 1*cm))

            footer_text = """
            <para alignment="center" fontSize="9" textColor="#6b7280">
            Merci pour votre confiance !<br/>
            En cas de question, contactez-nous à billing@shareyoursales.com<br/>
            <br/>
            <b>ShareYourSales</b> - Plateforme d'affiliation nouvelle génération
            </para>
            """
            content.append(Spacer(1, 1*cm))
            content.append(Paragraph(footer_text, normal_style))

            # Construire le PDF
            doc.build(content)

            # Récupérer les bytes du PDF
            pdf_bytes = buffer.getvalue()
            buffer.close()

            return pdf_bytes

        except Exception as e:
            print(f"Error generating invoice PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def _format_status(status: str) -> str:
        """Formate le statut de la facture pour l'affichage"""
        status_map = {
            'draft': 'Brouillon',
            'pending': 'En attente',
            'paid': 'Payée',
            'failed': 'Échouée',
            'refunded': 'Remboursée'
        }
        return status_map.get(status, status.capitalize())

    @staticmethod
    def save_invoice_pdf(invoice_id: str, save_path: str) -> Optional[str]:
        """Génère et sauvegarde un PDF de facture"""
        try:
            pdf_bytes = InvoiceService.generate_invoice_pdf(invoice_id)
            if not pdf_bytes:
                return None

            # Créer le dossier si nécessaire
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Sauvegarder le fichier
            with open(save_path, 'wb') as f:
                f.write(pdf_bytes)

            return save_path

        except Exception as e:
            print(f"Error saving invoice PDF: {e}")
            return None

    @staticmethod
    def send_invoice_email(invoice_id: str, user_email: str) -> bool:
        """Envoie une facture par email"""
        try:
            # Générer le PDF
            pdf_bytes = InvoiceService.generate_invoice_pdf(invoice_id)
            if not pdf_bytes:
                return False

            # TODO: Implémenter l'envoi d'email avec le PDF en pièce jointe
            # Utiliser un service comme SendGrid, AWS SES, ou SMTP
            print(f"Would send invoice {invoice_id} to {user_email}")

            return True

        except Exception as e:
            print(f"Error sending invoice email: {e}")
            return False


class InvoiceEmailTemplate:
    """Templates d'emails pour les factures"""

    @staticmethod
    def invoice_ready_template(invoice_number: str, total: float, currency: str, due_date: str) -> str:
        """Template pour facture prête"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9fafb; }}
                .invoice-details {{ background-color: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Nouvelle Facture</h1>
                </div>
                <div class="content">
                    <p>Bonjour,</p>
                    <p>Votre facture est maintenant disponible.</p>

                    <div class="invoice-details">
                        <h2>Détails de la facture</h2>
                        <p><strong>Numéro:</strong> {invoice_number}</p>
                        <p><strong>Montant total:</strong> {total:.2f} {currency}</p>
                        <p><strong>Date d'échéance:</strong> {due_date}</p>
                    </div>

                    <p>La facture est jointe à cet email au format PDF.</p>

                    <a href="https://shareyoursales.com/my-subscription/invoices" class="button">
                        Voir mes factures
                    </a>

                    <p>Merci pour votre confiance !</p>
                </div>
                <div class="footer">
                    <p>ShareYourSales - Plateforme d'affiliation nouvelle génération</p>
                    <p>123 Avenue Mohammed V, Casablanca, Maroc</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def payment_failed_template(invoice_number: str, amount: float, currency: str) -> str:
        """Template pour échec de paiement"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9fafb; }}
                .alert {{ background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Échec du paiement</h1>
                </div>
                <div class="content">
                    <div class="alert">
                        <p><strong>⚠️ Action requise</strong></p>
                        <p>Le paiement de votre abonnement n'a pas pu être traité.</p>
                    </div>

                    <p><strong>Facture:</strong> {invoice_number}</p>
                    <p><strong>Montant:</strong> {amount:.2f} {currency}</p>

                    <p>Raisons possibles:</p>
                    <ul>
                        <li>Fonds insuffisants</li>
                        <li>Carte expirée</li>
                        <li>Informations de paiement incorrectes</li>
                    </ul>

                    <p>Veuillez mettre à jour votre méthode de paiement pour continuer à bénéficier de nos services.</p>

                    <a href="https://shareyoursales.com/my-subscription/payment-methods" class="button">
                        Mettre à jour le paiement
                    </a>
                </div>
                <div class="footer">
                    <p>ShareYourSales</p>
                    <p>En cas de question, contactez-nous à support@shareyoursales.com</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def payment_success_template(invoice_number: str, amount: float, currency: str, next_billing_date: str) -> str:
        """Template pour paiement réussi"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #10b981; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9fafb; }}
                .success {{ background-color: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✓ Paiement réussi</h1>
                </div>
                <div class="content">
                    <div class="success">
                        <p><strong>Merci !</strong></p>
                        <p>Votre paiement a été traité avec succès.</p>
                    </div>

                    <p><strong>Facture:</strong> {invoice_number}</p>
                    <p><strong>Montant payé:</strong> {amount:.2f} {currency}</p>
                    <p><strong>Prochain paiement:</strong> {next_billing_date}</p>

                    <p>Votre facture est disponible dans votre espace client.</p>

                    <a href="https://shareyoursales.com/my-subscription/invoices" class="button">
                        Voir la facture
                    </a>
                </div>
                <div class="footer">
                    <p>ShareYourSales - Merci pour votre confiance !</p>
                </div>
            </div>
        </body>
        </html>
        """

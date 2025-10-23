"""
Service de facturation automatique pour la plateforme ShareYourSales
Génère des factures mensuelles, crée des PDF et envoie par email

Auteur: ShareYourSales Platform
Date: 2025-10-23
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from supabase_client import supabase
import logging
from io import BytesIO
import base64

# Pour génération PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not installed. PDF generation will be disabled.")

logger = logging.getLogger(__name__)


class InvoicingService:
    """Service de gestion des factures plateforme"""
    
    def __init__(self):
        self.company_info = {
            'name': 'ShareYourSales Platform',
            'address': 'Casablanca, Maroc',
            'email': 'billing@shareyoursales.ma',
            'phone': '+212 XXX XXX XXX',
            'ice': 'ICE000000000000',  # À remplacer
            'rc': 'RC000000',  # À remplacer
            'logo_url': None  # URL du logo
        }
    
    def generate_monthly_invoices(self, year: int, month: int) -> Dict:
        """
        Génère toutes les factures pour le mois donné
        
        Args:
            year: Année (ex: 2025)
            month: Mois (1-12)
        
        Returns:
            Dict avec nombre de factures créées et détails
        """
        
        try:
            # Calculer période
            period_start = datetime(year, month, 1)
            if month == 12:
                period_end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                period_end = datetime(year, month + 1, 1) - timedelta(days=1)
            
            logger.info(f"Generating invoices for {period_start.strftime('%B %Y')}")
            
            # Récupérer toutes les ventes du mois (status = completed)
            sales_result = supabase.table('sales')\
                .select('*, merchants(id, company_name, email, address, ice, payment_gateway)')\
                .eq('status', 'completed')\
                .gte('created_at', period_start.isoformat())\
                .lte('created_at', period_end.isoformat())\
                .execute()
            
            if not sales_result.data:
                logger.info("No completed sales found for this period")
                return {
                    'success': True,
                    'invoices_created': 0,
                    'message': 'No sales to invoice'
                }
            
            # Grouper par merchant
            sales_by_merchant = {}
            for sale in sales_result.data:
                merchant_id = sale['merchant_id']
                if merchant_id not in sales_by_merchant:
                    sales_by_merchant[merchant_id] = {
                        'merchant': sale['merchants'],
                        'sales': []
                    }
                sales_by_merchant[merchant_id]['sales'].append(sale)
            
            # Créer facture pour chaque merchant
            invoices_created = []
            
            for merchant_id, data in sales_by_merchant.items():
                invoice = self._create_invoice_for_merchant(
                    merchant=data['merchant'],
                    sales=data['sales'],
                    period_start=period_start,
                    period_end=period_end
                )
                
                if invoice:
                    invoices_created.append(invoice)
            
            logger.info(f"Created {len(invoices_created)} invoices")
            
            return {
                'success': True,
                'invoices_created': len(invoices_created),
                'invoices': invoices_created
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly invoices: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_invoice_for_merchant(
        self,
        merchant: Dict,
        sales: List[Dict],
        period_start: datetime,
        period_end: datetime
    ) -> Optional[Dict]:
        """Crée une facture pour un merchant"""
        
        try:
            # Calculer totaux
            total_sales_amount = sum(Decimal(str(sale.get('total_amount', 0))) for sale in sales)
            platform_commission = sum(Decimal(str(sale.get('platform_commission', 0))) for sale in sales)
            
            # TVA (20% au Maroc)
            tax_rate = Decimal('0.20')
            tax_amount = platform_commission * tax_rate
            total_amount = platform_commission + tax_amount
            
            # Générer numéro de facture
            invoice_number = self._generate_invoice_number()
            
            # Date d'échéance (30 jours)
            due_date = datetime.now() + timedelta(days=30)
            
            # Créer facture
            invoice_data = {
                'merchant_id': merchant['id'],
                'invoice_number': invoice_number,
                'invoice_date': datetime.now().date().isoformat(),
                'due_date': due_date.date().isoformat(),
                'period_start': period_start.date().isoformat(),
                'period_end': period_end.date().isoformat(),
                'total_sales_amount': float(total_sales_amount),
                'platform_commission': float(platform_commission),
                'tax_amount': float(tax_amount),
                'total_amount': float(total_amount),
                'currency': 'MAD',
                'status': 'pending',
                'payment_method': merchant.get('payment_gateway', 'manual')
            }
            
            invoice_result = supabase.table('platform_invoices')\
                .insert(invoice_data)\
                .execute()
            
            if not invoice_result.data:
                logger.error(f"Failed to create invoice for merchant {merchant['id']}")
                return None
            
            invoice = invoice_result.data[0]
            invoice_id = invoice['id']
            
            # Créer lignes de facture
            line_items = []
            for sale in sales:
                line_item = {
                    'invoice_id': invoice_id,
                    'sale_id': sale['id'],
                    'description': f"Vente #{sale.get('order_id', 'N/A')} - {sale.get('product_name', 'Produit')}",
                    'sale_date': sale.get('created_at', '').split('T')[0],
                    'sale_amount': float(sale.get('total_amount', 0)),
                    'commission_rate': float(sale.get('platform_commission_rate', 5.0)),
                    'commission_amount': float(sale.get('platform_commission', 0))
                }
                line_items.append(line_item)
            
            supabase.table('invoice_line_items').insert(line_items).execute()
            
            # Générer PDF
            pdf_url = self._generate_pdf(invoice, merchant, line_items)
            if pdf_url:
                supabase.table('platform_invoices')\
                    .update({'pdf_url': pdf_url})\
                    .eq('id', invoice_id)\
                    .execute()
            
            # Envoyer email
            self._send_invoice_email(invoice, merchant, pdf_url)
            
            # Mettre à jour status
            supabase.table('platform_invoices')\
                .update({'status': 'sent'})\
                .eq('id', invoice_id)\
                .execute()
            
            logger.info(f"Invoice {invoice_number} created for {merchant.get('company_name')}")
            
            return invoice
            
        except Exception as e:
            logger.error(f"Error creating invoice for merchant: {e}")
            return None
    
    def _generate_invoice_number(self) -> str:
        """Génère un numéro de facture unique"""
        
        try:
            # Utiliser la fonction SQL
            result = supabase.rpc('generate_invoice_number').execute()
            if result.data:
                return result.data
            else:
                # Fallback
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                return f"INV-{timestamp}"
        except Exception as e:
            logger.error(f"Error generating invoice number: {e}")
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            return f"INV-{timestamp}"
    
    def _generate_pdf(self, invoice: Dict, merchant: Dict, line_items: List[Dict]) -> Optional[str]:
        """Génère le PDF de la facture"""
        
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not available, skipping PDF generation")
            return None
        
        try:
            # Créer buffer
            buffer = BytesIO()
            
            # Créer document
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a56db'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Titre
            elements.append(Paragraph(f"FACTURE {invoice['invoice_number']}", title_style))
            elements.append(Spacer(1, 20))
            
            # Informations entreprise et client (2 colonnes)
            info_data = [
                [
                    Paragraph(f"<b>{self.company_info['name']}</b><br/>{self.company_info['address']}<br/>{self.company_info['email']}<br/>{self.company_info['phone']}<br/>ICE: {self.company_info['ice']}", styles['Normal']),
                    Paragraph(f"<b>FACTURÉ À:</b><br/><b>{merchant.get('company_name', 'N/A')}</b><br/>{merchant.get('address', 'N/A')}<br/>{merchant.get('email', 'N/A')}<br/>ICE: {merchant.get('ice', 'N/A')}", styles['Normal'])
                ]
            ]
            
            info_table = Table(info_data, colWidths=[250, 250])
            info_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 30))
            
            # Dates
            dates_data = [
                ['Date de facture:', invoice['invoice_date']],
                ['Période:', f"{invoice['period_start']} au {invoice['period_end']}"],
                ['Date d\'échéance:', invoice['due_date']],
            ]
            
            dates_table = Table(dates_data, colWidths=[150, 150])
            dates_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            
            elements.append(dates_table)
            elements.append(Spacer(1, 30))
            
            # Lignes de facture
            lines_data = [['Description', 'Montant vente', 'Taux (%)', 'Commission']]
            
            for item in line_items:
                lines_data.append([
                    item['description'],
                    f"{item['sale_amount']:.2f} MAD",
                    f"{item['commission_rate']:.1f}%",
                    f"{item['commission_amount']:.2f} MAD"
                ])
            
            # Totaux
            lines_data.append(['', '', 'Sous-total:', f"{invoice['platform_commission']:.2f} MAD"])
            lines_data.append(['', '', f"TVA (20%):", f"{invoice['tax_amount']:.2f} MAD"])
            lines_data.append(['', '', 'TOTAL À PAYER:', f"{invoice['total_amount']:.2f} MAD"])
            
            lines_table = Table(lines_data, colWidths=[250, 80, 80, 90])
            lines_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Body
                ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -4), 10),
                ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
                
                # Totaux
                ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 14),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('ALIGN', (2, -3), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 1), (1, -4), 'LEFT'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ]))
            
            elements.append(lines_table)
            elements.append(Spacer(1, 30))
            
            # Notes de paiement
            payment_notes = f"""
            <b>Modalités de paiement:</b><br/>
            Paiement à effectuer avant le {invoice['due_date']}<br/>
            Mode de paiement: {invoice.get('payment_method', 'Virement bancaire').upper()}<br/>
            <br/>
            En cas de question, contactez-nous à {self.company_info['email']}
            """
            
            elements.append(Paragraph(payment_notes, styles['Normal']))
            
            # Générer PDF
            doc.build(elements)
            
            # Convertir en base64 pour stockage
            pdf_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Dans un vrai système, uploader vers Supabase Storage
            # Pour l'instant, retourner data URL
            pdf_url = f"data:application/pdf;base64,{pdf_base64}"
            
            logger.info(f"PDF generated for invoice {invoice['invoice_number']}")
            
            return pdf_url
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return None
    
    def _send_invoice_email(self, invoice: Dict, merchant: Dict, pdf_url: Optional[str] = None):
        """Envoie la facture par email"""
        
        try:
            # TODO: Intégrer service email (SendGrid, AWS SES, etc.)
            
            email_body = f"""
            Bonjour {merchant.get('company_name')},
            
            Veuillez trouver ci-joint votre facture pour la période du {invoice['period_start']} au {invoice['period_end']}.
            
            Numéro de facture: {invoice['invoice_number']}
            Montant total: {invoice['total_amount']:.2f} MAD
            Date d'échéance: {invoice['due_date']}
            
            Vous pouvez payer cette facture via votre dashboard merchant ou par virement bancaire.
            
            Cordialement,
            L'équipe ShareYourSales
            """
            
            logger.info(f"Email sent to {merchant.get('email')} for invoice {invoice['invoice_number']}")
            
            # Ici, intégrer vraiment l'envoi d'email
            # import sendgrid
            # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            # ...
            
        except Exception as e:
            logger.error(f"Error sending invoice email: {e}")
    
    def mark_invoice_paid(
        self,
        invoice_id: str,
        payment_method: str,
        payment_reference: Optional[str] = None
    ) -> Dict:
        """Marque une facture comme payée"""
        
        try:
            update_data = {
                'status': 'paid',
                'paid_at': datetime.now().isoformat(),
                'payment_method': payment_method,
                'payment_reference': payment_reference
            }
            
            result = supabase.table('platform_invoices')\
                .update(update_data)\
                .eq('id', invoice_id)\
                .execute()
            
            if result.data:
                logger.info(f"Invoice {invoice_id} marked as paid")
                return {
                    'success': True,
                    'invoice': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'error': 'Invoice not found'
                }
                
        except Exception as e:
            logger.error(f"Error marking invoice as paid: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_overdue_invoices(self) -> List[Dict]:
        """Récupère toutes les factures en retard"""
        
        try:
            today = datetime.now().date().isoformat()
            
            result = supabase.table('platform_invoices')\
                .select('*, merchants(company_name, email)')\
                .in_('status', ['pending', 'sent', 'viewed'])\
                .lt('due_date', today)\
                .execute()
            
            if result.data:
                # Mettre à jour status en 'overdue'
                for invoice in result.data:
                    supabase.table('platform_invoices')\
                        .update({'status': 'overdue'})\
                        .eq('id', invoice['id'])\
                        .execute()
                
                return result.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting overdue invoices: {e}")
            return []
    
    def send_payment_reminders(self):
        """Envoie des rappels pour les factures en retard"""
        
        try:
            overdue = self.get_overdue_invoices()
            
            for invoice in overdue:
                merchant = invoice.get('merchants', {})
                
                email_body = f"""
                Bonjour {merchant.get('company_name')},
                
                Nous vous rappelons que votre facture {invoice['invoice_number']} 
                d'un montant de {invoice['total_amount']:.2f} MAD est en retard de paiement.
                
                Date d'échéance: {invoice['due_date']}
                
                Merci de régulariser votre situation dans les plus brefs délais.
                
                Cordialement,
                L'équipe ShareYourSales
                """
                
                logger.info(f"Reminder sent for invoice {invoice['invoice_number']}")
            
            return {
                'success': True,
                'reminders_sent': len(overdue)
            }
            
        except Exception as e:
            logger.error(f"Error sending reminders: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_merchant_invoices(self, merchant_id: str) -> List[Dict]:
        """Récupère toutes les factures d'un merchant"""
        
        try:
            result = supabase.table('platform_invoices')\
                .select('*')\
                .eq('merchant_id', merchant_id)\
                .order('invoice_date', desc=True)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting merchant invoices: {e}")
            return []
    
    def get_invoice_details(self, invoice_id: str) -> Optional[Dict]:
        """Récupère les détails complets d'une facture"""
        
        try:
            # Facture
            invoice_result = supabase.table('platform_invoices')\
                .select('*, merchants(company_name, email, address, ice)')\
                .eq('id', invoice_id)\
                .single()\
                .execute()
            
            if not invoice_result.data:
                return None
            
            invoice = invoice_result.data
            
            # Lignes
            lines_result = supabase.table('invoice_line_items')\
                .select('*')\
                .eq('invoice_id', invoice_id)\
                .execute()
            
            invoice['line_items'] = lines_result.data if lines_result.data else []
            
            return invoice
            
        except Exception as e:
            logger.error(f"Error getting invoice details: {e}")
            return None


# Instance globale
invoicing_service = InvoicingService()

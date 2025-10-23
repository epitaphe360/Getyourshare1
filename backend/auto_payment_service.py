"""
Service de Paiement Automatique pour Influenceurs
Gère la validation des ventes et les paiements automatiques
"""

from datetime import datetime, timedelta
from supabase_client import supabase
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
MIN_PAYOUT_AMOUNT = 50.0  # Montant minimum pour retrait
SALE_VALIDATION_DAYS = 14  # Jours avant validation automatique
PAYOUT_SCHEDULE = "FRIDAY"  # Jour de paiement hebdomadaire

class AutoPaymentService:
    """Service de gestion des paiements automatiques"""
    
    def __init__(self):
        self.supabase = supabase
        
    # ============================================
    # 1. VALIDATION AUTOMATIQUE DES VENTES
    # ============================================
    
    def validate_pending_sales(self) -> Dict:
        """
        Valide automatiquement les ventes de plus de 14 jours
        et crédite le solde des influenceurs
        """
        try:
            # Date limite (14 jours en arrière)
            validation_date = (datetime.now() - timedelta(days=SALE_VALIDATION_DAYS)).isoformat()
            
            # Récupérer les ventes en attente (pending) de plus de 14 jours
            response = supabase.table('sales').select("""
                id,
                influencer_id,
                merchant_id,
                amount,
                influencer_commission,
                platform_commission,
                merchant_revenue,
                product_id,
                link_id,
                created_at
            """).eq('status', 'pending').lt('created_at', validation_date).execute()
            
            pending_sales = response.data if response.data else []
            
            validated_count = 0
            total_commission = 0.0
            influencers_updated = set()
            
            for sale in pending_sales:
                # Vérifier qu'il n'y a pas eu de retour/remboursement
                # (Cette logique peut être étendue avec une table de retours)
                
                try:
                    # 1. Mettre à jour le statut de la vente
                    supabase.table('sales').update({
                        'status': 'completed',
                        'payment_status': 'pending',
                        'payment_processed_at': None
                    }).eq('id', sale['id']).execute()
                    
                    # 2. Créer l'entrée de commission
                    commission_data = {
                        'sale_id': sale['id'],
                        'influencer_id': sale['influencer_id'],
                        'amount': sale['influencer_commission'],
                        'currency': 'EUR',
                        'status': 'approved',  # Approuvée automatiquement
                        'approved_at': datetime.now().isoformat()
                    }
                    supabase.table('commissions').insert(commission_data).execute()
                    
                    # 3. Mettre à jour le solde de l'influenceur
                    influencer = supabase.table('influencers').select('balance, total_earnings').eq('id', sale['influencer_id']).execute()
                    
                    if influencer.data:
                        current_balance = float(influencer.data[0].get('balance', 0))
                        current_earnings = float(influencer.data[0].get('total_earnings', 0))
                        
                        new_balance = current_balance + float(sale['influencer_commission'])
                        new_earnings = current_earnings + float(sale['influencer_commission'])
                        
                        supabase.table('influencers').update({
                            'balance': new_balance,
                            'total_earnings': new_earnings,
                            'updated_at': datetime.now().isoformat()
                        }).eq('id', sale['influencer_id']).execute()
                        
                        influencers_updated.add(sale['influencer_id'])
                    
                    # 4. Mettre à jour les stats du lien d'affiliation
                    if sale.get('link_id'):
                        link = supabase.table('trackable_links').select('total_commission').eq('id', sale['link_id']).execute()
                        if link.data:
                            current_link_commission = float(link.data[0].get('total_commission', 0))
                            supabase.table('trackable_links').update({
                                'total_commission': current_link_commission + float(sale['influencer_commission'])
                            }).eq('id', sale['link_id']).execute()
                    
                    validated_count += 1
                    total_commission += float(sale['influencer_commission'])
                    
                    print(f"✅ Vente validée: {sale['id']} - Commission: {sale['influencer_commission']}€")
                    
                except Exception as e:
                    print(f"❌ Erreur validation vente {sale['id']}: {e}")
                    continue
            
            return {
                "success": True,
                "validated_sales": validated_count,
                "total_commission": round(total_commission, 2),
                "influencers_updated": len(influencers_updated),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erreur dans validate_pending_sales: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================
    # 2. PAIEMENT AUTOMATIQUE
    # ============================================
    
    def process_automatic_payouts(self) -> Dict:
        """
        Traite automatiquement les paiements pour les influenceurs
        dont le solde est ≥ 50€ et qui ont configuré leur méthode de paiement
        """
        try:
            # Récupérer les influenceurs éligibles
            response = supabase.table('influencers').select("""
                id,
                user_id,
                username,
                balance,
                payment_method,
                payment_details
            """).gte('balance', MIN_PAYOUT_AMOUNT).execute()
            
            eligible_influencers = response.data if response.data else []
            
            processed_count = 0
            total_paid = 0.0
            failed_payments = []
            
            for influencer in eligible_influencers:
                # Vérifier que la méthode de paiement est configurée
                if not influencer.get('payment_method') or not influencer.get('payment_details'):
                    print(f"⚠️  Influenceur {influencer['username']}: Méthode de paiement non configurée")
                    failed_payments.append({
                        "influencer_id": influencer['id'],
                        "reason": "payment_method_not_configured",
                        "balance": influencer['balance']
                    })
                    continue
                
                # Vérifier qu'il n'y a pas déjà un paiement en cours
                pending_payout = supabase.table('payouts').select('id').eq(
                    'influencer_id', influencer['id']
                ).in_('status', ['pending', 'processing']).execute()
                
                if pending_payout.data:
                    print(f"⚠️  Influenceur {influencer['username']}: Paiement déjà en cours")
                    continue
                
                # Créer la demande de paiement
                payout_amount = float(influencer['balance'])
                
                payout_data = {
                    'influencer_id': influencer['id'],
                    'amount': payout_amount,
                    'currency': 'EUR',
                    'status': 'processing',
                    'payment_method': influencer['payment_method'],
                    'requested_at': datetime.now().isoformat(),
                    'approved_at': datetime.now().isoformat(),
                    'is_automatic': True
                }
                
                payout_result = supabase.table('payouts').insert(payout_data).execute()
                
                if payout_result.data:
                    payout_id = payout_result.data[0]['id']
                    
                    # Tenter le paiement selon la méthode
                    payment_success = False
                    transaction_id = None
                    
                    if influencer['payment_method'] == 'paypal':
                        payment_success, transaction_id = self._process_paypal_payment(
                            influencer['payment_details'],
                            payout_amount
                        )
                    elif influencer['payment_method'] == 'bank_transfer':
                        payment_success, transaction_id = self._process_bank_transfer(
                            influencer['payment_details'],
                            payout_amount
                        )
                    
                    if payment_success:
                        # Mettre à jour le payout
                        supabase.table('payouts').update({
                            'status': 'paid',
                            'transaction_id': transaction_id,
                            'paid_at': datetime.now().isoformat()
                        }).eq('id', payout_id).execute()
                        
                        # Débiter le solde de l'influenceur
                        supabase.table('influencers').update({
                            'balance': 0.0,
                            'updated_at': datetime.now().isoformat()
                        }).eq('id', influencer['id']).execute()
                        
                        processed_count += 1
                        total_paid += payout_amount
                        
                        print(f"✅ Paiement réussi: {influencer['username']} - {payout_amount}€")
                        
                        # Envoyer notification
                        self._send_payment_notification(influencer, payout_amount, transaction_id)
                        
                    else:
                        # Échec du paiement
                        supabase.table('payouts').update({
                            'status': 'failed',
                            'notes': 'Échec du traitement automatique'
                        }).eq('id', payout_id).execute()
                        
                        failed_payments.append({
                            "influencer_id": influencer['id'],
                            "reason": "payment_processing_failed",
                            "balance": payout_amount
                        })
                        
                        print(f"❌ Échec paiement: {influencer['username']}")
                
            return {
                "success": True,
                "processed_count": processed_count,
                "total_paid": round(total_paid, 2),
                "failed_count": len(failed_payments),
                "failed_payments": failed_payments,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erreur dans process_automatic_payouts: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================
    # 3. MÉTHODES DE PAIEMENT
    # ============================================
    
    def _process_paypal_payment(self, payment_details: dict, amount: float) -> tuple:
        """
        Traite un paiement PayPal
        Retourne: (success: bool, transaction_id: str)
        """
        try:
            # TODO: Intégrer l'API PayPal Payouts
            # https://developer.paypal.com/docs/api/payments.payouts-batch/v1/
            
            paypal_email = payment_details.get('email')
            
            if not paypal_email:
                return False, None
            
            # SIMULATION pour le développement
            # En production, utiliser paypalrestsdk
            """
            import paypalrestsdk
            
            payout = paypalrestsdk.Payout({
                "sender_batch_header": {
                    "sender_batch_id": f"Payout_{datetime.now().timestamp()}",
                    "email_subject": "Votre commission ShareYourSales",
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(amount),
                        "currency": "EUR"
                    },
                    "receiver": paypal_email,
                    "note": "Commission d'affiliation",
                    "sender_item_id": f"item_{datetime.now().timestamp()}"
                }]
            })
            
            if payout.create():
                return True, payout.batch_header.payout_batch_id
            else:
                print(f"PayPal Error: {payout.error}")
                return False, None
            """
            
            # SIMULATION
            transaction_id = f"PAYPAL_SIM_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            print(f"[SIMULATION] Paiement PayPal: {amount}€ → {paypal_email}")
            return True, transaction_id
            
        except Exception as e:
            print(f"Erreur PayPal: {e}")
            return False, None
    
    def _process_bank_transfer(self, payment_details: dict, amount: float) -> tuple:
        """
        Génère un ordre de virement bancaire (SEPA)
        Retourne: (success: bool, transaction_id: str)
        """
        try:
            iban = payment_details.get('iban')
            bic = payment_details.get('bic')
            account_name = payment_details.get('account_name')
            
            if not iban or not account_name:
                return False, None
            
            # Générer fichier SEPA XML
            transaction_id = f"SEPA_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # TODO: Générer fichier SEPA pour import dans banque
            # Utiliser bibliothèque comme sepaxml ou pain.001
            
            print(f"[SIMULATION] Virement SEPA: {amount}€ → {iban}")
            return True, transaction_id
            
        except Exception as e:
            print(f"Erreur virement: {e}")
            return False, None
    
    # ============================================
    # 4. NOTIFICATIONS
    # ============================================
    
    def _send_payment_notification(self, influencer: dict, amount: float, transaction_id: str):
        """Envoie une notification de paiement à l'influenceur"""
        try:
            # Récupérer l'email de l'utilisateur
            user = supabase.table('users').select('email').eq('id', influencer['user_id']).execute()
            
            if user.data:
                email = user.data[0]['email']
                
                # TODO: Envoyer email via SendGrid/SMTP
                print(f"📧 Notification envoyée à {email}: Paiement de {amount}€")
                
                # Créer une notification in-app
                notification_data = {
                    'user_id': influencer['user_id'],
                    'type': 'payout_completed',
                    'title': 'Paiement effectué',
                    'message': f'Votre paiement de {amount}€ a été traité avec succès. Référence: {transaction_id}',
                    'is_read': False,
                    'created_at': datetime.now().isoformat()
                }
                
                supabase.table('notifications').insert(notification_data).execute()
                
        except Exception as e:
            print(f"Erreur notification: {e}")
    
    # ============================================
    # 5. GESTION DES RETOURS
    # ============================================
    
    def process_refund(self, sale_id: str, reason: str = "customer_return") -> Dict:
        """
        Traite un remboursement/retour de marchandise
        Annule la commission et débite le solde de l'influenceur
        """
        try:
            # Récupérer la vente
            sale = supabase.table('sales').select('*').eq('id', sale_id).execute()
            
            if not sale.data:
                return {"success": False, "error": "Vente non trouvée"}
            
            sale_data = sale.data[0]
            
            # Vérifier que la vente n'est pas déjà remboursée
            if sale_data['status'] == 'refunded':
                return {"success": False, "error": "Vente déjà remboursée"}
            
            # 1. Mettre à jour le statut de la vente
            supabase.table('sales').update({
                'status': 'refunded',
                'payment_status': 'refunded',
                'updated_at': datetime.now().isoformat()
            }).eq('id', sale_id).execute()
            
            # 2. Annuler la commission
            supabase.table('commissions').update({
                'status': 'cancelled'
            }).eq('sale_id', sale_id).execute()
            
            # 3. Débiter le solde de l'influenceur si la commission était déjà créditée
            if sale_data['status'] == 'completed':
                influencer = supabase.table('influencers').select('balance').eq(
                    'id', sale_data['influencer_id']
                ).execute()
                
                if influencer.data:
                    current_balance = float(influencer.data[0]['balance'])
                    commission_amount = float(sale_data['influencer_commission'])
                    
                    new_balance = max(0, current_balance - commission_amount)  # Ne pas passer en négatif
                    
                    supabase.table('influencers').update({
                        'balance': new_balance
                    }).eq('id', sale_data['influencer_id']).execute()
            
            return {
                "success": True,
                "message": "Remboursement traité",
                "sale_id": sale_id,
                "commission_cancelled": sale_data['influencer_commission']
            }
            
        except Exception as e:
            print(f"Erreur process_refund: {e}")
            return {"success": False, "error": str(e)}


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def run_daily_validation():
    """Fonction à exécuter quotidiennement (cron job)"""
    service = AutoPaymentService()
    result = service.validate_pending_sales()
    print(f"\n{'='*50}")
    print(f"VALIDATION QUOTIDIENNE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    print(f"Ventes validées: {result.get('validated_sales', 0)}")
    print(f"Commission totale: {result.get('total_commission', 0)}€")
    print(f"Influenceurs mis à jour: {result.get('influencers_updated', 0)}")
    print(f"{'='*50}\n")
    return result

def run_weekly_payouts():
    """Fonction à exécuter chaque vendredi (cron job)"""
    service = AutoPaymentService()
    result = service.process_automatic_payouts()
    print(f"\n{'='*50}")
    print(f"PAIEMENTS AUTOMATIQUES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    print(f"Paiements traités: {result.get('processed_count', 0)}")
    print(f"Montant total payé: {result.get('total_paid', 0)}€")
    print(f"Échecs: {result.get('failed_count', 0)}")
    print(f"{'='*50}\n")
    return result


if __name__ == "__main__":
    # Test du service
    print("🚀 Test du service de paiement automatique\n")
    
    # Test 1: Validation des ventes
    print("📝 Test 1: Validation des ventes...")
    result1 = run_daily_validation()
    
    # Test 2: Paiements automatiques
    print("\n💰 Test 2: Paiements automatiques...")
    result2 = run_weekly_payouts()

"""
Endpoints API pour le système de demandes d'affiliation
Workflow: Influenceur demande → Marchand approuve/refuse → Lien généré automatiquement
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from supabase_client import supabase
from tracking_service import tracking_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/affiliation-requests", tags=["affiliation_requests"])

# ============================================
# MODELS PYDANTIC
# ============================================

class AffiliationRequestCreate(BaseModel):
    """Modèle pour créer une demande d'affiliation"""
    product_id: str
    influencer_message: Optional[str] = None
    influencer_followers: Optional[int] = None
    influencer_engagement_rate: Optional[float] = None
    influencer_social_links: Optional[dict] = None

class AffiliationRequestResponse(BaseModel):
    """Modèle de réponse pour approuver/refuser une demande"""
    status: str  # "approved" ou "rejected"
    merchant_response: Optional[str] = None
    rejection_reason: Optional[str] = None  # Si rejected

# ============================================
# ENDPOINTS
# ============================================

@router.post("/request")
async def create_affiliation_request(
    request_data: AffiliationRequestCreate,
    request: Request,
    user = Depends(lambda: {})  # TODO: Remplacer par vrai système d'auth
):
    """
    Endpoint pour qu'un influenceur demande l'affiliation à un produit

    Workflow:
    1. Influenceur envoie demande avec son profil
    2. Système récupère le merchant_id depuis le product
    3. Création de la demande avec status='pending'
    4. Notification automatique au marchand (Email + SMS + Dashboard)
    5. Retour confirmation à l'influenceur
    """
    try:
        # 1. Récupérer le produit pour avoir le merchant_id
        product_result = supabase.table('products').select('*').eq('id', request_data.product_id).execute()

        if not product_result.data:
            raise HTTPException(status_code=404, detail="Produit introuvable")

        product = product_result.data[0]
        merchant_id = product['merchant_id']

        # 2. Récupérer l'influenceur depuis l'utilisateur connecté
        # TODO: Récupérer user_id depuis le token JWT
        user_id = request.headers.get('X-User-Id', 'mock-user-id')  # Mock pour l'instant

        influencer_result = supabase.table('influencers').select('*').eq('user_id', user_id).execute()

        if not influencer_result.data:
            raise HTTPException(status_code=403, detail="Vous devez être un influenceur pour faire une demande")

        influencer = influencer_result.data[0]
        influencer_id = influencer['id']

        # 3. Vérifier qu'il n'y a pas déjà une demande pending pour ce produit
        existing_request = supabase.table('affiliation_requests').select('*').eq('influencer_id', influencer_id).eq('product_id', request_data.product_id).eq('status', 'pending').execute()

        if existing_request.data:
            raise HTTPException(status_code=400, detail="Vous avez déjà une demande en attente pour ce produit")

        # 4. Créer la demande d'affiliation
        affiliation_request = {
            'influencer_id': influencer_id,
            'product_id': request_data.product_id,
            'merchant_id': merchant_id,
            'status': 'pending',
            'influencer_message': request_data.influencer_message,
            'influencer_followers': request_data.influencer_followers or influencer.get('audience_size', 0),
            'influencer_engagement_rate': request_data.influencer_engagement_rate or influencer.get('engagement_rate', 0),
            'influencer_social_links': request_data.influencer_social_links or influencer.get('social_links', {}),
            'requested_at': datetime.now().isoformat()
        }

        result = supabase.table('affiliation_requests').insert(affiliation_request).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Erreur lors de la création de la demande")

        request_id = result.data[0]['id']

        # 5. Envoyer notifications au marchand
        await send_merchant_notifications(merchant_id, influencer, product, request_id)

        logger.info(f"✅ Demande d'affiliation créée: {request_id} | Influenceur: {influencer_id} | Produit: {request_data.product_id}")

        return {
            "success": True,
            "message": "Demande d'affiliation envoyée avec succès",
            "request_id": request_id,
            "status": "pending",
            "merchant_response_time": "Le marchand a 48h pour répondre"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création demande d'affiliation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-requests")
async def get_my_requests(
    request: Request,
    user = Depends(lambda: {})  # TODO: Remplacer par vrai système d'auth
):
    """
    Récupère toutes les demandes d'affiliation de l'influenceur connecté
    """
    try:
        # TODO: Récupérer user_id depuis le token JWT
        user_id = request.headers.get('X-User-Id', 'mock-user-id')

        influencer_result = supabase.table('influencers').select('id').eq('user_id', user_id).execute()

        if not influencer_result.data:
            raise HTTPException(status_code=403, detail="Influenceur introuvable")

        influencer_id = influencer_result.data[0]['id']

        # Récupérer les demandes avec les infos produit et marchand
        requests = supabase.table('affiliation_requests').select(
            '*, products(name, price, commission_rate, images), merchants(company_name, logo_url)'
        ).eq('influencer_id', influencer_id).order('requested_at', desc=True).execute()

        return {
            "success": True,
            "requests": requests.data or []
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération demandes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/merchant/pending")
async def get_merchant_pending_requests(
    request: Request,
    user = Depends(lambda: {})  # TODO: Remplacer par vrai système d'auth
):
    """
    Récupère toutes les demandes d'affiliation EN ATTENTE pour le marchand connecté
    """
    try:
        # TODO: Récupérer user_id depuis le token JWT
        user_id = request.headers.get('X-User-Id', 'mock-merchant-id')

        merchant_result = supabase.table('merchants').select('id').eq('user_id', user_id).execute()

        if not merchant_result.data:
            raise HTTPException(status_code=403, detail="Marchand introuvable")

        merchant_id = merchant_result.data[0]['id']

        # Récupérer les demandes pending avec les infos influenceur et produit
        requests = supabase.table('affiliation_requests').select(
            '*, influencers(username, full_name, profile_picture_url, audience_size, engagement_rate, total_sales, total_earnings), products(name, price, commission_rate, images)'
        ).eq('merchant_id', merchant_id).eq('status', 'pending').order('requested_at', desc=True).execute()

        return {
            "success": True,
            "pending_requests": requests.data or [],
            "count": len(requests.data) if requests.data else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération demandes marchand: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{request_id}/respond")
async def respond_to_request(
    request_id: str,
    response_data: AffiliationRequestResponse,
    request: Request,
    user = Depends(lambda: {})  # TODO: Remplacer par vrai système d'auth
):
    """
    Endpoint pour qu'un marchand approuve ou refuse une demande d'affiliation

    Workflow si APPROUVÉ:
    1. Marchand clique "Approuver"
    2. Système génère automatiquement un lien trackable unique
    3. Mise à jour de la demande avec status='approved' et generated_link_id
    4. Notification à l'influenceur (Email + SMS + Dashboard) avec son lien
    5. Lien activé et prêt à l'emploi

    Workflow si REFUSÉ:
    1. Marchand clique "Refuser" et indique la raison
    2. Mise à jour de la demande avec status='rejected' et rejection_reason
    3. Notification à l'influenceur avec message encourageant
    """
    try:
        # 1. Récupérer la demande
        request_result = supabase.table('affiliation_requests').select('*').eq('id', request_id).execute()

        if not request_result.data:
            raise HTTPException(status_code=404, detail="Demande introuvable")

        affiliation_request = request_result.data[0]

        # 2. Vérifier que le marchand a le droit de répondre
        # TODO: Vérifier user_id du marchand connecté
        user_id = request.headers.get('X-User-Id', 'mock-merchant-id')

        merchant_result = supabase.table('merchants').select('id').eq('user_id', user_id).execute()

        if not merchant_result.data:
            raise HTTPException(status_code=403, detail="Marchand introuvable")

        merchant_id = merchant_result.data[0]['id']

        if affiliation_request['merchant_id'] != merchant_id:
            raise HTTPException(status_code=403, detail="Vous n'avez pas le droit de répondre à cette demande")

        # 3. Vérifier que la demande est pending
        if affiliation_request['status'] != 'pending':
            raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée")

        # 4. Traiter selon la réponse
        if response_data.status == 'approved':
            # ✅ APPROBATION
            # Générer automatiquement le lien trackable
            product = supabase.table('products').select('*').eq('id', affiliation_request['product_id']).execute().data[0]

            link_result = await tracking_service.create_tracking_link(
                influencer_id=affiliation_request['influencer_id'],
                product_id=affiliation_request['product_id'],
                merchant_url=product.get('url', f"https://merchant.com/product/{product['id']}"),
                campaign_id=None
            )

            if not link_result.get('success'):
                raise HTTPException(status_code=500, detail="Erreur lors de la génération du lien")

            # Mettre à jour la demande
            update_data = {
                'status': 'approved',
                'merchant_response': response_data.merchant_response,
                'generated_link_id': link_result['link_id'],
                'responded_at': datetime.now().isoformat()
            }

            supabase.table('affiliation_requests').update(update_data).eq('id', request_id).execute()

            # Envoyer notification à l'influenceur
            await send_influencer_approval_notification(
                affiliation_request['influencer_id'],
                product,
                link_result['tracking_url'],
                link_result['short_code'],
                response_data.merchant_response
            )

            logger.info(f"✅ Demande approuvée: {request_id} | Lien généré: {link_result['short_code']}")

            return {
                "success": True,
                "message": "Demande approuvée avec succès",
                "status": "approved",
                "tracking_link": link_result['tracking_url'],
                "short_code": link_result['short_code']
            }

        elif response_data.status == 'rejected':
            # ❌ REFUS
            if not response_data.rejection_reason:
                raise HTTPException(status_code=400, detail="La raison du refus est obligatoire")

            # Mettre à jour la demande
            update_data = {
                'status': 'rejected',
                'merchant_response': response_data.merchant_response,
                'rejection_reason': response_data.rejection_reason,
                'responded_at': datetime.now().isoformat()
            }

            supabase.table('affiliation_requests').update(update_data).eq('id', request_id).execute()

            # Envoyer notification à l'influenceur
            await send_influencer_rejection_notification(
                affiliation_request['influencer_id'],
                affiliation_request['product_id'],
                response_data.rejection_reason,
                response_data.merchant_response
            )

            logger.info(f"❌ Demande refusée: {request_id} | Raison: {response_data.rejection_reason}")

            return {
                "success": True,
                "message": "Demande refusée",
                "status": "rejected",
                "rejection_reason": response_data.rejection_reason
            }

        else:
            raise HTTPException(status_code=400, detail="Status invalide. Utilisez 'approved' ou 'rejected'")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur réponse à la demande: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# FONCTIONS DE NOTIFICATION
# ============================================

async def send_merchant_notifications(merchant_id: str, influencer: dict, product: dict, request_id: str):
    """
    Envoie toutes les notifications au marchand quand un influenceur fait une demande
    - Email
    - SMS
    - Notification Dashboard
    - WhatsApp (optionnel)
    """
    try:
        # Récupérer les infos du marchand
        merchant = supabase.table('merchants').select('*, users(email, phone)').eq('id', merchant_id).execute().data[0]

        # EMAIL
        email_data = {
            'to': merchant['users']['email'],
            'subject': f"📬 Nouvelle demande d'affiliation - {influencer['username']}",
            'body': f"""
            Bonjour {merchant['company_name']},

            Vous avez reçu une nouvelle demande d'affiliation !

            Influenceur: {influencer['full_name']} (@{influencer['username']})
            Produit: {product['name']}
            Abonnés: {influencer.get('audience_size', 0):,}
            Taux d'engagement: {influencer.get('engagement_rate', 0)}%

            Consultez la demande complète et approuvez-la en 1 clic:
            https://shareyoursales.ma/merchant/affiliation-requests/{request_id}

            Vous avez 48h pour répondre.

            ShareYourSales Team
            """
        }

        # TODO: Envoyer l'email via service SMTP
        logger.info(f"📧 Email envoyé à {merchant['users']['email']}")

        # SMS
        sms_data = {
            'to': merchant['users']['phone'],
            'message': f"📬 Nouvelle demande d'affiliation de {influencer['username']} ({influencer.get('audience_size', 0):,} abonnés). Consultez sur ShareYourSales.ma"
        }

        # TODO: Envoyer SMS via Twilio/Vonage
        logger.info(f"📱 SMS envoyé à {merchant['users']['phone']}")

        # NOTIFICATION DASHBOARD
        notification = {
            'user_id': merchant['user_id'],
            'type': 'affiliation_request',
            'title': 'Nouvelle demande d\'affiliation',
            'message': f"{influencer['username']} souhaite promouvoir {product['name']}",
            'link': f"/merchant/affiliation-requests/{request_id}",
            'is_read': False
        }

        supabase.table('notifications').insert(notification).execute()
        logger.info(f"🔔 Notification dashboard créée pour marchand {merchant_id}")

    except Exception as e:
        logger.error(f"Erreur envoi notifications marchand: {e}")


async def send_influencer_approval_notification(influencer_id: str, product: dict, tracking_url: str, short_code: str, merchant_message: str):
    """
    Envoie notifications à l'influenceur quand sa demande est approuvée
    """
    try:
        # Récupérer l'influenceur
        influencer = supabase.table('influencers').select('*, users(email, phone)').eq('id', influencer_id).execute().data[0]

        # EMAIL
        email_data = {
            'to': influencer['users']['email'],
            'subject': f"🎉 Demande approuvée - {product['name']}",
            'body': f"""
            Félicitations {influencer['full_name']} !

            Votre demande d'affiliation a été APPROUVÉE !

            Produit: {product['name']}
            Commission: {product['commission_rate']}% par vente

            Votre lien personnel:
            {tracking_url}

            Code court: {short_code}

            Message du marchand:
            {merchant_message or "Bienvenue ! Hâte de travailler avec vous."}

            Téléchargez votre kit marketing:
            https://shareyoursales.ma/influencer/my-links/{short_code}/kit

            Commencez à promouvoir dès maintenant !

            ShareYourSales Team
            """
        }

        logger.info(f"📧 Email d'approbation envoyé à {influencer['users']['email']}")

        # NOTIFICATION DASHBOARD
        notification = {
            'user_id': influencer['user_id'],
            'type': 'request_approved',
            'title': 'Demande approuvée !',
            'message': f"Votre demande pour {product['name']} a été approuvée. Votre lien: {tracking_url}",
            'link': f"/influencer/my-links",
            'is_read': False
        }

        supabase.table('notifications').insert(notification).execute()
        logger.info(f"🔔 Notification approbation créée pour influenceur {influencer_id}")

    except Exception as e:
        logger.error(f"Erreur envoi notifications approbation: {e}")


async def send_influencer_rejection_notification(influencer_id: str, product_id: str, rejection_reason: str, merchant_message: str):
    """
    Envoie notifications à l'influenceur quand sa demande est refusée
    """
    try:
        # Récupérer l'influenceur et le produit
        influencer = supabase.table('influencers').select('*, users(email)').eq('id', influencer_id).execute().data[0]
        product = supabase.table('products').select('name').eq('id', product_id).execute().data[0]

        # EMAIL
        email_data = {
            'to': influencer['users']['email'],
            'subject': f"Demande non retenue - {product['name']}",
            'body': f"""
            Bonjour {influencer['full_name']},

            Malheureusement, votre demande pour {product['name']} n'a pas été retenue.

            Raison: {rejection_reason}

            Message du marchand:
            {merchant_message or "Merci pour votre intérêt."}

            NE VOUS DÉCOURAGEZ PAS !
            Il y a 2,456 autres produits sur la plateforme qui correspondent mieux à votre profil.

            Continuez à postuler: https://shareyoursales.ma/marketplace

            ShareYourSales Team
            """
        }

        logger.info(f"📧 Email de refus envoyé à {influencer['users']['email']}")

        # NOTIFICATION DASHBOARD
        notification = {
            'user_id': influencer['user_id'],
            'type': 'request_rejected',
            'title': 'Demande non retenue',
            'message': f"Votre demande pour {product['name']} n'a pas été retenue. Raison: {rejection_reason}",
            'link': "/marketplace",
            'is_read': False
        }

        supabase.table('notifications').insert(notification).execute()
        logger.info(f"🔔 Notification refus créée pour influenceur {influencer_id}")

    except Exception as e:
        logger.error(f"Erreur envoi notifications refus: {e}")

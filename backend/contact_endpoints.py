"""
Contact Page Endpoints
Gestion des messages de contact du site web

Endpoints:
- POST /api/contact/submit - Envoyer message contact
- GET /api/contact/my-messages - Mes messages
- GET /api/contact/admin/messages - Tous messages (admin)
- GET /api/contact/admin/messages/{id} - Détail message (admin)
- PATCH /api/contact/admin/messages/{id} - Répondre/Mettre à jour (admin)
- GET /api/contact/admin/stats - Statistiques (admin)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
import structlog

from auth import get_current_user, get_current_admin
from supabase_client import supabase

router = APIRouter(prefix="/api/contact", tags=["Contact"])
logger = structlog.get_logger()


# ============================================
# PYDANTIC MODELS
# ============================================

class SubmitContactRequest(BaseModel):
    """Envoyer un message de contact"""
    name: str = Field(..., min_length=2, max_length=255, description="Nom complet")
    email: EmailStr = Field(..., description="Email")
    phone: Optional[str] = Field(None, max_length=50, description="Téléphone (optionnel)")
    subject: str = Field(..., min_length=5, max_length=500, description="Sujet")
    message: str = Field(..., min_length=10, description="Message")
    category: str = Field(
        default="general",
        pattern="^(general|support|merchant_inquiry|influencer_inquiry|partnership|bug_report|feature_request|complaint)$",
        description="Catégorie du message"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Fatima Zahra",
                "email": "fatima@example.ma",
                "phone": "+212 6 12 34 56 78",
                "subject": "Question sur les commissions",
                "message": "Bonjour, je voudrais savoir comment fonctionnent les commissions pour les influenceurs...",
                "category": "influencer_inquiry"
            }
        }


class UpdateContactMessageRequest(BaseModel):
    """Mettre à jour un message (admin)"""
    status: Optional[str] = Field(None, pattern="^(new|read|in_progress|resolved|closed|spam)$")
    admin_response: Optional[str] = Field(None, min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "resolved",
                "admin_response": "Merci pour votre message. Les commissions sont calculées à 5-15% selon le produit..."
            }
        }


# ============================================
# PUBLIC ENDPOINTS
# ============================================

@router.post("/submit", response_model=dict, status_code=201)
async def submit_contact_message(
    request_data: SubmitContactRequest,
    req: Request
):
    """
    Envoyer un message de contact

    **Public endpoint** - Pas besoin d'authentification

    **Catégories:**
    - general: Question générale
    - support: Support technique
    - merchant_inquiry: Question commerçant
    - influencer_inquiry: Question influenceur
    - partnership: Demande de partenariat
    - bug_report: Signaler un bug
    - feature_request: Demande de fonctionnalité
    - complaint: Réclamation

    **Returns:**
    - Message ID
    - Confirmation
    """
    try:
        # Récupérer IP et user agent
        ip_address = req.client.host if req.client else None
        user_agent = req.headers.get("user-agent")

        # Vérifier si email existe dans users (pour lier automatiquement)
        user_result = supabase.table('users').select('id').eq('email', request_data.email).execute()
        user_id = user_result.data[0]['id'] if user_result.data else None

        # Créer message
        message_data = {
            'user_id': user_id,
            'name': request_data.name,
            'email': request_data.email,
            'phone': request_data.phone,
            'subject': request_data.subject,
            'message': request_data.message,
            'category': request_data.category,
            'status': 'new',
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.utcnow().isoformat()
        }

        result = supabase.table('contact_messages').insert(message_data).execute()

        if not result.data:
            raise Exception("Failed to create contact message")

        message = result.data[0]

        logger.info("contact_message_submitted",
                   email=request_data.email,
                   category=request_data.category,
                   message_id=message['id'])

        # TODO: Envoyer notification email aux admins
        # TODO: Envoyer email de confirmation à l'expéditeur

        return {
            "success": True,
            "message": "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.",
            "message_id": message['id'],
            "reference": f"MSG-{message['id'][:8].upper()}"
        }

    except Exception as e:
        logger.error("contact_submit_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'envoi du message"
        )


@router.get("/my-messages", response_model=dict)
async def get_my_contact_messages(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer mes messages de contact

    **Requis:** Utilisateur connecté

    **Returns:**
    - Liste de mes messages
    - Réponses des admins
    """
    user_id = current_user.get("id")
    user_email = current_user.get("email")

    try:
        offset = (page - 1) * limit

        # Récupérer messages de l'utilisateur
        result = supabase.table('contact_messages').select('*').or_(
            f"user_id.eq.{user_id},email.eq.{user_email}"
        ).order('created_at', desc=True).range(offset, offset + limit - 1).execute()

        messages = result.data or []

        return {
            "success": True,
            "messages": messages,
            "total": len(messages),
            "page": page,
            "limit": limit
        }

    except Exception as e:
        logger.error("get_my_messages_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des messages"
        )


# ============================================
# ADMIN ENDPOINTS
# ============================================

@router.get("/admin/messages", response_model=dict)
async def get_all_contact_messages(
    page: int = 1,
    limit: int = 50,
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Récupérer tous les messages de contact (Admin)

    **Filters:**
    - status: new, read, in_progress, resolved, closed, spam
    - category: general, support, merchant_inquiry, etc.
    - search: Recherche dans nom, email, sujet, message

    **Returns:**
    - Liste complète des messages
    - Informations utilisateur si connecté
    """
    try:
        offset = (page - 1) * limit

        query = supabase.table('contact_messages').select(
            '*',
            count='exact'
        )

        # Filtres
        if status_filter:
            query = query.eq('status', status_filter)

        if category:
            query = query.eq('category', category)

        if search:
            # Note: Supabase ne supporte pas le full-text search facilement
            # On peut faire une recherche basique
            query = query.or_(
                f"name.ilike.%{search}%,email.ilike.%{search}%,subject.ilike.%{search}%,message.ilike.%{search}%"
            )

        query = query.order('created_at', desc=True).range(offset, offset + limit - 1)

        result = query.execute()

        messages = result.data or []
        total_count = result.count or 0

        # Enrichir avec info utilisateur
        for msg in messages:
            if msg.get('user_id'):
                user_result = supabase.table('users').select('id, email, first_name, last_name, role').eq('id', msg['user_id']).execute()
                if user_result.data:
                    msg['user'] = user_result.data[0]

            if msg.get('responded_by'):
                admin_result = supabase.table('users').select('id, email, first_name, last_name').eq('id', msg['responded_by']).execute()
                if admin_result.data:
                    msg['admin'] = admin_result.data[0]

        return {
            "success": True,
            "messages": messages,
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit if total_count else 0
        }

    except Exception as e:
        logger.error("get_all_messages_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des messages"
        )


@router.get("/admin/messages/{message_id}", response_model=dict)
async def get_contact_message_detail(
    message_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Récupérer détail d'un message (Admin)

    **Returns:**
    - Message complet
    - Informations utilisateur
    - Historique de réponses
    """
    try:
        result = supabase.table('contact_messages').select('*').eq('id', message_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message non trouvé"
            )

        message = result.data[0]

        # Enrichir avec info utilisateur
        if message.get('user_id'):
            user_result = supabase.table('users').select('*').eq('id', message['user_id']).execute()
            if user_result.data:
                message['user'] = user_result.data[0]

        # Marquer comme "lu" si nouveau
        if message['status'] == 'new':
            supabase.table('contact_messages').update({
                'status': 'read',
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', message_id).execute()

            message['status'] = 'read'

        logger.info("contact_message_viewed", message_id=message_id, admin_id=current_admin.get('id'))

        return {
            "success": True,
            "message": message
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_message_detail_failed", message_id=message_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du message"
        )


@router.patch("/admin/messages/{message_id}", response_model=dict)
async def update_contact_message(
    message_id: str,
    update_data: UpdateContactMessageRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Mettre à jour un message de contact (Admin)

    **Actions:**
    - Changer le statut
    - Ajouter une réponse
    - Marquer comme spam

    **Status transitions:**
    - new → read → in_progress → resolved → closed
    - any → spam
    """
    admin_id = current_admin.get("id")

    try:
        # Vérifier que le message existe
        msg_result = supabase.table('contact_messages').select('*').eq('id', message_id).execute()

        if not msg_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message non trouvé"
            )

        # Préparer update
        update_dict = {
            'updated_at': datetime.utcnow().isoformat()
        }

        if update_data.status:
            update_dict['status'] = update_data.status

        if update_data.admin_response:
            update_dict['admin_response'] = update_data.admin_response
            update_dict['responded_by'] = admin_id
            update_dict['responded_at'] = datetime.utcnow().isoformat()

            # TODO: Envoyer email avec la réponse au client

        # Update
        result = supabase.table('contact_messages').update(update_dict).eq('id', message_id).execute()

        logger.info("contact_message_updated",
                   message_id=message_id,
                   admin_id=admin_id,
                   status=update_data.status,
                   has_response=bool(update_data.admin_response))

        return {
            "success": True,
            "message": "Message mis à jour avec succès",
            "data": result.data[0] if result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_message_failed", message_id=message_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du message"
        )


@router.get("/admin/stats", response_model=dict)
async def get_contact_stats(current_admin: dict = Depends(get_current_admin)):
    """
    Statistiques des messages de contact (Admin)

    **Returns:**
    - Total messages
    - Par statut (new, read, resolved, etc.)
    - Par période (24h, 7j, 30j)
    - Temps de réponse moyen
    """
    try:
        # Récupérer stats depuis la vue
        stats_result = supabase.table('v_contact_stats').select('*').execute()

        if stats_result.data:
            stats = stats_result.data[0]
        else:
            stats = {
                "total_messages": 0,
                "new_messages": 0,
                "read_messages": 0,
                "in_progress_messages": 0,
                "resolved_messages": 0,
                "spam_messages": 0,
                "last_24h": 0,
                "last_7days": 0,
                "last_30days": 0,
                "avg_response_time_hours": 0
            }

        # Stats par catégorie
        category_stats = {}
        categories = ['general', 'support', 'merchant_inquiry', 'influencer_inquiry', 'partnership', 'bug_report', 'feature_request', 'complaint']

        for cat in categories:
            cat_result = supabase.table('contact_messages').select('*', count='exact').eq('category', cat).execute()
            category_stats[cat] = cat_result.count or 0

        return {
            "success": True,
            "stats": stats,
            "by_category": category_stats
        }

    except Exception as e:
        logger.error("get_contact_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques"
        )

"""
API Endpoints pour le Bot IA Conversationnel

Endpoints:
- POST /api/bot/chat - Envoyer un message au bot
- GET /api/bot/conversations - Historique des conversations
- DELETE /api/bot/conversations/{id} - Supprimer une conversation
- POST /api/bot/feedback - Feedback sur une réponse
- GET /api/bot/suggestions - Suggestions contextuelles
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import structlog

from services.ai_bot_service import (
    AIBotService,
    ConversationContext,
    BotLanguage,
    Message,
    MessageRole,
    create_conversation_context
)
from auth import get_current_user

router = APIRouter(prefix="/api/bot", tags=["AI Bot"])
logger = structlog.get_logger()

# ============================================
# MODÈLES PYDANTIC
# ============================================

class ChatRequest(BaseModel):
    """Requête pour envoyer un message au bot"""
    message: str = Field(..., min_length=1, max_length=2000, description="Message utilisateur")
    language: Optional[str] = Field("fr", description="Langue (fr, en, ar)")
    session_id: Optional[str] = Field(None, description="ID de session pour continuer conversation")


class ChatResponse(BaseModel):
    """Réponse du bot"""
    bot_response: str
    session_id: str
    timestamp: datetime
    intent_detected: Optional[str] = None
    action_executed: Optional[dict] = None
    suggestions: Optional[List[str]] = None


class ConversationHistoryResponse(BaseModel):
    """Historique d'une conversation"""
    session_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    messages: List[dict]


class FeedbackRequest(BaseModel):
    """Feedback sur une réponse du bot"""
    session_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    comment: Optional[str] = Field(None, max_length=500)


class SuggestionResponse(BaseModel):
    """Suggestions contextuelles"""
    suggestions: List[str]
    category: str


# ============================================
# STOCKAGE EN MÉMOIRE (temporaire)
# ============================================

# TODO: Remplacer par base de données
conversations_store = {}


# ============================================
# ENDPOINTS
# ============================================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Converser avec le bot IA

    Le bot peut:
    - Répondre aux questions
    - Exécuter des actions (créer affiliation, stats, etc.)
    - Guider l'utilisateur
    - Proposer des suggestions
    """
    try:
        user_id = current_user["id"]
        user_role = current_user.get("role", "influencer")

        # Récupérer ou créer contexte
        session_id = request.session_id or f"{user_id}_{datetime.utcnow().timestamp()}"

        if session_id in conversations_store:
            context = conversations_store[session_id]
        else:
            context = create_conversation_context(
                user_id=user_id,
                user_role=user_role,
                language=request.language
            )
            context.session_id = session_id
            conversations_store[session_id] = context

        # Créer le service bot
        bot = AIBotService()

        # Envoyer le message
        bot_response, action = await bot.chat(request.message, context)

        # Générer suggestions contextuelles
        suggestions = _generate_suggestions(context, current_user)

        logger.info(
            "bot_chat",
            user_id=user_id,
            session_id=session_id,
            message_length=len(request.message)
        )

        return ChatResponse(
            bot_response=bot_response,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            intent_detected=context.messages[-2].metadata.get("intent") if len(context.messages) >= 2 else None,
            action_executed=action.__dict__ if action else None,
            suggestions=suggestions
        )

    except Exception as e:
        logger.error("bot_chat_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la communication avec le bot"
        )


@router.get("/conversations", response_model=List[ConversationHistoryResponse])
async def get_conversations(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer l'historique des conversations de l'utilisateur
    """
    try:
        user_id = current_user["id"]

        # Filtrer les conversations de l'utilisateur
        user_conversations = [
            conv for session_id, conv in conversations_store.items()
            if conv.user_id == user_id
        ]

        # Trier par date (plus récentes en premier)
        user_conversations.sort(
            key=lambda x: x.messages[-1].timestamp if x.messages else datetime.min,
            reverse=True
        )

        # Limiter
        user_conversations = user_conversations[:limit]

        # Formater réponse
        response = []
        for conv in user_conversations:
            if not conv.messages:
                continue

            response.append(ConversationHistoryResponse(
                session_id=conv.session_id,
                created_at=conv.messages[0].timestamp,
                updated_at=conv.messages[-1].timestamp,
                message_count=len(conv.messages),
                messages=[
                    {
                        "role": msg.role.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in conv.messages
                ]
            ))

        return response

    except Exception as e:
        logger.error("get_conversations_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des conversations"
        )


@router.get("/conversations/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer une conversation spécifique
    """
    try:
        if session_id not in conversations_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation non trouvée"
            )

        conv = conversations_store[session_id]

        # Vérifier que la conversation appartient à l'utilisateur
        if conv.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à cette conversation"
            )

        return ConversationHistoryResponse(
            session_id=conv.session_id,
            created_at=conv.messages[0].timestamp if conv.messages else datetime.utcnow(),
            updated_at=conv.messages[-1].timestamp if conv.messages else datetime.utcnow(),
            message_count=len(conv.messages),
            messages=[
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in conv.messages
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_conversation_error", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de la conversation"
        )


@router.delete("/conversations/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprimer une conversation
    """
    try:
        if session_id not in conversations_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation non trouvée"
            )

        conv = conversations_store[session_id]

        # Vérifier propriété
        if conv.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )

        del conversations_store[session_id]

        logger.info("conversation_deleted", session_id=session_id, user_id=current_user["id"])

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_conversation_error", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression"
        )


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Soumettre un feedback sur une réponse du bot

    Utilisé pour améliorer le bot via fine-tuning
    """
    try:
        # TODO: Sauvegarder feedback en DB pour analyse et fine-tuning

        logger.info(
            "bot_feedback_received",
            user_id=current_user["id"],
            session_id=feedback.session_id,
            rating=feedback.rating
        )

        return {
            "status": "success",
            "message": "Merci pour votre feedback!"
        }

    except Exception as e:
        logger.error("feedback_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la soumission du feedback"
        )


@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir des suggestions contextuelles

    Suggestions basées sur:
    - Rôle utilisateur
    - État du compte
    - Actions récentes
    """
    try:
        suggestions = _generate_suggestions(None, current_user)

        return SuggestionResponse(
            suggestions=suggestions,
            category="general"
        )

    except Exception as e:
        logger.error("suggestions_error", error=str(e), user_id=current_user["id"])
        return SuggestionResponse(suggestions=[], category="general")


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def _generate_suggestions(
    context: Optional[ConversationContext],
    current_user: dict
) -> List[str]:
    """
    Génère des suggestions contextuelles pour l'utilisateur
    """
    role = current_user.get("role", "influencer")

    if role == "influencer":
        return [
            "📊 Voir mes statistiques",
            "🔗 Créer un lien d'affiliation",
            "📱 Connecter mes réseaux sociaux",
            "💰 Vérifier mon solde",
            "📈 Conseils pour augmenter mes ventes"
        ]
    elif role == "merchant":
        return [
            "📦 Ajouter un produit",
            "👥 Voir les demandes d'affiliation",
            "📊 Analyser mes performances",
            "🔍 Rechercher des influenceurs",
            "💳 Gérer mon abonnement"
        ]
    else:
        return [
            "❓ Comment ça marche?",
            "💰 Quels sont les tarifs?",
            "📱 Connecter mes réseaux sociaux",
            "📝 Créer mon compte"
        ]


# ============================================
# WEBHOOK POUR PLATEFORMES EXTERNES
# ============================================

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: dict):
    """
    Webhook pour intégration WhatsApp Business

    Permet de répondre aux messages WhatsApp via le bot
    """
    # TODO: Implémenter intégration WhatsApp Business API
    return {"status": "not_implemented"}


@router.post("/webhook/messenger")
async def messenger_webhook(request: dict):
    """
    Webhook pour intégration Facebook Messenger

    Permet de répondre aux messages Messenger via le bot
    """
    # TODO: Implémenter intégration Messenger
    return {"status": "not_implemented"}


@router.post("/webhook/telegram")
async def telegram_webhook(request: dict):
    """
    Webhook pour intégration Telegram

    Permet de répondre aux messages Telegram via le bot
    """
    # TODO: Implémenter intégration Telegram Bot API
    return {"status": "not_implemented"}

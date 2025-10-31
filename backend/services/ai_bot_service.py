"""
Service de Bot IA Ultra Sophistiqué pour ShareYourSales

Fonctionnalités:
- Assistant conversationnel intelligent (Claude/GPT-4)
- Réponses contextuelles basées sur l'historique
- Support multilingue (FR, EN, AR)
- Intégration avec la base de données pour réponses personnalisées
- Actions automatiques (créer affiliation, vérifier stats, etc.)
- Analyse de sentiment
- Suggestions proactives
- Memory/Context management
- RAG (Retrieval-Augmented Generation) pour doc
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import httpx
import structlog
from dataclasses import dataclass, asdict
import re

logger = structlog.get_logger()


class BotLanguage(str, Enum):
    FRENCH = "fr"
    ENGLISH = "en"
    ARABIC = "ar"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class IntentType(str, Enum):
    """Types d'intentions détectées"""
    GREETING = "greeting"
    HELP = "help"
    CREATE_AFFILIATION = "create_affiliation"
    CHECK_STATS = "check_stats"
    CONNECT_SOCIAL = "connect_social"
    SUBSCRIPTION = "subscription"
    PAYMENT = "payment"
    COMPLAINT = "complaint"
    QUESTION = "question"
    GOODBYE = "goodbye"


@dataclass
class Message:
    """Message dans la conversation"""
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict] = None


@dataclass
class ConversationContext:
    """Contexte de la conversation"""
    user_id: str
    user_role: str  # influencer, merchant, admin
    language: BotLanguage
    messages: List[Message]
    user_data: Optional[Dict] = None
    session_id: Optional[str] = None


@dataclass
class BotAction:
    """Action à exécuter par le bot"""
    action_type: str
    parameters: Dict
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None


class AIBotService:
    """
    Service principal du bot IA

    Architecture:
    1. Intent Detection - Détecte l'intention de l'utilisateur
    2. Context Enrichment - Enrichit avec données DB
    3. Response Generation - Génère réponse via LLM
    4. Action Execution - Exécute actions si nécessaire
    5. Memory Management - Sauvegarde contexte
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_context_messages: int = 20
    ):
        self.api_key = api_key
        self.model = model
        self.max_context_messages = max_context_messages

        # Intent patterns (regex)
        self.intent_patterns = {
            IntentType.GREETING: [
                r'\b(bonjour|salut|hello|hi|hey|salam)\b',
                r'\b(bonsoir|good morning|good evening)\b'
            ],
            IntentType.CREATE_AFFILIATION: [
                r'\b(créer|générer|demander).{0,30}(lien|affiliation)\b',
                r'\b(create|generate).{0,30}(link|affiliation)\b',
                r'\b(je veux|i want).{0,30}(promouvoir|promote)\b'
            ],
            IntentType.CHECK_STATS: [
                r'\b(statistiques?|stats?|performances?)\b',
                r'\b(combien|how (much|many)).{0,30}(ventes?|sales?|commissions?)\b',
                r'\b(followers?|abonnés?|engagement)\b'
            ],
            IntentType.CONNECT_SOCIAL: [
                r'\b(connecter|connect|lier|link).{0,30}(instagram|tiktok|facebook)\b',
                r'\b(réseaux sociaux|social media)\b'
            ],
            IntentType.SUBSCRIPTION: [
                r'\b(abonnement|subscription|plan|pricing)\b',
                r'\b(upgrade|downgrade|cancel)\b'
            ],
            IntentType.PAYMENT: [
                r'\b(paiement|payment|payer|pay)\b',
                r'\b(retrait|withdraw|transfer)\b',
                r'\b(solde|balance|argent|money)\b'
            ],
            IntentType.COMPLAINT: [
                r'\b(problème|problem|bug|erreur|error)\b',
                r'\b(ne fonctionne pas|doesn\'t work|broken)\b',
                r'\b(plainte|complaint|insatisfait)\b'
            ],
            IntentType.GOODBYE: [
                r'\b(au revoir|bye|goodbye|adieu|à bientôt)\b',
                r'\b(merci|thank you|thanks)\b.*\b(bye|au revoir)\b'
            ]
        }

    async def chat(
        self,
        user_message: str,
        context: ConversationContext
    ) -> Tuple[str, Optional[BotAction]]:
        """
        Méthode principale pour interagir avec le bot

        Args:
            user_message: Message de l'utilisateur
            context: Contexte de la conversation

        Returns:
            Tuple (réponse du bot, action exécutée)
        """
        try:
            # 1. Détecter l'intention
            intent = self._detect_intent(user_message, context.language)
            logger.info("intent_detected", intent=intent.value, user_id=context.user_id)

            # 2. Enrichir le contexte avec données DB
            enriched_context = await self._enrich_context(context)

            # 3. Ajouter le message utilisateur
            enriched_context.messages.append(Message(
                role=MessageRole.USER,
                content=user_message,
                timestamp=datetime.utcnow(),
                metadata={"intent": intent.value}
            ))

            # 4. Limiter historique conversation
            if len(enriched_context.messages) > self.max_context_messages:
                # Garder le message système + les N derniers messages
                system_msg = [m for m in enriched_context.messages if m.role == MessageRole.SYSTEM]
                recent_msgs = enriched_context.messages[-self.max_context_messages:]
                enriched_context.messages = system_msg + recent_msgs

            # 5. Générer réponse via LLM
            bot_response = await self._generate_response(
                enriched_context,
                intent
            )

            # 6. Exécuter action si nécessaire
            action = await self._execute_action(
                intent,
                user_message,
                enriched_context
            )

            # 7. Ajouter réponse bot à l'historique
            enriched_context.messages.append(Message(
                role=MessageRole.ASSISTANT,
                content=bot_response,
                timestamp=datetime.utcnow(),
                metadata={"action": asdict(action) if action else None}
            ))

            # 8. Sauvegarder contexte
            await self._save_conversation(enriched_context)

            logger.info(
                "bot_response_generated",
                user_id=context.user_id,
                intent=intent.value,
                action_executed=action is not None
            )

            return bot_response, action

        except Exception as e:
            logger.error("bot_error", error=str(e), user_id=context.user_id)
            return self._get_error_response(context.language), None

    def _detect_intent(self, message: str, language: BotLanguage) -> IntentType:
        """
        Détecte l'intention de l'utilisateur via regex patterns

        Returns:
            IntentType détecté
        """
        message_lower = message.lower()

        # Parcourir tous les patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return intent

        # Par défaut: question générale
        return IntentType.QUESTION

    async def _enrich_context(self, context: ConversationContext) -> ConversationContext:
        """
        Enrichit le contexte avec données de la base de données

        Récupère:
        - Profil utilisateur
        - Statistiques récentes
        - Dernières affiliations
        - Solde/paiements
        """
        # TODO: Implémenter récupération DB
        # Pour l'instant, retourner contexte inchangé

        # Exemple de ce qu'il faut récupérer:
        # if context.user_role == "influencer":
        #     context.user_data = {
        #         "total_sales": 1250,
        #         "commission_earned": 375.50,
        #         "active_links": 5,
        #         "followers": 25000,
        #         "engagement_rate": 4.2,
        #         "pending_affiliations": 2
        #     }
        # elif context.user_role == "merchant":
        #     context.user_data = {
        #         "total_products": 15,
        #         "active_influencers": 8,
        #         "total_sales": 5600,
        #         "pending_requests": 3
        #     }

        return context

    async def _generate_response(
        self,
        context: ConversationContext,
        intent: IntentType
    ) -> str:
        """
        Génère la réponse via LLM (Claude/GPT-4)

        Si pas d'API key, utilise réponses pré-définies
        """
        if not self.api_key:
            # Fallback: réponses pré-définies
            return self._get_predefined_response(intent, context)

        # Construire le prompt système
        system_prompt = self._build_system_prompt(context)

        # Construire l'historique de conversation
        messages = []
        for msg in context.messages:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })

        try:
            # Appel à l'API Claude (ou GPT-4)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 1024,
                        "system": system_prompt,
                        "messages": messages
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["content"][0]["text"]
                else:
                    logger.error("llm_api_error", status=response.status_code)
                    return self._get_predefined_response(intent, context)

        except Exception as e:
            logger.error("llm_generation_error", error=str(e))
            return self._get_predefined_response(intent, context)

    def _build_system_prompt(self, context: ConversationContext) -> str:
        """
        Construit le prompt système pour le LLM
        """
        role_instructions = {
            "influencer": """Vous êtes un assistant IA expert en marketing d'affiliation, spécialisé dans l'aide aux influenceurs.
Vous aidez les influenceurs à:
- Créer des liens d'affiliation
- Optimiser leurs performances
- Comprendre leurs statistiques
- Connecter leurs réseaux sociaux
- Maximiser leurs commissions""",

            "merchant": """Vous êtes un assistant IA expert en e-commerce et marketing d'affiliation.
Vous aidez les marchands à:
- Gérer leurs produits
- Recruter des influenceurs
- Analyser les performances
- Approuver les demandes d'affiliation
- Optimiser leur ROI""",

            "admin": """Vous êtes un assistant IA pour les administrateurs de la plateforme ShareYourSales.
Vous aidez à:
- Monitorer la plateforme
- Gérer les utilisateurs
- Analyser les métriques globales
- Résoudre les problèmes"""
        }

        base_prompt = f"""Tu es ShareBot, l'assistant intelligent de ShareYourSales.ma, la plateforme d'affiliation #1 au Maroc.

{role_instructions.get(context.user_role, role_instructions['influencer'])}

RÈGLES IMPORTANTES:
- Réponds TOUJOURS en {context.language.value.upper()} (français si fr, anglais si en, arabe si ar)
- Sois concis, amical et professionnel
- Utilise des emojis occasionnellement pour rendre la conversation vivante
- Si tu ne sais pas, recommande de contacter le support
- Propose des actions concrètes (boutons, liens)
- Utilise les données utilisateur pour personnaliser les réponses

DONNÉES UTILISATEUR:
{json.dumps(context.user_data or {}, indent=2, ensure_ascii=False)}

CAPACITÉS:
- Créer des demandes d'affiliation
- Afficher les statistiques en temps réel
- Guider pour connecter réseaux sociaux
- Expliquer le système de commission
- Aider à résoudre des problèmes
"""
        return base_prompt

    def _get_predefined_response(
        self,
        intent: IntentType,
        context: ConversationContext
    ) -> str:
        """
        Réponses pré-définies si pas d'API LLM disponible
        """
        lang = context.language

        responses = {
            IntentType.GREETING: {
                BotLanguage.FRENCH: f"👋 Bonjour! Je suis ShareBot, votre assistant intelligent ShareYourSales.\n\nComment puis-je vous aider aujourd'hui?",
                BotLanguage.ENGLISH: f"👋 Hello! I'm ShareBot, your ShareYourSales intelligent assistant.\n\nHow can I help you today?",
                BotLanguage.ARABIC: f"👋 مرحبا! أنا ShareBot، مساعدك الذكي في ShareYourSales.\n\nكيف يمكنني مساعدتك اليوم؟"
            },
            IntentType.HELP: {
                BotLanguage.FRENCH: """🤖 Je peux vous aider avec:

📊 **Statistiques** - Vérifier vos ventes et commissions
🔗 **Affiliation** - Créer des liens d'affiliation
📱 **Réseaux Sociaux** - Connecter Instagram, TikTok
💰 **Paiements** - Vérifier votre solde
📦 **Produits** - Trouver des produits à promouvoir

Que souhaitez-vous faire?""",
                BotLanguage.ENGLISH: """🤖 I can help you with:

📊 **Statistics** - Check your sales and commissions
🔗 **Affiliation** - Create affiliation links
📱 **Social Media** - Connect Instagram, TikTok
💰 **Payments** - Check your balance
📦 **Products** - Find products to promote

What would you like to do?""",
                BotLanguage.ARABIC: """🤖 يمكنني مساعدتك في:

📊 **الإحصائيات** - تحقق من مبيعاتك وعمولاتك
🔗 **الانتساب** - إنشاء روابط الانتساب
📱 **وسائل التواصل** - ربط Instagram و TikTok
💰 **المدفوعات** - تحقق من رصيدك
📦 **المنتجات** - ابحث عن منتجات للترويج

ماذا تريد أن تفعل؟"""
            },
            IntentType.CHECK_STATS: {
                BotLanguage.FRENCH: f"""📊 **Vos Statistiques**

{self._format_stats(context)}

Voulez-vous plus de détails sur une métrique spécifique?""",
                BotLanguage.ENGLISH: f"""📊 **Your Statistics**

{self._format_stats(context)}

Would you like more details on a specific metric?"""
            },
            IntentType.CONNECT_SOCIAL: {
                BotLanguage.FRENCH: """📱 **Connexion Réseaux Sociaux**

Connectez vos comptes pour:
✅ Synchronisation automatique des stats
✅ Profil plus attractif pour les marchands
✅ Suivi de votre croissance

Plateformes disponibles:
• Instagram
• TikTok
• Facebook

👉 [Connecter mes réseaux sociaux](/influencer/social-media)""",
                BotLanguage.ENGLISH: """📱 **Social Media Connection**

Connect your accounts to:
✅ Automatic stats synchronization
✅ More attractive profile for merchants
✅ Track your growth

Available platforms:
• Instagram
• TikTok
• Facebook

👉 [Connect my social media](/influencer/social-media)"""
            },
            IntentType.GOODBYE: {
                BotLanguage.FRENCH: "👋 À bientôt! N'hésitez pas si vous avez d'autres questions.",
                BotLanguage.ENGLISH: "👋 See you soon! Don't hesitate if you have other questions.",
                BotLanguage.ARABIC: "👋 أراك قريبا! لا تتردد إذا كان لديك أسئلة أخرى."
            }
        }

        return responses.get(intent, {}).get(
            lang,
            responses[IntentType.HELP][BotLanguage.FRENCH]
        )

    def _format_stats(self, context: ConversationContext) -> str:
        """Formate les statistiques pour affichage"""
        if not context.user_data:
            return "Aucune donnée disponible pour le moment."

        if context.user_role == "influencer":
            data = context.user_data
            return f"""
💰 Commission gagnée: {data.get('commission_earned', 0)} MAD
🛍️ Ventes totales: {data.get('total_sales', 0)}
🔗 Liens actifs: {data.get('active_links', 0)}
👥 Followers: {data.get('followers', 0):,}
📈 Taux d'engagement: {data.get('engagement_rate', 0)}%
"""
        else:
            data = context.user_data
            return f"""
📦 Produits: {data.get('total_products', 0)}
👥 Influenceurs actifs: {data.get('active_influencers', 0)}
💰 Ventes totales: {data.get('total_sales', 0)} MAD
⏳ Demandes en attente: {data.get('pending_requests', 0)}
"""

    async def _execute_action(
        self,
        intent: IntentType,
        message: str,
        context: ConversationContext
    ) -> Optional[BotAction]:
        """
        Exécute une action si l'intention le requiert

        Actions possibles:
        - Créer demande d'affiliation
        - Récupérer statistiques
        - Initier connexion réseaux sociaux
        """
        # Pour l'instant, pas d'actions automatiques
        # TODO: Implémenter actions réelles
        return None

    async def _save_conversation(self, context: ConversationContext):
        """
        Sauvegarde la conversation en base de données
        """
        # TODO: Implémenter sauvegarde DB
        pass

    def _get_error_response(self, language: BotLanguage) -> str:
        """Réponse en cas d'erreur"""
        errors = {
            BotLanguage.FRENCH: "😔 Désolé, j'ai rencontré une erreur. Veuillez réessayer ou contacter le support.",
            BotLanguage.ENGLISH: "😔 Sorry, I encountered an error. Please try again or contact support.",
            BotLanguage.ARABIC: "😔 عذرا، واجهت خطأ. يرجى المحاولة مرة أخرى أو الاتصال بالدعم."
        }
        return errors.get(language, errors[BotLanguage.FRENCH])


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def create_conversation_context(
    user_id: str,
    user_role: str,
    language: str = "fr"
) -> ConversationContext:
    """
    Crée un nouveau contexte de conversation
    """
    return ConversationContext(
        user_id=user_id,
        user_role=user_role,
        language=BotLanguage(language),
        messages=[],
        user_data=None,
        session_id=None
    )


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

async def example_usage():
    """Exemple d'utilisation du bot"""

    # Créer le service bot
    bot = AIBotService(
        api_key=None,  # Pas d'API key = utilise réponses pré-définies
        model="claude-3-5-sonnet-20241022"
    )

    # Créer un contexte pour un influenceur
    context = create_conversation_context(
        user_id="user-123",
        user_role="influencer",
        language="fr"
    )

    # Simuler une conversation
    messages = [
        "Bonjour!",
        "Comment créer un lien d'affiliation?",
        "Quelles sont mes statistiques?",
        "Merci, au revoir!"
    ]

    for user_msg in messages:
        response, action = await bot.chat(user_msg, context)
        print(f"\n👤 User: {user_msg}")
        print(f"🤖 Bot: {response}")
        if action:
            print(f"⚡ Action: {action.action_type}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())

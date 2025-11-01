"""
🤖 Endpoints API - Assistant IA Multilingue
ShareYourSales - Version Premium 2025

Routes pour toutes les fonctionnalités IA:
1. POST /ai/chat - Chatbot multilingue
2. POST /ai/product-description - Génération descriptions produits
3. POST /ai/product-suggestions - Suggestions personnalisées
4. POST /ai/seo-optimize - Optimisation SEO
5. POST /ai/translate - Traduction FR↔AR
6. POST /ai/sentiment-analysis - Analyse sentiment reviews
7. POST /ai/sales-prediction - Prédiction ventes
8. POST /ai/influencer-recommendations - Matching influenceurs
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.services.ai_assistant_multilingual_service import (
    AIAssistantMultilingualService,
    Language,
    SentimentType,
    SEODifficulty,
    ai_assistant_service
)

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


# ============================================
# MODELS PYDANTIC
# ============================================

class ChatRequest(BaseModel):
    """Requête chatbot"""
    message: str = Field(..., description="Message utilisateur")
    language: Language = Field(default=Language.FRENCH, description="Langue")
    context: Optional[Dict] = Field(default=None, description="Contexte utilisateur")
    user_id: Optional[str] = Field(default=None, description="ID utilisateur")


class ProductDescriptionRequest(BaseModel):
    """Requête génération description produit"""
    product_name: str
    category: str
    price: float
    key_features: Optional[List[str]] = None
    language: Language = Language.FRENCH
    tone: str = Field(default="professional", description="professional, casual, enthusiastic")


class ProductSuggestionsRequest(BaseModel):
    """Requête suggestions produits"""
    user_id: str
    user_profile: Dict[str, Any]
    browsing_history: Optional[List[Dict]] = None
    purchase_history: Optional[List[Dict]] = None
    max_suggestions: int = Field(default=10, ge=1, le=50)


class SEOOptimizationRequest(BaseModel):
    """Requête optimisation SEO"""
    content: str
    target_keywords: List[str]
    language: Language = Language.FRENCH
    content_type: str = Field(default="product", description="product, blog, landing_page")


class TranslationRequest(BaseModel):
    """Requête traduction"""
    text: str
    source_language: Language
    target_language: Language
    context: Optional[str] = Field(default=None, description="e-commerce, chat, marketing")


class SentimentAnalysisRequest(BaseModel):
    """Requête analyse sentiment"""
    reviews: List[str]
    language: Language = Language.FRENCH


class SalesPredictionRequest(BaseModel):
    """Requête prédiction ventes"""
    product_id: str
    historical_data: List[Dict]  # {date, sales, price, ...}
    time_period: str = Field(default="next_week", description="next_week, next_month, next_quarter")
    external_factors: Optional[Dict] = None


class InfluencerRecommendationRequest(BaseModel):
    """Requête recommandation influenceurs"""
    product_data: Dict[str, Any]
    budget: float = Field(..., gt=0, description="Budget campagne en MAD")
    target_audience: Dict[str, Any]
    campaign_goals: List[str]  # awareness, sales, engagement
    max_recommendations: int = Field(default=10, ge=1, le=20)


# ============================================
# ENDPOINTS
# ============================================

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    🤖 Chatbot IA Multilingue

    Chatbot conversationnel intelligent en FR/AR/EN avec:
    - Compréhension contextuelle
    - Réponses personnalisées
    - Actions suggérées
    - Support multilingue

    **Exemple:**
    ```json
    {
      "message": "Comment créer un lien d'affiliation?",
      "language": "fr",
      "user_id": "user_123"
    }
    ```
    """
    try:
        response = await ai_assistant_service.chat(
            message=request.message,
            language=request.language,
            context=request.context,
            user_id=request.user_id
        )

        return {
            "success": True,
            "data": response,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chatbot: {str(e)}")


@router.post("/product-description")
async def generate_product_description(request: ProductDescriptionRequest):
    """
    ✍️ Génération Automatique de Descriptions Produits

    Génère des descriptions optimisées SEO en FR/AR/EN:
    - Titre accrocheur
    - Description courte et longue
    - Bullet points des caractéristiques
    - Mots-clés SEO
    - Public cible identifié

    **Parfait pour:**
    - E-commerce
    - Marketplaces
    - Catalogues produits

    **Exemple:**
    ```json
    {
      "product_name": "Écouteurs Bluetooth Pro",
      "category": "électronique",
      "price": 599.99,
      "key_features": ["Réduction de bruit", "30h autonomie"],
      "language": "fr",
      "tone": "enthusiastic"
    }
    ```
    """
    try:
        description = await ai_assistant_service.generate_product_description(
            product_name=request.product_name,
            category=request.category,
            price=request.price,
            key_features=request.key_features,
            language=request.language,
            tone=request.tone
        )

        return {
            "success": True,
            "data": {
                "title": description.title,
                "short_description": description.short_description,
                "full_description": description.full_description,
                "key_features": description.key_features,
                "target_audience": description.target_audience,
                "seo_keywords": description.seo_keywords,
                "confidence_score": description.confidence_score,
                "language": description.language.value
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération description: {str(e)}")


@router.post("/product-suggestions")
async def suggest_products(request: ProductSuggestionsRequest):
    """
    🎯 Suggestions de Produits Personnalisées par IA

    Recommandations intelligentes basées sur:
    - Profil utilisateur (âge, sexe, localisation)
    - Historique de navigation
    - Historique d'achats
    - Tendances actuelles
    - Comportements similaires

    Retourne produits avec scores de pertinence et raisons.

    **Exemple:**
    ```json
    {
      "user_id": "user_123",
      "user_profile": {"age": 25, "gender": "female", "location": "Casablanca"},
      "browsing_history": [{"product_id": "PROD-1", "category": "beauty"}],
      "max_suggestions": 10
    }
    ```
    """
    try:
        suggestions = await ai_assistant_service.suggest_products(
            user_id=request.user_id,
            user_profile=request.user_profile,
            browsing_history=request.browsing_history,
            purchase_history=request.purchase_history,
            max_suggestions=request.max_suggestions
        )

        return {
            "success": True,
            "data": {
                "suggestions": suggestions,
                "count": len(suggestions)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur suggestions: {str(e)}")


@router.post("/seo-optimize")
async def optimize_seo(request: SEOOptimizationRequest):
    """
    🚀 Optimisation SEO Automatique

    Optimise votre contenu pour Google avec:
    - Titre SEO optimisé (50-60 caractères)
    - Meta description parfaite (150-160 caractères)
    - Mots-clés principaux
    - Structure H1/H2
    - Alt texts pour images
    - Schema markup JSON-LD
    - Estimation de ranking Google

    **Spécialisé pour le marché marocain!**

    **Exemple:**
    ```json
    {
      "content": "Votre contenu produit ici...",
      "target_keywords": ["écouteurs bluetooth", "maroc", "sans fil"],
      "language": "fr",
      "content_type": "product"
    }
    ```
    """
    try:
        optimization = await ai_assistant_service.optimize_seo(
            content=request.content,
            target_keywords=request.target_keywords,
            language=request.language,
            content_type=request.content_type
        )

        return {
            "success": True,
            "data": {
                "optimized_title": optimization.optimized_title,
                "meta_description": optimization.meta_description,
                "keywords": optimization.keywords,
                "h1_tag": optimization.h1_tag,
                "h2_tags": optimization.h2_tags,
                "alt_texts": optimization.alt_texts,
                "schema_markup": optimization.schema_markup,
                "difficulty": optimization.difficulty.value,
                "estimated_ranking": optimization.estimated_ranking
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur optimisation SEO: {str(e)}")


@router.post("/translate")
async def translate(request: TranslationRequest):
    """
    🌍 Traduction Instantanée FR ↔ AR ↔ EN

    Traduction spécialisée e-commerce avec:
    - Préservation du contexte commercial
    - Adaptation culturelle marocaine
    - Termes e-commerce appropriés
    - Qualité professionnelle

    **Langues supportées:**
    - 🇫🇷 Français
    - 🇸🇦 Arabe (standard moderne)
    - 🇬🇧 Anglais

    **Exemple:**
    ```json
    {
      "text": "Livraison gratuite partout au Maroc",
      "source_language": "fr",
      "target_language": "ar",
      "context": "e-commerce"
    }
    ```
    """
    try:
        translation = await ai_assistant_service.translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            context=request.context
        )

        return {
            "success": True,
            "data": translation,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur traduction: {str(e)}")


@router.post("/sentiment-analysis")
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """
    😊 Analyse de Sentiment des Avis Clients

    Analyse NLP avancée des reviews avec:
    - Sentiment global (positif/neutre/négatif)
    - Scores de confiance
    - Émotions détectées (joie, colère, surprise...)
    - Phrases clés positives/négatives
    - Résumé actionnable

    **Idéal pour:**
    - Monitoring réputation
    - Amélioration produits
    - Réponses clients automatisées

    **Exemple:**
    ```json
    {
      "reviews": [
        "Excellent produit, très satisfait!",
        "Livraison rapide mais produit moyen",
        "Déçu de la qualité"
      ],
      "language": "fr"
    }
    ```
    """
    try:
        analysis = await ai_assistant_service.analyze_sentiment(
            reviews=request.reviews,
            language=request.language
        )

        return {
            "success": True,
            "data": {
                "overall_sentiment": analysis.overall_sentiment.value,
                "confidence": analysis.confidence,
                "positive_score": analysis.positive_score,
                "neutral_score": analysis.neutral_score,
                "negative_score": analysis.negative_score,
                "key_phrases": analysis.key_phrases,
                "emotions": analysis.emotions,
                "summary": analysis.summary,
                "total_reviews": len(request.reviews)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur analyse sentiment: {str(e)}")


@router.post("/sales-prediction")
async def predict_sales(request: SalesPredictionRequest):
    """
    📈 Prédiction des Ventes avec Machine Learning

    Prédictions intelligentes basées sur:
    - Historique de ventes
    - Tendances de prix
    - Facteurs saisonniers
    - Promotions planifiées
    - Patterns de comportement

    **Retourne:**
    - Prédiction précise
    - Intervalle de confiance
    - Tendance (croissante/stable/décroissante)
    - Facteurs d'influence
    - Recommandations actionnables

    **Exemple:**
    ```json
    {
      "product_id": "PROD-123",
      "historical_data": [
        {"date": "2024-01-01", "sales": 50, "price": 299.99},
        {"date": "2024-01-08", "sales": 65, "price": 289.99}
      ],
      "time_period": "next_month",
      "external_factors": {"seasonality": 1.2, "promotion": 1.0}
    }
    ```
    """
    try:
        prediction = await ai_assistant_service.predict_sales(
            product_id=request.product_id,
            historical_data=request.historical_data,
            time_period=request.time_period,
            external_factors=request.external_factors
        )

        return {
            "success": True,
            "data": {
                "predicted_sales": prediction.predicted_sales,
                "confidence_interval": {
                    "min": prediction.confidence_interval[0],
                    "max": prediction.confidence_interval[1]
                },
                "trend": prediction.trend,
                "factors": prediction.factors,
                "recommendations": prediction.recommendations,
                "time_period": prediction.time_period,
                "product_id": request.product_id
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prédiction ventes: {str(e)}")


@router.post("/influencer-recommendations")
async def recommend_influencers(request: InfluencerRecommendationRequest):
    """
    🎯 Recommandations d'Influenceurs avec IA Matching

    Trouve les MEILLEURS influenceurs pour votre produit:
    - Matching niche produit/influenceur
    - Analyse démographique de l'audience
    - Taux d'engagement réel
    - ROI estimé de la campagne
    - Historique de performances
    - Langue et localisation

    **Critères de matching:**
    - Score de pertinence 0-100
    - Raisons du match détaillées
    - Estimation ROI en %
    - Budget fit

    **Exemple:**
    ```json
    {
      "product_data": {
        "name": "Écouteurs Bluetooth",
        "category": "électronique",
        "price": 599.99
      },
      "budget": 5000.0,
      "target_audience": {
        "age_range": [18, 35],
        "location": "Morocco",
        "interests": ["tech", "music"]
      },
      "campaign_goals": ["awareness", "sales"],
      "max_recommendations": 10
    }
    ```
    """
    try:
        recommendations = await ai_assistant_service.recommend_influencers(
            product_data=request.product_data,
            budget=request.budget,
            target_audience=request.target_audience,
            campaign_goals=request.campaign_goals,
            max_recommendations=request.max_recommendations
        )

        return {
            "success": True,
            "data": {
                "recommendations": [
                    {
                        "influencer_id": rec.influencer_id,
                        "name": rec.name,
                        "match_score": rec.match_score,
                        "reasons": rec.reasons,
                        "niche": rec.niche,
                        "followers": rec.followers,
                        "engagement_rate": rec.engagement_rate,
                        "estimated_roi": rec.estimated_roi,
                        "language": rec.language.value,
                        "location": rec.location
                    }
                    for rec in recommendations
                ],
                "count": len(recommendations),
                "total_budget": request.budget,
                "budget_per_influencer": request.budget / len(recommendations) if recommendations else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recommandation influenceurs: {str(e)}")


# ============================================
# ENDPOINT DE SANTÉ
# ============================================

@router.get("/health")
async def health_check():
    """
    ✅ Santé du service IA

    Vérifie:
    - Service actif
    - Mode (production/demo)
    - Fonctionnalités disponibles
    """
    return {
        "status": "healthy",
        "service": "AI Assistant Multilingual",
        "version": "2025.1.0",
        "demo_mode": ai_assistant_service.demo_mode,
        "features": {
            "chatbot": True,
            "product_description": True,
            "product_suggestions": True,
            "seo_optimization": True,
            "translation": True,
            "sentiment_analysis": True,
            "sales_prediction": True,
            "influencer_recommendations": True
        },
        "supported_languages": ["fr", "ar", "en"],
        "powered_by": "Claude AI & Anthropic",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/stats")
async def get_stats():
    """
    📊 Statistiques d'utilisation IA

    Retourne les métriques d'utilisation (démo pour l'instant)
    """
    # TODO: Implémenter vraies stats depuis DB
    return {
        "success": True,
        "data": {
            "total_requests": 1250,
            "requests_today": 87,
            "popular_features": {
                "chatbot": 450,
                "product_description": 320,
                "seo_optimization": 180,
                "translation": 150,
                "sentiment_analysis": 90,
                "sales_prediction": 40,
                "influencer_recommendations": 20
            },
            "average_response_time_ms": 850,
            "success_rate": 98.5,
            "demo_mode": ai_assistant_service.demo_mode
        },
        "timestamp": datetime.utcnow().isoformat()
    }

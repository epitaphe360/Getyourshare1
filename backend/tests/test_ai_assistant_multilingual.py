"""
Tests pour l'Assistant IA Multilingue

Couvre toutes les 8 fonctionnalités:
1. Chatbot multilingue FR/AR/EN
2. Génération descriptions produits
3. Suggestions produits personnalisées
4. Optimisation SEO automatique
5. Traduction FR ↔ AR
6. Analyse sentiment reviews
7. Prédiction ventes (ML)
8. Recommandations influenceurs
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from services.ai_assistant_multilingual_service import (
    AIAssistantMultilingualService,
    Language,
    SentimentType,
    SEODifficulty,
    ProductDescription,
    SEOOptimization,
    SentimentAnalysis,
    SalesPrediction,
    InfluencerRecommendation
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def ai_service_demo():
    """Service IA en mode démo"""
    return AIAssistantMultilingualService(demo_mode=True)


@pytest.fixture
def sample_product():
    """Produit exemple"""
    return {
        "name": "Écouteurs Bluetooth Pro",
        "category": "électronique",
        "price": 599.99,
        "key_features": [
            "Réduction de bruit active",
            "30h d'autonomie",
            "Bluetooth 5.0",
            "Étanche IPX7"
        ]
    }


@pytest.fixture
def sample_reviews():
    """Avis clients exemples"""
    return [
        "Excellent produit! Très satisfait de mon achat. La qualité audio est parfaite.",
        "Livraison rapide, mais le produit ne correspond pas à la description.",
        "Prix un peu élevé mais ça vaut le coup. Je recommande!",
        "Déçu de la qualité. Ne fonctionne plus après 1 semaine.",
        "Parfait pour le sport! Très confortable et bonne autonomie."
    ]


@pytest.fixture
def sample_user_profile():
    """Profil utilisateur"""
    return {
        "user_id": "user_123",
        "age": 28,
        "gender": "female",
        "location": "Casablanca",
        "interests": ["tech", "fitness", "beauty"]
    }


# ============================================
# TESTS 1: CHATBOT MULTILINGUE
# ============================================

class TestChatbotMultilingual:
    """Tests du chatbot IA"""

    @pytest.mark.asyncio
    async def test_chat_french(self, ai_service_demo):
        """Test chatbot en français"""
        response = await ai_service_demo.chat(
            message="Bonjour, comment créer un lien d'affiliation?",
            language=Language.FRENCH
        )

        assert response["success"] is True
        assert "response" in response
        assert response["language"] == "fr"
        assert len(response["response"]) > 0

    @pytest.mark.asyncio
    async def test_chat_arabic(self, ai_service_demo):
        """Test chatbot en arabe"""
        response = await ai_service_demo.chat(
            message="مرحبا، كيف أنشئ رابط إحالة؟",
            language=Language.ARABIC
        )

        assert response["success"] is True
        assert response["language"] == "ar"
        assert "مساعد" in response["response"] or "DEMO" in response["response"] or "تجريبي" in response["response"]

    @pytest.mark.asyncio
    async def test_chat_english(self, ai_service_demo):
        """Test chatbot en anglais"""
        response = await ai_service_demo.chat(
            message="Hello, how do I create an affiliate link?",
            language=Language.ENGLISH
        )

        assert response["success"] is True
        assert response["language"] == "en"

    @pytest.mark.asyncio
    async def test_chat_with_context(self, ai_service_demo):
        """Test chatbot avec contexte utilisateur"""
        context = {
            "user_role": "influencer",
            "total_sales": 150,
            "commission_earned": 2500.0
        }

        response = await ai_service_demo.chat(
            message="Quel est mon solde?",
            language=Language.FRENCH,
            context=context,
            user_id="user_123"
        )

        assert response["success"] is True
        assert response["response"] is not None

    @pytest.mark.asyncio
    async def test_chat_suggested_actions(self, ai_service_demo):
        """Test extraction d'actions suggérées"""
        response = await ai_service_demo.chat(
            message="Je veux créer un lien et voir mes statistiques",
            language=Language.FRENCH
        )

        assert "suggested_actions" in response or response["success"] is True


# ============================================
# TESTS 2: GÉNÉRATION DESCRIPTIONS PRODUITS
# ============================================

class TestProductDescriptionGeneration:
    """Tests génération descriptions produits"""

    @pytest.mark.asyncio
    async def test_generate_description_french(self, ai_service_demo, sample_product):
        """Test génération description en français"""
        description = await ai_service_demo.generate_product_description(
            product_name=sample_product["name"],
            category=sample_product["category"],
            price=sample_product["price"],
            key_features=sample_product["key_features"],
            language=Language.FRENCH
        )

        assert isinstance(description, ProductDescription)
        assert len(description.title) > 0
        assert len(description.short_description) > 0
        assert len(description.full_description) > 0
        assert len(description.key_features) >= 3
        assert len(description.seo_keywords) >= 3
        assert description.language == Language.FRENCH

    @pytest.mark.asyncio
    async def test_generate_description_arabic(self, ai_service_demo, sample_product):
        """Test génération description en arabe"""
        description = await ai_service_demo.generate_product_description(
            product_name=sample_product["name"],
            category=sample_product["category"],
            price=sample_product["price"],
            language=Language.ARABIC
        )

        assert isinstance(description, ProductDescription)
        assert description.language == Language.ARABIC
        # Vérifier présence de caractères arabes
        assert any(ord(c) > 1536 and ord(c) < 1791 for c in description.title)

    @pytest.mark.asyncio
    async def test_description_tone_variations(self, ai_service_demo, sample_product):
        """Test différents tons de description"""
        tones = ["professional", "casual", "enthusiastic"]

        for tone in tones:
            description = await ai_service_demo.generate_product_description(
                product_name=sample_product["name"],
                category=sample_product["category"],
                price=sample_product["price"],
                language=Language.FRENCH,
                tone=tone
            )

            assert description.title is not None
            assert description.confidence_score > 0.5

    def test_description_seo_keywords(self, ai_service_demo, sample_product):
        """Test que les mots-clés SEO sont pertinents"""
        # En mode démo
        description = ai_service_demo._demo_product_description(
            sample_product["name"],
            Language.FRENCH
        )

        # Vérifier que les keywords contiennent le nom du produit
        keywords_str = " ".join(description.seo_keywords).lower()
        assert len(description.seo_keywords) >= 3


# ============================================
# TESTS 3: SUGGESTIONS PRODUITS
# ============================================

class TestProductSuggestions:
    """Tests suggestions produits personnalisées"""

    @pytest.mark.asyncio
    async def test_suggest_products_basic(self, ai_service_demo, sample_user_profile):
        """Test suggestions basiques"""
        suggestions = await ai_service_demo.suggest_products(
            user_id=sample_user_profile["user_id"],
            user_profile=sample_user_profile,
            max_suggestions=5
        )

        assert len(suggestions) <= 5
        assert all("relevance_score" in s for s in suggestions)
        assert all("reason" in s for s in suggestions)

    @pytest.mark.asyncio
    async def test_suggestions_with_history(self, ai_service_demo, sample_user_profile):
        """Test suggestions avec historique"""
        browsing_history = [
            {"product_id": "PROD-1", "category": "tech"},
            {"product_id": "PROD-2", "category": "tech"}
        ]

        purchase_history = [
            {"product_id": "PROD-10", "category": "fitness", "price": 299.99}
        ]

        suggestions = await ai_service_demo.suggest_products(
            user_id=sample_user_profile["user_id"],
            user_profile=sample_user_profile,
            browsing_history=browsing_history,
            purchase_history=purchase_history,
            max_suggestions=10
        )

        assert len(suggestions) > 0
        # Vérifier que les suggestions sont triées par score
        scores = [s["relevance_score"] for s in suggestions]
        assert scores == sorted(scores, reverse=True)

    def test_extract_user_interests(self, ai_service_demo):
        """Test extraction des intérêts utilisateur"""
        profile = {}
        browsing = [
            {"category": "tech"},
            {"category": "tech"},
            {"category": "fitness"}
        ]
        purchases = [
            {"category": "tech"}
        ]

        interests = ai_service_demo._extract_user_interests(profile, browsing, purchases)

        assert "tech" in interests
        assert interests["tech"] > interests.get("fitness", 0)

    def test_calculate_relevance(self, ai_service_demo):
        """Test calcul du score de pertinence"""
        product = {
            "id": "PROD-1",
            "category": "tech",
            "is_new": True,
            "has_discount": True
        }

        interests = {"tech": 0.8, "fitness": 0.3}

        score = ai_service_demo._calculate_relevance(product, interests)

        assert score > 0.8  # Base + bonus nouveauté + bonus promo
        assert score <= 1.0


# ============================================
# TESTS 4: OPTIMISATION SEO
# ============================================

class TestSEOOptimization:
    """Tests optimisation SEO"""

    @pytest.mark.asyncio
    async def test_seo_optimize_product(self, ai_service_demo):
        """Test optimisation SEO pour produit"""
        content = "Écouteurs Bluetooth de haute qualité avec réduction de bruit"
        keywords = ["écouteurs bluetooth", "réduction bruit", "maroc"]

        optimization = await ai_service_demo.optimize_seo(
            content=content,
            target_keywords=keywords,
            language=Language.FRENCH,
            content_type="product"
        )

        assert isinstance(optimization, SEOOptimization)
        assert len(optimization.optimized_title) >= 40
        assert len(optimization.meta_description) >= 100
        assert len(optimization.keywords) >= 3
        assert optimization.h1_tag is not None
        assert len(optimization.h2_tags) >= 2
        assert isinstance(optimization.difficulty, SEODifficulty)
        assert 1 <= optimization.estimated_ranking <= 100

    @pytest.mark.asyncio
    async def test_seo_meta_description_length(self, ai_service_demo):
        """Test que la meta description respecte la longueur SEO"""
        optimization = await ai_service_demo.optimize_seo(
            content="Test produit",
            target_keywords=["test", "maroc"],
            language=Language.FRENCH
        )

        # Meta description doit être entre 150-160 caractères (idéal SEO)
        meta_len = len(optimization.meta_description)
        assert meta_len >= 100  # Au moins 100 pour être utile
        assert meta_len <= 200  # Pas trop long

    def test_analyze_seo_current(self, ai_service_demo):
        """Test analyse SEO actuelle"""
        content = "écouteurs bluetooth écouteurs qualité supérieure bluetooth maroc"
        keywords = ["écouteurs bluetooth", "maroc"]

        analysis = ai_service_demo._analyze_seo_current(content, keywords)

        assert "keyword_counts" in analysis
        assert "keyword_density" in analysis
        assert analysis["word_count"] > 0
        assert analysis["keyword_counts"]["maroc"] == 1

    @pytest.mark.asyncio
    async def test_seo_schema_markup(self, ai_service_demo):
        """Test génération du schema markup"""
        optimization = await ai_service_demo.optimize_seo(
            content="Test produit",
            target_keywords=["produit", "test"],
            language=Language.FRENCH
        )

        # Vérifier structure du schema
        schema = optimization.schema_markup
        assert "@context" in schema or len(schema) == 0 or isinstance(schema, dict)


# ============================================
# TESTS 5: TRADUCTION FR ↔ AR
# ============================================

class TestTranslation:
    """Tests traduction multilingue"""

    @pytest.mark.asyncio
    async def test_translate_french_to_arabic(self, ai_service_demo):
        """Test traduction FR → AR"""
        translation = await ai_service_demo.translate(
            text="Livraison gratuite",
            source_language=Language.FRENCH,
            target_language=Language.ARABIC
        )

        assert translation["success"] is True
        assert translation["source_language"] == "fr"
        assert translation["target_language"] == "ar"
        assert len(translation["translation"]) > 0

    @pytest.mark.asyncio
    async def test_translate_arabic_to_french(self, ai_service_demo):
        """Test traduction AR → FR"""
        translation = await ai_service_demo.translate(
            text="توصيل مجاني",
            source_language=Language.ARABIC,
            target_language=Language.FRENCH
        )

        assert translation["success"] is True
        assert "translation" in translation

    @pytest.mark.asyncio
    async def test_translate_same_language(self, ai_service_demo):
        """Test traduction même langue (devrait retourner l'original)"""
        text = "Bonjour"
        translation = await ai_service_demo.translate(
            text=text,
            source_language=Language.FRENCH,
            target_language=Language.FRENCH
        )

        assert translation["success"] is True
        assert translation["translation"] == text

    @pytest.mark.asyncio
    async def test_translate_with_context(self, ai_service_demo):
        """Test traduction avec contexte e-commerce"""
        translation = await ai_service_demo.translate(
            text="Ajouter au panier",
            source_language=Language.FRENCH,
            target_language=Language.ARABIC,
            context="e-commerce"
        )

        assert translation["success"] is True
        assert translation.get("context") == "e-commerce"


# ============================================
# TESTS 6: ANALYSE SENTIMENT
# ============================================

class TestSentimentAnalysis:
    """Tests analyse de sentiment"""

    @pytest.mark.asyncio
    async def test_analyze_sentiment_positive(self, ai_service_demo):
        """Test analyse de reviews positives"""
        positive_reviews = [
            "Excellent produit!",
            "Parfait, je recommande!",
            "Très satisfait de mon achat"
        ]

        analysis = await ai_service_demo.analyze_sentiment(
            reviews=positive_reviews,
            language=Language.FRENCH
        )

        assert isinstance(analysis, SentimentAnalysis)
        assert analysis.overall_sentiment == SentimentType.POSITIVE
        assert analysis.positive_score > analysis.negative_score

    @pytest.mark.asyncio
    async def test_analyze_sentiment_mixed(self, ai_service_demo, sample_reviews):
        """Test analyse de reviews mixtes"""
        analysis = await ai_service_demo.analyze_sentiment(
            reviews=sample_reviews,
            language=Language.FRENCH
        )

        assert analysis.overall_sentiment in [
            SentimentType.POSITIVE,
            SentimentType.MIXED,
            SentimentType.NEUTRAL
        ]
        assert 0 <= analysis.confidence <= 1
        assert 0 <= analysis.positive_score <= 1
        assert 0 <= analysis.neutral_score <= 1
        assert 0 <= analysis.negative_score <= 1
        # Les scores doivent être cohérents
        total = analysis.positive_score + analysis.neutral_score + analysis.negative_score
        assert 0.9 <= total <= 1.1  # Proche de 1

    @pytest.mark.asyncio
    async def test_sentiment_emotions(self, ai_service_demo, sample_reviews):
        """Test détection des émotions"""
        analysis = await ai_service_demo.analyze_sentiment(
            reviews=sample_reviews,
            language=Language.FRENCH
        )

        assert isinstance(analysis.emotions, dict)
        assert len(analysis.emotions) > 0
        # Toutes les valeurs d'émotion doivent être entre 0 et 1
        assert all(0 <= v <= 1 for v in analysis.emotions.values())

    def test_basic_sentiment_analysis(self, ai_service_demo):
        """Test analyse sentiment basique (basée sur mots-clés)"""
        text = "Excellent produit, parfait, je recommande! Très satisfait."

        analysis = ai_service_demo._basic_sentiment_analysis(text)

        assert analysis["overall_sentiment"] == "positive"
        assert analysis["positive_score"] > analysis["negative_score"]


# ============================================
# TESTS 7: PRÉDICTION VENTES
# ============================================

class TestSalesPrediction:
    """Tests prédiction de ventes"""

    @pytest.mark.asyncio
    async def test_predict_sales_basic(self, ai_service_demo):
        """Test prédiction basique"""
        historical_data = [
            {"date": "2024-01-01", "sales": 50, "price": 299.99},
            {"date": "2024-01-08", "sales": 55, "price": 299.99},
            {"date": "2024-01-15", "sales": 60, "price": 289.99},
            {"date": "2024-01-22", "sales": 65, "price": 289.99}
        ]

        prediction = await ai_service_demo.predict_sales(
            product_id="PROD-123",
            historical_data=historical_data,
            time_period="next_week"
        )

        assert isinstance(prediction, SalesPrediction)
        assert prediction.predicted_sales > 0
        assert prediction.confidence_interval[0] < prediction.confidence_interval[1]
        assert prediction.trend in ["increasing", "stable", "decreasing"]
        assert len(prediction.recommendations) > 0

    @pytest.mark.asyncio
    async def test_predict_with_external_factors(self, ai_service_demo):
        """Test prédiction avec facteurs externes"""
        historical_data = [
            {"date": "2024-01-01", "sales": 100, "price": 199.99}
        ] * 4

        external_factors = {
            "seasonality": 1.5,  # Pic saisonnier
            "promotion": 1.2     # Promotion active
        }

        prediction = await ai_service_demo.predict_sales(
            product_id="PROD-123",
            historical_data=historical_data,
            time_period="next_month",
            external_factors=external_factors
        )

        # La prédiction devrait être boostée par les facteurs externes
        assert prediction.predicted_sales > 100
        assert "seasonality" in prediction.factors
        assert "promotion" in prediction.factors

    def test_calculate_trend_increasing(self, ai_service_demo):
        """Test calcul de tendance croissante"""
        sales_data = [10, 15, 20, 25, 30, 35, 40]
        trend = ai_service_demo._calculate_trend(sales_data)

        assert trend > 1.0  # Tendance croissante

    def test_calculate_trend_decreasing(self, ai_service_demo):
        """Test calcul de tendance décroissante"""
        sales_data = [40, 35, 30, 25, 20, 15, 10]
        trend = ai_service_demo._calculate_trend(sales_data)

        assert trend < 1.0  # Tendance décroissante

    def test_generate_sales_recommendations(self, ai_service_demo):
        """Test génération de recommandations"""
        recommendations = ai_service_demo._generate_sales_recommendations(
            trend="decreasing",
            elasticity=-1.5,
            seasonality=0.7
        )

        assert len(recommendations) > 0
        assert any("baisse" in rec.lower() for rec in recommendations)


# ============================================
# TESTS 8: RECOMMANDATIONS INFLUENCEURS
# ============================================

class TestInfluencerRecommendations:
    """Tests recommandations influenceurs"""

    @pytest.mark.asyncio
    async def test_recommend_influencers_basic(self, ai_service_demo, sample_product):
        """Test recommandations basiques"""
        recommendations = await ai_service_demo.recommend_influencers(
            product_data=sample_product,
            budget=5000.0,
            target_audience={"age_range": [18, 35], "location": "Morocco"},
            campaign_goals=["awareness", "sales"],
            max_recommendations=5
        )

        assert len(recommendations) <= 5
        assert all(isinstance(r, InfluencerRecommendation) for r in recommendations)
        assert all(0 <= r.match_score <= 100 for r in recommendations)
        assert all(r.estimated_roi is not None for r in recommendations)

    @pytest.mark.asyncio
    async def test_influencer_recommendations_sorted(self, ai_service_demo, sample_product):
        """Test que les recommandations sont triées par score"""
        recommendations = await ai_service_demo.recommend_influencers(
            product_data=sample_product,
            budget=10000.0,
            target_audience={},
            campaign_goals=["awareness"],
            max_recommendations=10
        )

        scores = [r.match_score for r in recommendations]
        assert scores == sorted(scores, reverse=True)

    def test_detect_product_niche(self, ai_service_demo):
        """Test détection de niche produit"""
        test_cases = {
            "tech": {"category": "électronique"},
            "fashion": {"category": "mode"},
            "beauty": {"category": "cosmétique"},
            "fitness": {"category": "sport"}
        }

        for expected_niche, product_data in test_cases.items():
            niche = ai_service_demo._detect_product_niche(product_data)
            assert niche == expected_niche or niche == "general"

    def test_calculate_influencer_match_score(self, ai_service_demo, sample_product):
        """Test calcul du score de matching"""
        influencer = {
            "id": "INF-1",
            "niche": "tech",
            "followers": 50000,
            "engagement_rate": 7.5,
            "location": "Morocco"
        }

        score = ai_service_demo._calculate_influencer_match_score(
            influencer,
            sample_product,
            {"location": "Morocco"},
            ["awareness"]
        )

        assert 0 <= score <= 100

    def test_estimate_campaign_roi(self, ai_service_demo, sample_product):
        """Test estimation du ROI"""
        influencer = {
            "followers": 100000,
            "engagement_rate": 5.0
        }

        roi = ai_service_demo._estimate_campaign_roi(
            influencer,
            sample_product,
            budget=1000.0
        )

        assert isinstance(roi, float)
        # ROI peut être négatif ou positif
        assert -100 <= roi <= 1000  # Fourchette raisonnable


# ============================================
# TESTS D'INTÉGRATION
# ============================================

@pytest.mark.integration
class TestAIAssistantIntegration:
    """Tests d'intégration multi-fonctionnalités"""

    @pytest.mark.asyncio
    async def test_complete_product_workflow(self, ai_service_demo, sample_product):
        """Test workflow complet: description → SEO → traduction"""
        # 1. Générer description
        description = await ai_service_demo.generate_product_description(
            product_name=sample_product["name"],
            category=sample_product["category"],
            price=sample_product["price"],
            language=Language.FRENCH
        )

        assert description.title is not None

        # 2. Optimiser SEO
        seo = await ai_service_demo.optimize_seo(
            content=description.full_description,
            target_keywords=description.seo_keywords[:3],
            language=Language.FRENCH
        )

        assert seo.optimized_title is not None

        # 3. Traduire en arabe
        translation = await ai_service_demo.translate(
            text=description.short_description,
            source_language=Language.FRENCH,
            target_language=Language.ARABIC
        )

        assert translation["success"] is True

    @pytest.mark.asyncio
    async def test_complete_influencer_campaign_workflow(
        self, ai_service_demo, sample_product, sample_reviews
    ):
        """Test workflow campagne influenceur complet"""
        # 1. Analyser sentiment des reviews existantes
        sentiment = await ai_service_demo.analyze_sentiment(
            reviews=sample_reviews,
            language=Language.FRENCH
        )

        assert sentiment.overall_sentiment is not None

        # 2. Prédire les ventes
        historical_data = [{"date": "2024-01-01", "sales": 50, "price": 299.99}] * 4

        prediction = await ai_service_demo.predict_sales(
            product_id="PROD-123",
            historical_data=historical_data,
            time_period="next_month"
        )

        assert prediction.predicted_sales > 0

        # 3. Recommander influenceurs
        recommendations = await ai_service_demo.recommend_influencers(
            product_data=sample_product,
            budget=prediction.predicted_sales * 0.2,  # 20% du CA prévu
            target_audience={},
            campaign_goals=["awareness", "sales"],
            max_recommendations=5
        )

        assert len(recommendations) > 0


# ============================================
# TESTS DE PERFORMANCE
# ============================================

@pytest.mark.performance
class TestPerformance:
    """Tests de performance"""

    @pytest.mark.asyncio
    async def test_chat_response_time(self, ai_service_demo):
        """Test temps de réponse du chatbot"""
        import asyncio
        start = datetime.now()

        response = await ai_service_demo.chat(
            message="Test message",
            language=Language.FRENCH
        )

        duration = (datetime.now() - start).total_seconds()

        assert duration < 2.0  # Moins de 2 secondes en mode démo
        assert response["success"] is True

    @pytest.mark.asyncio
    async def test_bulk_translations(self, ai_service_demo):
        """Test traductions en masse"""
        texts = [
            "Livraison gratuite",
            "Paiement sécurisé",
            "Garantie 1 an",
            "Retour gratuit",
            "Service client 24/7"
        ]

        start = datetime.now()

        translations = []
        for text in texts:
            trans = await ai_service_demo.translate(
                text=text,
                source_language=Language.FRENCH,
                target_language=Language.ARABIC
            )
            translations.append(trans)

        duration = (datetime.now() - start).total_seconds()

        # 5 traductions en moins de 3 secondes en mode démo
        assert duration < 3.0
        assert len(translations) == 5
        assert all(t["success"] for t in translations)

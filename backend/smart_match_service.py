"""
Smart Match AI Service
Algorithme intelligent de matching influenceurs-marques
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import math

# ============================================
# MODELS
# ============================================

class Niche(str, Enum):
    FASHION = "fashion"
    BEAUTY = "beauty"
    TECH = "tech"
    FOOD = "food"
    TRAVEL = "travel"
    FITNESS = "fitness"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    EDUCATION = "education"
    GAMING = "gaming"

class AudienceAge(str, Enum):
    TEEN = "13-17"
    YOUNG_ADULT = "18-24"
    ADULT = "25-34"
    MATURE = "35-44"
    SENIOR = "45+"

class AudienceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    MIXED = "mixed"

class InfluencerProfile(BaseModel):
    user_id: str
    name: str
    niches: List[Niche]
    followers_count: int
    engagement_rate: float  # 0-100
    audience_age: List[AudienceAge]
    audience_gender: AudienceGender
    audience_location: List[str]  # ["MA", "FR", "US"]
    platforms: List[str]  # ["instagram", "tiktok", "youtube"]
    average_views: int
    content_quality_score: float  # 0-100
    reliability_score: float  # 0-100 (basé sur historique)
    preferred_commission: float  # % minimum souhaité
    language: List[str]  # ["fr", "ar", "en"]

class BrandProfile(BaseModel):
    company_id: str
    company_name: str
    product_category: Niche
    target_audience_age: List[AudienceAge]
    target_audience_gender: AudienceGender
    target_locations: List[str]
    budget_per_influencer: float
    commission_percentage: float
    campaign_description: str
    required_followers_min: int
    required_engagement_min: float
    preferred_platforms: List[str]
    language: List[str]

class MatchResult(BaseModel):
    influencer_id: str
    influencer_name: str
    company_id: str
    company_name: str
    compatibility_score: float  # 0-100
    match_reasons: List[str]
    potential_issues: List[str]
    predicted_roi: float  # Retour sur investissement prédit
    predicted_reach: int
    predicted_conversions: int
    recommended_commission: float
    confidence_level: str  # "high", "medium", "low"

# ============================================
# SMART MATCH SERVICE
# ============================================

class SmartMatchService:
    """Service de matching intelligent entre influenceurs et marques"""

    def __init__(self):
        # Poids des différents critères (total = 100)
        self.weights = {
            "niche_match": 25,
            "audience_match": 20,
            "engagement_quality": 15,
            "followers_range": 10,
            "platform_match": 10,
            "location_match": 10,
            "reliability": 5,
            "commission_fit": 5
        }

    async def find_matches_for_brand(
        self,
        brand: BrandProfile,
        influencers: List[InfluencerProfile],
        top_n: int = 10
    ) -> List[MatchResult]:
        """
        Trouve les meilleurs influenceurs pour une marque

        Algorithme:
        1. Score de compatibilité pour chaque influenceur
        2. Tri par score
        3. Prédiction du ROI
        4. Retour des top N
        """

        matches = []

        for influencer in influencers:
            match_result = await self._calculate_match_score(influencer, brand)
            if match_result.compatibility_score >= 50:  # Seuil minimum
                matches.append(match_result)

        # Trier par score décroissant
        matches.sort(key=lambda x: x.compatibility_score, reverse=True)

        return matches[:top_n]

    async def find_matches_for_influencer(
        self,
        influencer: InfluencerProfile,
        brands: List[BrandProfile],
        top_n: int = 10
    ) -> List[MatchResult]:
        """Trouve les meilleures marques pour un influenceur"""

        matches = []

        for brand in brands:
            match_result = await self._calculate_match_score(influencer, brand)
            if match_result.compatibility_score >= 50:
                matches.append(match_result)

        matches.sort(key=lambda x: x.compatibility_score, reverse=True)

        return matches[:top_n]

    async def _calculate_match_score(
        self,
        influencer: InfluencerProfile,
        brand: BrandProfile
    ) -> MatchResult:
        """
        Calcule le score de compatibilité entre un influenceur et une marque

        Score = Σ (critère_score * poids_critère)
        """

        scores = {}
        match_reasons = []
        potential_issues = []

        # 1. NICHE MATCH (25 points max)
        niche_score = self._calculate_niche_match(influencer.niches, brand.product_category)
        scores["niche_match"] = niche_score

        if niche_score >= 80:
            match_reasons.append(f"✅ Niche parfaitement alignée ({brand.product_category})")
        elif niche_score < 50:
            potential_issues.append(f"⚠️ Niche peu compatible")

        # 2. AUDIENCE MATCH (20 points max)
        audience_score = self._calculate_audience_match(
            influencer.audience_age,
            influencer.audience_gender,
            brand.target_audience_age,
            brand.target_audience_gender
        )
        scores["audience_match"] = audience_score

        if audience_score >= 80:
            match_reasons.append("✅ Audience cible identique")
        elif audience_score < 50:
            potential_issues.append("⚠️ Audiences différentes")

        # 3. ENGAGEMENT QUALITY (15 points max)
        engagement_score = self._calculate_engagement_score(
            influencer.engagement_rate,
            influencer.content_quality_score
        )
        scores["engagement_quality"] = engagement_score

        if influencer.engagement_rate >= 5:
            match_reasons.append(f"✅ Excellent engagement ({influencer.engagement_rate:.1f}%)")
        elif influencer.engagement_rate < 2:
            potential_issues.append(f"⚠️ Engagement faible ({influencer.engagement_rate:.1f}%)")

        # 4. FOLLOWERS RANGE (10 points max)
        followers_score = self._calculate_followers_fit(
            influencer.followers_count,
            brand.required_followers_min
        )
        scores["followers_range"] = followers_score

        if followers_score < 50:
            potential_issues.append(f"⚠️ Nombre de followers insuffisant (requis: {brand.required_followers_min:,})")

        # 5. PLATFORM MATCH (10 points max)
        platform_score = self._calculate_platform_match(
            influencer.platforms,
            brand.preferred_platforms
        )
        scores["platform_match"] = platform_score

        # 6. LOCATION MATCH (10 points max)
        location_score = self._calculate_location_match(
            influencer.audience_location,
            brand.target_locations
        )
        scores["location_match"] = location_score

        if location_score >= 80:
            match_reasons.append("✅ Présent dans les zones cibles")

        # 7. RELIABILITY (5 points max)
        reliability_score = influencer.reliability_score
        scores["reliability"] = reliability_score

        if reliability_score >= 90:
            match_reasons.append(f"✅ Influenceur très fiable (score {reliability_score:.0f}/100)")

        # 8. COMMISSION FIT (5 points max)
        commission_score = self._calculate_commission_fit(
            influencer.preferred_commission,
            brand.commission_percentage
        )
        scores["commission_fit"] = commission_score

        if commission_score < 50:
            potential_issues.append(f"⚠️ Attentes de commission élevées ({influencer.preferred_commission}% vs {brand.commission_percentage}% offert)")

        # CALCUL DU SCORE TOTAL
        total_score = sum(
            scores[criterion] * (self.weights[criterion] / 100)
            for criterion in self.weights.keys()
        )

        # PRÉDICTIONS
        predicted_reach = self._predict_reach(influencer)
        predicted_conversions = self._predict_conversions(influencer, total_score)
        predicted_roi = self._predict_roi(brand, predicted_conversions)
        recommended_commission = self._calculate_recommended_commission(
            influencer,
            brand,
            total_score
        )

        # NIVEAU DE CONFIANCE
        confidence_level = "high" if total_score >= 80 else "medium" if total_score >= 65 else "low"

        return MatchResult(
            influencer_id=influencer.user_id,
            influencer_name=influencer.name,
            company_id=brand.company_id,
            company_name=brand.company_name,
            compatibility_score=round(total_score, 2),
            match_reasons=match_reasons,
            potential_issues=potential_issues,
            predicted_roi=round(predicted_roi, 2),
            predicted_reach=predicted_reach,
            predicted_conversions=predicted_conversions,
            recommended_commission=round(recommended_commission, 2),
            confidence_level=confidence_level
        )

    def _calculate_niche_match(self, influencer_niches: List[Niche], brand_niche: Niche) -> float:
        """Score de compatibilité des niches"""

        if brand_niche in influencer_niches:
            return 100.0  # Match parfait

        # Niches compatibles (mapping)
        compatible_niches = {
            Niche.FASHION: [Niche.BEAUTY, Niche.LIFESTYLE],
            Niche.BEAUTY: [Niche.FASHION, Niche.LIFESTYLE],
            Niche.TECH: [Niche.GAMING, Niche.BUSINESS],
            Niche.FOOD: [Niche.TRAVEL, Niche.LIFESTYLE],
            Niche.FITNESS: [Niche.LIFESTYLE],
        }

        compatible = compatible_niches.get(brand_niche, [])

        for niche in influencer_niches:
            if niche in compatible:
                return 70.0  # Compatible

        return 30.0  # Peu compatible

    def _calculate_audience_match(
        self,
        influencer_age: List[AudienceAge],
        influencer_gender: AudienceGender,
        brand_age: List[AudienceAge],
        brand_gender: AudienceGender
    ) -> float:
        """Score de compatibilité d'audience"""

        score = 0

        # Age match (60% du score)
        age_overlap = len(set(influencer_age) & set(brand_age))
        age_score = (age_overlap / max(len(brand_age), 1)) * 60

        # Gender match (40% du score)
        if influencer_gender == brand_gender:
            gender_score = 40
        elif influencer_gender == AudienceGender.MIXED or brand_gender == AudienceGender.MIXED:
            gender_score = 30
        else:
            gender_score = 10

        return age_score + gender_score

    def _calculate_engagement_score(self, engagement_rate: float, quality_score: float) -> float:
        """Score basé sur l'engagement et la qualité"""

        # Engagement rate benchmark
        # <1%: faible, 1-3%: moyen, 3-5%: bon, >5%: excellent
        if engagement_rate >= 5:
            engagement_score = 100
        elif engagement_rate >= 3:
            engagement_score = 75
        elif engagement_rate >= 1:
            engagement_score = 50
        else:
            engagement_score = 25

        # Moyenne avec quality score
        return (engagement_score * 0.6) + (quality_score * 0.4)

    def _calculate_followers_fit(self, followers: int, required_min: int) -> float:
        """Score basé sur le nombre de followers"""

        if followers < required_min:
            # Pénalité proportionnelle
            ratio = followers / required_min
            return ratio * 50  # Max 50 si en dessous du minimum

        # Au-dessus du minimum, score élevé
        if followers >= required_min * 2:
            return 100
        else:
            return 75 + ((followers - required_min) / required_min) * 25

    def _calculate_platform_match(
        self,
        influencer_platforms: List[str],
        brand_platforms: List[str]
    ) -> float:
        """Score de compatibilité des plateformes"""

        overlap = len(set(influencer_platforms) & set(brand_platforms))
        if overlap == 0:
            return 0
        return (overlap / len(brand_platforms)) * 100

    def _calculate_location_match(
        self,
        influencer_locations: List[str],
        brand_locations: List[str]
    ) -> float:
        """Score de compatibilité géographique"""

        overlap = len(set(influencer_locations) & set(brand_locations))
        if overlap == 0:
            return 0
        return (overlap / len(brand_locations)) * 100

    def _calculate_commission_fit(self, preferred: float, offered: float) -> float:
        """Score basé sur l'alignement des commissions"""

        if offered >= preferred:
            return 100  # Parfait

        # Pénalité proportionnelle
        ratio = offered / preferred
        return ratio * 100

    def _predict_reach(self, influencer: InfluencerProfile) -> int:
        """Prédit la portée d'une campagne"""

        # Estimation conservative: 30-50% des followers verront le contenu
        base_reach = influencer.followers_count * 0.4

        # Ajuster selon l'engagement
        engagement_multiplier = 1 + (influencer.engagement_rate / 10)

        predicted_reach = int(base_reach * engagement_multiplier)
        return predicted_reach

    def _predict_conversions(self, influencer: InfluencerProfile, match_score: float) -> int:
        """Prédit le nombre de conversions"""

        reach = self._predict_reach(influencer)

        # Taux de conversion moyen: 1-3% selon la compatibilité
        base_conversion_rate = 0.01  # 1%

        # Bonus selon le match score
        match_bonus = (match_score / 100) * 0.02  # Jusqu'à +2%

        total_conversion_rate = base_conversion_rate + match_bonus

        predicted_conversions = int(reach * total_conversion_rate)
        return max(predicted_conversions, 1)

    def _predict_roi(self, brand: BrandProfile, conversions: int) -> float:
        """Prédit le ROI de la campagne"""

        # Investissement = budget influenceur
        investment = brand.budget_per_influencer

        # Supposons un panier moyen de 500 MAD (à ajuster selon le produit)
        average_order_value = 500

        # Revenu estimé
        revenue = conversions * average_order_value * (brand.commission_percentage / 100)

        # ROI = (Revenu - Investissement) / Investissement * 100
        if investment == 0:
            return 0

        roi = ((revenue - investment) / investment) * 100
        return roi

    def _calculate_recommended_commission(
        self,
        influencer: InfluencerProfile,
        brand: BrandProfile,
        match_score: float
    ) -> float:
        """Calcule la commission recommandée pour maximiser l'acceptation"""

        # Prendre en compte les préférences des deux parties
        base_commission = (influencer.preferred_commission + brand.commission_percentage) / 2

        # Ajuster selon le match score
        if match_score >= 90:
            # Match parfait: la marque peut offrir un peu moins
            recommended = base_commission * 0.95
        elif match_score >= 75:
            recommended = base_commission
        else:
            # Match moyen: offrir un peu plus pour compenser
            recommended = base_commission * 1.05

        return max(recommended, brand.commission_percentage)

# ============================================
# BATCH MATCHING
# ============================================

class BatchMatchingService:
    """Service de matching en masse pour optimiser les campagnes"""

    def __init__(self):
        self.matcher = SmartMatchService()

    async def match_campaign_to_influencers(
        self,
        campaign_id: str,
        brand: BrandProfile,
        all_influencers: List[InfluencerProfile],
        target_influencer_count: int = 10,
        min_score: float = 65.0
    ) -> Dict[str, Any]:
        """
        Matche une campagne avec les meilleurs influenceurs

        Retourne un rapport détaillé avec:
        - Top influenceurs recommandés
        - Statistiques prédictives
        - Budget total estimé
        - ROI global prédit
        """

        # Trouver les matches
        matches = await self.matcher.find_matches_for_brand(
            brand,
            all_influencers,
            top_n=target_influencer_count * 2  # Sur-sélection pour filtrage
        )

        # Filtrer par score minimum
        qualified_matches = [m for m in matches if m.compatibility_score >= min_score]

        # Prendre les top N
        selected_matches = qualified_matches[:target_influencer_count]

        # Calculer les stats globales
        total_predicted_reach = sum(m.predicted_reach for m in selected_matches)
        total_predicted_conversions = sum(m.predicted_conversions for m in selected_matches)
        total_budget = brand.budget_per_influencer * len(selected_matches)
        average_roi = sum(m.predicted_roi for m in selected_matches) / len(selected_matches) if selected_matches else 0

        return {
            "campaign_id": campaign_id,
            "company_name": brand.company_name,
            "selected_influencers_count": len(selected_matches),
            "matches": selected_matches,
            "campaign_predictions": {
                "total_reach": total_predicted_reach,
                "total_conversions": total_predicted_conversions,
                "total_budget": total_budget,
                "average_roi": round(average_roi, 2),
                "cost_per_conversion": round(total_budget / total_predicted_conversions, 2) if total_predicted_conversions > 0 else 0
            },
            "confidence_breakdown": {
                "high_confidence": len([m for m in selected_matches if m.confidence_level == "high"]),
                "medium_confidence": len([m for m in selected_matches if m.confidence_level == "medium"]),
                "low_confidence": len([m for m in selected_matches if m.confidence_level == "low"])
            }
        }

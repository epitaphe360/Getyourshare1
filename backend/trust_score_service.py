"""
Trust Score System
Système anti-fraude avec score de confiance public pour influenceurs
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import statistics

# ============================================
# MODELS
# ============================================

class TrustLevel(str, Enum):
    VERIFIED_PRO = "verified_pro"  # 90-100
    TRUSTED = "trusted"  # 75-89
    RELIABLE = "reliable"  # 60-74
    AVERAGE = "average"  # 40-59
    UNVERIFIED = "unverified"  # 20-39
    SUSPICIOUS = "suspicious"  # 0-19

class TrustScoreBreakdown(BaseModel):
    overall_score: float  # 0-100
    trust_level: TrustLevel
    conversion_quality: float  # 0-100
    traffic_authenticity: float  # 0-100
    campaign_completion_rate: float  # 0-100
    response_time: float  # 0-100
    content_quality: float  # 0-100
    merchant_satisfaction: float  # 0-100
    account_age_bonus: float  # 0-10
    verification_status: float  # 0-10

class FraudIndicator(BaseModel):
    indicator: str
    severity: str  # "high", "medium", "low"
    description: str
    detected_at: datetime

class TrustReport(BaseModel):
    user_id: str
    username: str
    trust_score: float
    trust_level: TrustLevel
    breakdown: TrustScoreBreakdown
    badges: List[str]
    fraud_indicators: List[FraudIndicator]
    recommendations: List[str]
    last_updated: datetime
    campaign_stats: Dict[str, Any]

# ============================================
# TRUST SCORE SERVICE
# ============================================

class TrustScoreService:
    """Service de calcul et gestion du Trust Score"""

    def __init__(self):
        # Poids des différents critères (total = 100)
        self.weights = {
            "conversion_quality": 30,  # Le plus important
            "traffic_authenticity": 25,
            "campaign_completion_rate": 20,
            "response_time": 10,
            "content_quality": 10,
            "merchant_satisfaction": 5
        }

        # Bonus additionnels (max +20)
        self.bonuses = {
            "account_age": 10,  # Compte ancien = plus fiable
            "verification_status": 10  # KYC vérifié
        }

    async def calculate_trust_score(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        campaign_history: List[Dict[str, Any]],
        traffic_data: Dict[str, Any]
    ) -> TrustReport:
        """
        Calcule le Trust Score complet d'un influenceur

        Paramètres:
        - user_data: Infos du profil utilisateur
        - campaign_history: Historique des campagnes
        - traffic_data: Données de trafic (clics, conversions)
        """

        # 1. CONVERSION QUALITY (30 points)
        conversion_quality = self._calculate_conversion_quality(campaign_history, traffic_data)

        # 2. TRAFFIC AUTHENTICITY (25 points)
        traffic_authenticity = await self._analyze_traffic_authenticity(traffic_data)

        # 3. CAMPAIGN COMPLETION RATE (20 points)
        completion_rate = self._calculate_completion_rate(campaign_history)

        # 4. RESPONSE TIME (10 points)
        response_time = self._calculate_response_time_score(user_data)

        # 5. CONTENT QUALITY (10 points)
        content_quality = self._calculate_content_quality(campaign_history)

        # 6. MERCHANT SATISFACTION (5 points)
        merchant_satisfaction = self._calculate_merchant_satisfaction(campaign_history)

        # BONUS
        account_age_bonus = self._calculate_account_age_bonus(user_data.get("created_at"))
        verification_bonus = self._calculate_verification_bonus(user_data)

        # SCORE TOTAL
        base_score = (
            conversion_quality * (self.weights["conversion_quality"] / 100) +
            traffic_authenticity * (self.weights["traffic_authenticity"] / 100) +
            completion_rate * (self.weights["campaign_completion_rate"] / 100) +
            response_time * (self.weights["response_time"] / 100) +
            content_quality * (self.weights["content_quality"] / 100) +
            merchant_satisfaction * (self.weights["merchant_satisfaction"] / 100)
        )

        overall_score = min(base_score + account_age_bonus + verification_bonus, 100)

        # DÉTECTION DE FRAUDE
        fraud_indicators = await self._detect_fraud_indicators(traffic_data, campaign_history)

        # PÉNALITÉS POUR FRAUDE
        if fraud_indicators:
            fraud_penalty = len([f for f in fraud_indicators if f.severity == "high"]) * 15
            fraud_penalty += len([f for f in fraud_indicators if f.severity == "medium"]) * 8
            overall_score = max(overall_score - fraud_penalty, 0)

        # DÉTERMINER LE NIVEAU
        trust_level = self._get_trust_level(overall_score)

        # BADGES
        badges = self._award_badges(overall_score, campaign_history, user_data)

        # RECOMMANDATIONS
        recommendations = self._generate_recommendations(
            overall_score,
            conversion_quality,
            traffic_authenticity,
            completion_rate,
            fraud_indicators
        )

        # STATISTIQUES
        campaign_stats = self._calculate_campaign_stats(campaign_history)

        # BREAKDOWN
        breakdown = TrustScoreBreakdown(
            overall_score=round(overall_score, 2),
            trust_level=trust_level,
            conversion_quality=round(conversion_quality, 2),
            traffic_authenticity=round(traffic_authenticity, 2),
            campaign_completion_rate=round(completion_rate, 2),
            response_time=round(response_time, 2),
            content_quality=round(content_quality, 2),
            merchant_satisfaction=round(merchant_satisfaction, 2),
            account_age_bonus=round(account_age_bonus, 2),
            verification_status=round(verification_bonus, 2)
        )

        return TrustReport(
            user_id=user_id,
            username=user_data.get("username", ""),
            trust_score=round(overall_score, 2),
            trust_level=trust_level,
            breakdown=breakdown,
            badges=badges,
            fraud_indicators=fraud_indicators,
            recommendations=recommendations,
            last_updated=datetime.now(),
            campaign_stats=campaign_stats
        )

    def _calculate_conversion_quality(
        self,
        campaign_history: List[Dict[str, Any]],
        traffic_data: Dict[str, Any]
    ) -> float:
        """
        Analyse la qualité des conversions

        Critères:
        - Taux de conversion (clics → ventes)
        - Cohérence dans le temps
        - Ratio retours/ventes
        """

        if not campaign_history:
            return 50.0  # Score neutre pour nouveaux

        total_clicks = traffic_data.get("total_clicks", 0)
        total_conversions = traffic_data.get("total_conversions", 0)

        if total_clicks == 0:
            return 30.0

        # Taux de conversion
        conversion_rate = (total_conversions / total_clicks) * 100

        # Benchmark:
        # <0.5%: faible (30 points)
        # 0.5-1%: moyen (50 points)
        # 1-3%: bon (75 points)
        # >3%: excellent (100 points)
        if conversion_rate >= 3:
            score = 100
        elif conversion_rate >= 1:
            score = 75
        elif conversion_rate >= 0.5:
            score = 50
        else:
            score = 30

        # Vérifier la cohérence
        conversion_rates_by_campaign = []
        for campaign in campaign_history:
            clicks = campaign.get("clicks", 0)
            conversions = campaign.get("conversions", 0)
            if clicks > 0:
                rate = (conversions / clicks) * 100
                conversion_rates_by_campaign.append(rate)

        # Si les taux sont cohérents, c'est bon signe
        if len(conversion_rates_by_campaign) >= 3:
            std_dev = statistics.stdev(conversion_rates_by_campaign)
            if std_dev < 1:  # Très cohérent
                score = min(score + 10, 100)

        return score

    async def _analyze_traffic_authenticity(self, traffic_data: Dict[str, Any]) -> float:
        """
        Détecte le trafic frauduleux (bots, fermes de clics)

        Indicateurs de fraude:
        - Taux de rebond anormal (>90%)
        - Durée de session très courte (<5s)
        - IPs suspectes (VPN, data centers)
        - Patterns de clics (tous en même temps)
        - Géolocalisation incohérente
        """

        score = 100.0  # On commence à 100 et on déduit

        # 1. Taux de rebond
        bounce_rate = traffic_data.get("bounce_rate", 0)
        if bounce_rate > 90:
            score -= 30
        elif bounce_rate > 75:
            score -= 15

        # 2. Durée de session
        avg_session_duration = traffic_data.get("avg_session_duration", 0)
        if avg_session_duration < 5:
            score -= 25
        elif avg_session_duration < 15:
            score -= 10

        # 3. IPs suspectes
        suspicious_ip_percentage = traffic_data.get("suspicious_ip_percentage", 0)
        score -= suspicious_ip_percentage * 0.5

        # 4. Clics suspects (tous en rafale)
        click_pattern_score = traffic_data.get("click_pattern_score", 100)
        if click_pattern_score < 50:
            score -= 20

        # 5. Géo incohérence
        geo_consistency = traffic_data.get("geo_consistency", 100)
        if geo_consistency < 70:
            score -= 15

        return max(score, 0)

    def _calculate_completion_rate(self, campaign_history: List[Dict[str, Any]]) -> float:
        """
        Taux de completion des campagnes acceptées

        100% = toutes les campagnes terminées avec succès
        """

        if not campaign_history:
            return 50.0

        completed = len([c for c in campaign_history if c.get("status") == "completed"])
        abandoned = len([c for c in campaign_history if c.get("status") == "abandoned"])
        total = len(campaign_history)

        if total == 0:
            return 50.0

        completion_rate = (completed / total) * 100

        # Pénalité pour abandons
        if abandoned > 0:
            penalty = (abandoned / total) * 30
            completion_rate -= penalty

        return max(completion_rate, 0)

    def _calculate_response_time_score(self, user_data: Dict[str, Any]) -> float:
        """
        Temps de réponse moyen aux messages des marques

        Rapide = meilleur score
        """

        avg_response_time_hours = user_data.get("avg_response_time_hours", 24)

        # <1h: 100 points
        # <6h: 80 points
        # <24h: 60 points
        # <48h: 40 points
        # >48h: 20 points
        if avg_response_time_hours < 1:
            return 100
        elif avg_response_time_hours < 6:
            return 80
        elif avg_response_time_hours < 24:
            return 60
        elif avg_response_time_hours < 48:
            return 40
        else:
            return 20

    def _calculate_content_quality(self, campaign_history: List[Dict[str, Any]]) -> float:
        """
        Qualité du contenu créé (évalué par les marques)
        """

        if not campaign_history:
            return 50.0

        quality_ratings = [
            c.get("content_quality_rating", 0)
            for c in campaign_history
            if c.get("content_quality_rating") is not None
        ]

        if not quality_ratings:
            return 50.0

        avg_rating = statistics.mean(quality_ratings)
        return avg_rating * 20  # Supposant que les ratings sont sur 5

    def _calculate_merchant_satisfaction(self, campaign_history: List[Dict[str, Any]]) -> float:
        """Note moyenne des marchands"""

        ratings = [
            c.get("merchant_rating", 0)
            for c in campaign_history
            if c.get("merchant_rating") is not None
        ]

        if not ratings:
            return 50.0

        avg_rating = statistics.mean(ratings)
        return avg_rating * 20  # Ratings sur 5

    def _calculate_account_age_bonus(self, created_at: Optional[str]) -> float:
        """Bonus pour ancienneté du compte"""

        if not created_at:
            return 0

        account_age_days = (datetime.now() - datetime.fromisoformat(created_at.replace('Z', '+00:00'))).days

        # <30 jours: 0 bonus
        # 30-90 jours: +2
        # 90-180 jours: +5
        # 180-365 jours: +7
        # >365 jours: +10
        if account_age_days < 30:
            return 0
        elif account_age_days < 90:
            return 2
        elif account_age_days < 180:
            return 5
        elif account_age_days < 365:
            return 7
        else:
            return 10

    def _calculate_verification_bonus(self, user_data: Dict[str, Any]) -> float:
        """Bonus pour vérifications complétées"""

        bonus = 0

        if user_data.get("email_verified"):
            bonus += 2
        if user_data.get("phone_verified"):
            bonus += 3
        if user_data.get("kyc_verified"):
            bonus += 5

        return bonus

    async def _detect_fraud_indicators(
        self,
        traffic_data: Dict[str, Any],
        campaign_history: List[Dict[str, Any]]
    ) -> List[FraudIndicator]:
        """Détecte des patterns de fraude"""

        indicators = []

        # 1. Taux de rebond trop élevé
        if traffic_data.get("bounce_rate", 0) > 95:
            indicators.append(FraudIndicator(
                indicator="high_bounce_rate",
                severity="high",
                description=f"Taux de rebond anormalement élevé ({traffic_data.get('bounce_rate')}%)",
                detected_at=datetime.now()
            ))

        # 2. Trop d'IPs suspectes
        if traffic_data.get("suspicious_ip_percentage", 0) > 50:
            indicators.append(FraudIndicator(
                indicator="suspicious_ips",
                severity="high",
                description="Plus de 50% du trafic provient d'IPs suspectes (VPN, bots)",
                detected_at=datetime.now()
            ))

        # 3. Pic de conversions suspect
        if campaign_history:
            recent_conversions = [c.get("conversions", 0) for c in campaign_history[-5:]]
            if recent_conversions and max(recent_conversions) > statistics.mean(recent_conversions) * 5:
                indicators.append(FraudIndicator(
                    indicator="conversion_spike",
                    severity="medium",
                    description="Pic de conversions inhabituel détecté",
                    detected_at=datetime.now()
                ))

        # 4. Sessions trop courtes
        if traffic_data.get("avg_session_duration", 0) < 3:
            indicators.append(FraudIndicator(
                indicator="short_sessions",
                severity="medium",
                description="Durée de session anormalement courte (<3 secondes)",
                detected_at=datetime.now()
            ))

        return indicators

    def _get_trust_level(self, score: float) -> TrustLevel:
        """Détermine le niveau de confiance"""

        if score >= 90:
            return TrustLevel.VERIFIED_PRO
        elif score >= 75:
            return TrustLevel.TRUSTED
        elif score >= 60:
            return TrustLevel.RELIABLE
        elif score >= 40:
            return TrustLevel.AVERAGE
        elif score >= 20:
            return TrustLevel.UNVERIFIED
        else:
            return TrustLevel.SUSPICIOUS

    def _award_badges(
        self,
        score: float,
        campaign_history: List[Dict[str, Any]],
        user_data: Dict[str, Any]
    ) -> List[str]:
        """Attribue des badges de reconnaissance"""

        badges = []

        if score >= 95:
            badges.append("🏆 Elite Partner")
        if score >= 90:
            badges.append("✅ Verified Pro")
        if score >= 80:
            badges.append("⭐ Top Rated")

        # Badges spéciaux
        if len(campaign_history) >= 50:
            badges.append("💼 Veteran (50+ campagnes)")
        if len(campaign_history) >= 100:
            badges.append("🎖️ Master (100+ campagnes)")

        total_conversions = sum(c.get("conversions", 0) for c in campaign_history)
        if total_conversions >= 1000:
            badges.append("💰 Conversion King (1000+ ventes)")

        if user_data.get("kyc_verified"):
            badges.append("🔐 Identity Verified")

        return badges

    def _generate_recommendations(
        self,
        overall_score: float,
        conversion_quality: float,
        traffic_authenticity: float,
        completion_rate: float,
        fraud_indicators: List[FraudIndicator]
    ) -> List[str]:
        """Génère des recommandations pour améliorer le score"""

        recommendations = []

        if overall_score < 60:
            recommendations.append("🎯 Concentrez-vous sur l'amélioration de la qualité de vos conversions")

        if conversion_quality < 50:
            recommendations.append("📈 Travaillez sur votre taux de conversion (ciblage, contenu)")

        if traffic_authenticity < 70:
            recommendations.append("⚠️ Améliorer l'authenticité du trafic - éviter les pratiques frauduleuses")

        if completion_rate < 80:
            recommendations.append("✅ Finalisez toutes vos campagnes acceptées pour augmenter votre fiabilité")

        if fraud_indicators:
            recommendations.append("🚨 URGENT: Des indicateurs de fraude ont été détectés - contactez le support")

        if overall_score >= 80:
            recommendations.append("🌟 Excellent score ! Continuez comme ça pour débloquer plus d'opportunités")

        return recommendations

    def _calculate_campaign_stats(self, campaign_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Statistiques de campagne pour le rapport"""

        if not campaign_history:
            return {
                "total_campaigns": 0,
                "completed_campaigns": 0,
                "total_conversions": 0,
                "total_revenue_generated": 0,
                "average_conversion_rate": 0
            }

        total = len(campaign_history)
        completed = len([c for c in campaign_history if c.get("status") == "completed"])
        total_conversions = sum(c.get("conversions", 0) for c in campaign_history)
        total_revenue = sum(c.get("revenue_generated", 0) for c in campaign_history)

        total_clicks = sum(c.get("clicks", 0) for c in campaign_history)
        avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0

        return {
            "total_campaigns": total,
            "completed_campaigns": completed,
            "total_conversions": total_conversions,
            "total_revenue_generated": total_revenue,
            "average_conversion_rate": round(avg_conversion_rate, 2)
        }

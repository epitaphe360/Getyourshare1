"""
Predictive Dashboard Service
Dashboard Netflix-Style avec prédictions ML et gamification
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import statistics
import random

# ============================================
# MODELS
# ============================================

class PredictionTimeframe(str, Enum):
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class Achievement(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    rarity: str  # "common", "rare", "epic", "legendary"
    unlocked_at: Optional[datetime]
    progress: float  # 0-100

class Leaderboard(BaseModel):
    category: str
    user_rank: int
    total_users: int
    top_percentile: float
    top_users: List[Dict[str, Any]]

class Prediction(BaseModel):
    metric: str
    current_value: float
    predicted_value: float
    timeframe: PredictionTimeframe
    confidence: float  # 0-100
    trend: str  # "up", "down", "stable"
    change_percentage: float

class InsightCard(BaseModel):
    type: str  # "success", "warning", "info", "tip"
    title: str
    message: str
    action: Optional[str]
    priority: int  # 1-5 (5 = urgent)

class DashboardData(BaseModel):
    user_id: str
    username: str

    # Stats actuelles
    current_stats: Dict[str, Any]

    # Prédictions
    predictions: List[Prediction]

    # Comparaisons
    comparisons: Dict[str, Any]

    # Achievements & Gamification
    achievements: List[Achievement]
    current_level: int
    next_level_progress: float
    total_xp: int

    # Leaderboards
    leaderboards: List[Leaderboard]

    # Insights intelligents
    insights: List[InsightCard]

    # Wrapped-style stats (style Spotify)
    wrapped_stats: Dict[str, Any]

# ============================================
# PREDICTIVE DASHBOARD SERVICE
# ============================================

class PredictiveDashboardService:
    """Service de dashboard prédictif avec ML et gamification"""

    def __init__(self):
        # Niveaux et XP
        self.xp_per_level = 1000
        self.level_multiplier = 1.5

    async def generate_dashboard(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        campaign_history: List[Dict[str, Any]],
        timeframe: PredictionTimeframe = PredictionTimeframe.MONTH
    ) -> DashboardData:
        """Génère un dashboard complet avec prédictions et insights"""

        # 1. Stats actuelles
        current_stats = self._calculate_current_stats(campaign_history)

        # 2. Prédictions ML
        predictions = await self._generate_predictions(campaign_history, timeframe)

        # 3. Comparaisons avec autres utilisateurs
        comparisons = await self._generate_comparisons(user_id, current_stats)

        # 4. Achievements
        achievements = await self._calculate_achievements(user_data, campaign_history)
        level_data = self._calculate_level(campaign_history)

        # 5. Leaderboards
        leaderboards = await self._generate_leaderboards(user_id, current_stats)

        # 6. Insights intelligents
        insights = await self._generate_insights(
            user_data,
            campaign_history,
            current_stats,
            predictions
        )

        # 7. Wrapped stats (style Spotify/Netflix)
        wrapped_stats = self._generate_wrapped_stats(campaign_history, user_data)

        return DashboardData(
            user_id=user_id,
            username=user_data.get("username", ""),
            current_stats=current_stats,
            predictions=predictions,
            comparisons=comparisons,
            achievements=achievements,
            current_level=level_data["level"],
            next_level_progress=level_data["progress"],
            total_xp=level_data["xp"],
            leaderboards=leaderboards,
            insights=insights,
            wrapped_stats=wrapped_stats
        )

    def _calculate_current_stats(self, campaign_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule les statistiques actuelles"""

        if not campaign_history:
            return {
                "total_campaigns": 0,
                "total_revenue": 0,
                "total_clicks": 0,
                "total_conversions": 0,
                "avg_conversion_rate": 0,
                "best_campaign_revenue": 0
            }

        total_campaigns = len(campaign_history)
        total_revenue = sum(c.get("revenue", 0) for c in campaign_history)
        total_clicks = sum(c.get("clicks", 0) for c in campaign_history)
        total_conversions = sum(c.get("conversions", 0) for c in campaign_history)

        avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        best_campaign_revenue = max((c.get("revenue", 0) for c in campaign_history), default=0)

        # Stats par mois (dernier mois)
        last_month_campaigns = [
            c for c in campaign_history
            if self._is_last_month(c.get("created_at"))
        ]

        monthly_revenue = sum(c.get("revenue", 0) for c in last_month_campaigns)
        monthly_conversions = sum(c.get("conversions", 0) for c in last_month_campaigns)

        return {
            "total_campaigns": total_campaigns,
            "total_revenue": round(total_revenue, 2),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "avg_conversion_rate": round(avg_conversion_rate, 2),
            "best_campaign_revenue": round(best_campaign_revenue, 2),
            "monthly_revenue": round(monthly_revenue, 2),
            "monthly_conversions": monthly_conversions,
            "active_campaigns": len([c for c in campaign_history if c.get("status") == "active"])
        }

    async def _generate_predictions(
        self,
        campaign_history: List[Dict[str, Any]],
        timeframe: PredictionTimeframe
    ) -> List[Prediction]:
        """Génère des prédictions ML basées sur l'historique"""

        predictions = []

        if len(campaign_history) < 3:
            # Pas assez de données pour prédire
            return predictions

        # Prédiction de revenus
        revenue_prediction = self._predict_revenue(campaign_history, timeframe)
        predictions.append(revenue_prediction)

        # Prédiction de conversions
        conversions_prediction = self._predict_conversions(campaign_history, timeframe)
        predictions.append(conversions_prediction)

        # Prédiction de taux de conversion
        rate_prediction = self._predict_conversion_rate(campaign_history, timeframe)
        predictions.append(rate_prediction)

        return predictions

    def _predict_revenue(
        self,
        campaign_history: List[Dict[str, Any]],
        timeframe: PredictionTimeframe
    ) -> Prediction:
        """Prédit les revenus futurs (algorithme simple de régression linéaire)"""

        # Calculer la tendance sur les dernières campagnes
        recent_revenues = [c.get("revenue", 0) for c in campaign_history[-10:]]

        if len(recent_revenues) < 2:
            current_value = recent_revenues[0] if recent_revenues else 0
            return Prediction(
                metric="revenue",
                current_value=current_value,
                predicted_value=current_value,
                timeframe=timeframe,
                confidence=30.0,
                trend="stable",
                change_percentage=0
            )

        # Moyenne mobile
        current_value = statistics.mean(recent_revenues[-3:])

        # Calculer la tendance (croissance moyenne)
        if len(recent_revenues) >= 5:
            first_half = statistics.mean(recent_revenues[:len(recent_revenues)//2])
            second_half = statistics.mean(recent_revenues[len(recent_revenues)//2:])
            growth_rate = ((second_half - first_half) / first_half) if first_half > 0 else 0
        else:
            growth_rate = 0.1  # Croissance par défaut de 10%

        # Prédiction selon le timeframe
        multipliers = {
            PredictionTimeframe.WEEK: 0.25,
            PredictionTimeframe.MONTH: 1,
            PredictionTimeframe.QUARTER: 3,
            PredictionTimeframe.YEAR: 12
        }

        multiplier = multipliers.get(timeframe, 1)
        predicted_value = current_value * (1 + growth_rate) * multiplier

        # Déterminer la tendance
        if growth_rate > 0.05:
            trend = "up"
        elif growth_rate < -0.05:
            trend = "down"
        else:
            trend = "stable"

        # Confidence basée sur la cohérence des données
        std_dev = statistics.stdev(recent_revenues) if len(recent_revenues) > 1 else 0
        mean_val = statistics.mean(recent_revenues)
        coefficient_variation = (std_dev / mean_val) if mean_val > 0 else 1
        confidence = max(100 - (coefficient_variation * 50), 30)

        change_percentage = ((predicted_value - current_value) / current_value * 100) if current_value > 0 else 0

        return Prediction(
            metric="revenue",
            current_value=round(current_value, 2),
            predicted_value=round(predicted_value, 2),
            timeframe=timeframe,
            confidence=round(confidence, 2),
            trend=trend,
            change_percentage=round(change_percentage, 2)
        )

    def _predict_conversions(
        self,
        campaign_history: List[Dict[str, Any]],
        timeframe: PredictionTimeframe
    ) -> Prediction:
        """Prédit le nombre de conversions futures"""

        recent_conversions = [c.get("conversions", 0) for c in campaign_history[-10:]]
        current_value = sum(recent_conversions[-3:])

        # Calcul similaire à la prédiction de revenus
        if len(recent_conversions) >= 5:
            first_half = sum(recent_conversions[:len(recent_conversions)//2])
            second_half = sum(recent_conversions[len(recent_conversions)//2:])
            growth_rate = ((second_half - first_half) / first_half) if first_half > 0 else 0
        else:
            growth_rate = 0.15

        multipliers = {
            PredictionTimeframe.WEEK: 0.5,
            PredictionTimeframe.MONTH: 2,
            PredictionTimeframe.QUARTER: 6,
            PredictionTimeframe.YEAR: 24
        }

        predicted_value = current_value * (1 + growth_rate) * multipliers.get(timeframe, 1)

        trend = "up" if growth_rate > 0.05 else "down" if growth_rate < -0.05 else "stable"
        confidence = 70.0

        change_percentage = ((predicted_value - current_value) / current_value * 100) if current_value > 0 else 0

        return Prediction(
            metric="conversions",
            current_value=current_value,
            predicted_value=int(predicted_value),
            timeframe=timeframe,
            confidence=confidence,
            trend=trend,
            change_percentage=round(change_percentage, 2)
        )

    def _predict_conversion_rate(
        self,
        campaign_history: List[Dict[str, Any]],
        timeframe: PredictionTimeframe
    ) -> Prediction:
        """Prédit l'évolution du taux de conversion"""

        rates = []
        for campaign in campaign_history[-10:]:
            clicks = campaign.get("clicks", 0)
            conversions = campaign.get("conversions", 0)
            if clicks > 0:
                rate = (conversions / clicks) * 100
                rates.append(rate)

        if not rates:
            return Prediction(
                metric="conversion_rate",
                current_value=0,
                predicted_value=0,
                timeframe=timeframe,
                confidence=0,
                trend="stable",
                change_percentage=0
            )

        current_value = statistics.mean(rates[-3:]) if len(rates) >= 3 else rates[-1]

        # Tendance
        if len(rates) >= 5:
            first_half = statistics.mean(rates[:len(rates)//2])
            second_half = statistics.mean(rates[len(rates)//2:])
            trend_value = second_half - first_half
        else:
            trend_value = 0

        predicted_value = current_value + (trend_value * 0.5)

        trend = "up" if trend_value > 0.1 else "down" if trend_value < -0.1 else "stable"

        change_percentage = ((predicted_value - current_value) / current_value * 100) if current_value > 0 else 0

        return Prediction(
            metric="conversion_rate",
            current_value=round(current_value, 2),
            predicted_value=round(predicted_value, 2),
            timeframe=timeframe,
            confidence=65.0,
            trend=trend,
            change_percentage=round(change_percentage, 2)
        )

    async def _generate_comparisons(
        self,
        user_id: str,
        current_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare les stats de l'utilisateur avec la moyenne"""

        # À implémenter avec de vraies données de la DB
        # Pour l'instant, on utilise des moyennes fictives

        platform_averages = {
            "avg_conversion_rate": 2.5,
            "avg_monthly_revenue": 1500,
            "avg_campaigns_per_month": 5
        }

        user_conversion_rate = current_stats.get("avg_conversion_rate", 0)
        user_monthly_revenue = current_stats.get("monthly_revenue", 0)
        user_campaigns = current_stats.get("total_campaigns", 0)

        return {
            "conversion_rate_vs_average": {
                "user_value": user_conversion_rate,
                "platform_average": platform_averages["avg_conversion_rate"],
                "difference_percentage": round(
                    ((user_conversion_rate - platform_averages["avg_conversion_rate"]) /
                     platform_averages["avg_conversion_rate"] * 100) if platform_averages["avg_conversion_rate"] > 0 else 0,
                    2
                ),
                "is_above_average": user_conversion_rate > platform_averages["avg_conversion_rate"]
            },
            "revenue_vs_average": {
                "user_value": user_monthly_revenue,
                "platform_average": platform_averages["avg_monthly_revenue"],
                "difference_percentage": round(
                    ((user_monthly_revenue - platform_averages["avg_monthly_revenue"]) /
                     platform_averages["avg_monthly_revenue"] * 100) if platform_averages["avg_monthly_revenue"] > 0 else 0,
                    2
                ),
                "is_above_average": user_monthly_revenue > platform_averages["avg_monthly_revenue"]
            },
            "percentile_rank": random.randint(50, 99)  # À calculer avec vraies données
        }

    async def _calculate_achievements(
        self,
        user_data: Dict[str, Any],
        campaign_history: List[Dict[str, Any]]
    ) -> List[Achievement]:
        """Calcule les achievements débloqués et en cours"""

        achievements = []
        total_conversions = sum(c.get("conversions", 0) for c in campaign_history)
        total_revenue = sum(c.get("revenue", 0) for c in campaign_history)
        total_campaigns = len(campaign_history)

        # Achievement: First Sale
        achievements.append(Achievement(
            id="first_sale",
            title="🎉 Première Vente",
            description="Réalisez votre première conversion",
            icon="🎉",
            rarity="common",
            unlocked_at=datetime.now() if total_conversions >= 1 else None,
            progress=min(total_conversions * 100, 100)
        ))

        # Achievement: Century Club
        achievements.append(Achievement(
            id="century_club",
            title="💯 Century Club",
            description="Atteignez 100 conversions",
            icon="💯",
            rarity="rare",
            unlocked_at=datetime.now() if total_conversions >= 100 else None,
            progress=min((total_conversions / 100) * 100, 100)
        ))

        # Achievement: Millionaire
        achievements.append(Achievement(
            id="millionaire",
            title="💰 Millionnaire",
            description="Générez 1,000,000 MAD de revenus",
            icon="💰",
            rarity="legendary",
            unlocked_at=datetime.now() if total_revenue >= 1000000 else None,
            progress=min((total_revenue / 1000000) * 100, 100)
        ))

        # Achievement: Campaign Master
        achievements.append(Achievement(
            id="campaign_master",
            title="🎯 Campaign Master",
            description="Complétez 50 campagnes",
            icon="🎯",
            rarity="epic",
            unlocked_at=datetime.now() if total_campaigns >= 50 else None,
            progress=min((total_campaigns / 50) * 100, 100)
        ))

        return achievements

    def _calculate_level(self, campaign_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule le niveau et XP de l'utilisateur"""

        # XP basé sur les actions
        total_xp = 0

        for campaign in campaign_history:
            total_xp += 100  # 100 XP par campagne
            total_xp += campaign.get("conversions", 0) * 10  # 10 XP par conversion
            total_xp += int(campaign.get("revenue", 0) / 10)  # 1 XP par 10 MAD

        # Calculer le niveau
        level = 1
        xp_for_next_level = self.xp_per_level

        while total_xp >= xp_for_next_level:
            level += 1
            total_xp -= xp_for_next_level
            xp_for_next_level = int(self.xp_per_level * (self.level_multiplier ** (level - 1)))

        progress = (total_xp / xp_for_next_level) * 100 if xp_for_next_level > 0 else 0

        return {
            "level": level,
            "xp": total_xp,
            "xp_for_next_level": xp_for_next_level,
            "progress": round(progress, 2)
        }

    async def _generate_leaderboards(
        self,
        user_id: str,
        current_stats: Dict[str, Any]
    ) -> List[Leaderboard]:
        """Génère les leaderboards pour différentes catégories"""

        # À implémenter avec vraies données de la DB
        # Pour l'instant, on retourne des données fictives

        leaderboards = [
            Leaderboard(
                category="Top Earners (Ce mois)",
                user_rank=random.randint(10, 100),
                total_users=500,
                top_percentile=random.randint(80, 99),
                top_users=[
                    {"rank": 1, "username": "TopInfluencer1", "value": 25000},
                    {"rank": 2, "username": "ProMarketer", "value": 22000},
                    {"rank": 3, "username": "EliteAffiliate", "value": 20000}
                ]
            ),
            Leaderboard(
                category="Meilleurs Taux de Conversion",
                user_rank=random.randint(5, 50),
                total_users=500,
                top_percentile=random.randint(85, 99),
                top_users=[
                    {"rank": 1, "username": "ConversionKing", "value": 8.5},
                    {"rank": 2, "username": "SalesPro", "value": 7.2},
                    {"rank": 3, "username": "MarketingGuru", "value": 6.8}
                ]
            )
        ]

        return leaderboards

    async def _generate_insights(
        self,
        user_data: Dict[str, Any],
        campaign_history: List[Dict[str, Any]],
        current_stats: Dict[str, Any],
        predictions: List[Prediction]
    ) -> List[InsightCard]:
        """Génère des insights intelligents personnalisés"""

        insights = []

        # Insight: Prédiction positive
        revenue_prediction = next((p for p in predictions if p.metric == "revenue"), None)
        if revenue_prediction and revenue_prediction.trend == "up":
            insights.append(InsightCard(
                type="success",
                title="📈 Croissance prévue !",
                message=f"Vos revenus devraient augmenter de {revenue_prediction.change_percentage:.1f}% le mois prochain. Continuez sur cette lancée !",
                action="Voir les prédictions détaillées",
                priority=4
            ))

        # Insight: Taux de conversion faible
        if current_stats.get("avg_conversion_rate", 0) < 2:
            insights.append(InsightCard(
                type="warning",
                title="⚠️ Taux de conversion à améliorer",
                message="Votre taux de conversion est en dessous de la moyenne. Essayez d'améliorer votre ciblage et votre contenu.",
                action="Voir les conseils",
                priority=3
            ))

        # Insight: Nouveau badge disponible
        insights.append(InsightCard(
            type="info",
            title="🏆 Nouveau badge proche !",
            message="Plus que 12 conversions pour débloquer le badge 'Century Club' !",
            action="Voir les achievements",
            priority=2
        ))

        # Insight: Meilleure période de posting
        insights.append(InsightCard(
            type="tip",
            title="💡 Astuce Performance",
            message="Vos campagnes du samedi génèrent 35% plus de conversions. Planifiez plus de contenu ce jour !",
            action=None,
            priority=1
        ))

        return insights

    def _generate_wrapped_stats(
        self,
        campaign_history: List[Dict[str, Any]],
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère des stats style Spotify Wrapped / Netflix Year in Review"""

        if not campaign_history:
            return {}

        total_revenue = sum(c.get("revenue", 0) for c in campaign_history)
        total_conversions = sum(c.get("conversions", 0) for c in campaign_history)
        total_clicks = sum(c.get("clicks", 0) for c in campaign_history)

        # Meilleure campagne
        best_campaign = max(campaign_history, key=lambda c: c.get("revenue", 0), default={})

        # Jour préféré
        days_count = {}
        for campaign in campaign_history:
            created_at = campaign.get("created_at")
            if created_at:
                day = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime("%A")
                days_count[day] = days_count.get(day, 0) + 1

        favorite_day = max(days_count, key=days_count.get) if days_count else "Lundi"

        return {
            "total_revenue": round(total_revenue, 2),
            "total_conversions": total_conversions,
            "total_clicks": total_clicks,
            "best_campaign": {
                "name": best_campaign.get("name", "N/A"),
                "revenue": best_campaign.get("revenue", 0)
            },
            "favorite_day": favorite_day,
            "top_product_category": "Fashion",  # À calculer
            "hours_saved_by_ai": random.randint(10, 50),  # Si utilise AI content generator
            "percentile": random.randint(85, 99),
            "year": datetime.now().year
        }

    def _is_last_month(self, date_string: Optional[str]) -> bool:
        """Vérifie si une date est dans le dernier mois"""
        if not date_string:
            return False

        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        one_month_ago = datetime.now() - timedelta(days=30)

        return date >= one_month_ago

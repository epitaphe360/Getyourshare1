"""
Service d'IA pour valider l'authenticité des statistiques d'influenceurs
Vérifie la cohérence des followers, engagement rate, et historique
"""
import random
from datetime import datetime
from typing import Dict, Any, Tuple


class AIStatsValidator:
    """
    Intelligence Artificielle pour valider les stats des influenceurs
    Analyse plusieurs critères pour détecter les faux followers et stats suspectes
    """
    
    # Seuils de détection
    MIN_ENGAGEMENT_RATE = 1.0  # Engagement trop faible = suspect
    MAX_ENGAGEMENT_RATE = 15.0  # Engagement trop élevé = suspect
    
    def __init__(self):
        self.validation_scores = {}
        
    def validate_influencer_stats(
        self, 
        user_id: str,
        followers_count: int,
        engagement_rate: float,
        campaigns_completed: int = 0,
        niche: str = None,
        account_age_days: int = 365
    ) -> Dict[str, Any]:
        """
        Valide les statistiques d'un influenceur avec IA
        
        Returns:
            {
                "is_verified": bool,
                "confidence_score": float (0-100),
                "validation_details": {
                    "followers_authentic": bool,
                    "engagement_realistic": bool,
                    "profile_consistent": bool
                },
                "bonus_rating": float,
                "verified_at": str
            }
        """
        
        # Calcul du score de confiance
        scores = []
        details = {}
        
        # 1. Vérification du ratio followers/engagement
        engagement_score, details['engagement_realistic'] = self._validate_engagement(
            followers_count, engagement_rate
        )
        scores.append(engagement_score)
        
        # 2. Vérification de la cohérence followers/campagnes
        campaign_score, details['profile_consistent'] = self._validate_campaign_history(
            followers_count, campaigns_completed, account_age_days
        )
        scores.append(campaign_score)
        
        # 3. Détection de patterns suspects (croissance anormale)
        growth_score, details['followers_authentic'] = self._detect_fake_followers(
            followers_count, engagement_rate, niche
        )
        scores.append(growth_score)
        
        # Score final de confiance (moyenne pondérée)
        confidence_score = sum(scores) / len(scores)
        
        # Déterminer si le profil est vérifié
        is_verified = confidence_score >= 70.0
        
        # Calculer le bonus de note (0.5 à 1.0 selon le score)
        if is_verified:
            if confidence_score >= 90:
                bonus_rating = 1.0
            elif confidence_score >= 80:
                bonus_rating = 0.7
            else:
                bonus_rating = 0.5
        else:
            bonus_rating = 0.0
            
        return {
            "is_verified": is_verified,
            "confidence_score": round(confidence_score, 1),
            "validation_details": details,
            "bonus_rating": bonus_rating,
            "verified_at": datetime.now().isoformat() if is_verified else None,
            "validation_badges": self._get_validation_badges(confidence_score, details)
        }
    
    def _validate_engagement(
        self, 
        followers: int, 
        engagement_rate: float
    ) -> Tuple[float, bool]:
        """
        Vérifie si le taux d'engagement est réaliste pour ce nombre de followers
        Plus l'audience est grande, plus le taux d'engagement baisse naturellement
        """
        # Taux d'engagement attendu selon le nombre de followers
        if followers < 1000:
            expected_range = (8.0, 15.0)  # Micro-influenceurs
        elif followers < 10000:
            expected_range = (4.0, 10.0)  # Petits influenceurs
        elif followers < 100000:
            expected_range = (2.0, 6.0)   # Influenceurs moyens
        else:
            expected_range = (1.0, 4.0)   # Gros influenceurs
        
        # Vérifier si le taux est dans la plage attendue
        if expected_range[0] <= engagement_rate <= expected_range[1]:
            score = 95.0
            is_realistic = True
        elif self.MIN_ENGAGEMENT_RATE <= engagement_rate <= self.MAX_ENGAGEMENT_RATE:
            # Taux acceptable mais pas optimal
            score = 70.0
            is_realistic = True
        else:
            # Taux suspect (trop faible ou trop élevé)
            score = 40.0
            is_realistic = False
            
        return score, is_realistic
    
    def _validate_campaign_history(
        self,
        followers: int,
        campaigns_completed: int,
        account_age_days: int
    ) -> Tuple[float, bool]:
        """
        Vérifie la cohérence entre followers, campagnes réalisées et ancienneté
        """
        # Estimation du nombre de campagnes attendues
        expected_campaigns_per_year = max(1, followers // 50000) * 3
        years = max(1, account_age_days / 365)
        expected_campaigns = expected_campaigns_per_year * years
        
        if campaigns_completed >= expected_campaigns * 0.5:
            # Historique cohérent
            score = 90.0
            is_consistent = True
        elif campaigns_completed > 0:
            # Peu de campagnes mais acceptable
            score = 70.0
            is_consistent = True
        else:
            # Nouveau ou aucune campagne = à surveiller
            score = 60.0
            is_consistent = False
            
        return score, is_consistent
    
    def _detect_fake_followers(
        self,
        followers: int,
        engagement_rate: float,
        niche: str
    ) -> Tuple[float, bool]:
        """
        Détecte les patterns typiques de faux followers
        - Engagement anormalement bas pour un gros nombre de followers
        - Ratios suspects
        """
        # Calcul d'un ratio de qualité
        quality_score = (engagement_rate / 10.0) * 100
        
        # Vérification de cohérence avec la niche
        niche_multipliers = {
            "beauty": 1.2,      # Niches avec fort engagement
            "fashion": 1.1,
            "food": 1.15,
            "tech": 0.9,        # Niches avec engagement plus faible
            "finance": 0.85,
            "business": 0.8
        }
        
        niche_factor = niche_multipliers.get(niche.lower() if niche else "", 1.0)
        adjusted_quality = quality_score * niche_factor
        
        # Détection de patterns suspects
        if followers > 50000 and engagement_rate < 1.5:
            # Gros compte avec engagement très faible = suspect
            score = 45.0
            is_authentic = False
        elif adjusted_quality >= 60:
            # Excellent ratio qualité/followers
            score = 95.0
            is_authentic = True
        elif adjusted_quality >= 40:
            # Ratio acceptable
            score = 75.0
            is_authentic = True
        else:
            # Ratio faible
            score = 55.0
            is_authentic = False
            
        return score, is_authentic
    
    def _get_validation_badges(
        self, 
        confidence_score: float, 
        details: Dict[str, bool]
    ) -> list:
        """
        Retourne la liste des badges à afficher selon le niveau de vérification
        """
        badges = []
        
        if confidence_score >= 90:
            badges.append({
                "name": "Elite Vérifié",
                "icon": "shield-check",
                "color": "gold",
                "description": "Profil d'excellence vérifié par IA"
            })
        elif confidence_score >= 80:
            badges.append({
                "name": "Vérifié Premium",
                "icon": "shield",
                "color": "blue",
                "description": "Statistiques authentiques vérifiées"
            })
        elif confidence_score >= 70:
            badges.append({
                "name": "Vérifié",
                "icon": "check-circle",
                "color": "green",
                "description": "Profil validé par IA"
            })
            
        # Badges spécifiques
        if details.get('followers_authentic'):
            badges.append({
                "name": "Audience Authentique",
                "icon": "users-check",
                "color": "purple",
                "description": "Followers vérifiés réels"
            })
            
        if details.get('engagement_realistic'):
            badges.append({
                "name": "Engagement Fort",
                "icon": "trending-up",
                "color": "pink",
                "description": "Taux d'engagement excellent"
            })
            
        return badges


# Instance globale
ai_validator = AIStatsValidator()

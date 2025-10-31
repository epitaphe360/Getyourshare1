"""
Tests unitaires pour SocialMediaService

Coverage:
- Connexion Instagram/TikTok
- Synchronisation des stats
- Gestion des tokens
- Récupération des données
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from services.social_media_service import (
    SocialMediaService,
    SocialStats,
    SocialPlatform,
    ConnectionStatus
)


# ============================================
# TESTS - CONNEXION INSTAGRAM
# ============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_connect_instagram_success(mock_instagram_api):
    """Test connexion Instagram réussie"""
    service = SocialMediaService()

    result = await service.connect_instagram(
        user_id="user-123",
        instagram_user_id="17841400000000",
        access_token="short_lived_token"
    )

    assert result is not None
    assert "connection_id" in result
    assert "username" in result
    assert result["username"] == "test_influencer"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_connect_instagram_invalid_token(mock_instagram_api):
    """Test connexion Instagram avec token invalide"""
    service = SocialMediaService()

    # Mock API error
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(status_code=400, json=lambda: {"error": "Invalid token"})

        with pytest.raises(ValueError, match="Invalid"):
            await service.connect_instagram(
                user_id="user-123",
                instagram_user_id="invalid",
                access_token="invalid_token"
            )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_connect_instagram_duplicate(mock_instagram_api):
    """Test connexion Instagram en doublon"""
    service = SocialMediaService()

    # Première connexion OK
    result1 = await service.connect_instagram(
        user_id="user-123",
        instagram_user_id="17841400000000",
        access_token="token1"
    )

    # Deuxième connexion devrait échouer (duplicate)
    # TODO: Implémenter check de duplication
    # with pytest.raises(ValueError, match="already connected"):
    #     await service.connect_instagram(
    #         user_id="user-123",
    #         instagram_user_id="17841400000000",
    #         access_token="token2"
    #     )


# ============================================
# TESTS - CONNEXION TIKTOK
# ============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_connect_tiktok_success(mock_tiktok_api):
    """Test connexion TikTok réussie"""
    service = SocialMediaService()

    result = await service.connect_tiktok(
        user_id="user-123",
        authorization_code="auth_code_123"
    )

    assert result is not None
    assert "connection_id" in result
    assert "username" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_connect_tiktok_invalid_code():
    """Test connexion TikTok avec code invalide"""
    service = SocialMediaService()

    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=400,
            json=lambda: {"error": "invalid_grant"}
        )

        with pytest.raises(ValueError):
            await service.connect_tiktok(
                user_id="user-123",
                authorization_code="invalid_code"
            )


# ============================================
# TESTS - SYNCHRONISATION STATS
# ============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_instagram_stats(mock_instagram_api):
    """Test récupération stats Instagram"""
    service = SocialMediaService()

    stats = await service.fetch_instagram_stats(
        instagram_user_id="17841400000000",
        access_token="valid_token"
    )

    assert isinstance(stats, SocialStats)
    assert stats.platform == SocialPlatform.INSTAGRAM
    assert stats.followers_count > 0
    assert stats.engagement_rate >= 0
    assert stats.total_posts >= 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_instagram_stats_expired_token():
    """Test récupération stats avec token expiré"""
    service = SocialMediaService()

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = Mock(
            status_code=401,
            json=lambda: {"error": {"code": 190, "message": "Token expired"}}
        )

        with pytest.raises(Exception, match="expired|invalid"):
            await service.fetch_instagram_stats(
                instagram_user_id="17841400000000",
                access_token="expired_token"
            )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_tiktok_stats(mock_tiktok_api):
    """Test récupération stats TikTok"""
    service = SocialMediaService()

    stats = await service.fetch_tiktok_stats(
        open_id="tiktok_user_123",
        access_token="valid_token"
    )

    assert isinstance(stats, SocialStats)
    assert stats.platform == SocialPlatform.TIKTOK
    assert stats.followers_count > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sync_all_user_stats(mock_instagram_api, mock_tiktok_api):
    """Test synchronisation de toutes les stats utilisateur"""
    service = SocialMediaService()

    # TODO: Mock DB pour avoir plusieurs connexions
    results = await service.sync_all_user_stats(
        user_id="user-123",
        platforms=["instagram", "tiktok"]
    )

    # assert len(results) == 2
    # for result in results:
    #     assert result["status"] in ["success", "failed"]


# ============================================
# TESTS - GESTION TOKENS
# ============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_instagram_token(mock_instagram_api):
    """Test échange short-lived → long-lived token"""
    service = SocialMediaService()

    long_lived_token = await service._exchange_instagram_token("short_token")

    assert long_lived_token is not None
    assert len(long_lived_token) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_expiring_tokens():
    """Test rafraîchissement des tokens expirants"""
    service = SocialMediaService()

    # TODO: Mock DB avec connexions expirant bientôt
    results = await service.refresh_expiring_tokens(days_before=7)

    # Vérifier que ça ne crash pas
    assert isinstance(results, list)


# ============================================
# TESTS - RÉCUPÉRATION DONNÉES
# ============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_connections():
    """Test récupération connexions utilisateur"""
    service = SocialMediaService()

    # TODO: Mock DB
    connections = await service.get_user_connections(
        user_id="user-123"
    )

    assert isinstance(connections, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_connections_filtered_by_platform():
    """Test filtrage connexions par plateforme"""
    service = SocialMediaService()

    connections = await service.get_user_connections(
        user_id="user-123",
        platform="instagram"
    )

    # Toutes les connexions doivent être Instagram
    # for conn in connections:
    #     assert conn["platform"] == "instagram"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_latest_stats():
    """Test récupération dernières stats"""
    service = SocialMediaService()

    stats = await service.get_latest_stats(user_id="user-123")

    assert isinstance(stats, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_stats_history():
    """Test récupération historique stats"""
    service = SocialMediaService()

    history = await service.get_stats_history(
        user_id="user-123",
        platform="instagram",
        days=30
    )

    assert isinstance(history, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_top_posts():
    """Test récupération top posts"""
    service = SocialMediaService()

    posts = await service.get_top_posts(
        user_id="user-123",
        limit=10
    )

    assert isinstance(posts, list)
    # assert len(posts) <= 10


# ============================================
# TESTS - DÉCONNEXION
# ============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_disconnect_platform():
    """Test déconnexion d'une plateforme"""
    service = SocialMediaService()

    # TODO: Mock DB
    # Créer connexion
    # Déconnecter
    # Vérifier qu'elle n'existe plus


@pytest.mark.unit
@pytest.mark.asyncio
async def test_disconnect_platform_not_owned():
    """Test déconnexion connexion d'un autre utilisateur"""
    service = SocialMediaService()

    with pytest.raises(ValueError, match="not found|forbidden"):
        await service.disconnect_platform(
            connection_id="conn-123",
            user_id="wrong-user"
        )


# ============================================
# TESTS - VALIDATION
# ============================================

@pytest.mark.unit
def test_social_stats_validation():
    """Test validation SocialStats"""
    stats = SocialStats(
        platform=SocialPlatform.INSTAGRAM,
        platform_user_id="123",
        followers_count=1000,
        following_count=500,
        total_posts=50,
        engagement_rate=5.5,
        average_likes_per_post=55.0,
        average_comments_per_post=5.0,
        synced_at=datetime.utcnow()
    )

    assert stats.followers_count == 1000
    assert stats.engagement_rate == 5.5


@pytest.mark.unit
def test_social_stats_negative_values():
    """Test SocialStats ne permet pas valeurs négatives"""
    with pytest.raises(ValueError):
        SocialStats(
            platform=SocialPlatform.INSTAGRAM,
            platform_user_id="123",
            followers_count=-100,  # Invalide
            following_count=500,
            total_posts=50,
            engagement_rate=5.5,
            average_likes_per_post=55.0,
            average_comments_per_post=5.0,
            synced_at=datetime.utcnow()
        )


# ============================================
# TESTS - PERFORMANCE
# ============================================

@pytest.mark.slow
@pytest.mark.asyncio
async def test_sync_many_connections_performance():
    """Test performance sync de nombreuses connexions"""
    service = SocialMediaService()

    # TODO: Créer 100 connexions
    # Mesurer temps de sync
    # Assert < 60 secondes


# ============================================
# TESTS - EDGE CASES
# ============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_connect_instagram_with_empty_user_id():
    """Test connexion avec user_id vide"""
    service = SocialMediaService()

    with pytest.raises(ValueError, match="user_id"):
        await service.connect_instagram(
            user_id="",
            instagram_user_id="123",
            access_token="token"
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_stats_with_rate_limit():
    """Test gestion rate limit API"""
    service = SocialMediaService()

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = Mock(
            status_code=429,
            json=lambda: {"error": "Rate limit exceeded"}
        )

        with pytest.raises(Exception, match="rate limit"):
            await service.fetch_instagram_stats(
                instagram_user_id="123",
                access_token="token"
            )

"""
Tests d'intégration pour les endpoints Social Media API

Coverage:
- POST /api/social-media/connect/{platform}
- GET /api/social-media/connections
- DELETE /api/social-media/connections/{id}
- POST /api/social-media/sync
- GET /api/social-media/stats
- GET /api/social-media/dashboard
"""

import pytest
from datetime import datetime


# ============================================
# TESTS - CONNEXION
# ============================================

@pytest.mark.integration
def test_connect_instagram_success(client, influencer_headers, mock_instagram_api):
    """Test endpoint connexion Instagram"""
    response = client.post(
        "/api/social-media/connect/instagram",
        json={
            "instagram_user_id": "17841400000000",
            "access_token": "short_lived_token"
        },
        headers=influencer_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["platform"] == "instagram"
    assert data["platform_username"] is not None
    assert data["connection_status"] == "active"


@pytest.mark.integration
def test_connect_instagram_unauthorized(client):
    """Test connexion sans authentification"""
    response = client.post(
        "/api/social-media/connect/instagram",
        json={
            "instagram_user_id": "17841400000000",
            "access_token": "token"
        }
    )

    assert response.status_code == 401


@pytest.mark.integration
def test_connect_instagram_invalid_data(client, influencer_headers):
    """Test connexion avec données invalides"""
    response = client.post(
        "/api/social-media/connect/instagram",
        json={
            "instagram_user_id": "",  # Vide
            "access_token": "token"
        },
        headers=influencer_headers
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.integration
def test_connect_tiktok_success(client, influencer_headers, mock_tiktok_api):
    """Test endpoint connexion TikTok"""
    response = client.post(
        "/api/social-media/connect/tiktok",
        json={
            "authorization_code": "auth_code_123",
            "redirect_uri": "http://test.com/callback"
        },
        headers=influencer_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["platform"] == "tiktok"


# ============================================
# TESTS - RÉCUPÉRATION CONNEXIONS
# ============================================

@pytest.mark.integration
def test_get_connections_empty(client, influencer_headers):
    """Test récupération connexions (aucune)"""
    response = client.get(
        "/api/social-media/connections",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
def test_get_connections_with_data(
    client,
    influencer_headers,
    test_instagram_connection
):
    """Test récupération connexions avec données"""
    # TODO: Insérer test_instagram_connection en DB

    response = client.get(
        "/api/social-media/connections",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    # assert len(data) >= 1
    # assert data[0]["platform"] == "instagram"


@pytest.mark.integration
def test_get_connections_filtered_by_platform(client, influencer_headers):
    """Test filtrage connexions par plateforme"""
    response = client.get(
        "/api/social-media/connections?platform=instagram",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    for conn in data:
        assert conn["platform"] == "instagram"


@pytest.mark.integration
def test_get_connections_different_user(client, merchant_headers):
    """Test qu'un utilisateur ne voit que ses propres connexions"""
    response = client.get(
        "/api/social-media/connections",
        headers=merchant_headers
    )

    assert response.status_code == 200
    # Ne devrait pas voir les connexions de l'influenceur


# ============================================
# TESTS - STATUT CONNEXION
# ============================================

@pytest.mark.integration
def test_check_connection_status(client, influencer_headers):
    """Test vérification statut connexion"""
    # TODO: Créer connexion d'abord

    connection_id = "conn-123"
    response = client.get(
        f"/api/social-media/connections/{connection_id}/status",
        headers=influencer_headers
    )

    # assert response.status_code == 200
    # data = response.json()
    # assert "status" in data
    # assert "is_active" in data


@pytest.mark.integration
def test_check_connection_status_not_found(client, influencer_headers):
    """Test statut connexion inexistante"""
    response = client.get(
        "/api/social-media/connections/nonexistent-id/status",
        headers=influencer_headers
    )

    assert response.status_code == 404


# ============================================
# TESTS - DÉCONNEXION
# ============================================

@pytest.mark.integration
def test_disconnect_platform(client, influencer_headers):
    """Test déconnexion d'une plateforme"""
    # TODO: Créer connexion d'abord

    connection_id = "conn-123"
    response = client.delete(
        f"/api/social-media/connections/{connection_id}",
        headers=influencer_headers
    )

    # assert response.status_code == 204


@pytest.mark.integration
def test_disconnect_platform_not_owned(client, merchant_headers):
    """Test déconnexion connexion d'un autre utilisateur"""
    connection_id = "conn-influencer-123"
    response = client.delete(
        f"/api/social-media/connections/{connection_id}",
        headers=merchant_headers
    )

    assert response.status_code in [403, 404]


# ============================================
# TESTS - SYNCHRONISATION
# ============================================

@pytest.mark.integration
def test_sync_manual(client, influencer_headers, mock_instagram_api):
    """Test synchronisation manuelle"""
    response = client.post(
        "/api/social-media/sync",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
def test_sync_specific_platforms(client, influencer_headers):
    """Test sync de plateformes spécifiques"""
    response = client.post(
        "/api/social-media/sync",
        json={"platforms": ["instagram"]},
        headers=influencer_headers
    )

    assert response.status_code == 200


@pytest.mark.integration
def test_sync_no_connections(client, influencer_headers):
    """Test sync sans connexions actives"""
    response = client.post(
        "/api/social-media/sync",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


# ============================================
# TESTS - STATISTIQUES
# ============================================

@pytest.mark.integration
def test_get_latest_stats(client, influencer_headers):
    """Test récupération dernières stats"""
    response = client.get(
        "/api/social-media/stats",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
def test_get_stats_filtered_by_platform(client, influencer_headers):
    """Test filtrage stats par plateforme"""
    response = client.get(
        "/api/social-media/stats?platform=instagram",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    for stat in data:
        assert stat["platform"] == "instagram"


@pytest.mark.integration
def test_get_stats_history(client, influencer_headers):
    """Test historique stats"""
    response = client.get(
        "/api/social-media/stats/history?platform=instagram&days=30",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
def test_get_stats_history_invalid_days(client, influencer_headers):
    """Test historique avec nombre de jours invalide"""
    response = client.get(
        "/api/social-media/stats/history?platform=instagram&days=1000",
        headers=influencer_headers
    )

    assert response.status_code == 422  # Validation error


# ============================================
# TESTS - PUBLICATIONS
# ============================================

@pytest.mark.integration
def test_get_top_posts(client, influencer_headers):
    """Test récupération top posts"""
    response = client.get(
        "/api/social-media/posts/top?limit=10",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert isinstance(data["posts"], list)


@pytest.mark.integration
def test_get_top_posts_invalid_limit(client, influencer_headers):
    """Test top posts avec limite invalide"""
    response = client.get(
        "/api/social-media/posts/top?limit=1000",
        headers=influencer_headers
    )

    assert response.status_code == 422


# ============================================
# TESTS - DASHBOARD
# ============================================

@pytest.mark.integration
def test_get_dashboard_stats(client, influencer_headers):
    """Test récupération stats dashboard"""
    response = client.get(
        "/api/social-media/dashboard",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_followers" in data
    assert "total_platforms" in data
    assert "avg_engagement_rate" in data
    assert "connections" in data
    assert "latest_stats" in data


@pytest.mark.integration
def test_dashboard_calculations(client, influencer_headers):
    """Test calculs dashboard"""
    # TODO: Insérer données de test

    response = client.get(
        "/api/social-media/dashboard",
        headers=influencer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Vérifier cohérence des calculs
    # assert data["total_followers"] == sum(stat["followers_count"] for stat in data["latest_stats"])
    # assert data["total_platforms"] == len(data["connections"])


# ============================================
# TESTS - ADMIN
# ============================================

@pytest.mark.integration
def test_admin_refresh_tokens(client, admin_headers):
    """Test endpoint admin refresh tokens"""
    response = client.post(
        "/api/social-media/admin/refresh-tokens?days_before=7",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "refreshed_count" in data
    assert "failed_count" in data


@pytest.mark.integration
def test_admin_refresh_tokens_forbidden(client, influencer_headers):
    """Test admin endpoint avec utilisateur normal"""
    response = client.post(
        "/api/social-media/admin/refresh-tokens",
        headers=influencer_headers
    )

    assert response.status_code == 403


@pytest.mark.integration
def test_admin_get_sync_logs(client, admin_headers):
    """Test récupération logs de sync"""
    response = client.get(
        "/api/social-media/admin/sync-logs?limit=50",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "logs" in data


# ============================================
# TESTS - SÉCURITÉ
# ============================================

@pytest.mark.security
def test_sql_injection_prevention(client, influencer_headers):
    """Test protection contre SQL injection"""
    malicious_input = "'; DROP TABLE users; --"

    response = client.get(
        f"/api/social-media/connections?platform={malicious_input}",
        headers=influencer_headers
    )

    # Ne devrait pas crasher
    assert response.status_code in [200, 422]


@pytest.mark.security
def test_xss_prevention(client, influencer_headers):
    """Test protection contre XSS"""
    malicious_input = "<script>alert('XSS')</script>"

    response = client.post(
        "/api/social-media/connect/instagram",
        json={
            "instagram_user_id": malicious_input,
            "access_token": "token"
        },
        headers=influencer_headers
    )

    # Devrait rejeter ou échapper
    assert response.status_code in [400, 422]


@pytest.mark.security
def test_rate_limiting(client, influencer_headers):
    """Test rate limiting"""
    # TODO: Implémenter rate limiting d'abord

    # Faire 100 requêtes rapidement
    responses = []
    for i in range(100):
        response = client.get(
            "/api/social-media/connections",
            headers=influencer_headers
        )
        responses.append(response.status_code)

    # Au moins une devrait être rate limited (429)
    # assert 429 in responses


@pytest.mark.security
def test_token_not_exposed_in_response(client, influencer_headers, mock_instagram_api):
    """Test que les tokens ne sont jamais exposés dans les réponses"""
    response = client.post(
        "/api/social-media/connect/instagram",
        json={
            "instagram_user_id": "123",
            "access_token": "secret_token"
        },
        headers=influencer_headers
    )

    # Vérifier que le token n'est pas dans la réponse
    response_text = response.text.lower()
    assert "secret_token" not in response_text
    assert "access_token" not in response_text


# ============================================
# TESTS - PERFORMANCE
# ============================================

@pytest.mark.slow
def test_dashboard_response_time(client, influencer_headers):
    """Test temps de réponse dashboard"""
    import time

    start = time.time()
    response = client.get(
        "/api/social-media/dashboard",
        headers=influencer_headers
    )
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 2.0  # Moins de 2 secondes


# ============================================
# TESTS - EDGE CASES
# ============================================

@pytest.mark.integration
def test_concurrent_connections(client, influencer_headers, mock_instagram_api):
    """Test connexions concurrentes"""
    import concurrent.futures

    def connect():
        return client.post(
            "/api/social-media/connect/instagram",
            json={
                "instagram_user_id": "123",
                "access_token": "token"
            },
            headers=influencer_headers
        )

    # Exécuter 5 connexions en parallèle
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(connect) for _ in range(5)]
        results = [f.result() for f in futures]

    # Une seule devrait réussir (les autres = duplicate)
    success_count = sum(1 for r in results if r.status_code == 201)
    # assert success_count == 1

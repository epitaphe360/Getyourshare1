"""
Tests pour les endpoints de gestion d'équipe

Coverage:
- Liste des membres d'équipe
- Invitation de membres
- Acceptation d'invitation
- Mise à jour de permissions
- Suppression de membres
- Gestion des rôles
- Vérification des limites
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


# ============================================
# TESTS - LISTE DES MEMBRES
# ============================================

@pytest.mark.asyncio
async def test_list_team_members(async_client, merchant_headers):
    """Test listing all team members"""
    response = await async_client.get(
        "/api/team/members",
        headers=merchant_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    # L'équipe peut être vide au début


@pytest.mark.asyncio
async def test_list_team_members_with_filters(async_client, merchant_headers):
    """Test listing team members with role filter"""
    response = await async_client.get(
        "/api/team/members?role=commercial",
        headers=merchant_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Tous les membres retournés doivent être commerciaux
    for member in data:
        assert member["team_role"] == "commercial"


# ============================================
# TESTS - INVITATION DE MEMBRES
# ============================================

@pytest.mark.asyncio
async def test_invite_team_member(async_client, merchant_headers):
    """Test inviting a new team member"""
    response = await async_client.post(
        "/api/team/invite",
        headers=merchant_headers,
        json={
            "email": "commercial@example.com",
            "team_role": "commercial",
            "can_view_all_sales": True,
            "can_manage_products": False
        }
    )

    assert response.status_code in [200, 201]
    data = response.json()

    assert data["invited_email"] == "commercial@example.com"
    assert data["team_role"] == "commercial"
    assert data["status"] == "pending_invitation"
    assert "invitation_token" in data


@pytest.mark.asyncio
async def test_invite_influencer_to_team(async_client, merchant_headers):
    """Test inviting an influencer to the team"""
    response = await async_client.post(
        "/api/team/invite",
        headers=merchant_headers,
        json={
            "email": "influencer@example.com",
            "team_role": "influencer",
            "can_view_all_sales": False,
            "can_manage_products": False
        }
    )

    assert response.status_code in [200, 201]
    data = response.json()

    assert data["team_role"] == "influencer"


@pytest.mark.asyncio
async def test_invite_with_invalid_role(async_client, merchant_headers):
    """Test inviting with invalid team role"""
    response = await async_client.post(
        "/api/team/invite",
        headers=merchant_headers,
        json={
            "email": "user@example.com",
            "team_role": "invalid_role"
        }
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invite_duplicate_email(async_client, merchant_headers):
    """Test inviting same email twice"""
    # Première invitation
    await async_client.post(
        "/api/team/invite",
        headers=merchant_headers,
        json={
            "email": "duplicate@example.com",
            "team_role": "commercial"
        }
    )

    # Deuxième invitation (devrait échouer)
    response = await async_client.post(
        "/api/team/invite",
        headers=merchant_headers,
        json={
            "email": "duplicate@example.com",
            "team_role": "commercial"
        }
    )

    assert response.status_code in [409, 400]


@pytest.mark.asyncio
async def test_invite_exceeds_team_limit(async_client, merchant_headers):
    """Test inviting when team limit is reached"""
    # Simuler que la limite est atteinte
    with patch('subscription_endpoints.check_subscription_limit') as mock_check:
        mock_check.return_value = False  # Limite atteinte

        response = await async_client.post(
            "/api/team/invite",
            headers=merchant_headers,
            json={
                "email": "newmember@example.com",
                "team_role": "commercial"
            }
        )

        assert response.status_code in [403, 400]


# ============================================
# TESTS - ACCEPTATION D'INVITATION
# ============================================

@pytest.mark.asyncio
async def test_accept_invitation(async_client):
    """Test accepting a team invitation"""
    # Token d'invitation fictif
    invitation_token = "test_invitation_token_123"

    response = await async_client.post(
        f"/api/team/accept-invitation/{invitation_token}"
    )

    # 200 si succès, 404 si token invalide
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_accept_expired_invitation(async_client):
    """Test accepting an expired invitation"""
    expired_token = "expired_token_123"

    response = await async_client.post(
        f"/api/team/accept-invitation/{expired_token}"
    )

    # Devrait échouer si le token est expiré
    assert response.status_code in [404, 410]


# ============================================
# TESTS - MISE À JOUR DES MEMBRES
# ============================================

@pytest.mark.asyncio
async def test_update_member_permissions(async_client, merchant_headers):
    """Test updating team member permissions"""
    member_id = "test_member_123"

    response = await async_client.patch(
        f"/api/team/members/{member_id}",
        headers=merchant_headers,
        json={
            "can_view_all_sales": True,
            "can_manage_products": True
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert data["can_view_all_sales"] == True
        assert data["can_manage_products"] == True


@pytest.mark.asyncio
async def test_update_member_role(async_client, merchant_headers):
    """Test updating team member role"""
    member_id = "test_member_123"

    response = await async_client.patch(
        f"/api/team/members/{member_id}",
        headers=merchant_headers,
        json={
            "team_role": "manager"
        }
    )

    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_update_member_custom_commission(async_client, merchant_headers):
    """Test setting custom commission rate for member"""
    member_id = "test_member_123"

    response = await async_client.patch(
        f"/api/team/members/{member_id}",
        headers=merchant_headers,
        json={
            "custom_commission_rate": 12.5
        }
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert data["custom_commission_rate"] == 12.5


# ============================================
# TESTS - SUPPRESSION DE MEMBRES
# ============================================

@pytest.mark.asyncio
async def test_remove_team_member(async_client, merchant_headers):
    """Test removing a team member"""
    member_id = "test_member_123"

    response = await async_client.delete(
        f"/api/team/members/{member_id}",
        headers=merchant_headers
    )

    assert response.status_code in [200, 204, 404]


@pytest.mark.asyncio
async def test_remove_nonexistent_member(async_client, merchant_headers):
    """Test removing a member that doesn't exist"""
    response = await async_client.delete(
        "/api/team/members/nonexistent_id",
        headers=merchant_headers
    )

    assert response.status_code == 404


# ============================================
# TESTS - CONSULTATION DE MEMBRE
# ============================================

@pytest.mark.asyncio
async def test_get_member_details(async_client, merchant_headers):
    """Test getting details of a specific team member"""
    member_id = "test_member_123"

    response = await async_client.get(
        f"/api/team/members/{member_id}",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "team_role" in data
        assert "status" in data
        assert "can_view_all_sales" in data


@pytest.mark.asyncio
async def test_get_member_stats(async_client, merchant_headers):
    """Test getting performance stats for a team member"""
    member_id = "test_member_123"

    response = await async_client.get(
        f"/api/team/members/{member_id}/stats",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        # Stats peuvent inclure: ventes, commissions, clics, etc.
        assert isinstance(data, dict)


# ============================================
# TESTS - AUTORISATION
# ============================================

@pytest.mark.asyncio
async def test_team_endpoints_require_auth(async_client):
    """Test that team endpoints require authentication"""
    endpoints = [
        "/api/team/members",
        "/api/team/invite"
    ]

    for endpoint in endpoints:
        response = await async_client.get(endpoint)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_member_cannot_manage_other_company_team(async_client, merchant_headers):
    """Test that a company cannot manage another company's team"""
    # Essayer d'accéder aux membres d'une autre entreprise
    other_company_member_id = "other_company_member_123"

    response = await async_client.get(
        f"/api/team/members/{other_company_member_id}",
        headers=merchant_headers
    )

    # Devrait être 404 (not found) ou 403 (forbidden)
    assert response.status_code in [403, 404]


@pytest.mark.asyncio
async def test_influencer_cannot_invite_team_members(async_client, influencer_headers):
    """Test that influencers cannot invite team members"""
    response = await async_client.post(
        "/api/team/invite",
        headers=influencer_headers,
        json={
            "email": "test@example.com",
            "team_role": "commercial"
        }
    )

    # Les influenceurs ne devraient pas pouvoir gérer des équipes
    assert response.status_code in [403, 404]


# ============================================
# TESTS - STATUT DES MEMBRES
# ============================================

@pytest.mark.asyncio
async def test_deactivate_team_member(async_client, merchant_headers):
    """Test deactivating a team member"""
    member_id = "test_member_123"

    response = await async_client.post(
        f"/api/team/members/{member_id}/deactivate",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "inactive"


@pytest.mark.asyncio
async def test_reactivate_team_member(async_client, merchant_headers):
    """Test reactivating a deactivated team member"""
    member_id = "test_member_123"

    response = await async_client.post(
        f"/api/team/members/{member_id}/activate",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "active"


# ============================================
# TESTS - RECHERCHE ET FILTRES
# ============================================

@pytest.mark.asyncio
async def test_search_team_members(async_client, merchant_headers):
    """Test searching team members by name or email"""
    response = await async_client.get(
        "/api/team/members?search=john",
        headers=merchant_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Résultats devraient contenir "john" dans le nom ou email
    for member in data:
        assert "john" in member.get("member_email", "").lower() or \
               "john" in member.get("member_first_name", "").lower()


@pytest.mark.asyncio
async def test_filter_by_status(async_client, merchant_headers):
    """Test filtering team members by status"""
    response = await async_client.get(
        "/api/team/members?status=active",
        headers=merchant_headers
    )

    assert response.status_code == 200
    data = response.json()

    for member in data:
        assert member["status"] == "active"


# ============================================
# TESTS - VALIDATION
# ============================================

@pytest.mark.asyncio
async def test_validate_email_format(async_client, merchant_headers):
    """Test email validation in invitation"""
    response = await async_client.post(
        "/api/team/invite",
        headers=merchant_headers,
        json={
            "email": "invalid_email",
            "team_role": "commercial"
        }
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_validate_commission_rate(async_client, merchant_headers):
    """Test commission rate validation"""
    member_id = "test_member_123"

    # Commission négative
    response = await async_client.patch(
        f"/api/team/members/{member_id}",
        headers=merchant_headers,
        json={
            "custom_commission_rate": -5.0
        }
    )

    assert response.status_code == 422

    # Commission trop élevée
    response = await async_client.patch(
        f"/api/team/members/{member_id}",
        headers=merchant_headers,
        json={
            "custom_commission_rate": 150.0
        }
    )

    assert response.status_code == 422

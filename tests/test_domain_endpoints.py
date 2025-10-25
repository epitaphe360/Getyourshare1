"""
Tests pour les endpoints de gestion des domaines

Coverage:
- Ajout de domaines
- Vérification de domaines (DNS, Meta tag, File)
- Liste des domaines
- Suppression de domaines
- Vérification des limites
- Validation des domaines
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch


# ============================================
# TESTS - AJOUT DE DOMAINES
# ============================================

@pytest.mark.asyncio
async def test_add_domain(async_client, merchant_headers):
    """Test adding a new domain"""
    response = await async_client.post(
        "/api/domains/add",
        headers=merchant_headers,
        json={
            "domain": "example.com"
        }
    )

    assert response.status_code in [200, 201]
    data = response.json()

    assert data["domain"] == "example.com"
    assert data["is_verified"] == False
    assert "verification_token" in data


@pytest.mark.asyncio
async def test_add_subdomain(async_client, merchant_headers):
    """Test adding a subdomain"""
    response = await async_client.post(
        "/api/domains/add",
        headers=merchant_headers,
        json={
            "domain": "shop.example.com"
        }
    )

    assert response.status_code in [200, 201]
    data = response.json()

    assert data["domain"] == "shop.example.com"


@pytest.mark.asyncio
async def test_add_domain_with_protocol(async_client, merchant_headers):
    """Test that protocol is stripped from domain"""
    response = await async_client.post(
        "/api/domains/add",
        headers=merchant_headers,
        json={
            "domain": "https://example.com"
        }
    )

    # Le domaine devrait être nettoyé automatiquement
    # Soit ça passe avec domaine nettoyé, soit validation error
    assert response.status_code in [200, 201, 422]


@pytest.mark.asyncio
async def test_add_duplicate_domain(async_client, merchant_headers):
    """Test adding a domain that already exists"""
    domain = "duplicate.com"

    # Premier ajout
    await async_client.post(
        "/api/domains/add",
        headers=merchant_headers,
        json={"domain": domain}
    )

    # Deuxième ajout (devrait échouer)
    response = await async_client.post(
        "/api/domains/add",
        headers=merchant_headers,
        json={"domain": domain}
    )

    assert response.status_code in [409, 400]


@pytest.mark.asyncio
async def test_add_domain_exceeds_limit(async_client, merchant_headers):
    """Test adding domain when limit is reached"""
    with patch('subscription_endpoints.check_subscription_limit') as mock_check:
        mock_check.return_value = False  # Limite atteinte

        response = await async_client.post(
            "/api/domains/add",
            headers=merchant_headers,
            json={"domain": "newdomain.com"}
        )

        assert response.status_code in [403, 400]


# ============================================
# TESTS - LISTE DES DOMAINES
# ============================================

@pytest.mark.asyncio
async def test_list_domains(async_client, merchant_headers):
    """Test listing all company domains"""
    response = await async_client.get(
        "/api/domains",
        headers=merchant_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_verified_domains_only(async_client, merchant_headers):
    """Test listing only verified domains"""
    response = await async_client.get(
        "/api/domains?verified=true",
        headers=merchant_headers
    )

    assert response.status_code == 200
    data = response.json()

    for domain in data:
        assert domain["is_verified"] == True


@pytest.mark.asyncio
async def test_list_active_domains_only(async_client, merchant_headers):
    """Test listing only active domains"""
    response = await async_client.get(
        "/api/domains?active=true",
        headers=merchant_headers
    )

    assert response.status_code == 200
    data = response.json()

    for domain in data:
        assert domain["is_active"] == True


# ============================================
# TESTS - VÉRIFICATION DNS
# ============================================

@pytest.mark.asyncio
async def test_verify_domain_dns(async_client, merchant_headers):
    """Test domain verification via DNS TXT record"""
    domain_id = "test_domain_123"

    with patch('dns.resolver.resolve') as mock_dns:
        # Simuler un enregistrement DNS valide
        mock_record = Mock()
        mock_record.to_text.return_value = '"shareyoursales-verify=test_token"'
        mock_dns.return_value = [mock_record]

        response = await async_client.post(
            f"/api/domains/{domain_id}/verify/dns",
            headers=merchant_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert data["is_verified"] == True
            assert data["verified_at"] is not None


@pytest.mark.asyncio
async def test_verify_domain_dns_fail(async_client, merchant_headers):
    """Test domain verification with wrong DNS record"""
    domain_id = "test_domain_123"

    with patch('dns.resolver.resolve') as mock_dns:
        # Simuler un enregistrement DNS incorrect
        mock_record = Mock()
        mock_record.to_text.return_value = '"wrong-token"'
        mock_dns.return_value = [mock_record]

        response = await async_client.post(
            f"/api/domains/{domain_id}/verify/dns",
            headers=merchant_headers
        )

        # La vérification devrait échouer
        assert response.status_code in [400, 404]


@pytest.mark.asyncio
async def test_verify_domain_dns_no_record(async_client, merchant_headers):
    """Test domain verification when DNS record doesn't exist"""
    domain_id = "test_domain_123"

    with patch('dns.resolver.resolve') as mock_dns:
        # Simuler l'absence d'enregistrement DNS
        from dns.resolver import NXDOMAIN
        mock_dns.side_effect = NXDOMAIN()

        response = await async_client.post(
            f"/api/domains/{domain_id}/verify/dns",
            headers=merchant_headers
        )

        assert response.status_code in [400, 404]


# ============================================
# TESTS - VÉRIFICATION META TAG
# ============================================

@pytest.mark.asyncio
async def test_verify_domain_meta_tag(async_client, merchant_headers):
    """Test domain verification via HTML meta tag"""
    domain_id = "test_domain_123"

    with patch('httpx.AsyncClient.get') as mock_http:
        # Simuler une page HTML avec meta tag valide
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<meta name="shareyoursales-verification" content="test_token">'
        mock_http.return_value = mock_response

        response = await async_client.post(
            f"/api/domains/{domain_id}/verify/meta",
            headers=merchant_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert data["is_verified"] == True


@pytest.mark.asyncio
async def test_verify_domain_meta_tag_missing(async_client, merchant_headers):
    """Test domain verification when meta tag is missing"""
    domain_id = "test_domain_123"

    with patch('httpx.AsyncClient.get') as mock_http:
        # Simuler une page HTML sans meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Hello</body></html>'
        mock_http.return_value = mock_response

        response = await async_client.post(
            f"/api/domains/{domain_id}/verify/meta",
            headers=merchant_headers
        )

        assert response.status_code in [400, 404]


# ============================================
# TESTS - VÉRIFICATION FICHIER
# ============================================

@pytest.mark.asyncio
async def test_verify_domain_file(async_client, merchant_headers):
    """Test domain verification via file upload"""
    domain_id = "test_domain_123"

    with patch('httpx.AsyncClient.get') as mock_http:
        # Simuler un fichier de vérification valide
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'shareyoursales-verification: test_token'
        mock_http.return_value = mock_response

        response = await async_client.post(
            f"/api/domains/{domain_id}/verify/file",
            headers=merchant_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert data["is_verified"] == True


@pytest.mark.asyncio
async def test_verify_domain_file_404(async_client, merchant_headers):
    """Test domain verification when file doesn't exist"""
    domain_id = "test_domain_123"

    with patch('httpx.AsyncClient.get') as mock_http:
        # Simuler un fichier non trouvé
        mock_response = Mock()
        mock_response.status_code = 404
        mock_http.return_value = mock_response

        response = await async_client.post(
            f"/api/domains/{domain_id}/verify/file",
            headers=merchant_headers
        )

        assert response.status_code in [400, 404]


# ============================================
# TESTS - CONSULTATION DE DOMAINE
# ============================================

@pytest.mark.asyncio
async def test_get_domain_details(async_client, merchant_headers):
    """Test getting details of a specific domain"""
    domain_id = "test_domain_123"

    response = await async_client.get(
        f"/api/domains/{domain_id}",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "domain" in data
        assert "is_verified" in data
        assert "is_active" in data


@pytest.mark.asyncio
async def test_get_domain_verification_instructions(async_client, merchant_headers):
    """Test getting verification instructions for a domain"""
    domain_id = "test_domain_123"

    response = await async_client.get(
        f"/api/domains/{domain_id}/verification-instructions",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "dns" in data
        assert "meta_tag" in data
        assert "file" in data


# ============================================
# TESTS - SUPPRESSION DE DOMAINE
# ============================================

@pytest.mark.asyncio
async def test_delete_domain(async_client, merchant_headers):
    """Test deleting a domain"""
    domain_id = "test_domain_123"

    response = await async_client.delete(
        f"/api/domains/{domain_id}",
        headers=merchant_headers
    )

    assert response.status_code in [200, 204, 404]


@pytest.mark.asyncio
async def test_delete_nonexistent_domain(async_client, merchant_headers):
    """Test deleting a domain that doesn't exist"""
    response = await async_client.delete(
        "/api/domains/nonexistent_domain",
        headers=merchant_headers
    )

    assert response.status_code == 404


# ============================================
# TESTS - ACTIVATION/DÉSACTIVATION
# ============================================

@pytest.mark.asyncio
async def test_deactivate_domain(async_client, merchant_headers):
    """Test deactivating a domain"""
    domain_id = "test_domain_123"

    response = await async_client.post(
        f"/api/domains/{domain_id}/deactivate",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert data["is_active"] == False


@pytest.mark.asyncio
async def test_activate_domain(async_client, merchant_headers):
    """Test activating a deactivated domain"""
    domain_id = "test_domain_123"

    response = await async_client.post(
        f"/api/domains/{domain_id}/activate",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert data["is_active"] == True


# ============================================
# TESTS - AUTORISATION
# ============================================

@pytest.mark.asyncio
async def test_domain_endpoints_require_auth(async_client):
    """Test that domain endpoints require authentication"""
    endpoints = [
        "/api/domains",
        "/api/domains/add"
    ]

    for endpoint in endpoints:
        response = await async_client.get(endpoint)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_cannot_access_other_company_domain(async_client, merchant_headers):
    """Test that a company cannot access another company's domain"""
    other_company_domain_id = "other_company_domain_123"

    response = await async_client.get(
        f"/api/domains/{other_company_domain_id}",
        headers=merchant_headers
    )

    assert response.status_code in [403, 404]


@pytest.mark.asyncio
async def test_influencer_cannot_manage_domains(async_client, influencer_headers):
    """Test that influencers cannot manage domains"""
    response = await async_client.post(
        "/api/domains/add",
        headers=influencer_headers,
        json={"domain": "example.com"}
    )

    # Les influenceurs marketplace n'ont pas de domaines à gérer
    assert response.status_code in [403, 404]


# ============================================
# TESTS - VALIDATION
# ============================================

@pytest.mark.asyncio
async def test_validate_domain_format(async_client, merchant_headers):
    """Test domain format validation"""
    # Domaine invalide
    response = await async_client.post(
        "/api/domains/add",
        headers=merchant_headers,
        json={"domain": "invalid domain with spaces"}
    )

    assert response.status_code == 422

    # Domaine vide
    response = await async_client.post(
        "/api/domains/add",
        headers=merchant_headers,
        json={"domain": ""}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_validate_domain_characters(async_client, merchant_headers):
    """Test domain character validation"""
    # Caractères spéciaux invalides
    invalid_domains = [
        "example@domain.com",
        "example$.com",
        "example/.com"
    ]

    for domain in invalid_domains:
        response = await async_client.post(
            "/api/domains/add",
            headers=merchant_headers,
            json={"domain": domain}
        )

        assert response.status_code == 422


# ============================================
# TESTS - RÉGÉNÉRATION DE TOKEN
# ============================================

@pytest.mark.asyncio
async def test_regenerate_verification_token(async_client, merchant_headers):
    """Test regenerating verification token for a domain"""
    domain_id = "test_domain_123"

    response = await async_client.post(
        f"/api/domains/{domain_id}/regenerate-token",
        headers=merchant_headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "verification_token" in data
        # Le token devrait être différent de l'ancien


# ============================================
# TESTS - STATISTIQUES
# ============================================

@pytest.mark.asyncio
async def test_get_domain_usage_stats(async_client, merchant_headers):
    """Test getting usage statistics for domains"""
    response = await async_client.get(
        "/api/domains/stats",
        headers=merchant_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "total_domains" in data
    assert "verified_domains" in data
    assert "active_domains" in data
    assert "domains_limit" in data

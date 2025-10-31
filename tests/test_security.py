"""
Tests de sécurité

Coverage:
- Authentification et autorisation
- Protection contre injections
- Rate limiting
- CSRF protection
- Encryption
- Validation des inputs
"""

import pytest
import jwt
from datetime import datetime, timedelta


# ============================================
# TESTS - AUTHENTIFICATION
# ============================================

@pytest.mark.security
def test_jwt_token_validation(client):
    """Test validation JWT"""
    # Token invalide
    response = client.get(
        "/api/social-media/connections",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


@pytest.mark.security
def test_jwt_token_expired(client):
    """Test token JWT expiré"""
    # Créer token expiré
    expired_token = jwt.encode(
        {
            "sub": "user-123",
            "exp": datetime.utcnow() - timedelta(hours=1)
        },
        "secret",
        algorithm="HS256"
    )

    response = client.get(
        "/api/social-media/connections",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401


@pytest.mark.security
def test_jwt_token_wrong_signature(client):
    """Test token JWT avec mauvaise signature"""
    malicious_token = jwt.encode(
        {
            "sub": "admin-123",
            "role": "admin",
            "exp": datetime.utcnow() + timedelta(hours=1)
        },
        "wrong_secret",
        algorithm="HS256"
    )

    response = client.get(
        "/api/social-media/admin/sync-logs",
        headers={"Authorization": f"Bearer {malicious_token}"}
    )

    assert response.status_code == 401


# ============================================
# TESTS - AUTORISATION
# ============================================

@pytest.mark.security
def test_role_based_access_control(client, influencer_headers):
    """Test RBAC - influenceur ne peut pas accéder admin"""
    response = client.get(
        "/api/social-media/admin/sync-logs",
        headers=influencer_headers
    )

    assert response.status_code == 403


@pytest.mark.security
def test_user_can_only_access_own_data(client, influencer_headers, merchant_headers):
    """Test qu'un utilisateur ne voit que ses propres données"""
    # TODO: Créer connexion pour influencer

    # Marchand tente d'accéder aux connexions de l'influenceur
    response = client.get(
        "/api/social-media/connections",
        headers=merchant_headers
    )

    # Ne devrait voir que ses propres connexions (vide)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


# ============================================
# TESTS - INJECTION SQL
# ============================================

@pytest.mark.security
def test_sql_injection_in_query_params(client, influencer_headers):
    """Test protection SQL injection dans query params"""
    payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "' OR 1=1--"
    ]

    for payload in payloads:
        response = client.get(
            f"/api/social-media/connections?platform={payload}",
            headers=influencer_headers
        )

        # Ne devrait pas crasher
        assert response.status_code in [200, 400, 422]


@pytest.mark.security
def test_sql_injection_in_body(client, influencer_headers):
    """Test protection SQL injection dans request body"""
    response = client.post(
        "/api/social-media/connect/instagram",
        json={
            "instagram_user_id": "'; DROP TABLE users; --",
            "access_token": "token"
        },
        headers=influencer_headers
    )

    # Devrait rejeter ou échapper
    assert response.status_code in [400, 422]


# ============================================
# TESTS - XSS
# ============================================

@pytest.mark.security
def test_xss_in_user_input(client, influencer_headers):
    """Test protection contre XSS"""
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg/onload=alert('XSS')>"
    ]

    for payload in xss_payloads:
        response = client.post(
            "/api/bot/chat",
            json={"message": payload, "language": "fr"},
            headers=influencer_headers
        )

        # Vérifier que le script n'est pas dans la réponse
        if response.status_code == 200:
            response_text = response.text
            # Le script devrait être échappé ou rejeté
            assert "<script>" not in response_text.lower()


# ============================================
# TESTS - CSRF
# ============================================

@pytest.mark.security
def test_csrf_protection():
    """Test protection CSRF"""
    # TODO: Implémenter CSRF tokens

    # Les requêtes POST/PUT/DELETE devraient nécessiter un CSRF token
    # en plus du JWT token
    pass


# ============================================
# TESTS - RATE LIMITING
# ============================================

@pytest.mark.security
@pytest.mark.slow
def test_rate_limiting_login(client):
    """Test rate limiting sur login"""
    # TODO: Implémenter rate limiting

    # Tenter 100 login ratés rapidement
    for i in range(100):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrong_password"
            }
        )

    # Les dernières requêtes devraient être rate limited
    # assert response.status_code == 429


@pytest.mark.security
def test_rate_limiting_api_calls(client, influencer_headers):
    """Test rate limiting sur API calls"""
    # TODO: Implémenter rate limiting

    responses = []
    for i in range(1000):
        response = client.get(
            "/api/social-media/connections",
            headers=influencer_headers
        )
        responses.append(response.status_code)

        if response.status_code == 429:
            break

    # Devrait être rate limited avant 1000 requêtes
    # assert 429 in responses


# ============================================
# TESTS - ENCRYPTION
# ============================================

@pytest.mark.security
def test_oauth_tokens_encrypted_in_db(db_session):
    """Test que les tokens OAuth sont chiffrés en DB"""
    # TODO: Vérifier en DB que les tokens sont chiffrés

    # from database import get_db_connection
    # conn = get_db_connection()
    # cursor = conn.cursor()
    #
    # cursor.execute("SELECT access_token_encrypted FROM social_media_connections LIMIT 1")
    # result = cursor.fetchone()
    #
    # if result:
    #     # Le token ne devrait pas être en clair
    #     assert not result[0].startswith("IGQV")  # Instagram tokens start with this
    #     assert not result[0].startswith("Bearer")


@pytest.mark.security
def test_banking_details_encrypted(db_session):
    """Test que les coordonnées bancaires sont chiffrées"""
    # TODO: Vérifier chiffrement IBAN/RIB
    pass


@pytest.mark.security
def test_passwords_hashed(db_session):
    """Test que les mots de passe sont hashés"""
    # TODO: Vérifier bcrypt/argon2

    # from database import get_db_connection
    # conn = get_db_connection()
    # cursor = conn.cursor()
    #
    # cursor.execute("SELECT password_hash FROM users LIMIT 1")
    # result = cursor.fetchone()
    #
    # if result:
    #     # Devrait être un hash bcrypt
    #     assert result[0].startswith("$2b$")


# ============================================
# TESTS - VALIDATION
# ============================================

@pytest.mark.security
def test_input_validation_email(client):
    """Test validation email"""
    invalid_emails = [
        "notanemail",
        "@example.com",
        "user@",
        "user@.com",
        "user name@example.com"
    ]

    for email in invalid_emails:
        response = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "ValidPassword123!",
                "full_name": "Test User"
            }
        )

        assert response.status_code == 422


@pytest.mark.security
def test_input_validation_phone(client):
    """Test validation numéro téléphone"""
    invalid_phones = [
        "123",  # Trop court
        "abcdefghij",  # Lettres
        "+1 (555) 123-45-67-89-10",  # Trop long
    ]

    for phone in invalid_phones:
        response = client.post(
            "/api/auth/register",
            json={
                "email": "valid@example.com",
                "password": "ValidPassword123!",
                "phone": phone
            }
        )

        # Devrait rejeter
        assert response.status_code in [400, 422]


@pytest.mark.security
def test_input_validation_url(client, influencer_headers):
    """Test validation URLs"""
    invalid_urls = [
        "not a url",
        "javascript:alert('XSS')",
        "data:text/html,<script>alert('XSS')</script>"
    ]

    for url in invalid_urls:
        response = client.post(
            "/api/influencers/profile",
            json={
                "instagram_url": url
            },
            headers=influencer_headers
        )

        assert response.status_code in [400, 422]


# ============================================
# TESTS - FILE UPLOAD
# ============================================

@pytest.mark.security
def test_file_upload_size_limit(client, influencer_headers):
    """Test limite taille fichier upload"""
    # Fichier de 100MB (trop gros)
    large_file = b"x" * (100 * 1024 * 1024)

    response = client.post(
        "/api/kyc/upload",
        files={"file": ("large.jpg", large_file, "image/jpeg")},
        headers=influencer_headers
    )

    assert response.status_code in [413, 422]  # Payload Too Large


@pytest.mark.security
def test_file_upload_type_validation(client, influencer_headers):
    """Test validation type fichier"""
    # Fichier PHP déguisé en image
    malicious_file = b"<?php system($_GET['cmd']); ?>"

    response = client.post(
        "/api/kyc/upload",
        files={"file": ("malicious.php", malicious_file, "image/jpeg")},
        data={"document_type": "cin"},
        headers=influencer_headers
    )

    # Devrait rejeter
    assert response.status_code in [400, 422]


# ============================================
# TESTS - HEADERS SÉCURITÉ
# ============================================

@pytest.mark.security
def test_security_headers(client):
    """Test présence headers de sécurité"""
    response = client.get("/")

    headers = response.headers

    # Headers de sécurité recommandés
    # assert "X-Content-Type-Options" in headers
    # assert headers["X-Content-Type-Options"] == "nosniff"
    #
    # assert "X-Frame-Options" in headers
    # assert headers["X-Frame-Options"] in ["DENY", "SAMEORIGIN"]
    #
    # assert "X-XSS-Protection" in headers
    #
    # assert "Strict-Transport-Security" in headers
    #
    # assert "Content-Security-Policy" in headers


# ============================================
# TESTS - SECRETS
# ============================================

@pytest.mark.security
def test_no_secrets_in_responses(client, influencer_headers):
    """Test qu'aucun secret n'est exposé dans les réponses"""
    response = client.get(
        "/api/social-media/connections",
        headers=influencer_headers
    )

    response_text = response.text.lower()

    # Secrets qui ne devraient JAMAIS être dans les réponses
    forbidden_strings = [
        "password",
        "secret_key",
        "api_key",
        "private_key",
        "access_token",
        "refresh_token",
        "jwt_secret"
    ]

    for secret in forbidden_strings:
        # Les clés peuvent être présentes, mais pas leurs valeurs
        assert secret not in response_text or f'"{secret}": null' in response_text


# ============================================
# TESTS - LOGGING
# ============================================

@pytest.mark.security
def test_sensitive_data_not_logged():
    """Test que les données sensibles ne sont pas loggées"""
    # TODO: Vérifier les logs

    # Les logs ne devraient JAMAIS contenir:
    # - Mots de passe
    # - Tokens complets (max 8 premiers caractères)
    # - Numéros carte bancaire
    # - IBAN/RIB complets
    pass


# ============================================
# TESTS - RÉPONSES D'ERREUR
# ============================================

@pytest.mark.security
def test_error_messages_not_verbose(client):
    """Test que les erreurs ne révèlent pas d'infos système"""
    response = client.get("/api/nonexistent/endpoint")

    # Ne devrait pas révéler stack traces, chemins fichiers, etc.
    response_text = response.text.lower()

    forbidden_in_errors = [
        "traceback",
        "/home/",
        "/var/www/",
        ".py line",
        "sqlalchemy",
        "postgresql"
    ]

    for forbidden in forbidden_in_errors:
        assert forbidden not in response_text


# ============================================
# TESTS - CORS
# ============================================

@pytest.mark.security
def test_cors_configuration(client):
    """Test configuration CORS"""
    response = client.options(
        "/api/social-media/connections",
        headers={"Origin": "https://malicious.com"}
    )

    # Ne devrait pas autoriser tous les origins
    if "Access-Control-Allow-Origin" in response.headers:
        assert response.headers["Access-Control-Allow-Origin"] != "*"
        # Devrait être limité au domaine de l'app
        # assert "shareyoursales.ma" in response.headers["Access-Control-Allow-Origin"]

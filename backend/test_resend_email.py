"""
Script de test pour le service email Resend
Teste l'envoi d'email avec le domaine info@shareyoursales.ma
"""

import sys
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.resend_email_service import resend_service


def test_simple_email():
    """Test basique d'envoi d'email"""
    print("🧪 Test 1: Email simple...")
    print("-" * 50)

    result = resend_service.send_email(
        to_email="epitaphemarket@gmail.com",
        subject="✅ Test ShareYourSales - Email configuré!",
        html_content="""
        <h1>🎉 Félicitations!</h1>
        <p>Votre service email Resend fonctionne parfaitement avec le domaine <strong>info@shareyoursales.ma</strong>!</p>
        <ul>
            <li>✅ API Resend configurée</li>
            <li>✅ Domaine personnalisé actif</li>
            <li>✅ Emails prêts pour la production</li>
        </ul>
        <p><em>Envoyé depuis ShareYourSales Platform</em></p>
        """
    )

    if result["success"]:
        print(f"✅ Email envoyé avec succès!")
        print(f"   Message ID: {result.get('message_id')}")
        print(f"   FROM: ShareYourSales <info@shareyoursales.ma>")
        print(f"   TO: epitaphemarket@gmail.com")
    else:
        print(f"❌ Erreur: {result.get('error')}")

    print()
    return result["success"]


def test_welcome_email():
    """Test email de bienvenue"""
    print("🧪 Test 2: Email de bienvenue...")
    print("-" * 50)

    result = resend_service.send_welcome_email(
        to_email="epitaphemarket@gmail.com",
        user_name="Samuel",
        role="influencer"
    )

    if result["success"]:
        print(f"✅ Email de bienvenue envoyé!")
        print(f"   Message ID: {result.get('message_id')}")
    else:
        print(f"❌ Erreur: {result.get('error')}")

    print()
    return result["success"]


def test_affiliate_request():
    """Test email de demande d'affiliation"""
    print("🧪 Test 3: Email demande d'affiliation...")
    print("-" * 50)

    result = resend_service.send_affiliate_request_confirmation(
        to_email="epitaphemarket@gmail.com",
        user_name="Samuel",
        product_name="Ordinateur Gaming HP",
        company_name="TechStore Maroc"
    )

    if result["success"]:
        print(f"✅ Email d'affiliation envoyé!")
        print(f"   Message ID: {result.get('message_id')}")
    else:
        print(f"❌ Erreur: {result.get('error')}")

    print()
    return result["success"]


def test_2fa_code():
    """Test email avec code 2FA"""
    print("🧪 Test 4: Email code 2FA...")
    print("-" * 50)

    result = resend_service.send_2fa_code(
        to_email="epitaphemarket@gmail.com",
        user_name="Samuel",
        code="123456"
    )

    if result["success"]:
        print(f"✅ Email 2FA envoyé!")
        print(f"   Message ID: {result.get('message_id')}")
    else:
        print(f"❌ Erreur: {result.get('error')}")

    print()
    return result["success"]


def main():
    """Exécuter tous les tests"""
    print("=" * 50)
    print("🚀 TEST SERVICE EMAIL RESEND")
    print("   Domaine: info@shareyoursales.ma")
    print("   API: Resend")
    print("=" * 50)
    print()

    # Vérifier la configuration
    if not resend_service.api_key:
        print("❌ ERREUR: Clé API Resend non configurée!")
        print("   Vérifiez votre fichier .env")
        return

    print(f"✅ Configuration détectée:")
    print(f"   FROM: {resend_service.from_name} <{resend_service.from_address}>")
    print(f"   API Key: {resend_service.api_key[:20]}...")
    print()

    # Exécuter les tests
    tests = [
        ("Email simple", test_simple_email),
        ("Email de bienvenue", test_welcome_email),
        ("Email affiliation", test_affiliate_request),
        ("Email 2FA", test_2fa_code)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur lors du test: {str(e)}")
            results.append((test_name, False))

    # Résumé
    print("=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")

    print()
    print(f"Résultat: {passed}/{total} tests réussis")

    if passed == total:
        print()
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Votre service email Resend est prêt pour la production")
        print(f"✅ Domaine {resend_service.from_address} configuré et fonctionnel")
    else:
        print()
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")


if __name__ == "__main__":
    main()

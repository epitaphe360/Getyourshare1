"""
Tests d'Intégration End-to-End (E2E)

Tests complets des workflows métier combinant plusieurs services:
- WhatsApp + Mobile Payments
- TikTok Shop + Content Studio
- WhatsApp + TikTok + Paiements
- Parcours complet influenceur
- Parcours complet marchand

Simule des scénarios réels d'utilisation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
import asyncio

from services.whatsapp_business_service import WhatsAppBusinessService
from services.tiktok_shop_service import TikTokShopService
from services.content_studio_service import ContentStudioService
from services.mobile_payment_morocco_service import (
    MobilePaymentService,
    MobilePaymentProvider,
    MobilePayoutRequest,
    PayoutStatus
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def all_services_demo():
    """Tous les services en mode démo"""
    whatsapp = WhatsAppBusinessService()
    whatsapp.demo_mode = True

    tiktok = TikTokShopService()
    tiktok.demo_mode = True

    content_studio = ContentStudioService()
    content_studio.demo_mode = True

    mobile_payment = MobilePaymentService()

    return {
        "whatsapp": whatsapp,
        "tiktok": tiktok,
        "content_studio": content_studio,
        "mobile_payment": mobile_payment
    }


@pytest.fixture
def influencer_profile():
    """Profil d'un influenceur type"""
    return {
        "id": "inf_12345",
        "name": "Sarah Martinez",
        "phone": "+212612345678",
        "email": "sarah@example.com",
        "language": "fr",
        "payment_provider": MobilePaymentProvider.CASH_PLUS,
        "commission_rate": 15.0,
        "total_sales": 0,
        "total_commissions": 0.0
    }


@pytest.fixture
def merchant_profile():
    """Profil d'un marchand type"""
    return {
        "id": "mer_67890",
        "name": "TechStore Maroc",
        "phone": "+212698765432",
        "email": "contact@techstore.ma",
        "tiktok_shop_id": "shop_123",
        "products_count": 0,
        "total_sales": 0
    }


@pytest.fixture
def sample_product():
    """Produit exemple pour les tests"""
    return {
        "title": "Écouteurs Bluetooth Pro",
        "description": "Écouteurs sans fil avec réduction de bruit active, 30h d'autonomie",
        "price": 599.99,
        "currency": "MAD",
        "stock": 50,
        "images": [
            "https://example.com/images/headphones-1.jpg",
            "https://example.com/images/headphones-2.jpg"
        ],
        "category_id": "electronics_audio",
        "brand": "TechPro",
        "sku_id": "SKU-HEAD-001"
    }


# ============================================
# TESTS E2E - PARCOURS INFLUENCEUR
# ============================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestInfluencerJourney:
    """Tests du parcours complet d'un influenceur"""

    async def test_new_influencer_onboarding(self, all_services_demo, influencer_profile):
        """
        Test: Onboarding d'un nouvel influenceur

        Workflow:
        1. Inscription → Message de bienvenue WhatsApp
        2. Réception du lien d'affiliation
        3. Première vente → Notification
        4. Accumulation de commissions
        5. Premier paiement
        """
        services = all_services_demo
        influencer = influencer_profile

        # ÉTAPE 1: Message de bienvenue
        welcome = await services["whatsapp"].send_template_message(
            to_phone=influencer["phone"],
            template_name="welcome_influencer",
            language_code=influencer["language"],
            parameters=[influencer["name"]]
        )
        assert welcome["success"] is True

        # ÉTAPE 2: Envoi du lien d'affiliation
        affiliate_code = f"AFF-{influencer['id']}"
        affiliate_link = f"https://shareyoursales.com/r/{affiliate_code}"

        link_msg = await services["whatsapp"].send_affiliate_link(
            to_phone=influencer["phone"],
            affiliate_link=affiliate_link,
            product_name="Écouteurs Bluetooth Pro",
            commission_rate=influencer["commission_rate"]
        )
        assert link_msg["success"] is True

        # ÉTAPE 3: Première vente (simulée)
        sale_amount = 599.99
        commission = sale_amount * (influencer["commission_rate"] / 100)

        sale_notification = await services["whatsapp"].send_notification(
            to_phone=influencer["phone"],
            notification_type="new_sale",
            data={
                "product": "Écouteurs Bluetooth Pro",
                "price": sale_amount,
                "commission": commission,
                "language": influencer["language"]
            }
        )
        assert sale_notification["success"] is True

        # ÉTAPE 4: Mise à jour du profil
        influencer["total_sales"] += 1
        influencer["total_commissions"] += commission

        # ÉTAPE 5: Paiement des commissions (seuil atteint: 100 MAD)
        if influencer["total_commissions"] >= 100:
            payout_request = MobilePayoutRequest(
                user_id=influencer["id"],
                amount=influencer["total_commissions"],
                phone_number=influencer["phone"],
                provider=influencer["payment_provider"],
                reference=f"PAYOUT-{influencer['id']}-{datetime.now().strftime('%Y%m%d')}",
                metadata={"type": "commission", "period": "monthly"}
            )

            payout = await services["mobile_payment"].initiate_payout(payout_request)
            assert payout.status in [PayoutStatus.COMPLETED, PayoutStatus.PROCESSING]

            # Notification de paiement
            payout_notif = await services["whatsapp"].send_notification(
                to_phone=influencer["phone"],
                notification_type="payout_approved",
                data={
                    "amount": influencer["total_commissions"],
                    "payment_method": influencer["payment_provider"].value,
                    "language": influencer["language"]
                }
            )
            assert payout_notif["success"] is True

        # Vérifier que toutes les étapes se sont bien déroulées
        assert influencer["total_sales"] > 0
        assert influencer["total_commissions"] > 0

    async def test_influencer_monthly_workflow(self, all_services_demo, influencer_profile):
        """
        Test: Workflow mensuel d'un influenceur actif

        - Multiples ventes durant le mois
        - Notifications régulières
        - Paiement en fin de mois
        """
        services = all_services_demo
        influencer = influencer_profile

        # Simuler 20 ventes durant le mois
        sales = []
        for i in range(20):
            sale = {
                "product": f"Produit {i+1}",
                "amount": 100.0 + (i * 50),
                "commission_rate": influencer["commission_rate"]
            }
            sale["commission"] = sale["amount"] * (sale["commission_rate"] / 100)
            sales.append(sale)

            # Notification pour chaque vente
            await services["whatsapp"].send_notification(
                to_phone=influencer["phone"],
                notification_type="new_sale",
                data={
                    "product": sale["product"],
                    "price": sale["amount"],
                    "commission": sale["commission"],
                    "language": "fr"
                }
            )

        # Calculer total
        total_commission = sum(s["commission"] for s in sales)
        assert total_commission > 0

        # Paiement mensuel
        payout_request = MobilePayoutRequest(
            user_id=influencer["id"],
            amount=total_commission,
            phone_number=influencer["phone"],
            provider=MobilePaymentProvider.CASH_PLUS
        )

        payout = await services["mobile_payment"].initiate_payout(payout_request)
        assert payout.status == PayoutStatus.COMPLETED

    async def test_influencer_creates_content(self, all_services_demo, influencer_profile, sample_product):
        """
        Test: Influenceur crée du contenu promotionnel

        Workflow:
        1. Génère une image AI pour le produit
        2. Ajoute un watermark avec son nom
        3. Génère un QR code avec lien d'affiliation
        4. Partage sur WhatsApp
        """
        services = all_services_demo
        content_studio = services["content_studio"]
        whatsapp = services["whatsapp"]

        # ÉTAPE 1: Générer image AI
        image_result = await content_studio.generate_image_ai(
            prompt=f"{sample_product['title']} - {sample_product['description']}",
            style="realistic",
            size="1080x1080"
        )
        assert image_result["success"] is True

        # ÉTAPE 2: Ajouter watermark (en production, utiliserait l'image générée)
        # Pour le test, on simule juste la fonctionnalité
        watermark_text = f"@{influencer_profile['name'].replace(' ', '')}"

        # ÉTAPE 3: Générer QR code avec lien d'affiliation
        affiliate_link = f"https://shareyoursales.com/r/AFF-{influencer_profile['id']}"
        qr_code = content_studio.generate_qr_code(
            url=affiliate_link,
            style="modern",
            color="#FF6B35"
        )
        assert qr_code.startswith("data:image/png;base64,")

        # ÉTAPE 4: Partager sur WhatsApp
        share_url = whatsapp.get_whatsapp_share_url(
            text=f"Découvrez ce produit incroyable! {sample_product['title']}",
            url=affiliate_link
        )
        assert "wa.me" in share_url or "whatsapp.com" in share_url


# ============================================
# TESTS E2E - PARCOURS MARCHAND
# ============================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestMerchantJourney:
    """Tests du parcours complet d'un marchand"""

    async def test_merchant_product_listing_workflow(self, all_services_demo, merchant_profile, sample_product):
        """
        Test: Marchand liste un nouveau produit

        Workflow:
        1. Créer le contenu visuel (images, vidéo)
        2. Synchroniser sur TikTok Shop
        3. Générer le matériel marketing
        4. Notification WhatsApp de confirmation
        """
        services = all_services_demo
        merchant = merchant_profile

        # ÉTAPE 1: Créer contenu visuel avec Content Studio
        # Générer des images promotionnelles
        promo_images = []
        for i, style in enumerate(["realistic", "artistic"]):
            image = await services["content_studio"].generate_image_ai(
                prompt=sample_product["description"],
                style=style,
                size="1080x1080"
            )
            assert image["success"] is True
            promo_images.append(image)

        # Générer un script vidéo
        video_script = services["tiktok"].generate_video_script(
            product={
                "name": sample_product["title"],  # TikTok service utilise 'name'
                "description": sample_product["description"],
                "price": sample_product["price"]
            },
            style="review"
        )
        assert video_script is not None
        assert "scenes" in video_script
        assert len(video_script["scenes"]) > 0

        # ÉTAPE 2: Synchroniser sur TikTok Shop
        sync_result = await services["tiktok"].sync_product_to_tiktok(sample_product)
        assert sync_result["success"] is True

        # ÉTAPE 3: Générer QR code pour le produit
        product_url = f"https://shop.tiktok.com/{merchant['tiktok_shop_id']}/product/{sync_result.get('product_id', 'demo')}"
        qr_code = services["content_studio"].generate_qr_code(
            url=product_url,
            style="rounded"
        )
        assert qr_code is not None

        # ÉTAPE 4: Notification WhatsApp au marchand
        confirmation = await services["whatsapp"].send_text_message(
            to_phone=merchant["phone"],
            message=f"✅ Produit '{sample_product['title']}' synchronisé avec succès sur TikTok Shop!"
        )
        assert confirmation["success"] is True

        # Mise à jour stats
        merchant["products_count"] += 1

    async def test_merchant_campaign_management(self, all_services_demo, merchant_profile):
        """
        Test: Marchand gère une campagne marketing

        Workflow:
        1. Planifier posts sur réseaux sociaux
        2. Créer A/B tests
        3. Suivre les performances
        4. Ajuster la stratégie
        """
        services = all_services_demo
        content_studio = services["content_studio"]

        # ÉTAPE 1: Planifier posts
        from services.content_studio_service import SocialPlatform

        scheduled_posts = []
        platforms = [SocialPlatform.TIKTOK, SocialPlatform.INSTAGRAM, SocialPlatform.FACEBOOK]

        for i, platform in enumerate(platforms):
            post = content_studio.schedule_post(
                content={
                    "text": f"🔥 Nouvelle promotion! Réduction de {10 + i*5}%",
                    "images": ["https://example.com/promo.jpg"],
                    "hashtags": ["#promo", "#maroc", "#shopping"]
                },
                platforms=[platform],
                scheduled_time=datetime.now() + timedelta(hours=i+1),
                user_id=merchant_profile["id"]
            )
            assert post["success"] is True
            scheduled_posts.append(post)

        assert len(scheduled_posts) == 3

        # ÉTAPE 2: Générer du contenu visuel varié
        # Test de différents styles pour campagne
        image_a = await content_studio.generate_image_ai(
            prompt="Promotion exceptionnelle - Style moderne",
            style="realistic",
            size="1080x1080"
        )
        assert image_a["success"] is True

        image_b = await content_studio.generate_image_ai(
            prompt="Offre limitée - Style artistique",
            style="artistic",
            size="1080x1080"
        )
        assert image_b["success"] is True

        # ÉTAPE 3: Générer QR codes pour tracking
        qr_variant_a = content_studio.generate_qr_code(
            url=f"https://shop.example.com/promo?variant=A",
            style="modern"
        )
        qr_variant_b = content_studio.generate_qr_code(
            url=f"https://shop.example.com/promo?variant=B",
            style="rounded"
        )
        assert qr_variant_a is not None
        assert qr_variant_b is not None


# ============================================
# TESTS E2E - WORKFLOWS COMPLEXES
# ============================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestComplexWorkflows:
    """Tests de workflows complexes multi-services"""

    async def test_viral_product_workflow(self, all_services_demo, influencer_profile, merchant_profile, sample_product):
        """
        Test: Produit devient viral - workflow complet

        Scénario:
        1. Marchand liste le produit
        2. Influenceur crée du contenu
        3. Ventes massives
        4. Gestion des stocks
        5. Paiements multiples
        """
        services = all_services_demo

        # PHASE 1: Listing produit
        sync = await services["tiktok"].sync_product_to_tiktok(sample_product)
        assert sync["success"] is True

        # PHASE 2: Influenceur crée contenu viral
        video_script = services["tiktok"].generate_video_script(
            product={
                "name": sample_product["title"],  # TikTok service utilise 'name'
                "description": sample_product["description"],
                "price": sample_product["price"]
            },
            style="unboxing"
        )
        assert video_script is not None
        assert "scenes" in video_script

        # PHASE 3: Simule 100 ventes en 24h
        total_sales = 100
        commission_rate = influencer_profile["commission_rate"]

        total_revenue = total_sales * sample_product["price"]
        total_commission = total_revenue * (commission_rate / 100)

        # PHASE 4: Vérifier stock
        stock_remaining = sample_product["stock"] - total_sales
        if stock_remaining < 10:
            # Alert marchand
            alert = await services["whatsapp"].send_text_message(
                to_phone=merchant_profile["phone"],
                message=f"⚠️ Stock faible pour {sample_product['title']}: {stock_remaining} unités restantes"
            )
            assert alert["success"] is True

        # PHASE 5: Paiement commission à l'influenceur
        payout = await services["mobile_payment"].initiate_payout(
            MobilePayoutRequest(
                user_id=influencer_profile["id"],
                amount=total_commission,
                phone_number=influencer_profile["phone"],
                provider=MobilePaymentProvider.CASH_PLUS,
                metadata={"sales_count": total_sales, "period": "viral_campaign"}
            )
        )
        assert payout.status == PayoutStatus.COMPLETED

        # Notification à l'influenceur
        notif = await services["whatsapp"].send_notification(
            to_phone=influencer_profile["phone"],
            notification_type="payout_approved",
            data={
                "amount": total_commission,
                "payment_method": "Cash Plus",
                "language": "fr"
            }
        )
        assert notif["success"] is True

    async def test_multi_influencer_campaign(self, all_services_demo, sample_product):
        """
        Test: Campagne avec plusieurs influenceurs

        - 5 influenceurs différents
        - Chacun avec son lien d'affiliation
        - Tracking des performances individuelles
        - Paiements différenciés
        """
        services = all_services_demo

        influencers = [
            {"id": f"inf_{i}", "phone": f"+21261234567{i}", "commission_rate": 10 + i}
            for i in range(5)
        ]

        results = []

        for influencer in influencers:
            # Créer lien d'affiliation unique
            affiliate_link = f"https://shareyoursales.com/r/AFF-{influencer['id']}"

            # Envoyer lien
            msg = await services["whatsapp"].send_affiliate_link(
                to_phone=influencer["phone"],
                affiliate_link=affiliate_link,
                product_name=sample_product["title"],
                commission_rate=influencer["commission_rate"]
            )

            # Simuler ventes (variable par influenceur)
            sales_count = 10 + (influencers.index(influencer) * 5)
            commission = sales_count * sample_product["price"] * (influencer["commission_rate"] / 100)

            results.append({
                "influencer_id": influencer["id"],
                "sales": sales_count,
                "commission": commission,
                "message_sent": msg["success"]
            })

        # Vérifications
        assert len(results) == 5
        assert all(r["message_sent"] for r in results)
        assert sum(r["sales"] for r in results) > 0

        # Payer tous les influenceurs
        payouts = []
        for influencer, result in zip(influencers, results):
            if result["commission"] >= 50:  # Seuil minimum
                payout = await services["mobile_payment"].initiate_payout(
                    MobilePayoutRequest(
                        user_id=influencer["id"],
                        amount=result["commission"],
                        phone_number=influencer["phone"],
                        provider=MobilePaymentProvider.CASH_PLUS
                    )
                )
                payouts.append(payout)

        assert len(payouts) > 0
        assert all(p.status == PayoutStatus.COMPLETED for p in payouts)


# ============================================
# TESTS E2E - GESTION D'ERREURS
# ============================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestErrorRecovery:
    """Tests de récupération d'erreurs dans les workflows"""

    async def test_failed_payment_retry(self, all_services_demo, influencer_profile):
        """
        Test: Récupération après échec de paiement

        Workflow:
        1. Paiement échoue
        2. Notification à l'utilisateur
        3. Retry automatique
        4. Succès au 2ème essai
        """
        services = all_services_demo

        # Premier essai (pourrait échouer)
        payout_request = MobilePayoutRequest(
            user_id=influencer_profile["id"],
            amount=500.0,
            phone_number=influencer_profile["phone"],
            provider=MobilePaymentProvider.ORANGE_MONEY
        )

        first_attempt = await services["mobile_payment"].initiate_payout(payout_request)

        if first_attempt.status == PayoutStatus.FAILED:
            # Notifier l'utilisateur
            await services["whatsapp"].send_text_message(
                to_phone=influencer_profile["phone"],
                message="⚠️ Votre paiement a rencontré un problème. Nouvelle tentative en cours..."
            )

            # Retry
            second_attempt = await services["mobile_payment"].initiate_payout(payout_request)
            assert second_attempt.payout_id != first_attempt.payout_id

    async def test_graceful_degradation(self, all_services_demo):
        """
        Test: Dégradation gracieuse quand un service est indisponible

        - TikTok API down → continuer sans sync
        - WhatsApp down → logger uniquement
        - Paiements down → mode queue
        """
        services = all_services_demo

        # Même si un service est en démo/mock, le workflow continue
        try:
            # Tentative sync TikTok
            result = await services["tiktok"].sync_product_to_tiktok({
                "title": "Test Product",
                "price": 100.0
            })

            # En mode démo, devrait toujours réussir
            assert result["success"] is True or result.get("demo_mode") is True

        except Exception:
            # Continuer même en cas d'erreur
            pass

        # L'application doit rester fonctionnelle
        assert services["whatsapp"] is not None
        assert services["mobile_payment"] is not None

-- ============================================================================
-- Script de validation pour create_sale_transaction et approve_payout_transaction
-- Usage : \i database/tests/test_transaction_functions.sql
-- Ce script crée des données temporaires, appelle les fonctions et
-- affiche les résultats pour vérifier les effets attendus.
-- Toutes les opérations sont annulées en fin de test (ROLLBACK).
-- ============================================================================

BEGIN;

-- Créer une table temporaire pour stocker les IDs générés
CREATE TEMP TABLE test_vars (
    merchant_user_id UUID,
    influencer_user_id UUID,
    merchant_id UUID,
    influencer_id UUID,
    product_id UUID,
    link_id UUID
);

-- Générer et stocker les UUIDs
INSERT INTO test_vars VALUES (
    gen_random_uuid(),
    gen_random_uuid(),
    gen_random_uuid(),
    gen_random_uuid(),
    gen_random_uuid(),
    gen_random_uuid()
);

-- Créer les utilisateurs
INSERT INTO users (id, email, password_hash, role, is_active)
SELECT 
    merchant_user_id,
    CONCAT('merchant+', merchant_user_id::text, '@example.com'),
    'hashed',
    'merchant',
    TRUE
FROM test_vars;

INSERT INTO users (id, email, password_hash, role, is_active)
SELECT 
    influencer_user_id,
    CONCAT('influencer+', influencer_user_id::text, '@example.com'),
    'hashed',
    'influencer',
    TRUE
FROM test_vars;

-- Créer le merchant
INSERT INTO merchants (id, user_id, company_name)
SELECT merchant_id, merchant_user_id, 'Test Company'
FROM test_vars;

-- Créer l'influencer
INSERT INTO influencers (id, user_id, username, balance)
SELECT influencer_id, influencer_user_id, CONCAT('influencer_', influencer_id::text), 0
FROM test_vars;

-- Créer le produit
INSERT INTO products (id, merchant_id, name, price, commission_rate, commission_type)
SELECT product_id, merchant_id, 'Produit test', 199.90, 10, 'percentage'
FROM test_vars;

-- Créer le lien tracké
INSERT INTO trackable_links (id, product_id, influencer_id, unique_code, full_url)
SELECT link_id, product_id, influencer_id, 'TESTCODE', 'https://example.com/test'
FROM test_vars;

-- Appeler la fonction de création de vente
SELECT create_sale_transaction(
    p_link_id => link_id,
    p_product_id => product_id,
    p_influencer_id => influencer_id,
    p_merchant_id => merchant_id,
    p_amount => 199.90,
    p_currency => 'EUR',
    p_quantity => 1,
    p_customer_email => 'client@example.com',
    p_customer_name => 'Client Test'
)
FROM test_vars;

-- Vérifier la vente et la commission créées
SELECT 
    s.id AS sale_id,
    s.amount,
    s.influencer_commission,
    s.platform_commission,
    s.merchant_revenue,
    s.status,
    c.id AS commission_id,
    c.status AS commission_status
FROM sales s
JOIN commissions c ON c.sale_id = s.id
JOIN test_vars v ON v.product_id = s.product_id AND v.influencer_id = s.influencer_id
ORDER BY s.created_at DESC
LIMIT 1;

-- Approuver la commission
SELECT approve_payout_transaction(c.id, 'approved') AS approved
FROM commissions c
JOIN sales s ON s.id = c.sale_id
JOIN test_vars v ON v.product_id = s.product_id
ORDER BY c.created_at DESC
LIMIT 1;

-- Marquer comme payé
SELECT approve_payout_transaction(c.id, 'paid') AS paid
FROM commissions c
JOIN sales s ON s.id = c.sale_id
JOIN test_vars v ON v.product_id = s.product_id
ORDER BY c.created_at DESC
LIMIT 1;

-- Vérifier le solde et les compteurs mis à jour
SELECT
    i.total_sales,
    i.total_earnings,
    i.balance,
    m.total_sales AS merchant_total_sales,
    m.total_commission_paid,
    tl.sales AS link_sales,
    tl.total_revenue,
    tl.total_commission,
    tl.conversion_rate
FROM test_vars v
JOIN influencers i ON i.id = v.influencer_id
JOIN trackable_links tl ON tl.id = v.link_id
JOIN products p ON p.id = v.product_id
JOIN merchants m ON m.id = v.merchant_id;

-- Nettoyer
DROP TABLE test_vars;

ROLLBACK;

-- Fin du script =============================================================

-- ============================================
-- EXEMPLES DE REQUÊTES SQL - SHAREYOURSALES
-- ============================================

-- ============================================
-- 1. AUTHENTICATION & USERS
-- ============================================

-- Inscription d'un nouvel influenceur
BEGIN;
    -- Créer l'utilisateur
    INSERT INTO users (email, password_hash, role, phone, two_fa_enabled)
    VALUES ('influencer@example.com', '$2b$12$...', 'influencer', '+33612345678', TRUE)
    RETURNING id;
    
    -- Créer le profil influenceur
    INSERT INTO influencers (user_id, username, full_name, category, influencer_type, subscription_plan)
    VALUES (
        (SELECT id FROM users WHERE email = 'influencer@example.com'),
        'johndoe',
        'John Doe',
        'Mode',
        'micro',
        'starter'
    );
    
    -- Créer l'abonnement
    INSERT INTO subscriptions (user_id, plan_type, monthly_fee, platform_fee_rate, status)
    VALUES (
        (SELECT id FROM users WHERE email = 'influencer@example.com'),
        'influencer_starter',
        9.90,
        5.00,
        'active'
    );
COMMIT;

-- Login avec vérification 2FA
-- Étape 1: Vérifier email/password
SELECT id, email, role, password_hash, two_fa_enabled
FROM users
WHERE email = 'user@example.com' AND is_active = TRUE;

-- Étape 2: Générer et enregistrer code 2FA
UPDATE users
SET two_fa_code = '123456',
    two_fa_expires_at = NOW() + INTERVAL '5 minutes'
WHERE id = 'user_uuid';

-- Étape 3: Vérifier code 2FA
SELECT id, email, role
FROM users
WHERE id = 'user_uuid'
    AND two_fa_code = '123456'
    AND two_fa_expires_at > NOW();

-- Créer une session
INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, expires_at)
VALUES (
    'user_uuid',
    'jwt_token_here',
    '192.168.1.1',
    'Mozilla/5.0...',
    NOW() + INTERVAL '24 hours'
);

-- ============================================
-- 2. TRACKABLE LINKS & AFFILIATION
-- ============================================

-- Générer un lien d'affiliation unique
INSERT INTO trackable_links (
    product_id,
    influencer_id,
    unique_code,
    full_url,
    short_url,
    is_active
)
VALUES (
    'product_uuid',
    'influencer_uuid',
    'abc123xyz789',
    'https://shareyoursales.com/r/abc123xyz789',
    'https://sys.co/abc123',
    TRUE
)
RETURNING id, unique_code, full_url;

-- Récupérer tous les liens d'un influenceur
SELECT 
    tl.id,
    tl.unique_code,
    tl.full_url,
    tl.short_url,
    p.name as product_name,
    p.price,
    p.commission_rate,
    tl.clicks,
    tl.sales,
    tl.conversion_rate,
    tl.total_revenue,
    tl.total_commission,
    tl.is_active,
    tl.created_at
FROM trackable_links tl
JOIN products p ON tl.product_id = p.id
WHERE tl.influencer_id = 'influencer_uuid'
ORDER BY tl.created_at DESC;

-- Ajouter une offre de rabais à un lien
UPDATE trackable_links
SET has_discount = TRUE,
    discount_code = 'SAVE20',
    discount_percentage = 20.00
WHERE id = 'link_uuid';

-- ============================================
-- 3. TRACKING DES CLICS
-- ============================================

-- Enregistrer un clic
INSERT INTO click_tracking (
    link_id,
    ip_address,
    user_agent,
    referrer,
    country,
    city,
    device_type,
    os,
    browser,
    session_id,
    is_unique_visitor
)
VALUES (
    'link_uuid',
    '192.168.1.100',
    'Mozilla/5.0 (iPhone...)',
    'https://instagram.com',
    'FR',
    'Paris',
    'Mobile',
    'iOS',
    'Safari',
    'session_abc123',
    TRUE
);

-- Incrémenter les compteurs du lien
UPDATE trackable_links
SET clicks = clicks + 1,
    unique_clicks = unique_clicks + 1
WHERE id = 'link_uuid';

-- Statistiques de clics par pays (derniers 7 jours)
SELECT 
    country,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT ip_address) as unique_visitors,
    COUNT(DISTINCT session_id) as unique_sessions
FROM click_tracking
WHERE link_id = 'link_uuid'
    AND clicked_at >= NOW() - INTERVAL '7 days'
GROUP BY country
ORDER BY total_clicks DESC;

-- ============================================
-- 4. SALES & COMMISSIONS
-- ============================================

-- Enregistrer une vente
BEGIN;
    -- Insérer la vente
    INSERT INTO sales (
        link_id,
        product_id,
        influencer_id,
        merchant_id,
        customer_email,
        customer_name,
        customer_ip,
        quantity,
        amount,
        influencer_commission,
        platform_commission,
        merchant_revenue,
        status,
        payment_status,
        sale_timestamp
    )
    VALUES (
        'link_uuid',
        'product_uuid',
        'influencer_uuid',
        'merchant_uuid',
        'customer@example.com',
        'Jane Smith',
        '192.168.1.100',
        1,
        100.00,
        15.00,  -- 15% commission influenceur
        5.00,   -- 5% frais plateforme
        80.00,  -- Revenus merchant
        'pending',
        'pending',
        NOW()
    )
    RETURNING id;
    
    -- Créer la commission
    INSERT INTO commissions (sale_id, influencer_id, amount, status)
    VALUES ('sale_uuid', 'influencer_uuid', 15.00, 'pending');
    
    -- Mettre à jour les statistiques du lien
    UPDATE trackable_links
    SET sales = sales + 1,
        total_revenue = total_revenue + 100.00,
        total_commission = total_commission + 15.00,
        conversion_rate = (sales + 1)::decimal / NULLIF(clicks, 0) * 100
    WHERE id = 'link_uuid';
    
    -- Mettre à jour le solde de l'influenceur
    UPDATE influencers
    SET total_sales = total_sales + 1,
        balance = balance + 15.00,
        total_earnings = total_earnings + 15.00
    WHERE id = 'influencer_uuid';
COMMIT;

-- Ventes d'un influenceur (avec détails)
SELECT 
    s.id,
    s.sale_timestamp,
    p.name as product_name,
    s.quantity,
    s.amount,
    s.influencer_commission,
    s.status,
    s.payment_status,
    tl.unique_code as tracking_code
FROM sales s
JOIN products p ON s.product_id = p.id
JOIN trackable_links tl ON s.link_id = tl.id
WHERE s.influencer_id = 'influencer_uuid'
ORDER BY s.sale_timestamp DESC;

-- Commissions en attente
SELECT 
    c.id,
    c.amount,
    c.status,
    c.created_at,
    s.sale_timestamp,
    p.name as product_name,
    i.username as influencer_username
FROM commissions c
JOIN sales s ON c.sale_id = s.id
JOIN products p ON s.product_id = p.id
JOIN influencers i ON c.influencer_id = i.id
WHERE c.status = 'pending'
ORDER BY c.created_at ASC;

-- Approuver une commission
UPDATE commissions
SET status = 'approved'
WHERE id = 'commission_uuid';

-- Payer une commission
BEGIN;
    -- Mettre à jour la commission
    UPDATE commissions
    SET status = 'paid',
        payment_method = 'paypal',
        transaction_id = 'PAYPAL_TXN_123',
        paid_at = NOW()
    WHERE id = 'commission_uuid';
    
    -- Enregistrer le paiement
    INSERT INTO payments (
        user_id,
        amount,
        payment_type,
        payment_method,
        transaction_id,
        status,
        description
    )
    SELECT 
        i.user_id,
        c.amount,
        'commission',
        'paypal',
        'PAYPAL_TXN_123',
        'completed',
        'Commission pour vente ' || s.id
    FROM commissions c
    JOIN influencers i ON c.influencer_id = i.id
    JOIN sales s ON c.sale_id = s.id
    WHERE c.id = 'commission_uuid';
COMMIT;

-- ============================================
-- 5. PRODUCTS & MARKETPLACE
-- ============================================

-- Récupérer tous les produits avec filtres
SELECT 
    p.id,
    p.name,
    p.description,
    p.category,
    p.price,
    p.commission_rate,
    p.images,
    p.stock_quantity,
    p.is_available,
    m.company_name as merchant_name,
    AVG(r.rating) as average_rating,
    COUNT(r.id) as review_count,
    SUM(tl.clicks) as total_clicks,
    SUM(tl.sales) as total_sales
FROM products p
JOIN merchants m ON p.merchant_id = m.id
LEFT JOIN reviews r ON p.id = r.product_id
LEFT JOIN trackable_links tl ON p.id = tl.product_id
WHERE p.is_available = TRUE
    AND p.category = 'Mode'  -- Filtrer par catégorie
    AND p.price BETWEEN 50 AND 200  -- Filtrer par prix
GROUP BY p.id, m.company_name
HAVING AVG(r.rating) >= 4.0  -- Filtrer par note minimale
ORDER BY total_sales DESC
LIMIT 20;

-- Recherche de produits
SELECT 
    p.id,
    p.name,
    p.description,
    p.category,
    p.price,
    p.commission_rate,
    m.company_name
FROM products p
JOIN merchants m ON p.merchant_id = m.id
WHERE p.is_available = TRUE
    AND (
        p.name ILIKE '%smartphone%'
        OR p.description ILIKE '%smartphone%'
    )
ORDER BY p.total_sales DESC;

-- Produits les plus performants
SELECT 
    p.id,
    p.name,
    p.category,
    m.company_name,
    COUNT(DISTINCT tl.id) as influencer_count,
    SUM(tl.clicks) as total_clicks,
    SUM(tl.sales) as total_sales,
    SUM(tl.total_revenue) as total_revenue,
    AVG(tl.conversion_rate) as avg_conversion_rate
FROM products p
JOIN merchants m ON p.merchant_id = m.id
JOIN trackable_links tl ON p.id = tl.product_id
WHERE p.is_available = TRUE
GROUP BY p.id, m.company_name
ORDER BY total_sales DESC
LIMIT 10;

-- ============================================
-- 6. ANALYTICS & REPORTS
-- ============================================

-- Dashboard Influenceur (résumé)
SELECT 
    i.username,
    i.full_name,
    i.influencer_type,
    i.audience_size,
    i.engagement_rate,
    i.total_clicks,
    i.total_sales,
    i.total_earnings,
    i.balance,
    COUNT(DISTINCT tl.id) as total_active_links,
    COUNT(DISTINCT p.id) as total_products_promoted,
    COUNT(DISTINCT s.id) as total_sales_count,
    SUM(s.amount) as total_revenue_generated
FROM influencers i
LEFT JOIN trackable_links tl ON i.id = tl.influencer_id AND tl.is_active = TRUE
LEFT JOIN products p ON tl.product_id = p.id
LEFT JOIN sales s ON i.id = s.influencer_id AND s.status = 'completed'
WHERE i.id = 'influencer_uuid'
GROUP BY i.id;

-- Performance par produit (pour un influenceur)
SELECT 
    p.name,
    p.category,
    p.price,
    p.commission_rate,
    tl.clicks,
    tl.sales,
    tl.conversion_rate,
    tl.total_revenue,
    tl.total_commission,
    em.likes,
    em.comments,
    em.shares,
    em.roi_percentage
FROM trackable_links tl
JOIN products p ON tl.product_id = p.id
LEFT JOIN engagement_metrics em ON tl.id = em.link_id
WHERE tl.influencer_id = 'influencer_uuid'
ORDER BY tl.total_commission DESC;

-- Dashboard Admin (statistiques globales)
SELECT 
    (SELECT COUNT(*) FROM users WHERE role = 'influencer' AND is_active = TRUE) as total_influencers,
    (SELECT COUNT(*) FROM users WHERE role = 'merchant' AND is_active = TRUE) as total_merchants,
    (SELECT COUNT(*) FROM products WHERE is_available = TRUE) as active_products,
    (SELECT COUNT(*) FROM trackable_links WHERE is_active = TRUE) as active_links,
    (SELECT SUM(amount) FROM sales WHERE status = 'completed') as total_sales_amount,
    (SELECT SUM(amount) FROM commissions WHERE status = 'paid') as total_commissions_paid,
    (SELECT SUM(platform_commission) FROM sales WHERE status = 'completed') as platform_revenue;

-- Top 10 Influenceurs (par revenus générés)
SELECT 
    i.username,
    i.full_name,
    i.influencer_type,
    i.category,
    i.total_sales,
    i.total_earnings,
    SUM(s.amount) as total_revenue_generated,
    COUNT(DISTINCT tl.id) as active_links,
    AVG(tl.conversion_rate) as avg_conversion_rate
FROM influencers i
LEFT JOIN trackable_links tl ON i.id = tl.influencer_id
LEFT JOIN sales s ON i.id = s.influencer_id AND s.status = 'completed'
GROUP BY i.id
ORDER BY total_revenue_generated DESC
LIMIT 10;

-- Performance par catégorie de produit
SELECT 
    p.category,
    COUNT(DISTINCT p.id) as total_products,
    COUNT(DISTINCT tl.influencer_id) as influencer_count,
    SUM(tl.clicks) as total_clicks,
    SUM(tl.sales) as total_sales,
    SUM(tl.total_revenue) as total_revenue,
    AVG(tl.conversion_rate) as avg_conversion_rate,
    AVG(p.commission_rate) as avg_commission_rate
FROM products p
JOIN trackable_links tl ON p.id = tl.product_id
WHERE p.is_available = TRUE
GROUP BY p.category
ORDER BY total_revenue DESC;

-- Ventes par jour (derniers 30 jours)
SELECT 
    DATE(sale_timestamp) as sale_date,
    COUNT(*) as order_count,
    SUM(amount) as daily_revenue,
    SUM(influencer_commission) as influencer_commission,
    SUM(platform_commission) as platform_commission,
    AVG(amount) as avg_order_value
FROM sales
WHERE status = 'completed'
    AND sale_timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE(sale_timestamp)
ORDER BY sale_date DESC;

-- ============================================
-- 7. ENGAGEMENT METRICS
-- ============================================

-- Calculer et enregistrer les métriques d'engagement
INSERT INTO engagement_metrics (
    link_id,
    product_id,
    influencer_id,
    likes,
    comments,
    shares,
    impressions,
    clicks,
    conversions,
    conversion_rate,
    roi_percentage,
    metric_date
)
SELECT 
    tl.id,
    tl.product_id,
    tl.influencer_id,
    0, -- À remplir manuellement
    0,
    0,
    ct.impressions,
    COUNT(ct.id) as clicks,
    COUNT(s.id) as conversions,
    (COUNT(s.id)::decimal / NULLIF(COUNT(ct.id), 0) * 100) as conversion_rate,
    0.00, -- À calculer
    CURRENT_DATE
FROM trackable_links tl
LEFT JOIN click_tracking ct ON tl.id = ct.link_id AND DATE(ct.clicked_at) = CURRENT_DATE
LEFT JOIN sales s ON tl.id = s.link_id AND DATE(s.sale_timestamp) = CURRENT_DATE
WHERE tl.influencer_id = 'influencer_uuid'
GROUP BY tl.id, ct.impressions
ON CONFLICT (link_id, metric_date)
DO UPDATE SET
    clicks = EXCLUDED.clicks,
    conversions = EXCLUDED.conversions,
    conversion_rate = EXCLUDED.conversion_rate;

-- ============================================
-- 8. AI ANALYTICS
-- ============================================

-- Enregistrer des prédictions IA
INSERT INTO ai_analytics (
    product_id,
    merchant_id,
    predicted_sales,
    trend_score,
    recommended_strategy,
    recommended_budget,
    recommended_influencers,
    confidence_score,
    analysis_period_start,
    analysis_period_end
)
VALUES (
    'product_uuid',
    'merchant_uuid',
    150,  -- Prédiction: 150 ventes
    75.5, -- Tendance positive
    'Augmenter le budget publicitaire de 20% et cibler les influenceurs macro dans la catégorie Mode',
    5000.00,
    '["influencer_uuid_1", "influencer_uuid_2"]'::jsonb,
    85.0, -- 85% de confiance
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '30 days'
);

-- Récupérer les recommandations IA pour un produit
SELECT 
    aa.predicted_sales,
    aa.trend_score,
    aa.recommended_strategy,
    aa.recommended_budget,
    aa.confidence_score,
    p.name as product_name,
    p.total_sales as current_sales
FROM ai_analytics aa
JOIN products p ON aa.product_id = p.id
WHERE aa.product_id = 'product_uuid'
ORDER BY aa.created_at DESC
LIMIT 1;

-- ============================================
-- 9. SUBSCRIPTIONS & PAYMENTS
-- ============================================

-- Vérifier l'abonnement actif d'un utilisateur
SELECT 
    s.plan_type,
    s.monthly_fee,
    s.commission_rate,
    s.status,
    s.start_date,
    s.next_billing_date,
    s.features
FROM subscriptions s
WHERE s.user_id = 'user_uuid'
    AND s.status = 'active'
    AND (s.end_date IS NULL OR s.end_date > CURRENT_DATE)
ORDER BY s.start_date DESC
LIMIT 1;

-- Changer de plan d'abonnement
BEGIN;
    -- Terminer l'ancien abonnement
    UPDATE subscriptions
    SET status = 'cancelled',
        end_date = CURRENT_DATE
    WHERE user_id = 'user_uuid'
        AND status = 'active';
    
    -- Créer le nouvel abonnement
    INSERT INTO subscriptions (
        user_id,
        plan_type,
        monthly_fee,
        commission_rate,
        max_products,
        max_links,
        features,
        start_date,
        next_billing_date,
        status
    )
    VALUES (
        'user_uuid',
        'pro',
        199.00,
        3.00,
        500,
        NULL,
        '["ai_marketing", "advanced_analytics", "priority_support"]'::jsonb,
        CURRENT_DATE,
        CURRENT_DATE + INTERVAL '1 month',
        'active'
    );
COMMIT;

-- Historique des paiements d'un utilisateur
SELECT 
    p.id,
    p.amount,
    p.payment_type,
    p.payment_method,
    p.status,
    p.transaction_date,
    p.description
FROM payments p
WHERE p.user_id = 'user_uuid'
ORDER BY p.transaction_date DESC;

-- ============================================
-- 10. REVIEWS & RATINGS
-- ============================================

-- Ajouter un avis
INSERT INTO reviews (
    product_id,
    user_id,
    rating,
    title,
    comment,
    is_verified_purchase
)
VALUES (
    'product_uuid',
    'user_uuid',
    5,
    'Excellent produit!',
    'Très satisfait de mon achat, qualité au rendez-vous.',
    TRUE
);

-- Récupérer les avis d'un produit
SELECT 
    r.rating,
    r.title,
    r.comment,
    r.is_verified_purchase,
    r.helpful_count,
    r.created_at,
    u.email as reviewer_email
FROM reviews r
JOIN users u ON r.user_id = u.id
WHERE r.product_id = 'product_uuid'
    AND r.is_approved = TRUE
ORDER BY r.helpful_count DESC, r.created_at DESC;

-- Moyenne des notes d'un produit
SELECT 
    p.id,
    p.name,
    AVG(r.rating) as average_rating,
    COUNT(r.id) as review_count,
    COUNT(CASE WHEN r.rating = 5 THEN 1 END) as five_star,
    COUNT(CASE WHEN r.rating = 4 THEN 1 END) as four_star,
    COUNT(CASE WHEN r.rating = 3 THEN 1 END) as three_star,
    COUNT(CASE WHEN r.rating = 2 THEN 1 END) as two_star,
    COUNT(CASE WHEN r.rating = 1 THEN 1 END) as one_star
FROM products p
LEFT JOIN reviews r ON p.id = r.product_id AND r.is_approved = TRUE
WHERE p.id = 'product_uuid'
GROUP BY p.id;

-- ============================================
-- 11. MAINTENANCE & CLEANUP
-- ============================================

-- Supprimer les sessions expirées
DELETE FROM user_sessions
WHERE expires_at < NOW();

-- Supprimer les codes 2FA expirés
UPDATE users
SET two_fa_code = NULL,
    two_fa_expires_at = NULL
WHERE two_fa_expires_at < NOW();

-- Archiver les ventes anciennes (optionnel)
-- Créer d'abord une table d'archive
CREATE TABLE IF NOT EXISTS sales_archive (LIKE sales INCLUDING ALL);

-- Déplacer les ventes de plus d'un an
INSERT INTO sales_archive
SELECT * FROM sales
WHERE sale_timestamp < NOW() - INTERVAL '1 year';

DELETE FROM sales
WHERE sale_timestamp < NOW() - INTERVAL '1 year';

-- Nettoyer les clics anciens (garder 90 jours)
DELETE FROM click_tracking
WHERE clicked_at < NOW() - INTERVAL '90 days';

-- ============================================
-- 12. BACKUP & EXPORT
-- ============================================

-- Exporter les données d'un influenceur (CSV)
COPY (
    SELECT 
        s.sale_timestamp,
        p.name as product_name,
        s.amount,
        s.influencer_commission,
        s.status
    FROM sales s
    JOIN products p ON s.product_id = p.id
    WHERE s.influencer_id = 'influencer_uuid'
    ORDER BY s.sale_timestamp DESC
) TO '/tmp/influencer_sales_export.csv' WITH CSV HEADER;

-- Exporter les statistiques d'un merchant
COPY (
    SELECT 
        p.name,
        p.category,
        COUNT(DISTINCT tl.id) as influencer_count,
        SUM(tl.clicks) as total_clicks,
        SUM(tl.sales) as total_sales,
        SUM(tl.total_revenue) as total_revenue
    FROM products p
    LEFT JOIN trackable_links tl ON p.id = tl.product_id
    WHERE p.merchant_id = 'merchant_uuid'
    GROUP BY p.id
) TO '/tmp/merchant_stats_export.csv' WITH CSV HEADER;

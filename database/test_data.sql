-- ============================================
-- DONNÉES DE TEST - SHAREYOURSALES
-- ============================================
-- Script complet pour ajouter des données de test dans toutes les tables
-- À exécuter après la création des tables principales

-- ============================================
-- 1. USERS - Utilisateurs de test
-- ============================================
-- Mot de passe hashé: admin123 / merchant123 / influencer123
-- Hash bcrypt: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW

INSERT INTO users (id, email, password_hash, role, phone, phone_verified, two_fa_enabled, is_active) VALUES
-- Admin
('11111111-1111-1111-1111-111111111111', 'admin@shareyoursales.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'admin', '+33600000000', TRUE, TRUE, TRUE),

-- Merchants
('22222222-2222-2222-2222-222222222222', 'contact@techstyle.fr', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'merchant', '+33601234567', TRUE, TRUE, TRUE),
('22222222-2222-2222-2222-222222222223', 'hello@beautypro.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'merchant', '+33601234568', TRUE, FALSE, TRUE),
('22222222-2222-2222-2222-222222222224', 'contact@fitgear.fr', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'merchant', '+33601234569', TRUE, FALSE, TRUE),

-- Influencers
('33333333-3333-3333-3333-333333333333', 'emma.style@instagram.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'influencer', '+33602345678', TRUE, TRUE, TRUE),
('33333333-3333-3333-3333-333333333334', 'lucas.tech@youtube.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'influencer', '+33602345679', TRUE, FALSE, TRUE),
('33333333-3333-3333-3333-333333333335', 'julie.beauty@tiktok.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'influencer', '+33602345680', TRUE, FALSE, TRUE),
('33333333-3333-3333-3333-333333333336', 'thomas.sport@instagram.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'influencer', '+33602345681', TRUE, FALSE, TRUE)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- 2. MERCHANTS - Profils marchands
-- ============================================
INSERT INTO merchants (id, user_id, company_name, industry, category, address, website, description, subscription_plan, commission_rate, monthly_fee, total_sales, total_commission_paid) VALUES
('44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222222', 'TechStyle', 'E-commerce', 'Mode et lifestyle', '123 Rue de la Mode, Paris', 'https://techstyle.fr', 'Boutique de vêtements tech et streetwear', 'pro', 5.00, 99.00, 45000.00, 2250.00),
('44444444-4444-4444-4444-444444444445', '22222222-2222-2222-2222-222222222223', 'BeautyPro', 'E-commerce', 'Beauté et bien-être', '45 Avenue des Cosmétiques, Lyon', 'https://beautypro.com', 'Produits de beauté professionnels', 'starter', 7.00, 49.00, 28000.00, 1960.00),
('44444444-4444-4444-4444-444444444446', '22222222-2222-2222-2222-222222222224', 'FitGear', 'E-commerce', 'Sport et fitness', '78 Boulevard du Sport, Marseille', 'https://fitgear.fr', 'Équipements de fitness et nutrition', 'enterprise', 4.00, 299.00, 82000.00, 3280.00)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================
-- 3. INFLUENCERS - Profils influenceurs
-- ============================================
INSERT INTO influencers (id, user_id, username, full_name, bio, category, influencer_type, audience_size, engagement_rate, subscription_plan, platform_fee_rate, monthly_fee, social_links, total_clicks, total_sales, total_earnings, balance) VALUES
('55555555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333333', 'emma.style', 'Emma Dubois', 'Passionnée de mode et lifestyle 🌸 | Paris | Collaborations: emma.style@instagram.com', 'Mode', 'micro', 45000, 5.2, 'pro', 5.00, 19.90, '{"instagram": "https://instagram.com/emma.style", "tiktok": "https://tiktok.com/@emma.style"}', 12500, 340, 8500.00, 3200.00),
('55555555-5555-5555-5555-555555555556', '33333333-3333-3333-3333-333333333334', 'lucas.tech', 'Lucas Martin', 'Tech reviewer & gadget lover 💻 | YouTube 150K | Unboxing & Reviews', 'Technologie', 'macro', 150000, 4.8, 'pro', 5.00, 19.90, '{"youtube": "https://youtube.com/@lucastech", "instagram": "https://instagram.com/lucas.tech"}', 28000, 580, 15600.00, 7800.00),
('55555555-5555-5555-5555-555555555557', '33333333-3333-3333-3333-333333333335', 'julie.beauty', 'Julie Bertrand', 'Makeup artist & beauty tips 💄 | TikTok 85K | Collaborations ouvertes', 'Beauté', 'micro', 85000, 6.1, 'starter', 7.00, 9.90, '{"tiktok": "https://tiktok.com/@julie.beauty", "instagram": "https://instagram.com/julie.beauty"}', 18500, 425, 9350.00, 4200.00),
('55555555-5555-5555-5555-555555555558', '33333333-3333-3333-3333-333333333336', 'thomas.sport', 'Thomas Rousseau', 'Coach sportif & nutrition 💪 | Transformations inspirantes | DM for collabs', 'Sport', 'micro', 62000, 5.5, 'starter', 7.00, 9.90, '{"instagram": "https://instagram.com/thomas.sport", "youtube": "https://youtube.com/@thomassport"}', 15200, 298, 7450.00, 2850.00)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================
-- 4. PRODUCTS - Produits de test
-- ============================================
INSERT INTO products (id, merchant_id, name, description, category, price, commission_rate, commission_type, images, stock_quantity, is_available, slug) VALUES
-- TechStyle Products
('66666666-6666-6666-6666-666666666661', '44444444-4444-4444-4444-444444444444', 'T-shirt Tech Logo', 'T-shirt en coton bio avec logo tech moderne', 'Mode', 29.90, 15.00, 'percentage', '["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab"]', 150, TRUE, 'tshirt-tech-logo'),
('66666666-6666-6666-6666-666666666662', '44444444-4444-4444-4444-444444444444', 'Hoodie Streetwear Premium', 'Sweat à capuche épais, coupe oversized', 'Mode', 79.90, 18.00, 'percentage', '["https://images.unsplash.com/photo-1556821840-3a63f95609a7"]', 80, TRUE, 'hoodie-streetwear-premium'),
('66666666-6666-6666-6666-666666666663', '44444444-4444-4444-4444-444444444444', 'Casquette RGB Gaming', 'Casquette avec LED RGB programmables', 'Mode', 39.90, 20.00, 'percentage', '["https://images.unsplash.com/photo-1588850561407-ed78c282e89b"]', 120, TRUE, 'casquette-rgb-gaming'),

-- BeautyPro Products
('66666666-6666-6666-6666-666666666664', '44444444-4444-4444-4444-444444444445', 'Sérum Anti-Âge Premium', 'Sérum concentré en acide hyaluronique', 'Beauté', 45.00, 22.00, 'percentage', '["https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b"]', 200, TRUE, 'serum-anti-age-premium'),
('66666666-6666-6666-6666-666666666665', '44444444-4444-4444-4444-444444444445', 'Palette Maquillage Pro', 'Palette 20 couleurs professionnelle', 'Beauté', 59.90, 25.00, 'percentage', '["https://images.unsplash.com/photo-1512496015851-a90fb38ba796"]', 95, TRUE, 'palette-maquillage-pro'),
('66666666-6666-6666-6666-666666666666', '44444444-4444-4444-4444-444444444445', 'Kit Soins Visage Complet', 'Kit avec nettoyant, tonique, crème', 'Beauté', 89.00, 20.00, 'percentage', '["https://images.unsplash.com/photo-1556228578-0d85b1a4d571"]', 75, TRUE, 'kit-soins-visage-complet'),

-- FitGear Products
('66666666-6666-6666-6666-666666666667', '44444444-4444-4444-4444-444444444446', 'Protéine Whey Isolate 2kg', 'Protéine pure isolate goût vanille', 'Sport', 54.90, 15.00, 'percentage', '["https://images.unsplash.com/photo-1593095948071-474c5cc2989d"]', 300, TRUE, 'proteine-whey-isolate-2kg'),
('66666666-6666-6666-6666-666666666668', '44444444-4444-4444-4444-444444444446', 'Tapis de Yoga Antidérapant', 'Tapis éco-responsable 6mm épaisseur', 'Sport', 34.90, 18.00, 'percentage', '["https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f"]', 180, TRUE, 'tapis-yoga-antiderapant'),
('66666666-6666-6666-6666-666666666669', '44444444-4444-4444-4444-444444444446', 'Élastiques de Résistance Set', 'Set de 5 élastiques différents niveaux', 'Sport', 24.90, 20.00, 'percentage', '["https://images.unsplash.com/photo-1598289431512-b97b0917affc"]', 250, TRUE, 'elastiques-resistance-set')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 5. TRACKABLE LINKS - Liens d'affiliation
-- ============================================
INSERT INTO trackable_links (id, product_id, influencer_id, unique_code, full_url, clicks, unique_clicks, sales, conversion_rate, total_revenue, total_commission, is_active) VALUES
-- Emma (micro influencer Mode) - TechStyle Products
('77777777-7777-7777-7777-777777777771', '66666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555555', 'EMMA-TECH-001', 'https://shareyoursales.com/r/EMMA-TECH-001', 450, 380, 42, 11.05, 1255.80, 188.37, TRUE),
('77777777-7777-7777-7777-777777777772', '66666666-6666-6666-6666-666666666662', '55555555-5555-5555-5555-555555555555', 'EMMA-TECH-002', 'https://shareyoursales.com/r/EMMA-TECH-002', 320, 275, 28, 10.18, 2237.20, 402.70, TRUE),

-- Lucas (macro influencer Tech) - TechStyle & FitGear
('77777777-7777-7777-7777-777777777773', '66666666-6666-6666-6666-666666666663', '55555555-5555-5555-5555-555555555556', 'LUCAS-TECH-001', 'https://shareyoursales.com/r/LUCAS-TECH-001', 850, 720, 95, 13.19, 3790.50, 758.10, TRUE),
('77777777-7777-7777-7777-777777777774', '66666666-6666-6666-6666-666666666667', '55555555-5555-5555-5555-555555555556', 'LUCAS-FIT-001', 'https://shareyoursales.com/r/LUCAS-FIT-001', 620, 540, 78, 14.44, 4282.20, 642.33, TRUE),

-- Julie (micro influencer Beauté) - BeautyPro Products
('77777777-7777-7777-7777-777777777775', '66666666-6666-6666-6666-666666666664', '55555555-5555-5555-5555-555555555557', 'JULIE-BEAUTY-001', 'https://shareyoursales.com/r/JULIE-BEAUTY-001', 580, 490, 68, 13.88, 3060.00, 673.20, TRUE),
('77777777-7777-7777-7777-777777777776', '66666666-6666-6666-6666-666666666665', '55555555-5555-5555-5555-555555555557', 'JULIE-BEAUTY-002', 'https://shareyoursales.com/r/JULIE-BEAUTY-002', 420, 355, 52, 14.65, 3114.80, 778.70, TRUE),

-- Thomas (micro influencer Sport) - FitGear Products
('77777777-7777-7777-7777-777777777777', '66666666-6666-6666-6666-666666666668', '55555555-5555-5555-5555-555555555558', 'THOMAS-FIT-001', 'https://shareyoursales.com/r/THOMAS-FIT-001', 380, 320, 45, 14.06, 1570.50, 282.69, TRUE),
('77777777-7777-7777-7777-777777777778', '66666666-6666-6666-6666-666666666669', '55555555-5555-5555-5555-555555555558', 'THOMAS-FIT-002', 'https://shareyoursales.com/r/THOMAS-FIT-002', 290, 250, 38, 15.20, 946.20, 189.24, TRUE)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 6. SALES - Ventes de test
-- ============================================
INSERT INTO sales (id, link_id, product_id, influencer_id, merchant_id, customer_email, customer_name, quantity, amount, influencer_commission, platform_commission, merchant_revenue, status, payment_status, sale_timestamp) VALUES
-- Ventes Emma
('88888888-8888-8888-8888-888888888881', '77777777-7777-7777-7777-777777777771', '66666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555555', '44444444-4444-4444-4444-444444444444', 'client1@example.com', 'Sophie Dupont', 2, 59.80, 8.97, 2.99, 47.84, 'completed', 'paid', NOW() - INTERVAL '5 days'),
('88888888-8888-8888-8888-888888888882', '77777777-7777-7777-7777-777777777771', '66666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555555', '44444444-4444-4444-4444-444444444444', 'client2@example.com', 'Marc Leroy', 1, 29.90, 4.49, 1.50, 23.91, 'completed', 'paid', NOW() - INTERVAL '4 days'),

-- Ventes Lucas
('88888888-8888-8888-8888-888888888883', '77777777-7777-7777-7777-777777777773', '66666666-6666-6666-6666-666666666663', '55555555-5555-5555-5555-555555555556', '44444444-4444-4444-4444-444444444444', 'client3@example.com', 'Julie Martin', 3, 119.70, 23.94, 5.99, 89.77, 'completed', 'paid', NOW() - INTERVAL '3 days'),
('88888888-8888-8888-8888-888888888884', '77777777-7777-7777-7777-777777777774', '66666666-6666-6666-6666-666666666667', '55555555-5555-5555-5555-555555555556', '44444444-4444-4444-4444-444444444446', 'client4@example.com', 'Thomas Bernard', 2, 109.80, 16.47, 4.39, 88.94, 'completed', 'paid', NOW() - INTERVAL '2 days'),

-- Ventes Julie
('88888888-8888-8888-8888-888888888885', '77777777-7777-7777-7777-777777777775', '66666666-6666-6666-6666-666666666664', '55555555-5555-5555-5555-555555555557', '44444444-4444-4444-4444-444444444445', 'client5@example.com', 'Emma Rousseau', 1, 45.00, 9.90, 3.15, 31.95, 'completed', 'paid', NOW() - INTERVAL '1 day'),
('88888888-8888-8888-8888-888888888886', '77777777-7777-7777-7777-777777777776', '66666666-6666-6666-6666-666666666665', '55555555-5555-5555-5555-555555555557', '44444444-4444-4444-4444-444444444445', 'client6@example.com', 'Lucas Petit', 1, 59.90, 14.98, 4.19, 40.73, 'pending', 'pending', NOW() - INTERVAL '6 hours'),

-- Ventes Thomas
('88888888-8888-8888-8888-888888888887', '77777777-7777-7777-7777-777777777777', '66666666-6666-6666-6666-666666666668', '55555555-5555-5555-5555-555555555558', '44444444-4444-4444-4444-444444444446', 'client7@example.com', 'Marie Dubois', 2, 69.80, 12.56, 2.79, 54.45, 'completed', 'paid', NOW() - INTERVAL '8 hours'),
('88888888-8888-8888-8888-888888888888', '77777777-7777-7777-7777-777777777778', '66666666-6666-6666-6666-666666666669', '55555555-5555-5555-5555-555555555558', '44444444-4444-4444-4444-444444444446', 'client8@example.com', 'Pierre Lambert', 3, 74.70, 14.94, 2.99, 56.77, 'completed', 'paid', NOW() - INTERVAL '12 hours')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 7. COMMISSIONS - Commissions influenceurs
-- ============================================
INSERT INTO commissions (id, sale_id, influencer_id, amount, status, payment_method) VALUES
('99999999-9999-9999-9999-999999999991', '88888888-8888-8888-8888-888888888881', '55555555-5555-5555-5555-555555555555', 8.97, 'paid', 'paypal'),
('99999999-9999-9999-9999-999999999992', '88888888-8888-8888-8888-888888888882', '55555555-5555-5555-5555-555555555555', 4.49, 'paid', 'paypal'),
('99999999-9999-9999-9999-999999999993', '88888888-8888-8888-8888-888888888883', '55555555-5555-5555-5555-555555555556', 23.94, 'paid', 'bank_transfer'),
('99999999-9999-9999-9999-999999999994', '88888888-8888-8888-8888-888888888884', '55555555-5555-5555-5555-555555555556', 16.47, 'paid', 'bank_transfer'),
('99999999-9999-9999-9999-999999999995', '88888888-8888-8888-8888-888888888885', '55555555-5555-5555-5555-555555555557', 9.90, 'approved', 'paypal'),
('99999999-9999-9999-9999-999999999996', '88888888-8888-8888-8888-888888888886', '55555555-5555-5555-5555-555555555557', 14.98, 'pending', NULL),
('99999999-9999-9999-9999-999999999997', '88888888-8888-8888-8888-888888888887', '55555555-5555-5555-5555-555555555558', 12.56, 'paid', 'paypal'),
('99999999-9999-9999-9999-999999999998', '88888888-8888-8888-8888-888888888888', '55555555-5555-5555-5555-555555555558', 14.94, 'approved', 'paypal')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 8. CAMPAIGNS - Campagnes marketing
-- ============================================
INSERT INTO campaigns (id, merchant_id, name, description, budget, spent, start_date, end_date, status, total_clicks, total_conversions, total_revenue) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '44444444-4444-4444-4444-444444444444', 'Lancement Collection Automne', 'Campagne de lancement de la nouvelle collection automne/hiver', 5000.00, 2340.50, NOW() - INTERVAL '30 days', NOW() + INTERVAL '30 days', 'active', 1250, 85, 4280.00),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaab', '44444444-4444-4444-4444-444444444445', 'Black Friday Beauty', 'Promotions exceptionnelles Black Friday', 8000.00, 4520.00, NOW() - INTERVAL '15 days', NOW() + INTERVAL '5 days', 'active', 2180, 142, 8560.00),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaac', '44444444-4444-4444-4444-444444444446', 'Challenge Fitness Janvier', 'Challenge de remise en forme pour la nouvelle année', 3500.00, 890.00, NOW() + INTERVAL '10 days', NOW() + INTERVAL '60 days', 'draft', 0, 0, 0.00)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 9. CLICK TRACKING - Suivi des clics
-- ============================================
INSERT INTO click_tracking (id, link_id, ip_address, user_agent, country, city, device_type, os, browser, is_unique_visitor, clicked_at) VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '77777777-7777-7777-7777-777777777771', '192.168.1.10', 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)', 'FR', 'Paris', 'Mobile', 'iOS', 'Safari', TRUE, NOW() - INTERVAL '2 hours'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2', '77777777-7777-7777-7777-777777777771', '192.168.1.11', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'FR', 'Lyon', 'Desktop', 'Windows', 'Chrome', TRUE, NOW() - INTERVAL '5 hours'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb3', '77777777-7777-7777-7777-777777777773', '192.168.1.12', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'FR', 'Marseille', 'Desktop', 'macOS', 'Safari', TRUE, NOW() - INTERVAL '1 day'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb4', '77777777-7777-7777-7777-777777777775', '192.168.1.13', 'Mozilla/5.0 (Linux; Android 12)', 'FR', 'Toulouse', 'Mobile', 'Android', 'Chrome', TRUE, NOW() - INTERVAL '3 hours')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 10. REVIEWS - Avis produits
-- ============================================
INSERT INTO reviews (id, product_id, user_id, rating, title, comment, is_verified_purchase, is_approved, helpful_count) VALUES
('cccccccc-cccc-cccc-cccc-cccccccccccc', '66666666-6666-6666-6666-666666666661', '33333333-3333-3333-3333-333333333333', 5, 'Super qualité!', 'T-shirt très confortable et la qualité du tissu est top. Je recommande!', TRUE, TRUE, 12),
('cccccccc-cccc-cccc-cccc-ccccccccccc2', '66666666-6666-6666-6666-666666666664', '33333333-3333-3333-3333-333333333335', 5, 'Mon sérum préféré', 'Résultats visibles après 2 semaines. Ma peau est plus lisse et éclatante.', TRUE, TRUE, 24),
('cccccccc-cccc-cccc-cccc-ccccccccccc3', '66666666-6666-6666-6666-666666666667', '33333333-3333-3333-3333-333333333336', 4, 'Bon rapport qualité/prix', 'Protéine de bonne qualité, goût agréable. Juste un peu cher.', TRUE, TRUE, 8),
('cccccccc-cccc-cccc-cccc-ccccccccccc4', '66666666-6666-6666-6666-666666666662', '33333333-3333-3333-3333-333333333334', 5, 'Excellent hoodie!', 'Coupe parfaite, tissu épais et chaud. Taille parfaitement.', TRUE, TRUE, 15)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 11. SUBSCRIPTIONS - Abonnements
-- ============================================
INSERT INTO subscriptions (id, user_id, plan_type, monthly_fee, commission_rate, start_date, next_billing_date, status, payment_method) VALUES
('dddddddd-dddd-dddd-dddd-dddddddddddd', '22222222-2222-2222-2222-222222222222', 'pro', 99.00, 5.00, NOW() - INTERVAL '6 months', NOW() + INTERVAL '1 month', 'active', 'credit_card'),
('dddddddd-dddd-dddd-dddd-ddddddddddd2', '22222222-2222-2222-2222-222222222223', 'starter', 49.00, 7.00, NOW() - INTERVAL '3 months', NOW() + INTERVAL '1 month', 'active', 'paypal'),
('dddddddd-dddd-dddd-dddd-ddddddddddd3', '33333333-3333-3333-3333-333333333333', 'influencer_pro', 19.90, 5.00, NOW() - INTERVAL '4 months', NOW() + INTERVAL '1 month', 'active', 'credit_card'),
('dddddddd-dddd-dddd-dddd-ddddddddddd4', '33333333-3333-3333-3333-333333333334', 'influencer_pro', 19.90, 5.00, NOW() - INTERVAL '8 months', NOW() + INTERVAL '1 month', 'active', 'bank_transfer')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 12. PAYMENTS - Historique paiements
-- ============================================
INSERT INTO payments (id, user_id, subscription_id, amount, payment_type, payment_method, transaction_id, status, description) VALUES
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '22222222-2222-2222-2222-222222222222', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 99.00, 'subscription', 'credit_card', 'PAY-123456789', 'completed', 'Abonnement Pro - Janvier 2025'),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee2', '33333333-3333-3333-3333-333333333333', 'dddddddd-dddd-dddd-dddd-ddddddddddd3', 19.90, 'subscription', 'credit_card', 'PAY-987654321', 'completed', 'Abonnement Influencer Pro - Janvier 2025'),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee3', '33333333-3333-3333-3333-333333333335', NULL, 450.00, 'commission', 'paypal', 'COMM-2025-001', 'completed', 'Paiement commission Décembre 2024')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 13. CONVERSATIONS - Messagerie
-- ============================================
INSERT INTO conversations (id, user1_id, user1_type, user2_id, user2_type, subject, status, last_message_at) VALUES
('ffffffff-ffff-ffff-ffff-ffffffffffff', '22222222-2222-2222-2222-222222222222', 'merchant', '33333333-3333-3333-3333-333333333333', 'influencer', 'Collaboration Collection Automne', 'active', NOW() - INTERVAL '2 hours'),
('ffffffff-ffff-ffff-ffff-fffffffffff2', '22222222-2222-2222-2222-222222222223', 'merchant', '33333333-3333-3333-3333-333333333335', 'influencer', 'Partenariat produits beauté', 'active', NOW() - INTERVAL '1 day'),
('ffffffff-ffff-ffff-ffff-fffffffffff3', '22222222-2222-2222-2222-222222222224', 'merchant', '33333333-3333-3333-3333-333333333336', 'influencer', 'Challenge Fitness', 'active', NOW() - INTERVAL '5 hours')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 14. MESSAGES - Messages de conversation
-- ============================================
INSERT INTO messages (id, conversation_id, sender_id, sender_type, content, is_read) VALUES
('gggggggg-gggg-gggg-gggg-gggggggggggg', 'ffffffff-ffff-ffff-ffff-ffffffffffff', '22222222-2222-2222-2222-222222222222', 'merchant', 'Bonjour Emma, j''aimerais collaborer avec toi pour notre nouvelle collection automne. Es-tu intéressée ?', TRUE),
('gggggggg-gggg-gggg-gggg-ggggggggggg2', 'ffffffff-ffff-ffff-ffff-ffffffffffff', '33333333-3333-3333-3333-333333333333', 'influencer', 'Hello ! Oui je suis très intéressée ! Peux-tu me donner plus de détails sur la collaboration ?', TRUE),
('gggggggg-gggg-gggg-gggg-ggggggggggg3', 'ffffffff-ffff-ffff-ffff-ffffffffffff', '22222222-2222-2222-2222-222222222222', 'merchant', 'Super ! Nous proposons 18% de commission sur toute la collection. Je t''envoie le catalogue en MP.', FALSE),

('gggggggg-gggg-gggg-gggg-ggggggggggg4', 'ffffffff-ffff-ffff-ffff-fffffffffff2', '22222222-2222-2222-2222-222222222223', 'merchant', 'Salut Julie ! Ton contenu est super, on aimerait t''envoyer des produits à tester. Partante ?', TRUE),
('gggggggg-gggg-gggg-gggg-ggggggggggg5', 'ffffffff-ffff-ffff-ffff-fffffffffff2', '33333333-3333-3333-3333-333333333335', 'influencer', 'Merci beaucoup ! Oui je suis totalement partante ! Quels produits voulez-vous que je teste ?', FALSE)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 15. NOTIFICATIONS - Notifications utilisateurs
-- ============================================
INSERT INTO notifications (id, user_id, user_type, type, title, message, link, is_read) VALUES
('hhhhhhhh-hhhh-hhhh-hhhh-hhhhhhhhhhhh', '33333333-3333-3333-3333-333333333333', 'influencer', 'sale', 'Nouvelle vente !', 'Vous avez réalisé une vente de 59.80€', '/performance/conversions', TRUE),
('hhhhhhhh-hhhh-hhhh-hhhh-hhhhhhhhhhh2', '33333333-3333-3333-3333-333333333334', 'influencer', 'payout', 'Paiement reçu', 'Votre paiement de 450.00€ a été traité', '/affiliates/payouts', TRUE),
('hhhhhhhh-hhhh-hhhh-hhhh-hhhhhhhhhhh3', '22222222-2222-2222-2222-222222222222', 'merchant', 'message', 'Nouveau message', 'Emma vous a envoyé un message', '/messages/ffffffff-ffff-ffff-ffff-ffffffffffff', FALSE),
('hhhhhhhh-hhhh-hhhh-hhhh-hhhhhhhhhhh4', '33333333-3333-3333-3333-333333333335', 'influencer', 'campaign', 'Nouvelle invitation', 'BeautyPro vous invite à une campagne', '/campaigns', FALSE)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 16. INVITATIONS - Invitations campagnes
-- ============================================
INSERT INTO invitations (id, merchant_id, influencer_id, campaign_id, status, message, commission_rate) VALUES
('iiiiiiii-iiii-iiii-iiii-iiiiiiiiiiii', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'accepted', 'Rejoins notre campagne collection automne ! Commission de 18%', 18.00),
('iiiiiiii-iiii-iiii-iiii-iiiiiiiiiii2', '22222222-2222-2222-2222-222222222223', '33333333-3333-3333-3333-333333333335', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaab', 'pending', 'Campagne Black Friday avec des commissions exceptionnelles !', 25.00),
('iiiiiiii-iiii-iiii-iiii-iiiiiiiiiii3', '22222222-2222-2222-2222-222222222224', '33333333-3333-3333-3333-333333333336', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaac', 'pending', 'Challenge fitness avec prime à la performance', 20.00)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 17. SETTINGS - Paramètres plateforme
-- ============================================
-- (Déjà inséré dans create_tables_missing.sql)

-- ============================================
-- 18. ENGAGEMENT METRICS - Métriques engagement
-- ============================================
INSERT INTO engagement_metrics (id, link_id, product_id, influencer_id, likes, comments, shares, impressions, clicks, conversions, conversion_rate, metric_date) VALUES
('jjjjjjjj-jjjj-jjjj-jjjj-jjjjjjjjjjjj', '77777777-7777-7777-7777-777777777771', '66666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555555', 245, 18, 32, 12500, 450, 42, 9.33, NOW() - INTERVAL '1 day'),
('jjjjjjjj-jjjj-jjjj-jjjj-jjjjjjjjjjj2', '77777777-7777-7777-7777-777777777773', '66666666-6666-6666-6666-666666666663', '55555555-5555-5555-5555-555555555556', 892, 64, 125, 48500, 850, 95, 11.18, NOW() - INTERVAL '1 day'),
('jjjjjjjj-jjjj-jjjj-jjjj-jjjjjjjjjjj3', '77777777-7777-7777-7777-777777777775', '66666666-6666-6666-6666-666666666664', '55555555-5555-5555-5555-555555555557', 486, 42, 67, 28400, 580, 68, 11.72, NOW() - INTERVAL '2 days')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- RÉSUMÉ DES DONNÉES INSÉRÉES
-- ============================================
-- ✓ 8 utilisateurs (1 admin, 3 merchants, 4 influencers)
-- ✓ 3 profils merchants
-- ✓ 4 profils influencers
-- ✓ 9 produits (3 par merchant)
-- ✓ 8 liens trackables
-- ✓ 8 ventes
-- ✓ 8 commissions
-- ✓ 3 campagnes
-- ✓ 4 clics trackés
-- ✓ 4 avis produits
-- ✓ 4 abonnements
-- ✓ 3 paiements
-- ✓ 3 conversations
-- ✓ 5 messages
-- ✓ 4 notifications
-- ✓ 3 invitations
-- ✓ 3 métriques d'engagement

-- Mot de passe pour tous les comptes de test: admin123 / merchant123 / influencer123
-- Code 2FA pour les tests: 123456

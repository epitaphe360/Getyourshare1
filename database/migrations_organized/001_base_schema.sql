-- ============================================
-- SHAREYOURSALES DATABASE SCHEMA (PostgreSQL/Supabase)
-- ============================================

-- ============================================
-- 1. USERS & AUTHENTICATION
-- ============================================

-- Table principale des utilisateurs
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'merchant', 'influencer')),
    phone VARCHAR(20),
    phone_verified BOOLEAN DEFAULT FALSE,
    two_fa_enabled BOOLEAN DEFAULT TRUE,
    two_fa_code VARCHAR(6),
    two_fa_expires_at TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions de connexion
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(500) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. MERCHANTS/COMPANIES
-- ============================================

CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    category VARCHAR(100) CHECK (category IN (
        'E-commerce',
        'Services en ligne',
        'Voyage et tourisme',
        'Mode et lifestyle',
        'Beauté et bien-être',
        'Technologie',
        'Finance et assurance',
        'Santé et bien-être',
        'Alimentation et boissons',
        'Divertissement et médias',
        'Automobile',
        'Immobilier',
        'Sport et fitness',
        'Éducation',
        'Bricolage et décoration'
    )),
    address TEXT,
    tax_id VARCHAR(50),
    website VARCHAR(255),
    logo_url TEXT,
    description TEXT,
    subscription_plan VARCHAR(50) CHECK (subscription_plan IN ('free', 'starter', 'pro', 'enterprise')),
    subscription_status VARCHAR(50) DEFAULT 'active',
    commission_rate DECIMAL(5, 2) DEFAULT 5.00, -- Frais plateforme (%)
    monthly_fee DECIMAL(10, 2) DEFAULT 0.00,
    total_sales DECIMAL(15, 2) DEFAULT 0.00,
    total_commission_paid DECIMAL(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. INFLUENCERS
-- ============================================

CREATE TABLE influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    bio TEXT,
    profile_picture_url TEXT,
    category VARCHAR(100), -- Mode, Beauté, Fitness, etc.
    influencer_type VARCHAR(50) CHECK (influencer_type IN ('nano', 'micro', 'macro', 'mega')),
    audience_size INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 2) DEFAULT 0.00,
    subscription_plan VARCHAR(50) CHECK (subscription_plan IN ('starter', 'pro')),
    subscription_status VARCHAR(50) DEFAULT 'active',
    platform_fee_rate DECIMAL(5, 2) DEFAULT 5.00, -- Frais plateforme (%)
    monthly_fee DECIMAL(10, 2) DEFAULT 9.90,
    
    -- Réseaux sociaux (JSON)
    social_links JSONB DEFAULT '{}', -- {instagram: "url", youtube: "url", tiktok: "url"}
    
    -- Statistiques globales
    total_clicks INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    total_earnings DECIMAL(15, 2) DEFAULT 0.00,
    balance DECIMAL(15, 2) DEFAULT 0.00, -- Solde disponible
    
    -- Méthodes de paiement
    payment_method VARCHAR(50), -- PayPal, Bank, Crypto
    payment_details JSONB, -- Détails sécurisés du paiement
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. PRODUCTS
-- ============================================

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) CHECK (category IN (
        'Mode', 'Beauté', 'Technologie', 'Alimentation', 
        'Artisanat', 'Sport', 'Santé', 'Maison', 'Autre'
    )),
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Commission pour les affiliés
    commission_rate DECIMAL(5, 2) NOT NULL, -- 10-25%
    commission_type VARCHAR(20) CHECK (commission_type IN ('percentage', 'fixed')),
    
    -- Médias
    images JSONB DEFAULT '[]', -- Array d'URLs d'images
    videos JSONB DEFAULT '[]', -- Array d'URLs de vidéos
    
    -- Caractéristiques
    specifications JSONB, -- Détails techniques
    
    -- Stock & Disponibilité
    stock_quantity INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    
    -- SEO
    slug VARCHAR(255) UNIQUE,
    meta_description TEXT,
    
    -- Statistiques
    total_views INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. TRACKABLE LINKS (Liens d'affiliation)
-- ============================================

CREATE TABLE trackable_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    
    -- Lien unique
    unique_code VARCHAR(50) UNIQUE NOT NULL, -- Code unique crypté
    full_url TEXT NOT NULL, -- URL complète
    short_url TEXT, -- URL raccourcie (optionnel)
    
    -- Offres spéciales
    has_discount BOOLEAN DEFAULT FALSE,
    discount_code VARCHAR(50),
    discount_percentage DECIMAL(5, 2),
    
    -- Statistiques de performance
    clicks INTEGER DEFAULT 0,
    unique_clicks INTEGER DEFAULT 0, -- Clics uniques (IP tracking)
    sales INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    total_revenue DECIMAL(15, 2) DEFAULT 0.00,
    total_commission DECIMAL(15, 2) DEFAULT 0.00,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP, -- Expiration du lien (optionnel)
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(product_id, influencer_id)
);

-- ============================================
-- 6. SALES (Ventes)
-- ============================================

CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID REFERENCES trackable_links(id) ON DELETE SET NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    influencer_id UUID REFERENCES influencers(id) ON DELETE SET NULL,
    merchant_id UUID REFERENCES merchants(id) ON DELETE SET NULL,
    
    -- Informations client
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    customer_ip INET,
    
    -- Détails de la vente
    quantity INTEGER DEFAULT 1,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Commissions
    influencer_commission DECIMAL(10, 2) NOT NULL,
    platform_commission DECIMAL(10, 2) NOT NULL,
    merchant_revenue DECIMAL(10, 2) NOT NULL,
    
    -- Status
    status VARCHAR(50) CHECK (status IN ('pending', 'completed', 'refunded', 'cancelled')),
    payment_status VARCHAR(50) CHECK (payment_status IN ('pending', 'paid')),
    
    -- Timestamps
    sale_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_processed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 7. COMMISSIONS (Paiements aux influenceurs)
-- ============================================

CREATE TABLE commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    status VARCHAR(50) CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')),
    
    -- Paiement
    payment_method VARCHAR(50), -- PayPal, Bank Transfer, Crypto
    transaction_id VARCHAR(255), -- ID transaction externe
    paid_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 8. ENGAGEMENT METRICS
-- ============================================

CREATE TABLE engagement_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID REFERENCES trackable_links(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    
    -- Métriques d'engagement
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    
    -- Métriques de conversion
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    
    -- ROI
    roi_percentage DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Valeur économique
    vep_value DECIMAL(15, 2) DEFAULT 0.00, -- Valeur Économique de la Visibilité
    
    -- CPA (Coût par acquisition)
    cpa DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Date
    metric_date DATE DEFAULT CURRENT_DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(link_id, metric_date)
);

-- ============================================
-- 9. CAMPAIGNS (Campagnes marketing)
-- ============================================

CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Budget
    budget DECIMAL(15, 2),
    spent DECIMAL(15, 2) DEFAULT 0.00,
    
    -- Période
    start_date DATE,
    end_date DATE,
    
    -- Ciblage
    target_audience JSONB, -- {age_range, gender, interests, location}
    
    -- Status
    status VARCHAR(50) CHECK (status IN ('draft', 'active', 'paused', 'completed')),
    
    -- Performance
    total_clicks INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    total_revenue DECIMAL(15, 2) DEFAULT 0.00,
    roi DECIMAL(10, 2) DEFAULT 0.00,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 10. AI ANALYTICS (Analyses IA)
-- ============================================

CREATE TABLE ai_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    
    -- Prédictions
    predicted_sales INTEGER,
    trend_score DECIMAL(5, 2), -- Score de tendance (-100 à +100)
    
    -- Recommandations
    recommended_strategy TEXT,
    recommended_budget DECIMAL(15, 2),
    recommended_influencers JSONB, -- Array d'IDs d'influenceurs
    
    -- Insights
    audience_insights JSONB, -- Données démographiques prédites
    competitor_analysis JSONB,
    
    -- Période d'analyse
    analysis_period_start DATE,
    analysis_period_end DATE,
    
    -- Confiance
    confidence_score DECIMAL(5, 2), -- 0-100%
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 11. SUBSCRIPTIONS (Abonnements)
-- ============================================

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    plan_type VARCHAR(50) CHECK (plan_type IN (
        'free', 'starter', 'pro', 'enterprise',
        'influencer_starter', 'influencer_pro'
    )),
    
    -- Tarification
    monthly_fee DECIMAL(10, 2) NOT NULL,
    commission_rate DECIMAL(5, 2), -- Frais plateforme (%)
    
    -- Limites du plan
    max_products INTEGER,
    max_links INTEGER,
    max_users INTEGER,
    
    -- Features
    features JSONB, -- Array de features incluses
    
    -- Période
    start_date DATE NOT NULL,
    end_date DATE,
    next_billing_date DATE,
    
    -- Status
    status VARCHAR(50) CHECK (status IN ('active', 'cancelled', 'expired', 'trial')),
    
    -- Paiement
    payment_method VARCHAR(50),
    last_payment_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 12. PAYMENTS (Historique des paiements)
-- ============================================

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    
    -- Montant
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Type
    payment_type VARCHAR(50) CHECK (payment_type IN ('subscription', 'commission', 'refund')),
    
    -- Méthode
    payment_method VARCHAR(50) CHECK (payment_method IN ('credit_card', 'paypal', 'bank_transfer', 'crypto')),
    
    -- Transaction
    transaction_id VARCHAR(255) UNIQUE,
    gateway_response JSONB, -- Réponse du gateway de paiement
    
    -- Status
    status VARCHAR(50) CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    
    -- Détails
    description TEXT,
    
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 13. REVIEWS & RATINGS
-- ============================================

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    
    -- Vérification
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    
    -- Modération
    is_approved BOOLEAN DEFAULT TRUE,
    
    -- Utile
    helpful_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 14. CATEGORIES
-- ============================================

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    icon_url TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 15. CLICKS TRACKING (Détails des clics)
-- ============================================

CREATE TABLE click_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID REFERENCES trackable_links(id) ON DELETE CASCADE,
    
    -- Informations client
    ip_address INET,
    user_agent TEXT,
    referrer TEXT,
    
    -- Géolocalisation
    country VARCHAR(2),
    city VARCHAR(100),
    
    -- Device
    device_type VARCHAR(50), -- Mobile, Desktop, Tablet
    os VARCHAR(50),
    browser VARCHAR(50),
    
    -- Session
    session_id VARCHAR(255),
    is_unique_visitor BOOLEAN DEFAULT TRUE,
    
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES pour Performance
-- ============================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Merchants
CREATE INDEX idx_merchants_user_id ON merchants(user_id);
CREATE INDEX idx_merchants_category ON merchants(category);

-- Influencers
CREATE INDEX idx_influencers_user_id ON influencers(user_id);
CREATE INDEX idx_influencers_username ON influencers(username);
CREATE INDEX idx_influencers_type ON influencers(influencer_type);

-- Products
CREATE INDEX idx_products_merchant_id ON products(merchant_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_slug ON products(slug);

-- Trackable Links
CREATE INDEX idx_trackable_links_code ON trackable_links(unique_code);
CREATE INDEX idx_trackable_links_product ON trackable_links(product_id);
CREATE INDEX idx_trackable_links_influencer ON trackable_links(influencer_id);

-- Sales
CREATE INDEX idx_sales_link_id ON sales(link_id);
CREATE INDEX idx_sales_influencer_id ON sales(influencer_id);
CREATE INDEX idx_sales_merchant_id ON sales(merchant_id);
CREATE INDEX idx_sales_timestamp ON sales(sale_timestamp);
CREATE INDEX idx_sales_status ON sales(status);

-- Commissions
CREATE INDEX idx_commissions_influencer_id ON commissions(influencer_id);
CREATE INDEX idx_commissions_status ON commissions(status);

-- Click Tracking
CREATE INDEX idx_click_tracking_link_id ON click_tracking(link_id);
CREATE INDEX idx_click_tracking_ip ON click_tracking(ip_address);
CREATE INDEX idx_click_tracking_date ON click_tracking(clicked_at);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer le trigger aux tables concernées
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_merchants_updated_at BEFORE UPDATE ON merchants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_influencers_updated_at BEFORE UPDATE ON influencers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trackable_links_updated_at BEFORE UPDATE ON trackable_links FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS pour Rapports
-- ============================================

-- Vue: Performance des influenceurs
CREATE VIEW influencer_performance AS
SELECT 
    i.id,
    i.username,
    i.full_name,
    i.influencer_type,
    i.category,
    COUNT(DISTINCT tl.id) as total_links,
    SUM(tl.clicks) as total_clicks,
    SUM(tl.sales) as total_sales,
    SUM(tl.total_revenue) as total_revenue,
    SUM(tl.total_commission) as total_commission,
    i.balance,
    i.total_earnings
FROM influencers i
LEFT JOIN trackable_links tl ON i.id = tl.influencer_id
GROUP BY i.id;

-- Vue: Performance des produits
CREATE VIEW product_performance AS
SELECT 
    p.id,
    p.name,
    p.category,
    m.company_name as merchant_name,
    COUNT(DISTINCT tl.id) as total_links,
    SUM(tl.clicks) as total_clicks,
    SUM(tl.sales) as total_sales,
    SUM(tl.total_revenue) as total_revenue,
    AVG(r.rating) as average_rating,
    COUNT(r.id) as review_count
FROM products p
JOIN merchants m ON p.merchant_id = m.id
LEFT JOIN trackable_links tl ON p.id = tl.product_id
LEFT JOIN reviews r ON p.id = r.product_id
GROUP BY p.id, m.company_name;

-- Vue: Dashboard Admin
CREATE VIEW admin_dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM users WHERE role = 'influencer') as total_influencers,
    (SELECT COUNT(*) FROM users WHERE role = 'merchant') as total_merchants,
    (SELECT COUNT(*) FROM products WHERE is_available = TRUE) as active_products,
    (SELECT SUM(total_revenue) FROM trackable_links) as total_platform_revenue,
    (SELECT SUM(total_commission) FROM trackable_links) as total_commissions_paid,
    (SELECT COUNT(*) FROM sales WHERE status = 'completed') as total_sales,
    (SELECT COUNT(*) FROM trackable_links WHERE is_active = TRUE) as active_links;

-- ============================================
-- SEED DATA (Données initiales)
-- ============================================

-- Table de configuration SMTP (ajoutée après déploiement initial)
CREATE TABLE IF NOT EXISTS smtp_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    host VARCHAR(255) NOT NULL DEFAULT 'smtp.gmail.com',
    port INTEGER NOT NULL DEFAULT 587,
    username VARCHAR(255),
    password VARCHAR(255),
    from_email VARCHAR(255) NOT NULL DEFAULT 'noreply@shareyoursales.com',
    from_name VARCHAR(255) NOT NULL DEFAULT 'Share Your Sales',
    encryption VARCHAR(10) CHECK (encryption IN ('tls', 'ssl', 'none')) DEFAULT 'tls',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catégories de base
INSERT INTO categories (name, slug, description, display_order) VALUES
('Mode', 'mode', 'Vêtements, accessoires, chaussures', 1),
('Beauté', 'beaute', 'Cosmétiques, soins, parfums', 2),
('Technologie', 'technologie', 'Électronique, gadgets, informatique', 3),
('Alimentation', 'alimentation', 'Produits alimentaires, boissons', 4),
('Artisanat', 'artisanat', 'Produits artisanaux, fait main', 5),
('Sport', 'sport', 'Équipements sportifs, fitness', 6),
('Maison', 'maison', 'Décoration, meubles, électroménager', 7),
('Santé', 'sante', 'Compléments, bien-être', 8);

-- Admin par défaut (mot de passe: Admin123!)
INSERT INTO users (email, password_hash, role, phone, phone_verified) VALUES
('admin@shareyoursales.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'admin', '+33600000000', TRUE);

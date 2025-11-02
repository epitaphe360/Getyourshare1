-- ============================================
-- INITIALISATION SUPABASE - VERSION SIMPLIFIÉE
-- ============================================
-- ⚠️ ATTENTION: Ce script crée UNIQUEMENT les tables principales
-- Compatible avec Supabase Auth (pas de table users custom)
-- ============================================

-- ============================================
-- 1. MERCHANTS (ENTREPRISES)
-- ============================================
CREATE TABLE IF NOT EXISTS merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE, -- Référence à auth.users
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
    subscription_plan VARCHAR(50) CHECK (subscription_plan IN ('free', 'starter', 'pro', 'enterprise')) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    commission_rate DECIMAL(5, 2) DEFAULT 5.00,
    monthly_fee DECIMAL(10, 2) DEFAULT 0.00,
    total_sales DECIMAL(15, 2) DEFAULT 0.00,
    total_commission_paid DECIMAL(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. INFLUENCERS
-- ============================================
CREATE TABLE IF NOT EXISTS influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE, -- Référence à auth.users
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    bio TEXT,
    profile_picture_url TEXT,
    category VARCHAR(100),
    influencer_type VARCHAR(50) CHECK (influencer_type IN ('nano', 'micro', 'macro', 'mega')) DEFAULT 'nano',
    audience_size INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 2) DEFAULT 0.00,
    subscription_plan VARCHAR(50) CHECK (subscription_plan IN ('starter', 'pro')) DEFAULT 'starter',
    subscription_status VARCHAR(50) DEFAULT 'active',
    platform_fee_rate DECIMAL(5, 2) DEFAULT 5.00,
    monthly_fee DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Réseaux sociaux (JSON)
    social_links JSONB DEFAULT '{}',
    
    -- Statistiques
    total_clicks INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    total_earnings DECIMAL(15, 2) DEFAULT 0.00,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    
    -- Paiement
    payment_method VARCHAR(50),
    payment_details JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. PRODUCTS
-- ============================================
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'MAD',
    
    commission_rate DECIMAL(5, 2) NOT NULL,
    commission_type VARCHAR(20) CHECK (commission_type IN ('percentage', 'fixed')) DEFAULT 'percentage',
    
    images JSONB DEFAULT '[]',
    videos JSONB DEFAULT '[]',
    specifications JSONB,
    
    stock_quantity INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    
    slug VARCHAR(255) UNIQUE,
    meta_description TEXT,
    
    total_views INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. CAMPAIGNS
-- ============================================
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(50) CHECK (campaign_type IN ('product', 'brand', 'seasonal', 'flash_sale')) DEFAULT 'product',
    
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    
    commission_rate DECIMAL(5, 2) NOT NULL,
    budget DECIMAL(15, 2),
    
    target_audience JSONB,
    requirements JSONB,
    
    status VARCHAR(50) CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')) DEFAULT 'draft',
    
    total_clicks INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    total_revenue DECIMAL(15, 2) DEFAULT 0.00,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. AFFILIATIONS
-- ============================================
CREATE TABLE IF NOT EXISTS affiliations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    
    status VARCHAR(50) CHECK (status IN ('pending', 'approved', 'rejected', 'active', 'inactive')) DEFAULT 'pending',
    
    tracking_link VARCHAR(500) UNIQUE NOT NULL,
    promo_code VARCHAR(50),
    
    commission_rate DECIMAL(5, 2) NOT NULL,
    
    total_clicks INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    total_earnings DECIMAL(15, 2) DEFAULT 0.00,
    
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(influencer_id, merchant_id, campaign_id)
);

-- ============================================
-- 6. TRACKABLE LINKS
-- ============================================
CREATE TABLE IF NOT EXISTS trackable_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    affiliation_id UUID REFERENCES affiliations(id) ON DELETE CASCADE,
    
    short_code VARCHAR(20) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    
    total_clicks INTEGER DEFAULT 0,
    unique_clicks INTEGER DEFAULT 0,
    
    metadata JSONB,
    
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_clicked_at TIMESTAMP
);

-- ============================================
-- 7. CLICKS (TRACKING)
-- ============================================
CREATE TABLE IF NOT EXISTS clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trackable_link_id UUID REFERENCES trackable_links(id) ON DELETE CASCADE,
    
    ip_address INET,
    user_agent TEXT,
    referer TEXT,
    
    country VARCHAR(2),
    city VARCHAR(100),
    device VARCHAR(50),
    browser VARCHAR(50),
    
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 8. TRANSACTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    affiliation_id UUID REFERENCES affiliations(id) ON DELETE CASCADE,
    
    order_id VARCHAR(255),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'MAD',
    
    commission_amount DECIMAL(15, 2) NOT NULL,
    commission_rate DECIMAL(5, 2) NOT NULL,
    
    status VARCHAR(50) CHECK (status IN ('pending', 'approved', 'rejected', 'paid')) DEFAULT 'pending',
    
    customer_info JSONB,
    
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    paid_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEX POUR PERFORMANCE
-- ============================================
CREATE INDEX IF NOT EXISTS idx_merchants_user_id ON merchants(user_id);
CREATE INDEX IF NOT EXISTS idx_influencers_user_id ON influencers(user_id);
CREATE INDEX IF NOT EXISTS idx_products_merchant_id ON products(merchant_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_merchant_id ON campaigns(merchant_id);
CREATE INDEX IF NOT EXISTS idx_affiliations_influencer_id ON affiliations(influencer_id);
CREATE INDEX IF NOT EXISTS idx_affiliations_merchant_id ON affiliations(merchant_id);
CREATE INDEX IF NOT EXISTS idx_trackable_links_influencer_id ON trackable_links(influencer_id);
CREATE INDEX IF NOT EXISTS idx_clicks_trackable_link_id ON clicks(trackable_link_id);
CREATE INDEX IF NOT EXISTS idx_transactions_affiliation_id ON transactions(affiliation_id);

-- ============================================
-- FIN DU SCRIPT
-- ============================================

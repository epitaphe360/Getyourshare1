-- ============================================
-- SCRIPT SÉCURISÉ - AJOUTE SEULEMENT CE QUI MANQUE
-- ============================================
-- Ce script vérifie et crée uniquement les tables/colonnes manquantes
-- Pas d'erreur si une table existe déjà

-- ============================================
-- 1. VÉRIFIER ET CRÉER MERCHANTS
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' AND table_name = 'merchants') THEN
        CREATE TABLE merchants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL UNIQUE,
            company_name VARCHAR(255) NOT NULL,
            industry VARCHAR(100),
            category VARCHAR(100),
            address TEXT,
            tax_id VARCHAR(50),
            website VARCHAR(255),
            logo_url TEXT,
            description TEXT,
            subscription_plan VARCHAR(50) DEFAULT 'free',
            subscription_status VARCHAR(50) DEFAULT 'active',
            commission_rate DECIMAL(5, 2) DEFAULT 5.00,
            monthly_fee DECIMAL(10, 2) DEFAULT 0.00,
            total_sales DECIMAL(15, 2) DEFAULT 0.00,
            total_commission_paid DECIMAL(15, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Table merchants créée';
    ELSE
        RAISE NOTICE 'Table merchants existe déjà';
    END IF;
END $$;

-- ============================================
-- 2. VÉRIFIER ET CRÉER INFLUENCERS
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' AND table_name = 'influencers') THEN
        CREATE TABLE influencers (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL UNIQUE,
            username VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(255),
            bio TEXT,
            profile_picture_url TEXT,
            category VARCHAR(100),
            influencer_type VARCHAR(50) DEFAULT 'nano',
            audience_size INTEGER DEFAULT 0,
            engagement_rate DECIMAL(5, 2) DEFAULT 0.00,
            subscription_plan VARCHAR(50) DEFAULT 'starter',
            subscription_status VARCHAR(50) DEFAULT 'active',
            platform_fee_rate DECIMAL(5, 2) DEFAULT 5.00,
            monthly_fee DECIMAL(10, 2) DEFAULT 0.00,
            social_links JSONB DEFAULT '{}',
            total_clicks INTEGER DEFAULT 0,
            total_sales INTEGER DEFAULT 0,
            total_earnings DECIMAL(15, 2) DEFAULT 0.00,
            balance DECIMAL(15, 2) DEFAULT 0.00,
            payment_method VARCHAR(50),
            payment_details JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Table influencers créée';
    ELSE
        RAISE NOTICE 'Table influencers existe déjà';
    END IF;
END $$;

-- ============================================
-- 3. VÉRIFIER ET CRÉER PRODUCTS
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' AND table_name = 'products') THEN
        CREATE TABLE products (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            price DECIMAL(10, 2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'MAD',
            commission_rate DECIMAL(5, 2) NOT NULL,
            commission_type VARCHAR(20) DEFAULT 'percentage',
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
        RAISE NOTICE 'Table products créée';
    ELSE
        RAISE NOTICE 'Table products existe déjà';
    END IF;
END $$;

-- ============================================
-- 4. VÉRIFIER ET CRÉER CAMPAIGNS
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' AND table_name = 'campaigns') THEN
        CREATE TABLE campaigns (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            campaign_type VARCHAR(50) DEFAULT 'product',
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            commission_rate DECIMAL(5, 2) NOT NULL,
            budget DECIMAL(15, 2),
            target_audience JSONB,
            requirements JSONB,
            status VARCHAR(50) DEFAULT 'draft',
            total_clicks INTEGER DEFAULT 0,
            total_conversions INTEGER DEFAULT 0,
            total_revenue DECIMAL(15, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Table campaigns créée';
    ELSE
        RAISE NOTICE 'Table campaigns existe déjà';
    END IF;
END $$;

-- ============================================
-- 5. VÉRIFIER ET CRÉER AFFILIATIONS
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' AND table_name = 'affiliations') THEN
        CREATE TABLE affiliations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
            merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
            campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
            status VARCHAR(50) DEFAULT 'pending',
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
        RAISE NOTICE 'Table affiliations créée';
    ELSE
        RAISE NOTICE 'Table affiliations existe déjà';
    END IF;
END $$;

-- ============================================
-- 6. VÉRIFIER ET CRÉER TRACKABLE_LINKS
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' AND table_name = 'trackable_links') THEN
        CREATE TABLE trackable_links (
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
        RAISE NOTICE 'Table trackable_links créée';
    ELSE
        RAISE NOTICE 'Table trackable_links existe déjà';
    END IF;
END $$;

-- ============================================
-- 7. VÉRIFIER ET CRÉER CLICKS
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' AND table_name = 'clicks') THEN
        CREATE TABLE clicks (
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
        RAISE NOTICE 'Table clicks créée';
    ELSE
        RAISE NOTICE 'Table clicks existe déjà';
    END IF;
END $$;

-- ============================================
-- 8. VÉRIFIER ET CRÉER TRANSACTIONS
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' AND table_name = 'transactions') THEN
        CREATE TABLE transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            affiliation_id UUID REFERENCES affiliations(id) ON DELETE CASCADE,
            order_id VARCHAR(255),
            amount DECIMAL(15, 2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'MAD',
            commission_amount DECIMAL(15, 2) NOT NULL,
            commission_rate DECIMAL(5, 2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            customer_info JSONB,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            paid_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Table transactions créée';
    ELSE
        RAISE NOTICE 'Table transactions existe déjà';
    END IF;
END $$;

-- ============================================
-- 9. CRÉER LES INDEX (VÉRIFICATION TABLE + COLONNE)
-- ============================================
DO $$
BEGIN
    -- Index pour merchants.user_id
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'merchants' AND column_name = 'user_id') THEN
        CREATE INDEX IF NOT EXISTS idx_merchants_user_id ON merchants(user_id);
    END IF;
    
    -- Index pour influencers.user_id
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'influencers' AND column_name = 'user_id') THEN
        CREATE INDEX IF NOT EXISTS idx_influencers_user_id ON influencers(user_id);
    END IF;
    
    -- Index pour products.merchant_id
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'products' AND column_name = 'merchant_id') THEN
        CREATE INDEX IF NOT EXISTS idx_products_merchant_id ON products(merchant_id);
    END IF;
    
    -- Index pour campaigns.merchant_id
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'campaigns' AND column_name = 'merchant_id') THEN
        CREATE INDEX IF NOT EXISTS idx_campaigns_merchant_id ON campaigns(merchant_id);
    END IF;
    
    -- Index pour affiliations
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'affiliations' AND column_name = 'influencer_id') THEN
        CREATE INDEX IF NOT EXISTS idx_affiliations_influencer_id ON affiliations(influencer_id);
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'affiliations' AND column_name = 'merchant_id') THEN
        CREATE INDEX IF NOT EXISTS idx_affiliations_merchant_id ON affiliations(merchant_id);
    END IF;
    
    -- Index pour trackable_links.influencer_id
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'trackable_links' AND column_name = 'influencer_id') THEN
        CREATE INDEX IF NOT EXISTS idx_trackable_links_influencer_id ON trackable_links(influencer_id);
    END IF;
    
    -- Index pour clicks.trackable_link_id
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'clicks' AND column_name = 'trackable_link_id') THEN
        CREATE INDEX IF NOT EXISTS idx_clicks_trackable_link_id ON clicks(trackable_link_id);
    END IF;
    
    -- Index pour transactions.affiliation_id
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'transactions' AND column_name = 'affiliation_id') THEN
        CREATE INDEX IF NOT EXISTS idx_transactions_affiliation_id ON transactions(affiliation_id);
    END IF;
    
    RAISE NOTICE '✅ Index créés avec succès';
END $$;

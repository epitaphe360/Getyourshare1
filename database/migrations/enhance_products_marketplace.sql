-- ============================================
-- Enhancement Products Table - Groupon-Style Marketplace
-- Migration pour améliorer la table products
-- ============================================

-- Ajouter colonnes pour marketplace
ALTER TABLE products
ADD COLUMN IF NOT EXISTS highlights JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS included TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS conditions TEXT,
ADD COLUMN IF NOT EXISTS how_it_works TEXT,
ADD COLUMN IF NOT EXISTS faq JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS location JSONB,
ADD COLUMN IF NOT EXISTS expiry_date TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS original_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS discounted_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS discount_percentage INTEGER,
ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_deal_of_day BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS min_purchase INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS max_purchase INTEGER,
ADD COLUMN IF NOT EXISTS stock_quantity INTEGER,
ADD COLUMN IF NOT EXISTS sold_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS views_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS rating_average DECIMAL(3,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS rating_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS images JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS video_url TEXT,
ADD COLUMN IF NOT EXISTS is_service BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS service_duration INTEGER,
ADD COLUMN IF NOT EXISTS service_location_required BOOLEAN DEFAULT FALSE;

-- Commentaires
COMMENT ON COLUMN products.highlights IS 'Points clés du produit/service (JSONB array)';
COMMENT ON COLUMN products.included IS 'Ce qui est inclus dans l''offre (array text)';
COMMENT ON COLUMN products.conditions IS 'Conditions d''utilisation';
COMMENT ON COLUMN products.how_it_works IS 'Comment ça marche (étapes)';
COMMENT ON COLUMN products.faq IS 'Questions fréquentes (JSONB array: {question, answer})';
COMMENT ON COLUMN products.location IS 'Localisation si service local: {address, city, lat, lng}';
COMMENT ON COLUMN products.expiry_date IS 'Date expiration de l''offre';
COMMENT ON COLUMN products.original_price IS 'Prix original (avant réduction)';
COMMENT ON COLUMN products.discounted_price IS 'Prix après réduction';
COMMENT ON COLUMN products.discount_percentage IS 'Pourcentage de réduction';
COMMENT ON COLUMN products.is_featured IS 'Produit mis en avant';
COMMENT ON COLUMN products.is_deal_of_day IS 'Deal du jour';
COMMENT ON COLUMN products.images IS 'URLs des images (JSONB array)';
COMMENT ON COLUMN products.video_url IS 'URL vidéo de présentation';
COMMENT ON COLUMN products.is_service IS 'True si service, False si produit physique';
COMMENT ON COLUMN products.service_duration IS 'Durée du service en minutes';

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_products_is_featured ON products(is_featured) WHERE is_featured = TRUE;
CREATE INDEX IF NOT EXISTS idx_products_is_deal_of_day ON products(is_deal_of_day) WHERE is_deal_of_day = TRUE;
CREATE INDEX IF NOT EXISTS idx_products_expiry_date ON products(expiry_date) WHERE expiry_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_discount_percentage ON products(discount_percentage) WHERE discount_percentage > 0;
CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating_average DESC);
CREATE INDEX IF NOT EXISTS idx_products_sold_count ON products(sold_count DESC);

-- ============================================
-- Table: product_reviews (Avis clients)
-- ============================================

CREATE TABLE IF NOT EXISTS product_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Review
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,

    -- Photos/Vidéos review
    images JSONB DEFAULT '[]'::jsonb,

    -- Vérification
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,

    -- Utilité
    helpful_count INTEGER DEFAULT 0,
    unhelpful_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Contrainte: 1 review par user par produit
    UNIQUE(product_id, user_id)
);

CREATE INDEX idx_product_reviews_product_id ON product_reviews(product_id);
CREATE INDEX idx_product_reviews_user_id ON product_reviews(user_id);
CREATE INDEX idx_product_reviews_rating ON product_reviews(rating);
CREATE INDEX idx_product_reviews_is_approved ON product_reviews(is_approved) WHERE is_approved = TRUE;

-- ============================================
-- Table: product_categories (Catégories hiérarchiques)
-- ============================================

CREATE TABLE IF NOT EXISTS product_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES product_categories(id) ON DELETE CASCADE,
    image_url TEXT,
    icon VARCHAR(100),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_product_categories_parent_id ON product_categories(parent_id);
CREATE INDEX idx_product_categories_slug ON product_categories(slug);
CREATE INDEX idx_product_categories_is_active ON product_categories(is_active) WHERE is_active = TRUE;

-- ============================================
-- Table: product_category_mapping
-- ============================================

CREATE TABLE IF NOT EXISTS product_category_mapping (
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES product_categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (product_id, category_id)
);

CREATE INDEX idx_product_category_mapping_product_id ON product_category_mapping(product_id);
CREATE INDEX idx_product_category_mapping_category_id ON product_category_mapping(category_id);

-- ============================================
-- Fonctions: Calcul automatique rating
-- ============================================

CREATE OR REPLACE FUNCTION update_product_rating()
RETURNS TRIGGER AS $$
BEGIN
    -- Recalculer rating moyen et nombre d'avis
    UPDATE products
    SET
        rating_average = (
            SELECT COALESCE(AVG(rating), 0)
            FROM product_reviews
            WHERE product_id = NEW.product_id AND is_approved = TRUE
        ),
        rating_count = (
            SELECT COUNT(*)
            FROM product_reviews
            WHERE product_id = NEW.product_id AND is_approved = TRUE
        ),
        updated_at = NOW()
    WHERE id = NEW.product_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
DROP TRIGGER IF EXISTS trigger_update_product_rating ON product_reviews;
CREATE TRIGGER trigger_update_product_rating
    AFTER INSERT OR UPDATE OR DELETE ON product_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_product_rating();

-- ============================================
-- Fonction: Auto-update discount percentage
-- ============================================

CREATE OR REPLACE FUNCTION calculate_discount_percentage()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.original_price > 0 AND NEW.discounted_price > 0 THEN
        NEW.discount_percentage = ROUND(
            ((NEW.original_price - NEW.discounted_price) / NEW.original_price * 100)::numeric,
            0
        )::integer;
    ELSE
        NEW.discount_percentage = 0;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
DROP TRIGGER IF EXISTS trigger_calculate_discount ON products;
CREATE TRIGGER trigger_calculate_discount
    BEFORE INSERT OR UPDATE OF original_price, discounted_price ON products
    FOR EACH ROW
    EXECUTE FUNCTION calculate_discount_percentage();

-- ============================================
-- View: Products avec toutes les infos
-- ============================================

CREATE OR REPLACE VIEW v_products_full AS
SELECT
    p.*,
    u.email as merchant_email,
    u.first_name as merchant_first_name,
    u.last_name as merchant_last_name,
    -- Catégories (array)
    COALESCE(
        json_agg(DISTINCT jsonb_build_object(
            'id', pc.id,
            'name', pc.name,
            'slug', pc.slug
        )) FILTER (WHERE pc.id IS NOT NULL),
        '[]'::json
    ) as categories,
    -- Stats affiliates
    (SELECT COUNT(*) FROM affiliate_requests WHERE product_id = p.id AND status = 'approved') as active_affiliates_count,
    -- Deal status
    CASE
        WHEN p.expiry_date < NOW() THEN 'expired'
        WHEN p.stock_quantity IS NOT NULL AND p.stock_quantity <= 0 THEN 'sold_out'
        WHEN p.is_active = FALSE THEN 'inactive'
        ELSE 'active'
    END as deal_status
FROM products p
LEFT JOIN users u ON p.merchant_id = u.id
LEFT JOIN product_category_mapping pcm ON p.id = pcm.product_id
LEFT JOIN product_categories pc ON pcm.category_id = pc.id
GROUP BY p.id, u.id;

-- ============================================
-- View: Deals du jour
-- ============================================

CREATE OR REPLACE VIEW v_deals_of_day AS
SELECT *
FROM v_products_full
WHERE is_deal_of_day = TRUE
  AND deal_status = 'active'
  AND (expiry_date IS NULL OR expiry_date > NOW())
ORDER BY discount_percentage DESC, created_at DESC;

-- ============================================
-- View: Produits featured
-- ============================================

CREATE OR REPLACE VIEW v_featured_products AS
SELECT *
FROM v_products_full
WHERE is_featured = TRUE
  AND deal_status = 'active'
ORDER BY sold_count DESC, rating_average DESC;

-- ============================================
-- Fonction: Incrémenter vues produit
-- ============================================

CREATE OR REPLACE FUNCTION increment_product_views(p_product_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE products
    SET views_count = views_count + 1
    WHERE id = p_product_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Fonction: Incrémenter ventes produit
-- ============================================

CREATE OR REPLACE FUNCTION increment_product_sales(p_product_id UUID, p_quantity INTEGER DEFAULT 1)
RETURNS void AS $$
BEGIN
    UPDATE products
    SET
        sold_count = sold_count + p_quantity,
        stock_quantity = CASE
            WHEN stock_quantity IS NOT NULL THEN stock_quantity - p_quantity
            ELSE NULL
        END,
        updated_at = NOW()
    WHERE id = p_product_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Données de test - Catégories
-- ============================================

INSERT INTO product_categories (name, slug, description, icon, display_order) VALUES
('Beauté & Bien-être', 'beaute-bien-etre', 'Soins, spa, coiffure, massage', '💆', 1),
('Restaurants & Food', 'restaurants-food', 'Restaurants, cafés, livraison', '🍔', 2),
('Shopping & Mode', 'shopping-mode', 'Vêtements, accessoires, bijoux', '👗', 3),
('Sport & Fitness', 'sport-fitness', 'Salles de sport, yoga, coaching', '🏋️', 4),
('Loisirs & Divertissement', 'loisirs-divertissement', 'Cinéma, événements, activités', '🎬', 5),
('Voyage & Hôtels', 'voyage-hotels', 'Hébergement, excursions, voyages', '✈️', 6),
('Services Professionnels', 'services-professionnels', 'Formation, consulting, services', '💼', 7),
('Électronique & High-Tech', 'electronique-hightech', 'Gadgets, accessoires tech', '📱', 8)
ON CONFLICT (slug) DO NOTHING;

-- ============================================
-- RLS Policies
-- ============================================

-- Product reviews
ALTER TABLE product_reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY product_reviews_public_select
    ON product_reviews FOR SELECT
    USING (is_approved = TRUE);

CREATE POLICY product_reviews_user_insert
    ON product_reviews FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY product_reviews_user_update
    ON product_reviews FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY product_reviews_admin_all
    ON product_reviews FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Product categories
ALTER TABLE product_categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY product_categories_public_select
    ON product_categories FOR SELECT
    USING (is_active = TRUE);

CREATE POLICY product_categories_admin_all
    ON product_categories FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

COMMENT ON TABLE product_reviews IS 'Avis clients sur les produits/services';
COMMENT ON TABLE product_categories IS 'Catégories hiérarchiques des produits';
COMMENT ON VIEW v_products_full IS 'Vue complète produits avec catégories et stats';
COMMENT ON VIEW v_deals_of_day IS 'Deals du jour actifs';
COMMENT ON VIEW v_featured_products IS 'Produits mis en avant';

-- ============================================
-- DIRECTORIES SYSTEM - Share Your Sales
-- Annuaires Commerciaux & Influenceurs
-- ============================================

-- ============================================
-- Table: commercial_profiles
-- Profils de commerciaux dans l'annuaire
-- ============================================

CREATE TABLE IF NOT EXISTS commercial_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Utilisateur
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Profil professionnel
    headline VARCHAR(255), -- "Commercial B2B spécialisé en tech"
    bio TEXT, -- Description complète
    specialties JSONB DEFAULT '[]'::jsonb, -- ["Tech", "Finance", "Retail"]
    languages JSONB DEFAULT '[]'::jsonb, -- ["French", "English", "Arabic"]

    -- Localisation
    city VARCHAR(100),
    region VARCHAR(100),
    country VARCHAR(3) DEFAULT 'MA', -- Code pays ISO

    -- Expérience
    years_of_experience INTEGER, -- Années d'expérience
    industries JSONB DEFAULT '[]'::jsonb, -- ["E-commerce", "SaaS", "Retail"]

    -- Statistiques de performance
    total_sales INTEGER DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0,
    average_deal_size DECIMAL(10,2),
    success_rate DECIMAL(5,2), -- Pourcentage de deals conclus

    -- Disponibilité
    is_available BOOLEAN DEFAULT TRUE,
    availability_type VARCHAR(50) CHECK (availability_type IN (
        'full_time',
        'part_time',
        'freelance',
        'contract'
    )),

    -- Tarification (optionnel)
    hourly_rate DECIMAL(10,2),
    commission_expectation DECIMAL(5,2), -- Pourcentage de commission souhaité

    -- Portfolio
    portfolio_items JSONB DEFAULT '[]'::jsonb, -- Array de réalisations
    certifications JSONB DEFAULT '[]'::jsonb, -- Certifications professionnelles

    -- Contact
    phone VARCHAR(20),
    linkedin_url VARCHAR(255),
    website_url VARCHAR(255),

    -- Visibilité
    is_public BOOLEAN DEFAULT TRUE, -- Visible dans l'annuaire public
    featured BOOLEAN DEFAULT FALSE, -- Mis en avant
    verified BOOLEAN DEFAULT FALSE, -- Profil vérifié par admin

    -- SEO & Recherche
    search_vector tsvector, -- Pour recherche full-text PostgreSQL
    view_count INTEGER DEFAULT 0,
    contact_count INTEGER DEFAULT 0,

    -- Métadonnées
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_commercial_profiles_user ON commercial_profiles(user_id);
CREATE INDEX idx_commercial_profiles_available ON commercial_profiles(is_available);
CREATE INDEX idx_commercial_profiles_public ON commercial_profiles(is_public);
CREATE INDEX idx_commercial_profiles_featured ON commercial_profiles(featured);
CREATE INDEX idx_commercial_profiles_city ON commercial_profiles(city);
CREATE INDEX idx_commercial_profiles_specialties ON commercial_profiles USING GIN(specialties);
CREATE INDEX idx_commercial_profiles_industries ON commercial_profiles USING GIN(industries);
CREATE INDEX idx_commercial_profiles_search ON commercial_profiles USING GIN(search_vector);

-- Un utilisateur ne peut avoir qu'un seul profil commercial
CREATE UNIQUE INDEX idx_commercial_profiles_unique ON commercial_profiles(user_id);

-- ============================================
-- Table: influencer_profiles
-- Profils d'influenceurs dans l'annuaire
-- ============================================

CREATE TABLE IF NOT EXISTS influencer_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Utilisateur
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Profil d'influenceur
    display_name VARCHAR(255), -- Nom affiché publiquement
    headline VARCHAR(255), -- "Travel & Lifestyle Influencer"
    bio TEXT,

    -- Niches & Catégories
    niches JSONB DEFAULT '[]'::jsonb, -- ["Fashion", "Beauty", "Tech"]
    target_audience VARCHAR(100), -- "Femmes 25-35 ans"
    content_types JSONB DEFAULT '[]'::jsonb, -- ["Photos", "Videos", "Reels", "Stories"]

    -- Localisation
    city VARCHAR(100),
    region VARCHAR(100),
    country VARCHAR(3) DEFAULT 'MA',

    -- Réseaux sociaux
    instagram_handle VARCHAR(100),
    instagram_followers INTEGER,
    instagram_engagement_rate DECIMAL(5,2), -- Pourcentage

    facebook_handle VARCHAR(100),
    facebook_followers INTEGER,
    facebook_engagement_rate DECIMAL(5,2),

    tiktok_handle VARCHAR(100),
    tiktok_followers INTEGER,
    tiktok_engagement_rate DECIMAL(5,2),

    youtube_handle VARCHAR(100),
    youtube_subscribers INTEGER,
    youtube_avg_views INTEGER,

    -- Statistiques globales
    total_followers INTEGER GENERATED ALWAYS AS (
        COALESCE(instagram_followers, 0) +
        COALESCE(facebook_followers, 0) +
        COALESCE(tiktok_followers, 0) +
        COALESCE(youtube_subscribers, 0)
    ) STORED,

    average_engagement_rate DECIMAL(5,2), -- Moyenne pondérée

    -- Performance
    total_campaigns INTEGER DEFAULT 0,
    total_sales_generated INTEGER DEFAULT 0,
    total_revenue_generated DECIMAL(12,2) DEFAULT 0,
    average_conversion_rate DECIMAL(5,2),

    -- Tarification
    rate_per_post DECIMAL(10,2),
    rate_per_story DECIMAL(10,2),
    rate_per_video DECIMAL(10,2),
    preferred_commission_rate DECIMAL(5,2), -- Pourcentage préféré

    -- Portfolio
    portfolio_items JSONB DEFAULT '[]'::jsonb, -- Array de campagnes précédentes
    content_samples JSONB DEFAULT '[]'::jsonb, -- URLs d'exemples de contenu

    -- Disponibilité
    is_available BOOLEAN DEFAULT TRUE,
    accepts_affiliate BOOLEAN DEFAULT TRUE, -- Accepte les programmes d'affiliation
    accepts_sponsored BOOLEAN DEFAULT TRUE, -- Accepte les posts sponsorisés
    minimum_campaign_budget DECIMAL(10,2), -- Budget minimum accepté

    -- Contact
    email VARCHAR(255),
    phone VARCHAR(20),

    -- Visibilité
    is_public BOOLEAN DEFAULT TRUE,
    featured BOOLEAN DEFAULT FALSE,
    verified BOOLEAN DEFAULT FALSE, -- Badge vérifié

    -- SEO & Recherche
    search_vector tsvector,
    view_count INTEGER DEFAULT 0,
    contact_count INTEGER DEFAULT 0,

    -- Métadonnées
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_influencer_profiles_user ON influencer_profiles(user_id);
CREATE INDEX idx_influencer_profiles_available ON influencer_profiles(is_available);
CREATE INDEX idx_influencer_profiles_public ON influencer_profiles(is_public);
CREATE INDEX idx_influencer_profiles_featured ON influencer_profiles(featured);
CREATE INDEX idx_influencer_profiles_niches ON influencer_profiles USING GIN(niches);
CREATE INDEX idx_influencer_profiles_followers ON influencer_profiles(total_followers DESC);
CREATE INDEX idx_influencer_profiles_engagement ON influencer_profiles(average_engagement_rate DESC);
CREATE INDEX idx_influencer_profiles_search ON influencer_profiles USING GIN(search_vector);

-- Un utilisateur ne peut avoir qu'un seul profil influenceur
CREATE UNIQUE INDEX idx_influencer_profiles_unique ON influencer_profiles(user_id);

-- ============================================
-- Table: collaboration_requests
-- Demandes de collaboration entre entreprises et commerciaux/influenceurs
-- ============================================

CREATE TABLE IF NOT EXISTS collaboration_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Qui demande (entreprise)
    company_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- À qui (commercial ou influenceur)
    target_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_type VARCHAR(50) NOT NULL CHECK (target_type IN ('commercial', 'influencer')),

    -- Détails de la demande
    message TEXT NOT NULL, -- Message de l'entreprise
    campaign_details JSONB, -- Détails de la campagne proposée

    -- Conditions proposées
    proposed_commission_rate DECIMAL(5,2),
    proposed_budget DECIMAL(10,2),
    proposed_duration_days INTEGER,

    -- Statut
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
        'pending',      -- En attente de réponse
        'accepted',     -- Acceptée
        'declined',     -- Refusée
        'negotiating',  -- En négociation
        'completed',    -- Collaboration terminée
        'canceled'      -- Annulée
    )),

    -- Réponse
    response_message TEXT,
    responded_at TIMESTAMP WITH TIME ZONE,

    -- Métadonnées
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_collaboration_requests_company ON collaboration_requests(company_id);
CREATE INDEX idx_collaboration_requests_target ON collaboration_requests(target_user_id);
CREATE INDEX idx_collaboration_requests_status ON collaboration_requests(status);
CREATE INDEX idx_collaboration_requests_type ON collaboration_requests(target_type);

-- ============================================
-- Table: profile_reviews
-- Avis et notes pour commerciaux/influenceurs
-- ============================================

CREATE TABLE IF NOT EXISTS profile_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Profil évalué
    profile_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_type VARCHAR(50) NOT NULL CHECK (profile_type IN ('commercial', 'influencer')),

    -- Qui évalue (entreprise)
    reviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Évaluation
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,

    -- Critères spécifiques (1-5)
    professionalism_rating INTEGER CHECK (professionalism_rating >= 1 AND professionalism_rating <= 5),
    communication_rating INTEGER CHECK (communication_rating >= 1 AND communication_rating <= 5),
    results_rating INTEGER CHECK (results_rating >= 1 AND results_rating <= 5),

    -- Recommandation
    would_work_again BOOLEAN,

    -- Lié à une collaboration ?
    collaboration_request_id UUID REFERENCES collaboration_requests(id),

    -- Visibilité
    is_public BOOLEAN DEFAULT TRUE,
    verified_purchase BOOLEAN DEFAULT FALSE, -- A vraiment travaillé ensemble

    -- Réponse du profil
    response TEXT,
    response_date TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_profile_reviews_profile ON profile_reviews(profile_user_id);
CREATE INDEX idx_profile_reviews_reviewer ON profile_reviews(reviewer_id);
CREATE INDEX idx_profile_reviews_rating ON profile_reviews(rating DESC);
CREATE INDEX idx_profile_reviews_public ON profile_reviews(is_public);

-- Un utilisateur ne peut évaluer un profil qu'une fois
CREATE UNIQUE INDEX idx_profile_reviews_unique ON profile_reviews(profile_user_id, reviewer_id);

-- ============================================
-- Triggers: Auto-update updated_at
-- ============================================

CREATE TRIGGER trigger_commercial_profiles_updated_at
    BEFORE UPDATE ON commercial_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_influencer_profiles_updated_at
    BEFORE UPDATE ON influencer_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_collaboration_requests_updated_at
    BEFORE UPDATE ON collaboration_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_profile_reviews_updated_at
    BEFORE UPDATE ON profile_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- Triggers: Update search vectors
-- ============================================

CREATE OR REPLACE FUNCTION update_commercial_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('french', COALESCE(NEW.headline, '')), 'A') ||
        setweight(to_tsvector('french', COALESCE(NEW.bio, '')), 'B') ||
        setweight(to_tsvector('french', COALESCE(NEW.city, '')), 'C') ||
        setweight(to_tsvector('french', array_to_string(ARRAY(SELECT jsonb_array_elements_text(NEW.specialties)), ' ')), 'B') ||
        setweight(to_tsvector('french', array_to_string(ARRAY(SELECT jsonb_array_elements_text(NEW.industries)), ' ')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_commercial_search_vector
    BEFORE INSERT OR UPDATE ON commercial_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_commercial_search_vector();

CREATE OR REPLACE FUNCTION update_influencer_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('french', COALESCE(NEW.display_name, '')), 'A') ||
        setweight(to_tsvector('french', COALESCE(NEW.headline, '')), 'A') ||
        setweight(to_tsvector('french', COALESCE(NEW.bio, '')), 'B') ||
        setweight(to_tsvector('french', COALESCE(NEW.city, '')), 'C') ||
        setweight(to_tsvector('french', array_to_string(ARRAY(SELECT jsonb_array_elements_text(NEW.niches)), ' ')), 'A');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_influencer_search_vector
    BEFORE INSERT OR UPDATE ON influencer_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_influencer_search_vector();

-- ============================================
-- Functions: Calculate average ratings
-- ============================================

CREATE OR REPLACE FUNCTION get_profile_average_rating(
    p_user_id UUID,
    p_profile_type VARCHAR
) RETURNS DECIMAL AS $$
DECLARE
    v_avg_rating DECIMAL;
BEGIN
    SELECT AVG(rating)::DECIMAL(3,2)
    INTO v_avg_rating
    FROM profile_reviews
    WHERE profile_user_id = p_user_id
      AND profile_type = p_profile_type
      AND is_public = TRUE;

    RETURN COALESCE(v_avg_rating, 0);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_profile_review_count(
    p_user_id UUID,
    p_profile_type VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM profile_reviews
    WHERE profile_user_id = p_user_id
      AND profile_type = p_profile_type
      AND is_public = TRUE;

    RETURN COALESCE(v_count, 0);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- RLS Policies
-- ============================================

ALTER TABLE commercial_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE influencer_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE collaboration_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_reviews ENABLE ROW LEVEL SECURITY;

-- Commercial Profiles: Lecture publique des profils publics
CREATE POLICY commercial_profiles_public_read
    ON commercial_profiles FOR SELECT
    USING (is_public = TRUE);

-- Commercial Profiles: Utilisateur gère son propre profil
CREATE POLICY commercial_profiles_user_all
    ON commercial_profiles FOR ALL
    USING (user_id = auth.uid());

-- Commercial Profiles: Admin tout voir
CREATE POLICY commercial_profiles_admin_all
    ON commercial_profiles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Influencer Profiles: Lecture publique des profils publics
CREATE POLICY influencer_profiles_public_read
    ON influencer_profiles FOR SELECT
    USING (is_public = TRUE);

-- Influencer Profiles: Utilisateur gère son propre profil
CREATE POLICY influencer_profiles_user_all
    ON influencer_profiles FOR ALL
    USING (user_id = auth.uid());

-- Influencer Profiles: Admin tout voir
CREATE POLICY influencer_profiles_admin_all
    ON influencer_profiles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Collaboration Requests: Entreprise voit ses demandes
CREATE POLICY collaboration_requests_company_all
    ON collaboration_requests FOR ALL
    USING (company_id = auth.uid());

-- Collaboration Requests: Commercial/Influenceur voit les demandes le concernant
CREATE POLICY collaboration_requests_target_select
    ON collaboration_requests FOR SELECT
    USING (target_user_id = auth.uid());

-- Collaboration Requests: Commercial/Influenceur peut répondre
CREATE POLICY collaboration_requests_target_update
    ON collaboration_requests FOR UPDATE
    USING (target_user_id = auth.uid());

-- Profile Reviews: Lecture publique des avis publics
CREATE POLICY profile_reviews_public_read
    ON profile_reviews FOR SELECT
    USING (is_public = TRUE);

-- Profile Reviews: Entreprise crée des avis
CREATE POLICY profile_reviews_reviewer_create
    ON profile_reviews FOR INSERT
    WITH CHECK (
        reviewer_id = auth.uid() AND
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'merchant')
    );

-- Profile Reviews: Profil peut répondre
CREATE POLICY profile_reviews_profile_respond
    ON profile_reviews FOR UPDATE
    USING (profile_user_id = auth.uid());

-- ============================================
-- Views
-- ============================================

-- Vue: Profils commerciaux avec statistiques
CREATE OR REPLACE VIEW v_commercial_profiles_public AS
SELECT
    cp.*,
    u.first_name,
    u.last_name,
    u.email,
    u.profile_picture,
    get_profile_average_rating(cp.user_id, 'commercial') as average_rating,
    get_profile_review_count(cp.user_id, 'commercial') as review_count
FROM commercial_profiles cp
JOIN users u ON cp.user_id = u.id
WHERE cp.is_public = TRUE;

-- Vue: Profils influenceurs avec statistiques
CREATE OR REPLACE VIEW v_influencer_profiles_public AS
SELECT
    ip.*,
    u.first_name,
    u.last_name,
    u.email,
    u.profile_picture,
    get_profile_average_rating(ip.user_id, 'influencer') as average_rating,
    get_profile_review_count(ip.user_id, 'influencer') as review_count
FROM influencer_profiles ip
JOIN users u ON ip.user_id = u.id
WHERE ip.is_public = TRUE;

-- ============================================
-- Commentaires
-- ============================================

COMMENT ON TABLE commercial_profiles IS 'Annuaire des commerciaux - Profils publics recherchables';
COMMENT ON TABLE influencer_profiles IS 'Annuaire des influenceurs - Profils publics avec stats réseaux sociaux';
COMMENT ON TABLE collaboration_requests IS 'Demandes de collaboration entre entreprises et commerciaux/influenceurs';
COMMENT ON TABLE profile_reviews IS 'Avis et évaluations des commerciaux/influenceurs par les entreprises';

COMMENT ON COLUMN influencer_profiles.total_followers IS 'Somme automatique des followers sur tous les réseaux (colonne générée)';
COMMENT ON COLUMN commercial_profiles.search_vector IS 'Index de recherche full-text PostgreSQL (auto-généré)';
COMMENT ON COLUMN influencer_profiles.search_vector IS 'Index de recherche full-text PostgreSQL (auto-généré)';

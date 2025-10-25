-- ============================================
-- Table: social_media_publications
-- Publications automatiques sur réseaux sociaux
-- ============================================

CREATE TABLE IF NOT EXISTS social_media_publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,

    -- Plateforme
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram', 'tiktok', 'facebook', 'twitter', 'linkedin')),
    post_type VARCHAR(50) NOT NULL, -- feed, story, reel, video, etc.

    -- Post details
    platform_post_id VARCHAR(255),  -- ID du post sur la plateforme
    caption TEXT,
    media_url TEXT,
    affiliate_link TEXT,

    -- Stats (à mettre à jour via webhooks ou API)
    views_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    clicks_count INTEGER DEFAULT 0,  -- Clics sur le lien

    -- Status
    status VARCHAR(50) DEFAULT 'published' CHECK (status IN ('draft', 'scheduled', 'published', 'failed', 'deleted')),

    -- Timestamps
    published_at TIMESTAMP WITH TIME ZONE,
    scheduled_for TIMESTAMP WITH TIME ZONE,  -- Publication programmée
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_social_publications_user_id ON social_media_publications(user_id);
CREATE INDEX idx_social_publications_product_id ON social_media_publications(product_id);
CREATE INDEX idx_social_publications_platform ON social_media_publications(platform);
CREATE INDEX idx_social_publications_status ON social_media_publications(status);
CREATE INDEX idx_social_publications_published_at ON social_media_publications(published_at);

-- ============================================
-- Trigger: Auto-update updated_at
-- ============================================

CREATE TRIGGER trigger_social_publications_updated_at
    BEFORE UPDATE ON social_media_publications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- RLS Policies
-- ============================================

ALTER TABLE social_media_publications ENABLE ROW LEVEL SECURITY;

-- Users voient leurs publications
CREATE POLICY social_publications_user_select
    ON social_media_publications FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY social_publications_user_insert
    ON social_media_publications FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY social_publications_user_update
    ON social_media_publications FOR UPDATE
    USING (auth.uid() = user_id);

-- Admins voient tout
CREATE POLICY social_publications_admin_all
    ON social_media_publications FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

COMMENT ON TABLE social_media_publications IS 'Publications automatiques sur réseaux sociaux';

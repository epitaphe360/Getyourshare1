-- ============================================
-- MIGRATION: Intégration Réseaux Sociaux
-- Description: Tables pour connecter les comptes sociaux des influenceurs
--              et récupérer automatiquement leurs statistiques
-- ============================================

-- Table pour stocker les connexions aux réseaux sociaux
CREATE TABLE IF NOT EXISTS social_media_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relation utilisateur
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,

    -- Plateforme sociale
    platform VARCHAR(50) NOT NULL CHECK (platform IN (
        'instagram', 'tiktok', 'facebook', 'youtube', 'twitter', 'linkedin', 'snapchat', 'pinterest'
    )),

    -- Identifiants plateforme
    platform_user_id VARCHAR(255) NOT NULL, -- ID utilisateur sur la plateforme
    platform_username VARCHAR(255),          -- @username sur la plateforme
    platform_display_name VARCHAR(255),      -- Nom affiché

    -- Tokens OAuth (CHIFFRÉ!)
    access_token_encrypted TEXT NOT NULL,    -- Token d'accès chiffré
    refresh_token_encrypted TEXT,            -- Token de refresh (si applicable)
    token_type VARCHAR(50) DEFAULT 'Bearer',

    -- Expiration tokens
    token_expires_at TIMESTAMP,              -- Quand le token expire
    last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Scopes et permissions
    granted_scopes TEXT[],                   -- Permissions accordées

    -- Statut connexion
    connection_status VARCHAR(20) DEFAULT 'active' CHECK (connection_status IN (
        'active', 'expired', 'revoked', 'error'
    )),
    connection_error TEXT,                   -- Dernière erreur rencontrée

    -- Métadonnées
    profile_picture_url TEXT,
    profile_url TEXT,
    bio TEXT,

    -- Auto-refresh settings
    auto_refresh_enabled BOOLEAN DEFAULT TRUE,
    refresh_frequency_hours INTEGER DEFAULT 24, -- Rafraîchir toutes les 24h

    -- Timestamps
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Un utilisateur ne peut avoir qu'une connexion active par plateforme
    UNIQUE(user_id, platform, connection_status)
);

-- Table pour stocker l'historique des statistiques
CREATE TABLE IF NOT EXISTS social_media_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relation connexion
    connection_id UUID REFERENCES social_media_connections(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    platform VARCHAR(50) NOT NULL,

    -- Statistiques d'audience
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    total_posts INTEGER DEFAULT 0,
    total_videos INTEGER DEFAULT 0,

    -- Statistiques d'engagement
    total_likes BIGINT DEFAULT 0,
    total_comments BIGINT DEFAULT 0,
    total_shares BIGINT DEFAULT 0,
    total_saves BIGINT DEFAULT 0,
    total_views BIGINT DEFAULT 0,

    -- Métriques calculées
    engagement_rate DECIMAL(5,2) DEFAULT 0.00, -- Taux d'engagement (%)
    average_likes_per_post DECIMAL(10,2) DEFAULT 0.00,
    average_comments_per_post DECIMAL(10,2) DEFAULT 0.00,
    average_views_per_post DECIMAL(10,2) DEFAULT 0.00,

    -- Croissance (depuis dernière sync)
    followers_growth INTEGER DEFAULT 0,
    engagement_growth DECIMAL(5,2) DEFAULT 0.00,

    -- Reach et impressions (Instagram/Facebook)
    reach_last_30_days BIGINT,
    impressions_last_30_days BIGINT,

    -- Données brutes (JSON flexible par plateforme)
    raw_data JSONB DEFAULT '{}'::jsonb,

    -- Métadonnées
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour l'historique des publications (posts/vidéos)
CREATE TABLE IF NOT EXISTS social_media_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relation
    connection_id UUID REFERENCES social_media_connections(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    platform VARCHAR(50) NOT NULL,

    -- Identifiant du post sur la plateforme
    platform_post_id VARCHAR(255) NOT NULL,
    post_type VARCHAR(50), -- 'photo', 'video', 'carousel', 'reel', 'story'

    -- Contenu
    caption TEXT,
    media_url TEXT,
    thumbnail_url TEXT,
    permalink TEXT,

    -- Statistiques du post
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    saves_count INTEGER DEFAULT 0,
    views_count BIGINT DEFAULT 0,
    plays_count BIGINT DEFAULT 0,

    -- Engagement spécifique
    engagement_rate DECIMAL(5,2),

    -- Timestamps
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(connection_id, platform_post_id)
);

-- Table pour les logs de synchronisation (audit trail)
CREATE TABLE IF NOT EXISTS social_media_sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relation
    connection_id UUID REFERENCES social_media_connections(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    platform VARCHAR(50) NOT NULL,

    -- Type de sync
    sync_type VARCHAR(50) NOT NULL CHECK (sync_type IN (
        'manual', 'automatic', 'scheduled', 'token_refresh'
    )),

    -- Résultat
    sync_status VARCHAR(20) NOT NULL CHECK (sync_status IN (
        'success', 'partial_success', 'failed'
    )),

    -- Détails
    stats_fetched BOOLEAN DEFAULT FALSE,
    posts_fetched INTEGER DEFAULT 0,
    errors_encountered TEXT[],
    error_message TEXT,

    -- Performance
    duration_ms INTEGER, -- Durée en millisecondes
    api_calls_made INTEGER DEFAULT 0,

    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEX POUR PERFORMANCES
-- ============================================

-- Connexions
CREATE INDEX IF NOT EXISTS idx_social_connections_user ON social_media_connections(user_id);
CREATE INDEX IF NOT EXISTS idx_social_connections_influencer ON social_media_connections(influencer_id);
CREATE INDEX IF NOT EXISTS idx_social_connections_platform ON social_media_connections(platform);
CREATE INDEX IF NOT EXISTS idx_social_connections_status ON social_media_connections(connection_status);
CREATE INDEX IF NOT EXISTS idx_social_connections_expires ON social_media_connections(token_expires_at) WHERE connection_status = 'active';
CREATE INDEX IF NOT EXISTS idx_social_connections_refresh ON social_media_connections(last_synced_at) WHERE auto_refresh_enabled = TRUE;

-- Stats (partitionnement recommandé par date pour grandes volumétries)
CREATE INDEX IF NOT EXISTS idx_social_stats_connection ON social_media_stats(connection_id);
CREATE INDEX IF NOT EXISTS idx_social_stats_user ON social_media_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_social_stats_platform ON social_media_stats(platform);
CREATE INDEX IF NOT EXISTS idx_social_stats_synced ON social_media_stats(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_stats_engagement ON social_media_stats(engagement_rate DESC);

-- Posts
CREATE INDEX IF NOT EXISTS idx_social_posts_connection ON social_media_posts(connection_id);
CREATE INDEX IF NOT EXISTS idx_social_posts_user ON social_media_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON social_media_posts(platform, platform_post_id);
CREATE INDEX IF NOT EXISTS idx_social_posts_published ON social_media_posts(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_posts_engagement ON social_media_posts(engagement_rate DESC);

-- Logs
CREATE INDEX IF NOT EXISTS idx_sync_logs_connection ON social_media_sync_logs(connection_id);
CREATE INDEX IF NOT EXISTS idx_sync_logs_user ON social_media_sync_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_logs_status ON social_media_sync_logs(sync_status);
CREATE INDEX IF NOT EXISTS idx_sync_logs_created ON social_media_sync_logs(created_at DESC);

-- ============================================
-- FONCTIONS AUTOMATIQUES
-- ============================================

-- Fonction: Mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_social_connections_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_social_connections_updated_at
    BEFORE UPDATE ON social_media_connections
    FOR EACH ROW
    EXECUTE FUNCTION update_social_connections_updated_at();

-- Fonction: Calculer la croissance depuis dernière sync
CREATE OR REPLACE FUNCTION calculate_social_growth(p_connection_id UUID, p_new_followers INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_previous_followers INTEGER;
    v_growth INTEGER;
BEGIN
    -- Récupérer le nombre de followers de la dernière sync
    SELECT followers_count INTO v_previous_followers
    FROM social_media_stats
    WHERE connection_id = p_connection_id
    ORDER BY synced_at DESC
    LIMIT 1 OFFSET 1;

    IF v_previous_followers IS NULL THEN
        RETURN 0; -- Première sync
    END IF;

    v_growth := p_new_followers - v_previous_followers;
    RETURN v_growth;
END;
$$ LANGUAGE plpgsql;

-- Fonction: Mettre à jour le profil influenceur après sync
CREATE OR REPLACE FUNCTION sync_influencer_profile_from_social()
RETURNS TRIGGER AS $$
BEGIN
    -- Mettre à jour automatiquement le profil influenceur avec les dernières stats
    UPDATE influencers
    SET
        audience_size = (
            SELECT SUM(followers_count)
            FROM social_media_stats sms
            JOIN social_media_connections smc ON sms.connection_id = smc.id
            WHERE smc.influencer_id = (
                SELECT influencer_id
                FROM social_media_connections
                WHERE id = NEW.connection_id
            )
            AND sms.synced_at >= NOW() - INTERVAL '7 days'
            ORDER BY sms.synced_at DESC
            LIMIT 1
        ),
        engagement_rate = NEW.engagement_rate,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = (
        SELECT influencer_id
        FROM social_media_connections
        WHERE id = NEW.connection_id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sync_influencer_profile
    AFTER INSERT ON social_media_stats
    FOR EACH ROW
    EXECUTE FUNCTION sync_influencer_profile_from_social();

-- Fonction: Identifier les connexions expirant bientôt
CREATE OR REPLACE FUNCTION get_expiring_connections(p_days_before INTEGER DEFAULT 7)
RETURNS TABLE (
    connection_id UUID,
    user_id UUID,
    platform VARCHAR(50),
    expires_at TIMESTAMP,
    days_until_expiry INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        id,
        social_media_connections.user_id,
        social_media_connections.platform,
        token_expires_at,
        EXTRACT(DAY FROM (token_expires_at - CURRENT_TIMESTAMP))::INTEGER
    FROM social_media_connections
    WHERE connection_status = 'active'
    AND token_expires_at IS NOT NULL
    AND token_expires_at <= CURRENT_TIMESTAMP + (p_days_before || ' days')::INTERVAL
    ORDER BY token_expires_at ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

ALTER TABLE social_media_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_media_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_media_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_media_sync_logs ENABLE ROW LEVEL SECURITY;

-- Politique: Les utilisateurs voient leurs propres connexions
CREATE POLICY "Users can view their own social connections" ON social_media_connections
    FOR SELECT USING (
        user_id::text = auth.uid()::text
    );

CREATE POLICY "Users can manage their own social connections" ON social_media_connections
    FOR ALL USING (
        user_id::text = auth.uid()::text
    );

-- Politique: Les utilisateurs voient leurs propres stats
CREATE POLICY "Users can view their own social stats" ON social_media_stats
    FOR SELECT USING (
        user_id::text = auth.uid()::text
    );

-- Politique: Marchands peuvent voir les stats des influenceurs affiliés
CREATE POLICY "Merchants can view affiliated influencers stats" ON social_media_stats
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM trackable_links tl
            JOIN merchants m ON tl.merchant_id = m.id
            JOIN users u ON m.user_id = u.id
            JOIN influencers i ON tl.influencer_id = i.id
            WHERE i.user_id = social_media_stats.user_id
            AND u.id::text = auth.uid()::text
        )
    );

-- Politique: Les utilisateurs voient leurs propres posts
CREATE POLICY "Users can view their own social posts" ON social_media_posts
    FOR SELECT USING (
        user_id::text = auth.uid()::text
    );

-- Politique: Les admins voient tout
CREATE POLICY "Admins can view all social data" ON social_media_connections
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id::text = auth.uid()::text
            AND role = 'admin'
        )
    );

CREATE POLICY "Admins can view all stats" ON social_media_stats
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id::text = auth.uid()::text
            AND role = 'admin'
        )
    );

-- Politique: Logs accessibles aux propriétaires et admins
CREATE POLICY "Users and admins can view sync logs" ON social_media_sync_logs
    FOR SELECT USING (
        user_id::text = auth.uid()::text
        OR EXISTS (
            SELECT 1 FROM users
            WHERE id::text = auth.uid()::text
            AND role = 'admin'
        )
    );

-- ============================================
-- VUE MATÉRIALISÉE POUR PERFORMANCES DASHBOARD
-- ============================================

-- Vue: Dernières stats par connexion (pour dashboards)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_latest_social_stats AS
SELECT DISTINCT ON (connection_id)
    sms.connection_id,
    sms.user_id,
    sms.platform,
    smc.platform_username,
    smc.platform_display_name,
    smc.profile_picture_url,
    sms.followers_count,
    sms.following_count,
    sms.engagement_rate,
    sms.average_likes_per_post,
    sms.total_posts,
    sms.followers_growth,
    sms.synced_at,
    smc.connection_status
FROM social_media_stats sms
JOIN social_media_connections smc ON sms.connection_id = smc.id
ORDER BY connection_id, synced_at DESC;

CREATE UNIQUE INDEX ON mv_latest_social_stats (connection_id);
CREATE INDEX ON mv_latest_social_stats (user_id);
CREATE INDEX ON mv_latest_social_stats (platform);

-- Vue: Top influenceurs par engagement
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_influencers_by_engagement AS
SELECT
    u.id as user_id,
    u.email,
    i.id as influencer_id,
    i.display_name,
    AVG(sms.engagement_rate) as avg_engagement_rate,
    SUM(sms.followers_count) as total_followers,
    COUNT(DISTINCT sms.platform) as platforms_count,
    MAX(sms.synced_at) as last_synced_at
FROM users u
JOIN influencers i ON u.id = i.user_id
JOIN social_media_connections smc ON u.id = smc.user_id
JOIN social_media_stats sms ON smc.id = sms.connection_id
WHERE sms.synced_at >= NOW() - INTERVAL '30 days'
GROUP BY u.id, u.email, i.id, i.display_name
ORDER BY avg_engagement_rate DESC
LIMIT 100;

CREATE UNIQUE INDEX ON mv_top_influencers_by_engagement (user_id);

-- Fonction pour rafraîchir les vues matérialisées
CREATE OR REPLACE FUNCTION refresh_social_media_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_latest_social_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_influencers_by_engagement;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON TABLE social_media_connections IS 'Connexions OAuth aux réseaux sociaux des influenceurs';
COMMENT ON TABLE social_media_stats IS 'Historique des statistiques des comptes sociaux';
COMMENT ON TABLE social_media_posts IS 'Historique des publications (posts/vidéos) des influenceurs';
COMMENT ON TABLE social_media_sync_logs IS 'Logs de synchronisation pour audit et debugging';

COMMENT ON COLUMN social_media_connections.access_token_encrypted IS 'Token OAuth chiffré - JAMAIS en clair!';
COMMENT ON COLUMN social_media_connections.token_expires_at IS 'Instagram: 60 jours, TikTok: variable';
COMMENT ON COLUMN social_media_stats.engagement_rate IS 'Calculé: (avg_likes + avg_comments) / followers * 100';
COMMENT ON COLUMN social_media_connections.auto_refresh_enabled IS 'Si TRUE, Celery rafraîchit automatiquement les stats';

-- ============================================
-- DONNÉES DE TEST (OPTIONNEL)
-- ============================================

-- Insérer une connexion Instagram de test (NE PAS utiliser en production!)
/*
INSERT INTO social_media_connections (
    user_id, platform, platform_user_id, platform_username,
    access_token_encrypted, connection_status
) VALUES (
    (SELECT id FROM users WHERE role = 'influencer' LIMIT 1),
    'instagram',
    '17841400000000000',
    'influencer_test',
    pgp_sym_encrypt('fake_token_for_testing', 'your-encryption-key'),
    'active'
) ON CONFLICT DO NOTHING;
*/

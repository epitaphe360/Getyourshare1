-- ============================================
-- AMÉLIORATION DES PERFORMANCES - INDEX MANQUANTS
-- ============================================
-- À exécuter après la création des tables principales

-- Index sur les colonnes de status (fréquemment filtrées)
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_reviews_approved ON reviews(is_approved);

-- Index sur les messages non lus (améliore les requêtes de notifications)
CREATE INDEX IF NOT EXISTS idx_messages_is_read ON messages(is_read) WHERE is_read = FALSE;

-- Index sur les user_sessions actives
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

-- Index composites pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_sales_status_merchant ON sales(status, merchant_id);
CREATE INDEX IF NOT EXISTS idx_sales_status_influencer ON sales(status, influencer_id);

-- Index pour la recherche de produits
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_available ON products(is_available) WHERE is_available = TRUE;

-- Index pour les recherches d'influenceurs
CREATE INDEX IF NOT EXISTS idx_influencers_category ON influencers(category);
CREATE INDEX IF NOT EXISTS idx_influencers_type_category ON influencers(influencer_type, category);

-- Index pour les tracking links actifs
CREATE INDEX IF NOT EXISTS idx_trackable_links_active ON trackable_links(is_active) WHERE is_active = TRUE;

-- Commentaires sur les améliorations
COMMENT ON INDEX idx_campaigns_status IS 'Améliore les requêtes de filtrage par statut de campagne';
COMMENT ON INDEX idx_messages_is_read IS 'Optimise les requêtes de messages non lus';
COMMENT ON INDEX idx_sales_status_merchant IS 'Index composite pour les ventes par merchant et statut';

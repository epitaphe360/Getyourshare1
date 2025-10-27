-- ============================================
-- SYSTÈME DE DEMANDES D'AFFILIATION
-- Date: 2025-10-23
-- ============================================

-- Table pour les demandes d'affiliation
CREATE TABLE IF NOT EXISTS affiliation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    
    -- Informations de la demande
    message TEXT, -- Message de l'influenceur au marchand
    influencer_stats JSONB, -- Statistiques de l'influenceur (followers, engagement, etc.)
    
    -- Statut de la demande
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    
    -- Réponse du marchand
    merchant_response TEXT,
    reviewed_at TIMESTAMP,
    reviewed_by UUID REFERENCES users(id),
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    UNIQUE(influencer_id, product_id), -- Un influenceur ne peut faire qu'une demande par produit
    CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled'))
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_influencer ON affiliation_requests(influencer_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_merchant ON affiliation_requests(merchant_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_product ON affiliation_requests(product_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_status ON affiliation_requests(status);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_created ON affiliation_requests(created_at DESC);

-- Table pour l'historique des demandes
CREATE TABLE IF NOT EXISTS affiliation_request_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID NOT NULL REFERENCES affiliation_requests(id) ON DELETE CASCADE,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_by UUID REFERENCES users(id),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_affiliation_request_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour updated_at
DROP TRIGGER IF EXISTS update_affiliation_request_modtime ON affiliation_requests;
CREATE TRIGGER update_affiliation_request_modtime
    BEFORE UPDATE ON affiliation_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_affiliation_request_timestamp();

-- Trigger pour créer un lien de tracking automatiquement après approbation
CREATE OR REPLACE FUNCTION create_tracking_link_on_approval()
RETURNS TRIGGER AS $$
BEGIN
    -- Si la demande vient d'être approuvée
    IF NEW.status = 'approved' AND OLD.status = 'pending' THEN
        -- Créer un lien de tracking dans trackable_links
        INSERT INTO trackable_links (
            influencer_id,
            product_id,
            unique_code,
            is_active
        )
        VALUES (
            NEW.influencer_id,
            NEW.product_id,
            substring(md5(random()::text || NEW.influencer_id::text || NEW.product_id::text) from 1 for 8),
            true
        );
        
        -- Enregistrer dans l'historique
        INSERT INTO affiliation_request_history (
            request_id,
            old_status,
            new_status,
            changed_by,
            comment
        ) VALUES (
            NEW.id,
            OLD.status,
            NEW.status,
            NEW.reviewed_by,
            'Demande approuvée - Lien de tracking créé automatiquement'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS auto_create_tracking_link ON affiliation_requests;
CREATE TRIGGER auto_create_tracking_link
    AFTER UPDATE ON affiliation_requests
    FOR EACH ROW
    WHEN (NEW.status = 'approved' AND OLD.status != 'approved')
    EXECUTE FUNCTION create_tracking_link_on_approval();

-- Vue pour les statistiques des demandes
CREATE OR REPLACE VIEW affiliation_requests_stats AS
SELECT 
    merchant_id,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE status = 'pending') as pending_requests,
    COUNT(*) FILTER (WHERE status = 'approved') as approved_requests,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected_requests,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'approved')::numeric / 
        NULLIF(COUNT(*) FILTER (WHERE status != 'pending')::numeric, 0) * 100, 
        2
    ) as approval_rate
FROM affiliation_requests
GROUP BY merchant_id;

-- Vue détaillée des demandes pour les influenceurs
CREATE OR REPLACE VIEW influencer_affiliation_requests AS
SELECT 
    ar.id,
    ar.influencer_id,
    ar.product_id,
    ar.merchant_id,
    ar.status,
    ar.message,
    ar.merchant_response,
    ar.created_at,
    ar.reviewed_at,
    
    -- Informations produit
    p.name as product_name,
    p.description as product_description,
    p.commission_rate,
    p.price as product_price,
    
    -- Informations marchand
    m.company_name as merchant_company
    
FROM affiliation_requests ar
LEFT JOIN products p ON ar.product_id = p.id
LEFT JOIN merchants m ON ar.merchant_id = m.id;

-- Vue détaillée des demandes pour les marchands
CREATE OR REPLACE VIEW merchant_affiliation_requests AS
SELECT 
    ar.id,
    ar.influencer_id,
    ar.product_id,
    ar.merchant_id,
    ar.status,
    ar.message,
    ar.influencer_stats,
    ar.merchant_response,
    ar.created_at,
    ar.reviewed_at,
    
    -- Informations influenceur
    u.email as influencer_email,
    inf.full_name as influencer_name,
    inf.profile_picture_url as influencer_avatar,
    
    -- Informations produit
    p.name as product_name,
    p.commission_rate,
    p.price as product_price,
    
    -- Statistiques influenceur (si disponibles)
    (ar.influencer_stats->>'followers')::integer as followers_count,
    (ar.influencer_stats->>'engagement_rate')::numeric as engagement_rate,
    ar.influencer_stats->>'platforms' as platforms
    
FROM affiliation_requests ar
LEFT JOIN influencers inf ON ar.influencer_id = inf.id
LEFT JOIN users u ON inf.user_id = u.id
LEFT JOIN products p ON ar.product_id = p.id;

COMMENT ON TABLE affiliation_requests IS 'Demandes d''affiliation des influenceurs pour les produits';
COMMENT ON COLUMN affiliation_requests.status IS 'pending: en attente, approved: approuvée, rejected: refusée, cancelled: annulée';
COMMENT ON COLUMN affiliation_requests.influencer_stats IS 'Statistiques JSON de l''influenceur (followers, engagement, etc.)';

-- ============================================
-- MODIFICATION SYSTÈME AFFILIATION UNIFIÉ
-- Date: 2025-10-23
-- ============================================

-- ÉTAPE 1: Supprimer les vues qui dépendent de trackable_links (si elles existent)
DROP VIEW IF EXISTS merchant_affiliation_requests CASCADE;
DROP VIEW IF EXISTS affiliation_requests_stats CASCADE;
DROP VIEW IF EXISTS influencer_affiliation_requests CASCADE;

-- ÉTAPE 2: Vérifier si trackable_links est une vue ou une table
-- Si c'est une vue, la supprimer et créer la table
DO $$
BEGIN
    -- Vérifier si trackable_links est une vue
    IF EXISTS (
        SELECT 1 FROM information_schema.views 
        WHERE table_schema = 'public' 
        AND table_name = 'trackable_links'
    ) THEN
        -- C'est une vue, la supprimer
        DROP VIEW IF EXISTS trackable_links CASCADE;
        RAISE NOTICE 'Vue trackable_links supprimée';
    END IF;
END $$;

-- ÉTAPE 3: Ajouter les colonnes nécessaires pour les demandes d'affiliation
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS influencer_message TEXT;
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS merchant_response TEXT;
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS reviewed_by UUID REFERENCES users(id);

-- Ajouter la colonne status si elle n'existe pas
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending_approval';

-- Modifier le statut par défaut et les contraintes
ALTER TABLE trackable_links ALTER COLUMN status SET DEFAULT 'pending_approval';
ALTER TABLE trackable_links DROP CONSTRAINT IF EXISTS trackable_links_status_check;
ALTER TABLE trackable_links ADD CONSTRAINT trackable_links_status_check
    CHECK (status IN ('pending_approval', 'active', 'rejected', 'inactive'));

-- Créer un index pour les statuts
CREATE INDEX IF NOT EXISTS idx_trackable_links_status ON trackable_links(status);

-- Vue pour les demandes d'affiliation des marchands (remplace merchant_affiliation_requests)
CREATE OR REPLACE VIEW merchant_affiliation_requests AS
SELECT
    tl.id,
    tl.influencer_id,
    tl.product_id,
    tl.status,
    tl.influencer_message,
    tl.merchant_response,
    tl.created_at,
    tl.reviewed_at,

    -- Informations influenceur
    u.email as influencer_email,
    inf.full_name as influencer_name,
    inf.profile_picture_url as influencer_avatar,

    -- Informations produit
    p.name as product_name,
    p.commission_rate,
    p.price as product_price,

    -- Informations marchand (pour filtrage)
    p.merchant_id

FROM trackable_links tl
LEFT JOIN influencers inf ON tl.influencer_id = inf.id
LEFT JOIN users u ON inf.user_id = u.id
LEFT JOIN products p ON tl.product_id = p.id
WHERE tl.status IN ('pending_approval', 'active', 'rejected');

-- Vue pour les statistiques des demandes d'affiliation
CREATE OR REPLACE VIEW affiliation_requests_stats AS
SELECT
    p.merchant_id,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE tl.status = 'pending_approval') as pending_requests,
    COUNT(*) FILTER (WHERE tl.status = 'active') as approved_requests,
    COUNT(*) FILTER (WHERE tl.status = 'rejected') as rejected_requests,
    ROUND(
        COUNT(*) FILTER (WHERE tl.status = 'active')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE tl.status IN ('active', 'rejected'))::numeric, 0) * 100,
        2
    ) as approval_rate
FROM trackable_links tl
LEFT JOIN products p ON tl.product_id = p.id
WHERE tl.status IN ('pending_approval', 'active', 'rejected')
GROUP BY p.merchant_id;

-- Fonction pour approuver une demande d'affiliation (modifie le statut et génère le short_code)
CREATE OR REPLACE FUNCTION approve_affiliation_request(
    p_request_id UUID,
    p_merchant_response TEXT,
    p_reviewed_by UUID
) RETURNS VOID AS $$
DECLARE
    v_influencer_id UUID;
    v_product_id UUID;
BEGIN
    -- Récupérer les informations de la demande
    SELECT influencer_id, product_id INTO v_influencer_id, v_product_id
    FROM trackable_links
    WHERE id = p_request_id AND status = 'pending_approval';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Demande non trouvée ou déjà traitée';
    END IF;

    -- Générer le short_code unique et approuver
    UPDATE trackable_links SET
        status = 'active',
        merchant_response = p_merchant_response,
        reviewed_at = CURRENT_TIMESTAMP,
        reviewed_by = p_reviewed_by,
        unique_code = substring(md5(random()::text || v_influencer_id::text || v_product_id::text || CURRENT_TIMESTAMP::text) from 1 for 8),
        is_active = true
    WHERE id = p_request_id;

END;
$$ LANGUAGE plpgsql;

-- Fonction pour refuser une demande d'affiliation
CREATE OR REPLACE FUNCTION reject_affiliation_request(
    p_request_id UUID,
    p_merchant_response TEXT,
    p_reviewed_by UUID
) RETURNS VOID AS $$
BEGIN
    UPDATE trackable_links SET
        status = 'rejected',
        merchant_response = p_merchant_response,
        reviewed_at = CURRENT_TIMESTAMP,
        reviewed_by = p_reviewed_by
    WHERE id = p_request_id AND status = 'pending_approval';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Demande non trouvée ou déjà traitée';
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE trackable_links IS 'Liens de tracking et demandes d''affiliation unifiées';
COMMENT ON COLUMN trackable_links.status IS 'pending_approval: en attente, active: approuvé, rejected: refusé, inactive: inactif';
COMMENT ON COLUMN trackable_links.influencer_message IS 'Message de l''influenceur lors de la demande';
COMMENT ON COLUMN trackable_links.merchant_response IS 'Réponse du marchand (approbation ou refus)';

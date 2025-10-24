-- ============================================
-- MIGRATION: Système de Demandes d'Affiliation
-- Description: Crée la table affiliation_requests pour gérer le workflow
--              Influenceur demande → Marchand approuve/refuse → Lien généré
-- ============================================

-- Table pour gérer les demandes d'affiliation des influenceurs
CREATE TABLE IF NOT EXISTS affiliation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE NOT NULL,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE NOT NULL,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE NOT NULL,

    -- Statut de la demande
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),

    -- Message de l'influenceur lors de la demande
    influencer_message TEXT,

    -- Statistiques de l'influenceur au moment de la demande
    influencer_followers INTEGER,
    influencer_engagement_rate DECIMAL(5, 2),
    influencer_social_links JSONB, -- {instagram: "url", tiktok: "url", etc.}

    -- Réponse du marchand
    merchant_response TEXT,
    rejection_reason VARCHAR(100), -- "Profil inadapté", "Statistiques insuffisantes", etc.

    -- Lien généré (si approuvé)
    generated_link_id UUID REFERENCES trackable_links(id) ON DELETE SET NULL,

    -- Timestamps
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Un influenceur ne peut faire qu'une seule demande active par produit
    UNIQUE(influencer_id, product_id, status)
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_influencer ON affiliation_requests(influencer_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_product ON affiliation_requests(product_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_merchant ON affiliation_requests(merchant_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_status ON affiliation_requests(status);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_requested_at ON affiliation_requests(requested_at DESC);

-- Fonction trigger pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_affiliation_requests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_affiliation_requests_updated_at
    BEFORE UPDATE ON affiliation_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_affiliation_requests_updated_at();

-- Row Level Security (RLS)
ALTER TABLE affiliation_requests ENABLE ROW LEVEL SECURITY;

-- Politique: Les influenceurs voient leurs propres demandes
CREATE POLICY "Influencers can view their own requests" ON affiliation_requests
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM influencers i
            JOIN users u ON i.user_id = u.id
            WHERE i.id = influencer_id
            AND u.id::text = auth.uid()::text
        )
    );

-- Politique: Les marchands voient les demandes pour leurs produits
CREATE POLICY "Merchants can view requests for their products" ON affiliation_requests
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM merchants m
            JOIN users u ON m.user_id = u.id
            WHERE m.id = merchant_id
            AND u.id::text = auth.uid()::text
        )
    );

-- Politique: Les admins voient tout
CREATE POLICY "Admins can view all requests" ON affiliation_requests
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id::text = auth.uid()::text
            AND role = 'admin'
        )
    );

-- Politique: Les influenceurs peuvent créer des demandes
CREATE POLICY "Influencers can create requests" ON affiliation_requests
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM influencers i
            JOIN users u ON i.user_id = u.id
            WHERE i.id = influencer_id
            AND u.id::text = auth.uid()::text
        )
    );

-- Politique: Les marchands peuvent mettre à jour les demandes (approuver/refuser)
CREATE POLICY "Merchants can update requests" ON affiliation_requests
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM merchants m
            JOIN users u ON m.user_id = u.id
            WHERE m.id = merchant_id
            AND u.id::text = auth.uid()::text
        )
    );

COMMENT ON TABLE affiliation_requests IS 'Gère les demandes d''affiliation des influenceurs pour les produits marchands';
COMMENT ON COLUMN affiliation_requests.status IS 'pending: en attente, approved: approuvé, rejected: refusé';
COMMENT ON COLUMN affiliation_requests.rejection_reason IS 'Raison du refus si status=rejected';
COMMENT ON COLUMN affiliation_requests.generated_link_id IS 'ID du lien généré automatiquement si approuvé';

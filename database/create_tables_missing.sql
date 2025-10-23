-- SQL pour créer les tables manquantes dans Supabase
-- À exécuter dans l'éditeur SQL de Supabase

-- Table invitations pour le système d'invitation marchant->influenceur
CREATE TABLE IF NOT EXISTS invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id),
    influencer_id UUID REFERENCES users(id),
    campaign_id UUID REFERENCES campaigns(id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'expired')),
    message TEXT,
    commission_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP
);

-- Table settings pour les paramètres de la plateforme
CREATE TABLE IF NOT EXISTS settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table junction campaign_products pour relier campagnes et produits
CREATE TABLE IF NOT EXISTS campaign_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, product_id)
);

-- Insertion des paramètres par défaut
INSERT INTO settings (key, value, description) VALUES
('platform_name', 'ShareYourSales', 'Nom de la plateforme'),
('commission_rate', '10', 'Taux de commission par défaut (%)'),
('min_payout', '50', 'Montant minimum pour un paiement (€)'),
('currency', 'EUR', 'Devise utilisée'),
('enable_2fa', 'false', 'Activer l''authentification 2FA'),
('email_notifications', 'true', 'Activer les notifications email'),
('max_commission_rate', '30', 'Taux de commission maximum (%)'),
('cookie_duration', '30', 'Durée du cookie de tracking (jours)')
ON CONFLICT (key) DO NOTHING;

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_invitations_merchant ON invitations(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invitations_influencer ON invitations(influencer_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON invitations(status);
CREATE INDEX IF NOT EXISTS idx_invitations_campaign ON invitations(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_products_campaign ON campaign_products(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_products_product ON campaign_products(product_id);
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);

-- Permissions RLS (Row Level Security)
ALTER TABLE invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_products ENABLE ROW LEVEL SECURITY;

-- Politique pour invitations (les marchands voient leurs invitations envoyées, les influenceurs voient celles reçues)
CREATE POLICY "Users can view their invitations" ON invitations
    FOR SELECT USING (
        auth.uid()::text = (SELECT user_id FROM users WHERE id = merchant_id)::text
        OR auth.uid()::text = (SELECT user_id FROM users WHERE id = influencer_id)::text
    );

-- Politique pour settings (tous peuvent lire, seuls les admins peuvent modifier)
CREATE POLICY "Anyone can view settings" ON settings
    FOR SELECT USING (true);

CREATE POLICY "Only admins can modify settings" ON settings
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE user_id = auth.uid()::text 
            AND role = 'admin'
        )
    );

-- Politique pour campaign_products (visible selon la visibilité de la campagne)
CREATE POLICY "Users can view campaign products" ON campaign_products
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM campaigns c
            WHERE c.id = campaign_id
        )
    );

-- ============================================
-- MIGRATION: Ajout des colonnes pour paiements automatiques
-- Date: 2025-10-23
-- ============================================

-- 1. Ajouter colonne updated_at aux sales si manquante
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='sales' AND column_name='updated_at') THEN
        ALTER TABLE sales ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- 2. Ajouter colonne approved_at aux commissions si manquante
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='commissions' AND column_name='approved_at') THEN
        ALTER TABLE commissions ADD COLUMN approved_at TIMESTAMP;
    END IF;
END $$;

-- 3. Créer la table payouts si elle n'existe pas
CREATE TABLE IF NOT EXISTS payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    
    -- Montant
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Statut du paiement
    status VARCHAR(50) CHECK (status IN ('pending', 'processing', 'approved', 'paid', 'rejected', 'failed')),
    
    -- Méthode
    payment_method VARCHAR(50),
    
    -- Transaction
    transaction_id VARCHAR(255),
    
    -- Dates
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    paid_at TIMESTAMP,
    
    -- Notes
    notes TEXT,
    is_automatic BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Créer la table notifications si elle n'existe pas
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Type de notification
    type VARCHAR(50) NOT NULL,
    
    -- Contenu
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    
    -- Lien optionnel
    link VARCHAR(500),
    
    -- Statut
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- Métadonnées
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Ajouter index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_payouts_influencer ON payouts(influencer_id);
CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_sales_status_created ON sales(status, created_at);
CREATE INDEX IF NOT EXISTS idx_sales_influencer ON sales(influencer_id);

-- 6. Ajouter les colonnes payment_details si manquantes
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='influencers' AND column_name='payment_details') THEN
        ALTER TABLE influencers ADD COLUMN payment_details JSONB;
    END IF;
END $$;

-- 7. Mettre à jour les sales existantes sans updated_at
UPDATE sales 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- 8. Afficher le résumé
DO $$
DECLARE
    sales_count INTEGER;
    commissions_count INTEGER;
    payouts_count INTEGER;
    notifications_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO sales_count FROM sales;
    SELECT COUNT(*) INTO commissions_count FROM commissions;
    SELECT COUNT(*) INTO payouts_count FROM payouts;
    SELECT COUNT(*) INTO notifications_count FROM notifications;
    
    RAISE NOTICE '============================================';
    RAISE NOTICE 'MIGRATION TERMINÉE AVEC SUCCÈS';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Ventes: %', sales_count;
    RAISE NOTICE 'Commissions: %', commissions_count;
    RAISE NOTICE 'Payouts: %', payouts_count;
    RAISE NOTICE 'Notifications: %', notifications_count;
    RAISE NOTICE '============================================';
END $$;

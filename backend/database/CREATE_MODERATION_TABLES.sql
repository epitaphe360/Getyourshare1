-- ============================================
-- TABLE DE MODÉRATION DES PRODUITS
-- Stocke les produits en attente de validation admin
-- ============================================

-- Table principale de modération
CREATE TABLE IF NOT EXISTS moderation_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Référence au produit
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Données du produit au moment de la soumission
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT NOT NULL,
    product_category VARCHAR(100),
    product_price DECIMAL(10, 2),
    product_images JSONB, -- URLs des images
    
    -- Résultat de la modération IA
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'under_review')),
    ai_decision VARCHAR(20), -- 'approved' ou 'rejected'
    ai_confidence DECIMAL(3, 2), -- 0.00 à 1.00
    ai_risk_level VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    ai_flags JSONB, -- Array des catégories détectées
    ai_reason TEXT, -- Raison du rejet par l'IA
    ai_recommendation TEXT,
    moderation_method VARCHAR(20), -- 'ai' ou 'keywords'
    
    -- Décision admin
    admin_decision VARCHAR(20), -- 'approved' ou 'rejected'
    admin_user_id UUID REFERENCES users(id),
    admin_comment TEXT,
    reviewed_at TIMESTAMP,
    
    -- Metadata
    submission_attempts INT DEFAULT 1,
    priority INT DEFAULT 0, -- Plus élevé = plus prioritaire
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX idx_moderation_status ON moderation_queue(status);
CREATE INDEX idx_moderation_merchant ON moderation_queue(merchant_id);
CREATE INDEX idx_moderation_created ON moderation_queue(created_at DESC);
CREATE INDEX idx_moderation_priority ON moderation_queue(priority DESC, created_at DESC);
CREATE INDEX idx_moderation_risk ON moderation_queue(ai_risk_level);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_moderation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER moderation_update_timestamp
    BEFORE UPDATE ON moderation_queue
    FOR EACH ROW
    EXECUTE FUNCTION update_moderation_timestamp();

-- ============================================
-- TABLE DES STATS DE MODÉRATION
-- ============================================

CREATE TABLE IF NOT EXISTS moderation_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE DEFAULT CURRENT_DATE,
    
    -- Compteurs
    total_submissions INT DEFAULT 0,
    ai_approved INT DEFAULT 0,
    ai_rejected INT DEFAULT 0,
    admin_approved INT DEFAULT 0,
    admin_rejected INT DEFAULT 0,
    pending INT DEFAULT 0,
    
    -- Flags par catégorie
    flags_adult_content INT DEFAULT 0,
    flags_weapons INT DEFAULT 0,
    flags_drugs INT DEFAULT 0,
    flags_gambling INT DEFAULT 0,
    flags_counterfeit INT DEFAULT 0,
    flags_illegal INT DEFAULT 0,
    flags_other INT DEFAULT 0,
    
    -- Performance
    avg_ai_confidence DECIMAL(3, 2),
    avg_review_time_minutes INT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(date)
);

-- Index pour stats
CREATE INDEX idx_moderation_stats_date ON moderation_stats(date DESC);

-- ============================================
-- HISTORIQUE DES DÉCISIONS
-- ============================================

CREATE TABLE IF NOT EXISTS moderation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    moderation_id UUID REFERENCES moderation_queue(id) ON DELETE CASCADE,
    
    action VARCHAR(50) NOT NULL, -- 'submitted', 'ai_reviewed', 'admin_approved', 'admin_rejected'
    performed_by UUID REFERENCES users(id),
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    comment TEXT,
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_moderation_history_mod ON moderation_history(moderation_id);
CREATE INDEX idx_moderation_history_date ON moderation_history(created_at DESC);

-- ============================================
-- VUES UTILES
-- ============================================

-- Vue des produits en attente de révision admin
CREATE OR REPLACE VIEW v_pending_moderation AS
SELECT 
    mq.*,
    m.company_name as merchant_name,
    u_merchant.email as merchant_email,
    u.email as user_email,
    EXTRACT(EPOCH FROM (NOW() - mq.created_at))/3600 as hours_pending,
    CASE 
        WHEN ai_risk_level = 'critical' THEN 1
        WHEN ai_risk_level = 'high' THEN 2
        WHEN ai_risk_level = 'medium' THEN 3
        ELSE 4
    END as risk_priority
FROM moderation_queue mq
LEFT JOIN merchants m ON mq.merchant_id = m.id
LEFT JOIN users u_merchant ON m.user_id = u_merchant.id
LEFT JOIN users u ON mq.user_id = u.id
WHERE mq.status = 'pending'
ORDER BY risk_priority ASC, mq.created_at ASC;

-- Vue des stats quotidiennes
CREATE OR REPLACE VIEW v_daily_moderation_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE ai_decision = 'approved') as ai_approved,
    COUNT(*) FILTER (WHERE ai_decision = 'rejected') as ai_rejected,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    COUNT(*) FILTER (WHERE status = 'approved') as admin_approved,
    COUNT(*) FILTER (WHERE status = 'rejected') as admin_rejected,
    AVG(ai_confidence) as avg_confidence,
    AVG(EXTRACT(EPOCH FROM (reviewed_at - created_at))/60) FILTER (WHERE reviewed_at IS NOT NULL) as avg_review_minutes
FROM moderation_queue
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================
-- FONCTIONS UTILES
-- ============================================

-- Fonction pour soumettre un produit à modération
CREATE OR REPLACE FUNCTION submit_product_for_moderation(
    p_product_id UUID,
    p_merchant_id UUID,
    p_user_id UUID,
    p_product_name VARCHAR,
    p_product_description TEXT,
    p_product_category VARCHAR,
    p_product_price DECIMAL,
    p_product_images JSONB,
    p_ai_result JSONB
)
RETURNS UUID AS $$
DECLARE
    v_moderation_id UUID;
BEGIN
    INSERT INTO moderation_queue (
        product_id,
        merchant_id,
        user_id,
        product_name,
        product_description,
        product_category,
        product_price,
        product_images,
        ai_decision,
        ai_confidence,
        ai_risk_level,
        ai_flags,
        ai_reason,
        ai_recommendation,
        moderation_method,
        status
    ) VALUES (
        p_product_id,
        p_merchant_id,
        p_user_id,
        p_product_name,
        p_product_description,
        p_product_category,
        p_product_price,
        p_product_images,
        (p_ai_result->>'approved')::BOOLEAN::TEXT,
        (p_ai_result->>'confidence')::DECIMAL,
        p_ai_result->>'risk_level',
        p_ai_result->'flags',
        p_ai_result->>'reason',
        p_ai_result->>'recommendation',
        p_ai_result->>'moderation_method',
        CASE 
            WHEN (p_ai_result->>'approved')::BOOLEAN = true THEN 'approved'
            ELSE 'pending'
        END
    )
    RETURNING id INTO v_moderation_id;
    
    -- Log dans l'historique
    INSERT INTO moderation_history (moderation_id, action, new_status, metadata)
    VALUES (v_moderation_id, 'submitted', 'pending', p_ai_result);
    
    RETURN v_moderation_id;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour approuver un produit
CREATE OR REPLACE FUNCTION approve_moderation(
    p_moderation_id UUID,
    p_admin_user_id UUID,
    p_comment TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE moderation_queue
    SET 
        status = 'approved',
        admin_decision = 'approved',
        admin_user_id = p_admin_user_id,
        admin_comment = p_comment,
        reviewed_at = NOW()
    WHERE id = p_moderation_id
    AND status = 'pending';
    
    IF FOUND THEN
        INSERT INTO moderation_history (moderation_id, action, performed_by, old_status, new_status, comment)
        VALUES (p_moderation_id, 'admin_approved', p_admin_user_id, 'pending', 'approved', p_comment);
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour rejeter un produit
CREATE OR REPLACE FUNCTION reject_moderation(
    p_moderation_id UUID,
    p_admin_user_id UUID,
    p_comment TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE moderation_queue
    SET 
        status = 'rejected',
        admin_decision = 'rejected',
        admin_user_id = p_admin_user_id,
        admin_comment = p_comment,
        reviewed_at = NOW()
    WHERE id = p_moderation_id
    AND status = 'pending';
    
    IF FOUND THEN
        INSERT INTO moderation_history (moderation_id, action, performed_by, old_status, new_status, comment)
        VALUES (p_moderation_id, 'admin_rejected', p_admin_user_id, 'pending', 'rejected', p_comment);
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- DONNÉES DE TEST
-- ============================================

-- Exemple de soumission
/*
SELECT submit_product_for_moderation(
    'uuid-du-produit',
    'uuid-du-merchant',
    'uuid-du-user',
    'Montre Rolex Submariner',
    'Magnifique montre de luxe en parfait état',
    'Accessoires',
    15000.00,
    '["https://example.com/image1.jpg"]'::jsonb,
    '{
        "approved": false,
        "confidence": 0.85,
        "risk_level": "high",
        "flags": ["counterfeit"],
        "reason": "Possible produit contrefait - prix suspect pour une Rolex",
        "recommendation": "Manual review required",
        "moderation_method": "ai"
    }'::jsonb
);
*/

-- ============================================
-- NOTES
-- ============================================

/*
WORKFLOW DE MODÉRATION:

1. Merchant crée un produit
2. Backend appelle moderation_service.moderate_product()
3. IA analyse et retourne résultat
4. Si IA approuve + confiance > 0.8: produit créé directement
5. Si IA rejette OU confiance < 0.8: ajout à moderation_queue
6. Admin reçoit notification
7. Admin revoit dans dashboard modération
8. Admin approuve ou rejette manuellement
9. Si approuvé: produit créé et visible
10. Si rejeté: merchant notifié avec raison

PERMISSIONS:
- Seuls les admins peuvent voir moderation_queue
- Merchants peuvent voir le statut de leurs produits en attente
- Historique gardé pour audit
*/

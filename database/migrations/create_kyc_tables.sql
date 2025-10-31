-- ============================================
-- Tables KYC (Know Your Customer)
-- Vérification d'identité et conformité
-- ============================================

-- Table: kyc_submissions
CREATE TABLE IF NOT EXISTS kyc_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_type VARCHAR(50) NOT NULL CHECK (user_type IN ('merchant', 'influencer')),

    -- Statut du KYC
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'submitted', 'under_review', 'approved', 'rejected', 'expired')),

    -- Informations personnelles (JSONB)
    personal_info JSONB NOT NULL,

    -- Document d'identité (JSONB)
    identity_document JSONB NOT NULL,

    -- Documents d'entreprise (JSONB - optionnel pour influencers)
    company_documents JSONB,

    -- Compte bancaire (JSONB)
    bank_account JSONB NOT NULL,

    -- Metadata
    ip_address VARCHAR(45),  -- IPv4 ou IPv6
    submitted_at TIMESTAMP WITH TIME ZONE,

    -- Review par admin
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewer_notes TEXT,

    -- Rejet
    rejection_reason VARCHAR(100),
    rejection_comment TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour performances
CREATE INDEX idx_kyc_submissions_user_id ON kyc_submissions(user_id);
CREATE INDEX idx_kyc_submissions_status ON kyc_submissions(status);
CREATE INDEX idx_kyc_submissions_submitted_at ON kyc_submissions(submitted_at);

-- Index pour recherches admin
CREATE INDEX idx_kyc_submissions_status_submitted ON kyc_submissions(status, submitted_at);

-- ============================================
-- Table: kyc_documents (stockage documents individuels)
-- ============================================

CREATE TABLE IF NOT EXISTS kyc_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES kyc_submissions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Type de document
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN (
        'cin', 'passport', 'ice', 'rc', 'tva', 'rib',
        'selfie', 'proof_address', 'statuts'
    )),

    -- Fichier
    file_url TEXT NOT NULL,
    file_name VARCHAR(255),
    file_size INTEGER,
    file_type VARCHAR(50),  -- image/jpeg, application/pdf, etc.

    -- Metadata
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Vérification
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Index
CREATE INDEX idx_kyc_documents_submission_id ON kyc_documents(submission_id);
CREATE INDEX idx_kyc_documents_user_id ON kyc_documents(user_id);
CREATE INDEX idx_kyc_documents_type ON kyc_documents(document_type);

-- ============================================
-- Table: kyc_verifications (historique vérifications)
-- ============================================

CREATE TABLE IF NOT EXISTS kyc_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES kyc_submissions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Action
    action VARCHAR(50) NOT NULL CHECK (action IN ('submitted', 'under_review', 'approved', 'rejected', 'resubmitted')),

    -- Admin
    admin_id UUID REFERENCES users(id) ON DELETE SET NULL,
    admin_comment TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_kyc_verifications_submission_id ON kyc_verifications(submission_id);
CREATE INDEX idx_kyc_verifications_user_id ON kyc_verifications(user_id);
CREATE INDEX idx_kyc_verifications_created_at ON kyc_verifications(created_at);

-- ============================================
-- View: kyc_summary (résumé KYC pour admin)
-- ============================================

CREATE OR REPLACE VIEW kyc_summary AS
SELECT
    s.id as submission_id,
    s.user_id,
    u.email,
    u.first_name,
    u.last_name,
    u.role as user_type,
    s.status,
    s.submitted_at,
    s.reviewed_at,
    s.reviewer_id,
    admin.email as reviewer_email,
    s.rejection_reason,
    -- Compter documents uploadés
    (SELECT COUNT(*) FROM kyc_documents WHERE submission_id = s.id) as documents_count,
    -- Compter documents vérifiés
    (SELECT COUNT(*) FROM kyc_documents WHERE submission_id = s.id AND verified = TRUE) as verified_documents_count,
    -- Données personnelles extraites
    s.personal_info->>'first_name' as kyc_first_name,
    s.personal_info->>'last_name' as kyc_last_name,
    s.personal_info->>'phone' as kyc_phone,
    s.identity_document->>'document_type' as id_document_type,
    s.identity_document->>'document_number' as id_document_number,
    s.identity_document->>'expiry_date' as id_expiry_date,
    s.company_documents->>'company_name' as company_name,
    s.company_documents->>'ice' as company_ice,
    s.bank_account->>'iban' as bank_iban,
    s.bank_account->>'bank_name' as bank_name,
    s.created_at,
    s.updated_at
FROM
    kyc_submissions s
    JOIN users u ON s.user_id = u.id
    LEFT JOIN users admin ON s.reviewer_id = admin.id;

-- ============================================
-- Fonction: trigger pour updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_kyc_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger sur kyc_submissions
CREATE TRIGGER trigger_kyc_submissions_updated_at
    BEFORE UPDATE ON kyc_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_kyc_updated_at();

-- ============================================
-- Fonction: automatique kyc_verifications
-- ============================================

CREATE OR REPLACE FUNCTION log_kyc_status_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Logger changement de statut
    IF (TG_OP = 'UPDATE' AND OLD.status != NEW.status) THEN
        INSERT INTO kyc_verifications (
            submission_id,
            user_id,
            action,
            admin_id,
            admin_comment
        ) VALUES (
            NEW.id,
            NEW.user_id,
            NEW.status,
            NEW.reviewer_id,
            NEW.reviewer_notes
        );
    END IF;

    -- Logger nouvelle soumission
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO kyc_verifications (
            submission_id,
            user_id,
            action,
            admin_id
        ) VALUES (
            NEW.id,
            NEW.user_id,
            'submitted',
            NULL
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trigger_log_kyc_status_change
    AFTER INSERT OR UPDATE ON kyc_submissions
    FOR EACH ROW
    EXECUTE FUNCTION log_kyc_status_change();

-- ============================================
-- RLS (Row Level Security)
-- ============================================

-- Activer RLS
ALTER TABLE kyc_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE kyc_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE kyc_verifications ENABLE ROW LEVEL SECURITY;

-- Policy: Users peuvent voir leurs propres KYC
CREATE POLICY kyc_submissions_user_select
    ON kyc_submissions FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users peuvent créer leur KYC
CREATE POLICY kyc_submissions_user_insert
    ON kyc_submissions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Admins peuvent tout voir
CREATE POLICY kyc_submissions_admin_all
    ON kyc_submissions FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Policy similaires pour kyc_documents
CREATE POLICY kyc_documents_user_select
    ON kyc_documents FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY kyc_documents_user_insert
    ON kyc_documents FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY kyc_documents_admin_all
    ON kyc_documents FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Policy pour kyc_verifications
CREATE POLICY kyc_verifications_user_select
    ON kyc_verifications FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY kyc_verifications_admin_all
    ON kyc_verifications FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================
-- Données de test (optionnel)
-- ============================================

-- Insérer des statuts KYC fictifs pour tests
-- ATTENTION: À supprimer en production!

COMMENT ON TABLE kyc_submissions IS 'Soumissions KYC des utilisateurs';
COMMENT ON TABLE kyc_documents IS 'Documents individuels uploadés pour KYC';
COMMENT ON TABLE kyc_verifications IS 'Historique des vérifications KYC';
COMMENT ON VIEW kyc_summary IS 'Vue résumée des KYC pour dashboard admin';

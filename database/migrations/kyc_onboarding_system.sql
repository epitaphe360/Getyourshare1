-- ============================================
-- SYSTÈME KYC (Know Your Customer) PROFESSIONNEL
-- Conformité: Maroc (AMMC, Bank Al-Maghrib) + International (FATF, GDPR)
-- ============================================

-- ============================================
-- 1. TABLE: user_kyc_documents
-- Stocke tous les documents d'identité et de vérification
-- ============================================
CREATE TABLE IF NOT EXISTS user_kyc_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,

    -- Type de document
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN (
        'cin',              -- Carte d'Identité Nationale (Maroc)
        'passport',         -- Passeport
        'residence_permit', -- Carte de séjour
        'driving_license',  -- Permis de conduire
        'proof_address',    -- Justificatif de domicile
        'bank_statement',   -- Relevé bancaire (RIB)
        'tax_certificate',  -- Certificat d'immatriculation fiscale
        'commercial_register', -- Registre de commerce
        'professional_card', -- Carte professionnelle
        'ice_certificate',  -- Identifiant Commun de l'Entreprise (Maroc)
        'tva_certificate',  -- Certificat TVA
        'selfie'            -- Selfie avec pièce d'identité (vérification liveness)
    )),

    -- Fichier
    file_url TEXT NOT NULL,
    file_name VARCHAR(255),
    file_size INTEGER,  -- en bytes
    file_mime_type VARCHAR(100),

    -- Métadonnées extraites du document
    extracted_data JSONB DEFAULT '{}'::jsonb,
    -- Exemple pour CIN:
    -- {
    --   "full_name": "Mohammed Ahmed",
    --   "cin_number": "AB123456",
    --   "date_of_birth": "1990-05-15",
    --   "place_of_birth": "Casablanca",
    --   "address": "123 Rue...",
    --   "issue_date": "2015-03-20",
    --   "expiry_date": "2025-03-20"
    -- }

    -- Statut de vérification
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN (
        'pending',    -- En attente de vérification
        'reviewing',  -- En cours de révision
        'approved',   -- Approuvé
        'rejected',   -- Rejeté
        'expired'     -- Document expiré
    )),

    -- Vérification automatique vs manuelle
    auto_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),  -- Admin qui a vérifié
    verified_at TIMESTAMP,

    -- Raison du rejet
    rejection_reason TEXT,
    rejection_category VARCHAR(50) CHECK (rejection_category IN (
        'document_expired',
        'document_unreadable',
        'document_falsified',
        'information_mismatch',
        'document_incomplete',
        'other'
    )),

    -- Scoring de confiance (0-100)
    confidence_score DECIMAL(5,2) DEFAULT 0.00,  -- Score IA de véracité du document

    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- Date d'expiration du document
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX idx_kyc_docs_user ON user_kyc_documents(user_id);
CREATE INDEX idx_kyc_docs_type ON user_kyc_documents(document_type);
CREATE INDEX idx_kyc_docs_status ON user_kyc_documents(verification_status);
CREATE INDEX idx_kyc_docs_expiry ON user_kyc_documents(expires_at) WHERE expires_at IS NOT NULL;

-- Trigger pour updated_at
CREATE TRIGGER update_kyc_documents_updated_at
    BEFORE UPDATE ON user_kyc_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 2. TABLE: user_kyc_profile
-- Profil KYC global de l'utilisateur
-- ============================================
CREATE TABLE IF NOT EXISTS user_kyc_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE NOT NULL,

    -- Niveau KYC (Tier system)
    kyc_level INTEGER DEFAULT 0 CHECK (kyc_level BETWEEN 0 AND 3),
    -- 0: Aucune vérification (compte créé mais pas vérifié)
    -- 1: Email + Téléphone vérifié
    -- 2: Identité vérifiée (CIN/Passeport + Selfie)
    -- 3: Full KYC (Identité + Adresse + Banque + Fiscalité)

    -- Statut global
    kyc_status VARCHAR(20) DEFAULT 'incomplete' CHECK (kyc_status IN (
        'incomplete',   -- Documents manquants
        'pending',      -- Tous les documents soumis, en attente de vérification
        'approved',     -- KYC approuvé
        'rejected',     -- KYC rejeté
        'suspended'     -- Compte suspendu (activité suspecte)
    )),

    -- Informations personnelles vérifiées
    verified_full_name VARCHAR(255),
    verified_date_of_birth DATE,
    verified_nationality VARCHAR(2),  -- ISO country code
    verified_address TEXT,
    verified_city VARCHAR(100),
    verified_postal_code VARCHAR(20),
    verified_country VARCHAR(2),

    -- Type de compte
    account_type VARCHAR(20) CHECK (account_type IN (
        'individual',        -- Particulier
        'sole_proprietor',   -- Auto-entrepreneur
        'company',           -- Entreprise
        'association'        -- Association
    )),

    -- Pour les entreprises
    company_name VARCHAR(255),
    company_ice VARCHAR(50),              -- ICE (Maroc)
    company_rc VARCHAR(50),               -- Registre Commerce
    company_tax_id VARCHAR(50),           -- Numéro fiscal
    company_tva_number VARCHAR(50),       -- Numéro TVA
    company_legal_form VARCHAR(50),       -- SARL, SA, SAS, etc.
    company_incorporation_date DATE,
    company_capital DECIMAL(15,2),

    -- Représentant légal (pour entreprises)
    legal_representative_name VARCHAR(255),
    legal_representative_cin VARCHAR(50),
    legal_representative_function VARCHAR(100),

    -- Risk scoring
    risk_level VARCHAR(20) DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    risk_score DECIMAL(5,2) DEFAULT 0.00,  -- 0-100
    risk_factors JSONB DEFAULT '[]'::jsonb,  -- ["high_transaction_volume", "multiple_countries", etc.]

    -- Flags
    is_pep BOOLEAN DEFAULT FALSE,  -- Politically Exposed Person
    is_sanctioned BOOLEAN DEFAULT FALSE,  -- Sur liste de sanctions internationales

    -- Vérifications
    identity_verified BOOLEAN DEFAULT FALSE,
    address_verified BOOLEAN DEFAULT FALSE,
    bank_verified BOOLEAN DEFAULT FALSE,
    tax_verified BOOLEAN DEFAULT FALSE,
    business_verified BOOLEAN DEFAULT FALSE,  -- Pour marchands

    -- Dates de vérification
    identity_verified_at TIMESTAMP,
    address_verified_at TIMESTAMP,
    bank_verified_at TIMESTAMP,
    tax_verified_at TIMESTAMP,
    business_verified_at TIMESTAMP,

    -- Approbation finale
    approved_by UUID REFERENCES users(id),  -- Admin qui a approuvé
    approved_at TIMESTAMP,
    rejection_reason TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_reviewed_at TIMESTAMP
);

-- Index
CREATE INDEX idx_kyc_profile_user ON user_kyc_profile(user_id);
CREATE INDEX idx_kyc_profile_status ON user_kyc_profile(kyc_status);
CREATE INDEX idx_kyc_profile_level ON user_kyc_profile(kyc_level);
CREATE INDEX idx_kyc_profile_risk ON user_kyc_profile(risk_level);

-- ============================================
-- 3. TABLE: user_banking_details
-- Informations bancaires sécurisées (chiffrées)
-- ============================================
CREATE TABLE IF NOT EXISTS user_banking_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,

    -- Type de compte bancaire
    account_type VARCHAR(20) DEFAULT 'bank_account' CHECK (account_type IN (
        'bank_account',  -- Compte bancaire classique
        'paypal',        -- PayPal
        'mobile_money',  -- Mobile Money (Orange Money, etc.)
        'crypto',        -- Wallet crypto (pour certains pays)
        'wise',          -- Wise (ex-TransferWise)
        'payoneer'       -- Payoneer
    )),

    -- Coordonnées bancaires (CHIFFRÉES !)
    -- ⚠️ Ne JAMAIS stocker en clair, utiliser pgcrypto
    account_holder_name TEXT,  -- Nom du titulaire
    iban_encrypted TEXT,       -- IBAN chiffré (Europe/Maroc)
    rib_encrypted TEXT,        -- RIB chiffré (Maroc: 24 chiffres)
    swift_bic_encrypted TEXT,  -- Code SWIFT/BIC
    bank_name VARCHAR(255),
    bank_branch VARCHAR(255),

    -- Pour PayPal/autres
    paypal_email_encrypted TEXT,
    mobile_phone_encrypted TEXT,  -- Pour Mobile Money
    crypto_wallet_address_encrypted TEXT,

    -- Pays du compte
    account_country VARCHAR(2),  -- ISO code
    account_currency VARCHAR(3) DEFAULT 'MAD',  -- ISO currency

    -- Vérification
    is_verified BOOLEAN DEFAULT FALSE,
    verification_method VARCHAR(50),  -- 'microdeposit', 'instant', 'manual'
    verified_at TIMESTAMP,

    -- Pour la vérification par micro-dépôt
    verification_amount_1 DECIMAL(5,2),  -- Montant 1 (ex: 0.01€)
    verification_amount_2 DECIMAL(5,2),  -- Montant 2 (ex: 0.07€)
    verification_attempts INTEGER DEFAULT 0,
    verification_status VARCHAR(20) DEFAULT 'pending',

    -- Statut
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,  -- Compte par défaut pour les paiements

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX idx_banking_user ON user_banking_details(user_id);
CREATE INDEX idx_banking_default ON user_banking_details(user_id, is_default) WHERE is_default = TRUE;

-- ============================================
-- 4. TABLE: kyc_verification_logs
-- Logs de toutes les actions KYC (audit trail)
-- ============================================
CREATE TABLE IF NOT EXISTS kyc_verification_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    document_id UUID REFERENCES user_kyc_documents(id) ON DELETE SET NULL,

    -- Action
    action VARCHAR(50) NOT NULL CHECK (action IN (
        'document_uploaded',
        'document_reviewed',
        'document_approved',
        'document_rejected',
        'kyc_level_changed',
        'account_verified',
        'account_suspended',
        'account_reactivated',
        'risk_score_updated'
    )),

    -- Détails
    performed_by UUID REFERENCES users(id),  -- Qui a effectué l'action
    ip_address INET,
    user_agent TEXT,

    -- Données avant/après (pour audit)
    previous_data JSONB,
    new_data JSONB,

    -- Note/Commentaire
    note TEXT,

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX idx_kyc_logs_user ON kyc_verification_logs(user_id);
CREATE INDEX idx_kyc_logs_action ON kyc_verification_logs(action);
CREATE INDEX idx_kyc_logs_date ON kyc_verification_logs(created_at DESC);

-- ============================================
-- 5. TABLE: tax_compliance_info
-- Informations fiscales (Maroc + International)
-- ============================================
CREATE TABLE IF NOT EXISTS tax_compliance_info (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE NOT NULL,

    -- Maroc
    ice_number VARCHAR(50),  -- Identifiant Commun de l'Entreprise
    cin_number VARCHAR(50),  -- Numéro CIN
    tax_id VARCHAR(50),      -- Identifiant Fiscal
    tva_number VARCHAR(50),  -- Numéro TVA
    rc_number VARCHAR(50),   -- Numéro Registre Commerce

    -- International
    vat_number VARCHAR(50),          -- VAT Number (Europe)
    ein VARCHAR(50),                 -- Employer Identification Number (USA)
    tax_residence_country VARCHAR(2), -- Pays de résidence fiscale

    -- Catégorie fiscale
    tax_category VARCHAR(50) CHECK (tax_category IN (
        'individual',           -- Particulier (IR)
        'auto_entrepreneur',    -- Auto-entrepreneur (régime simplifié)
        'professional',         -- Professionnel libéral
        'company_is',          -- Société (IS)
        'association',         -- Association
        'foreign_entity'       -- Entité étrangère
    )),

    -- Régime TVA (Maroc)
    tva_regime VARCHAR(50) CHECK (tva_regime IN (
        'not_subject',     -- Non assujetti
        'cash_basis',      -- Régime d'encaissement
        'invoice_basis',   -- Régime des débits
        'exempted'         -- Exonéré
    )),

    -- Taux TVA applicables
    tva_rate DECIMAL(5,2) DEFAULT 20.00,  -- 20% par défaut au Maroc

    -- Déclarations fiscales
    last_tax_declaration_date DATE,
    last_tax_declaration_file_url TEXT,

    -- Documents
    ice_certificate_url TEXT,
    tax_certificate_url TEXT,
    tva_certificate_url TEXT,
    rc_certificate_url TEXT,

    -- Vérification
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX idx_tax_user ON tax_compliance_info(user_id);
CREATE INDEX idx_tax_ice ON tax_compliance_info(ice_number) WHERE ice_number IS NOT NULL;
CREATE INDEX idx_tax_verified ON tax_compliance_info(is_verified);

-- ============================================
-- 6. FONCTIONS & TRIGGERS
-- ============================================

-- Fonction pour calculer le niveau KYC automatiquement
CREATE OR REPLACE FUNCTION calculate_kyc_level(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_level INTEGER := 0;
    v_profile RECORD;
BEGIN
    SELECT * INTO v_profile
    FROM user_kyc_profile
    WHERE user_id = p_user_id;

    -- Level 1: Email + Phone vérifié (géré par users table)
    IF EXISTS (SELECT 1 FROM users WHERE id = p_user_id AND email_verified = TRUE) THEN
        v_level := 1;
    END IF;

    -- Level 2: Identité vérifiée
    IF v_profile.identity_verified = TRUE THEN
        v_level := 2;
    END IF;

    -- Level 3: Full KYC
    IF v_profile.identity_verified = TRUE
       AND v_profile.address_verified = TRUE
       AND v_profile.bank_verified = TRUE THEN
        v_level := 3;
    END IF;

    -- Update KYC profile
    UPDATE user_kyc_profile
    SET kyc_level = v_level,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id;

    RETURN v_level;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour calculer le risk score
CREATE OR REPLACE FUNCTION calculate_risk_score(p_user_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    v_score DECIMAL := 0.00;
    v_profile RECORD;
    v_user RECORD;
    v_doc_count INTEGER;
    v_rejected_docs INTEGER;
BEGIN
    SELECT * INTO v_profile FROM user_kyc_profile WHERE user_id = p_user_id;
    SELECT * INTO v_user FROM users WHERE id = p_user_id;

    -- Base risk factors

    -- 1. Compte récent (+10 points de risque)
    IF (CURRENT_TIMESTAMP - v_user.created_at) < INTERVAL '30 days' THEN
        v_score := v_score + 10;
    END IF;

    -- 2. Documents rejetés (+5 points par document rejeté)
    SELECT COUNT(*) INTO v_rejected_docs
    FROM user_kyc_documents
    WHERE user_id = p_user_id AND verification_status = 'rejected';
    v_score := v_score + (v_rejected_docs * 5);

    -- 3. Pas de documents (+30 points)
    SELECT COUNT(*) INTO v_doc_count
    FROM user_kyc_documents
    WHERE user_id = p_user_id AND verification_status = 'approved';
    IF v_doc_count = 0 THEN
        v_score := v_score + 30;
    END IF;

    -- 4. PEP (+20 points)
    IF v_profile.is_pep = TRUE THEN
        v_score := v_score + 20;
    END IF;

    -- 5. Sur liste de sanctions (+100 points = blocage)
    IF v_profile.is_sanctioned = TRUE THEN
        v_score := 100;
    END IF;

    -- Déterminer le niveau de risque
    DECLARE
        v_risk_level VARCHAR(20);
    BEGIN
        IF v_score >= 75 THEN
            v_risk_level := 'critical';
        ELSIF v_score >= 50 THEN
            v_risk_level := 'high';
        ELSIF v_score >= 25 THEN
            v_risk_level := 'medium';
        ELSE
            v_risk_level := 'low';
        END IF;

        -- Update profile
        UPDATE user_kyc_profile
        SET risk_score = v_score,
            risk_level = v_risk_level,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = p_user_id;
    END;

    RETURN v_score;
END;
$$ LANGUAGE plpgsql;

-- Trigger après approbation d'un document
CREATE OR REPLACE FUNCTION after_document_approved()
RETURNS TRIGGER AS $$
BEGIN
    -- Log l'action
    INSERT INTO kyc_verification_logs (user_id, document_id, action, performed_by)
    VALUES (NEW.user_id, NEW.id, 'document_approved', NEW.verified_by);

    -- Recalculer le niveau KYC
    PERFORM calculate_kyc_level(NEW.user_id);

    -- Recalculer le risk score
    PERFORM calculate_risk_score(NEW.user_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_document_approved
    AFTER UPDATE OF verification_status ON user_kyc_documents
    FOR EACH ROW
    WHEN (NEW.verification_status = 'approved' AND OLD.verification_status != 'approved')
    EXECUTE FUNCTION after_document_approved();

-- ============================================
-- 7. ROW LEVEL SECURITY (RLS)
-- ============================================

-- Activer RLS
ALTER TABLE user_kyc_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_kyc_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_banking_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE tax_compliance_info ENABLE ROW LEVEL SECURITY;

-- Policies: Users peuvent voir leurs propres données
CREATE POLICY "Users can view their own KYC documents" ON user_kyc_documents
    FOR SELECT USING (user_id::text = auth.uid()::text);

CREATE POLICY "Users can upload their own documents" ON user_kyc_documents
    FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);

-- Policies: Admins voient tout
CREATE POLICY "Admins can view all KYC documents" ON user_kyc_documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id::text = auth.uid()::text AND role = 'admin'
        )
    );

CREATE POLICY "Admins can update KYC documents" ON user_kyc_documents
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id::text = auth.uid()::text AND role = 'admin'
        )
    );

-- ============================================
-- 8. VUES UTILES
-- ============================================

-- Vue pour le dashboard admin KYC
CREATE OR REPLACE VIEW admin_kyc_dashboard AS
SELECT
    COUNT(*) FILTER (WHERE kyc_status = 'pending') as pending_verifications,
    COUNT(*) FILTER (WHERE kyc_status = 'approved') as approved_users,
    COUNT(*) FILTER (WHERE kyc_status = 'rejected') as rejected_users,
    COUNT(*) FILTER (WHERE risk_level = 'high') as high_risk_users,
    COUNT(*) FILTER (WHERE risk_level = 'critical') as critical_risk_users,
    COUNT(*) FILTER (WHERE kyc_level = 0) as unverified_users,
    COUNT(*) FILTER (WHERE kyc_level = 3) as fully_verified_users
FROM user_kyc_profile;

-- Vue pour les documents en attente
CREATE OR REPLACE VIEW pending_kyc_documents AS
SELECT
    d.id,
    d.user_id,
    u.email,
    d.document_type,
    d.file_url,
    d.uploaded_at,
    d.confidence_score,
    p.kyc_level,
    p.risk_level
FROM user_kyc_documents d
JOIN users u ON d.user_id = u.id
LEFT JOIN user_kyc_profile p ON d.user_id = p.user_id
WHERE d.verification_status = 'pending'
ORDER BY d.uploaded_at ASC;

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON TABLE user_kyc_documents IS 'Stocke tous les documents KYC (CIN, passeport, justificatifs, etc.)';
COMMENT ON TABLE user_kyc_profile IS 'Profil KYC global de l''utilisateur avec niveau de vérification';
COMMENT ON TABLE user_banking_details IS 'Coordonnées bancaires CHIFFRÉES pour les paiements';
COMMENT ON TABLE tax_compliance_info IS 'Informations fiscales (Maroc: ICE, RC, TVA / International: VAT, EIN)';
COMMENT ON TABLE kyc_verification_logs IS 'Audit trail de toutes les actions KYC';

COMMENT ON COLUMN user_kyc_profile.kyc_level IS 'Niveau KYC: 0=Non vérifié, 1=Email+Tel, 2=Identité, 3=Full KYC';
COMMENT ON COLUMN user_kyc_profile.risk_score IS 'Score de risque 0-100 (algorithme anti-fraude)';
COMMENT ON COLUMN user_banking_details.iban_encrypted IS 'IBAN chiffré avec pgcrypto - NE JAMAIS stocker en clair';

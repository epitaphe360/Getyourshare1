-- ============================================
-- Table 2FA (Two-Factor Authentication)
-- Authentification à deux facteurs
-- ============================================

-- Table: user_2fa
CREATE TABLE IF NOT EXISTS user_2fa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Configuration
    method VARCHAR(20) NOT NULL DEFAULT 'totp' CHECK (method IN ('totp', 'email')),
    enabled BOOLEAN DEFAULT FALSE,

    -- TOTP Secret (base32)
    secret VARCHAR(255),

    -- Backup codes (hashed SHA-256)
    backup_codes JSONB DEFAULT '[]'::jsonb,

    -- Email 2FA (temporaire)
    email_code VARCHAR(6),
    email_code_expiry TIMESTAMP WITH TIME ZONE,

    -- Metadata
    enabled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_user_2fa_user_id ON user_2fa(user_id);
CREATE INDEX idx_user_2fa_enabled ON user_2fa(enabled);

-- ============================================
-- Table: user_2fa_attempts (rate limiting)
-- ============================================

CREATE TABLE IF NOT EXISTS user_2fa_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Tentative
    code_attempted VARCHAR(20),
    method VARCHAR(20),
    success BOOLEAN DEFAULT FALSE,

    -- IP & User Agent
    ip_address VARCHAR(45),
    user_agent TEXT,

    -- Timestamp
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_2fa_attempts_user_id ON user_2fa_attempts(user_id);
CREATE INDEX idx_2fa_attempts_attempted_at ON user_2fa_attempts(attempted_at);
CREATE INDEX idx_2fa_attempts_ip ON user_2fa_attempts(ip_address);

-- ============================================
-- Table: user_2fa_sessions
-- ============================================

CREATE TABLE IF NOT EXISTS user_2fa_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session
    session_token VARCHAR(255) NOT NULL UNIQUE,
    verified BOOLEAN DEFAULT FALSE,

    -- IP & User Agent
    ip_address VARCHAR(45),
    user_agent TEXT,

    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified_at TIMESTAMP WITH TIME ZONE
);

-- Index
CREATE INDEX idx_2fa_sessions_user_id ON user_2fa_sessions(user_id);
CREATE INDEX idx_2fa_sessions_token ON user_2fa_sessions(session_token);
CREATE INDEX idx_2fa_sessions_expires_at ON user_2fa_sessions(expires_at);

-- ============================================
-- Fonctions
-- ============================================

-- Fonction: Auto-update updated_at
CREATE OR REPLACE FUNCTION update_2fa_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trigger_user_2fa_updated_at
    BEFORE UPDATE ON user_2fa
    FOR EACH ROW
    EXECUTE FUNCTION update_2fa_updated_at();

-- ============================================
-- Fonction: Nettoyer tentatives anciennes
-- ============================================

CREATE OR REPLACE FUNCTION cleanup_old_2fa_attempts()
RETURNS void AS $$
BEGIN
    -- Supprimer tentatives > 30 jours
    DELETE FROM user_2fa_attempts
    WHERE attempted_at < NOW() - INTERVAL '30 days';

    -- Supprimer sessions expirées
    DELETE FROM user_2fa_sessions
    WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Fonction: Vérifier rate limiting
-- ============================================

CREATE OR REPLACE FUNCTION check_2fa_rate_limit(
    p_user_id UUID,
    p_time_window INTERVAL DEFAULT '10 minutes',
    p_max_attempts INTEGER DEFAULT 5
)
RETURNS BOOLEAN AS $$
DECLARE
    attempt_count INTEGER;
BEGIN
    -- Compter tentatives récentes
    SELECT COUNT(*)
    INTO attempt_count
    FROM user_2fa_attempts
    WHERE user_id = p_user_id
      AND attempted_at > NOW() - p_time_window
      AND success = FALSE;

    -- Retourner FALSE si trop de tentatives
    RETURN attempt_count < p_max_attempts;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Fonction: Logger tentative 2FA
-- ============================================

CREATE OR REPLACE FUNCTION log_2fa_attempt(
    p_user_id UUID,
    p_code_attempted VARCHAR,
    p_method VARCHAR,
    p_success BOOLEAN,
    p_ip_address VARCHAR DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    attempt_id UUID;
BEGIN
    INSERT INTO user_2fa_attempts (
        user_id,
        code_attempted,
        method,
        success,
        ip_address,
        user_agent
    ) VALUES (
        p_user_id,
        p_code_attempted,
        p_method,
        p_success,
        p_ip_address,
        p_user_agent
    ) RETURNING id INTO attempt_id;

    RETURN attempt_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- View: 2FA Statistics
-- ============================================

CREATE OR REPLACE VIEW v_2fa_stats AS
SELECT
    COUNT(DISTINCT user_id) as total_users_with_2fa,
    COUNT(DISTINCT CASE WHEN enabled = TRUE THEN user_id END) as users_2fa_enabled,
    COUNT(DISTINCT CASE WHEN enabled = FALSE THEN user_id END) as users_2fa_disabled,
    COUNT(DISTINCT CASE WHEN method = 'totp' AND enabled = TRUE THEN user_id END) as users_totp,
    COUNT(DISTINCT CASE WHEN method = 'email' AND enabled = TRUE THEN user_id END) as users_email,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN enabled = TRUE THEN user_id END) /
        NULLIF(COUNT(DISTINCT user_id), 0),
        2
    ) as adoption_rate_percent
FROM user_2fa;

-- ============================================
-- View: 2FA Attempts Summary
-- ============================================

CREATE OR REPLACE VIEW v_2fa_attempts_summary AS
SELECT
    user_id,
    u.email,
    u.first_name,
    u.last_name,
    COUNT(*) as total_attempts,
    COUNT(CASE WHEN success = TRUE THEN 1 END) as successful_attempts,
    COUNT(CASE WHEN success = FALSE THEN 1 END) as failed_attempts,
    MAX(attempted_at) as last_attempt_at,
    COUNT(DISTINCT ip_address) as unique_ips
FROM user_2fa_attempts a
JOIN users u ON a.user_id = u.id
WHERE attempted_at > NOW() - INTERVAL '30 days'
GROUP BY user_id, u.email, u.first_name, u.last_name;

-- ============================================
-- RLS (Row Level Security)
-- ============================================

-- Activer RLS
ALTER TABLE user_2fa ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_2fa_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_2fa_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Users voient uniquement leurs données 2FA
CREATE POLICY user_2fa_user_select
    ON user_2fa FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY user_2fa_user_insert
    ON user_2fa FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY user_2fa_user_update
    ON user_2fa FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users voient leurs tentatives
CREATE POLICY user_2fa_attempts_user_select
    ON user_2fa_attempts FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users voient leurs sessions
CREATE POLICY user_2fa_sessions_user_select
    ON user_2fa_sessions FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Admins voient tout
CREATE POLICY user_2fa_admin_all
    ON user_2fa FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY user_2fa_attempts_admin_all
    ON user_2fa_attempts FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY user_2fa_sessions_admin_all
    ON user_2fa_sessions FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================
-- Commentaires
-- ============================================

COMMENT ON TABLE user_2fa IS 'Configuration 2FA des utilisateurs';
COMMENT ON TABLE user_2fa_attempts IS 'Historique des tentatives de vérification 2FA';
COMMENT ON TABLE user_2fa_sessions IS 'Sessions 2FA actives';
COMMENT ON COLUMN user_2fa.secret IS 'Secret TOTP base32 pour Google Authenticator';
COMMENT ON COLUMN user_2fa.backup_codes IS 'Codes de backup hashés (SHA-256)';
COMMENT ON FUNCTION check_2fa_rate_limit IS 'Vérifier si utilisateur a dépassé limite de tentatives';
COMMENT ON FUNCTION log_2fa_attempt IS 'Logger tentative de vérification 2FA';

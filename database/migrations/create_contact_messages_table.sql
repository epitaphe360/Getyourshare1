-- ============================================
-- Table: contact_messages
-- Messages de contact du site web
-- ============================================

CREATE TABLE IF NOT EXISTS contact_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Expéditeur
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- NULL si non connecté
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),

    -- Message
    subject VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,

    -- Catégorie
    category VARCHAR(100) DEFAULT 'general' CHECK (category IN (
        'general',
        'support',
        'merchant_inquiry',
        'influencer_inquiry',
        'partnership',
        'bug_report',
        'feature_request',
        'complaint'
    )),

    -- Status
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN (
        'new',
        'read',
        'in_progress',
        'resolved',
        'closed',
        'spam'
    )),

    -- Réponse admin
    admin_response TEXT,
    responded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    responded_at TIMESTAMP WITH TIME ZONE,

    -- Métadonnées
    ip_address VARCHAR(45),
    user_agent TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_contact_messages_user_id ON contact_messages(user_id);
CREATE INDEX idx_contact_messages_email ON contact_messages(email);
CREATE INDEX idx_contact_messages_status ON contact_messages(status);
CREATE INDEX idx_contact_messages_category ON contact_messages(category);
CREATE INDEX idx_contact_messages_created_at ON contact_messages(created_at);

-- ============================================
-- Trigger: Auto-update updated_at
-- ============================================

CREATE TRIGGER trigger_contact_messages_updated_at
    BEFORE UPDATE ON contact_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- View: Contact Messages Summary
-- ============================================

CREATE OR REPLACE VIEW v_contact_messages_summary AS
SELECT
    cm.*,
    u.email as user_email,
    u.first_name as user_first_name,
    u.last_name as user_last_name,
    admin.email as admin_email,
    admin.first_name as admin_first_name,
    admin.last_name as admin_last_name
FROM contact_messages cm
LEFT JOIN users u ON cm.user_id = u.id
LEFT JOIN users admin ON cm.responded_by = admin.id
ORDER BY cm.created_at DESC;

-- ============================================
-- View: Contact Stats
-- ============================================

CREATE OR REPLACE VIEW v_contact_stats AS
SELECT
    COUNT(*) as total_messages,
    COUNT(CASE WHEN status = 'new' THEN 1 END) as new_messages,
    COUNT(CASE WHEN status = 'read' THEN 1 END) as read_messages,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_messages,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_messages,
    COUNT(CASE WHEN status = 'spam' THEN 1 END) as spam_messages,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as last_24h,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as last_7days,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as last_30days,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (responded_at - created_at))/3600),
        2
    ) as avg_response_time_hours
FROM contact_messages
WHERE status != 'spam';

-- ============================================
-- Function: Auto-send email notification
-- ============================================

CREATE OR REPLACE FUNCTION notify_new_contact_message()
RETURNS TRIGGER AS $$
BEGIN
    -- TODO: Implémenter notification email aux admins
    -- Via service email externe (SendGrid, etc.)

    RAISE LOG 'New contact message received from: %', NEW.email;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trigger_notify_new_contact
    AFTER INSERT ON contact_messages
    FOR EACH ROW
    WHEN (NEW.status = 'new')
    EXECUTE FUNCTION notify_new_contact_message();

-- ============================================
-- RLS Policies
-- ============================================

ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;

-- Users voient uniquement leurs propres messages
CREATE POLICY contact_messages_user_select
    ON contact_messages FOR SELECT
    USING (
        auth.uid() = user_id
        OR email = (SELECT email FROM users WHERE id = auth.uid())
    );

-- Tout le monde peut insérer (contact public)
CREATE POLICY contact_messages_public_insert
    ON contact_messages FOR INSERT
    WITH CHECK (true);

-- Admins voient tout et peuvent tout faire
CREATE POLICY contact_messages_admin_all
    ON contact_messages FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admins peuvent update (répondre)
CREATE POLICY contact_messages_admin_update
    ON contact_messages FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================
-- Commentaires
-- ============================================

COMMENT ON TABLE contact_messages IS 'Messages de contact du site web';
COMMENT ON COLUMN contact_messages.category IS 'Catégorie du message pour tri et routing';
COMMENT ON COLUMN contact_messages.status IS 'Statut de traitement du message';
COMMENT ON COLUMN contact_messages.admin_response IS 'Réponse de l''admin au message';

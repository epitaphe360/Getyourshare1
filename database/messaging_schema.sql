-- ============================================
-- SYSTÈME DE MESSAGERIE - ShareYourSales
-- ============================================

-- Table des conversations (threads entre 2 utilisateurs)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Participants (merchant <-> influencer)
    user1_id UUID NOT NULL,
    user1_type VARCHAR(50) NOT NULL, -- 'merchant', 'influencer', 'admin'
    user2_id UUID NOT NULL,
    user2_type VARCHAR(50) NOT NULL,
    
    -- Métadonnées
    subject VARCHAR(255),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    
    -- Dernière activité
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Index unique pour éviter doublons
    UNIQUE(user1_id, user2_id)
);

-- Table des messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Expéditeur
    sender_id UUID NOT NULL,
    sender_type VARCHAR(50) NOT NULL, -- 'merchant', 'influencer', 'admin'
    
    -- Contenu
    content TEXT NOT NULL,
    attachments JSONB, -- [{url: 'https://...', type: 'image', name: 'file.jpg'}]
    
    -- Status de lecture
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Destinataire
    user_id UUID NOT NULL,
    user_type VARCHAR(50) NOT NULL,
    
    -- Type de notification
    type VARCHAR(50) NOT NULL, -- 'message', 'sale', 'campaign', 'payout'
    
    -- Contenu
    title VARCHAR(255) NOT NULL,
    message TEXT,
    link VARCHAR(500), -- URL de redirection
    
    -- Données additionnelles
    data JSONB,
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimisation
CREATE INDEX IF NOT EXISTS idx_conversations_user1 ON conversations(user1_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user2 ON conversations(user2_id);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message ON conversations(last_message_at DESC);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at DESC);

-- Fonction pour mettre à jour last_message_at
CREATE OR REPLACE FUNCTION update_conversation_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET last_message_at = NEW.created_at,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour automatiquement
DROP TRIGGER IF EXISTS trigger_update_conversation_last_message ON messages;
CREATE TRIGGER trigger_update_conversation_last_message
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_last_message();

-- Commentaires
COMMENT ON TABLE conversations IS 'Conversations privées entre utilisateurs (merchant-influencer)';
COMMENT ON TABLE messages IS 'Messages individuels dans les conversations';
COMMENT ON TABLE notifications IS 'Notifications système pour tous les utilisateurs';

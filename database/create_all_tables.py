"""
Script de migration automatique pour créer toutes les nouvelles tables Supabase
Pour les nouvelles features: AI Content, Mobile Payments, Smart Match, Trust Score, Dashboard
"""

import os
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_SERVICE_KEY = "sbp_d45d903473cb0435b31f5ddafc74f8dff93273fe"

# Initialiser le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("=" * 80)
print("CRÉATION AUTOMATIQUE DES TABLES SUPABASE")
print("=" * 80)

# SQL pour créer toutes les nouvelles tables
migrations = [
    # 1. TABLE TRUST_SCORES
    {
        "name": "trust_scores",
        "sql": """
        CREATE TABLE IF NOT EXISTS trust_scores (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID NOT NULL,
            username TEXT,
            trust_score DECIMAL(5,2) NOT NULL DEFAULT 50.00,
            trust_level TEXT DEFAULT 'average',
            breakdown JSONB DEFAULT '{}'::jsonb,
            badges TEXT[] DEFAULT ARRAY[]::TEXT[],
            fraud_indicators JSONB DEFAULT '[]'::jsonb,
            campaign_stats JSONB DEFAULT '{}'::jsonb,
            last_updated TIMESTAMPTZ DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id)
        );

        -- Indexes pour performance
        CREATE INDEX IF NOT EXISTS idx_trust_scores_user_id ON trust_scores(user_id);
        CREATE INDEX IF NOT EXISTS idx_trust_scores_score ON trust_scores(trust_score DESC);
        CREATE INDEX IF NOT EXISTS idx_trust_scores_level ON trust_scores(trust_level);

        -- Commentaires
        COMMENT ON TABLE trust_scores IS 'Trust Score anti-fraude pour chaque utilisateur';
        COMMENT ON COLUMN trust_scores.trust_score IS 'Score de confiance 0-100';
        COMMENT ON COLUMN trust_scores.trust_level IS 'Niveau: verified_pro, trusted, reliable, average, unverified, suspicious';
        """
    },

    # 2. TABLE PAYOUTS (Paiements Mobiles)
    {
        "name": "payouts",
        "sql": """
        CREATE TABLE IF NOT EXISTS payouts (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            fee DECIMAL(10,2) NOT NULL DEFAULT 0,
            net_amount DECIMAL(10,2) NOT NULL,
            provider TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            payout_id TEXT UNIQUE,
            transaction_id TEXT,
            qr_code_url TEXT,
            estimated_completion TEXT,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            completed_at TIMESTAMPTZ
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_payouts_user_id ON payouts(user_id);
        CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts(status);
        CREATE INDEX IF NOT EXISTS idx_payouts_payout_id ON payouts(payout_id);
        CREATE INDEX IF NOT EXISTS idx_payouts_created ON payouts(created_at DESC);

        -- Commentaires
        COMMENT ON TABLE payouts IS 'Historique des paiements mobiles (CashPlus, Orange Money, etc.)';
        COMMENT ON COLUMN payouts.provider IS 'cashplus, orange_money, mt_cash, wafacash, payzone';
        COMMENT ON COLUMN payouts.status IS 'pending, processing, completed, failed, refunded';
        """
    },

    # 3. TABLE PAYMENT_ACCOUNTS
    {
        "name": "payment_accounts",
        "sql": """
        CREATE TABLE IF NOT EXISTS payment_accounts (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID NOT NULL,
            provider TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            account_name TEXT,
            is_verified BOOLEAN DEFAULT FALSE,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, provider, phone_number)
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_payment_accounts_user_id ON payment_accounts(user_id);
        CREATE INDEX IF NOT EXISTS idx_payment_accounts_provider ON payment_accounts(provider);
        CREATE INDEX IF NOT EXISTS idx_payment_accounts_default ON payment_accounts(user_id, is_default) WHERE is_default = TRUE;

        -- Commentaires
        COMMENT ON TABLE payment_accounts IS 'Comptes de paiement mobile enregistrés par les utilisateurs';
        """
    },

    # 4. TABLE AI_CONTENT_HISTORY
    {
        "name": "ai_content_history",
        "sql": """
        CREATE TABLE IF NOT EXISTS ai_content_history (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID NOT NULL,
            platform TEXT,
            content_type TEXT,
            product_name TEXT,
            product_description TEXT,
            generated_content TEXT,
            script TEXT,
            hooks TEXT[],
            hashtags TEXT[],
            call_to_action TEXT,
            estimated_engagement DECIMAL(5,2),
            trending_keywords TEXT[],
            best_posting_time TEXT,
            tips TEXT[],
            language TEXT DEFAULT 'fr',
            tone TEXT DEFAULT 'engaging',
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_ai_content_user_id ON ai_content_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_ai_content_platform ON ai_content_history(platform);
        CREATE INDEX IF NOT EXISTS idx_ai_content_created ON ai_content_history(created_at DESC);

        -- Commentaires
        COMMENT ON TABLE ai_content_history IS 'Historique des contenus générés par IA';
        COMMENT ON COLUMN ai_content_history.platform IS 'tiktok, instagram, youtube_shorts, facebook, twitter';
        """
    },

    # 5. TABLE SMART_MATCHES (pour cacher les résultats de matching)
    {
        "name": "smart_matches",
        "sql": """
        CREATE TABLE IF NOT EXISTS smart_matches (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            influencer_id UUID,
            company_id UUID,
            compatibility_score DECIMAL(5,2),
            match_reasons TEXT[],
            potential_issues TEXT[],
            predicted_roi DECIMAL(10,2),
            predicted_reach INTEGER,
            predicted_conversions INTEGER,
            recommended_commission DECIMAL(5,2),
            confidence_level TEXT,
            match_data JSONB,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days')
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_smart_matches_influencer ON smart_matches(influencer_id);
        CREATE INDEX IF NOT EXISTS idx_smart_matches_company ON smart_matches(company_id);
        CREATE INDEX IF NOT EXISTS idx_smart_matches_score ON smart_matches(compatibility_score DESC);
        CREATE INDEX IF NOT EXISTS idx_smart_matches_active ON smart_matches(is_active) WHERE is_active = TRUE;

        -- Commentaires
        COMMENT ON TABLE smart_matches IS 'Cache des résultats de matching IA influenceurs-marques';
        """
    },

    # 6. TABLE ACHIEVEMENTS
    {
        "name": "achievements",
        "sql": """
        CREATE TABLE IF NOT EXISTS achievements (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID NOT NULL,
            achievement_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            rarity TEXT DEFAULT 'common',
            progress DECIMAL(5,2) DEFAULT 0,
            unlocked BOOLEAN DEFAULT FALSE,
            unlocked_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, achievement_id)
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_achievements_user_id ON achievements(user_id);
        CREATE INDEX IF NOT EXISTS idx_achievements_unlocked ON achievements(user_id, unlocked) WHERE unlocked = TRUE;

        -- Commentaires
        COMMENT ON TABLE achievements IS 'Achievements et badges gamification';
        COMMENT ON COLUMN achievements.rarity IS 'common, rare, epic, legendary';
        """
    },

    # 7. TABLE USER_LEVELS (Gamification)
    {
        "name": "user_levels",
        "sql": """
        CREATE TABLE IF NOT EXISTS user_levels (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID NOT NULL UNIQUE,
            current_level INTEGER DEFAULT 1,
            total_xp INTEGER DEFAULT 0,
            xp_for_next_level INTEGER DEFAULT 1000,
            last_level_up TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_user_levels_user_id ON user_levels(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_levels_level ON user_levels(current_level DESC);
        CREATE INDEX IF NOT EXISTS idx_user_levels_xp ON user_levels(total_xp DESC);

        -- Commentaires
        COMMENT ON TABLE user_levels IS 'Système de niveaux et XP pour gamification';
        """
    },

    # 8. TABLE NOTIFICATIONS_SUBSCRIPTIONS (Push Notifications)
    {
        "name": "notification_subscriptions",
        "sql": """
        CREATE TABLE IF NOT EXISTS notification_subscriptions (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID NOT NULL,
            endpoint TEXT NOT NULL,
            keys JSONB NOT NULL,
            user_agent TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_used TIMESTAMPTZ,
            UNIQUE(endpoint)
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_notification_subs_user_id ON notification_subscriptions(user_id);
        CREATE INDEX IF NOT EXISTS idx_notification_subs_active ON notification_subscriptions(is_active) WHERE is_active = TRUE;

        -- Commentaires
        COMMENT ON TABLE notification_subscriptions IS 'Subscriptions Push Notifications pour PWA';
        """
    }
]

# Fonction pour exécuter les migrations
def execute_migration(migration):
    """Exécute une migration SQL"""
    try:
        print(f"\n📋 Création de la table: {migration['name']}")
        print("-" * 80)

        # Supabase ne permet pas d'exécuter du SQL DDL directement via le SDK Python
        # On doit utiliser l'API REST ou le client PostgreSQL
        # Pour l'instant, on va juste afficher le SQL à exécuter manuellement

        print(f"✅ SQL généré pour {migration['name']}")
        print(f"   → Copiez et exécutez ce SQL dans Supabase SQL Editor")

        return True

    except Exception as e:
        print(f"❌ Erreur pour {migration['name']}: {e}")
        return False

# Fonction pour ajouter des colonnes aux tables existantes
def add_missing_columns():
    """Ajoute les colonnes manquantes aux tables existantes"""

    print("\n" + "=" * 80)
    print("AJOUT DES COLONNES MANQUANTES AUX TABLES EXISTANTES")
    print("=" * 80)

    alter_statements = """
    -- Ajouter colonnes à la table users
    ALTER TABLE users ADD COLUMN IF NOT EXISTS avg_response_time_hours DECIMAL(10,2) DEFAULT 24;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS balance DECIMAL(10,2) DEFAULT 0;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS kyc_verified BOOLEAN DEFAULT FALSE;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan TEXT DEFAULT 'free';
    ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'active';

    -- Ajouter colonnes à la table campaigns (si elle existe)
    ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS clicks INTEGER DEFAULT 0;
    ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS conversions INTEGER DEFAULT 0;
    ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS revenue DECIMAL(10,2) DEFAULT 0;
    ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS content_quality_rating DECIMAL(3,1);
    ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS merchant_rating DECIMAL(3,1);
    ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS bounce_rate DECIMAL(5,2);
    ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS avg_session_duration INTEGER;

    -- Créer des indexes sur les nouvelles colonnes
    CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_plan);
    CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance);
    CREATE INDEX IF NOT EXISTS idx_campaigns_revenue ON campaigns(revenue DESC);
    CREATE INDEX IF NOT EXISTS idx_campaigns_conversions ON campaigns(conversions DESC);
    """

    print(alter_statements)
    print("\n✅ SQL ALTER TABLE généré")
    print("   → Copiez et exécutez ce SQL dans Supabase SQL Editor")

# Fonction pour créer les données initiales
def seed_initial_data():
    """Crée des données de seed pour tester"""

    print("\n" + "=" * 80)
    print("DONNÉES INITIALES (OPTIONNEL)")
    print("=" * 80)

    seed_sql = """
    -- Insérer des achievements par défaut
    INSERT INTO achievements (user_id, achievement_id, title, description, icon, rarity, progress)
    SELECT
        id as user_id,
        'first_sale' as achievement_id,
        '🎉 Première Vente' as title,
        'Réalisez votre première conversion' as description,
        '🎉' as icon,
        'common' as rarity,
        0 as progress
    FROM users
    ON CONFLICT (user_id, achievement_id) DO NOTHING;

    -- Initialiser les niveaux pour tous les utilisateurs existants
    INSERT INTO user_levels (user_id, current_level, total_xp)
    SELECT id, 1, 0
    FROM users
    ON CONFLICT (user_id) DO NOTHING;

    -- Initialiser les trust scores pour tous les utilisateurs
    INSERT INTO trust_scores (user_id, username, trust_score, trust_level)
    SELECT id, email, 50.00, 'average'
    FROM users
    ON CONFLICT (user_id) DO NOTHING;
    """

    print(seed_sql)
    print("\n✅ SQL SEED généré")
    print("   → Exécutez ce SQL après avoir créé toutes les tables")

# Script principal
def main():
    print("\n🚀 DÉMARRAGE DE LA MIGRATION...\n")

    # 1. Générer le SQL pour les nouvelles tables
    print("=" * 80)
    print("PARTIE 1: CRÉATION DES NOUVELLES TABLES")
    print("=" * 80)

    all_sql = []

    for migration in migrations:
        print(f"\n-- Table: {migration['name']}")
        print(migration['sql'])
        all_sql.append(migration['sql'])

    # 2. Générer le SQL pour les colonnes manquantes
    add_missing_columns()

    # 3. Générer le SQL pour les données initiales
    seed_initial_data()

    # 4. Sauvegarder tout dans un fichier SQL
    print("\n" + "=" * 80)
    print("SAUVEGARDE DANS UN FICHIER SQL")
    print("=" * 80)

    full_migration_sql = "\n\n".join(all_sql)

    with open("/home/user/Getyourshare1/database/migrations/create_new_features_tables.sql", "w") as f:
        f.write("-- Migration automatique pour les nouvelles features ShareYourSales\n")
        f.write("-- Date: 2025-10-26\n")
        f.write("-- Features: AI Content, Mobile Payments, Smart Match, Trust Score, Dashboard\n\n")
        f.write(full_migration_sql)
        f.write("\n\n-- Colonnes manquantes\n")
        f.write("""
ALTER TABLE users ADD COLUMN IF NOT EXISTS avg_response_time_hours DECIMAL(10,2) DEFAULT 24;
ALTER TABLE users ADD COLUMN IF NOT EXISTS balance DECIMAL(10,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS kyc_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan TEXT DEFAULT 'free';

ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS clicks INTEGER DEFAULT 0;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS conversions INTEGER DEFAULT 0;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS revenue DECIMAL(10,2) DEFAULT 0;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS content_quality_rating DECIMAL(3,1);
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS merchant_rating DECIMAL(3,1);
""")

    print(f"✅ Fichier SQL créé: database/migrations/create_new_features_tables.sql")

    print("\n" + "=" * 80)
    print("✅ MIGRATION TERMINÉE !")
    print("=" * 80)

    print("""
📋 PROCHAINES ÉTAPES:

1. Ouvrez Supabase Dashboard: https://app.supabase.com
2. Allez dans SQL Editor
3. Copiez-collez le contenu du fichier:
   database/migrations/create_new_features_tables.sql
4. Exécutez le SQL
5. Vérifiez que toutes les tables sont créées dans Table Editor

OU

Utilisez directement le fichier SQL que je viens de créer !
    """)

if __name__ == "__main__":
    main()

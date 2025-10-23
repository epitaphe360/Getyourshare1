"""
Création des tables manquantes pour les nouvelles fonctionnalités
"""
from supabase_client import get_supabase_client

def create_missing_tables():
    """Créer les tables manquantes"""
    supabase = get_supabase_client()
    
    print("🔨 Création des tables manquantes...")
    
    # Table invitations
    print("\n📧 Création table invitations...")
    try:
        result = supabase.table('invitations').select("*").limit(1).execute()
        print("✅ Table invitations existe déjà")
    except Exception as e:
        print(f"⚠️  Table invitations n'existe pas encore - à créer via SQL")
    
    # Table settings
    print("\n⚙️  Création table settings...")
    try:
        result = supabase.table('settings').select("*").limit(1).execute()
        print("✅ Table settings existe déjà")
    except Exception as e:
        print(f"⚠️  Table settings n'existe pas encore - à créer via SQL")
    
    # Table campaign_products
    print("\n🔗 Création table campaign_products...")
    try:
        result = supabase.table('campaign_products').select("*").limit(1).execute()
        print("✅ Table campaign_products existe déjà")
    except Exception as e:
        print(f"⚠️  Table campaign_products n'existe pas encore - à créer via SQL")
    
    print("\n" + "="*60)
    print("SQL à exécuter dans Supabase:")
    print("="*60)
    
    sql_script = """
-- Table invitations
CREATE TABLE IF NOT EXISTS invitations (
    id SERIAL PRIMARY KEY,
    merchant_id INTEGER REFERENCES users(id),
    influencer_id INTEGER REFERENCES users(id),
    campaign_id INTEGER REFERENCES campaigns(id),
    status VARCHAR(20) DEFAULT 'pending',
    message TEXT,
    commission_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    responded_at TIMESTAMP
);

-- Table settings
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table campaign_products (junction)
CREATE TABLE IF NOT EXISTS campaign_products (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(campaign_id, product_id)
);

-- Insertion des paramètres par défaut
INSERT INTO settings (key, value, description) VALUES
('platform_name', 'ShareYourSales', 'Nom de la plateforme'),
('commission_rate', '10', 'Taux de commission par défaut (%)'),
('min_payout', '50', 'Montant minimum pour un paiement (€)'),
('currency', 'EUR', 'Devise utilisée'),
('enable_2fa', 'false', 'Activer l''authentification 2FA')
ON CONFLICT (key) DO NOTHING;

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_invitations_merchant ON invitations(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invitations_influencer ON invitations(influencer_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON invitations(status);
CREATE INDEX IF NOT EXISTS idx_campaign_products_campaign ON campaign_products(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_products_product ON campaign_products(product_id);
"""
    
    print(sql_script)
    print("\n💡 Copiez ce SQL et exécutez-le dans l'éditeur SQL de Supabase")
    print("   URL: https://iamezkmapbhlhhvvsits.supabase.co")

if __name__ == "__main__":
    create_missing_tables()

-- Migration pour la table des liens d'affiliation
-- Date: 2025-11-03

-- ============================================
-- TABLE: Liens d'affiliation
-- ============================================

CREATE TABLE IF NOT EXISTS affiliate_links (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Affilié (influenceur)
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Produit associé
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  
  -- Code unique du lien
  code TEXT NOT NULL UNIQUE,
  
  -- Commission
  commission_rate DECIMAL(5,2) NOT NULL DEFAULT 10.00,
  
  -- Statut
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'expired', 'suspended')),
  
  -- Statistiques
  clicks INTEGER DEFAULT 0,
  conversions INTEGER DEFAULT 0,
  total_sales DECIMAL(10,2) DEFAULT 0,
  total_commission DECIMAL(10,2) DEFAULT 0,
  
  -- Métadonnées
  expires_at TIMESTAMP WITH TIME ZONE,
  last_used_at TIMESTAMP WITH TIME ZONE,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEX
-- ============================================

CREATE INDEX idx_affiliate_links_user ON affiliate_links(user_id);
CREATE INDEX idx_affiliate_links_product ON affiliate_links(product_id);
CREATE INDEX idx_affiliate_links_code ON affiliate_links(code);
CREATE INDEX idx_affiliate_links_status ON affiliate_links(status) WHERE status = 'active';

-- ============================================
-- TABLE: Clics sur les liens d'affiliation
-- ============================================

CREATE TABLE IF NOT EXISTS affiliate_clicks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  affiliate_link_id UUID NOT NULL REFERENCES affiliate_links(id) ON DELETE CASCADE,
  
  -- Informations du visiteur
  ip_address TEXT,
  user_agent TEXT,
  referrer TEXT,
  
  -- Géolocalisation
  country TEXT,
  city TEXT,
  
  -- Conversion
  converted BOOLEAN DEFAULT FALSE,
  order_id UUID,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_affiliate_clicks_link ON affiliate_clicks(affiliate_link_id);
CREATE INDEX idx_affiliate_clicks_converted ON affiliate_clicks(converted) WHERE converted = TRUE;

-- ============================================
-- TABLE: Commissions générées
-- ============================================

CREATE TABLE IF NOT EXISTS affiliate_commissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  affiliate_link_id UUID NOT NULL REFERENCES affiliate_links(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Commande associée
  order_id UUID,
  product_id UUID REFERENCES products(id),
  
  -- Montants
  sale_amount DECIMAL(10,2) NOT NULL,
  commission_rate DECIMAL(5,2) NOT NULL,
  commission_amount DECIMAL(10,2) NOT NULL,
  
  -- Statut paiement
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')),
  paid_at TIMESTAMP WITH TIME ZONE,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_affiliate_commissions_link ON affiliate_commissions(affiliate_link_id);
CREATE INDEX idx_affiliate_commissions_user ON affiliate_commissions(user_id);
CREATE INDEX idx_affiliate_commissions_status ON affiliate_commissions(status);

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON TABLE affiliate_links IS 
'Liens d''affiliation pour les influenceurs';

COMMENT ON TABLE affiliate_clicks IS 
'Clics trackés sur les liens d''affiliation';

COMMENT ON TABLE affiliate_commissions IS 
'Commissions générées par les ventes affiliées';

-- ============================================
-- FIN DE LA MIGRATION
-- ============================================

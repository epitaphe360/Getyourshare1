-- Migration pour système de collaboration Marchand-Influenceur
-- Date: 2025-11-03

-- ============================================
-- TABLE: Demandes de collaboration
-- ============================================

CREATE TABLE IF NOT EXISTS collaboration_requests (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Parties impliquées
  merchant_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  influencer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Produit concerné
  product_id UUID REFERENCES products(id) ON DELETE SET NULL,
  product_name TEXT NOT NULL,
  product_price DECIMAL(10,2),
  product_image TEXT,
  product_description TEXT,
  
  -- Termes de collaboration
  commission_rate DECIMAL(5,2) NOT NULL, -- % proposé par marchand
  counter_commission_rate DECIMAL(5,2), -- % contre-offre influenceur
  duration_months INTEGER DEFAULT 12, -- Durée collaboration
  
  -- Messages
  merchant_message TEXT,
  influencer_message TEXT, -- Pour contre-offre ou refus
  
  -- Statut
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'counter_offer', 'expired')),
  
  -- Contrat
  contract_accepted BOOLEAN DEFAULT FALSE,
  contract_accepted_at TIMESTAMP WITH TIME ZONE,
  contract_version TEXT DEFAULT 'v1.0',
  contract_terms JSONB, -- Termes du contrat
  merchant_signature TEXT, -- Hash signature
  influencer_signature TEXT,
  
  -- Lien d'affiliation généré
  affiliate_link_id UUID REFERENCES affiliate_links(id),
  
  -- Métadonnées
  viewed_by_influencer BOOLEAN DEFAULT FALSE,
  viewed_at TIMESTAMP WITH TIME ZONE,
  responded_at TIMESTAMP WITH TIME ZONE,
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEX
-- ============================================

CREATE INDEX idx_collab_merchant ON collaboration_requests(merchant_id, status);
CREATE INDEX idx_collab_influencer ON collaboration_requests(influencer_id, status);
CREATE INDEX idx_collab_status ON collaboration_requests(status) WHERE status = 'pending';
CREATE INDEX idx_collab_product ON collaboration_requests(product_id);

-- ============================================
-- TABLE: Historique des actions
-- ============================================

CREATE TABLE IF NOT EXISTS collaboration_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  collaboration_request_id UUID NOT NULL REFERENCES collaboration_requests(id) ON DELETE CASCADE,
  
  action TEXT NOT NULL CHECK (action IN (
    'created', 'viewed', 'accepted', 'rejected', 
    'counter_offer_sent', 'counter_offer_accepted', 'counter_offer_rejected',
    'contract_signed', 'expired', 'link_generated'
  )),
  
  actor_id UUID NOT NULL REFERENCES users(id),
  actor_role TEXT NOT NULL CHECK (actor_role IN ('merchant', 'influencer')),
  
  details JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_collab_history_request ON collaboration_history(collaboration_request_id);

-- ============================================
-- FONCTION: Créer demande de collaboration
-- ============================================

CREATE OR REPLACE FUNCTION create_collaboration_request(
  p_merchant_id UUID,
  p_influencer_id UUID,
  p_product_id UUID,
  p_commission_rate DECIMAL,
  p_message TEXT
)
RETURNS TABLE(
  request_id UUID,
  status TEXT,
  expires_at TIMESTAMP WITH TIME ZONE
) AS $$
DECLARE
  v_request_id UUID;
  v_product RECORD;
BEGIN
  -- Récupérer infos produit
  SELECT name, price, image_url, description
  INTO v_product
  FROM products
  WHERE id = p_product_id;
  
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Produit non trouvé';
  END IF;
  
  -- Vérifier qu'il n'existe pas déjà une demande en attente
  IF EXISTS (
    SELECT 1 FROM collaboration_requests
    WHERE merchant_id = p_merchant_id
    AND influencer_id = p_influencer_id
    AND product_id = p_product_id
    AND status = 'pending'
  ) THEN
    RAISE EXCEPTION 'Une demande existe déjà pour ce produit';
  END IF;
  
  -- Créer la demande
  INSERT INTO collaboration_requests (
    merchant_id,
    influencer_id,
    product_id,
    product_name,
    product_price,
    product_image,
    product_description,
    commission_rate,
    merchant_message,
    status
  ) VALUES (
    p_merchant_id,
    p_influencer_id,
    p_product_id,
    v_product.name,
    v_product.price,
    v_product.image_url,
    v_product.description,
    p_commission_rate,
    p_message,
    'pending'
  )
  RETURNING id INTO v_request_id;
  
  -- Logger l'action
  INSERT INTO collaboration_history (
    collaboration_request_id,
    action,
    actor_id,
    actor_role,
    details
  ) VALUES (
    v_request_id,
    'created',
    p_merchant_id,
    'merchant',
    jsonb_build_object(
      'commission_rate', p_commission_rate,
      'product_name', v_product.name
    )
  );
  
  RETURN QUERY
  SELECT 
    v_request_id,
    'pending'::TEXT,
    (NOW() + INTERVAL '30 days')::TIMESTAMP WITH TIME ZONE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Accepter demande
-- ============================================

CREATE OR REPLACE FUNCTION accept_collaboration_request(
  p_request_id UUID,
  p_influencer_id UUID
)
RETURNS BOOLEAN AS $$
BEGIN
  -- Vérifier que c'est le bon influenceur
  IF NOT EXISTS (
    SELECT 1 FROM collaboration_requests
    WHERE id = p_request_id
    AND influencer_id = p_influencer_id
    AND status = 'pending'
  ) THEN
    RAISE EXCEPTION 'Demande non valide ou déjà traitée';
  END IF;
  
  -- Mettre à jour le statut
  UPDATE collaboration_requests
  SET 
    status = 'accepted',
    responded_at = NOW(),
    updated_at = NOW()
  WHERE id = p_request_id;
  
  -- Logger
  INSERT INTO collaboration_history (
    collaboration_request_id,
    action,
    actor_id,
    actor_role
  ) VALUES (
    p_request_id,
    'accepted',
    p_influencer_id,
    'influencer'
  );
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Refuser demande
-- ============================================

CREATE OR REPLACE FUNCTION reject_collaboration_request(
  p_request_id UUID,
  p_influencer_id UUID,
  p_reason TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
  UPDATE collaboration_requests
  SET 
    status = 'rejected',
    influencer_message = p_reason,
    responded_at = NOW(),
    updated_at = NOW()
  WHERE id = p_request_id
  AND influencer_id = p_influencer_id;
  
  INSERT INTO collaboration_history (
    collaboration_request_id,
    action,
    actor_id,
    actor_role,
    details
  ) VALUES (
    p_request_id,
    'rejected',
    p_influencer_id,
    'influencer',
    jsonb_build_object('reason', p_reason)
  );
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Contre-offre
-- ============================================

CREATE OR REPLACE FUNCTION counter_offer_collaboration(
  p_request_id UUID,
  p_influencer_id UUID,
  p_counter_commission DECIMAL,
  p_message TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
  UPDATE collaboration_requests
  SET 
    status = 'counter_offer',
    counter_commission_rate = p_counter_commission,
    influencer_message = p_message,
    responded_at = NOW(),
    updated_at = NOW()
  WHERE id = p_request_id
  AND influencer_id = p_influencer_id;
  
  INSERT INTO collaboration_history (
    collaboration_request_id,
    action,
    actor_id,
    actor_role,
    details
  ) VALUES (
    p_request_id,
    'counter_offer_sent',
    p_influencer_id,
    'influencer',
    jsonb_build_object(
      'counter_commission', p_counter_commission,
      'message', p_message
    )
  );
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Accepter contrat
-- ============================================

CREATE OR REPLACE FUNCTION accept_contract(
  p_request_id UUID,
  p_user_id UUID,
  p_user_role TEXT,
  p_signature TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
  -- Mettre à jour la signature
  IF p_user_role = 'merchant' THEN
    UPDATE collaboration_requests
    SET merchant_signature = p_signature
    WHERE id = p_request_id;
  ELSE
    UPDATE collaboration_requests
    SET 
      influencer_signature = p_signature,
      contract_accepted = TRUE,
      contract_accepted_at = NOW()
    WHERE id = p_request_id;
  END IF;
  
  INSERT INTO collaboration_history (
    collaboration_request_id,
    action,
    actor_id,
    actor_role
  ) VALUES (
    p_request_id,
    'contract_signed',
    p_user_id,
    p_user_role
  );
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Générer lien affiliation
-- ============================================

CREATE OR REPLACE FUNCTION generate_affiliate_link_from_collaboration(
  p_request_id UUID
)
RETURNS UUID AS $$
DECLARE
  v_link_id UUID;
  v_request RECORD;
BEGIN
  -- Récupérer la demande
  SELECT * INTO v_request
  FROM collaboration_requests
  WHERE id = p_request_id
  AND status = 'accepted'
  AND contract_accepted = TRUE;
  
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Demande non valide pour génération de lien';
  END IF;
  
  -- Créer le lien d'affiliation
  INSERT INTO affiliate_links (
    user_id,
    product_id,
    code,
    commission_rate,
    status,
    expires_at
  ) VALUES (
    v_request.influencer_id,
    v_request.product_id,
    'COLLAB-' || substring(gen_random_uuid()::TEXT, 1, 8),
    COALESCE(v_request.counter_commission_rate, v_request.commission_rate),
    'active',
    NOW() + INTERVAL '1 year'
  )
  RETURNING id INTO v_link_id;
  
  -- Associer à la demande
  UPDATE collaboration_requests
  SET affiliate_link_id = v_link_id
  WHERE id = p_request_id;
  
  -- Logger
  INSERT INTO collaboration_history (
    collaboration_request_id,
    action,
    actor_id,
    actor_role,
    details
  ) VALUES (
    p_request_id,
    'link_generated',
    v_request.merchant_id,
    'merchant',
    jsonb_build_object('link_id', v_link_id)
  );
  
  RETURN v_link_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON TABLE collaboration_requests IS 
'Demandes de collaboration entre marchands et influenceurs';

COMMENT ON TABLE collaboration_history IS 
'Historique des actions sur les demandes de collaboration';

COMMENT ON FUNCTION create_collaboration_request IS 
'Créer une nouvelle demande de collaboration';

COMMENT ON FUNCTION accept_collaboration_request IS 
'Accepter une demande de collaboration';

COMMENT ON FUNCTION reject_collaboration_request IS 
'Refuser une demande de collaboration';

COMMENT ON FUNCTION counter_offer_collaboration IS 
'Faire une contre-offre sur la commission';

COMMENT ON FUNCTION accept_contract IS 
'Accepter et signer le contrat de collaboration';

COMMENT ON FUNCTION generate_affiliate_link_from_collaboration IS 
'Générer automatiquement le lien d''affiliation après acceptation';

-- ============================================
-- FIN DE LA MIGRATION
-- ============================================

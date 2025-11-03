-- Migration pour activer les trials gratuits 14 jours
-- Date: 2025-11-03

-- ============================================
-- FONCTION: Créer abonnement avec trial 14 jours
-- ============================================

CREATE OR REPLACE FUNCTION create_subscription_with_trial(
  p_user_id UUID,
  p_plan_code TEXT,
  p_user_type TEXT DEFAULT 'merchant'
)
RETURNS TABLE(
  subscription_id UUID,
  trial_end TIMESTAMP WITH TIME ZONE,
  message TEXT
) AS $$
DECLARE
  v_plan_id UUID;
  v_subscription_id UUID;
  v_trial_end TIMESTAMP WITH TIME ZONE;
  v_is_freemium BOOLEAN;
BEGIN
  -- Vérifier si le plan existe
  SELECT id, (code LIKE '%freemium%')
  INTO v_plan_id, v_is_freemium
  FROM subscription_plans
  WHERE code = p_plan_code
  AND user_type = p_user_type
  AND is_active = TRUE;

  IF v_plan_id IS NULL THEN
    RAISE EXCEPTION 'Plan % non trouvé', p_plan_code;
  END IF;

  -- Calculer trial_end (14 jours) seulement pour plans non-freemium
  IF v_is_freemium THEN
    v_trial_end := NULL;
  ELSE
    v_trial_end := NOW() + INTERVAL '14 days';
  END IF;

  -- Créer l'abonnement
  INSERT INTO subscriptions (
    user_id,
    plan_id,
    status,
    trial_start,
    trial_end,
    current_period_start,
    current_period_end
  ) VALUES (
    p_user_id,
    v_plan_id,
    CASE WHEN v_is_freemium THEN 'active' ELSE 'trialing' END,
    CASE WHEN v_is_freemium THEN NULL ELSE NOW() END,
    v_trial_end,
    NOW(),
    NOW() + INTERVAL '1 month'
  )
  RETURNING id INTO v_subscription_id;

  -- Créer entrée dans subscription_history
  INSERT INTO subscription_history (
    subscription_id,
    action,
    plan_id,
    metadata
  ) VALUES (
    v_subscription_id,
    CASE WHEN v_is_freemium THEN 'created' ELSE 'trial_started' END,
    v_plan_id,
    jsonb_build_object(
      'trial_days', CASE WHEN v_is_freemium THEN 0 ELSE 14 END,
      'trial_end', v_trial_end
    )
  );

  -- Initialiser les compteurs d'usage
  INSERT INTO subscription_usage (
    subscription_id,
    resource_type,
    current_count,
    last_reset_at
  )
  SELECT
    v_subscription_id,
    unnest(ARRAY['products', 'campaigns', 'affiliates']) as resource_type,
    0,
    NOW();

  RETURN QUERY
  SELECT 
    v_subscription_id,
    v_trial_end,
    CASE 
      WHEN v_is_freemium THEN 'Abonnement Freemium créé'
      ELSE 'Trial de 14 jours activé'
    END;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Vérifier si trial est actif
-- ============================================

CREATE OR REPLACE FUNCTION is_trial_active(p_subscription_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS(
    SELECT 1
    FROM subscriptions
    WHERE id = p_subscription_id
    AND status = 'trialing'
    AND trial_end > NOW()
  );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Obtenir jours restants du trial
-- ============================================

CREATE OR REPLACE FUNCTION get_trial_days_left(p_subscription_id UUID)
RETURNS INTEGER AS $$
DECLARE
  v_days_left INTEGER;
BEGIN
  SELECT EXTRACT(DAY FROM (trial_end - NOW()))::INTEGER
  INTO v_days_left
  FROM subscriptions
  WHERE id = p_subscription_id
  AND status = 'trialing'
  AND trial_end > NOW();

  RETURN COALESCE(v_days_left, 0);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Convertir trial en abonnement payant
-- ============================================

CREATE OR REPLACE FUNCTION convert_trial_to_paid(
  p_subscription_id UUID,
  p_stripe_subscription_id TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
  -- Mettre à jour le statut
  UPDATE subscriptions
  SET 
    status = 'active',
    stripe_subscription_id = p_stripe_subscription_id,
    updated_at = NOW()
  WHERE id = p_subscription_id
  AND status = 'trialing';

  -- Logger dans l'historique
  INSERT INTO subscription_history (
    subscription_id,
    action,
    plan_id,
    metadata
  )
  SELECT
    p_subscription_id,
    'trial_converted',
    plan_id,
    jsonb_build_object(
      'stripe_subscription_id', p_stripe_subscription_id,
      'converted_at', NOW()
    )
  FROM subscriptions
  WHERE id = p_subscription_id;

  RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Gérer expiration du trial
-- ============================================

CREATE OR REPLACE FUNCTION handle_expired_trials()
RETURNS TABLE(
  subscription_id UUID,
  user_id UUID,
  plan_code TEXT,
  action_taken TEXT
) AS $$
BEGIN
  -- Trouver tous les trials expirés
  RETURN QUERY
  WITH expired_trials AS (
    SELECT 
      s.id as sub_id,
      s.user_id as usr_id,
      sp.code as pln_code,
      sp.user_type
    FROM subscriptions s
    JOIN subscription_plans sp ON s.plan_id = sp.id
    WHERE s.status = 'trialing'
    AND s.trial_end <= NOW()
  ),
  updated AS (
    -- Downgrade vers Freemium
    UPDATE subscriptions s
    SET 
      plan_id = (
        SELECT id 
        FROM subscription_plans 
        WHERE code = CASE 
          WHEN et.user_type = 'merchant' THEN 'merchant_freemium'
          ELSE 'influencer_freemium'
        END
        LIMIT 1
      ),
      status = 'active',
      trial_start = NULL,
      trial_end = NULL,
      updated_at = NOW()
    FROM expired_trials et
    WHERE s.id = et.sub_id
    RETURNING s.id, s.user_id
  ),
  logged AS (
    -- Logger dans l'historique
    INSERT INTO subscription_history (
      subscription_id,
      action,
      plan_id,
      metadata
    )
    SELECT
      u.id,
      'trial_expired_downgraded',
      (SELECT id FROM subscription_plans WHERE code LIKE '%freemium%' LIMIT 1),
      jsonb_build_object('reason', 'trial_expired', 'expired_at', NOW())
    FROM updated u
    RETURNING subscription_id
  )
  SELECT 
    et.sub_id,
    et.usr_id,
    et.pln_code,
    'downgraded_to_freemium'::TEXT
  FROM expired_trials et;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON FUNCTION create_subscription_with_trial IS 
'Crée un abonnement avec trial de 14 jours (sauf freemium)';

COMMENT ON FUNCTION is_trial_active IS 
'Vérifie si une période d''essai est active';

COMMENT ON FUNCTION get_trial_days_left IS 
'Retourne le nombre de jours restants dans le trial';

COMMENT ON FUNCTION convert_trial_to_paid IS 
'Convertit un trial en abonnement payant après paiement';

COMMENT ON FUNCTION handle_expired_trials IS 
'Downgrade automatiquement les trials expirés vers Freemium';

-- ============================================
-- INDEX pour optimiser les requêtes trial
-- ============================================

CREATE INDEX IF NOT EXISTS idx_subscriptions_trial_status 
ON subscriptions(status, trial_end) 
WHERE status = 'trialing';

-- ============================================
-- FIN DE LA MIGRATION
-- ============================================

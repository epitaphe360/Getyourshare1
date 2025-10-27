-- =============================================================================
-- Migration: Transactional helpers for sales & payouts
-- Description: Adds stored procedures to guarantee atomic operations when
--              creating sales and approving payouts.
-- Date: 2025-10-26
-- =============================================================================

CREATE OR REPLACE FUNCTION create_sale_transaction(
    p_link_id UUID,
    p_product_id UUID,
    p_influencer_id UUID,
    p_merchant_id UUID,
    p_amount NUMERIC,
    p_currency TEXT DEFAULT 'EUR',
    p_quantity INTEGER DEFAULT 1,
    p_customer_email TEXT DEFAULT NULL,
    p_customer_name TEXT DEFAULT NULL,
    p_payment_status TEXT DEFAULT 'pending',
    p_status TEXT DEFAULT 'completed'
)
RETURNS sales AS $$
DECLARE
    v_product RECORD;
    v_link RECORD;
    v_sale sales%ROWTYPE;
    v_commission_rate NUMERIC;
    v_commission_type TEXT;
    v_influencer_commission NUMERIC;
    v_platform_commission NUMERIC;
    v_merchant_revenue NUMERIC;
BEGIN
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Le montant de la vente doit être supérieur à 0.';
    END IF;

    IF COALESCE(p_quantity, 1) <= 0 THEN
        RAISE EXCEPTION 'La quantité doit être positive.';
    END IF;

    IF p_status NOT IN ('pending', 'completed', 'refunded', 'cancelled') THEN
        RAISE EXCEPTION 'Statut de vente % non supporté', p_status;
    END IF;

    IF p_payment_status NOT IN ('pending', 'paid') THEN
        RAISE EXCEPTION 'Statut de paiement % non supporté', p_payment_status;
    END IF;

    SELECT commission_rate, COALESCE(commission_type, 'percentage') AS commission_type
         , merchant_id
    INTO v_product
    FROM products
    WHERE id = p_product_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Product % introuvable', p_product_id;
    END IF;

    IF v_product.merchant_id <> p_merchant_id THEN
        RAISE EXCEPTION 'Le produit % appartient à un autre marchand.', p_product_id;
    END IF;

    SELECT product_id, influencer_id
    INTO v_link
    FROM trackable_links
    WHERE id = p_link_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Lien tracké % introuvable', p_link_id;
    END IF;

    IF v_link.product_id <> p_product_id THEN
        RAISE EXCEPTION 'Le lien tracké ne correspond pas au produit indiqué.';
    END IF;

    IF v_link.influencer_id <> p_influencer_id THEN
        RAISE EXCEPTION 'Le lien tracké ne correspond pas à l''influenceur indiqué.';
    END IF;

    v_commission_rate := COALESCE(v_product.commission_rate, 0);
    v_commission_type := v_product.commission_type;

    IF v_commission_type = 'fixed' THEN
        v_influencer_commission := ROUND(v_commission_rate, 2);
    ELSE
        v_influencer_commission := ROUND(p_amount * (v_commission_rate / 100), 2);
    END IF;

    v_platform_commission := ROUND(p_amount * 0.05, 2);
    v_merchant_revenue := ROUND(p_amount - v_influencer_commission - v_platform_commission, 2);

    INSERT INTO sales (
        link_id,
        product_id,
        influencer_id,
        merchant_id,
        customer_email,
        customer_name,
        quantity,
        amount,
        currency,
        influencer_commission,
        platform_commission,
        merchant_revenue,
        status,
        payment_status,
        sale_timestamp,
        created_at
    )
    VALUES (
        p_link_id,
        p_product_id,
        p_influencer_id,
        p_merchant_id,
        p_customer_email,
        p_customer_name,
        COALESCE(p_quantity, 1),
        p_amount,
        p_currency,
        v_influencer_commission,
        v_platform_commission,
        v_merchant_revenue,
        p_status,
        p_payment_status,
        NOW(),
        NOW()
    )
    RETURNING * INTO v_sale;

    INSERT INTO commissions (
        sale_id,
        influencer_id,
        amount,
        currency,
        status,
        created_at
    )
    VALUES (
        v_sale.id,
        p_influencer_id,
        v_influencer_commission,
        p_currency,
        'pending',
        NOW()
    );

    UPDATE trackable_links
    SET
        sales = COALESCE(sales, 0) + 1,
        total_revenue = COALESCE(total_revenue, 0) + p_amount,
        total_commission = COALESCE(total_commission, 0) + v_influencer_commission,
        conversion_rate = CASE
            WHEN COALESCE(clicks, 0) > 0
                THEN ROUND(((COALESCE(sales, 0) + 1)::NUMERIC / COALESCE(clicks, 1)) * 100, 2)
            ELSE conversion_rate
        END,
        updated_at = NOW()
    WHERE id = p_link_id;

    UPDATE influencers
    SET
        total_sales = COALESCE(total_sales, 0) + 1,
        total_earnings = COALESCE(total_earnings, 0) + v_influencer_commission,
        balance = COALESCE(balance, 0) + v_influencer_commission,
        updated_at = NOW()
    WHERE id = p_influencer_id;

    UPDATE merchants
    SET
        total_sales = COALESCE(total_sales, 0) + 1,
        updated_at = NOW()
    WHERE id = p_merchant_id;

    UPDATE products
    SET
        total_sales = COALESCE(total_sales, 0) + 1,
        updated_at = NOW()
    WHERE id = p_product_id;

    RETURN v_sale;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION approve_payout_transaction(
    p_commission_id UUID,
    p_status TEXT DEFAULT 'approved'
)
RETURNS BOOLEAN AS $$
DECLARE
    v_commission RECORD;
BEGIN
    SELECT
        c.id,
        c.sale_id,
        c.influencer_id,
        c.amount,
        c.currency,
        c.status,
        s.merchant_id,
        i.balance AS influencer_balance
    INTO v_commission
    FROM commissions c
    LEFT JOIN sales s ON s.id = c.sale_id
    JOIN influencers i ON i.id = c.influencer_id
    WHERE c.id = p_commission_id
    FOR UPDATE OF c, i;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Commission % introuvable', p_commission_id;
    END IF;

    IF v_commission.influencer_balance IS NULL THEN
        RAISE EXCEPTION 'Influenceur introuvable pour la commission %', p_commission_id;
    END IF;

    IF v_commission.status = 'paid' AND p_status <> 'paid' THEN
        RAISE EXCEPTION 'La commission % a déjà été réglée et ne peut pas changer de statut.', p_commission_id;
    END IF;

    IF p_status = v_commission.status THEN
        RETURN TRUE;
    END IF;

    IF v_commission.amount <= 0 THEN
        RAISE EXCEPTION 'Montant invalide pour la commission %', p_commission_id;
    END IF;

    IF p_status NOT IN ('approved', 'paid', 'rejected', 'pending') THEN
        RAISE EXCEPTION 'Statut % non supporté', p_status;
    END IF;

    -- Gestion des transitions de statut avec ajustement du solde
    IF p_status = 'approved' AND v_commission.status = 'pending' THEN
        IF COALESCE(v_commission.influencer_balance, 0) < v_commission.amount THEN
            RAISE EXCEPTION 'Solde insuffisant pour approuver la commission %', p_commission_id;
        END IF;
        UPDATE influencers
        SET balance = COALESCE(balance, 0) - v_commission.amount
        WHERE id = v_commission.influencer_id;
    ELSIF p_status = 'pending' AND v_commission.status = 'approved' THEN
        UPDATE influencers
        SET balance = COALESCE(balance, 0) + v_commission.amount
        WHERE id = v_commission.influencer_id;
    ELSIF p_status = 'rejected' AND v_commission.status = 'approved' THEN
        UPDATE influencers
        SET balance = COALESCE(balance, 0) + v_commission.amount
        WHERE id = v_commission.influencer_id;
    ELSIF p_status = 'rejected' AND v_commission.status = 'pending' THEN
        -- Aucun ajustement, on libère simplement la commission
        NULL;
    ELSIF p_status = 'paid' AND v_commission.status <> 'approved' THEN
        RAISE EXCEPTION 'La commission doit être approuvée avant d''être payée.';
    ELSIF p_status = 'paid' AND v_commission.status = 'approved' THEN
        IF v_commission.merchant_id IS NOT NULL THEN
            UPDATE merchants
            SET
                total_commission_paid = COALESCE(total_commission_paid, 0) + v_commission.amount,
                updated_at = NOW()
            WHERE id = v_commission.merchant_id;
        END IF;
    END IF;

    UPDATE commissions
    SET
        status = p_status,
        approved_at = CASE
            WHEN p_status = 'approved' AND v_commission.status = 'pending' THEN NOW()
            WHEN p_status IN ('pending', 'rejected') THEN NULL
            ELSE approved_at
        END,
        paid_at = CASE
            WHEN p_status = 'paid' THEN NOW()
            WHEN p_status IN ('pending', 'rejected') THEN NULL
            ELSE paid_at
        END
    WHERE id = p_commission_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Notes d'utilisation
-- 1. create_sale_transaction :
--    - Déclencher lors de la validation d'une vente traquée.
--    - Garantit la création de la vente, de la commission et la mise à jour
--      des métriques clés (lien, influenceur, marchand, produit) en une seule
--      transaction.
--    - Exemple d'appel :
--        SELECT create_sale_transaction(
--            p_link_id => '...UUID...',
--            p_product_id => '...UUID...',
--            p_influencer_id => '...UUID...',
--            p_merchant_id => '...UUID...',
--            p_amount => 199.90,
--            p_currency => 'EUR',
--            p_quantity => 1,
--            p_customer_email => 'client@example.com',
--            p_customer_name => 'Client Demo'
--        );
--
-- 2. approve_payout_transaction :
--    - À utiliser dans le workflow d'approbation des retraits.
--    - Gère les transitions de statut autorisées et l'ajustement du solde
--      disponible de l'influenceur.
--    - Exemple d'appel :
--        SELECT approve_payout_transaction(
--            p_commission_id => '...UUID...',
--            p_status => 'approved'
--        );
--
-- 3. Rollback manuel (DOWN) :
--    - DROP FUNCTION IF EXISTS create_sale_transaction(
--        UUID, UUID, UUID, UUID, NUMERIC, TEXT, INTEGER,
--        TEXT, TEXT, TEXT, TEXT
--      );
--    - DROP FUNCTION IF EXISTS approve_payout_transaction(UUID, TEXT);
-- ============================================================================

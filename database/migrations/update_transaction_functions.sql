-- =============================================================================
-- Migration: Update transaction functions (remove metadata parameter)
-- Description: Drops old version of create_sale_transaction with metadata
--              and recreates it without that parameter to match schema.
-- Date: 2025-10-27
-- =============================================================================

-- Drop the old version with metadata parameter
DROP FUNCTION IF EXISTS create_sale_transaction(
    UUID, UUID, UUID, UUID, NUMERIC, TEXT, INTEGER,
    TEXT, TEXT, TEXT, TEXT, JSONB
);

-- Recreate the function without metadata
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

-- ============================================================================
-- Fin de la migration
-- ============================================================================

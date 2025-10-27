-- ============================================================================
-- MIGRATION: Système de Gateways de Paiement Multi-Gateway (Maroc)
-- Description: Support CMI, PayZen, Société Générale Maroc
-- Date: 2025-10-23
-- ============================================================================

-- ============================================================================
-- 1. ALTER TABLE: merchants - Ajouter configuration gateway
-- ============================================================================
ALTER TABLE merchants
ADD COLUMN IF NOT EXISTS payment_gateway VARCHAR(50) DEFAULT 'manual',
ADD COLUMN IF NOT EXISTS gateway_config JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS auto_debit_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS gateway_activated_at TIMESTAMP;

COMMENT ON COLUMN merchants.payment_gateway IS 'Gateway utilisé: manual, cmi, payzen, sg_maroc';
COMMENT ON COLUMN merchants.gateway_config IS 'Configuration JSON du gateway (API keys, merchant IDs, etc.)';
COMMENT ON COLUMN merchants.auto_debit_enabled IS 'Si TRUE, prélèvement automatique activé';

-- ============================================================================
-- 2. CREATE TABLE: platform_invoices
-- Description: Factures émises par la plateforme aux merchants
-- ============================================================================
CREATE TABLE IF NOT EXISTS platform_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    
    -- Numérotation
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    
    -- Période facturée
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Montants
    total_sales_amount DECIMAL(10, 2) DEFAULT 0,
    platform_commission DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    
    -- Devise
    currency VARCHAR(3) DEFAULT 'MAD',
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    -- Status possibles: pending, sent, viewed, paid, overdue, cancelled
    
    -- Paiement
    payment_method VARCHAR(50),  -- manual, cmi, payzen, sg_maroc
    paid_at TIMESTAMP,
    payment_reference VARCHAR(255),
    
    -- Fichiers
    pdf_url TEXT,
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_platform_invoices_merchant ON platform_invoices(merchant_id);
CREATE INDEX idx_platform_invoices_status ON platform_invoices(status);
CREATE INDEX idx_platform_invoices_due_date ON platform_invoices(due_date);
CREATE INDEX idx_platform_invoices_number ON platform_invoices(invoice_number);

-- ============================================================================
-- 3. CREATE TABLE: invoice_line_items
-- Description: Détail des lignes de facture (ventes individuelles)
-- ============================================================================
CREATE TABLE IF NOT EXISTS invoice_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES platform_invoices(id) ON DELETE CASCADE,
    sale_id UUID REFERENCES sales(id) ON DELETE SET NULL,
    
    -- Détails
    description TEXT NOT NULL,
    sale_date DATE,
    sale_amount DECIMAL(10, 2) NOT NULL,
    commission_rate DECIMAL(5, 2),
    commission_amount DECIMAL(10, 2) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoice_line_items_invoice ON invoice_line_items(invoice_id);
CREATE INDEX idx_invoice_line_items_sale ON invoice_line_items(sale_id);

-- ============================================================================
-- 4. CREATE TABLE: gateway_transactions
-- Description: Historique des transactions avec les gateways de paiement
-- ============================================================================
CREATE TABLE IF NOT EXISTS gateway_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES platform_invoices(id) ON DELETE SET NULL,
    
    -- Gateway
    gateway VARCHAR(50) NOT NULL,  -- cmi, payzen, sg_maroc
    transaction_id VARCHAR(255),  -- ID externe du gateway
    order_id VARCHAR(255),  -- ID de commande interne
    
    -- Montants
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'MAD',
    fees DECIMAL(10, 2) DEFAULT 0,
    net_amount DECIMAL(10, 2),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    -- Status possibles: pending, processing, completed, failed, refunded, cancelled
    failure_reason TEXT,
    
    -- URLs
    payment_url TEXT,
    redirect_url TEXT,
    
    -- Données
    request_payload JSONB,
    response_payload JSONB,
    webhook_payload JSONB,
    
    -- Sécurité
    signature VARCHAR(500),
    ip_address VARCHAR(45),
    
    -- Timestamps
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gateway_transactions_merchant ON gateway_transactions(merchant_id);
CREATE INDEX idx_gateway_transactions_invoice ON gateway_transactions(invoice_id);
CREATE INDEX idx_gateway_transactions_status ON gateway_transactions(status);
CREATE INDEX idx_gateway_transactions_gateway ON gateway_transactions(gateway);
CREATE INDEX idx_gateway_transactions_transaction_id ON gateway_transactions(transaction_id);

-- ============================================================================
-- 5. CREATE TABLE: payment_gateway_logs
-- Description: Logs détaillés des communications avec les gateways
-- ============================================================================
CREATE TABLE IF NOT EXISTS payment_gateway_logs (
    id BIGSERIAL PRIMARY KEY,
    transaction_id UUID REFERENCES gateway_transactions(id) ON DELETE CASCADE,
    
    -- Type d'événement
    event_type VARCHAR(100) NOT NULL,
    -- Types: api_request, api_response, webhook_received, signature_verified, error
    
    -- Données
    request_url TEXT,
    request_method VARCHAR(10),
    request_headers JSONB,
    request_body JSONB,
    response_status INTEGER,
    response_headers JSONB,
    response_body JSONB,
    
    -- Erreur
    error_message TEXT,
    error_code VARCHAR(50),
    
    -- Performance
    response_time_ms INTEGER,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payment_gateway_logs_transaction ON payment_gateway_logs(transaction_id);
CREATE INDEX idx_payment_gateway_logs_event_type ON payment_gateway_logs(event_type);
CREATE INDEX idx_payment_gateway_logs_created_at ON payment_gateway_logs(created_at DESC);

-- ============================================================================
-- 6. CREATE FUNCTION: Generate Invoice Number
-- Description: Génère un numéro de facture unique (Format: INV-2025-10-0001)
-- ============================================================================
CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    current_year VARCHAR(4);
    current_month VARCHAR(2);
    last_number INTEGER;
    new_number VARCHAR(4);
BEGIN
    current_year := TO_CHAR(CURRENT_DATE, 'YYYY');
    current_month := TO_CHAR(CURRENT_DATE, 'MM');
    
    -- Récupérer le dernier numéro du mois
    SELECT COALESCE(
        MAX(
            CAST(
                SUBSTRING(invoice_number FROM '[0-9]+$') AS INTEGER
            )
        ), 0
    ) INTO last_number
    FROM platform_invoices
    WHERE invoice_number LIKE 'INV-' || current_year || '-' || current_month || '-%';
    
    -- Incrémenter
    new_number := LPAD((last_number + 1)::TEXT, 4, '0');
    
    RETURN 'INV-' || current_year || '-' || current_month || '-' || new_number;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. CREATE FUNCTION: Auto-update updated_at
-- Description: Trigger pour mettre à jour automatiquement updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer aux tables appropriées
CREATE TRIGGER update_platform_invoices_updated_at
    BEFORE UPDATE ON platform_invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gateway_transactions_updated_at
    BEFORE UPDATE ON gateway_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 8. MATERIALIZED VIEW: Gateway Statistics
-- Description: Statistiques agrégées par gateway
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS gateway_statistics CASCADE;

CREATE MATERIALIZED VIEW gateway_statistics AS
SELECT
    gt.gateway,
    COUNT(DISTINCT gt.id) AS total_transactions,
    COUNT(DISTINCT CASE WHEN gt.status = 'completed' THEN gt.id END) AS successful_transactions,
    COUNT(DISTINCT CASE WHEN gt.status = 'failed' THEN gt.id END) AS failed_transactions,
    ROUND(
        COUNT(DISTINCT CASE WHEN gt.status = 'completed' THEN gt.id END)::NUMERIC * 100.0 /
        NULLIF(COUNT(DISTINCT gt.id), 0),
        2
    ) AS success_rate,
    SUM(CASE WHEN gt.status = 'completed' THEN gt.amount ELSE 0 END) AS total_amount_processed,
    SUM(CASE WHEN gt.status = 'completed' THEN gt.fees ELSE 0 END) AS total_fees_paid,
    SUM(CASE WHEN gt.status = 'completed' THEN gt.net_amount ELSE 0 END) AS total_net_amount,
    AVG(CASE WHEN gt.status = 'completed' THEN EXTRACT(EPOCH FROM (gt.completed_at - gt.initiated_at)) END) AS avg_completion_time_seconds,
    MAX(gt.created_at) AS last_transaction_date
FROM gateway_transactions gt
GROUP BY gt.gateway;

CREATE INDEX idx_gateway_statistics_gateway ON gateway_statistics(gateway);

-- ============================================================================
-- 9. MATERIALIZED VIEW: Merchant Payment Summary
-- Description: Résumé des paiements par merchant
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS merchant_payment_summary CASCADE;

CREATE MATERIALIZED VIEW merchant_payment_summary AS
SELECT
    m.id AS merchant_id,
    m.company_name,
    m.payment_gateway,
    m.auto_debit_enabled,
    
    -- Factures
    COUNT(DISTINCT pi.id) AS total_invoices,
    COUNT(DISTINCT CASE WHEN pi.status = 'paid' THEN pi.id END) AS paid_invoices,
    COUNT(DISTINCT CASE WHEN pi.status = 'overdue' THEN pi.id END) AS overdue_invoices,
    
    -- Montants
    SUM(CASE WHEN pi.status = 'paid' THEN pi.total_amount ELSE 0 END) AS total_paid,
    SUM(CASE WHEN pi.status IN ('pending', 'sent', 'viewed') THEN pi.total_amount ELSE 0 END) AS total_pending,
    SUM(CASE WHEN pi.status = 'overdue' THEN pi.total_amount ELSE 0 END) AS total_overdue,
    
    -- Dates
    MAX(pi.paid_at) AS last_payment_date,
    MIN(CASE WHEN pi.status = 'overdue' THEN pi.due_date END) AS earliest_overdue_date
    
FROM merchants m
LEFT JOIN platform_invoices pi ON m.id = pi.merchant_id
GROUP BY m.id, m.company_name, m.payment_gateway, m.auto_debit_enabled;

CREATE INDEX idx_merchant_payment_summary_merchant ON merchant_payment_summary(merchant_id);

-- ============================================================================
-- 10. INSERT: Données de configuration initiales
-- ============================================================================

-- Ajouter les gateways disponibles dans une table de référence
CREATE TABLE IF NOT EXISTS payment_gateway_configs (
    id SERIAL PRIMARY KEY,
    gateway_code VARCHAR(50) UNIQUE NOT NULL,
    gateway_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    countries VARCHAR(10)[] DEFAULT ARRAY['MA'],
    currencies VARCHAR(3)[] DEFAULT ARRAY['MAD'],
    fee_percentage DECIMAL(5, 2),
    fee_fixed DECIMAL(10, 2),
    settlement_days INTEGER,
    supports_split_payment BOOLEAN DEFAULT FALSE,
    configuration_fields JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO payment_gateway_configs (gateway_code, gateway_name, description, fee_percentage, fee_fixed, settlement_days, supports_split_payment, configuration_fields) VALUES
('cmi', 'CMI - Centre Monétique Interbancaire', 'Solution de paiement nationale marocaine', 1.75, 0, 2, FALSE, 
 '{"required_fields": ["cmi_merchant_id", "cmi_api_key", "cmi_store_key", "cmi_terminal_id"]}'),
 
('payzen', 'PayZen / Lyra', 'Solution de paiement française populaire au Maroc', 2.00, 0, 1, TRUE,
 '{"required_fields": ["payzen_shop_id", "payzen_api_key", "payzen_secret_key", "payzen_mode"]}'),
 
('sg_maroc', 'Société Générale Maroc - e-Payment', 'TPE virtuel + API Société Générale', 2.00, 0, 2, FALSE,
 '{"required_fields": ["sg_merchant_code", "sg_terminal_id", "sg_api_username", "sg_api_password", "sg_certificate"]}'),
 
('manual', 'Paiement Manuel', 'Facturation et suivi manuel des paiements', 0, 0, 30, FALSE,
 '{"required_fields": []}');

-- ============================================================================
-- 11. MIGRATION SUMMARY
-- ============================================================================
-- ✅ Tables créées:
--   - platform_invoices (factures plateforme)
--   - invoice_line_items (détails factures)
--   - gateway_transactions (transactions gateways)
--   - payment_gateway_logs (logs communications)
--   - payment_gateway_configs (configurations gateways)
--
-- ✅ Colonnes ajoutées à merchants:
--   - payment_gateway
--   - gateway_config
--   - auto_debit_enabled
--   - gateway_activated_at
--
-- ✅ Fonctions créées:
--   - generate_invoice_number()
--   - update_updated_at_column()
--
-- ✅ Vues matérialisées:
--   - gateway_statistics
--   - merchant_payment_summary
--
-- ✅ Indexes créés pour performance
--
-- ✅ Triggers créés pour auto-update
--
-- ============================================================================

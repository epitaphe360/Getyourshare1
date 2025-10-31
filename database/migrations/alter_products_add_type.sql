-- ============================================
-- ALTER PRODUCTS TABLE - Add Product Type
-- Support for both Products and Services
-- ============================================

-- Ajouter le champ 'type' pour distinguer produits physiques et services
ALTER TABLE products ADD COLUMN IF NOT EXISTS type VARCHAR(50) DEFAULT 'product'
CHECK (type IN ('product', 'service'));

-- Créer un index pour le type
CREATE INDEX IF NOT EXISTS idx_products_type ON products(type);

-- Ajouter des champs spécifiques aux services
ALTER TABLE products ADD COLUMN IF NOT EXISTS service_duration INTEGER; -- Durée en minutes
ALTER TABLE products ADD COLUMN IF NOT EXISTS service_delivery VARCHAR(50)
CHECK (service_delivery IN ('online', 'in_person', 'hybrid'));

-- Mettre à jour les produits existants comme 'product' par défaut
UPDATE products SET type = 'product' WHERE type IS NULL;

-- ============================================
-- Commentaires
-- ============================================

COMMENT ON COLUMN products.type IS 'Type: product (physique) ou service (immatériel)';
COMMENT ON COLUMN products.service_duration IS 'Durée du service en minutes (pour services uniquement)';
COMMENT ON COLUMN products.service_delivery IS 'Mode de livraison du service: online, in_person, hybrid';

-- ============================================
-- Vue: Produits uniquement
-- ============================================

CREATE OR REPLACE VIEW v_products_only AS
SELECT * FROM products WHERE type = 'product' AND is_available = TRUE;

-- ============================================
-- Vue: Services uniquement
-- ============================================

CREATE OR REPLACE VIEW v_services_only AS
SELECT * FROM products WHERE type = 'service' AND is_available = TRUE;

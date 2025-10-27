-- Migration pour nettoyer l'ancien système dual-table d'affiliation
-- Supprimer l'ancienne table affiliation_requests et toutes les références associées

-- Supprimer la table affiliation_requests si elle existe
DROP TABLE IF EXISTS affiliation_requests CASCADE;

-- Supprimer les anciennes vues si elles existent encore (au cas où)
DROP VIEW IF EXISTS old_affiliation_requests CASCADE;
DROP VIEW IF EXISTS old_merchant_affiliation_requests CASCADE;

-- Supprimer les anciennes fonctions si elles existent encore
DROP FUNCTION IF EXISTS old_create_affiliation_request(UUID, UUID, TEXT) CASCADE;
DROP FUNCTION IF EXISTS old_approve_affiliation_request(UUID, TEXT, UUID) CASCADE;
DROP FUNCTION IF EXISTS old_reject_affiliation_request(UUID, TEXT, UUID) CASCADE;

-- Commentaire sur la migration
COMMENT ON DATABASE postgres IS 'Système d''affiliation unifié migré - ancienne table affiliation_requests supprimée';

-- ============================================
-- VÉRIFICATION DE LA STRUCTURE DE LA TABLE USERS
-- ============================================
-- Ce script vérifie les colonnes existantes dans la table users

-- Afficher toutes les colonnes de la table users
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

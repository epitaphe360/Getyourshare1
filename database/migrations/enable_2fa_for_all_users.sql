-- ============================================
-- ACTIVER LA 2FA POUR TOUS LES UTILISATEURS
-- ============================================
-- Script pour activer l'authentification à 2 facteurs
-- pour tous les comptes de test
-- 
-- À exécuter dans Supabase SQL Editor:
-- 1. Ouvrez https://supabase.com/dashboard
-- 2. Sélectionnez votre projet
-- 3. Allez dans "SQL Editor"
-- 4. Créez une nouvelle requête
-- 5. Copiez-collez ce script
-- 6. Cliquez sur "Run"
-- ============================================

-- Activer la 2FA pour tous les utilisateurs
UPDATE users
SET two_fa_enabled = true
WHERE two_fa_enabled IS NULL OR two_fa_enabled = false;

-- Vérifier le résultat
SELECT 
    email,
    role,
    two_fa_enabled,
    CASE 
        WHEN two_fa_enabled THEN '✅ ACTIVÉE'
        ELSE '❌ DÉSACTIVÉE'
    END as statut_2fa
FROM users
ORDER BY role, email;

-- Afficher un message de confirmation
DO $$
DECLARE
    user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users WHERE two_fa_enabled = true;
    RAISE NOTICE '✅ 2FA activée pour % utilisateur(s)', user_count;
END $$;

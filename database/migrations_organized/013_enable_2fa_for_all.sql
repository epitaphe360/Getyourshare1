-- ============================================
-- ACTIVATION 2FA POUR TOUS LES UTILISATEURS
-- Date: 2025-10-23
-- ============================================

-- Vérifier l'état actuel
SELECT 
    email,
    role,
    two_fa_enabled,
    CASE 
        WHEN two_fa_enabled THEN '✅ Activée'
        ELSE '❌ Désactivée'
    END as statut_2fa
FROM users
ORDER BY role, email;

-- Activer la 2FA pour tous les utilisateurs
UPDATE users
SET two_fa_enabled = true
WHERE two_fa_enabled = false OR two_fa_enabled IS NULL;

-- Vérifier le résultat
SELECT 
    role,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE two_fa_enabled = true) as avec_2fa,
    COUNT(*) FILTER (WHERE two_fa_enabled = false OR two_fa_enabled IS NULL) as sans_2fa
FROM users
GROUP BY role;

-- Afficher tous les utilisateurs avec leur statut 2FA
SELECT 
    email,
    role,
    two_fa_enabled,
    created_at
FROM users
ORDER BY created_at DESC;

COMMENT ON TABLE users IS 'Table des utilisateurs - 2FA activée pour tous les comptes';

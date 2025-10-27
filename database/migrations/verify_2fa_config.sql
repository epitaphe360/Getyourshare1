-- ============================================
-- VERIFICATION ET CONFIGURATION 2FA
-- Date: 2025-10-23
-- Description: Vérifier et configurer la colonne two_fa_enabled
-- ============================================

-- Vérifier l'état actuel des utilisateurs
SELECT 
    id,
    email,
    role,
    two_fa_enabled,
    is_active
FROM users
ORDER BY role, email;

-- Activer 2FA pour tous les influenceurs (optionnel)
-- UPDATE users 
-- SET two_fa_enabled = TRUE 
-- WHERE role = 'influencer';

-- Désactiver 2FA pour les comptes de test (optionnel pour faciliter les tests)
-- UPDATE users 
-- SET two_fa_enabled = FALSE 
-- WHERE email IN (
--     'admin@shareyoursales.com',
--     'contact@techstyle.fr',
--     'emma.style@instagram.com'
-- );

-- Activer 2FA uniquement pour les influenceurs (recommandé en production)
-- UPDATE users 
-- SET two_fa_enabled = CASE 
--     WHEN role = 'influencer' THEN TRUE
--     ELSE FALSE
-- END;

-- Vérification finale
SELECT 
    role,
    COUNT(*) as total_users,
    SUM(CASE WHEN two_fa_enabled THEN 1 ELSE 0 END) as with_2fa_enabled,
    SUM(CASE WHEN NOT two_fa_enabled THEN 1 ELSE 0 END) as without_2fa
FROM users
GROUP BY role
ORDER BY role;

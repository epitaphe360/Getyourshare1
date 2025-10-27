-- ============================================
-- VÉRIFICATION 2FA POUR LES MARCHANDS
-- Date: 2025-10-23
-- ============================================

-- Vérifier l'état 2FA de tous les utilisateurs par rôle
SELECT 
    role,
    email,
    two_fa_enabled,
    is_active,
    created_at
FROM users
WHERE role IN ('merchant', 'influencer', 'admin')
ORDER BY role, email;

-- Statistiques par rôle
SELECT 
    role,
    COUNT(*) as total_users,
    SUM(CASE WHEN two_fa_enabled THEN 1 ELSE 0 END) as with_2fa,
    SUM(CASE WHEN NOT two_fa_enabled THEN 1 ELSE 0 END) as without_2fa
FROM users
GROUP BY role
ORDER BY role;

-- OPTION 1: Désactiver 2FA pour tous les comptes de test (facilite les tests)
-- Décommentez les lignes ci-dessous pour exécuter
/*
UPDATE users 
SET two_fa_enabled = FALSE 
WHERE email IN (
    'admin@shareyoursales.com',
    'contact@techstyle.fr',
    'hello@beautypro.com',
    'emma.style@instagram.com',
    'lucas.tech@youtube.com',
    'julie.beauty@tiktok.com'
);
*/

-- OPTION 2: Activer 2FA uniquement pour les influenceurs (sécurité renforcée)
-- Décommentez les lignes ci-dessous pour exécuter
/*
UPDATE users 
SET two_fa_enabled = CASE 
    WHEN role = 'influencer' THEN TRUE
    ELSE FALSE
END;
*/

-- OPTION 3: Activer 2FA pour tous les rôles (sécurité maximale)
-- Décommentez les lignes ci-dessous pour exécuter
/*
UPDATE users 
SET two_fa_enabled = TRUE;
*/

-- Vérification finale après modification
SELECT 
    role,
    email,
    two_fa_enabled,
    CASE 
        WHEN two_fa_enabled THEN 'Code 2FA requis (123456)'
        ELSE 'Connexion directe'
    END as connexion_type
FROM users
WHERE role IN ('merchant', 'influencer', 'admin')
ORDER BY role, email;

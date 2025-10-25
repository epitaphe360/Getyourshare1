# Fonctions Mockées - À Implémenter

## 📋 LISTE COMPLÈTE DES FONCTIONS MOCKÉES

### 1. SETTINGS / PARAMÈTRES (8 fonctions)

| Fichier | Fonction | Endpoint API | Status |
|---------|----------|--------------|--------|
| **CompanySettings.js** | handleSubmit | POST /api/settings/company | ❌ Mocké |
| **PersonalSettings.js** | handleSubmit | PUT /api/users/{id} | ❌ Mocké |
| **AffiliateSettings.js** | handleSubmit | POST /api/settings/affiliate | ❌ Mocké |
| **RegistrationSettings.js** | handleSubmit | POST /api/settings/registration | ❌ Mocké |
| **MLMSettings.js** | handleSubmit | POST /api/settings/mlm | ❌ Mocké |
| **WhiteLabel.js** | handleSubmit | POST /api/settings/whitelabel | ❌ Mocké |
| **SMTP.js** | handleSubmit + handleTest | POST /api/settings/smtp, POST /api/settings/smtp/test | ❌ Mocké |
| **Permissions.js** | handleSubmit | POST /api/settings/permissions | ❌ Mocké |

---

## 🔧 IMPLÉMENTATION REQUISE

### Stratégie Supabase

Pour implémenter ces fonctions, nous allons utiliser:
1. **Table `settings`** - Déjà existante dans le schéma
2. **Table `users`** - Pour PersonalSettings
3. **Table `merchants`** - Pour CompanySettings (lié au user merchant)
4. **Table `influencers`** - Pour les settings influenceurs

### Structure de la table `settings`

```sql
CREATE TABLE IF NOT EXISTS settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Fonctions à implémenter

#### 1. CompanySettings.js

```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const response = await api.put('/api/settings/company', settings);
    toast.success('Paramètres sauvegardés avec succès');
  } catch (error) {
    console.error('Error saving settings:', error);
    toast.error('Erreur lors de la sauvegarde');
  }
};
```

#### 2. PersonalSettings.js

```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const response = await api.put(`/api/users/${user.id}`, formData);
    toast.success('Profil mis à jour avec succès');
    // Mettre à jour le contexte AuthContext
  } catch (error) {
    console.error('Error updating profile:', error);
    toast.error('Erreur lors de la mise à jour');
  }
};
```

#### 3. SMTP.js

```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    await api.post('/api/settings/smtp', smtpConfig);
    toast.success('Configuration SMTP sauvegardée');
  } catch (error) {
    toast.error('Erreur lors de la sauvegarde');
  }
};

const handleTest = async () => {
  try {
    setTesting(true);
    const response = await api.post('/api/settings/smtp/test');
    if (response.data.success) {
      toast.success('Email de test envoyé avec succès');
    } else {
      toast.error('Échec du test SMTP');
    }
  } catch (error) {
    toast.error('Erreur lors du test SMTP');
  } finally {
    setTesting(false);
  }
};
```

---

## 📦 DONNÉES DE TEST À AJOUTER

### Settings de base

```sql
-- Company settings
INSERT INTO settings (key, value, description) VALUES
('company_name', 'ShareYourSales', 'Nom de l''entreprise'),
('company_email', 'contact@shareyoursales.com', 'Email de contact'),
('company_address', '123 Rue de la Tech, 75001 Paris, France', 'Adresse de l''entreprise'),
('company_tax_id', 'FR12345678901', 'Numéro de TVA'),
('company_currency', 'EUR', 'Devise par défaut')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Affiliate settings
INSERT INTO settings (key, value, description) VALUES
('affiliate_min_payout', '50', 'Montant minimum pour retrait (€)'),
('affiliate_default_commission', '10', 'Commission par défaut (%)'),
('affiliate_cookie_duration', '30', 'Durée du cookie (jours)'),
('affiliate_approval_required', 'true', 'Approbation manuelle des affiliés')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Registration settings
INSERT INTO settings (key, value, description) VALUES
('registration_enabled', 'true', 'Inscription ouverte'),
('registration_auto_approve', 'false', 'Approbation automatique'),
('registration_require_2fa', 'true', 'Requiert 2FA'),
('registration_allowed_roles', '["influencer","merchant"]', 'Rôles autorisés')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- MLM settings
INSERT INTO settings (key, value, description) VALUES
('mlm_enabled', 'false', 'MLM activé'),
('mlm_max_levels', '3', 'Nombre de niveaux MLM'),
('mlm_level_1_commission', '5', 'Commission niveau 1 (%)'),
('mlm_level_2_commission', '3', 'Commission niveau 2 (%)'),
('mlm_level_3_commission', '2', 'Commission niveau 3 (%)')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- SMTP settings
INSERT INTO settings (key, value, description) VALUES
('smtp_host', 'smtp.gmail.com', 'Serveur SMTP'),
('smtp_port', '587', 'Port SMTP'),
('smtp_encryption', 'tls', 'Encryption SMTP'),
('smtp_from_email', 'noreply@shareyoursales.com', 'Email expéditeur'),
('smtp_from_name', 'ShareYourSales', 'Nom expéditeur')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- White label settings
INSERT INTO settings (key, value, description) VALUES
('whitelabel_company_name', 'ShareYourSales', 'Nom de marque'),
('whitelabel_primary_color', '#6366f1', 'Couleur primaire'),
('whitelabel_secondary_color', '#8b5cf6', 'Couleur secondaire'),
('whitelabel_accent_color', '#10b981', 'Couleur accent'),
('whitelabel_logo_url', '', 'URL du logo'),
('whitelabel_custom_domain', '', 'Domaine personnalisé')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
```

---

## 🎯 PRIORISATION

### Priorité 1 - CRITIQUE
1. ✅ **PersonalSettings** - Les users doivent pouvoir modifier leur profil
2. ✅ **CompanySettings** - Les merchants doivent configurer leur entreprise

### Priorité 2 - IMPORTANT
3. ✅ **AffiliateSettings** - Configuration des commissions
4. ✅ **RegistrationSettings** - Contrôle des inscriptions
5. ✅ **SMTP** - Envoi d'emails

### Priorité 3 - OPTIONNEL
6. ⬜ **MLMSettings** - Système multiniveau (optionnel)
7. ⬜ **WhiteLabel** - Personnalisation (optionnel)
8. ⬜ **Permissions** - Gestion fine des droits

---

## 📝 CHECKLIST IMPLÉMENTATION

Pour chaque fonction:
- [ ] Ajouter import `useToast`
- [ ] Implémenter `try/catch` avec toast notifications
- [ ] Ajouter state `loading` ou `saving`
- [ ] Désactiver bouton pendant sauvegarde
- [ ] Gérer les erreurs API
- [ ] Tester avec données de test
- [ ] Vérifier en base de données Supabase

---

**Date**: 2025-10-23
**Status**: En cours d'implémentation

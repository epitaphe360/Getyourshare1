# 🌐 Guide: Vérifier le Domaine `shareyoursales.ma` sur Resend

## 🎯 Objectif
Configurer votre domaine personnalisé pour envoyer des emails depuis `info@shareyoursales.ma` au lieu de `onboarding@resend.dev`.

---

## 📋 Prérequis

- ✅ Compte Resend créé (API Key: `re_K3foTU6E_GmhCZ6ZvLcHnnGZGcrNoUySB`)
- ✅ Domaine `shareyoursales.ma` enregistré
- ✅ Accès au panneau DNS de votre registrar (OVH, Gandi, Namecheap, etc.)

---

## 📝 Étapes Détaillées

### Étape 1: Accéder à Resend Dashboard

1. Allez sur: **https://resend.com/login**
2. Connectez-vous avec vos identifiants
3. Une fois connecté, allez sur: **https://resend.com/domains**

### Étape 2: Ajouter le Domaine

1. Cliquez sur le bouton **"Add Domain"** (en haut à droite)
2. Entrez votre domaine: `shareyoursales.ma`
3. Choisissez la région: **Europe (EU)** (recommandé pour Maroc)
4. Cliquez sur **"Add"**

### Étape 3: Récupérer les Enregistrements DNS

Resend va vous afficher **4 enregistrements DNS** à créer:

#### 📌 Enregistrement 1: Vérification du Domaine (TXT)
```
Type: TXT
Name: _resend
Value: resend-domain-verification=xxxxx-yyyy-zzzz-aaaa-bbbb
TTL: 3600 (ou 1 heure)
```

#### 📌 Enregistrement 2: SPF (TXT)
```
Type: TXT
Name: @ (ou laissez vide)
Value: v=spf1 include:_spf.resend.com ~all
TTL: 3600
```

#### 📌 Enregistrement 3: DKIM (CNAME)
```
Type: CNAME
Name: resend._domainkey
Value: resend._domainkey.resend.com
TTL: 3600
```

#### 📌 Enregistrement 4: MX (Optionnel - pour recevoir bounces)
```
Type: MX
Name: @ (ou laissez vide)
Priority: 10
Value: feedback-smtp.eu.resend.com
TTL: 3600
```

**⚠️ Note:** Les valeurs exactes seront affichées dans votre dashboard Resend. Copiez-les exactement!

---

### Étape 4: Configurer DNS chez votre Registrar

#### Si vous êtes chez **OVH**:

1. Allez sur: https://www.ovh.com/manager/
2. Cliquez sur votre domaine `shareyoursales.ma`
3. Allez dans l'onglet **"Zone DNS"**
4. Cliquez sur **"Ajouter une entrée"**

**Pour chaque enregistrement:**
- Sélectionnez le type (TXT, CNAME, ou MX)
- Remplissez les champs avec les valeurs Resend
- Cliquez sur **"Suivant"** puis **"Valider"**

#### Si vous êtes chez **Gandi**:

1. Allez sur: https://admin.gandi.net/
2. Sélectionnez votre domaine
3. Allez dans **"Enregistrements DNS"**
4. Cliquez sur **"Ajouter"** pour chaque enregistrement

#### Si vous êtes chez **Namecheap**:

1. Dashboard → Domain List
2. Cliquez sur **"Manage"** à côté de `shareyoursales.ma`
3. Allez dans **"Advanced DNS"**
4. Cliquez sur **"Add New Record"** pour chaque enregistrement

---

### Étape 5: Attendre la Propagation DNS

⏱️ **Temps d'attente:** 5 à 30 minutes (parfois jusqu'à 24h)

**Vérifier la propagation:**
1. Allez sur: https://dnschecker.org/
2. Entrez: `_resend.shareyoursales.ma`
3. Sélectionnez: **TXT Record**
4. Cliquez sur **"Search"**

Si vous voyez votre code de vérification Resend → DNS propagé ✅

---

### Étape 6: Vérifier le Domaine dans Resend

1. Retournez sur: https://resend.com/domains
2. À côté de `shareyoursales.ma`, cliquez sur **"Verify"**
3. Si tout est OK, vous verrez: **"Verified" ✅**

**En cas d'erreur:**
- Attendez encore 10-15 minutes
- Vérifiez que vous avez copié les valeurs exactement
- Vérifiez qu'il n'y a pas d'espaces avant/après les valeurs

---

### Étape 7: Mettre à Jour la Configuration

Une fois le domaine vérifié ✅:

#### Modifier `.env`:
```bash
cd backend
```

Ouvrez `.env` et changez:
```env
# AVANT
EMAIL_FROM_ADDRESS=onboarding@resend.dev

# APRÈS
EMAIL_FROM_ADDRESS=info@shareyoursales.ma
```

#### Redémarrer le Backend:
```bash
# Arrêter le serveur actuel (Ctrl+C)

# Relancer
python server_complete.py
```

---

### Étape 8: Tester l'Envoi

#### Test rapide:
```bash
cd backend
python test_resend_email.py
```

**Résultat attendu:**
```
✅ Email envoyé avec succès!
   FROM: ShareYourSales <info@shareyoursales.ma>
   TO: epitaphemarket@gmail.com
```

#### Test depuis le code:
```python
from services.resend_email_service import resend_service

result = resend_service.send_email(
    to_email="epitaphemarket@gmail.com",
    subject="Test Domaine Vérifié ✅",
    html_content="<h1>Bravo! Le domaine shareyoursales.ma fonctionne!</h1>"
)

print(result)
```

---

## ✅ Vérification Complète

### Checklist Finale:

- [ ] Domaine ajouté dans Resend
- [ ] 4 enregistrements DNS créés:
  - [ ] TXT (_resend)
  - [ ] TXT (SPF)
  - [ ] CNAME (DKIM)
  - [ ] MX (optionnel)
- [ ] DNS propagés (vérifié sur dnschecker.org)
- [ ] Domaine vérifié dans Resend (badge vert ✅)
- [ ] `.env` mis à jour (`info@shareyoursales.ma`)
- [ ] Backend redémarré
- [ ] Email de test envoyé et reçu ✅
- [ ] Email arrive en boîte principale (pas spam)

---

## 🔧 Troubleshooting

### ❌ "Domain not verified" après 1 heure

**Solutions:**
1. Vérifiez que les enregistrements DNS sont exacts
2. Supprimez les anciens enregistrements SPF/DKIM si présents
3. Contactez support registrar (OVH, Gandi, etc.)
4. Contactez Resend support: support@resend.com

### ❌ Emails arrivent en spam

**Solutions:**
1. Vérifiez que DKIM est configuré (CNAME resend._domainkey)
2. Vérifiez SPF (TXT avec include:_spf.resend.com)
3. Ajoutez un enregistrement DMARC:
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:postmaster@shareyoursales.ma
```
4. Réchauffez le domaine (envoyez progressivement, pas 1000 emails d'un coup)
5. Utilisez contenu professionnel (évitez mots "gratuit", "urgent", etc.)

### ❌ "DNS propagation taking too long"

**Solutions:**
1. Attendez 24h (rare mais possible)
2. Vérifiez avec `nslookup`:
```bash
nslookup -type=TXT _resend.shareyoursales.ma
```
3. Flush votre DNS local:
```bash
# Windows
ipconfig /flushdns

# Mac/Linux
sudo dscacheutil -flushcache
```

### ❌ "Invalid DKIM record"

**Solutions:**
1. Vérifiez qu'il n'y a pas d'espaces dans la valeur CNAME
2. Le Name doit être exactement: `resend._domainkey`
3. La Value doit être exactement: `resend._domainkey.resend.com`
4. Pas de point final `.` à la fin

---

## 📊 Enregistrements DNS Recommandés (Complets)

Une fois le domaine vérifié, voici la configuration DNS complète recommandée:

```dns
# Vérification Resend
Type: TXT
Name: _resend
Value: resend-domain-verification=xxxxx-yyyy-zzzz
TTL: 3600

# SPF (anti-spam)
Type: TXT
Name: @
Value: v=spf1 include:_spf.resend.com ~all
TTL: 3600

# DKIM (signature emails)
Type: CNAME
Name: resend._domainkey
Value: resend._domainkey.resend.com
TTL: 3600

# DMARC (politique email)
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=quarantine; rua=mailto:postmaster@shareyoursales.ma; pct=100
TTL: 3600

# MX (recevoir bounces)
Type: MX
Name: @
Priority: 10
Value: feedback-smtp.eu.resend.com
TTL: 3600
```

---

## 🎯 Avantages du Domaine Vérifié

Une fois `info@shareyoursales.ma` configuré:

✅ **Professionnalisme**
- Emails depuis votre marque (pas `@resend.dev`)
- Confiance clients augmentée
- Image professionnelle

✅ **Délivrabilité**
- Moins de risque spam
- Meilleur taux d'ouverture
- DKIM/SPF configurés correctement

✅ **Traçabilité**
- Tous emails depuis même domaine
- Analytics consolidées
- Réputation domaine propre

✅ **Scalabilité**
- Domaine vérifié = limites plus élevées
- Possibilité d'ajouter sous-domaines
- Support premium Resend

---

## 📞 Support

### Besoin d'Aide?

**Resend:**
- Documentation: https://resend.com/docs/dashboard/domains/introduction
- Support: support@resend.com
- Status: https://status.resend.com/

**DNS:**
- OVH Support: https://www.ovh.com/fr/support/
- Gandi Support: https://www.gandi.net/fr/contact
- DNS Checker: https://dnschecker.org/

**ShareYourSales:**
- Email: support@shareyoursales.ma
- Documentation: Ce guide

---

## 🎉 Une Fois Terminé

Votre configuration sera:

```
📧 Emails envoyés depuis: info@shareyoursales.ma
🔐 Sécurisé avec: SPF + DKIM + DMARC
✅ Domaine vérifié: shareyoursales.ma
🚀 Prêt pour production!
```

**Date de création:** 2 Novembre 2025
**Version:** 1.0

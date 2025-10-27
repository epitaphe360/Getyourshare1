# ShareYourSales - Configuration Railway

## Variables d'environnement requises

Configurez ces variables dans Railway Dashboard :

### Base de données Supabase
```
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre-clé-anon-publique-supabase
```

### JWT Sécurité
```
JWT_SECRET=votre-secret-jwt-genere-aleatoirement
JWT_ALGORITHM=HS256
```

### Configuration Serveur
```
PORT=8001
HOST=0.0.0.0
ENVIRONMENT=production
```

### SMTP Email (CMI Payment Gateway Emails)
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-application
SMTP_FROM=noreply@shareyoursales.ma
```

### Passerelles de paiement

#### CMI Payment Gateway (Maroc)
```
CMI_MERCHANT_ID=votre-merchant-id
CMI_API_KEY=votre-cmi-api-key
CMI_PAYMENT_URL=https://payment.cmi.ma/fim/api
CMI_OK_URL=https://votre-domaine.com/payment/success
CMI_FAIL_URL=https://votre-domaine.com/payment/failure
```

#### PayZen (Lyra Network)
```
PAYZEN_SHOP_ID=votre-shop-id
PAYZEN_API_KEY=votre-payzen-api-key
PAYZEN_HMAC_KEY=votre-hmac-key
PAYZEN_URL=https://secure.payzen.eu/vads-payment/
```

#### Société Générale Maroc
```
SGMA_MERCHANT_ID=votre-merchant-id
SGMA_SECRET_KEY=votre-secret-key
SGMA_PAYMENT_URL=https://payment.societegenerale.ma/api/v1
```

#### Stripe (International - Optionnel)
```
STRIPE_PUBLIC_KEY=pk_live_votre-cle-publique
STRIPE_SECRET_KEY=sk_live_votre-cle-secrete
STRIPE_WEBHOOK_SECRET=whsec_votre-webhook-secret
```

#### PayPal (International - Optionnel)
```
PAYPAL_CLIENT_ID=votre-client-id
PAYPAL_SECRET=votre-secret
PAYPAL_MODE=live
```

### Configuration Application
```
APP_NAME=ShareYourSales
APP_URL=https://votre-domaine-railway.up.railway.app
FRONTEND_URL=https://votre-domaine-railway.up.railway.app
CORS_ORIGINS=https://votre-domaine-railway.up.railway.app,https://votre-domaine-custom.com
```

### Sécurité additionnelle
```
BCRYPT_ROUNDS=12
SESSION_LIFETIME_HOURS=24
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Fonctionnalités
```
ENABLE_EMAIL_VERIFICATION=true
ENABLE_TWO_FACTOR_AUTH=false
ENABLE_AUTO_PAYOUTS=true
ENABLE_MLM_COMMISSIONS=true
AUTO_PAYOUT_THRESHOLD=500
```

## Commandes de déploiement

Railway détectera automatiquement :
- **Build** : `npm install` (frontend) + `pip install -r requirements.txt` (backend)
- **Start** : `python backend/server.py`

## Healthcheck

Railway vérifiera automatiquement `/` toutes les 30 secondes.

## Notes importantes

1. **SUPABASE_URL et SUPABASE_KEY** sont OBLIGATOIRES
2. **JWT_SECRET** doit être une chaîne aléatoire de minimum 32 caractères
3. Les passerelles de paiement sont optionnelles mais recommandées pour production
4. Configurez au moins CMI ou PayZen pour les paiements marocains
5. SMTP est requis pour les emails transactionnels
6. Vérifiez que `CORS_ORIGINS` inclut votre domaine final

## Génération JWT_SECRET

Utilisez cette commande Python :
```python
import secrets
print(secrets.token_urlsafe(32))
```

Ou cette commande Bash :
```bash
openssl rand -base64 32
```

## Support

Pour tout problème de déploiement, vérifiez :
1. Les logs Railway
2. Que toutes les variables d'environnement sont définies
3. Que Supabase est accessible depuis Railway
4. Que le port 8001 est bien configuré

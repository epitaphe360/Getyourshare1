# 🇲🇦 SYSTÈME DE PAIEMENT MULTI-GATEWAY - MAROC

## 📋 APERÇU

Système permettant aux merchants marocains de choisir parmi 3 solutions de paiement:
- **CMI** (Centre Monétique Interbancaire)
- **PayZen / Lyra**
- **Société Générale Maroc - e-Payment**

---

## 🏗️ ARCHITECTURE

### Flux de Paiement Unifié

```
Merchant s'inscrit
    ↓
Choisit sa gateway préférée: CMI / PayZen / SG
    ↓
Configure ses identifiants API
    ↓
Ventes arrivent (Shopify/WooCommerce/TikTok)
    ↓
Webhook → Calcul commission
    ↓
Prélèvement via gateway choisie
    ↓
Redistribution automatique
```

---

## 💳 OPTION 1: CMI (Centre Monétique Interbancaire)

### Informations Clés

**Site web:** https://www.cmi.co.ma  
**Documentation API:** https://developer.cmi.co.ma

**Frais:** 1.5% - 2% par transaction  
**Délai:** 2-3 jours ouvrés  
**Devises:** MAD (Dirhams marocains)

### Banques Partenaires

- Attijariwafa Bank
- BMCE Bank of Africa
- Banque Populaire
- Crédit du Maroc
- Société Générale Maroc
- CIH Bank
- Al Barid Bank

### Configuration Merchant

```json
{
  "gateway": "cmi",
  "cmi_merchant_id": "123456789",
  "cmi_api_key": "sk_live_xxxxxxxxxxxxx",
  "cmi_store_key": "xxxxxxxxxxxxx",
  "cmi_terminal_id": "T001",
  "currency": "MAD"
}
```

### API Endpoints CMI

**Base URL:** `https://payment.cmi.co.ma/api/v1`

**Créer un paiement:**
```http
POST /payments/create
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "amount": 15000,  // En centimes (150.00 MAD)
  "currency": "MAD",
  "merchant_id": "123456789",
  "order_id": "ORDER-2025-001",
  "description": "Commission plateforme ShareYourSales",
  "customer": {
    "email": "merchant@example.ma",
    "name": "Boutique Mode"
  },
  "callback_url": "https://yourdomain.com/api/webhook/cmi/callback"
}
```

**Response:**
```json
{
  "payment_id": "PMT_123456789",
  "status": "pending",
  "payment_url": "https://payment.cmi.co.ma/pay/PMT_123456789",
  "expires_at": "2025-10-24T10:00:00Z"
}
```

### Webhook CMI

**URL à configurer:** `https://yourdomain.com/api/webhook/cmi/{merchant_id}`

**Payload reçu:**
```json
{
  "event": "payment.succeeded",
  "payment_id": "PMT_123456789",
  "amount": 15000,
  "currency": "MAD",
  "status": "completed",
  "merchant_id": "123456789",
  "order_id": "ORDER-2025-001",
  "paid_at": "2025-10-23T15:30:00Z",
  "signature": "sha256_signature_here"
}
```

---

## 💳 OPTION 2: PayZen / Lyra

### Informations Clés

**Site web:** https://payzen.eu  
**Documentation:** https://docs.lyra.com

**Frais:** 1.8% - 2.5% par transaction  
**Délai:** 24-48 heures  
**Devises:** MAD, EUR, USD

### Avantages

✅ Utilisé par Marjane, Jumia, Avito  
✅ Interface en français/arabe  
✅ Support des cartes CMI + internationales  
✅ Split payment natif  
✅ Dashboard complet

### Configuration Merchant

```json
{
  "gateway": "payzen",
  "payzen_shop_id": "12345678",
  "payzen_api_key": "production_xxxxxxxxxxxxx",
  "payzen_secret_key": "xxxxxxxxxxxxx",
  "payzen_mode": "PRODUCTION",
  "currency": "MAD"
}
```

### API Endpoints PayZen

**Base URL:** `https://api.payzen.eu/api-payment/V4`

**Créer un paiement avec split:**
```http
POST /Charge/CreatePayment
Content-Type: application/json
Authorization: Basic {base64(shop_id:api_key)}

{
  "amount": 15000,  // En centimes
  "currency": "MAD",
  "orderId": "ORDER-2025-001",
  "customer": {
    "email": "merchant@example.ma",
    "reference": "MERCHANT-123"
  },
  "transactionOptions": {
    "cardOptions": {
      "paymentSource": "EC"
    }
  },
  "customData": {
    "platformCommission": 5000,
    "influencerCommission": 10000
  },
  "marketplace": {
    "sellerAccountId": "SELLER-123",
    "splits": [
      {
        "amount": 5000,
        "label": "Commission Plateforme",
        "accountId": "YOUR_PLATFORM_ACCOUNT"
      },
      {
        "amount": 10000,
        "label": "Commission Influenceur",
        "accountId": "INFLUENCER_ACCOUNT"
      }
    ]
  }
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "answer": {
    "formToken": "xxxxxxxxxxxxxx",
    "orderId": "ORDER-2025-001",
    "serverDate": "2025-10-23T15:00:00Z"
  }
}
```

### Webhook PayZen

**URL à configurer:** `https://yourdomain.com/api/webhook/payzen/{merchant_id}`

**Payload reçu (IPN):**
```json
{
  "kr-answer": {
    "orderStatus": "PAID",
    "orderDetails": {
      "orderId": "ORDER-2025-001",
      "orderTotalAmount": 15000,
      "orderCurrency": "MAD"
    },
    "customer": {
      "email": "merchant@example.ma"
    },
    "transactions": [
      {
        "uuid": "xxxxxxxxxxxxx",
        "amount": 15000,
        "currency": "MAD",
        "status": "CAPTURED"
      }
    ]
  },
  "kr-hash": "sha256_signature"
}
```

---

## 💳 OPTION 3: Société Générale Maroc - e-Payment

### Informations Clés

**Site web:** https://www.societegenerale.ma  
**Contact:** Département e-Banking

**Frais:** Négociables (1.5% - 2.5%)  
**Délai:** 2-3 jours  
**Devises:** MAD

### Avantages

✅ Banque établie au Maroc  
✅ Support local dédié  
✅ Frais négociables pour gros volumes  
✅ Intégration bancaire directe

### Configuration Merchant

```json
{
  "gateway": "sg_maroc",
  "sg_merchant_code": "SG123456",
  "sg_terminal_id": "TERM001",
  "sg_api_username": "api_user_xxx",
  "sg_api_password": "xxxxxxxxxxxxx",
  "sg_certificate": "-----BEGIN CERTIFICATE-----...",
  "currency": "MAD"
}
```

### API Endpoints SG Maroc

**Base URL:** `https://epayment.sg.ma/api/v2`

**Créer une transaction:**
```http
POST /payment/init
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "merchantCode": "SG123456",
  "terminalId": "TERM001",
  "amount": "150.00",
  "currency": "MAD",
  "orderId": "ORDER-2025-001",
  "description": "Commission ShareYourSales",
  "returnUrl": "https://yourdomain.com/payment/return",
  "cancelUrl": "https://yourdomain.com/payment/cancel",
  "ipnUrl": "https://yourdomain.com/api/webhook/sg/{merchant_id}",
  "customer": {
    "email": "merchant@example.ma",
    "phone": "+212600000000"
  }
}
```

**Response:**
```json
{
  "success": true,
  "transactionId": "TRX123456789",
  "paymentUrl": "https://epayment.sg.ma/pay?token=xxxxx",
  "expiresAt": "2025-10-24T10:00:00Z"
}
```

### Webhook SG Maroc

**URL à configurer:** `https://yourdomain.com/api/webhook/sg/{merchant_id}`

**Payload reçu:**
```json
{
  "transactionId": "TRX123456789",
  "orderId": "ORDER-2025-001",
  "amount": "150.00",
  "currency": "MAD",
  "status": "SUCCESS",
  "paymentDate": "2025-10-23T15:30:00Z",
  "merchantCode": "SG123456",
  "signature": "base64_hmac_sha256"
}
```

---

## 🔧 IMPLÉMENTATION TECHNIQUE

### Structure Base de Données

```sql
-- Ajouter colonnes gateway à la table merchants
ALTER TABLE merchants
ADD COLUMN IF NOT EXISTS payment_gateway VARCHAR(50) DEFAULT 'manual',  -- 'cmi', 'payzen', 'sg_maroc', 'manual'
ADD COLUMN IF NOT EXISTS gateway_config JSONB DEFAULT '{}',  -- Configuration spécifique gateway
ADD COLUMN IF NOT EXISTS auto_debit_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS gateway_activated_at TIMESTAMP;

-- Table pour transactions gateway
CREATE TABLE gateway_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES platform_invoices(id) ON DELETE SET NULL,
    
    -- Gateway
    gateway VARCHAR(50) NOT NULL,  -- 'cmi', 'payzen', 'sg_maroc'
    transaction_id VARCHAR(255),  -- ID externe du gateway
    
    -- Montants
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'MAD',
    fees DECIMAL(10, 2) DEFAULT 0,
    net_amount DECIMAL(10, 2),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed, refunded
    failure_reason TEXT,
    
    -- Données
    request_payload JSONB,
    response_payload JSONB,
    
    -- Timestamps
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gateway_transactions_merchant ON gateway_transactions(merchant_id);
CREATE INDEX idx_gateway_transactions_status ON gateway_transactions(status);
CREATE INDEX idx_gateway_transactions_gateway ON gateway_transactions(gateway);
```

### Service Python Multi-Gateway

Créons le fichier `backend/payment_gateways.py`:

```python
"""
Service de gestion des gateways de paiement marocains
Supporte: CMI, PayZen/Lyra, Société Générale Maroc
"""

from typing import Dict, Optional
import requests
import hmac
import hashlib
import base64
import json
from datetime import datetime
from supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

class PaymentGatewayService:
    """Service unifié pour tous les gateways"""
    
    def __init__(self):
        self.gateways = {
            'cmi': CMIGateway(),
            'payzen': PayZenGateway(),
            'sg_maroc': SGMarocGateway()
        }
    
    def create_payment(
        self,
        merchant_id: str,
        amount: float,
        description: str,
        invoice_id: Optional[str] = None
    ) -> Dict:
        """
        Crée un paiement via le gateway configuré du merchant
        
        Args:
            merchant_id: ID du merchant
            amount: Montant en MAD
            description: Description du paiement
            invoice_id: ID de la facture (optionnel)
        
        Returns:
            Dict avec payment_id, payment_url, status
        """
        
        # Récupérer config gateway du merchant
        merchant = supabase.table('merchants')\
            .select('payment_gateway, gateway_config')\
            .eq('id', merchant_id)\
            .single()\
            .execute()
        
        if not merchant.data:
            raise Exception(f"Merchant {merchant_id} not found")
        
        gateway_type = merchant.data['payment_gateway']
        gateway_config = merchant.data['gateway_config']
        
        if gateway_type == 'manual':
            # Facturation manuelle
            return {
                'payment_method': 'manual',
                'status': 'pending_manual_payment',
                'message': 'Paiement manuel requis - facture envoyée'
            }
        
        # Utiliser le gateway approprié
        gateway = self.gateways.get(gateway_type)
        if not gateway:
            raise Exception(f"Gateway {gateway_type} not supported")
        
        # Créer paiement
        result = gateway.create_payment(
            config=gateway_config,
            amount=amount,
            description=description,
            merchant_id=merchant_id
        )
        
        # Enregistrer transaction
        transaction = {
            'merchant_id': merchant_id,
            'invoice_id': invoice_id,
            'gateway': gateway_type,
            'transaction_id': result.get('transaction_id'),
            'amount': amount,
            'currency': 'MAD',
            'status': 'pending',
            'request_payload': result.get('request'),
            'response_payload': result.get('response')
        }
        
        supabase.table('gateway_transactions').insert(transaction).execute()
        
        return result


class CMIGateway:
    """Gateway CMI (Centre Monétique Interbancaire)"""
    
    BASE_URL = "https://payment.cmi.co.ma/api/v1"
    
    def create_payment(self, config: Dict, amount: float, description: str, merchant_id: str) -> Dict:
        """Crée un paiement via CMI"""
        
        payload = {
            "amount": int(amount * 100),  # Convertir en centimes
            "currency": "MAD",
            "merchant_id": config['cmi_merchant_id'],
            "order_id": f"ORDER-{datetime.now().strftime('%Y%m%d')}-{merchant_id[:8]}",
            "description": description,
            "callback_url": f"https://yourdomain.com/api/webhook/cmi/{merchant_id}"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['cmi_api_key']}"
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/payments/create",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'transaction_id': data['payment_id'],
                'payment_url': data['payment_url'],
                'status': 'pending',
                'gateway': 'cmi',
                'request': payload,
                'response': data
            }
            
        except Exception as e:
            logger.error(f"CMI payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'cmi'
            }
    
    def verify_webhook(self, payload: Dict, signature: str, secret: str) -> bool:
        """Vérifie la signature webhook CMI"""
        
        # CMI utilise HMAC-SHA256
        message = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        expected_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)


class PayZenGateway:
    """Gateway PayZen / Lyra"""
    
    BASE_URL = "https://api.payzen.eu/api-payment/V4"
    
    def create_payment(self, config: Dict, amount: float, description: str, merchant_id: str) -> Dict:
        """Crée un paiement via PayZen"""
        
        payload = {
            "amount": int(amount * 100),
            "currency": "MAD",
            "orderId": f"ORDER-{datetime.now().strftime('%Y%m%d')}-{merchant_id[:8]}",
            "customer": {
                "reference": merchant_id
            },
            "transactionOptions": {
                "cardOptions": {
                    "paymentSource": "EC"
                }
            }
        }
        
        # Basic Auth: shop_id:api_key en base64
        auth_string = f"{config['payzen_shop_id']}:{config['payzen_api_key']}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_header}"
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/Charge/CreatePayment",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'SUCCESS':
                return {
                    'success': True,
                    'transaction_id': data['answer']['orderId'],
                    'form_token': data['answer']['formToken'],
                    'status': 'pending',
                    'gateway': 'payzen',
                    'request': payload,
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': data.get('answer', {}).get('errorMessage', 'Unknown error'),
                    'gateway': 'payzen'
                }
                
        except Exception as e:
            logger.error(f"PayZen payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'payzen'
            }
    
    def verify_webhook(self, payload: str, signature: str, secret: str) -> bool:
        """Vérifie la signature webhook PayZen"""
        
        # PayZen utilise SHA256
        expected_signature = hashlib.sha256(
            f"{payload}{secret}".encode()
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)


class SGMarocGateway:
    """Gateway Société Générale Maroc"""
    
    BASE_URL = "https://epayment.sg.ma/api/v2"
    
    def __init__(self):
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self, config: Dict) -> str:
        """Obtient un access token OAuth2"""
        
        # Vérifier si token existe et valide
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # Demander nouveau token
        auth_url = f"{self.BASE_URL}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": config['sg_api_username'],
            "client_secret": config['sg_api_password']
        }
        
        response = requests.post(auth_url, data=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        self.access_token = data['access_token']
        self.token_expires_at = datetime.now() + timedelta(seconds=data['expires_in'] - 60)
        
        return self.access_token
    
    def create_payment(self, config: Dict, amount: float, description: str, merchant_id: str) -> Dict:
        """Crée un paiement via SG Maroc"""
        
        access_token = self._get_access_token(config)
        
        payload = {
            "merchantCode": config['sg_merchant_code'],
            "terminalId": config['sg_terminal_id'],
            "amount": f"{amount:.2f}",
            "currency": "MAD",
            "orderId": f"ORDER-{datetime.now().strftime('%Y%m%d')}-{merchant_id[:8]}",
            "description": description,
            "ipnUrl": f"https://yourdomain.com/api/webhook/sg/{merchant_id}"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/payment/init",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                return {
                    'success': True,
                    'transaction_id': data['transactionId'],
                    'payment_url': data['paymentUrl'],
                    'status': 'pending',
                    'gateway': 'sg_maroc',
                    'request': payload,
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': data.get('error', 'Unknown error'),
                    'gateway': 'sg_maroc'
                }
                
        except Exception as e:
            logger.error(f"SG Maroc payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'sg_maroc'
            }
    
    def verify_webhook(self, payload: Dict, signature: str, secret: str) -> bool:
        """Vérifie la signature webhook SG Maroc"""
        
        # Construire message (ordre alphabétique des clés)
        sorted_keys = sorted(payload.keys())
        message = ''.join(str(payload[key]) for key in sorted_keys)
        
        # HMAC-SHA256
        expected_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        expected_signature_b64 = base64.b64encode(expected_signature).decode()
        
        return hmac.compare_digest(expected_signature_b64, signature)
```

---

## 📊 TABLEAU COMPARATIF

| Critère | CMI | PayZen | SG Maroc |
|---------|-----|--------|----------|
| **Frais** | 1.5% - 2% | 1.8% - 2.5% | 1.5% - 2.5% (négociable) |
| **Délai** | 2-3 jours | 24-48h | 2-3 jours |
| **Split Payment** | ❌ Non natif | ✅ Oui natif | ⚠️ Possible mais complexe |
| **Cartes acceptées** | CMI, Visa, MC | CMI, Visa, MC, Amex | CMI, Visa, MC |
| **Devises** | MAD | MAD, EUR, USD | MAD |
| **API** | ✅ Simple | ✅ Excellente | ⚠️ Moyenne |
| **Dashboard** | ⚠️ Basique | ✅ Complet | ✅ Bon |
| **Support** | ✅ Local | ✅ FR/MA | ✅ Local |

---

## 🚀 PROCHAINES ÉTAPES

Maintenant que vous avez choisi les 3 options, voulez-vous que je crée:

1. ✅ **Migration SQL** complète (tables gateway)?
2. ✅ **Service Python** multi-gateway complet?
3. ✅ **Interface admin** pour gérer les gateways?
4. ✅ **Page merchant** pour choisir leur gateway?
5. ✅ **Webhooks handlers** pour les 3 gateways?

Dites-moi par quoi commencer! 🎯

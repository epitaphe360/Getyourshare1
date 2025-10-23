"""
Endpoints avancés pour ShareYourSales API
À intégrer dans server.py
"""

from fastapi import HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from advanced_helpers import *

# ============================================
# NOUVEAUX MODÈLES PYDANTIC
# ============================================

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str
    price: float = Field(..., gt=0)
    commission_rate: float = Field(..., ge=0, le=100)
    commission_type: str = Field(default="percentage", pattern="^(percentage|fixed)$")
    stock_quantity: int = Field(default=0, ge=0)
    sku: Optional[str] = None
    weight: Optional[float] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    commission_rate: Optional[float] = None
    stock_quantity: Optional[int] = None
    is_available: Optional[bool] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|paused|ended|archived)$")
    budget: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str
    commission_type: str = Field(default="percentage", pattern="^(percentage|fixed)$")
    commission_value: float = Field(..., gt=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = Field(None, gt=0)
    status: str = Field(default="active", pattern="^(active|paused|ended|archived)$")
    product_ids: Optional[List[int]] = []
    briefing: Optional[dict] = None

class InvitationCreate(BaseModel):
    email: EmailStr
    message: Optional[str] = None
    commission_rate: Optional[float] = Field(None, ge=0, le=100)

class SaleCreate(BaseModel):
    link_id: str
    product_id: str
    customer_email: EmailStr
    customer_name: str
    amount: float = Field(..., gt=0)
    quantity: int = Field(default=1, ge=1)
    currency: str = Field(default="EUR")

class PayoutRequest(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(PayPal|Bank Transfer|Other)$")

class ClickRecord(BaseModel):
    link_id: str
    ip_address: str
    user_agent: str
    referrer: Optional[str] = None
    country: Optional[str] = None
    device_type: Optional[str] = None

# ============================================
# PRODUCTS ENDPOINTS
# ============================================

def add_products_endpoints(app, verify_token):
    """Ajoute les endpoints pour la gestion des produits"""
    
    @app.post("/api/products")
    async def create_product_endpoint(product_data: ProductCreate, payload: dict = Depends(verify_token)):
        """Crée un nouveau produit"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant":
            raise HTTPException(status_code=403, detail="Seuls les merchants peuvent créer des produits")
        
        merchant = get_merchant_by_user_id(user["id"])
        if not merchant:
            raise HTTPException(status_code=404, detail="Profil merchant non trouvé")
        
        product = create_product(
            merchant_id=merchant["id"],
            name=product_data.name,
            price=product_data.price,
            commission_rate=product_data.commission_rate,
            description=product_data.description,
            category=product_data.category,
            commission_type=product_data.commission_type,
            stock_quantity=product_data.stock_quantity,
            sku=product_data.sku,
            weight=product_data.weight
        )
        
        if not product:
            raise HTTPException(status_code=500, detail="Erreur lors de la création du produit")
        
        return {"message": "Produit créé avec succès", "product": product}
    
    @app.put("/api/products/{product_id}")
    async def update_product_endpoint(product_id: str, updates: ProductUpdate, payload: dict = Depends(verify_token)):
        """Met à jour un produit"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Vérifier que le produit appartient au merchant
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        merchant = get_merchant_by_user_id(user["id"])
        if product["merchant_id"] != merchant["id"]:
            raise HTTPException(status_code=403, detail="Ce produit ne vous appartient pas")
        
        # Convertir en dict et retirer les None
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        
        success = update_product(product_id, update_dict)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")
        
        return {"message": "Produit mis à jour avec succès"}
    
    @app.delete("/api/products/{product_id}")
    async def delete_product_endpoint(product_id: str, payload: dict = Depends(verify_token)):
        """Supprime un produit"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        merchant = get_merchant_by_user_id(user["id"])
        if product["merchant_id"] != merchant["id"]:
            raise HTTPException(status_code=403, detail="Ce produit ne vous appartient pas")
        
        success = delete_product(product_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erreur lors de la suppression")
        
        return {"message": "Produit supprimé avec succès"}

# ============================================
# CAMPAIGNS ENDPOINTS
# ============================================

def add_campaigns_endpoints(app, verify_token):
    """Ajoute les endpoints pour la gestion des campagnes"""
    
    @app.post("/api/campaigns")
    async def create_campaign_endpoint(campaign_data: CampaignCreate, payload: dict = Depends(verify_token)):
        """Crée une nouvelle campagne"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant":
            raise HTTPException(status_code=403, detail="Seuls les merchants peuvent créer des campagnes")
        
        merchant = get_merchant_by_user_id(user["id"])
        if not merchant:
            raise HTTPException(status_code=404, detail="Profil merchant non trouvé")
        
        from db_helpers import get_supabase_client
        supabase = get_supabase_client()
        
        # Créer la campagne
        campaign_dict = {
            "merchant_id": merchant["id"],
            "name": campaign_data.name,
            "description": campaign_data.description,
            "category": campaign_data.category,
            "status": campaign_data.status or "active",
            "commission_type": campaign_data.commission_type,
            "commission_value": float(campaign_data.commission_value),
            "start_date": campaign_data.start_date,
            "end_date": campaign_data.end_date,
            "budget": float(campaign_data.budget) if campaign_data.budget else None,
            "briefing": campaign_data.briefing
        }
        
        result = supabase.table("campaigns").insert(campaign_dict).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Erreur lors de la création de la campagne")
        
        campaign = result.data[0]
        
        # Assigner les produits si fournis
        if campaign_data.product_ids:
            for product_id in campaign_data.product_ids:
                assign_products_to_campaign(campaign["id"], [product_id])
        
        return {"message": "Campagne créée avec succès", "campaign": campaign}
    
    @app.put("/api/campaigns/{campaign_id}")
    async def update_campaign_endpoint(campaign_id: str, updates: CampaignUpdate, payload: dict = Depends(verify_token)):
        """Met à jour une campagne"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        success = update_campaign(campaign_id, update_dict)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")
        
        return {"message": "Campagne mise à jour avec succès"}
    
    @app.delete("/api/campaigns/{campaign_id}")
    async def delete_campaign_endpoint(campaign_id: str, payload: dict = Depends(verify_token)):
        """Supprime une campagne"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        success = delete_campaign(campaign_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erreur lors de la suppression")
        
        return {"message": "Campagne supprimée avec succès"}

# ============================================
# INVITATIONS ENDPOINTS
# ============================================

def add_invitations_endpoints(app, verify_token):
    """Ajoute les endpoints pour les invitations d'affiliés"""
    
    @app.post("/api/invitations")
    async def create_invitation_endpoint(invitation_data: InvitationCreate, payload: dict = Depends(verify_token)):
        """Crée une invitation pour un affilié"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant":
            raise HTTPException(status_code=403, detail="Seuls les merchants peuvent inviter des affiliés")
        
        merchant = get_merchant_by_user_id(user["id"])
        if not merchant:
            raise HTTPException(status_code=404, detail="Profil merchant non trouvé")
        
        invitation = create_invitation(
            merchant_id=merchant["id"],
            email=invitation_data.email,
            message=invitation_data.message,
            commission_rate=invitation_data.commission_rate
        )
        
        if not invitation:
            raise HTTPException(status_code=500, detail="Erreur lors de la création de l'invitation")
        
        return {"message": "Invitation envoyée avec succès", "invitation": invitation}
    
    @app.get("/api/invitations")
    async def get_invitations_endpoint(payload: dict = Depends(verify_token)):
        """Liste les invitations"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "merchant":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        merchant = get_merchant_by_user_id(user["id"])
        
        # Récupérer les invitations du merchant
        invitations = supabase.table("invitations").select("*").eq("merchant_id", merchant["id"]).execute()
        
        return {"invitations": invitations.data or [], "total": len(invitations.data or [])}
    
    @app.post("/api/invitations/accept/{invitation_code}")
    async def accept_invitation_endpoint(invitation_code: str, payload: dict = Depends(verify_token)):
        """Accepte une invitation"""
        user = get_user_by_id(payload["sub"])
        
        success = accept_invitation(invitation_code, user["id"])
        
        if not success:
            raise HTTPException(status_code=400, detail="Impossible d'accepter l'invitation")
        
        return {"message": "Invitation acceptée avec succès"}

# ============================================
# SALES & TRACKING ENDPOINTS
# ============================================

def add_sales_endpoints(app, verify_token):
    """Ajoute les endpoints pour les ventes et le tracking"""
    
    @app.post("/api/sales")
    async def create_sale_endpoint(sale_data: SaleCreate, payload: dict = Depends(verify_token)):
        """Enregistre une nouvelle vente"""
        user = get_user_by_id(payload["sub"])
        
        # Récupérer les infos du lien
        link = supabase.table("trackable_links").select("influencer_id, product_id").eq("id", sale_data.link_id).execute()
        
        if not link.data:
            raise HTTPException(status_code=404, detail="Lien d'affiliation non trouvé")
        
        # Récupérer le merchant du produit
        product = get_product_by_id(sale_data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        sale = create_sale(
            link_id=sale_data.link_id,
            product_id=sale_data.product_id,
            influencer_id=link.data[0]["influencer_id"],
            merchant_id=product["merchant_id"],
            amount=sale_data.amount,
            customer_email=sale_data.customer_email,
            customer_name=sale_data.customer_name,
            quantity=sale_data.quantity,
            currency=sale_data.currency
        )
        
        if not sale:
            raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement de la vente")
        
        return {"message": "Vente enregistrée avec succès", "sale": sale}
    
    @app.post("/api/tracking/click")
    async def record_click_endpoint(click_data: ClickRecord):
        """Enregistre un clic sur un lien d'affiliation"""
        click = record_click(
            link_id=click_data.link_id,
            ip_address=click_data.ip_address,
            user_agent=click_data.user_agent,
            referrer=click_data.referrer,
            country=click_data.country,
            device_type=click_data.device_type
        )
        
        if not click:
            raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement du clic")
        
        return {"message": "Clic enregistré", "click_id": click["id"]}

# ============================================
# PAYOUTS ENDPOINTS
# ============================================

def add_payouts_endpoints(app, verify_token):
    """Ajoute les endpoints pour les paiements"""
    
    @app.post("/api/payouts/request")
    async def request_payout_endpoint(payout_data: PayoutRequest, payload: dict = Depends(verify_token)):
        """Crée une demande de paiement"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "influencer":
            raise HTTPException(status_code=403, detail="Seuls les influencers peuvent demander un paiement")
        
        influencer = get_influencer_by_user_id(user["id"])
        if not influencer:
            raise HTTPException(status_code=404, detail="Profil influencer non trouvé")
        
        payout = create_payout_request(
            influencer_id=influencer["id"],
            amount=payout_data.amount,
            payment_method=payout_data.payment_method
        )
        
        if not payout:
            raise HTTPException(status_code=400, detail="Solde insuffisant ou erreur")
        
        return {"message": "Demande de paiement créée", "payout": payout}
    
    @app.put("/api/payouts/{payout_id}/approve")
    async def approve_payout_endpoint(payout_id: str, payload: dict = Depends(verify_token)):
        """Approuve une demande de paiement"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        success = approve_payout(payout_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erreur lors de l'approbation")
        
        return {"message": "Paiement approuvé"}

# ============================================
# REPORTS ENDPOINTS
# ============================================

def add_reports_endpoints(app, verify_token):
    """Ajoute les endpoints pour les rapports"""
    
    @app.get("/api/reports/performance")
    async def get_performance_report_endpoint(start_date: str, end_date: str, payload: dict = Depends(verify_token)):
        """Génère un rapport de performance"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "influencer":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        influencer = get_influencer_by_user_id(user["id"])
        if not influencer:
            raise HTTPException(status_code=404, detail="Profil influencer non trouvé")
        
        report = get_performance_report(influencer["id"], start_date, end_date)
        
        return {"report": report}

# ============================================
# SETTINGS ENDPOINTS
# ============================================

def add_settings_endpoints(app, verify_token):
    """Ajoute les endpoints pour les paramètres"""
    
    @app.get("/api/settings/platform")
    async def get_platform_settings_endpoint(payload: dict = Depends(verify_token)):
        """Récupère les paramètres de la plateforme"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        settings = get_platform_settings()
        return {"settings": settings}
    
    @app.put("/api/settings/platform/{key}")
    async def update_platform_setting_endpoint(key: str, value: str, payload: dict = Depends(verify_token)):
        """Met à jour un paramètre de la plateforme"""
        user = get_user_by_id(payload["sub"])
        
        if user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        success = update_platform_setting(key, value)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")
        
        return {"message": "Paramètre mis à jour"}

# ============================================
# FONCTION PRINCIPALE D'INTÉGRATION
# ============================================

def integrate_all_endpoints(app, verify_token):
    """Intègre tous les nouveaux endpoints dans l'application"""
    add_products_endpoints(app, verify_token)
    add_campaigns_endpoints(app, verify_token)
    add_invitations_endpoints(app, verify_token)
    add_sales_endpoints(app, verify_token)
    add_payouts_endpoints(app, verify_token)
    add_reports_endpoints(app, verify_token)
    add_settings_endpoints(app, verify_token)
    
    # Ajouter les endpoints d'upload
    try:
        from upload_endpoints import add_upload_endpoints
        add_upload_endpoints(app, verify_token)
        print("✅ Endpoints d'upload intégrés")
    except ImportError:
        print("⚠️  Module upload_endpoints non trouvé")
    
    # Ajouter les endpoints de recherche d'influenceurs
    try:
        from influencer_search_endpoints import add_influencer_search_endpoints
        add_influencer_search_endpoints(app, verify_token)
        print("✅ Endpoints de recherche d'influenceurs intégrés")
    except ImportError:
        print("⚠️  Module influencer_search_endpoints non trouvé")
    
    print("✅ Tous les endpoints avancés ont été intégrés")

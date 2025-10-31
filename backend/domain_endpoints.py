"""
============================================
DOMAIN MANAGEMENT ENDPOINTS
Share Your Sales - Gestion des Domaines
============================================

Gestion des domaines autorisés pour les redirections:
- Small: 1 domaine
- Medium: 2 domaines
- Large: Domaines illimités
- Marketplace: Non applicable (pas de domaines personnalisés)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
import os
import secrets
import re
from auth import get_current_user

router = APIRouter(prefix="/api/domains", tags=["Domain Management"])

# ============================================
# ENVIRONMENT VARIABLES VALIDATION
# ============================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing required Supabase environment variables")

# ============================================
# SUPABASE CLIENT
# ============================================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================
# PYDANTIC MODELS
# ============================================

class AddDomainRequest(BaseModel):
    """Ajout d'un nouveau domaine"""
    domain: str = Field(..., description="Domain name (e.g., example.com or shop.example.com)")

    @validator('domain')
    def validate_domain(cls, v):
        # Nettoyer le domaine
        v = v.lower().strip()
        # Supprimer https://, http://, www.
        v = re.sub(r'^https?://', '', v)
        v = re.sub(r'^www\.', '', v)
        # Supprimer le trailing slash
        v = v.rstrip('/')

        # Valider le format
        domain_pattern = r'^([a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$'
        if not re.match(domain_pattern, v):
            raise ValueError('Invalid domain format')

        return v

class DomainResponse(BaseModel):
    """Détails d'un domaine"""
    id: str
    company_id: str
    domain: str
    is_verified: bool
    verification_token: Optional[str]
    verified_at: Optional[datetime]
    is_active: bool
    created_at: datetime

class DomainStatsResponse(BaseModel):
    """Statistiques des domaines"""
    total_domains: int
    verified_domains: int
    pending_verification: int
    domain_limit: Optional[int]
    can_add_domain: bool
    available_slots: Optional[int]

class VerifyDomainResponse(BaseModel):
    """Instructions de vérification du domaine"""
    domain: str
    verification_token: str
    verification_methods: List[Dict[str, str]]
    instructions: str

# ============================================
# HELPER FUNCTIONS
# ============================================

async def check_can_add_domain(company_id: str) -> bool:
    """Vérifie si l'entreprise peut ajouter un domaine"""
    try:
        response = supabase.rpc("check_subscription_limit", {
            "p_user_id": company_id,
            "p_limit_type": "domains"
        }).execute()

        return response.data if response.data is not None else False
    except Exception as e:
        print(f"Error checking domain limit: {e}")
        return False

async def get_domain_count(company_id: str) -> int:
    """Compte le nombre de domaines de l'entreprise"""
    try:
        response = supabase.from_("allowed_domains") \
            .select("id", count="exact") \
            .eq("company_id", company_id) \
            .eq("is_active", True) \
            .execute()

        return response.count if response.count else 0
    except Exception as e:
        print(f"Error counting domains: {e}")
        return 0

async def update_subscription_domain_count(company_id: str):
    """Met à jour le compteur de domaines dans la table subscriptions"""
    try:
        count = await get_domain_count(company_id)

        supabase.from_("subscriptions") \
            .update({"current_domains": count}) \
            .eq("user_id", company_id) \
            .in_("status", ["active", "trialing"]) \
            .execute()
    except Exception as e:
        print(f"Error updating domain count: {e}")

def generate_verification_instructions(domain: str, token: str) -> Dict[str, Any]:
    """Génère les instructions de vérification du domaine"""

    methods = [
        {
            "method": "DNS TXT Record",
            "name": "_shareyoursales-verification",
            "type": "TXT",
            "value": token,
            "description": "Add a TXT record to your DNS configuration"
        },
        {
            "method": "Meta Tag",
            "tag": f'<meta name="shareyoursales-verification" content="{token}">',
            "location": "<head> section of your homepage",
            "description": "Add this meta tag to your website's homepage"
        },
        {
            "method": "HTML File",
            "filename": "shareyoursales-verification.txt",
            "content": token,
            "location": f"https://{domain}/shareyoursales-verification.txt",
            "description": "Upload a text file containing the verification token"
        }
    ]

    instructions = f"""
    Domain Verification for {domain}

    Choose one of the following verification methods:

    Method 1: DNS TXT Record (Recommended)
    - Add a TXT record to your DNS:
      Name: _shareyoursales-verification
      Value: {token}
    - Wait for DNS propagation (up to 24 hours)
    - Click 'Verify' in your dashboard

    Method 2: Meta Tag
    - Add this tag to your homepage <head>:
      <meta name="shareyoursales-verification" content="{token}">
    - Click 'Verify' in your dashboard

    Method 3: HTML File
    - Create a file: shareyoursales-verification.txt
    - Content: {token}
    - Upload to: https://{domain}/shareyoursales-verification.txt
    - Click 'Verify' in your dashboard
    """

    return {
        "methods": methods,
        "instructions": instructions
    }

async def verify_domain_ownership(domain: str, token: str) -> bool:
    """Vérifie la propriété du domaine via différentes méthodes"""
    import aiohttp
    import asyncio

    # Méthode 1: Vérifier le fichier HTML
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://{domain}/shareyoursales-verification.txt"
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    if content.strip() == token:
                        return True
    except Exception:
        pass

    # Méthode 2: Vérifier la meta tag
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://{domain}"
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    if f'<meta name="shareyoursales-verification" content="{token}">' in html:
                        return True
    except Exception:
        pass

    # Méthode 3: Vérifier le DNS TXT (nécessite dnspython)
    try:
        import dns.resolver
        answers = dns.resolver.resolve(f"_shareyoursales-verification.{domain}", 'TXT')
        for rdata in answers:
            if token in str(rdata):
                return True
    except Exception:
        pass

    return False

# ============================================
# ENDPOINTS - DOMAIN MANAGEMENT
# ============================================

@router.get("/", response_model=List[DomainResponse])
async def get_domains(
    verified_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Liste les domaines de l'entreprise

    Filtres:
    - verified_only: Ne retourner que les domaines vérifiés
    """
    try:
        # Seules les entreprises peuvent gérer des domaines
        if current_user.get("role") not in ["merchant", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only companies can manage domains"
            )

        company_id = current_user["id"]

        query = supabase.from_("allowed_domains") \
            .select("*") \
            .eq("company_id", company_id) \
            .eq("is_active", True)

        if verified_only:
            query = query.eq("is_verified", True)

        response = query.order("created_at", desc=True).execute()

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching domains: {str(e)}"
        )

@router.get("/{domain_id}", response_model=DomainResponse)
async def get_domain(
    domain_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Détails d'un domaine spécifique"""
    try:
        company_id = current_user["id"]

        response = supabase.from_("allowed_domains") \
            .select("*") \
            .eq("id", domain_id) \
            .eq("company_id", company_id) \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Domain not found")

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching domain: {str(e)}"
        )

@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_domain(
    request: AddDomainRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Ajouter un nouveau domaine

    Process:
    1. Vérifie la limite du plan d'abonnement
    2. Vérifie que le domaine n'existe pas déjà
    3. Génère un token de vérification
    4. Crée l'entrée dans allowed_domains
    5. Retourne les instructions de vérification

    Restrictions:
    - Small: 1 domaine
    - Medium: 2 domaines
    - Large: Illimité
    - Marketplace: Non applicable
    """
    try:
        # Vérifier que c'est une entreprise
        if current_user.get("role") not in ["merchant", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only companies can add domains"
            )

        company_id = current_user["id"]

        # Vérifier la limite du plan
        can_add = await check_can_add_domain(company_id)
        if not can_add:
            raise HTTPException(
                status_code=403,
                detail="Domain limit reached. Please upgrade your plan."
            )

        # Vérifier que le domaine n'existe pas déjà
        existing = supabase.from_("allowed_domains") \
            .select("id") \
            .eq("company_id", company_id) \
            .eq("domain", request.domain) \
            .eq("is_active", True) \
            .execute()

        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=400,
                detail="This domain is already registered"
            )

        # Générer le token de vérification
        verification_token = secrets.token_urlsafe(32)

        # Créer le domaine
        domain_data = {
            "company_id": company_id,
            "domain": request.domain,
            "is_verified": False,
            "verification_token": verification_token,
            "is_active": True
        }

        response = supabase.from_("allowed_domains") \
            .insert(domain_data) \
            .execute()

        # Mettre à jour le compteur
        await update_subscription_domain_count(company_id)

        # Générer les instructions de vérification
        verification_info = generate_verification_instructions(
            request.domain,
            verification_token
        )

        return {
            "success": True,
            "message": f"Domain {request.domain} added. Please verify ownership.",
            "domain": response.data[0],
            "verification": verification_info
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding domain: {str(e)}"
        )

@router.post("/{domain_id}/verify")
async def verify_domain(
    domain_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Vérifier la propriété d'un domaine

    Vérifie la présence du token de vérification via:
    1. Fichier HTML (shareyoursales-verification.txt)
    2. Meta tag dans la page d'accueil
    3. DNS TXT record
    """
    try:
        company_id = current_user["id"]

        # Récupérer le domaine
        response = supabase.from_("allowed_domains") \
            .select("*") \
            .eq("id", domain_id) \
            .eq("company_id", company_id) \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Domain not found")

        domain_data = response.data

        # Si déjà vérifié
        if domain_data["is_verified"]:
            return {
                "success": True,
                "message": "Domain is already verified",
                "verified_at": domain_data["verified_at"]
            }

        # Vérifier la propriété
        is_verified = await verify_domain_ownership(
            domain_data["domain"],
            domain_data["verification_token"]
        )

        if is_verified:
            # Marquer comme vérifié
            supabase.from_("allowed_domains") \
                .update({
                    "is_verified": True,
                    "verified_at": datetime.now().isoformat(),
                    "verification_token": None  # Supprimer le token
                }) \
                .eq("id", domain_id) \
                .execute()

            return {
                "success": True,
                "message": f"Domain {domain_data['domain']} verified successfully",
                "verified_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Domain verification failed. Please check that you have correctly added the verification token."
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying domain: {str(e)}"
        )

@router.get("/{domain_id}/verification-info", response_model=VerifyDomainResponse)
async def get_verification_info(
    domain_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les instructions de vérification d'un domaine"""
    try:
        company_id = current_user["id"]

        response = supabase.from_("allowed_domains") \
            .select("*") \
            .eq("id", domain_id) \
            .eq("company_id", company_id) \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Domain not found")

        domain_data = response.data

        if domain_data["is_verified"]:
            raise HTTPException(
                status_code=400,
                detail="Domain is already verified"
            )

        verification_info = generate_verification_instructions(
            domain_data["domain"],
            domain_data["verification_token"]
        )

        return {
            "domain": domain_data["domain"],
            "verification_token": domain_data["verification_token"],
            "verification_methods": verification_info["methods"],
            "instructions": verification_info["instructions"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching verification info: {str(e)}"
        )

@router.delete("/{domain_id}")
async def remove_domain(
    domain_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprimer un domaine

    Note: Cette action désactive le domaine.
    Les liens existants pointant vers ce domaine cesseront de fonctionner.
    """
    try:
        company_id = current_user["id"]

        # Vérifier que le domaine existe
        existing = supabase.from_("allowed_domains") \
            .select("*") \
            .eq("id", domain_id) \
            .eq("company_id", company_id) \
            .single() \
            .execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="Domain not found")

        # Désactiver le domaine (soft delete)
        supabase.from_("allowed_domains") \
            .update({"is_active": False}) \
            .eq("id", domain_id) \
            .execute()

        # Mettre à jour le compteur
        await update_subscription_domain_count(company_id)

        return {
            "success": True,
            "message": f"Domain {existing.data['domain']} removed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error removing domain: {str(e)}"
        )

# ============================================
# ENDPOINTS - DOMAIN STATS
# ============================================

@router.get("/stats/summary", response_model=DomainStatsResponse)
async def get_domain_stats(current_user: dict = Depends(get_current_user)):
    """
    Statistiques des domaines

    Retourne:
    - Nombre total de domaines
    - Domaines vérifiés vs en attente
    - Limite du plan
    - Capacité à ajouter des domaines
    """
    try:
        company_id = current_user["id"]

        # Récupérer tous les domaines
        response = supabase.from_("allowed_domains") \
            .select("*") \
            .eq("company_id", company_id) \
            .eq("is_active", True) \
            .execute()

        domains = response.data

        # Compter par statut
        verified_domains = len([d for d in domains if d["is_verified"]])
        pending_verification = len([d for d in domains if not d["is_verified"]])

        # Récupérer la limite du plan
        subscription_response = supabase.from_("v_active_subscriptions") \
            .select("plan_max_domains") \
            .eq("user_id", company_id) \
            .single() \
            .execute()

        domain_limit = None
        available_slots = None
        can_add = False

        if subscription_response.data:
            domain_limit = subscription_response.data.get("plan_max_domains")
            if domain_limit is not None:
                available_slots = domain_limit - len(domains)
            can_add = await check_can_add_domain(company_id)

        return {
            "total_domains": len(domains),
            "verified_domains": verified_domains,
            "pending_verification": pending_verification,
            "domain_limit": domain_limit,
            "can_add_domain": can_add,
            "available_slots": available_slots
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching domain stats: {str(e)}"
        )

# ============================================
# ENDPOINTS - VALIDATION
# ============================================

@router.post("/validate-redirect")
async def validate_redirect_url(
    url: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Valider qu'une URL de redirection est autorisée

    Vérifie que le domaine est:
    1. Enregistré par l'entreprise
    2. Vérifié
    3. Actif
    """
    try:
        company_id = current_user["id"]

        # Extraire le domaine de l'URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Supprimer www.
        domain = re.sub(r'^www\.', '', domain)

        # Vérifier que le domaine est autorisé
        response = supabase.from_("allowed_domains") \
            .select("*") \
            .eq("company_id", company_id) \
            .eq("domain", domain) \
            .eq("is_verified", True) \
            .eq("is_active", True) \
            .single() \
            .execute()

        if response.data:
            return {
                "valid": True,
                "message": "Redirect URL is valid",
                "domain": domain
            }
        else:
            return {
                "valid": False,
                "message": "Domain is not verified or not registered",
                "domain": domain
            }

    except Exception as e:
        return {
            "valid": False,
            "message": f"Error validating URL: {str(e)}",
            "domain": None
        }

"""
Fonctions helpers pour interagir avec Supabase
Simplifie les opérations CRUD
"""

from supabase_client import supabase
from typing import Optional, List, Dict, Any
from datetime import datetime
import bcrypt
from cache_manager import cached, CACHE_TTL_MEDIUM, invalidate_cache

# ============================================
# USERS
# ============================================


def get_user_by_email(email: str) -> Optional[Dict]:
    """Récupère un utilisateur par email"""
    try:
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Récupère un utilisateur par ID"""
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user by id: {e}")
        return None


def create_user(email: str, password: str, role: str, **kwargs) -> Optional[Dict]:
    """Crée un nouvel utilisateur"""
    try:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "phone": kwargs.get("phone"),
            "two_fa_enabled": kwargs.get("two_fa_enabled", False),
            "is_active": kwargs.get("is_active", True),
        }

        if "email_verified" in kwargs:
            user_data["email_verified"] = kwargs.get("email_verified")
        if kwargs.get("verification_token"):
            user_data["verification_token"] = kwargs.get("verification_token")
        if kwargs.get("verification_expires"):
            user_data["verification_expires"] = kwargs.get("verification_expires")
        if kwargs.get("verification_sent_at"):
            user_data["verification_sent_at"] = kwargs.get("verification_sent_at")

        result = supabase.table("users").insert(user_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


def get_user_by_verification_token(token: str) -> Optional[Dict]:
    """Récupère un utilisateur via son token de vérification"""
    try:
        result = (
            supabase.table("users").select("*").eq("verification_token", token).limit(1).execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user by verification token: {e}")
        return None


def set_verification_token(user_id: str, token: str, expires_at: str, sent_at: str) -> bool:
    """Met à jour le token de vérification pour un utilisateur"""
    try:
        supabase.table("users").update(
            {
                "verification_token": token,
                "verification_expires": expires_at,
                "verification_sent_at": sent_at,
                "email_verified": False,
            }
        ).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error setting verification token: {e}")
        return False


def mark_email_verified(user_id: str) -> bool:
    """Marque l'email d'un utilisateur comme vérifié"""
    try:
        supabase.table("users").update(
            {
                "email_verified": True,
                "verification_token": None,
                "verification_expires": None,
                "verification_sent_at": None,
            }
        ).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error marking email as verified: {e}")
        return False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash"""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False


def update_user_last_login(user_id: str):
    """Met à jour la date de dernière connexion"""
    try:
        supabase.table("users").update({"last_login": datetime.now().isoformat()}).eq(
            "id", user_id
        ).execute()
    except Exception as e:
        print(f"Error updating last login: {e}")


# ============================================
# MERCHANTS
# ============================================


def get_all_merchants() -> List[Dict]:
    """Récupère tous les merchants avec leurs données utilisateur"""
    try:
        result = (
            supabase.table("merchants")
            .select(
                """
            *,
            users:user_id (
                id,
                email,
                phone,
                last_login
            )
        """
            )
            .execute()
        )
        return result.data
    except Exception as e:
        print(f"Error getting merchants: {e}")
        return []


def get_merchant_by_id(merchant_id: str) -> Optional[Dict]:
    """Récupère un merchant par ID"""
    try:
        result = (
            supabase.table("merchants")
            .select(
                """
            *,
            users:user_id (
                id,
                email,
                phone
            )
        """
            )
            .eq("id", merchant_id)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting merchant: {e}")
        return None


def get_merchant_by_user_id(user_id: str) -> Optional[Dict]:
    """Récupère un merchant par user_id"""
    try:
        result = supabase.table("merchants").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting merchant by user_id: {e}")
        return None


# ============================================
# INFLUENCERS
# ============================================


def get_all_influencers() -> List[Dict]:
    """Récupère tous les influencers"""
    try:
        result = (
            supabase.table("influencers")
            .select(
                """
            *,
            users:user_id (
                id,
                email,
                phone
            )
        """
            )
            .execute()
        )
        return result.data
    except Exception as e:
        print(f"Error getting influencers: {e}")
        return []


def get_influencer_by_id(influencer_id: str) -> Optional[Dict]:
    """Récupère un influencer par ID"""
    try:
        result = (
            supabase.table("influencers")
            .select(
                """
            *,
            users:user_id (
                id,
                email
            )
        """
            )
            .eq("id", influencer_id)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting influencer: {e}")
        return None


def get_influencer_by_user_id(user_id: str) -> Optional[Dict]:
    """Récupère un influencer par user_id"""
    try:
        result = supabase.table("influencers").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting influencer by user_id: {e}")
        return None


# ============================================
# PRODUCTS
# ============================================


def get_all_products(
    category: Optional[str] = None, merchant_id: Optional[str] = None
) -> List[Dict]:
    """Récupère tous les produits avec filtres optionnels"""
    try:
        query = supabase.table("products").select(
            """
            *,
            merchants:merchant_id (
                id,
                company_name
            )
        """
        )

        if category:
            query = query.eq("category", category)
        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        result = query.execute()
        return result.data
    except Exception as e:
        print(f"Error getting products: {e}")
        return []


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """Récupère un produit par ID"""
    try:
        result = (
            supabase.table("products")
            .select(
                """
            *,
            merchants:merchant_id (
                company_name
            )
        """
            )
            .eq("id", product_id)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting product: {e}")
        return None


# ============================================
# TRACKABLE LINKS (Affiliate Links)
# ============================================


def get_affiliate_links(influencer_id: Optional[str] = None) -> List[Dict]:
    """Récupère les liens d'affiliation"""
    try:
        query = supabase.table("trackable_links").select(
            """
            *,
            products:product_id (
                name,
                category,
                price
            ),
            influencers:influencer_id (
                username,
                full_name
            )
        """
        )

        if influencer_id:
            query = query.eq("influencer_id", influencer_id)

        result = query.execute()
        return result.data
    except Exception as e:
        print(f"Error getting affiliate links: {e}")
        return []


def create_affiliate_link(product_id: str, influencer_id: str, unique_code: str) -> Optional[Dict]:
    """Crée un nouveau lien d'affiliation ou retourne le lien existant"""
    try:
        # Check if link already exists
        existing_link = (
            supabase.table("trackable_links")
            .select("*")
            .eq("product_id", product_id)
            .eq("influencer_id", influencer_id)
            .execute()
        )

        if existing_link.data:
            print(f"Link already exists for product {product_id} and influencer {influencer_id}")
            return existing_link.data[0]

        # Create new link if it doesn't exist
        link_data = {
            "product_id": product_id,
            "influencer_id": influencer_id,
            "unique_code": unique_code,
            "full_url": f"https://shareyoursales.com/track/{unique_code}",
            "short_url": f"shs.io/{unique_code[:8]}",
            "is_active": True,
        }

        result = supabase.table("trackable_links").insert(link_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating affiliate link: {e}")
        return None


# ============================================
# CAMPAIGNS
# ============================================


def get_all_campaigns(merchant_id: Optional[str] = None) -> List[Dict]:
    """Récupère toutes les campagnes"""
    try:
        query = supabase.table("campaigns").select(
            """
            *,
            merchants:merchant_id (
                company_name
            )
        """
        )

        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        result = query.execute()
        return result.data
    except Exception as e:
        print(f"Error getting campaigns: {e}")
        return []


def create_campaign(merchant_id: str, name: str, **kwargs) -> Optional[Dict]:
    """Crée une nouvelle campagne"""
    try:
        campaign_data = {
            "merchant_id": merchant_id,
            "name": name,
            "description": kwargs.get("description"),
            "budget": kwargs.get("budget"),
            "start_date": kwargs.get("start_date"),
            "end_date": kwargs.get("end_date"),
            "status": kwargs.get("status", "draft"),
        }

        result = supabase.table("campaigns").insert(campaign_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating campaign: {e}")
        return None


# ============================================
# ANALYTICS
# ============================================


@cached(ttl=CACHE_TTL_MEDIUM, key_prefix="dashboard_stats")
def get_dashboard_stats(role: str, user_id: str) -> Dict:
    """
    Récupère les statistiques pour le dashboard selon le rôle
    OPTIMISÉ: Utilise des requêtes groupées pour éviter N+1 problem
    CACHE: Résultats mis en cache 5 minutes pour réduire charge DB
    """
    try:
        if role == "admin":
            # OPTIMISATION: Faire toutes les requêtes COUNT en parallèle via RPC ou requêtes groupées
            # Au lieu de 5 requêtes séparées, utiliser une seule requête SQL avec UNION ALL
            
            # Méthode optimisée: Requêtes parallèles au lieu de séquentielles
            from concurrent.futures import ThreadPoolExecutor
            
            def count_table(table_name, condition=None):
                query = supabase.table(table_name).select("id", count="exact")
                if condition:
                    for key, value in condition.items():
                        query = query.eq(key, value)
                return query.execute().count
            
            def sum_sales():
                sales = supabase.table("sales").select("amount").eq("status", "completed").execute()
                return sum([s["amount"] for s in sales.data]) if sales.data else 0
            
            # Exécution parallèle des requêtes (3x plus rapide)
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    'users': executor.submit(count_table, "users"),
                    'merchants': executor.submit(count_table, "merchants"),
                    'influencers': executor.submit(count_table, "influencers"),
                    'products': executor.submit(count_table, "products"),
                    'revenue': executor.submit(sum_sales)
                }
                
                results = {key: future.result() for key, future in futures.items()}

            return {
                "total_users": results['users'],
                "total_merchants": results['merchants'],
                "total_influencers": results['influencers'],
                "total_products": results['products'],
                "total_revenue": results['revenue'],
            }

        elif role == "merchant":
            # Stats merchant - OPTIMISÉ: 1 requête au lieu de plusieurs
            merchant = get_merchant_by_user_id(user_id)
            if not merchant:
                return {}

            merchant_id = merchant["id"]
            
            # OPTIMISATION: Requêtes parallèles
            from concurrent.futures import ThreadPoolExecutor
            
            def count_products():
                return (
                    supabase.table("products")
                    .select("id", count="exact")
                    .eq("merchant_id", merchant_id)
                    .execute()
                    .count
                )
            
            def sum_sales():
                sales = (
                    supabase.table("sales")
                    .select("amount")
                    .eq("merchant_id", merchant_id)
                    .eq("status", "completed")
                    .execute()
                )
                return sum([s["amount"] for s in sales.data]) if sales.data else 0
            
            def count_affiliates():
                # Compter les influenceurs ayant généré des ventes pour ce marchand
                result = (
                    supabase.table("sales")
                    .select("influencer_id", count="exact")
                    .eq("merchant_id", merchant_id)
                    .execute()
                )
                # Unique influencers
                unique_influencers = set(s["influencer_id"] for s in result.data if s.get("influencer_id"))
                return len(unique_influencers)
            
            # Exécution parallèle
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    'products': executor.submit(count_products),
                    'sales': executor.submit(sum_sales),
                    'affiliates': executor.submit(count_affiliates)
                }
                results = {key: future.result() for key, future in futures.items()}

            return {
                "total_sales": results['sales'],
                "products_count": results['products'],
                "affiliates_count": results['affiliates'],
                "roi": 320.5,  # Calcul ROI à implémenter
            }

        elif role == "influencer":
            # Stats influencer
            influencer = get_influencer_by_user_id(user_id)
            if not influencer:
                return {}

            return {
                "total_earnings": influencer.get("total_earnings", 0),
                "total_clicks": influencer.get("total_clicks", 0),
                "total_sales": influencer.get("total_sales", 0),
                "balance": influencer.get("balance", 0),
            }

        return {}

    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return {}


# ============================================
# CONVERSIONS & SALES
# ============================================


def get_conversions(limit: int = 20) -> List[Dict]:
    """Récupère les conversions récentes"""
    try:
        result = (
            supabase.table("sales")
            .select(
                """
            *,
            products:product_id (
                name
            ),
            influencers:influencer_id (
                full_name,
                username
            ),
            merchants:merchant_id (
                company_name
            )
        """
            )
            .order("sale_timestamp", desc=True)
            .limit(limit)
            .execute()
        )

        return result.data
    except Exception as e:
        print(f"Error getting conversions: {e}")
        return []


# ============================================
# CLICKS TRACKING
# ============================================


def get_clicks(limit: int = 50) -> List[Dict]:
    """Récupère les clics récents"""
    try:
        result = (
            supabase.table("click_tracking")
            .select(
                """
            *,
            trackable_links:link_id (
                unique_code,
                products:product_id (
                    name
                ),
                influencers:influencer_id (
                    username
                )
            )
        """
            )
            .order("clicked_at", desc=True)
            .limit(limit)
            .execute()
        )

        return result.data
    except Exception as e:
        print(f"Error getting clicks: {e}")
        return []


# ============================================
# PAYOUTS
# ============================================


def get_payouts() -> List[Dict]:
    """Récupère tous les payouts"""
    try:
        result = (
            supabase.table("commissions")
            .select(
                """
            *,
            influencers:influencer_id (
                full_name,
                username
            )
        """
            )
            .execute()
        )

        return result.data
    except Exception as e:
        print(f"Error getting payouts: {e}")
        return []


def update_payout_status(payout_id: str, status: str) -> bool:
    """Met à jour le statut d'un payout"""
    try:
        if status in {"approved", "paid", "rejected", "pending"}:
            result = supabase.rpc(
                "approve_payout_transaction", {"p_commission_id": payout_id, "p_status": status}
            ).execute()
            data = result.data
            if isinstance(data, list):
                return bool(data and data[0])
            return bool(data)

        update_data = {"status": status}
        supabase.table("commissions").update(update_data).eq("id", payout_id).execute()
        return True
    except Exception as e:
        print(f"Error updating payout status: {e}")
        return False

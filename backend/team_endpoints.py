"""
============================================
TEAM MANAGEMENT ENDPOINTS
Share Your Sales - Gestion d'Équipe
============================================

Gestion des membres d'équipe pour les entreprises:
- Invitation de commerciaux/influenceurs
- Gestion des permissions
- Respect des limites du plan d'abonnement
- Attribution de commissions personnalisées
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
import os
import secrets
from auth import get_current_user

router = APIRouter(prefix="/api/team", tags=["Team Management"])

# ============================================
# SUPABASE CLIENT
# ============================================

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# ============================================
# PYDANTIC MODELS
# ============================================

class InviteTeamMemberRequest(BaseModel):
    """Invitation d'un nouveau membre d'équipe"""
    email: EmailStr
    team_role: str = Field(..., description="commercial, influencer, or manager")
    can_view_all_sales: bool = False
    can_manage_products: bool = False
    custom_commission_rate: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None

    @validator('team_role')
    def validate_role(cls, v):
        allowed_roles = ['commercial', 'influencer', 'manager']
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v

    @validator('custom_commission_rate')
    def validate_commission(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Commission rate must be between 0 and 100")
        return v

class UpdateTeamMemberRequest(BaseModel):
    """Mise à jour d'un membre d'équipe"""
    team_role: Optional[str] = None
    can_view_all_sales: Optional[bool] = None
    can_manage_products: Optional[bool] = None
    custom_commission_rate: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    notes: Optional[str] = None

    @validator('team_role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = ['commercial', 'influencer', 'manager']
            if v not in allowed_roles:
                raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['active', 'inactive', 'pending_invitation']
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v

class TeamMemberResponse(BaseModel):
    """Détails d'un membre d'équipe"""
    id: str
    company_id: str
    member_id: Optional[str]
    team_role: str
    can_view_all_sales: bool
    can_manage_products: bool
    custom_commission_rate: Optional[float]
    status: str
    invited_email: Optional[str]
    invitation_sent_at: Optional[datetime]
    invitation_accepted_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    # Détails du membre (si accepté)
    member_email: Optional[str]
    member_first_name: Optional[str]
    member_last_name: Optional[str]
    member_role: Optional[str]

class TeamStatsResponse(BaseModel):
    """Statistiques de l'équipe"""
    total_members: int
    active_members: int
    pending_invitations: int
    members_by_role: Dict[str, int]
    team_limit: Optional[int]
    can_add_member: bool
    available_slots: Optional[int]

# ============================================
# HELPER FUNCTIONS
# ============================================

async def check_can_add_team_member(company_id: str) -> bool:
    """Vérifie si l'entreprise peut ajouter un membre"""
    try:
        response = supabase.rpc("check_subscription_limit", {
            "p_user_id": company_id,
            "p_limit_type": "team_members"
        }).execute()

        return response.data if response.data is not None else False
    except Exception as e:
        print(f"Error checking team limit: {e}")
        return False

async def get_team_member_count(company_id: str) -> int:
    """Compte le nombre de membres actifs dans l'équipe"""
    try:
        response = supabase.from_("team_members") \
            .select("id", count="exact") \
            .eq("company_id", company_id) \
            .in_("status", ["active", "pending_invitation"]) \
            .execute()

        return response.count if response.count else 0
    except Exception as e:
        print(f"Error counting team members: {e}")
        return 0

async def update_subscription_team_count(company_id: str):
    """Met à jour le compteur de membres dans la table subscriptions"""
    try:
        count = await get_team_member_count(company_id)

        supabase.from_("subscriptions") \
            .update({"current_team_members": count}) \
            .eq("user_id", company_id) \
            .in_("status", ["active", "trialing"]) \
            .execute()
    except Exception as e:
        print(f"Error updating team count: {e}")

async def send_invitation_email(email: str, company_name: str, token: str):
    """Envoie l'email d'invitation (à implémenter avec votre service email)"""
    # TODO: Intégrer avec votre service d'envoi d'emails
    invitation_link = f"https://shareyoursales.ma/accept-invitation?token={token}"

    print(f"""
    ==============================================
    INVITATION EMAIL
    ==============================================
    To: {email}
    Subject: Invitation à rejoindre l'équipe {company_name}

    Bonjour,

    {company_name} vous invite à rejoindre son équipe sur ShareYourSales.

    Cliquez sur le lien ci-dessous pour accepter l'invitation:
    {invitation_link}

    Ce lien est valide pendant 7 jours.

    Cordialement,
    L'équipe ShareYourSales
    ==============================================
    """)

# ============================================
# ENDPOINTS - TEAM MEMBERS
# ============================================

@router.get("/members", response_model=List[TeamMemberResponse])
async def get_team_members(
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Liste les membres de l'équipe de l'entreprise

    Filtres:
    - status: active, inactive, pending_invitation
    """
    try:
        # Seules les entreprises peuvent avoir une équipe
        if current_user.get("role") not in ["merchant", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only companies can manage teams"
            )

        company_id = current_user["id"]

        # Récupérer les membres depuis la vue
        query = supabase.from_("v_team_members_details") \
            .select("*") \
            .eq("company_id", company_id)

        if status_filter:
            query = query.eq("status", status_filter)

        response = query.order("created_at", desc=True).execute()

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching team members: {str(e)}"
        )

@router.get("/members/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Détails d'un membre d'équipe spécifique"""
    try:
        company_id = current_user["id"]

        response = supabase.from_("v_team_members_details") \
            .select("*") \
            .eq("company_id", company_id) \
            .eq("id", member_id) \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Team member not found")

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching team member: {str(e)}"
        )

@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_team_member(
    request: InviteTeamMemberRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Inviter un nouveau membre à rejoindre l'équipe

    Process:
    1. Vérifie la limite du plan d'abonnement
    2. Génère un token d'invitation unique
    3. Crée l'entrée dans team_members (status: pending_invitation)
    4. Envoie l'email d'invitation
    5. Met à jour le compteur dans subscriptions

    Restrictions:
    - Seules les entreprises peuvent inviter
    - Respecte la limite du plan (Small: 2, Medium: 10, Large: 30)
    """
    try:
        # Vérifier que c'est une entreprise
        if current_user.get("role") not in ["merchant", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only companies can invite team members"
            )

        company_id = current_user["id"]

        # Vérifier la limite du plan
        can_add = await check_can_add_team_member(company_id)
        if not can_add:
            raise HTTPException(
                status_code=403,
                detail="Team member limit reached. Please upgrade your plan."
            )

        # Vérifier que l'email n'est pas déjà dans l'équipe
        existing = supabase.from_("team_members") \
            .select("id") \
            .eq("company_id", company_id) \
            .eq("invited_email", request.email) \
            .in_("status", ["active", "pending_invitation"]) \
            .execute()

        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=400,
                detail="This email is already in your team"
            )

        # Générer le token d'invitation
        invitation_token = secrets.token_urlsafe(32)

        # Créer l'invitation
        team_member_data = {
            "company_id": company_id,
            "team_role": request.team_role,
            "can_view_all_sales": request.can_view_all_sales,
            "can_manage_products": request.can_manage_products,
            "custom_commission_rate": request.custom_commission_rate,
            "status": "pending_invitation",
            "invited_email": request.email,
            "invitation_token": invitation_token,
            "invitation_sent_at": datetime.now().isoformat(),
            "notes": request.notes
        }

        response = supabase.from_("team_members") \
            .insert(team_member_data) \
            .execute()

        # Mettre à jour le compteur
        await update_subscription_team_count(company_id)

        # Envoyer l'email en arrière-plan
        company_name = current_user.get("first_name", "Une entreprise")
        background_tasks.add_task(
            send_invitation_email,
            request.email,
            company_name,
            invitation_token
        )

        return {
            "success": True,
            "message": f"Invitation sent to {request.email}",
            "team_member": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inviting team member: {str(e)}"
        )

@router.post("/accept-invitation/{token}")
async def accept_invitation(
    token: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Accepter une invitation à rejoindre une équipe

    Process:
    1. Vérifie que le token est valide
    2. Vérifie que l'email correspond à l'utilisateur connecté
    3. Met à jour member_id et status
    4. Marque la date d'acceptation
    """
    try:
        # Récupérer l'invitation
        response = supabase.from_("team_members") \
            .select("*") \
            .eq("invitation_token", token) \
            .eq("status", "pending_invitation") \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Invitation not found or already accepted"
            )

        invitation = response.data

        # Vérifier que l'email correspond
        if invitation["invited_email"] != current_user["email"]:
            raise HTTPException(
                status_code=403,
                detail="This invitation was sent to a different email address"
            )

        # Vérifier que l'invitation n'est pas expirée (7 jours)
        invitation_date = datetime.fromisoformat(invitation["invitation_sent_at"].replace("Z", "+00:00"))
        if datetime.now(invitation_date.tzinfo) > invitation_date + timedelta(days=7):
            raise HTTPException(
                status_code=400,
                detail="This invitation has expired"
            )

        # Accepter l'invitation
        supabase.from_("team_members") \
            .update({
                "member_id": current_user["id"],
                "status": "active",
                "invitation_accepted_at": datetime.now().isoformat(),
                "invitation_token": None  # Invalider le token
            }) \
            .eq("id", invitation["id"]) \
            .execute()

        return {
            "success": True,
            "message": "Invitation accepted successfully",
            "company_id": invitation["company_id"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error accepting invitation: {str(e)}"
        )

@router.patch("/members/{member_id}")
async def update_team_member(
    member_id: str,
    request: UpdateTeamMemberRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Mettre à jour les permissions/paramètres d'un membre d'équipe

    Champs modifiables:
    - team_role (commercial, influencer, manager)
    - can_view_all_sales
    - can_manage_products
    - custom_commission_rate
    - status (active, inactive)
    - notes
    """
    try:
        company_id = current_user["id"]

        # Vérifier que le membre existe et appartient à cette entreprise
        existing = supabase.from_("team_members") \
            .select("*") \
            .eq("id", member_id) \
            .eq("company_id", company_id) \
            .single() \
            .execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="Team member not found")

        # Préparer les données de mise à jour
        update_data = {}
        if request.team_role is not None:
            update_data["team_role"] = request.team_role
        if request.can_view_all_sales is not None:
            update_data["can_view_all_sales"] = request.can_view_all_sales
        if request.can_manage_products is not None:
            update_data["can_manage_products"] = request.can_manage_products
        if request.custom_commission_rate is not None:
            update_data["custom_commission_rate"] = request.custom_commission_rate
        if request.status is not None:
            update_data["status"] = request.status
        if request.notes is not None:
            update_data["notes"] = request.notes

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Mettre à jour
        response = supabase.from_("team_members") \
            .update(update_data) \
            .eq("id", member_id) \
            .execute()

        return {
            "success": True,
            "message": "Team member updated successfully",
            "team_member": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating team member: {str(e)}"
        )

@router.delete("/members/{member_id}")
async def remove_team_member(
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retirer un membre de l'équipe

    Note: Cette action est irréversible.
    Les liens affiliés créés restent actifs mais ne peuvent plus être gérés.
    """
    try:
        company_id = current_user["id"]

        # Vérifier que le membre existe
        existing = supabase.from_("team_members") \
            .select("*") \
            .eq("id", member_id) \
            .eq("company_id", company_id) \
            .single() \
            .execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="Team member not found")

        # Supprimer le membre
        supabase.from_("team_members") \
            .delete() \
            .eq("id", member_id) \
            .execute()

        # Mettre à jour le compteur
        await update_subscription_team_count(company_id)

        return {
            "success": True,
            "message": "Team member removed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error removing team member: {str(e)}"
        )

@router.post("/members/{member_id}/resend-invitation")
async def resend_invitation(
    member_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Renvoyer l'email d'invitation à un membre en attente"""
    try:
        company_id = current_user["id"]

        # Récupérer le membre
        response = supabase.from_("team_members") \
            .select("*") \
            .eq("id", member_id) \
            .eq("company_id", company_id) \
            .eq("status", "pending_invitation") \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Pending invitation not found"
            )

        member = response.data

        # Générer un nouveau token
        new_token = secrets.token_urlsafe(32)

        # Mettre à jour
        supabase.from_("team_members") \
            .update({
                "invitation_token": new_token,
                "invitation_sent_at": datetime.now().isoformat()
            }) \
            .eq("id", member_id) \
            .execute()

        # Envoyer l'email
        company_name = current_user.get("first_name", "Une entreprise")
        background_tasks.add_task(
            send_invitation_email,
            member["invited_email"],
            company_name,
            new_token
        )

        return {
            "success": True,
            "message": f"Invitation resent to {member['invited_email']}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resending invitation: {str(e)}"
        )

# ============================================
# ENDPOINTS - TEAM STATS
# ============================================

@router.get("/stats", response_model=TeamStatsResponse)
async def get_team_stats(current_user: dict = Depends(get_current_user)):
    """
    Statistiques de l'équipe

    Retourne:
    - Nombre total de membres
    - Membres actifs vs invitations en attente
    - Répartition par rôle
    - Limite du plan
    - Capacité à ajouter des membres
    """
    try:
        company_id = current_user["id"]

        # Récupérer tous les membres
        response = supabase.from_("team_members") \
            .select("*") \
            .eq("company_id", company_id) \
            .execute()

        members = response.data

        # Compter par statut
        active_members = len([m for m in members if m["status"] == "active"])
        pending_invitations = len([m for m in members if m["status"] == "pending_invitation"])

        # Compter par rôle
        members_by_role = {}
        for member in members:
            if member["status"] != "inactive":
                role = member["team_role"]
                members_by_role[role] = members_by_role.get(role, 0) + 1

        # Récupérer la limite du plan
        subscription_response = supabase.from_("v_active_subscriptions") \
            .select("plan_max_team_members") \
            .eq("user_id", company_id) \
            .single() \
            .execute()

        team_limit = None
        available_slots = None
        can_add = False

        if subscription_response.data:
            team_limit = subscription_response.data.get("plan_max_team_members")
            if team_limit is not None:
                available_slots = team_limit - len(members)
            can_add = await check_can_add_team_member(company_id)

        return {
            "total_members": len(members),
            "active_members": active_members,
            "pending_invitations": pending_invitations,
            "members_by_role": members_by_role,
            "team_limit": team_limit,
            "can_add_member": can_add,
            "available_slots": available_slots
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching team stats: {str(e)}"
        )

# ============================================
# ENDPOINTS - MY TEAMS (For Team Members)
# ============================================

@router.get("/my-teams")
async def get_my_teams(current_user: dict = Depends(get_current_user)):
    """
    Liste les équipes dont l'utilisateur est membre

    Utilisé par les commerciaux/influenceurs pour voir
    les entreprises qui les ont ajoutés à leur équipe
    """
    try:
        user_id = current_user["id"]

        response = supabase.from_("v_team_members_details") \
            .select("*") \
            .eq("member_id", user_id) \
            .eq("status", "active") \
            .execute()

        return {
            "teams": response.data,
            "count": len(response.data)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching teams: {str(e)}"
        )

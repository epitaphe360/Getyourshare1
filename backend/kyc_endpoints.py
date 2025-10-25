"""
API Endpoints KYC - Know Your Customer
Vérification d'identité et conformité réglementaire

Endpoints:
- POST /api/kyc/submit - Soumettre KYC complet
- GET /api/kyc/status - Statut KYC utilisateur
- POST /api/kyc/upload-document - Upload document
- GET /api/kyc/required-documents - Liste documents requis
- POST /api/kyc/verify/{kyc_id} - Vérifier KYC (admin)
- POST /api/kyc/approve/{kyc_id} - Approuver KYC (admin)
- POST /api/kyc/reject/{kyc_id} - Rejeter KYC (admin)
- GET /api/kyc/pending - Liste KYC en attente (admin)
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
import structlog

from auth import get_current_user, require_role
from services.kyc_service import (
    KYCService,
    DocumentType,
    KYCStatus,
    RejectionReason
)

router = APIRouter(prefix="/api/kyc", tags=["KYC"])
logger = structlog.get_logger()

kyc_service = KYCService()


# ============================================
# PYDANTIC MODELS
# ============================================

class PersonalInfoRequest(BaseModel):
    """Informations personnelles"""
    first_name: str = Field(..., min_length=2, max_length=100, description="Prénom")
    last_name: str = Field(..., min_length=2, max_length=100, description="Nom")
    date_of_birth: str = Field(..., description="Date de naissance (YYYY-MM-DD)")
    nationality: str = Field(default="MA", description="Code pays ISO (MA pour Maroc)")
    phone: str = Field(..., description="Téléphone (format: +212612345678)")
    address: str = Field(..., min_length=10, max_length=500, description="Adresse complète")
    city: str = Field(..., min_length=2, max_length=100, description="Ville")
    postal_code: Optional[str] = Field(None, max_length=10, description="Code postal")

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Mohammed",
                "last_name": "Alami",
                "date_of_birth": "1990-01-15",
                "nationality": "MA",
                "phone": "+212612345678",
                "address": "123 Avenue Mohammed V",
                "city": "Casablanca",
                "postal_code": "20000"
            }
        }


class IdentityDocumentRequest(BaseModel):
    """Document d'identité"""
    document_type: str = Field(..., description="Type: cin ou passport")
    document_number: str = Field(..., min_length=5, max_length=20, description="Numéro du document")
    expiry_date: str = Field(..., description="Date d'expiration (YYYY-MM-DD)")
    document_front_url: str = Field(..., description="URL du recto (upload d'abord)")
    document_back_url: Optional[str] = Field(None, description="URL du verso (CIN uniquement)")
    selfie_url: Optional[str] = Field(None, description="URL du selfie avec document")

    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "cin",
                "document_number": "AB123456",
                "expiry_date": "2028-12-31",
                "document_front_url": "/uploads/documents/cin_front_abc123.jpg",
                "document_back_url": "/uploads/documents/cin_back_abc123.jpg",
                "selfie_url": "/uploads/documents/selfie_abc123.jpg"
            }
        }


class CompanyDocumentsRequest(BaseModel):
    """Documents d'entreprise (merchants)"""
    company_name: str = Field(..., min_length=2, max_length=255, description="Raison sociale")
    legal_form: str = Field(..., description="Forme juridique (SARL, SA, Auto-entrepreneur, etc.)")
    ice: str = Field(..., description="ICE (15 chiffres)")
    ice_document_url: str = Field(..., description="URL du certificat ICE")
    rc: str = Field(..., description="Numéro RC")
    rc_document_url: str = Field(..., description="URL du RC")
    tva: Optional[str] = Field(None, description="Numéro TVA (optionnel)")
    tva_document_url: Optional[str] = Field(None, description="URL du certificat TVA")
    statuts_url: Optional[str] = Field(None, description="URL des statuts")
    creation_date: Optional[str] = Field(None, description="Date de création (YYYY-MM-DD)")
    address: str = Field(..., min_length=10, max_length=500, description="Adresse du siège")
    city: str = Field(..., min_length=2, max_length=100, description="Ville")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "ShareYourSales SARL",
                "legal_form": "SARL",
                "ice": "001234567891234",
                "ice_document_url": "/uploads/documents/ice_abc123.pdf",
                "rc": "123456",
                "rc_document_url": "/uploads/documents/rc_abc123.pdf",
                "tva": "12345678",
                "tva_document_url": "/uploads/documents/tva_abc123.pdf",
                "address": "Boulevard Mohammed VI, Technopark",
                "city": "Casablanca"
            }
        }


class BankAccountRequest(BaseModel):
    """Informations bancaires"""
    bank_name: str = Field(..., min_length=2, max_length=100, description="Nom de la banque")
    account_holder_name: str = Field(..., min_length=2, max_length=255, description="Titulaire du compte")
    iban: str = Field(..., description="IBAN marocain (MA + 26 chiffres)")
    rib_document_url: str = Field(..., description="URL du RIB")

    class Config:
        json_schema_extra = {
            "example": {
                "bank_name": "Attijariwafa Bank",
                "account_holder_name": "Mohammed Alami",
                "iban": "MA12345678901234567890123456",
                "rib_document_url": "/uploads/documents/rib_abc123.pdf"
            }
        }


class KYCSubmissionRequest(BaseModel):
    """Soumission KYC complète"""
    personal_info: PersonalInfoRequest
    identity_document: IdentityDocumentRequest
    company_documents: Optional[CompanyDocumentsRequest] = None
    bank_account: BankAccountRequest


class KYCReviewRequest(BaseModel):
    """Review KYC par admin"""
    status: str = Field(..., pattern="^(approved|rejected)$", description="approved ou rejected")
    rejection_reason: Optional[str] = Field(None, description="Raison du rejet si rejected")
    rejection_comment: Optional[str] = Field(None, max_length=1000, description="Commentaire détaillé")
    notes: Optional[str] = Field(None, max_length=2000, description="Notes internes")


class DocumentUploadResponse(BaseModel):
    """Réponse upload document"""
    success: bool
    document_url: str
    document_type: str
    file_size: int
    uploaded_at: str


class KYCStatusResponse(BaseModel):
    """Statut KYC"""
    user_id: str
    status: str
    submitted_at: Optional[str] = None
    reviewed_at: Optional[str] = None
    reviewer_id: Optional[str] = None
    documents_uploaded: List[str] = []
    missing_documents: List[str] = []
    rejection_reason: Optional[str] = None
    rejection_comment: Optional[str] = None
    can_resubmit: bool = True


# ============================================
# ENDPOINTS - USER
# ============================================

@router.post("/submit", status_code=201, response_model=dict)
async def submit_kyc(
    submission: KYCSubmissionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Soumettre KYC complet

    **Requis:**
    - Informations personnelles complètes
    - Document d'identité (CIN ou Passeport)
    - Documents entreprise (si merchant)
    - Compte bancaire avec RIB

    **Process:**
    1. Upload tous les documents d'abord (via /upload-document)
    2. Soumettre le KYC avec les URLs des documents
    3. Le KYC sera vérifié par un admin sous 24-48h
    """
    user_id = current_user.get("id")
    user_type = current_user.get("role")  # merchant ou influencer

    try:
        logger.info("kyc_submission_started", user_id=user_id, user_type=user_type)

        # Validation documents entreprise pour merchants
        if user_type == "merchant" and not submission.company_documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Documents d'entreprise obligatoires pour les marchands (ICE, RC, etc.)"
            )

        # Validation avec le service KYC
        validation_result = await kyc_service.validate_submission({
            "user_id": user_id,
            "user_type": user_type,
            **submission.dict()
        })

        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Validation échouée",
                    "errors": validation_result["errors"]
                }
            )

        # Sauvegarder dans DB
        kyc_id = await kyc_service.create_submission(
            user_id=user_id,
            user_type=user_type,
            data=submission.dict(),
            ip_address=None  # TODO: Get from request
        )

        logger.info("kyc_submission_created", user_id=user_id, kyc_id=kyc_id)

        return {
            "success": True,
            "kyc_id": kyc_id,
            "status": "submitted",
            "message": "KYC soumis avec succès. Vérification sous 24-48h.",
            "warnings": validation_result.get("warnings", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("kyc_submission_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la soumission du KYC"
        )


@router.get("/status", response_model=KYCStatusResponse)
async def get_kyc_status(current_user: dict = Depends(get_current_user)):
    """
    Obtenir le statut KYC de l'utilisateur actuel

    **Statuts possibles:**
    - `pending`: Pas encore soumis
    - `submitted`: Soumis, en attente de vérification
    - `under_review`: En cours de vérification
    - `approved`: Approuvé ✅
    - `rejected`: Rejeté ❌
    - `expired`: Documents expirés
    """
    user_id = current_user.get("id")

    try:
        kyc_status = await kyc_service.get_user_kyc_status(user_id)

        return KYCStatusResponse(**kyc_status)

    except Exception as e:
        logger.error("kyc_status_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du statut KYC"
        )


@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="Document à uploader (max 10MB)"),
    document_type: str = Form(..., description="Type: cin, passport, ice, rc, tva, rib, selfie, etc."),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload un document KYC

    **Types acceptés:**
    - `cin`: Carte d'Identité Nationale
    - `passport`: Passeport
    - `ice`: Certificat ICE
    - `rc`: Registre de Commerce
    - `tva`: Certificat TVA
    - `rib`: Relevé d'Identité Bancaire
    - `selfie`: Photo selfie avec CIN
    - `proof_address`: Justificatif de domicile

    **Formats acceptés:** JPG, PNG, PDF (max 10MB)

    **Important:** Uploadez d'abord tous les documents, puis soumettez le KYC avec les URLs retournées
    """
    user_id = current_user.get("id")

    try:
        # Validation type de document
        valid_types = ["cin", "passport", "ice", "rc", "tva", "rib", "selfie", "proof_address", "statuts"]
        if document_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Type de document invalide. Types acceptés: {', '.join(valid_types)}"
            )

        # Validation fichier
        if not file.content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type de fichier non reconnu"
            )

        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Format non accepté. Formats acceptés: JPG, PNG, PDF"
            )

        # Taille max 10MB
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fichier trop volumineux (max 10MB)"
            )

        # Upload vers storage
        document_url = await kyc_service.upload_document(
            user_id=user_id,
            document_type=document_type,
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )

        logger.info("document_uploaded", user_id=user_id, document_type=document_type, size=file_size)

        return DocumentUploadResponse(
            success=True,
            document_url=document_url,
            document_type=document_type,
            file_size=file_size,
            uploaded_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("document_upload_error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'upload du document"
        )


@router.get("/required-documents", response_model=dict)
async def get_required_documents(current_user: dict = Depends(get_current_user)):
    """
    Liste des documents requis selon le type d'utilisateur

    **Influenceur:**
    - CIN ou Passeport (recto/verso)
    - Selfie avec CIN
    - RIB

    **Marchand:**
    - CIN ou Passeport (recto/verso)
    - Selfie avec CIN
    - RIB
    - Certificat ICE
    - Registre de Commerce (RC)
    - Certificat TVA (recommandé)
    - Statuts de la société (recommandé)
    """
    user_type = current_user.get("role")

    required = [
        {"type": "cin", "name": "Carte d'Identité Nationale", "description": "Recto et verso", "required": True},
        {"type": "selfie", "name": "Selfie avec CIN", "description": "Photo de vous tenant votre CIN", "required": True},
        {"type": "rib", "name": "Relevé d'Identité Bancaire", "description": "RIB de votre compte", "required": True},
    ]

    if user_type == "merchant":
        required.extend([
            {"type": "ice", "name": "Certificat ICE", "description": "Identifiant Commun de l'Entreprise", "required": True},
            {"type": "rc", "name": "Registre de Commerce", "description": "Extrait RC", "required": True},
            {"type": "tva", "name": "Certificat TVA", "description": "Numéro de TVA", "required": False},
            {"type": "statuts", "name": "Statuts de la société", "description": "Statuts signés", "required": False},
        ])

    return {
        "user_type": user_type,
        "required_documents": required,
        "total_required": sum(1 for doc in required if doc["required"]),
        "total_optional": sum(1 for doc in required if not doc["required"])
    }


# ============================================
# ENDPOINTS - ADMIN
# ============================================

@router.get("/pending", response_model=List[dict])
async def get_pending_kyc(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Liste des KYC en attente de vérification (ADMIN ONLY)

    Retourne tous les KYC avec statut `submitted` ou `under_review`
    """
    try:
        pending_kyc = await kyc_service.get_pending_submissions(page=page, limit=limit)

        return pending_kyc

    except Exception as e:
        logger.error("pending_kyc_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des KYC en attente"
        )


@router.get("/{kyc_id}", response_model=dict)
async def get_kyc_details(
    kyc_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Détails complets d'un KYC (ADMIN ONLY)

    Inclut tous les documents et informations soumises
    """
    try:
        kyc_details = await kyc_service.get_submission_details(kyc_id)

        if not kyc_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KYC non trouvé"
            )

        return kyc_details

    except HTTPException:
        raise
    except Exception as e:
        logger.error("kyc_details_error", kyc_id=kyc_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des détails KYC"
        )


@router.post("/approve/{kyc_id}", response_model=dict)
async def approve_kyc(
    kyc_id: str,
    review: KYCReviewRequest,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Approuver un KYC (ADMIN ONLY)

    **Effets:**
    - Statut → `approved`
    - Utilisateur peut utiliser toutes les fonctionnalités
    - Email de confirmation envoyé
    """
    if review.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisez cet endpoint uniquement pour approuver"
        )

    reviewer_id = current_user.get("id")

    try:
        success = await kyc_service.approve_kyc(
            kyc_id=kyc_id,
            reviewer_id=reviewer_id,
            notes=review.notes
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KYC non trouvé"
            )

        logger.info("kyc_approved", kyc_id=kyc_id, reviewer_id=reviewer_id)

        return {
            "success": True,
            "kyc_id": kyc_id,
            "status": "approved",
            "message": "KYC approuvé avec succès"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("kyc_approve_error", kyc_id=kyc_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'approbation du KYC"
        )


@router.post("/reject/{kyc_id}", response_model=dict)
async def reject_kyc(
    kyc_id: str,
    review: KYCReviewRequest,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Rejeter un KYC (ADMIN ONLY)

    **Requis:**
    - `rejection_reason`: Raison du rejet
    - `rejection_comment`: Commentaire détaillé

    **Effets:**
    - Statut → `rejected`
    - Utilisateur peut resoummettre après correction
    - Email avec raison du rejet envoyé
    """
    if review.status != "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisez cet endpoint uniquement pour rejeter"
        )

    if not review.rejection_reason or not review.rejection_comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Raison et commentaire obligatoires pour un rejet"
        )

    reviewer_id = current_user.get("id")

    try:
        success = await kyc_service.reject_kyc(
            kyc_id=kyc_id,
            reviewer_id=reviewer_id,
            reason=review.rejection_reason,
            comment=review.rejection_comment,
            notes=review.notes
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KYC non trouvé"
            )

        logger.info("kyc_rejected", kyc_id=kyc_id, reviewer_id=reviewer_id, reason=review.rejection_reason)

        return {
            "success": True,
            "kyc_id": kyc_id,
            "status": "rejected",
            "message": "KYC rejeté. L'utilisateur peut resoummettre après corrections."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("kyc_reject_error", kyc_id=kyc_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du rejet du KYC"
        )

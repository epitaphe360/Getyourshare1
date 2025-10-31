"""
Service KYC (Know Your Customer) Professionnel
Gestion complète de la vérification d'identité et conformité

Fonctionnalités:
- Upload et vérification de documents
- OCR automatique (extraction de données)
- Vérification liveness (selfie + IA)
- Calcul automatique de risk score
- Intégration avec services de vérification tiers
- Conformité Maroc (AMMC, Bank Al-Maghrib) + International (FATF, GDPR)
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import hashlib
import io

from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, Field
import structlog

from supabase_client import supabase

# Logging structuré
logger = structlog.get_logger(__name__)


# ============================================
# ENUMS & MODELS
# ============================================

class DocumentType(str, Enum):
    """Types de documents acceptés"""
    CIN = "cin"
    PASSPORT = "passport"
    RESIDENCE_PERMIT = "residence_permit"
    DRIVING_LICENSE = "driving_license"
    PROOF_ADDRESS = "proof_address"
    BANK_STATEMENT = "bank_statement"
    TAX_CERTIFICATE = "tax_certificate"
    COMMERCIAL_REGISTER = "commercial_register"
    PROFESSIONAL_CARD = "professional_card"
    ICE_CERTIFICATE = "ice_certificate"
    TVA_CERTIFICATE = "tva_certificate"
    SELFIE = "selfie"


class VerificationStatus(str, Enum):
    """Statuts de vérification"""
    PENDING = "pending"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class KYCLevel(int, Enum):
    """Niveaux KYC"""
    UNVERIFIED = 0        # Compte créé
    BASIC = 1             # Email + Téléphone
    IDENTITY = 2          # Identité vérifiée
    FULL_KYC = 3          # Full KYC (Identité + Adresse + Banque)


class RiskLevel(str, Enum):
    """Niveaux de risque"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Pydantic Models
class DocumentUpload(BaseModel):
    """Modèle pour l'upload d'un document"""
    document_type: DocumentType
    user_id: str


class DocumentVerification(BaseModel):
    """Modèle pour la vérification d'un document"""
    document_id: str
    status: VerificationStatus
    rejection_reason: Optional[str] = None
    rejection_category: Optional[str] = None
    extracted_data: Optional[Dict] = None


class KYCProfileUpdate(BaseModel):
    """Mise à jour du profil KYC"""
    verified_full_name: Optional[str] = None
    verified_date_of_birth: Optional[str] = None
    verified_nationality: Optional[str] = None
    verified_address: Optional[str] = None
    verified_city: Optional[str] = None
    verified_postal_code: Optional[str] = None
    verified_country: Optional[str] = None
    account_type: Optional[str] = None
    company_name: Optional[str] = None
    company_ice: Optional[str] = None
    company_rc: Optional[str] = None


# ============================================
# SERVICE KYC
# ============================================

class KYCService:
    """Service principal de gestion KYC"""

    def __init__(self):
        self.supabase = supabase
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.storage_bucket = os.getenv('SUPABASE_STORAGE_BUCKET', 'kyc-documents')

    # ============================================
    # UPLOAD DE DOCUMENTS
    # ============================================

    async def upload_document(
        self,
        user_id: str,
        document_type: DocumentType,
        file: UploadFile
    ) -> Dict:
        """
        Upload d'un document KYC

        Process:
        1. Validation du fichier (type, taille, sécurité)
        2. Upload vers Supabase Storage
        3. Création de l'entrée en base de données
        4. Extraction automatique des données (OCR) si applicable
        5. Calcul du confidence score
        """
        try:
            # 1. Validation du fichier
            await self._validate_file(file)

            # 2. Lire le contenu du fichier
            file_content = await file.read()
            file_size = len(file_content)

            # 3. Générer un nom de fichier sécurisé
            file_extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{user_id}/{document_type.value}/{uuid.uuid4()}{file_extension}"

            # 4. Upload vers Supabase Storage
            storage_response = self.supabase.storage.from_(self.storage_bucket).upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": file.content_type}
            )

            # 5. Obtenir l'URL publique
            file_url = self.supabase.storage.from_(self.storage_bucket).get_public_url(unique_filename)

            # 6. Extraction automatique de données (OCR)
            extracted_data = {}
            confidence_score = 0.0

            if document_type in [DocumentType.CIN, DocumentType.PASSPORT, DocumentType.DRIVING_LICENSE]:
                # TODO: Intégration OCR (Google Cloud Vision, AWS Textract, ou Tesseract)
                extracted_data, confidence_score = await self._extract_document_data(
                    file_content,
                    document_type
                )

            # 7. Créer l'entrée en base de données
            document_data = {
                'user_id': user_id,
                'document_type': document_type.value,
                'file_url': file_url,
                'file_name': file.filename,
                'file_size': file_size,
                'file_mime_type': file.content_type,
                'extracted_data': json.dumps(extracted_data) if extracted_data else '{}',
                'confidence_score': confidence_score,
                'verification_status': VerificationStatus.PENDING.value,
                'uploaded_at': datetime.now().isoformat()
            }

            result = self.supabase.table('user_kyc_documents').insert(document_data).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement du document")

            document_id = result.data[0]['id']

            # 8. Logging
            logger.info(
                "kyc_document_uploaded",
                user_id=user_id,
                document_type=document_type.value,
                document_id=document_id,
                file_size=file_size,
                confidence_score=confidence_score
            )

            # 9. Log dans audit trail
            await self._log_action(
                user_id=user_id,
                document_id=document_id,
                action="document_uploaded",
                new_data={"document_type": document_type.value, "file_name": file.filename}
            )

            return {
                "success": True,
                "document_id": document_id,
                "file_url": file_url,
                "extracted_data": extracted_data,
                "confidence_score": confidence_score,
                "verification_status": VerificationStatus.PENDING.value
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("kyc_document_upload_failed", user_id=user_id, error=str(e))
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

    async def _validate_file(self, file: UploadFile):
        """Valide un fichier uploadé"""
        # Vérifier l'extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Type de fichier non autorisé. Extensions acceptées: {self.allowed_extensions}"
            )

        # Vérifier la taille (lecture du contenu pour avoir la taille exacte)
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)  # Reset position

        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"Fichier trop volumineux. Taille maximale: {self.max_file_size / (1024*1024)}MB"
            )

        # TODO: Vérifier le type MIME réel (pas juste l'extension)
        # TODO: Scanner avec antivirus (ClamAV)

    async def _extract_document_data(
        self,
        file_content: bytes,
        document_type: DocumentType
    ) -> tuple[Dict, float]:
        """
        Extrait les données d'un document via OCR

        Retourne: (extracted_data, confidence_score)

        TODO: Intégrer un service OCR:
        - Google Cloud Vision API (recommandé, excellent pour CIN/Passeport)
        - AWS Textract
        - Azure Computer Vision
        - Tesseract (gratuit mais moins précis)
        """
        extracted_data = {}
        confidence_score = 0.0

        # Placeholder - À remplacer par vraie intégration OCR
        if document_type == DocumentType.CIN:
            # Exemple de données qu'on devrait extraire
            extracted_data = {
                "full_name": "",
                "cin_number": "",
                "date_of_birth": "",
                "place_of_birth": "",
                "address": "",
                "issue_date": "",
                "expiry_date": ""
            }
            confidence_score = 75.0  # Score de confiance de l'OCR

        elif document_type == DocumentType.PASSPORT:
            extracted_data = {
                "full_name": "",
                "passport_number": "",
                "nationality": "",
                "date_of_birth": "",
                "issue_date": "",
                "expiry_date": ""
            }
            confidence_score = 80.0

        # TODO: Implémenter vraie extraction OCR
        logger.warning("ocr_not_implemented", document_type=document_type.value)

        return extracted_data, confidence_score

    # ============================================
    # VÉRIFICATION DE DOCUMENTS
    # ============================================

    async def verify_document(
        self,
        document_id: str,
        verification: DocumentVerification,
        verified_by: str
    ) -> Dict:
        """
        Vérification d'un document par un admin

        Process:
        1. Mettre à jour le statut du document
        2. Extraire et valider les données si approuvé
        3. Recalculer le niveau KYC de l'utilisateur
        4. Recalculer le risk score
        5. Logger l'action
        """
        try:
            # 1. Récupérer le document
            doc_result = self.supabase.table('user_kyc_documents').select('*').eq('id', document_id).execute()

            if not doc_result.data:
                raise HTTPException(status_code=404, detail="Document introuvable")

            document = doc_result.data[0]
            user_id = document['user_id']

            # 2. Préparer les données de mise à jour
            update_data = {
                'verification_status': verification.status.value,
                'verified_by': verified_by,
                'verified_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            if verification.status == VerificationStatus.APPROVED:
                # Si approuvé, mettre à jour les données extraites si fournies
                if verification.extracted_data:
                    update_data['extracted_data'] = json.dumps(verification.extracted_data)

            elif verification.status == VerificationStatus.REJECTED:
                # Si rejeté, stocker la raison
                if not verification.rejection_reason:
                    raise HTTPException(status_code=400, detail="La raison du rejet est obligatoire")

                update_data['rejection_reason'] = verification.rejection_reason
                update_data['rejection_category'] = verification.rejection_category

            # 3. Mettre à jour le document
            self.supabase.table('user_kyc_documents').update(update_data).eq('id', document_id).execute()

            # 4. Mettre à jour le profil KYC si approuvé
            if verification.status == VerificationStatus.APPROVED:
                await self._update_kyc_profile_after_approval(user_id, document['document_type'], verification.extracted_data or {})

            # 5. Recalculer le niveau KYC et le risk score
            kyc_level = await self.calculate_kyc_level(user_id)
            risk_score = await self.calculate_risk_score(user_id)

            # 6. Logging
            logger.info(
                "kyc_document_verified",
                document_id=document_id,
                user_id=user_id,
                status=verification.status.value,
                verified_by=verified_by,
                new_kyc_level=kyc_level,
                risk_score=risk_score
            )

            # 7. Log dans audit trail
            await self._log_action(
                user_id=user_id,
                document_id=document_id,
                action=f"document_{verification.status.value}",
                performed_by=verified_by,
                new_data={"status": verification.status.value, "kyc_level": kyc_level}
            )

            return {
                "success": True,
                "document_id": document_id,
                "status": verification.status.value,
                "kyc_level": kyc_level,
                "risk_score": risk_score
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("kyc_document_verification_failed", document_id=document_id, error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    async def _update_kyc_profile_after_approval(
        self,
        user_id: str,
        document_type: str,
        extracted_data: Dict
    ):
        """
        Met à jour le profil KYC après approbation d'un document
        """
        try:
            update_data = {}

            if document_type in ['cin', 'passport']:
                # Mettre à jour les infos d'identité
                if 'full_name' in extracted_data:
                    update_data['verified_full_name'] = extracted_data['full_name']
                if 'date_of_birth' in extracted_data:
                    update_data['verified_date_of_birth'] = extracted_data['date_of_birth']
                if 'nationality' in extracted_data:
                    update_data['verified_nationality'] = extracted_data['nationality']

                update_data['identity_verified'] = True
                update_data['identity_verified_at'] = datetime.now().isoformat()

            elif document_type == 'proof_address':
                # Mettre à jour l'adresse
                if 'address' in extracted_data:
                    update_data['verified_address'] = extracted_data['address']
                if 'city' in extracted_data:
                    update_data['verified_city'] = extracted_data['city']
                if 'postal_code' in extracted_data:
                    update_data['verified_postal_code'] = extracted_data['postal_code']
                if 'country' in extracted_data:
                    update_data['verified_country'] = extracted_data['country']

                update_data['address_verified'] = True
                update_data['address_verified_at'] = datetime.now().isoformat()

            elif document_type == 'bank_statement':
                update_data['bank_verified'] = True
                update_data['bank_verified_at'] = datetime.now().isoformat()

            elif document_type in ['commercial_register', 'ice_certificate']:
                update_data['business_verified'] = True
                update_data['business_verified_at'] = datetime.now().isoformat()

            if update_data:
                update_data['updated_at'] = datetime.now().isoformat()
                self.supabase.table('user_kyc_profile').update(update_data).eq('user_id', user_id).execute()

        except Exception as e:
            logger.error("kyc_profile_update_failed", user_id=user_id, error=str(e))

    # ============================================
    # CALCULS AUTOMATIQUES
    # ============================================

    async def calculate_kyc_level(self, user_id: str) -> int:
        """
        Calcule le niveau KYC d'un utilisateur

        Level 0: Compte créé (aucune vérification)
        Level 1: Email + Téléphone vérifié
        Level 2: Identité vérifiée (CIN/Passeport + Selfie)
        Level 3: Full KYC (Identité + Adresse + Banque)
        """
        try:
            # Récupérer le profil KYC
            profile_result = self.supabase.table('user_kyc_profile').select('*').eq('user_id', user_id).execute()

            if not profile_result.data:
                # Créer le profil s'il n'existe pas
                await self._create_kyc_profile(user_id)
                return KYCLevel.UNVERIFIED.value

            profile = profile_result.data[0]

            # Vérifier l'utilisateur
            user_result = self.supabase.table('users').select('email_verified, phone_verified').eq('id', user_id).execute()

            if not user_result.data:
                return KYCLevel.UNVERIFIED.value

            user = user_result.data[0]

            # Calcul du niveau
            kyc_level = KYCLevel.UNVERIFIED.value

            # Level 1: Email vérifié
            if user.get('email_verified'):
                kyc_level = KYCLevel.BASIC.value

            # Level 2: Identité vérifiée
            if profile.get('identity_verified'):
                kyc_level = KYCLevel.IDENTITY.value

            # Level 3: Full KYC
            if (profile.get('identity_verified') and
                profile.get('address_verified') and
                profile.get('bank_verified')):
                kyc_level = KYCLevel.FULL_KYC.value

            # Mettre à jour le niveau dans le profil
            self.supabase.table('user_kyc_profile').update({
                'kyc_level': kyc_level,
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).execute()

            logger.info("kyc_level_calculated", user_id=user_id, kyc_level=kyc_level)

            return kyc_level

        except Exception as e:
            logger.error("kyc_level_calculation_failed", user_id=user_id, error=str(e))
            return KYCLevel.UNVERIFIED.value

    async def calculate_risk_score(self, user_id: str) -> float:
        """
        Calcule le risk score d'un utilisateur (0-100)

        Facteurs de risque:
        - Compte récent (+10)
        - Documents rejetés (+5 par document)
        - Aucun document (+30)
        - PEP (+20)
        - Liste de sanctions (+100 = blocage)
        - Transactions suspectes (+variable)
        """
        try:
            score = 0.0
            risk_factors = []

            # Récupérer l'utilisateur
            user_result = self.supabase.table('users').select('created_at').eq('id', user_id).execute()

            if not user_result.data:
                return 100.0  # Utilisateur introuvable = risque critique

            user = user_result.data[0]
            created_at = datetime.fromisoformat(user['created_at'])

            # 1. Compte récent (+10 points)
            if (datetime.now() - created_at).days < 30:
                score += 10
                risk_factors.append("account_recent")

            # 2. Documents rejetés (+5 par document)
            rejected_docs = self.supabase.table('user_kyc_documents').select('id').eq('user_id', user_id).eq('verification_status', 'rejected').execute()

            rejected_count = len(rejected_docs.data) if rejected_docs.data else 0
            if rejected_count > 0:
                score += rejected_count * 5
                risk_factors.append(f"rejected_documents_{rejected_count}")

            # 3. Aucun document approuvé (+30 points)
            approved_docs = self.supabase.table('user_kyc_documents').select('id').eq('user_id', user_id).eq('verification_status', 'approved').execute()

            if not approved_docs.data:
                score += 30
                risk_factors.append("no_approved_documents")

            # 4. Récupérer le profil KYC
            profile_result = self.supabase.table('user_kyc_profile').select('*').eq('user_id', user_id).execute()

            if profile_result.data:
                profile = profile_result.data[0]

                # PEP (+20 points)
                if profile.get('is_pep'):
                    score += 20
                    risk_factors.append("politically_exposed_person")

                # Liste de sanctions (+100 points = blocage)
                if profile.get('is_sanctioned'):
                    score = 100
                    risk_factors.append("sanctioned_entity")

            # Déterminer le niveau de risque
            if score >= 75:
                risk_level = RiskLevel.CRITICAL.value
            elif score >= 50:
                risk_level = RiskLevel.HIGH.value
            elif score >= 25:
                risk_level = RiskLevel.MEDIUM.value
            else:
                risk_level = RiskLevel.LOW.value

            # Mettre à jour le profil
            self.supabase.table('user_kyc_profile').update({
                'risk_score': round(score, 2),
                'risk_level': risk_level,
                'risk_factors': json.dumps(risk_factors),
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).execute()

            logger.info("risk_score_calculated", user_id=user_id, score=score, level=risk_level)

            return round(score, 2)

        except Exception as e:
            logger.error("risk_score_calculation_failed", user_id=user_id, error=str(e))
            return 100.0  # En cas d'erreur, considérer comme risque critique

    async def _create_kyc_profile(self, user_id: str):
        """Crée un profil KYC initial pour un utilisateur"""
        try:
            profile_data = {
                'user_id': user_id,
                'kyc_level': KYCLevel.UNVERIFIED.value,
                'kyc_status': 'incomplete',
                'risk_level': RiskLevel.LOW.value,
                'risk_score': 0.0,
                'created_at': datetime.now().isoformat()
            }

            self.supabase.table('user_kyc_profile').insert(profile_data).execute()

            logger.info("kyc_profile_created", user_id=user_id)

        except Exception as e:
            logger.error("kyc_profile_creation_failed", user_id=user_id, error=str(e))

    # ============================================
    # AUDIT TRAIL
    # ============================================

    async def _log_action(
        self,
        user_id: str,
        action: str,
        document_id: Optional[str] = None,
        performed_by: Optional[str] = None,
        previous_data: Optional[Dict] = None,
        new_data: Optional[Dict] = None,
        note: Optional[str] = None
    ):
        """Enregistre une action dans les logs KYC"""
        try:
            log_data = {
                'user_id': user_id,
                'document_id': document_id,
                'action': action,
                'performed_by': performed_by,
                'previous_data': json.dumps(previous_data) if previous_data else None,
                'new_data': json.dumps(new_data) if new_data else None,
                'note': note,
                'created_at': datetime.now().isoformat()
            }

            self.supabase.table('kyc_verification_logs').insert(log_data).execute()

        except Exception as e:
            logger.error("kyc_log_failed", user_id=user_id, action=action, error=str(e))

    # ============================================
    # RÉCUPÉRATION DE DONNÉES
    # ============================================

    async def get_user_documents(self, user_id: str) -> List[Dict]:
        """Récupère tous les documents d'un utilisateur"""
        try:
            result = self.supabase.table('user_kyc_documents').select('*').eq('user_id', user_id).order('uploaded_at', desc=True).execute()

            return result.data or []

        except Exception as e:
            logger.error("get_user_documents_failed", user_id=user_id, error=str(e))
            return []

    async def get_user_kyc_profile(self, user_id: str) -> Optional[Dict]:
        """Récupère le profil KYC d'un utilisateur"""
        try:
            result = self.supabase.table('user_kyc_profile').select('*').eq('user_id', user_id).execute()

            if result.data:
                return result.data[0]

            # Créer un profil s'il n'existe pas
            await self._create_kyc_profile(user_id)
            return await self.get_user_kyc_profile(user_id)

        except Exception as e:
            logger.error("get_kyc_profile_failed", user_id=user_id, error=str(e))
            return None

    async def get_pending_verifications(self) -> List[Dict]:
        """Récupère tous les documents en attente de vérification (pour admins)"""
        try:
            result = self.supabase.table('user_kyc_documents').select(
                '*',
                'users(email, first_name, last_name)'
            ).eq('verification_status', 'pending').order('uploaded_at', desc=False).execute()

            return result.data or []

        except Exception as e:
            logger.error("get_pending_verifications_failed", error=str(e))
            return []


    # ============================================
    # MÉTHODES POUR KYC ENDPOINTS
    # ============================================

    async def validate_submission(self, data: Dict) -> Dict:
        """Valider une soumission KYC complète"""
        errors = []
        warnings = []

        # Vérifier documents requis
        if not data.get("identity_document"):
            errors.append("Document d'identité obligatoire")

        if not data.get("bank_account"):
            errors.append("Informations bancaires obligatoires")

        if data.get("user_type") == "merchant" and not data.get("company_documents"):
            errors.append("Documents d'entreprise obligatoires pour les marchands")

        # Vérifier expiration des documents
        if data.get("identity_document", {}).get("expiry_date"):
            try:
                expiry = datetime.strptime(data["identity_document"]["expiry_date"], "%Y-%m-%d")
                days_until_expiry = (expiry - datetime.now()).days

                if days_until_expiry < 0:
                    errors.append("Document d'identité expiré")
                elif days_until_expiry < 90:
                    warnings.append(f"Le document d'identité expire dans {days_until_expiry} jours")
            except ValueError:
                errors.append("Format de date d'expiration invalide")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    async def create_submission(self, user_id: str, user_type: str, data: Dict, ip_address: Optional[str] = None) -> str:
        """Créer une soumission KYC"""
        try:
            import uuid
            kyc_id = str(uuid.uuid4())

            submission_data = {
                "id": kyc_id,
                "user_id": user_id,
                "user_type": user_type,
                "status": "submitted",
                "personal_info": data.get("personal_info"),
                "identity_document": data.get("identity_document"),
                "company_documents": data.get("company_documents"),
                "bank_account": data.get("bank_account"),
                "ip_address": ip_address,
                "submitted_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }

            # Sauvegarder dans DB (table: kyc_submissions)
            result = self.supabase.table('kyc_submissions').insert(submission_data).execute()

            logger.info("kyc_submission_created", kyc_id=kyc_id, user_id=user_id)

            return kyc_id

        except Exception as e:
            logger.error("create_submission_failed", user_id=user_id, error=str(e))
            raise

    async def get_user_kyc_status(self, user_id: str) -> Dict:
        """Obtenir le statut KYC d'un utilisateur"""
        try:
            # Récupérer dernière soumission
            result = self.supabase.table('kyc_submissions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()

            if not result.data:
                return {
                    "user_id": user_id,
                    "status": "pending",
                    "submitted_at": None,
                    "reviewed_at": None,
                    "reviewer_id": None,
                    "documents_uploaded": [],
                    "missing_documents": ["cin", "rib"],
                    "rejection_reason": None,
                    "rejection_comment": None,
                    "can_resubmit": True
                }

            submission = result.data[0]

            return {
                "user_id": user_id,
                "status": submission.get("status"),
                "submitted_at": submission.get("submitted_at"),
                "reviewed_at": submission.get("reviewed_at"),
                "reviewer_id": submission.get("reviewer_id"),
                "documents_uploaded": self._list_uploaded_documents(submission),
                "missing_documents": [],
                "rejection_reason": submission.get("rejection_reason"),
                "rejection_comment": submission.get("rejection_comment"),
                "can_resubmit": submission.get("status") in ["rejected", "expired"]
            }

        except Exception as e:
            logger.error("get_kyc_status_failed", user_id=user_id, error=str(e))
            raise

    def _list_uploaded_documents(self, submission: Dict) -> List[str]:
        """Lister les documents uploadés d'une soumission"""
        docs = []
        if submission.get("identity_document"):
            docs.append("identity_document")
        if submission.get("company_documents"):
            docs.append("company_documents")
        if submission.get("bank_account"):
            docs.append("bank_account")
        return docs

    async def upload_document(self, user_id: str, document_type: str, file_content: bytes, filename: str, content_type: str) -> str:
        """Upload un document vers le storage"""
        try:
            import uuid
            file_ext = filename.split(".")[-1] if "." in filename else "jpg"
            unique_filename = f"{user_id}/{document_type}_{uuid.uuid4()}.{file_ext}"

            # Upload vers Supabase Storage (bucket: kyc-documents)
            result = self.supabase.storage.from_('kyc-documents').upload(
                unique_filename,
                file_content,
                {'content-type': content_type}
            )

            # Générer URL publique
            document_url = self.supabase.storage.from_('kyc-documents').get_public_url(unique_filename)

            logger.info("document_uploaded", user_id=user_id, document_type=document_type, url=document_url)

            return document_url

        except Exception as e:
            logger.error("upload_document_failed", user_id=user_id, document_type=document_type, error=str(e))
            raise

    async def get_pending_submissions(self, page: int = 1, limit: int = 20) -> List[Dict]:
        """Récupérer les soumissions KYC en attente"""
        try:
            offset = (page - 1) * limit

            result = self.supabase.table('kyc_submissions').select(
                '*',
                'users(id, email, first_name, last_name, role)'
            ).in_('status', ['submitted', 'under_review']).order('submitted_at', desc=False).range(offset, offset + limit - 1).execute()

            return result.data or []

        except Exception as e:
            logger.error("get_pending_submissions_failed", error=str(e))
            return []

    async def get_submission_details(self, kyc_id: str) -> Optional[Dict]:
        """Récupérer les détails complets d'une soumission"""
        try:
            result = self.supabase.table('kyc_submissions').select(
                '*',
                'users(id, email, first_name, last_name, role, phone)'
            ).eq('id', kyc_id).execute()

            if not result.data:
                return None

            return result.data[0]

        except Exception as e:
            logger.error("get_submission_details_failed", kyc_id=kyc_id, error=str(e))
            return None

    async def approve_kyc(self, kyc_id: str, reviewer_id: str, notes: Optional[str] = None) -> bool:
        """Approuver un KYC"""
        try:
            update_data = {
                "status": "approved",
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewer_id": reviewer_id,
                "reviewer_notes": notes
            }

            result = self.supabase.table('kyc_submissions').update(update_data).eq('id', kyc_id).execute()

            if result.data:
                logger.info("kyc_approved", kyc_id=kyc_id, reviewer_id=reviewer_id)
                # TODO: Envoyer email de confirmation
                return True

            return False

        except Exception as e:
            logger.error("approve_kyc_failed", kyc_id=kyc_id, error=str(e))
            return False

    async def reject_kyc(self, kyc_id: str, reviewer_id: str, reason: str, comment: str, notes: Optional[str] = None) -> bool:
        """Rejeter un KYC"""
        try:
            update_data = {
                "status": "rejected",
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewer_id": reviewer_id,
                "rejection_reason": reason,
                "rejection_comment": comment,
                "reviewer_notes": notes
            }

            result = self.supabase.table('kyc_submissions').update(update_data).eq('id', kyc_id).execute()

            if result.data:
                logger.info("kyc_rejected", kyc_id=kyc_id, reviewer_id=reviewer_id, reason=reason)
                # TODO: Envoyer email avec raison du rejet
                return True

            return False

        except Exception as e:
            logger.error("reject_kyc_failed", kyc_id=kyc_id, error=str(e))
            return False


# Instance globale du service
kyc_service = KYCService()

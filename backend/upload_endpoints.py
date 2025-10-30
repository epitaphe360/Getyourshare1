"""
Endpoints pour l'upload de fichiers vers Supabase Storage
"""

from fastapi import HTTPException, Depends, UploadFile, File
from typing import List
import os
import uuid
from datetime import datetime


def add_upload_endpoints(app, verify_token):
    """Ajoute les endpoints pour l'upload de fichiers"""

    @app.post("/api/upload")
    async def upload_file(
        file: UploadFile = File(...), folder: str = "general", payload: dict = Depends(verify_token)
    ):
        """Upload un fichier vers Supabase Storage"""
        from db_helpers import get_supabase_client

        # Vérifier le type de fichier
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".zip"}
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Type de fichier non autorisé. Extensions autorisées: {', '.join(allowed_extensions)}",
            )

        # Vérifier la taille (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        contents = await file.read()
        if len(contents) > max_size:
            raise HTTPException(
                status_code=400, detail="Le fichier est trop volumineux. Taille maximale: 10MB"
            )

        # Générer un nom unique
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"{folder}/{datetime.now().strftime('%Y/%m')}/{unique_filename}"

        try:
            supabase = get_supabase_client()

            # Upload vers Supabase Storage
            # Note: Supabase Storage doit être configuré dans le dashboard Supabase
            result = supabase.storage.from_("uploads").upload(
                path=file_path, file=contents, file_options={"content-type": file.content_type}
            )

            # Obtenir l'URL publique
            public_url = supabase.storage.from_("uploads").get_public_url(file_path)

            return {
                "success": True,
                "filename": file.filename,
                "path": file_path,
                "url": public_url,
                "size": len(contents),
                "content_type": file.content_type,
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

    @app.post("/api/upload/multiple")
    async def upload_multiple_files(
        files: List[UploadFile] = File(...),
        folder: str = "general",
        payload: dict = Depends(verify_token),
    ):
        """Upload plusieurs fichiers à la fois"""

        if len(files) > 10:
            raise HTTPException(
                status_code=400, detail="Vous ne pouvez uploader que 10 fichiers à la fois maximum"
            )

        uploaded_files = []
        errors = []

        for file in files:
            try:
                # Réutiliser la logique d'upload unique
                result = await upload_file(file, folder, payload)
                uploaded_files.append(result)
            except HTTPException as e:
                errors.append({"filename": file.filename, "error": e.detail})

        return {
            "success": len(uploaded_files) > 0,
            "uploaded": uploaded_files,
            "errors": errors,
            "total": len(files),
            "successful": len(uploaded_files),
            "failed": len(errors),
        }

    @app.delete("/api/upload/{file_path:path}")
    async def delete_file(file_path: str, payload: dict = Depends(verify_token)):
        """Supprime un fichier de Supabase Storage"""
        from db_helpers import get_supabase_client

        try:
            supabase = get_supabase_client()

            # Supprimer le fichier
            result = supabase.storage.from_("uploads").remove([file_path])

            return {"success": True, "message": "Fichier supprimé avec succès", "path": file_path}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

    @app.get("/api/uploads/list")
    async def list_uploads(folder: str = "general", payload: dict = Depends(verify_token)):
        """Liste les fichiers uploadés dans un dossier"""
        from db_helpers import get_supabase_client

        try:
            supabase = get_supabase_client()

            # Lister les fichiers
            files = supabase.storage.from_("uploads").list(folder)

            file_list = []
            for file in files:
                file_list.append(
                    {
                        "name": file["name"],
                        "size": file.get("metadata", {}).get("size", 0),
                        "created_at": file.get("created_at"),
                        "updated_at": file.get("updated_at"),
                        "url": supabase.storage.from_("uploads").get_public_url(
                            f"{folder}/{file['name']}"
                        ),
                    }
                )

            return {"success": True, "folder": folder, "files": file_list, "count": len(file_list)}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erreur lors de la récupération de la liste: {str(e)}"
            )

"""
Content Studio Service

Service complet pour la création de contenu:
- Génération de visuels IA
- Templates prêts à l'emploi
- Bibliothèque média
- Éditeur vidéo simplifié
- QR codes stylisés
- Watermarking automatique
- Planification multi-réseaux
- A/B Testing

APIs utilisées:
- DALL-E 3 / Stable Diffusion pour génération IA
- Pillow pour manipulation d'images
- qrcode pour QR codes
- MoviePy pour vidéos
"""

import os
import json
import logging
import qrcode
import hashlib
import base64
from io import BytesIO
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import httpx

logger = logging.getLogger(__name__)

class ContentType(str, Enum):
    """Types de contenu"""
    POST = "post"
    STORY = "story"
    REEL = "reel"
    CAROUSEL = "carousel"
    VIDEO = "video"

class SocialPlatform(str, Enum):
    """Plateformes sociales"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"

class TemplateCategory(str, Enum):
    """Catégories de templates"""
    PRODUCT_SHOWCASE = "product_showcase"
    PROMOTION = "promotion"
    REVIEW = "review"
    TUTORIAL = "tutorial"
    TESTIMONIAL = "testimonial"
    ANNOUNCEMENT = "announcement"
    QUOTE = "quote"

class ContentStudioService:
    """Service pour le studio de création de contenu"""

    def __init__(self):
        # Configuration API génération d'images
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.stability_ai_key = os.getenv("STABILITY_AI_KEY", "")

        # Mode DEMO par défaut
        self.demo_mode = not bool(self.openai_api_key or self.stability_ai_key)

        # Chemins des assets
        self.assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        self.templates_dir = os.path.join(self.assets_dir, "templates")
        self.fonts_dir = os.path.join(self.assets_dir, "fonts")
        self.media_library = os.path.join(self.assets_dir, "media")

        # Créer les dossiers s'ils n'existent pas
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.fonts_dir, exist_ok=True)
        os.makedirs(self.media_library, exist_ok=True)

        if self.demo_mode:
            logger.warning("⚠️ Content Studio en mode DEMO (pas de clés API IA)")
        else:
            logger.info("✅ Content Studio configuré")

    async def generate_image_ai(
        self,
        prompt: str,
        style: str = "realistic",
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Dict[str, Any]:
        """
        Générer une image avec IA (DALL-E 3 ou Stable Diffusion)

        Args:
            prompt: Description de l'image à générer
            style: Style (realistic, artistic, cartoon, minimalist)
            size: Taille (1024x1024, 1792x1024, 1024x1792)
            quality: Qualité (standard, hd)

        Returns:
            URL de l'image générée
        """
        if self.demo_mode:
            logger.info(f"🎨 [DEMO] Génération IA: {prompt[:50]}...")
            return {
                "success": True,
                "image_url": "https://via.placeholder.com/1024x1024?text=AI+Generated+Image",
                "prompt": prompt,
                "style": style,
                "demo_mode": True
            }

        try:
            # Préférer DALL-E 3 si disponible
            if self.openai_api_key:
                return await self._generate_with_dalle(prompt, size, quality, style)
            elif self.stability_ai_key:
                return await self._generate_with_stable_diffusion(prompt, size, style)
            else:
                raise Exception("Aucune API de génération d'images configurée")

        except Exception as e:
            logger.error(f"❌ Erreur génération IA: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_with_dalle(
        self,
        prompt: str,
        size: str,
        quality: str,
        style: str
    ) -> Dict[str, Any]:
        """Générer avec DALL-E 3"""
        # Adapter le prompt selon le style
        style_prefixes = {
            "realistic": "Photorealistic, high quality, detailed",
            "artistic": "Artistic, creative, stylized",
            "cartoon": "Cartoon style, fun, colorful",
            "minimalist": "Minimalist, clean, simple"
        }

        enhanced_prompt = f"{style_prefixes.get(style, '')} {prompt}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": enhanced_prompt,
                    "size": size,
                    "quality": quality,
                    "n": 1
                },
                timeout=60.0
            )

            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "image_url": result["data"][0]["url"],
                "revised_prompt": result["data"][0].get("revised_prompt"),
                "model": "dall-e-3"
            }

    async def _generate_with_stable_diffusion(
        self,
        prompt: str,
        size: str,
        style: str
    ) -> Dict[str, Any]:
        """Générer avec Stable Diffusion"""
        # TODO: Implémenter Stable Diffusion
        # https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image

        logger.info("Génération avec Stable Diffusion")
        return {
            "success": True,
            "image_url": "https://via.placeholder.com/1024",
            "model": "stable-diffusion"
        }

    def get_templates(
        self,
        category: Optional[TemplateCategory] = None,
        content_type: Optional[ContentType] = None,
        platform: Optional[SocialPlatform] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les templates disponibles

        Retourne une liste de templates pré-conçus filtrables
        """
        # Bibliothèque de templates
        all_templates = [
            # Posts Instagram - Product Showcase
            {
                "id": "insta_product_1",
                "name": "Product Spotlight",
                "category": TemplateCategory.PRODUCT_SHOWCASE,
                "content_type": ContentType.POST,
                "platforms": [SocialPlatform.INSTAGRAM, SocialPlatform.FACEBOOK],
                "thumbnail": "/assets/templates/insta_product_1.jpg",
                "description": "Mise en avant produit avec fond coloré et texte accrocheur",
                "dimensions": {"width": 1080, "height": 1080},
                "elements": [
                    {"type": "background", "color": "#FF6B9D", "gradient": True},
                    {"type": "image", "placeholder": "product_image", "size": 0.6},
                    {"type": "text", "content": "{{product_name}}", "font": "bold", "size": 48},
                    {"type": "text", "content": "{{commission}}% Commission", "font": "regular", "size": 32},
                    {"type": "badge", "content": "NOUVEAU", "position": "top-right"}
                ]
            },

            # Stories Instagram - Promotion
            {
                "id": "insta_story_promo_1",
                "name": "Story Promo Flash",
                "category": TemplateCategory.PROMOTION,
                "content_type": ContentType.STORY,
                "platforms": [SocialPlatform.INSTAGRAM],
                "thumbnail": "/assets/templates/insta_story_promo_1.jpg",
                "description": "Story avec countdown et prix barré",
                "dimensions": {"width": 1080, "height": 1920},
                "elements": [
                    {"type": "background", "image": "gradient_vertical"},
                    {"type": "image", "placeholder": "product_image", "size": 0.5, "position": "center"},
                    {"type": "text", "content": "PROMO FLASH", "font": "bold", "size": 64, "color": "#FF0000"},
                    {"type": "price", "old_price": "{{old_price}}", "new_price": "{{price}}", "size": 48},
                    {"type": "countdown", "duration": 24, "position": "bottom"},
                    {"type": "cta", "content": "SWIPE UP", "position": "bottom"}
                ]
            },

            # TikTok - Review
            {
                "id": "tiktok_review_1",
                "name": "TikTok Review Template",
                "category": TemplateCategory.REVIEW,
                "content_type": ContentType.VIDEO,
                "platforms": [SocialPlatform.TIKTOK, SocialPlatform.INSTAGRAM],
                "thumbnail": "/assets/templates/tiktok_review_1.jpg",
                "description": "Template vidéo review avec rating et points clés",
                "dimensions": {"width": 1080, "height": 1920},
                "elements": [
                    {"type": "overlay", "position": "top", "content": "{{product_name}}"},
                    {"type": "rating", "stars": "{{rating}}", "position": "top-center"},
                    {"type": "text_list", "items": ["{{point_1}}", "{{point_2}}", "{{point_3}}"]},
                    {"type": "watermark", "content": "@{{username}}", "position": "bottom-left"}
                ]
            },

            # Carousel - Tutorial
            {
                "id": "carousel_tutorial_1",
                "name": "Tutorial Step-by-Step",
                "category": TemplateCategory.TUTORIAL,
                "content_type": ContentType.CAROUSEL,
                "platforms": [SocialPlatform.INSTAGRAM, SocialPlatform.LINKEDIN],
                "thumbnail": "/assets/templates/carousel_tutorial_1.jpg",
                "description": "Carousel explicatif avec numérotation",
                "dimensions": {"width": 1080, "height": 1080},
                "slides": 5,
                "elements": [
                    {"type": "background", "color": "#FFFFFF"},
                    {"type": "number", "position": "top-left", "size": 72, "color": "#FF6B9D"},
                    {"type": "title", "content": "{{step_title}}", "font": "bold", "size": 42},
                    {"type": "image", "placeholder": "step_image", "size": 0.5},
                    {"type": "description", "content": "{{step_description}}", "font": "regular", "size": 24}
                ]
            },

            # Quote / Testimonial
            {
                "id": "quote_testimonial_1",
                "name": "Customer Testimonial",
                "category": TemplateCategory.TESTIMONIAL,
                "content_type": ContentType.POST,
                "platforms": [SocialPlatform.INSTAGRAM, SocialPlatform.FACEBOOK, SocialPlatform.LINKEDIN],
                "thumbnail": "/assets/templates/quote_testimonial_1.jpg",
                "description": "Témoignage client avec photo et citation",
                "dimensions": {"width": 1080, "height": 1080},
                "elements": [
                    {"type": "background", "color": "#F5F5F5"},
                    {"type": "quote_icon", "position": "top-left", "size": 64},
                    {"type": "text", "content": "{{testimonial}}", "font": "italic", "size": 32, "align": "center"},
                    {"type": "avatar", "image": "{{customer_avatar}}", "size": 120, "position": "bottom-center"},
                    {"type": "name", "content": "{{customer_name}}", "font": "bold", "size": 24},
                    {"type": "rating", "stars": "{{rating}}", "position": "bottom"}
                ]
            },

            # Announcement
            {
                "id": "announcement_1",
                "name": "Big Announcement",
                "category": TemplateCategory.ANNOUNCEMENT,
                "content_type": ContentType.POST,
                "platforms": [SocialPlatform.INSTAGRAM, SocialPlatform.FACEBOOK, SocialPlatform.TWITTER],
                "thumbnail": "/assets/templates/announcement_1.jpg",
                "description": "Annonce avec fond dynamique",
                "dimensions": {"width": 1080, "height": 1080},
                "elements": [
                    {"type": "background", "pattern": "confetti", "colors": ["#FF6B9D", "#4ECDC4", "#FFE66D"]},
                    {"type": "text", "content": "🎉 ANNONCE 🎉", "font": "bold", "size": 56, "position": "top"},
                    {"type": "text", "content": "{{announcement_text}}", "font": "regular", "size": 36, "align": "center"},
                    {"type": "cta", "content": "EN SAVOIR PLUS", "position": "bottom"}
                ]
            },

            # Minimalist Quote
            {
                "id": "quote_minimal_1",
                "name": "Minimalist Quote",
                "category": TemplateCategory.QUOTE,
                "content_type": ContentType.POST,
                "platforms": [SocialPlatform.INSTAGRAM, SocialPlatform.TWITTER, SocialPlatform.LINKEDIN],
                "thumbnail": "/assets/templates/quote_minimal_1.jpg",
                "description": "Citation minimaliste élégante",
                "dimensions": {"width": 1080, "height": 1080},
                "elements": [
                    {"type": "background", "color": "#FFFFFF"},
                    {"type": "text", "content": "{{quote}}", "font": "serif", "size": 38, "align": "center", "color": "#333333"},
                    {"type": "divider", "style": "line", "width": 200, "color": "#FF6B9D"},
                    {"type": "author", "content": "— {{author}}", "font": "italic", "size": 24, "color": "#666666"}
                ]
            }
        ]

        # Filtrer selon les critères
        filtered = all_templates

        if category:
            filtered = [t for t in filtered if t["category"] == category]

        if content_type:
            filtered = [t for t in filtered if t["content_type"] == content_type]

        if platform:
            filtered = [t for t in filtered if platform in t["platforms"]]

        return filtered

    def generate_qr_code(
        self,
        url: str,
        style: str = "modern",
        color: str = "#000000",
        bg_color: str = "#FFFFFF",
        logo_url: Optional[str] = None,
        size: int = 512
    ) -> str:
        """
        Générer un QR code stylisé

        Args:
            url: URL à encoder
            style: Style (modern, rounded, dots, artistic)
            color: Couleur du QR code
            bg_color: Couleur de fond
            logo_url: URL du logo à centrer (optionnel)
            size: Taille en pixels

        Returns:
            QR code en base64
        """
        try:
            # Encoder l'URL pour gérer les caractères spéciaux
            from urllib.parse import quote
            # Ne pas encoder les caractères safe pour URLs
            safe_url = quote(url, safe=':/?#[]@!$&\'()*+,;=')

            # Créer le QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High pour permettre logo
                box_size=10,
                border=4
            )
            qr.add_data(safe_url)
            qr.make(fit=True)

            # Générer l'image
            if style == "artistic":
                img = qr.make_image(fill_color=color, back_color=bg_color).convert('RGB')
            else:
                img = qr.make_image(fill_color=color, back_color=bg_color)

            # Redimensionner
            img = img.resize((size, size), Image.LANCZOS)

            # Appliquer le style
            if style == "rounded":
                img = self._apply_rounded_qr(img)
            elif style == "dots":
                img = self._apply_dots_qr(img)

            # Ajouter le logo si fourni
            if logo_url:
                img = self._add_logo_to_qr(img, logo_url)

            # Convertir en base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            return f"data:image/png;base64,{img_base64}"

        except Exception as e:
            logger.error(f"❌ Erreur génération QR code: {str(e)}")
            return ""

    def _apply_rounded_qr(self, img: Image.Image) -> Image.Image:
        """Appliquer des coins arrondis au QR code"""
        # TODO: Implémenter l'arrondi des modules du QR code
        return img

    def _apply_dots_qr(self, img: Image.Image) -> Image.Image:
        """Transformer les carrés en dots"""
        # TODO: Implémenter la transformation en points
        return img

    def _add_logo_to_qr(self, qr_img: Image.Image, logo_url: str) -> Image.Image:
        """Ajouter un logo au centre du QR code"""
        # TODO: Télécharger le logo et le centrer
        return qr_img

    def add_watermark(
        self,
        image_path: str,
        watermark_text: str,
        position: str = "bottom-right",
        opacity: float = 0.7,
        include_link: bool = True,
        affiliate_link: Optional[str] = None
    ) -> str:
        """
        Ajouter un watermark à une image

        Args:
            image_path: Chemin de l'image
            watermark_text: Texte du watermark (ex: @username)
            position: Position (top-left, top-right, bottom-left, bottom-right, center)
            opacity: Opacité (0-1)
            include_link: Inclure le lien d'affiliation
            affiliate_link: Lien d'affiliation complet

        Returns:
            Chemin de l'image avec watermark
        """
        try:
            # Ouvrir l'image
            img = Image.open(image_path).convert("RGBA")

            # Créer un calque pour le watermark
            txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt)

            # Charger la police (fallback si pas disponible)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()
                font_small = font

            # Construire le texte
            full_text = watermark_text
            if include_link and affiliate_link:
                # Raccourcir le lien
                short_link = affiliate_link.split("//")[-1][:30] + "..."
                full_text = f"{watermark_text}\n🔗 {short_link}"

            # Calculer la position
            bbox = draw.textbbox((0, 0), full_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            positions = {
                "top-left": (20, 20),
                "top-right": (img.width - text_width - 20, 20),
                "bottom-left": (20, img.height - text_height - 20),
                "bottom-right": (img.width - text_width - 20, img.height - text_height - 20),
                "center": ((img.width - text_width) // 2, (img.height - text_height) // 2)
            }

            x, y = positions.get(position, positions["bottom-right"])

            # Dessiner le watermark avec ombre
            # Ombre
            draw.text((x+2, y+2), full_text, font=font, fill=(0, 0, 0, int(255 * opacity * 0.5)))
            # Texte principal
            draw.text((x, y), full_text, font=font, fill=(255, 255, 255, int(255 * opacity)))

            # Combiner les calques
            watermarked = Image.alpha_composite(img, txt)

            # Sauvegarder
            output_path = image_path.replace(".", "_watermarked.")
            watermarked.convert("RGB").save(output_path, quality=95)

            return output_path

        except Exception as e:
            logger.error(f"❌ Erreur watermark: {str(e)}")
            return image_path

    def schedule_post(
        self,
        content: Dict[str, Any],
        platforms: List[SocialPlatform],
        scheduled_time: datetime,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Planifier un post multi-réseaux

        Args:
            content: Contenu du post (image, texte, hashtags)
            platforms: Liste des plateformes cibles
            scheduled_time: Date/heure de publication
            user_id: ID de l'utilisateur

        Returns:
            ID de la tâche de scheduling
        """
        # Créer une entrée dans la table scheduled_posts
        scheduled_id = hashlib.md5(
            f"{user_id}{scheduled_time.isoformat()}".encode()
        ).hexdigest()[:16]

        scheduled_post = {
            "id": scheduled_id,
            "user_id": user_id,
            "content": content,
            "platforms": [p.value for p in platforms],
            "scheduled_time": scheduled_time.isoformat(),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

        # TODO: Sauvegarder en DB
        # TODO: Créer un job cron pour publier à l'heure

        logger.info(f"📅 Post planifié: {scheduled_id} pour {scheduled_time}")

        return {
            "success": True,
            "scheduled_id": scheduled_id,
            "scheduled_time": scheduled_time.isoformat(),
            "platforms": [p.value for p in platforms]
        }

    def analyze_creative_performance(
        self,
        creative_id: str,
        variant_a_id: str,
        variant_b_id: str
    ) -> Dict[str, Any]:
        """
        Analyser la performance de 2 créatives (A/B testing)

        Args:
            creative_id: ID de la creative originale
            variant_a_id: ID de la variante A
            variant_b_id: ID de la variante B

        Returns:
            Résultats de l'A/B test avec recommandation
        """
        # TODO: Récupérer les métriques réelles de chaque variante

        # Données demo
        variant_a_metrics = {
            "impressions": 5420,
            "clicks": 342,
            "conversions": 23,
            "ctr": 6.31,  # Click-through rate
            "conversion_rate": 6.73,
            "engagement_rate": 8.2
        }

        variant_b_metrics = {
            "impressions": 5380,
            "clicks": 478,
            "conversions": 34,
            "ctr": 8.88,
            "conversion_rate": 7.11,
            "engagement_rate": 11.5
        }

        # Calculer le gagnant
        winner = "B" if variant_b_metrics["conversions"] > variant_a_metrics["conversions"] else "A"
        improvement = (
            (variant_b_metrics["conversions"] - variant_a_metrics["conversions"]) /
            variant_a_metrics["conversions"] * 100
        )

        return {
            "creative_id": creative_id,
            "variant_a": {
                "id": variant_a_id,
                "metrics": variant_a_metrics
            },
            "variant_b": {
                "id": variant_b_id,
                "metrics": variant_b_metrics
            },
            "winner": winner,
            "improvement_percentage": round(improvement, 2),
            "recommendation": f"Utilisez la variante {winner} pour vos prochains posts",
            "insights": [
                f"La variante {winner} a généré {abs(improvement):.1f}% de conversions en plus",
                f"Le CTR de la variante {winner} est supérieur de {abs(variant_b_metrics['ctr'] - variant_a_metrics['ctr']):.2f}%",
                "Continuez les tests A/B pour optimiser vos créatives"
            ]
        }


# Instance singleton du service
content_studio_service = ContentStudioService()

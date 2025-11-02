"""
============================================
SERVICE DE MODÉRATION IA POUR PRODUITS
Utilise OpenAI pour détecter contenu inapproprié
============================================
"""

import os
from typing import Dict, Any, Optional
from openai import OpenAI
import json

# Configuration OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("⚠️ Warning: OpenAI API key not configured for content moderation")
    client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================
# CATÉGORIES INTERDITES
# ============================================

PROHIBITED_CATEGORIES = {
    "adult_content": "Contenu adulte/sexuel (+18)",
    "weapons": "Armes, explosifs, munitions",
    "drugs": "Drogues, substances illicites",
    "gambling": "Jeux d'argent, paris illégaux",
    "counterfeit": "Produits contrefaits, faux documents",
    "hate_speech": "Contenu haineux, discrimination",
    "violence": "Contenu violent, gore",
    "illegal_services": "Services illégaux (piratage, fraude)",
    "tobacco": "Tabac, cigarettes électroniques non autorisées",
    "alcohol": "Alcool (vente sans licence)",
    "medical_fraud": "Médicaments non autorisés, fausses promesses médicales",
    "pyramid_scheme": "Schémas pyramidaux, MLM frauduleux",
    "stolen_goods": "Biens volés, recel",
    "endangered_species": "Espèces protégées, ivoire",
    "personal_data": "Vente de données personnelles"
}

# ============================================
# MODÉRATION IA
# ============================================

async def moderate_product_with_ai(
    product_name: str,
    description: str,
    category: Optional[str] = None,
    price: Optional[float] = None,
    images_urls: Optional[list] = None
) -> Dict[str, Any]:
    """
    Analyse un produit avec l'IA OpenAI pour détecter du contenu inapproprié
    
    Returns:
        {
            "approved": bool,
            "confidence": float (0-1),
            "risk_level": "low" | "medium" | "high" | "critical",
            "flags": [list of detected issues],
            "reason": str (if rejected),
            "recommendation": str
        }
    """
    
    if not client:
        # Fallback: approuver par défaut si pas d'IA configurée
        print("⚠️ OpenAI not configured, approving by default (UNSAFE FOR PRODUCTION)")
        return {
            "approved": True,
            "confidence": 0.0,
            "risk_level": "unknown",
            "flags": [],
            "reason": "AI moderation disabled",
            "recommendation": "Manual review required - AI not configured"
        }
    
    try:
        # Construire le prompt pour l'IA
        prompt = f"""Tu es un système de modération de contenu pour une plateforme e-commerce au Maroc.
Analyse ce produit/service et détermine s'il est ACCEPTABLE ou INACCEPTABLE selon les critères suivants:

CRITÈRES D'INTERDICTION:
1. Contenu sexuel, adulte ou +18
2. Armes, explosifs, munitions
3. Drogues ou substances illicites
4. Jeux d'argent illégaux
5. Produits contrefaits ou faux documents
6. Contenu haineux ou discriminatoire
7. Contenu violent ou gore
8. Services illégaux (piratage, fraude, blanchiment)
9. Tabac ou cigarettes électroniques non autorisées
10. Alcool sans licence de vente
11. Médicaments non autorisés ou fausses promesses médicales
12. Schémas pyramidaux ou MLM frauduleux
13. Biens volés ou recel
14. Espèces animales protégées
15. Vente de données personnelles

PRODUIT À ANALYSER:
- Nom: {product_name}
- Description: {description}
- Catégorie: {category or "Non spécifiée"}
- Prix: {price} MAD
- Images: {"Oui" if images_urls else "Non"}

INSTRUCTIONS:
1. Analyse le nom et la description pour détecter des contenus interdits
2. Vérifie les termes cachés, euphémismes ou codes
3. Évalue le risque selon le contexte marocain et la loi islamique
4. Retourne UNIQUEMENT un JSON valide (pas de markdown, pas de texte avant/après)

FORMAT DE RÉPONSE (JSON STRICT):
{{
    "approved": true/false,
    "confidence": 0.0-1.0,
    "risk_level": "low"|"medium"|"high"|"critical",
    "flags": ["categorie1", "categorie2", ...],
    "reason": "Explication détaillée si rejeté",
    "recommendation": "Action recommandée"
}}"""

        # Appel à l'API OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Modèle rapide et économique
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en modération de contenu e-commerce. Tu réponds UNIQUEMENT en JSON valide, sans markdown ni texte supplémentaire."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Peu de créativité, cohérence max
            max_tokens=500,
            response_format={"type": "json_object"}  # Force le JSON
        )
        
        # Extraire la réponse
        result_text = response.choices[0].message.content.strip()
        
        # Parser le JSON
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Si le JSON est invalide, essayer de nettoyer
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(result_text)
        
        # Validation et enrichissement
        result.setdefault("approved", True)
        result.setdefault("confidence", 0.5)
        result.setdefault("risk_level", "low")
        result.setdefault("flags", [])
        result.setdefault("reason", "")
        result.setdefault("recommendation", "Approved")
        
        # Log pour monitoring
        status = "✅ APPROVED" if result["approved"] else "❌ REJECTED"
        print(f"{status} | Product: {product_name[:50]} | Risk: {result['risk_level']} | Confidence: {result['confidence']}")
        
        if result["flags"]:
            print(f"   Flags: {', '.join(result['flags'])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in AI moderation: {e}")
        # En cas d'erreur, rejeter par précaution
        return {
            "approved": False,
            "confidence": 0.0,
            "risk_level": "unknown",
            "flags": ["ai_error"],
            "reason": f"Erreur de modération IA: {str(e)}. Nécessite révision manuelle.",
            "recommendation": "Manual review required due to AI error"
        }

# ============================================
# MODÉRATION PAR MOTS-CLÉS (FALLBACK)
# ============================================

PROHIBITED_KEYWORDS = {
    "adult_content": [
        "sexe", "xxx", "porn", "adulte", "érotique", "sexuel", 
        "lingerie coquine", "sex toy", "vibr", "escort", "massage sensuel"
    ],
    "weapons": [
        "arme", "pistolet", "fusil", "couteau", "explosif", "munition",
        "grenade", "bombe", "kalachnikov", "revolver"
    ],
    "drugs": [
        "drogue", "cannabis", "cocaine", "héroïne", "mdma", "ecstasy",
        "shit", "beuh", "weed", "joint", "psychotrope"
    ],
    "gambling": [
        "casino", "poker", "pari sportif", "jeux d'argent", "bet",
        "machine à sous", "roulette", "blackjack"
    ],
    "counterfeit": [
        "faux", "contrefait", "copie", "réplique", "fake", "imitation",
        "fausse carte", "faux passeport", "faux diplôme"
    ],
    "illegal_services": [
        "piratage", "hacking", "crack", "keygen", "comptes piratés",
        "blanchiment", "fausse facture", "fraude"
    ]
}

def moderate_product_keywords(product_name: str, description: str) -> Dict[str, Any]:
    """
    Modération basique par mots-clés (fallback si pas d'IA)
    """
    text = f"{product_name} {description}".lower()
    flags = []
    
    for category, keywords in PROHIBITED_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                flags.append(category)
                break
    
    if flags:
        return {
            "approved": False,
            "confidence": 0.7,
            "risk_level": "high",
            "flags": list(set(flags)),
            "reason": f"Mots-clés interdits détectés: {', '.join(flags)}",
            "recommendation": "Manual review required - keyword match"
        }
    
    return {
        "approved": True,
        "confidence": 0.6,
        "risk_level": "low",
        "flags": [],
        "reason": "",
        "recommendation": "Approved by keyword filter"
    }

# ============================================
# FONCTION PRINCIPALE
# ============================================

async def moderate_product(
    product_name: str,
    description: str,
    category: Optional[str] = None,
    price: Optional[float] = None,
    images_urls: Optional[list] = None,
    use_ai: bool = True
) -> Dict[str, Any]:
    """
    Point d'entrée principal pour la modération de produit
    
    Args:
        product_name: Nom du produit
        description: Description détaillée
        category: Catégorie (optionnel)
        price: Prix en MAD (optionnel)
        images_urls: URLs des images (optionnel)
        use_ai: Utiliser l'IA OpenAI (si False, utilise mots-clés)
    
    Returns:
        Résultat de la modération avec approved, risk_level, flags, etc.
    """
    
    # Validation des entrées
    if not product_name or not description:
        return {
            "approved": False,
            "confidence": 1.0,
            "risk_level": "critical",
            "flags": ["incomplete_data"],
            "reason": "Nom ou description manquant",
            "recommendation": "Reject - incomplete product information"
        }
    
    # Modération par IA si disponible
    if use_ai and client:
        result = await moderate_product_with_ai(
            product_name, description, category, price, images_urls
        )
    else:
        # Fallback sur mots-clés
        result = moderate_product_keywords(product_name, description)
    
    # Ajouter metadata
    result["moderation_method"] = "ai" if (use_ai and client) else "keywords"
    result["product_name"] = product_name
    
    return result

# ============================================
# VÉRIFICATION RAPIDE
# ============================================

def quick_check_prohibited_keywords(text: str) -> bool:
    """
    Vérification rapide pour rejeter immédiatement les contenus évidents
    Retourne True si contenu suspect détecté
    """
    text_lower = text.lower()
    
    # Liste de mots ultra-interdits qui déclenchent un rejet immédiat
    instant_reject_words = [
        "porn", "xxx", "sexe", "drogue", "cannabis", "cocaine",
        "arme", "pistolet", "explosif", "escort", "casino"
    ]
    
    for word in instant_reject_words:
        if word in text_lower:
            return True
    
    return False

# ============================================
# STATISTIQUES DE MODÉRATION
# ============================================

class ModerationStats:
    """Classe pour tracker les stats de modération"""
    
    def __init__(self):
        self.total_checks = 0
        self.approved = 0
        self.rejected = 0
        self.flags_by_category = {}
    
    def record(self, result: Dict[str, Any]):
        """Enregistre un résultat de modération"""
        self.total_checks += 1
        
        if result["approved"]:
            self.approved += 1
        else:
            self.rejected += 1
        
        for flag in result.get("flags", []):
            self.flags_by_category[flag] = self.flags_by_category.get(flag, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques"""
        return {
            "total_checks": self.total_checks,
            "approved": self.approved,
            "rejected": self.rejected,
            "approval_rate": self.approved / max(self.total_checks, 1),
            "flags_by_category": self.flags_by_category
        }

# Instance globale pour les stats
moderation_stats = ModerationStats()

# ============================================
# EXEMPLE D'UTILISATION
# ============================================

"""
# Dans vos endpoints:

from moderation_service import moderate_product

@app.post("/api/products")
async def create_product(product: ProductCreate, user: dict = Depends(get_current_user)):
    # Modération automatique
    moderation_result = await moderate_product(
        product_name=product.name,
        description=product.description,
        category=product.category,
        price=product.price,
        use_ai=True
    )
    
    if not moderation_result["approved"]:
        # Produit rejeté par l'IA
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Product rejected by moderation",
                "reason": moderation_result["reason"],
                "flags": moderation_result["flags"]
            }
        )
    
    # Si approuvé, créer le produit
    # ... logique de création
"""

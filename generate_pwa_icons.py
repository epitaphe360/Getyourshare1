#!/usr/bin/env python3
"""
Script pour générer toutes les icônes PWA depuis le logo
"""
from PIL import Image
import os

# Chemins
logo_path = "frontend/public/logo.jpg"
icons_dir = "frontend/public/icons"

# Tailles d'icônes requises
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def generate_icons():
    """Génère toutes les icônes PWA depuis le logo"""
    
    # Créer le dossier icons s'il n'existe pas
    os.makedirs(icons_dir, exist_ok=True)
    
    print(f"📁 Dossier créé: {icons_dir}")
    
    # Ouvrir le logo
    try:
        logo = Image.open(logo_path)
        print(f"✅ Logo chargé: {logo_path} ({logo.size[0]}x{logo.size[1]})")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du logo: {e}")
        return
    
    # Convertir en RGBA pour transparence
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')
    
    # Générer chaque taille
    for size in SIZES:
        try:
            # Redimensionner avec antialiasing de haute qualité
            resized = logo.resize((size, size), Image.Resampling.LANCZOS)
            
            # Chemin de sortie
            output_path = os.path.join(icons_dir, f"icon-{size}x{size}.png")
            
            # Sauvegarder en PNG
            resized.save(output_path, "PNG", optimize=True)
            
            print(f"✅ Généré: icon-{size}x{size}.png")
            
        except Exception as e:
            print(f"❌ Erreur pour la taille {size}x{size}: {e}")
    
    print(f"\n🎉 Toutes les icônes PWA ont été générées dans {icons_dir}")
    print(f"📊 Total: {len(SIZES)} icônes créées")

if __name__ == "__main__":
    generate_icons()

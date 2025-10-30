"""
Client Supabase pour l'application ShareYourSales
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

# Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Client avec service_role (admin - pour backend)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Client avec anon key (pour frontend si nécessaire)
supabase_anon: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def get_supabase_client(admin=True) -> Client:
    """
    Retourne le client Supabase approprié

    Args:
        admin: Si True, retourne le client avec droits admin (service_role)
               Si False, retourne le client avec droits anonymes
    """
    return supabase_admin if admin else supabase_anon


# Export du client par défaut (admin)
supabase = supabase_admin

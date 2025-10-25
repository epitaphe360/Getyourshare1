"""
Configuration Celery pour l'exécution de tâches asynchrones

Tâches principales:
- Synchronisation quotidienne des stats des réseaux sociaux
- Rafraîchissement des tokens expirants
- Notifications par email/SMS
- Génération de rapports

Installation requise:
pip install celery redis

Configuration Redis:
docker run -d -p 6379:6379 redis:alpine

Démarrage Worker:
celery -A celery_app worker --loglevel=info

Démarrage Beat (scheduler):
celery -A celery_app beat --loglevel=info
"""

from celery import Celery
from celery.schedules import crontab
import os

# Configuration Redis (broker et backend)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Créer l'application Celery
app = Celery(
    'shareyoursales',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'celery_tasks.social_media_tasks',
        'celery_tasks.notification_tasks',
        'celery_tasks.report_tasks',
    ]
)

# Configuration Celery
app.conf.update(
    # Timezone
    timezone='Africa/Casablanca',  # Maroc
    enable_utc=True,

    # Sérialisation
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Expiration des résultats
    result_expires=3600,  # 1 heure

    # Retry policy
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Timeouts
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes

    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)

# Configuration des tâches périodiques (Celery Beat)
app.conf.beat_schedule = {
    # Synchroniser tous les comptes sociaux chaque jour à 8h00
    'sync-all-social-media-daily': {
        'task': 'celery_tasks.social_media_tasks.sync_all_active_connections',
        'schedule': crontab(hour=8, minute=0),  # 8h00 chaque jour
        'options': {
            'expires': 3600,  # Si la tâche n'est pas exécutée dans l'heure, l'annuler
        }
    },

    # Rafraîchir les tokens expirant dans 7 jours (chaque jour à 2h00)
    'refresh-expiring-tokens-daily': {
        'task': 'celery_tasks.social_media_tasks.refresh_expiring_tokens',
        'schedule': crontab(hour=2, minute=0),
        'kwargs': {'days_before': 7},
    },

    # Vérifier les connexions en erreur et tenter de les réactiver (chaque jour à 10h00)
    'check-failed-connections': {
        'task': 'celery_tasks.social_media_tasks.check_and_repair_connections',
        'schedule': crontab(hour=10, minute=0),
    },

    # Rafraîchir les vues matérialisées pour les dashboards (toutes les 6 heures)
    'refresh-materialized-views': {
        'task': 'celery_tasks.social_media_tasks.refresh_materialized_views',
        'schedule': crontab(minute=0, hour='*/6'),  # 0h, 6h, 12h, 18h
    },

    # Envoyer les rapports hebdomadaires (chaque lundi à 9h00)
    'send-weekly-reports': {
        'task': 'celery_tasks.report_tasks.send_weekly_social_reports',
        'schedule': crontab(hour=9, minute=0, day_of_week='monday'),
    },

    # Nettoyer les anciens logs de synchronisation (chaque dimanche à 3h00)
    'cleanup-old-sync-logs': {
        'task': 'celery_tasks.social_media_tasks.cleanup_old_logs',
        'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),
        'kwargs': {'days_to_keep': 90},
    },

    # Notifier les influenceurs des tokens expirant bientôt (chaque jour à 9h00)
    'notify-token-expiration': {
        'task': 'celery_tasks.notification_tasks.notify_expiring_tokens',
        'schedule': crontab(hour=9, minute=0),
        'kwargs': {'days_before': 3},
    },
}

# Configuration des routes (pour diriger certaines tâches vers des workers spécifiques)
app.conf.task_routes = {
    'celery_tasks.social_media_tasks.*': {'queue': 'social_media'},
    'celery_tasks.notification_tasks.*': {'queue': 'notifications'},
    'celery_tasks.report_tasks.*': {'queue': 'reports'},
}

# Configuration des limites de taux (rate limiting)
app.conf.task_annotations = {
    # Limiter les appels API Instagram (200 requêtes par heure)
    'celery_tasks.social_media_tasks.sync_instagram_account': {
        'rate_limit': '200/h'
    },
    # Limiter les appels API TikTok
    'celery_tasks.social_media_tasks.sync_tiktok_account': {
        'rate_limit': '100/h'
    },
    # Limiter les emails (éviter le spam)
    'celery_tasks.notification_tasks.send_email': {
        'rate_limit': '50/m'
    },
}

if __name__ == '__main__':
    app.start()

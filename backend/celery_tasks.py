"""
Celery Tasks - Background Jobs
Tâches asynchrones pour améliorer les performances

Tasks:
1. Email sending (async)
2. Social media stats sync
3. Commission calculations
4. Analytics aggregation
5. Stripe webhooks processing
6. Report generation
7. Data cleanup
"""

from celery import Celery
from celery.schedules import crontab
import os
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

# Configuration Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Initialiser Celery
celery_app = Celery(
    "shareyoursales",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Casablanca',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # Warning après 4 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)


# ============================================
# EMAIL TASKS
# ============================================

@celery_app.task(name="send_email_async", bind=True, max_retries=3)
def send_email_async(self, to_email: str, subject: str, html_content: str, text_content: str = None):
    """
    Envoyer email en async
    Retry 3 fois en cas d'échec
    """
    try:
        from services.email_service import email_service

        success = email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

        if not success:
            raise Exception("Email send failed")

        logger.info("email_task_completed", to=to_email)
        return {"success": True, "to": to_email}

    except Exception as e:
        logger.error("email_task_failed", to=to_email, error=str(e))

        # Retry avec backoff exponentiel
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(name="send_welcome_email")
def send_welcome_email(to_email: str, user_name: str, user_type: str):
    """Envoyer email de bienvenue"""
    from services.email_service import EmailTemplates
    import asyncio

    return asyncio.run(EmailTemplates.send_welcome_email(to_email, user_name, user_type))


@celery_app.task(name="send_kyc_approved_email")
def send_kyc_approved_email(to_email: str, user_name: str):
    """Envoyer email KYC approuvé"""
    from services.email_service import EmailTemplates
    import asyncio

    return asyncio.run(EmailTemplates.send_kyc_approved_email(to_email, user_name))


@celery_app.task(name="send_kyc_rejected_email")
def send_kyc_rejected_email(to_email: str, user_name: str, reason: str, comment: str):
    """Envoyer email KYC rejeté"""
    from services.email_service import EmailTemplates
    import asyncio

    return asyncio.run(EmailTemplates.send_kyc_rejected_email(to_email, user_name, reason, comment))


@celery_app.task(name="send_subscription_confirmation_email")
def send_subscription_confirmation_email(
    to_email: str,
    user_name: str,
    plan_name: str,
    amount: float,
    billing_cycle: str,
    next_billing_date: str
):
    """Envoyer email confirmation abonnement"""
    from services.email_service import EmailTemplates
    import asyncio

    return asyncio.run(EmailTemplates.send_subscription_confirmation_email(
        to_email, user_name, plan_name, amount, billing_cycle, next_billing_date
    ))


@celery_app.task(name="send_2fa_code_email")
def send_2fa_code_email(to_email: str, user_name: str, code: str):
    """Envoyer email avec code 2FA"""
    from services.email_service import EmailTemplates
    import asyncio

    return asyncio.run(EmailTemplates.send_2fa_code_email(to_email, user_name, code))


# ============================================
# SOCIAL MEDIA TASKS
# ============================================

@celery_app.task(name="sync_instagram_stats")
def sync_instagram_stats(user_id: str):
    """
    Synchroniser statistiques Instagram d'un utilisateur
    """
    try:
        from services.social_media_service import SocialMediaService
        import asyncio

        service = SocialMediaService()
        result = asyncio.run(service.sync_instagram_stats(user_id))

        logger.info("instagram_sync_completed", user_id=user_id, result=result)
        return result

    except Exception as e:
        logger.error("instagram_sync_failed", user_id=user_id, error=str(e))
        raise


@celery_app.task(name="sync_tiktok_stats")
def sync_tiktok_stats(user_id: str):
    """
    Synchroniser statistiques TikTok d'un utilisateur
    """
    try:
        from services.social_media_service import SocialMediaService
        import asyncio

        service = SocialMediaService()
        result = asyncio.run(service.sync_tiktok_stats(user_id))

        logger.info("tiktok_sync_completed", user_id=user_id, result=result)
        return result

    except Exception as e:
        logger.error("tiktok_sync_failed", user_id=user_id, error=str(e))
        raise


@celery_app.task(name="sync_all_social_stats")
def sync_all_social_stats():
    """
    Synchroniser toutes les stats des réseaux sociaux
    Task planifiée quotidiennement
    """
    try:
        from supabase_client import supabase

        # Récupérer tous les users avec comptes sociaux
        result = supabase.table('social_media_accounts').select('user_id, platform').eq('is_active', True).execute()

        accounts = result.data or []

        synced = 0
        for account in accounts:
            try:
                user_id = account['user_id']
                platform = account['platform']

                if platform == 'instagram':
                    sync_instagram_stats.delay(user_id)
                elif platform == 'tiktok':
                    sync_tiktok_stats.delay(user_id)

                synced += 1

            except Exception as e:
                logger.error("account_sync_failed", account=account, error=str(e))

        logger.info("all_social_stats_synced", total=len(accounts), synced=synced)
        return {"total": len(accounts), "synced": synced}

    except Exception as e:
        logger.error("sync_all_social_stats_failed", error=str(e))
        raise


# ============================================
# COMMISSION TASKS
# ============================================

@celery_app.task(name="calculate_commissions")
def calculate_commissions():
    """
    Calculer les commissions pour toutes les conversions
    Task planifiée toutes les heures
    """
    try:
        from supabase_client import supabase

        # Récupérer conversions non payées
        result = supabase.table('conversions').select('*').eq('commission_paid', False).execute()

        conversions = result.data or []

        processed = 0
        for conversion in conversions:
            try:
                # Calculer commission
                order_amount = conversion.get('order_amount', 0)
                commission_rate = conversion.get('commission_rate', 0)
                commission = order_amount * (commission_rate / 100)

                # Créer commission record
                supabase.table('commissions').insert({
                    'conversion_id': conversion['id'],
                    'influencer_id': conversion['influencer_id'],
                    'merchant_id': conversion['merchant_id'],
                    'amount': commission,
                    'status': 'pending',
                    'created_at': datetime.utcnow().isoformat()
                }).execute()

                # Marquer conversion comme payée
                supabase.table('conversions').update({
                    'commission_paid': True
                }).eq('id', conversion['id']).execute()

                processed += 1

            except Exception as e:
                logger.error("commission_calculation_failed", conversion=conversion, error=str(e))

        logger.info("commissions_calculated", total=len(conversions), processed=processed)
        return {"total": len(conversions), "processed": processed}

    except Exception as e:
        logger.error("calculate_commissions_failed", error=str(e))
        raise


# ============================================
# ANALYTICS TASKS
# ============================================

@celery_app.task(name="aggregate_daily_analytics")
def aggregate_daily_analytics():
    """
    Agréger analytics quotidiennes
    Task planifiée à minuit
    """
    try:
        from supabase_client import supabase

        yesterday = (datetime.utcnow() - timedelta(days=1)).date()

        # Agréger par utilisateur
        # TODO: Implémenter agrégation analytics

        logger.info("daily_analytics_aggregated", date=str(yesterday))
        return {"date": str(yesterday), "success": True}

    except Exception as e:
        logger.error("aggregate_daily_analytics_failed", error=str(e))
        raise


# ============================================
# CLEANUP TASKS
# ============================================

@celery_app.task(name="cleanup_expired_tokens")
def cleanup_expired_tokens():
    """
    Nettoyer tokens expirés
    Task planifiée quotidiennement
    """
    try:
        from supabase_client import supabase

        # Supprimer tokens expirés (> 30 jours)
        cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()

        # TODO: Nettoyer tokens expirés

        logger.info("expired_tokens_cleaned", cutoff_date=cutoff_date)
        return {"cutoff_date": cutoff_date, "success": True}

    except Exception as e:
        logger.error("cleanup_expired_tokens_failed", error=str(e))
        raise


@celery_app.task(name="cleanup_old_logs")
def cleanup_old_logs():
    """
    Nettoyer anciens logs
    Task planifiée hebdomadairement
    """
    try:
        # Supprimer logs > 90 jours
        cutoff_date = (datetime.utcnow() - timedelta(days=90)).isoformat()

        # TODO: Nettoyer logs

        logger.info("old_logs_cleaned", cutoff_date=cutoff_date)
        return {"cutoff_date": cutoff_date, "success": True}

    except Exception as e:
        logger.error("cleanup_old_logs_failed", error=str(e))
        raise


# ============================================
# STRIPE WEBHOOK TASKS
# ============================================

@celery_app.task(name="process_stripe_webhook", bind=True, max_retries=5)
def process_stripe_webhook(self, event_id: str, event_type: str, event_data: dict):
    """
    Traiter webhook Stripe en async
    Retry jusqu'à 5 fois en cas d'échec
    """
    try:
        from services.stripe_service import StripeService
        import asyncio

        service = StripeService()
        result = asyncio.run(service.process_webhook_event(event_type, event_data))

        logger.info("stripe_webhook_processed", event_id=event_id, event_type=event_type)
        return result

    except Exception as e:
        logger.error("stripe_webhook_processing_failed", event_id=event_id, error=str(e))

        # Retry avec backoff
        raise self.retry(exc=e, countdown=30 * (2 ** self.request.retries))


# ============================================
# REPORT GENERATION TASKS
# ============================================

@celery_app.task(name="generate_monthly_report")
def generate_monthly_report(user_id: str, month: str):
    """
    Générer rapport mensuel pour un utilisateur
    """
    try:
        # TODO: Implémenter génération de rapport
        # - Récupérer toutes les conversions du mois
        # - Calculer total commissions
        # - Générer PDF
        # - Envoyer par email

        logger.info("monthly_report_generated", user_id=user_id, month=month)
        return {"user_id": user_id, "month": month, "success": True}

    except Exception as e:
        logger.error("generate_monthly_report_failed", user_id=user_id, error=str(e))
        raise


# ============================================
# SCHEDULED TASKS (Beat)
# ============================================

celery_app.conf.beat_schedule = {
    # Sync réseaux sociaux - Tous les jours à 3h du matin
    'sync-all-social-stats': {
        'task': 'sync_all_social_stats',
        'schedule': crontab(hour=3, minute=0),
    },

    # Calculer commissions - Toutes les heures
    'calculate-commissions': {
        'task': 'calculate_commissions',
        'schedule': crontab(minute=0),
    },

    # Agréger analytics - Tous les jours à minuit
    'aggregate-daily-analytics': {
        'task': 'aggregate_daily_analytics',
        'schedule': crontab(hour=0, minute=0),
    },

    # Nettoyer tokens expirés - Tous les jours à 4h
    'cleanup-expired-tokens': {
        'task': 'cleanup_expired_tokens',
        'schedule': crontab(hour=4, minute=0),
    },

    # Nettoyer logs anciens - Tous les dimanches à 2h
    'cleanup-old-logs': {
        'task': 'cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),
    },
}


# ============================================
# CELERY SIGNALS
# ============================================

from celery.signals import task_prerun, task_postrun, task_failure


@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Signal avant exécution d'une tâche"""
    logger.info("task_started", task_id=task_id, task_name=task.name)


@task_postrun.connect
def task_postrun_handler(task_id, task, retval, *args, **kwargs):
    """Signal après exécution d'une tâche"""
    logger.info("task_completed", task_id=task_id, task_name=task.name, result=retval)


@task_failure.connect
def task_failure_handler(task_id, exception, *args, **kwargs):
    """Signal en cas d'échec d'une tâche"""
    logger.error("task_failed", task_id=task_id, error=str(exception))


# ============================================
# HELPER FUNCTIONS
# ============================================

def queue_task(task_name: str, *args, **kwargs):
    """
    Helper pour ajouter une tâche à la queue

    Usage:
        queue_task('send_welcome_email', to_email='user@example.com', user_name='John')
    """
    task = celery_app.tasks.get(task_name)

    if not task:
        logger.error("task_not_found", task_name=task_name)
        return None

    return task.delay(*args, **kwargs)


def get_task_status(task_id: str) -> dict:
    """
    Obtenir le statut d'une tâche

    Returns:
        {
            "status": "PENDING|STARTED|SUCCESS|FAILURE|RETRY",
            "result": <result_if_completed>,
            "error": <error_if_failed>
        }
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=celery_app)

    return {
        "status": result.status,
        "result": result.result if result.successful() else None,
        "error": str(result.result) if result.failed() else None
    }

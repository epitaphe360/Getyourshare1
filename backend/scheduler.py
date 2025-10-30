"""
Scheduler pour les tâches automatiques
Utilise APScheduler pour gérer les cron jobs
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from auto_payment_service import run_daily_validation, run_weekly_payouts

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Gestionnaire des tâches planifiées"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()

    def setup_jobs(self):
        """Configure les tâches planifiées"""

        # Tâche 1: Validation quotidienne des ventes (tous les jours à 2h du matin)
        self.scheduler.add_job(
            func=self.job_validate_sales,
            trigger=CronTrigger(hour=2, minute=0),
            id="validate_sales",
            name="Validation quotidienne des ventes",
            replace_existing=True,
        )
        logger.info("✅ Tâche planifiée: Validation quotidienne (2h00)")

        # Tâche 2: Paiements automatiques (tous les vendredis à 10h)
        self.scheduler.add_job(
            func=self.job_process_payouts,
            trigger=CronTrigger(day_of_week="fri", hour=10, minute=0),
            id="process_payouts",
            name="Paiements automatiques hebdomadaires",
            replace_existing=True,
        )
        logger.info("✅ Tâche planifiée: Paiements automatiques (Vendredi 10h00)")

        # Tâche 3: Nettoyage des sessions expirées (tous les jours à 3h)
        self.scheduler.add_job(
            func=self.job_cleanup_sessions,
            trigger=CronTrigger(hour=3, minute=0),
            id="cleanup_sessions",
            name="Nettoyage des sessions",
            replace_existing=True,
        )
        logger.info("✅ Tâche planifiée: Nettoyage sessions (3h00)")

        # Tâche 4: Rappel de configuration paiement (tous les lundis à 9h)
        self.scheduler.add_job(
            func=self.job_payment_config_reminder,
            trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
            id="payment_reminder",
            name="Rappel configuration paiement",
            replace_existing=True,
        )
        logger.info("✅ Tâche planifiée: Rappel configuration (Lundi 9h00)")

    def job_validate_sales(self):
        """Job: Valider les ventes en attente"""
        try:
            logger.info("🔄 Démarrage: Validation quotidienne des ventes")
            result = run_daily_validation()
            if result.get("success"):
                logger.info(
                    f"✅ Validation terminée: {result.get('validated_sales')} ventes, "
                    f"{result.get('total_commission')}€ de commissions"
                )
            else:
                logger.error(f"❌ Échec validation: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Erreur job_validate_sales: {e}")

    def job_process_payouts(self):
        """Job: Traiter les paiements automatiques"""
        try:
            logger.info("🔄 Démarrage: Paiements automatiques")
            result = run_weekly_payouts()
            if result.get("success"):
                logger.info(
                    f"✅ Paiements terminés: {result.get('processed_count')} paiements, "
                    f"{result.get('total_paid')}€ payés"
                )
                if result.get("failed_count") > 0:
                    logger.warning(f"⚠️  {result.get('failed_count')} paiements ont échoué")
            else:
                logger.error(f"❌ Échec paiements: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Erreur job_process_payouts: {e}")

    def job_cleanup_sessions(self):
        """Job: Nettoyer les sessions expirées"""
        try:
            logger.info("🔄 Démarrage: Nettoyage des sessions")
            from supabase_client import supabase

            # Supprimer les sessions expirées
            result = (
                supabase.table("user_sessions")
                .delete()
                .lt("expires_at", datetime.now().isoformat())
                .execute()
            )

            deleted_count = len(result.data) if result.data else 0
            logger.info(f"✅ Nettoyage terminé: {deleted_count} sessions supprimées")
        except Exception as e:
            logger.error(f"❌ Erreur job_cleanup_sessions: {e}")

    def job_payment_config_reminder(self):
        """Job: Rappeler aux influenceurs de configurer leur paiement"""
        try:
            logger.info("🔄 Démarrage: Rappel configuration paiement")
            from supabase_client import supabase

            # Trouver les influenceurs avec solde ≥ 30€ sans méthode de paiement
            result = (
                supabase.table("influencers")
                .select(
                    """
                id,
                user_id,
                username,
                balance
            """
                )
                .gte("balance", 30.0)
                .is_("payment_method", "null")
                .execute()
            )

            influencers = result.data if result.data else []

            for influencer in influencers:
                # Créer notification
                notification_data = {
                    "user_id": influencer["user_id"],
                    "type": "payment_setup_reminder",
                    "title": "Configurez votre méthode de paiement",
                    "message": f'Vous avez {influencer["balance"]}€ disponibles. Configurez votre méthode de paiement pour recevoir vos commissions automatiquement.',
                    "is_read": False,
                    "created_at": datetime.now().isoformat(),
                }
                supabase.table("notifications").insert(notification_data).execute()

            logger.info(f"✅ Rappels envoyés: {len(influencers)} notifications")
        except Exception as e:
            logger.error(f"❌ Erreur job_payment_config_reminder: {e}")

    def start(self):
        """Démarre le scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("🚀 Scheduler démarré")
            self.print_jobs()

    def stop(self):
        """Arrête le scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Scheduler arrêté")

    def print_jobs(self):
        """Affiche les tâches planifiées"""
        logger.info("\n" + "=" * 60)
        logger.info("TÂCHES PLANIFIÉES")
        logger.info("=" * 60)
        for job in self.scheduler.get_jobs():
            logger.info(f"📅 {job.name}")
            logger.info(f"   ID: {job.id}")
            logger.info(f"   Prochaine exécution: {job.next_run_time}")
            logger.info("")
        logger.info("=" * 60 + "\n")


# Instance globale du scheduler
scheduler_instance = TaskScheduler()


def start_scheduler():
    """Démarre le scheduler (appelé depuis server.py)"""
    scheduler_instance.start()


def stop_scheduler():
    """Arrête le scheduler"""
    scheduler_instance.stop()


if __name__ == "__main__":
    # Test du scheduler
    import time

    logger.info("🧪 Mode test du scheduler")

    # Démarrer
    scheduler_instance.start()

    # Exécuter immédiatement pour test
    logger.info("\n🔬 Exécution immédiate des jobs pour test...")
    scheduler_instance.job_validate_sales()
    scheduler_instance.job_process_payouts()

    # Garder le script actif
    try:
        logger.info("\n⏳ Scheduler actif. Appuyez sur Ctrl+C pour arrêter.")
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n🛑 Arrêt du scheduler...")
        scheduler_instance.stop()

"""
Tâches Celery pour la génération de rapports

Rapports générés:
- Rapports hebdomadaires des statistiques sociales
- Rapports mensuels de performance
- Rapports d'engagement pour les marchands
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
from typing import Dict, List
import json

from database import get_db_connection
from celery_tasks.notification_tasks import send_email_task

logger = get_task_logger(__name__)

# ============================================
# TÂCHES DE RAPPORTS
# ============================================

@shared_task(
    name='celery_tasks.report_tasks.send_weekly_social_reports',
    bind=True
)
def send_weekly_social_reports(self):
    """
    Envoyer les rapports hebdomadaires de statistiques sociales

    Exécuté chaque lundi à 9h00
    """
    try:
        logger.info("📊 Generating weekly social media reports")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer tous les influenceurs avec au moins une connexion active
        cursor.execute("""
            SELECT DISTINCT
                u.id,
                u.email,
                u.full_name
            FROM users u
            JOIN social_media_connections smc ON u.id = smc.user_id
            WHERE smc.connection_status = 'active'
            AND u.role = 'influencer'
        """)

        influencers = cursor.fetchall()

        logger.info(f"Found {len(influencers)} influencers to send reports to")

        reports_sent = 0

        for user_id, email, full_name in influencers:
            try:
                # Générer le rapport pour cet influenceur
                report_data = generate_weekly_report(user_id, cursor)

                if report_data:
                    # Envoyer l'email
                    send_weekly_report_email.delay(
                        email=email,
                        full_name=full_name,
                        report_data=report_data
                    )
                    reports_sent += 1

            except Exception as e:
                logger.error(f"Failed to generate report for user {user_id}: {str(e)}")

        cursor.close()
        conn.close()

        logger.info(f"✅ Sent {reports_sent} weekly reports")

        return {
            'total_influencers': len(influencers),
            'reports_sent': reports_sent,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as exc:
        logger.error(f"❌ Weekly reports generation failed: {str(exc)}")
        raise self.retry(exc=exc)


def generate_weekly_report(user_id: str, cursor) -> Dict:
    """
    Générer les données du rapport hebdomadaire pour un influenceur

    Returns:
        Dict avec les statistiques de la semaine
    """
    try:
        report = {
            'period': {
                'start': (datetime.now() - timedelta(days=7)).strftime('%d/%m/%Y'),
                'end': datetime.now().strftime('%d/%m/%Y')
            },
            'platforms': [],
            'summary': {
                'total_followers': 0,
                'total_growth': 0,
                'avg_engagement': 0,
                'best_platform': None
            }
        }

        # Récupérer les stats de chaque plateforme
        cursor.execute("""
            SELECT
                smc.platform,
                smc.platform_username,
                -- Stats actuelles (dernière sync)
                latest.followers_count as current_followers,
                latest.engagement_rate as current_engagement,
                latest.total_posts as current_posts,
                -- Stats d'il y a 7 jours
                week_ago.followers_count as week_ago_followers,
                week_ago.engagement_rate as week_ago_engagement
            FROM social_media_connections smc
            -- Dernière stats
            LEFT JOIN LATERAL (
                SELECT followers_count, engagement_rate, total_posts
                FROM social_media_stats
                WHERE connection_id = smc.id
                ORDER BY synced_at DESC
                LIMIT 1
            ) latest ON TRUE
            -- Stats d'il y a 7 jours
            LEFT JOIN LATERAL (
                SELECT followers_count, engagement_rate
                FROM social_media_stats
                WHERE connection_id = smc.id
                AND synced_at <= NOW() - INTERVAL '7 days'
                ORDER BY synced_at DESC
                LIMIT 1
            ) week_ago ON TRUE
            WHERE smc.user_id = %s
            AND smc.connection_status = 'active'
        """, (user_id,))

        platforms = cursor.fetchall()

        if not platforms:
            return None

        total_followers = 0
        total_growth = 0
        total_engagement = 0
        platforms_count = 0
        best_platform = {'name': None, 'growth': 0}

        for platform_data in platforms:
            (platform, username, current_followers, current_engagement, current_posts,
             week_ago_followers, week_ago_engagement) = platform_data

            # Calculer la croissance
            followers_growth = 0
            if week_ago_followers:
                followers_growth = current_followers - week_ago_followers

            engagement_change = 0
            if week_ago_engagement:
                engagement_change = current_engagement - week_ago_engagement

            # Ajouter au rapport
            platform_report = {
                'name': platform,
                'username': username,
                'followers': current_followers,
                'followers_growth': followers_growth,
                'engagement_rate': current_engagement,
                'engagement_change': engagement_change,
                'total_posts': current_posts
            }
            report['platforms'].append(platform_report)

            # Calculer totaux
            total_followers += current_followers
            total_growth += followers_growth
            total_engagement += current_engagement
            platforms_count += 1

            # Meilleure plateforme
            if followers_growth > best_platform['growth']:
                best_platform = {'name': platform, 'growth': followers_growth}

        # Summary
        report['summary']['total_followers'] = total_followers
        report['summary']['total_growth'] = total_growth
        report['summary']['avg_engagement'] = round(total_engagement / platforms_count, 2) if platforms_count > 0 else 0
        report['summary']['best_platform'] = best_platform['name']

        return report

    except Exception as e:
        logger.error(f"Error generating report for user {user_id}: {str(e)}")
        return None


@shared_task(
    name='celery_tasks.report_tasks.send_weekly_report_email',
    rate_limit='20/m'
)
def send_weekly_report_email(email: str, full_name: str, report_data: Dict):
    """
    Envoyer l'email du rapport hebdomadaire
    """
    try:
        subject = f"📊 Votre rapport hebdomadaire ShareYourSales"

        # Construire le HTML des plateformes
        platforms_html = ""
        for platform in report_data['platforms']:
            growth_icon = "📈" if platform['followers_growth'] >= 0 else "📉"
            growth_color = "#10b981" if platform['followers_growth'] >= 0 else "#ef4444"

            engagement_icon = "🔥" if platform['engagement_change'] >= 0 else "⚠️"
            engagement_color = "#10b981" if platform['engagement_change'] >= 0 else "#ef4444"

            platforms_html += f"""
            <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #667eea;">
                <h3 style="margin: 0 0 10px 0; color: #667eea; text-transform: capitalize;">
                    {platform['name']} (@{platform['username']})
                </h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <p style="margin: 5px 0; color: #6b7280; font-size: 14px;">Followers</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #111827;">
                            {platform['followers']:,}
                        </p>
                        <p style="margin: 5px 0; color: {growth_color}; font-size: 14px;">
                            {growth_icon} {platform['followers_growth']:+,} cette semaine
                        </p>
                    </div>
                    <div>
                        <p style="margin: 5px 0; color: #6b7280; font-size: 14px;">Engagement</p>
                        <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #111827;">
                            {platform['engagement_rate']:.1f}%
                        </p>
                        <p style="margin: 5px 0; color: {engagement_color}; font-size: 14px;">
                            {engagement_icon} {platform['engagement_change']:+.1f}% cette semaine
                        </p>
                    </div>
                </div>
            </div>
            """

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f3f4f6; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .summary {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stat-card {{ display: inline-block; width: 48%; padding: 15px; background: #f3f4f6; border-radius: 8px; margin: 5px 1%; vertical-align: top; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0 0 10px 0;">📊 Rapport Hebdomadaire</h1>
                    <p style="margin: 0; opacity: 0.9;">
                        {report_data['period']['start']} - {report_data['period']['end']}
                    </p>
                </div>

                <div class="content">
                    <p>Bonjour {full_name},</p>

                    <p>Voici le résumé de vos performances sur les réseaux sociaux cette semaine:</p>

                    <!-- Summary -->
                    <div class="summary">
                        <h2 style="margin: 0 0 20px 0; color: #111827;">Résumé</h2>
                        <div style="text-align: center;">
                            <div class="stat-card">
                                <p style="margin: 0; color: #6b7280; font-size: 14px;">Total Followers</p>
                                <p style="margin: 5px 0; font-size: 32px; font-weight: bold; color: #667eea;">
                                    {report_data['summary']['total_followers']:,}
                                </p>
                            </div>
                            <div class="stat-card">
                                <p style="margin: 0; color: #6b7280; font-size: 14px;">Croissance</p>
                                <p style="margin: 5px 0; font-size: 32px; font-weight: bold; color: {'#10b981' if report_data['summary']['total_growth'] >= 0 else '#ef4444'};">
                                    {report_data['summary']['total_growth']:+,}
                                </p>
                            </div>
                            <div class="stat-card">
                                <p style="margin: 0; color: #6b7280; font-size: 14px;">Engagement Moyen</p>
                                <p style="margin: 5px 0; font-size: 32px; font-weight: bold; color: #667eea;">
                                    {report_data['summary']['avg_engagement']:.1f}%
                                </p>
                            </div>
                            <div class="stat-card">
                                <p style="margin: 0; color: #6b7280; font-size: 14px;">Meilleure Plateforme</p>
                                <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #667eea; text-transform: capitalize;">
                                    {report_data['summary']['best_platform'] or 'N/A'}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Détails par plateforme -->
                    <h2 style="color: #111827; margin: 30px 0 15px 0;">Détails par Plateforme</h2>
                    {platforms_html}

                    <!-- CTA -->
                    <center>
                        <a href="https://shareyoursales.ma/influencer/social-media/history" class="button">
                            Voir mon historique complet
                        </a>
                    </center>

                    <!-- Conseils -->
                    <div style="background: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 30px 0; border-radius: 5px;">
                        <p style="margin: 0 0 10px 0; font-weight: bold; color: #1e40af;">💡 Conseil de la semaine</p>
                        <p style="margin: 0; color: #1e3a8a; font-size: 14px;">
                            Continuez à créer du contenu engageant et interagissez régulièrement avec votre audience
                            pour maintenir un bon taux d'engagement. Les marchands recherchent des influenceurs actifs !
                        </p>
                    </div>

                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

                    <p style="font-size: 12px; color: #6b7280; text-align: center;">
                        Vous recevez cet email car vous avez des comptes sociaux connectés sur ShareYourSales.
                        <br>
                        Pour ne plus recevoir ces rapports, désactivez-les dans vos paramètres.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        send_email_task.delay(
            to_email=email,
            subject=subject,
            html_body=html_body
        )

        logger.info(f"✅ Weekly report email queued for {email}")

        return {'status': 'sent', 'email': email}

    except Exception as exc:
        logger.error(f"❌ Failed to send weekly report to {email}: {str(exc)}")
        raise


@shared_task(
    name='celery_tasks.report_tasks.generate_monthly_performance_report'
)
def generate_monthly_performance_report():
    """
    Générer un rapport mensuel de performance pour les admins

    Statistiques globales de la plateforme
    """
    try:
        logger.info("📊 Generating monthly platform performance report")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Statistiques du mois
        cursor.execute("""
            SELECT
                COUNT(DISTINCT smc.user_id) as total_influencers,
                COUNT(DISTINCT smc.id) as total_connections,
                SUM(sms.followers_count) as total_followers,
                AVG(sms.engagement_rate) as avg_engagement,
                COUNT(DISTINCT CASE WHEN smc.connection_status = 'active' THEN smc.id END) as active_connections,
                COUNT(DISTINCT CASE WHEN smc.connection_status = 'error' THEN smc.id END) as error_connections
            FROM social_media_connections smc
            LEFT JOIN social_media_stats sms ON smc.id = sms.connection_id
            WHERE sms.synced_at >= NOW() - INTERVAL '30 days'
        """)

        stats = cursor.fetchone()

        cursor.close()
        conn.close()

        report = {
            'period': 'monthly',
            'month': datetime.now().strftime('%B %Y'),
            'total_influencers': stats[0],
            'total_connections': stats[1],
            'total_followers': stats[2],
            'avg_engagement': round(stats[3], 2) if stats[3] else 0,
            'active_connections': stats[4],
            'error_connections': stats[5],
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"✅ Monthly report generated: {report}")

        # TODO: Envoyer le rapport aux admins
        # send_admin_report_email.delay(report_data=report)

        return report

    except Exception as exc:
        logger.error(f"❌ Monthly report generation failed: {str(exc)}")
        raise

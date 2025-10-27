"""Utility helpers for transactional emails."""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Optional

logger = logging.getLogger("shareyoursales.email")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_FROM", "no-reply@shareyoursales.com")
DEFAULT_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "ShareYourSales")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
VERIFICATION_ROUTE = os.getenv("VERIFICATION_ROUTE", "/verify-email")


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> bool:
    """Sends an email using SMTP if configured, otherwise logs a mock message."""

    if not SMTP_HOST or not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.info(
            "[EMAIL MOCK] %s → %s | Subject: %s\n%s",
            DEFAULT_FROM_EMAIL,
            to_email,
            subject,
            text_body or html_body,
        )
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr((DEFAULT_FROM_NAME, DEFAULT_FROM_EMAIL))
    message["To"] = to_email

    if reply_to:
        message.add_header("Reply-To", reply_to)

    if text_body:
        message.attach(MIMEText(text_body, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if SMTP_USE_TLS:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
        else:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)

        logger.info("[EMAIL] Message envoyé à %s", to_email)
        return True
    except Exception as exc:  # pragma: no cover - depends on SMTP provider
        logger.error("[EMAIL] Échec de l'envoi à %s: %s", to_email, exc)
        return False


def build_verification_url(token: str) -> str:
    base = FRONTEND_URL.rstrip("/")
    route = VERIFICATION_ROUTE if VERIFICATION_ROUTE.startswith("/") else f"/{VERIFICATION_ROUTE}"
    return f"{base}{route}?token={token}"


def send_verification_email(to_email: str, token: str) -> str:
    """Send a verification email and return the URL used in the message."""
    verification_url = build_verification_url(token)

    subject = "Vérifiez votre adresse email"
    text_body = (
        "Bienvenue sur ShareYourSales !\n\n"
        "Pour activer votre compte, cliquez sur le lien suivant :\n"
        f"{verification_url}\n\n"
        "Ce lien expire dans 48 heures."
    )
    html_body = f"""
        <html>
            <body>
                <p>Bienvenue sur <strong>ShareYourSales</strong> !</p>
                <p>Pour activer votre compte, veuillez confirmer votre adresse email en cliquant sur le bouton ci-dessous :</p>
                <p style=\"margin:24px 0;\">
                    <a href=\"{verification_url}\" style=\"
                        background-color:#2563eb;
                        color:#ffffff;
                        padding:12px 24px;
                        border-radius:6px;
                        text-decoration:none;
                        display:inline-block;
                        font-weight:600;
                    \">Confirmer mon adresse email</a>
                </p>
                <p>Ce lien expire dans 48 heures. Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.</p>
                <p style=\"margin-top:32px; color:#6b7280; font-size:12px;\">
                    ShareYourSales · Plateforme d'affiliation intelligente
                </p>
            </body>
        </html>
    """

    send_email(to_email=to_email, subject=subject, html_body=html_body, text_body=text_body)
    return verification_url

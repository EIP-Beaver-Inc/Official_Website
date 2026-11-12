"""Outgoing email notifications (contact form & quote requests).

Configuration (environment variables):
    SMTP_HOST         SMTP server            (default: smtp.gmail.com)
    SMTP_PORT         SMTP port              (default: 587 -> STARTTLS, 465 -> implicit TLS)
    SMTP_USER         SMTP login             (e.g. beaver.eip@gmail.com)
    SMTP_PASSWORD     SMTP password          (Gmail: a 16-char App Password, NOT the account password)
    SMTP_FROM         From address           (default: SMTP_USER)
    NOTIFY_EMAIL_TO   Comma-separated recipients (default: beaver.eip@gmail.com)

If SMTP_USER / SMTP_PASSWORD are missing, the mailer is disabled and only logs.
"""
from __future__ import annotations

import asyncio
import html
import logging
import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from typing import Iterable, Optional

logger = logging.getLogger("beaver.mailer")

DEFAULT_RECIPIENT = "beaver.eip@gmail.com"


@dataclass(frozen=True)
class SMTPConfig:
    host: str
    port: int
    user: str
    password: str
    sender: str
    recipients: tuple[str, ...]

    @classmethod
    def from_env(cls) -> Optional["SMTPConfig"]:
        user = os.environ.get("SMTP_USER", "").strip()
        password = os.environ.get("SMTP_PASSWORD", "").strip()
        if not user or not password:
            return None
        recipients = tuple(
            r.strip()
            for r in os.environ.get("NOTIFY_EMAIL_TO", DEFAULT_RECIPIENT).split(",")
            if r.strip()
        )
        return cls(
            host=os.environ.get("SMTP_HOST", "smtp.gmail.com").strip(),
            port=int(os.environ.get("SMTP_PORT", "587")),
            user=user,
            # Gmail displays App Passwords with spaces; they are not part of it.
            password=password.replace(" ", ""),
            sender=os.environ.get("SMTP_FROM", "").strip() or user,
            recipients=recipients or (DEFAULT_RECIPIENT,),
        )


def _one_line(value: Optional[str]) -> str:
    """Collapse whitespace/newlines so user input can't break email headers."""
    return " ".join((value or "").split())


def _build_message(
    cfg: SMTPConfig,
    subject: str,
    fields: Iterable[tuple[str, Optional[str]]],
    reply_to: Optional[str],
) -> EmailMessage:
    fields = list(fields)

    text_lines = []
    html_rows = []
    for label, value in fields:
        value = (value or "").strip() or "—"
        text_lines.append(f"{label} :\n{value}\n" if "\n" in value else f"{label} : {value}")
        html_rows.append(
            "<tr>"
            f'<td style="padding:6px 12px 6px 0;color:#6b5a4e;vertical-align:top;white-space:nowrap">'
            f"<strong>{html.escape(label)}</strong></td>"
            f'<td style="padding:6px 0;white-space:pre-wrap">{html.escape(value)}</td>'
            "</tr>"
        )

    msg = EmailMessage()
    msg["Subject"] = _one_line(subject)[:200]
    msg["From"] = formataddr(("Site Beaver", cfg.sender))
    msg["To"] = ", ".join(cfg.recipients)
    msg["Message-ID"] = make_msgid(domain=cfg.sender.split("@")[-1])
    if reply_to:
        msg["Reply-To"] = _one_line(reply_to)

    msg.set_content(
        "\n".join(text_lines)
        + "\n\n--\nEnvoyé automatiquement depuis le formulaire du site Beaver."
        + "\nRépondez directement à cet email pour contacter l'expéditeur."
    )
    msg.add_alternative(
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#2b211b">'
        f'<h2 style="margin:0 0 16px;color:#a8412a">{html.escape(_one_line(subject))}</h2>'
        f'<table style="border-collapse:collapse">{"".join(html_rows)}</table>'
        '<p style="margin-top:24px;font-size:12px;color:#8a7a6e">'
        "Envoyé automatiquement depuis le formulaire du site Beaver. "
        "Répondez directement à cet email pour contacter l'expéditeur.</p></div>",
        subtype="html",
    )
    return msg


def _send_sync(cfg: SMTPConfig, msg: EmailMessage) -> None:
    context = ssl.create_default_context()
    if cfg.port == 465:
        with smtplib.SMTP_SSL(cfg.host, cfg.port, context=context, timeout=20) as smtp:
            smtp.login(cfg.user, cfg.password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(cfg.host, cfg.port, timeout=20) as smtp:
            smtp.starttls(context=context)
            smtp.login(cfg.user, cfg.password)
            smtp.send_message(msg)


async def send_notification(
    subject: str,
    fields: Iterable[tuple[str, Optional[str]]],
    reply_to: Optional[str] = None,
) -> str:
    """Send a notification email. Never raises.

    Returns "sent", "failed" or "disabled".
    """
    cfg = SMTPConfig.from_env()
    if cfg is None:
        logger.warning("SMTP not configured (SMTP_USER/SMTP_PASSWORD) - email not sent: %s", subject)
        return "disabled"
    try:
        msg = _build_message(cfg, subject, fields, reply_to)
        await asyncio.to_thread(_send_sync, cfg, msg)
        logger.info("Notification email sent to %s: %s", ", ".join(cfg.recipients), msg["Subject"])
        return "sent"
    except Exception:  # noqa: BLE001 - a mail failure must never break the request
        logger.exception("Failed to send notification email: %s", subject)
        return "failed"


# ---------------------------------------------------------------------------
# Form-specific helpers
# ---------------------------------------------------------------------------
async def notify_contact(contact: dict) -> str:
    who = _one_line(contact.get("nom"))
    company = _one_line(contact.get("entreprise"))
    subject = f"[Beaver · Contact] {who}" + (f" ({company})" if company else "")
    return await send_notification(
        subject,
        [
            ("Nom", contact.get("nom")),
            ("Entreprise", contact.get("entreprise")),
            ("Email", contact.get("email")),
            ("Téléphone", contact.get("telephone")),
            ("Message", contact.get("message")),
            ("Reçu le", contact.get("created_at")),
            ("ID", contact.get("id")),
        ],
        reply_to=contact.get("email"),
    )


async def notify_demo_request(req: dict) -> str:
    who = _one_line(req.get("nom"))
    company = _one_line(req.get("entreprise"))
    subject = f"[Beaver · Demande de devis] {company} — {who}"
    return await send_notification(
        subject,
        [
            ("Nom", req.get("nom")),
            ("Entreprise", req.get("entreprise")),
            ("Email", req.get("email")),
            ("Téléphone", req.get("telephone")),
            ("Taille scierie", req.get("taille_scierie")),
            ("Volume / jour", req.get("volume")),
            ("Message", req.get("message")),
            ("Reçu le", req.get("created_at")),
            ("ID", req.get("id")),
        ],
        reply_to=req.get("email"),
    )

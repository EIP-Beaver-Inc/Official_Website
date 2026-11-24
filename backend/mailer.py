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
from collections.abc import Iterable
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

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
    def from_env(cls) -> SMTPConfig | None:
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


def _one_line(value: str | None) -> str:
    """Collapse whitespace/newlines so user input can't break email headers."""
    return " ".join((value or "").split())


def _build_message(
    cfg: SMTPConfig,
    subject: str,
    fields: Iterable[tuple[str, str | None]],
    reply_to: str | None,
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


def _login(smtp: smtplib.SMTP, user: str, password: str) -> None:
    """Authenticate without an SMTP "initial response".

    smtplib's default login() sends `AUTH PLAIN <credentials>` in a single
    command; Gmail answers that by silently dropping the connection
    (SMTPServerDisconnected). Sending `AUTH LOGIN` / `AUTH PLAIN` first and the
    credentials after the 334 challenge works with Gmail and any other server.
    """
    smtp.ehlo_or_helo_if_needed()
    if not smtp.has_extn("auth"):
        raise smtplib.SMTPNotSupportedError("SMTP AUTH extension not supported by server.")
    advertised = smtp.esmtp_features["auth"].upper().split()
    smtp.user, smtp.password = user, password
    for mechanism in ("LOGIN", "PLAIN"):
        if mechanism in advertised:
            smtp.auth(mechanism, getattr(smtp, "auth_" + mechanism.lower()), initial_response_ok=False)
            return
    smtp.login(user, password)  # fall back to smtplib's own choice (e.g. CRAM-MD5)


def _send_sync(cfg: SMTPConfig, msg: EmailMessage) -> None:
    context = ssl.create_default_context()
    if cfg.port == 465:
        with smtplib.SMTP_SSL(cfg.host, cfg.port, context=context, timeout=20) as smtp:
            _login(smtp, cfg.user, cfg.password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(cfg.host, cfg.port, timeout=20) as smtp:
            smtp.starttls(context=context)
            _login(smtp, cfg.user, cfg.password)
            smtp.send_message(msg)


async def send_notification(
    subject: str,
    fields: Iterable[tuple[str, str | None]],
    reply_to: str | None = None,
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
    except Exception:
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


# ---------------------------------------------------------------------------
# Emails to customers (quote, delivery of the software)
# ---------------------------------------------------------------------------
def _customer_message(
    cfg: SMTPConfig,
    to: str,
    subject: str,
    greeting: str,
    paragraphs: list[str],
    code_blocks: Iterable[tuple[str, str]] = (),
    button: tuple[str, str] | None = None,
    closing: list[str] | None = None,
) -> EmailMessage:
    """A plain, readable email to a customer: paragraphs, labelled blocks of
    text to copy exactly (a licence key) and at most one button (a link).
    Replies go to the Beaver inbox, which also receives a copy (Bcc)."""
    code_blocks = list(code_blocks)
    closing = closing or []

    text = [greeting, ""]
    for p in paragraphs:
        text += [p, ""]
    if button:
        text += [f"{button[0]} : {button[1]}", ""]
    for label, value in code_blocks:
        text += [f"{label} :", value, ""]
    for p in closing:
        text += [p, ""]
    text += ["L'équipe Beaver", "beaver.eip@gmail.com"]

    def para(p: str) -> str:
        return f'<p style="margin:0 0 14px;line-height:1.55">{html.escape(p)}</p>'

    blocks_html = "".join(
        f'<p style="margin:18px 0 6px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;'
        f'color:#6b5a4e"><strong>{html.escape(label)}</strong></p>'
        f'<div style="font-family:Consolas,Menlo,monospace;font-size:13px;background:#f6efe6;'
        f'border:1px solid #e4d6c6;border-radius:8px;padding:12px;word-break:break-all">'
        f"{html.escape(value)}</div>"
        for label, value in code_blocks
    )
    button_html = (
        f'<p style="margin:22px 0"><a href="{html.escape(button[1], quote=True)}" '
        f'style="background:#a8412a;color:#fff;text-decoration:none;padding:12px 22px;'
        f'border-radius:999px;font-weight:bold;display:inline-block">{html.escape(button[0])}</a></p>'
        if button else ""
    )

    msg = EmailMessage()
    msg["Subject"] = _one_line(subject)[:200]
    msg["From"] = formataddr(("Beaver", cfg.sender))
    msg["To"] = _one_line(to)
    msg["Reply-To"] = cfg.recipients[0]
    msg["Bcc"] = ", ".join(cfg.recipients)
    msg["Message-ID"] = make_msgid(domain=cfg.sender.split("@")[-1])
    msg.set_content("\n".join(text))
    msg.add_alternative(
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#2b211b;max-width:600px">'
        + para(greeting)
        + "".join(para(p) for p in paragraphs)
        + button_html
        + blocks_html
        + '<div style="margin-top:18px">' + "".join(para(p) for p in closing) + "</div>"
        + '<p style="margin-top:24px;color:#6b5a4e">L\'équipe Beaver<br>beaver.eip@gmail.com</p></div>',
        subtype="html",
    )
    return msg


async def send_customer_email(to: str, subject: str, greeting: str, paragraphs: list[str],
                              code_blocks: Iterable[tuple[str, str]] = (),
                              button: tuple[str, str] | None = None,
                              closing: list[str] | None = None) -> str:
    """Send an email to a customer. Never raises. Returns "sent", "failed" or "disabled"."""
    cfg = SMTPConfig.from_env()
    if cfg is None:
        logger.warning("SMTP not configured - customer email not sent: %s", subject)
        return "disabled"
    try:
        msg = _customer_message(cfg, to, subject, greeting, paragraphs, code_blocks, button, closing)
        await asyncio.to_thread(_send_sync, cfg, msg)
        logger.info("Customer email sent to %s: %s", to, msg["Subject"])
        return "sent"
    except Exception:
        logger.exception("Failed to send customer email: %s", subject)
        return "failed"

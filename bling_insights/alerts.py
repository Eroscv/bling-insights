"""Envio de alertas de estoque baixo por e-mail (SMTP)."""

from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from .models import Product


def build_low_stock_message(low_stock: list[Product]) -> str:
    lines = ["Os seguintes produtos estão com estoque no mínimo ou abaixo dele:\n"]
    for p in low_stock:
        lines.append(f"- {p.name} (SKU {p.sku}): {p.stock} unidades (mínimo: {p.min_stock})")
    return "\n".join(lines)


def send_low_stock_email(
    low_stock: list[Product],
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    recipient: str,
) -> None:
    """Envia um e-mail de alerta. Não faz nada se a lista estiver vazia."""
    if not low_stock:
        return

    body = build_low_stock_message(low_stock)
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = f"[Alerta] {len(low_stock)} produto(s) com estoque baixo"
    msg["From"] = smtp_user
    msg["To"] = recipient

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [recipient], msg.as_string())

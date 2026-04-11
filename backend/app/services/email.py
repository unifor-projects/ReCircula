import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def _build_verification_email(destinatario: str, nome: str, token: str) -> MIMEMultipart:
    link = f"{settings.FRONTEND_URL}/verificar-email?token={token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Confirme seu e-mail – Plataforma de Doação e Troca"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = destinatario

    texto = (
        f"Olá, {nome}!\n\n"
        "Obrigado por se cadastrar na Plataforma de Doação e Troca.\n"
        f"Clique no link abaixo para confirmar seu e-mail:\n\n{link}\n\n"
        "Se você não criou esta conta, ignore este e-mail."
    )
    nome_escaped = escape(nome)
    html = f"""\
<html>
  <body>
    <p>Olá, <strong>{nome_escaped}</strong>!</p>
    <p>Obrigado por se cadastrar na <strong>Plataforma de Doação e Troca</strong>.</p>
    <p>
      <a href="{link}">Clique aqui para confirmar seu e-mail</a>
    </p>
    <p style="font-size:0.85em;color:#666;">
      Se você não criou esta conta, ignore este e-mail.
    </p>
  </body>
</html>"""

    msg.attach(MIMEText(texto, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


def send_verification_email(destinatario: str, nome: str, token: str) -> None:
    """Envia e-mail de verificação de conta.

    Falhas de envio são registradas em log e não propagadas ao chamador,
    para não bloquear o cadastro do usuário.
    """
    if not settings.SMTP_HOST:
        logger.info(
            "SMTP_HOST não configurado – e-mail de verificação não enviado para %s",
            destinatario,
        )
        return

    msg = _build_verification_email(destinatario, nome, token)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            smtp.ehlo()
            if settings.SMTP_TLS:
                smtp.starttls()
            if settings.SMTP_USER:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(settings.SMTP_FROM, destinatario, msg.as_string())
        logger.info("E-mail de verificação enviado para %s", destinatario)
    except Exception:
        logger.exception("Falha ao enviar e-mail de verificação para %s", destinatario)

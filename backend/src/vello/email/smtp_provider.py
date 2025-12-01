"""
SMTP email provider implementation.
Works with Gmail, Outlook, or any SMTP server.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from vello.core import config
from vello.email.base import EmailResult


class SMTPProvider:
    """
    SMTP email provider.
    Implements EmailProvider protocol without inheritance.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        default_from: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.default_from = default_from or username

    def send_email(
        self,
        to: str,
        subject: str,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
        **kwargs
    ) -> EmailResult:
        """Send email via SMTP."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or self.default_from
            msg['To'] = to

            # Add body parts
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            if body_html:
                msg.attach(MIMEText(body_html, 'html'))

            # Connect and send
            if self.use_tls:
                server = smtplib.SMTP(self.host, self.port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.host, self.port)

            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            # SMTP doesn't return a message ID easily, so we'll generate one
            message_id = f"<{hash(to + subject)}>@{self.host}"

            return EmailResult(success=True, message_id=message_id)

        except Exception as e:
            return EmailResult(success=False, error=str(e))

    def validate_config(self) -> bool:
        """Validate SMTP configuration."""
        return all([
            self.host,
            self.port,
            self.username,
            self.password
        ])


def create_smtp_provider() -> SMTPProvider:
    """Factory function to create SMTP provider from config."""
    return SMTPProvider(
        host=config.EMAIL_HOST,
        port=config.EMAIL_PORT,
        username=config.EMAIL_HOST_USER,
        password=config.EMAIL_HOST_PASSWORD,
        use_tls=config.EMAIL_USE_TLS,
        default_from=config.EMAIL_HOST_USER
    )

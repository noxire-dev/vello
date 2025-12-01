"""
SendGrid email provider (stub for future implementation).
To use: pip install sendgrid
"""
from typing import Optional

from vello.email.base import EmailResult


class SendGridProvider:
    """
    SendGrid email provider.
    Implements EmailProvider protocol without inheritance.
    """

    def __init__(self, api_key: str, default_from: Optional[str] = None):
        self.api_key = api_key
        self.default_from = default_from
        # self.client = sendgrid.SendGridAPIClient(api_key)

    def send_email(
        self,
        to: str,
        subject: str,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
        **kwargs
    ) -> EmailResult:
        """Send email via SendGrid."""
        # Stub implementation
        # from sendgrid.helpers.mail import Mail
        #
        # message = Mail(
        #     from_email=from_email or self.default_from,
        #     to_emails=to,
        #     subject=subject,
        #     plain_text_content=body_text,
        #     html_content=body_html
        # )
        #
        # try:
        #     response = self.client.send(message)
        #     return EmailResult(success=True, message_id=response.headers.get('X-Message-Id'))
        # except Exception as e:
        #     return EmailResult(success=False, error=str(e))

        raise NotImplementedError("SendGrid provider not yet implemented")

    def validate_config(self) -> bool:
        """Validate SendGrid configuration."""
        return bool(self.api_key and self.default_from)


def create_sendgrid_provider() -> SendGridProvider:
    """Factory function to create SendGrid provider from config."""
    from vello.core import config
    return SendGridProvider(
        api_key=config.SENDGRID_API_KEY,
        default_from=config.EMAIL_HOST_USER
    )

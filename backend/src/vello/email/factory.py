"""
Email provider factory using dependency injection.
"""
from typing import TYPE_CHECKING

from vello.core import config

if TYPE_CHECKING:
    from vello.email.base import EmailProvider


def get_email_provider() -> "EmailProvider":
    """
    Factory function to get the configured email provider.
    Uses dependency injection - returns a provider instance based on config.

    Returns:
        An instance implementing the EmailProvider protocol
    """
    provider_name = config.EMAIL_PROVIDER.lower()

    if provider_name == "smtp":
        from vello.email.smtp_provider import create_smtp_provider
        return create_smtp_provider()

    elif provider_name == "sendgrid":
        # Future implementation
        raise NotImplementedError("SendGrid provider not yet implemented")

    elif provider_name == "ses":
        # Future implementation
        raise NotImplementedError("AWS SES provider not yet implemented")

    else:
        raise ValueError(f"Unknown email provider: {provider_name}")


# Example of how to use with dependency injection:
#
# def send_campaign_email(provider: EmailProvider, recipient: str, subject: str, body: str):
#     result = provider.send_email(to=recipient, subject=subject, body_text=body)
#     return result
#
# # In your code:
# provider = get_email_provider()
# send_campaign_email(provider, "user@example.com", "Hello", "World")

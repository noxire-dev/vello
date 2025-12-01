"""
Email provider protocol using structural typing (Protocol).
This allows dependency injection without inheritance.
"""
from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class EmailResult:
    """Result of an email send operation."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class EmailProvider(Protocol):
    """
    Protocol for email providers.
    Any class implementing these methods can be used as an email provider.
    No inheritance required - just implement the methods.
    """

    def send_email(
        self,
        to: str,
        subject: str,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
        **kwargs
    ) -> EmailResult:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body
            from_email: Sender email (optional, uses default if not provided)
            **kwargs: Provider-specific options

        Returns:
            EmailResult with success status, message_id, and error if any
        """
        ...

    def validate_config(self) -> bool:
        """
        Validate that the provider is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        ...

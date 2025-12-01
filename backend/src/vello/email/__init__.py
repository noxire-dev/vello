"""
Email service package.
Provides email sending functionality with pluggable providers.
"""
from vello.email.base import EmailProvider, EmailResult
from vello.email.factory import get_email_provider

__all__ = ['get_email_provider', 'EmailProvider', 'EmailResult']

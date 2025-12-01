"""
Vello - Automation-First Email Outreach System
Main package initialization.
"""
from vello.core import config, db, models
from vello.email import EmailProvider, EmailResult, get_email_provider
from vello.services import CampaignManager, analyze_intent
from vello.utils import TemplateLoader, get_template_loader

__all__ = [
    'models',
    'db',
    'config',
    'analyze_intent',
    'CampaignManager',
    'get_template_loader',
    'TemplateLoader',
    'get_email_provider',
    'EmailProvider',
    'EmailResult',
]

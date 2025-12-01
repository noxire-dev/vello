"""
Example usage of the email service with dependency injection.
"""
import sys
from pathlib import Path

# Add backend/src to path so we can import vello package
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from vello.core import config, db
from vello.email import EmailProvider, get_email_provider


def send_campaign_email(
    provider: EmailProvider,
    recipient_email: str,
    subject: str,
    body_text: str,
    body_html: str = None
):
    """
    Send a campaign email using the injected provider.

    Args:
        provider: Email provider instance (injected)
        recipient_email: Recipient's email address
        subject: Email subject
        body_text: Plain text body
        body_html: HTML body (optional)
    """
    result = provider.send_email(
        to=recipient_email,
        subject=subject,
        body_text=body_text,
        body_html=body_html
    )

    if result.success:
        print(f"✓ Email sent to {recipient_email}")
        print(f"  Message ID: {result.message_id}")
    else:
        print(f"✗ Failed to send email to {recipient_email}")
        print(f"  Error: {result.error}")

    return result


if __name__ == "__main__":
    print("Email Service Example")
    print("=" * 50)

    # Check if email is configured
    if not config.EMAIL_HOST_USER or not config.EMAIL_HOST_PASSWORD:
        print("\n⚠️  Email configuration not found!")
        print("\nTo use this example, create a .env file in the backend/ directory with:")
        print("  EMAIL_PROVIDER=smtp")
        print("  EMAIL_HOST=smtp.gmail.com")
        print("  EMAIL_PORT=587")
        print("  EMAIL_HOST_USER=your-email@gmail.com")
        print("  EMAIL_HOST_PASSWORD=your-app-password")
        print("\nNote: For Gmail, you need to use an App Password, not your regular password.")
        print("      See: https://support.google.com/accounts/answer/185833")
        sys.exit(0)

    try:
        # Initialize database (creates vello.db if it doesn't exist)
        db.init_db()
        print("✓ Database initialized")

        # Get the configured provider (dependency injection)
        email_provider = get_email_provider()

        # Validate configuration
        if not email_provider.validate_config():
            print("\n❌ Error: Email provider is not properly configured")
            print("Please check your .env file settings.")
            sys.exit(1)

        print(f"\n✓ Email provider configured: {config.EMAIL_PROVIDER}")
        print(f"✓ SMTP host: {config.EMAIL_HOST}:{config.EMAIL_PORT}")
        print(f"✓ From email: {config.EMAIL_HOST_USER}")

        # Send a test email
        print("\nSending test email...")

        # Personal message content
        body_text = """Hey! 👋

If you're seeing this, Vello is working to some extent! 🎉

This is a test email sent through the Vello email outreach system. Insane right?

Vello is an automation-first email outreach engine designed to handle
cold email campaigns programmatically with smart automation and
deliverability-safe sending patterns.

---

Built with love by your beloved friend/brother/CTO,
Sina 'Noxire' Dilek

Love you gng <3

---
This is a test email from the Vello email outreach system.
Powered by Vello • Automation-First Email Outreach
"""

        body_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Vello Test Email</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {{font-family: Arial, sans-serif !important;}}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f3f4f6;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="max-width: 600px; background-color: #ffffff; border-radius: 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
                    <!-- Header with gradient -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 50px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;">
                                Hey! 👋
                            </h1>
                        </td>
                    </tr>

                    <!-- Main content -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px 0; font-size: 18px; line-height: 1.6; color: #1f2937;">
                                If you're seeing this, <span style="background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%); padding: 4px 8px; border-radius: 6px; font-weight: 600; color: #1f2937;">Vello is working to some extent!</span> (Don't mind the emoji, it's for testing)
                            </p>

                            <div style="text-align: center; margin: 30px 0;">
                                <span style="font-size: 48px;">🎉</span>
                            </div>

                            <p style="margin: 0 0 30px 0; font-size: 16px; line-height: 1.7; color: #4b5563;">
                                This is a test email sent through the <strong style="color: #667eea;">Vello</strong> email outreach system. Insane right?
                            </p>

                            <!-- Info box -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f9fafb; border-left: 4px solid #667eea; border-radius: 8px; margin: 30px 0;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #6b7280;">
                                            <strong style="color: #667eea;">Vello</strong> is an automation-first email outreach engine designed to handle cold email campaigns programmatically with smart automation and deliverability-safe sending patterns.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Signature section -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-top: 40px; padding-top: 30px; border-top: 2px solid #e5e7eb;">
                                <tr>
                                    <td>
                                        <p style="margin: 0 0 10px 0; font-size: 16px; line-height: 1.6; color: #1f2937;">
                                            Built with love by your beloved friend/brother/CTO,
                                        </p>
                                        <p style="margin: 0 0 20px 0; font-size: 20px; font-weight: 700; color: #667eea; letter-spacing: -0.3px;">
                                            Sina 'Noxire' Dilek
                                        </p>
                                        <p style="margin: 0; font-size: 16px; color: #6b7280; font-style: italic;">
                                            Love you gng <3
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px 40px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0; font-size: 12px; color: #9ca3af; line-height: 1.5;">
                                This is a test email from the Vello email outreach system.<br>
                                Powered by <strong style="color: #667eea;">Vello</strong> • Automation-First Email Outreach
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

        result = send_campaign_email(
            provider=email_provider,
            recipient_email="ibrahim.albajjeh003@gmail.com",
            subject="🚀 Vello is Working! (Test from Sina)",
            body_text=body_text,
            body_html=body_html
        )

        if result.success:
            print("\n✅ Email sent successfully!")
        else:
            print(f"\n❌ Failed to send email: {result.error}")
            print("\nCommon issues:")
            print("  - Invalid email credentials")
            print("  - Gmail requires App Passwords (not regular passwords)")
            print("  - SMTP server settings may be incorrect")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. The vello package is installed: pip install -e .")
        print("  2. Your .env file is in the backend/ directory")
        print("  3. All required environment variables are set")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("\nTo switch providers, change EMAIL_PROVIDER in .env:")
    print("  EMAIL_PROVIDER=smtp      # Use SMTP (Gmail, etc.)")
    print("  EMAIL_PROVIDER=sendgrid  # Use SendGrid (when implemented)")
    print("  EMAIL_PROVIDER=ses       # Use AWS SES (when implemented)")

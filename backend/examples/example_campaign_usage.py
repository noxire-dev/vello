"""
Example usage of the CampaignManager.
"""

import sys
from pathlib import Path


# Add backend/src to path so we can import vello package
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from vello.core import db
from vello.email import get_email_provider
from vello.services import CampaignManager


def example_create_and_run_campaign():
    """Example of creating a campaign and processing deliveries."""

    # Initialize database
    db.init_db()

    # Get email provider
    email_provider = get_email_provider()

    # Create campaign manager
    manager = CampaignManager(email_provider=email_provider)

    # Create a campaign with steps
    print("Creating campaign...")
    campaign = manager.create_campaign(
        name="Welcome Series Campaign",
        steps=[
            {
                "position": 0,
                "delay_minutes": 0,  # Send immediately
                "subject": "Welcome to Vello!",
                "body_text": "Hi {{name}}, welcome to Vello!",
                "body_html": "<h1>Welcome {{name}}!</h1><p>Thanks for joining Vello.</p>",
            },
            {
                "position": 1,
                "delay_minutes": 1440,  # 24 hours later
                "subject": "Follow-up: How can we help?",
                "body_text": "Hi {{name}}, just checking in. How can we help?",
                "body_html": "<p>Hi {{name}},</p><p>Just checking in. How can we help?</p>",
            },
        ],
    )
    print(f"✓ Campaign created with ID: {campaign.id}")

    # Add recipients
    print("\nAdding recipients...")
    count = manager.add_recipients(
        campaign_id=campaign.id,
        emails=["test1@example.com", "test2@example.com"],
        names={"test1@example.com": "John Doe", "test2@example.com": "Jane Smith"},
    )
    print(f"✓ Added {count} recipients")

    # Initialize deliveries (creates pending deliveries for first step)
    print("\nInitializing deliveries...")
    delivery_count = manager.initialize_campaign_deliveries(campaign.id)
    print(f"✓ Created {delivery_count} pending deliveries")

    # Process pending deliveries (sends emails that are ready)
    print("\nProcessing pending deliveries...")
    sent_count = manager.process_pending_deliveries(campaign_id=campaign.id)
    print(f"✓ Sent {sent_count} emails")

    # Get campaign statistics
    print("\nCampaign Statistics:")
    stats = manager.get_campaign_stats(campaign.id)
    print(f"  Campaign: {stats['campaign_name']}")
    print(f"  Total Recipients: {stats['total_recipients']}")
    print(f"  Active Recipients: {stats['active_recipients']}")
    print(f"  Deliveries Sent: {stats['deliveries']['sent']}")
    print(f"  Deliveries Pending: {stats['deliveries']['pending']}")
    print(f"  Responses: {stats['responses']['total']}")

    # Example: Handle a response
    print("\nHandling example response...")
    status = manager.handle_response(
        recipient_email="test1@example.com",
        content="Yes, I am interested!",
        delivery_id=None,
    )
    print(f"✓ Response classified as: {status.value}")

    print("\n✅ Campaign example completed!")


if __name__ == "__main__":
    try:
        example_create_and_run_campaign()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

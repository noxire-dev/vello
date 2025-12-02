"""
Campaign Manager - Orchestrates campaign execution, scheduling, and follow-ups.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from vello.core.models import (
    Campaign,
    CampaignStep,
    Recipient,
    Delivery,
    DeliveryStatus,
    ResponseStatus,
)
from vello.core import db
from vello.core import config
from vello.email import EmailProvider, EmailResult
from vello.utils import TemplateLoader, html_to_text
from vello.services import analyze_intent


class CampaignManager:
    """
    Manages campaign execution, scheduling, and follow-ups.

    Coordinates between:
    - Campaign models (Campaign, CampaignStep, Recipient, Delivery)
    - Email providers (SMTP, SendGrid, etc.)
    - Template loader (Jinja2 templates)
    - Analysis service (response intent classification)
    - Automation flags (from config)
    """

    def __init__(
        self,
        email_provider: EmailProvider,
        template_loader: Optional[TemplateLoader] = None,
        db_session: Optional[Session] = None,
    ):
        """
        Initialize CampaignManager.

        Args:
            email_provider: Email provider instance (dependency injection)
            template_loader: Template loader instance (optional, creates default if None)
            db_session: Database session (optional, uses get_db() if None)
        """
        self.email_provider = email_provider
        self.template_loader = template_loader
        self.db_session = db_session

    def _get_db(self) -> Session:
        """Get database session."""
        if self.db_session:
            return self.db_session
        return next(db.get_db())

    def create_campaign(self, name: str, steps: List[Dict[str, Any]]) -> Campaign:
        """
        Create a new campaign with steps.

        Args:
            name: Campaign name
            steps: List of step dictionaries with keys:
                  - position: int (0, 1, 2, ...)
                  - delay_minutes: int
                  - subject: str
                  - body_text: Optional[str]
                  - body_html: Optional[str]
                  - template_path: Optional[str] (if using templates)

        Returns:
            Created Campaign instance
        """
        session = self._get_db()
        try:
            campaign = Campaign(name=name, created_at=datetime.utcnow())
            session.add(campaign)
            session.flush()  # Get campaign.id

            for step_data in steps:
                step = CampaignStep(
                    campaign_id=campaign.id,
                    position=step_data["position"],
                    delay_minutes=step_data["delay_minutes"],
                    subject=step_data["subject"],
                    body_text=step_data.get("body_text"),
                    body_html=step_data.get("body_html"),
                )
                session.add(step)

            session.commit()
            return campaign
        except Exception as e:
            session.rollback()
            raise

    def add_recipients(
        self,
        campaign_id: int,
        emails: List[str],
        names: Optional[Dict[str, str]] = None,
        vars_json: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> int:
        """
        Add recipients to a campaign.

        Args:
            campaign_id: Campaign ID
            emails: List of email addresses
            names: Optional dict mapping email -> name
            vars_json: Optional dict mapping email -> variables dict (for templates)

        Returns:
            Number of recipients added
        """
        session = self._get_db()
        try:
            count = 0
            for email in emails:
                # Check if already exists
                existing = (
                    session.query(Recipient)
                    .filter_by(campaign_id=campaign_id, email=email)
                    .first()
                )

                if existing:
                    continue

                recipient = Recipient(
                    campaign_id=campaign_id,
                    email=email,
                    name=names.get(email) if names else None,
                    vars_json=str(vars_json.get(email))
                    if vars_json and vars_json.get(email)
                    else None,
                    suppressed=False,
                    created_at=datetime.utcnow(),
                )
                session.add(recipient)
                count += 1

            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise

    def process_pending_deliveries(self, campaign_id: Optional[int] = None) -> int:
        """
        Process pending deliveries that are ready to send.

        Checks for deliveries where:
        - Status is PENDING
        - Delay time has elapsed
        - Recipient is not suppressed

        Args:
            campaign_id: Optional campaign ID to filter by (None = all campaigns)

        Returns:
            Number of emails sent
        """
        session = self._get_db()
        try:
            # Query pending deliveries
            query = (
                session.query(Delivery)
                .join(Recipient)
                .join(CampaignStep)
                .filter(
                    Delivery.status == DeliveryStatus.PENDING,
                    not Recipient.suppressed,
                )
            )

            if campaign_id:
                query = query.filter(Recipient.campaign_id == campaign_id)

            pending_deliveries = query.all()

            sent_count = 0
            for delivery in pending_deliveries:
                # Check if delay has elapsed
                step = delivery.step
                recipient = delivery.recipient
                campaign = recipient.campaign

                # Calculate when this should be sent
                # First step: send immediately after recipient creation
                # Subsequent steps: after previous step + delay
                if step.position == 0:
                    # First step - check if recipient was created long enough ago
                    time_since_creation = datetime.utcnow() - recipient.created_at
                    if time_since_creation.total_seconds() < step.delay_minutes * 60:
                        continue
                else:
                    # Find previous step delivery
                    prev_step = (
                        session.query(CampaignStep)
                        .filter_by(campaign_id=campaign.id, position=step.position - 1)
                        .first()
                    )

                    if prev_step:
                        prev_delivery = (
                            session.query(Delivery)
                            .filter_by(recipient_id=recipient.id, step_id=prev_step.id)
                            .first()
                        )

                        if (
                            not prev_delivery
                            or prev_delivery.status != DeliveryStatus.SENT
                        ):
                            continue

                        if prev_delivery.sent_at:
                            time_since_prev = datetime.utcnow() - prev_delivery.sent_at
                            if (
                                time_since_prev.total_seconds()
                                < step.delay_minutes * 60
                            ):
                                continue

                # Send the email
                result = self._send_campaign_email(delivery, step, recipient)

                if result.success:
                    delivery.status = DeliveryStatus.SENT
                    delivery.sent_at = datetime.utcnow()
                    delivery.message_id = result.message_id
                    sent_count += 1
                else:
                    delivery.status = DeliveryStatus.FAILED
                    delivery.last_error = result.error

            session.commit()
            return sent_count
        except Exception as e:
            session.rollback()
            raise

    def _send_campaign_email(
        self, delivery: Delivery, step: CampaignStep, recipient: Recipient
    ) -> EmailResult:
        """
        Send a campaign email for a specific delivery.

        Args:
            delivery: Delivery record
            step: Campaign step
            recipient: Recipient

        Returns:
            EmailResult from email provider
        """
        # Get template variables if available
        variables = {}
        if recipient.vars_json:
            import json

            try:
                variables = json.loads(recipient.vars_json)
            except Exception:
                pass

        # Add default variables
        variables.setdefault("name", recipient.name or recipient.email.split("@")[0])
        variables.setdefault("email", recipient.email)

        # Use template if body_html/body_text not set
        body_html = step.body_html
        body_text = step.body_text

        # Auto-generate text from HTML if HTML exists but text doesn't
        if body_html and not body_text:
            body_text = html_to_text(body_html)

        # TODO: If step has template_path, use template_loader
        # For now, use direct body_html/body_text

        # Send email
        result = self.email_provider.send_email(
            to=recipient.email,
            subject=step.subject,
            body_text=body_text,
            body_html=body_html,
        )

        return result

    def handle_response(
        self, recipient_email: str, content: str, delivery_id: Optional[int] = None
    ) -> ResponseStatus:
        """
        Handle an incoming email response.

        Args:
            recipient_email: Email address of the responder
            content: Response content
            delivery_id: Optional delivery ID this response is for

        Returns:
            ResponseStatus enum value
        """
        session = self._get_db()
        try:
            # Find recipient
            recipient = (
                session.query(Recipient).filter_by(email=recipient_email).first()
            )
            if not recipient:
                return ResponseStatus.PENDING

            # Analyze intent
            status = analyze_intent(content)

            # Create response record
            from vello.core.models import Response

            response = Response(
                recipient_id=recipient.id,
                delivery_id=delivery_id,
                content=content,
                status=status,
                created_at=datetime.utcnow(),
            )
            session.add(response)

            # Auto-actions based on config
            if (
                config.AUTO_UNSUBSCRIBE_ON_REQUEST
                and status == ResponseStatus.UNSUBSCRIBED
            ):
                recipient.suppressed = True
                # Stop all pending deliveries for this recipient
                pending_deliveries = (
                    session.query(Delivery)
                    .join(CampaignStep)
                    .filter(
                        Delivery.recipient_id == recipient.id,
                        Delivery.status == DeliveryStatus.PENDING,
                    )
                    .all()
                )
                for delivery in pending_deliveries:
                    delivery.status = DeliveryStatus.FAILED
                    delivery.last_error = "Recipient unsubscribed"

            # TODO: Handle positive/negative responses based on AUTO_ACT_ON_RESPONSE

            session.commit()
            return status
        except Exception as e:
            session.rollback()
            raise

    def get_campaign_stats(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get statistics for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            Dictionary with campaign statistics
        """
        session = self._get_db()
        campaign = session.query(Campaign).filter_by(id=campaign_id).first()
        if not campaign:
            return {}

        recipients = session.query(Recipient).filter_by(campaign_id=campaign_id).all()
        total_recipients = len(recipients)
        suppressed = sum(1 for r in recipients if r.suppressed)

        # Count deliveries by status
        deliveries = (
            session.query(Delivery)
            .join(Recipient)
            .filter(Recipient.campaign_id == campaign_id)
            .all()
        )

        sent = sum(1 for d in deliveries if d.status == DeliveryStatus.SENT)
        pending = sum(1 for d in deliveries if d.status == DeliveryStatus.PENDING)
        failed = sum(1 for d in deliveries if d.status == DeliveryStatus.FAILED)

        # Count responses
        from vello.core.models import Response

        responses = (
            session.query(Response)
            .join(Recipient)
            .filter(Recipient.campaign_id == campaign_id)
            .all()
        )

        positive = sum(1 for r in responses if r.status == ResponseStatus.POSITIVE)
        negative = sum(1 for r in responses if r.status == ResponseStatus.NEGATIVE)
        unsubscribed = sum(
            1 for r in responses if r.status == ResponseStatus.UNSUBSCRIBED
        )

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "total_recipients": total_recipients,
            "suppressed": suppressed,
            "active_recipients": total_recipients - suppressed,
            "deliveries": {
                "sent": sent,
                "pending": pending,
                "failed": failed,
                "total": len(deliveries),
            },
            "responses": {
                "positive": positive,
                "negative": negative,
                "unsubscribed": unsubscribed,
                "total": len(responses),
            },
        }

    def initialize_campaign_deliveries(self, campaign_id: int) -> int:
        """
        Initialize delivery records for all recipients in a campaign.
        Creates pending deliveries for the first step of each recipient.

        Args:
            campaign_id: Campaign ID

        Returns:
            Number of deliveries created
        """
        session = self._get_db()
        try:
            campaign = session.query(Campaign).filter_by(id=campaign_id).first()
            if not campaign:
                return 0

            # Get first step
            first_step = (
                session.query(CampaignStep)
                .filter_by(campaign_id=campaign_id, position=0)
                .first()
            )

            if not first_step:
                return 0

            # Get all active recipients
            recipients = (
                session.query(Recipient)
                .filter_by(campaign_id=campaign_id, suppressed=False)
                .all()
            )

            count = 0
            for recipient in recipients:
                # Check if delivery already exists
                existing = (
                    session.query(Delivery)
                    .filter_by(recipient_id=recipient.id, step_id=first_step.id)
                    .first()
                )

                if not existing:
                    delivery = Delivery(
                        step_id=first_step.id,
                        recipient_id=recipient.id,
                        status=DeliveryStatus.PENDING,
                        created_at=datetime.utcnow(),
                    )
                    session.add(delivery)
                    count += 1

            session.commit()
            return count
        except Exception:
            session.rollback()
            raise

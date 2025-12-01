# models.py
import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class DeliveryStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class ResponseStatus(enum.Enum):
    PENDING = "pending"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    OPENED = "opened"
    CLICKED = "clicked"
    UNOPENED = "unopened"
    UNCLICKED = "unclicked"
    UNSUBSCRIBED = "unsubscribed"
    FAILED = "failed"


class Campaign(Base):
    __tablename__ = "campaign"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    steps = relationship("CampaignStep", back_populates="campaign", cascade="all, delete-orphan", order_by="CampaignStep.position")
    recipients = relationship("Recipient", back_populates="campaign", cascade="all, delete-orphan")

class CampaignStep(Base):
    __tablename__ = "campaign_step"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaign.id"), nullable=False)
    position = Column(Integer, nullable=False)  # 0,1,2,...
    delay_minutes = Column(Integer, nullable=False, default=0)
    subject = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)

    campaign = relationship("Campaign", back_populates="steps")
    deliveries = relationship("Delivery", back_populates="step", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("campaign_id", "position", name="uq_step_pos"),)

class Recipient(Base):
    __tablename__ = "recipient"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaign.id"), nullable=False, index=True)
    email = Column(String(320), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    vars_json = Column(Text, nullable=True)  # raw JSON string of CSV row
    suppressed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="recipients")
    deliveries = relationship("Delivery", back_populates="recipient", cascade="all, delete-orphan")

    # Prevent same email in same campaign
    __table_args__ = (UniqueConstraint("campaign_id", "email", name="uq_campaign_recipient_email"),)

class Delivery(Base):
    __tablename__ = "delivery"
    id = Column(Integer, primary_key=True)
    # Link to specific step ID for safety, not just position
    step_id = Column(Integer, ForeignKey("campaign_step.id"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("recipient.id"), nullable=False, index=True)

    status = Column(Enum(DeliveryStatus), nullable=False, default=DeliveryStatus.PENDING)
    last_error = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    message_id = Column(String(255), nullable=True)

    step = relationship("CampaignStep", back_populates="deliveries")
    recipient = relationship("Recipient", back_populates="deliveries")

    # Ensure one delivery record per recipient per step
    __table_args__ = (UniqueConstraint("recipient_id", "step_id", name="uq_recipient_step"),)

class Response(Base):
    __tablename__ = "response"
    id = Column(Integer, primary_key=True)
    recipient_id = Column(Integer, ForeignKey("recipient.id"), nullable=False, index=True)
    delivery_id = Column(Integer, ForeignKey("delivery.id"), nullable=True, index=True)

    content = Column(Text, nullable=False)
    status = Column(Enum(ResponseStatus), nullable=False, default=ResponseStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipient = relationship("Recipient")
    delivery = relationship("Delivery")


class Lead(Base):
    __tablename__ = "lead"
    id = Column(Integer, primary_key=True)

    email = Column(String(320), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    company = Column(String(200), nullable=True)
    title = Column(String(200), nullable=True)
    phone = Column(String(200), nullable=True)
    address = Column(String(200), nullable=True)
    city = Column(String(200), nullable=True)
    state = Column(String(200), nullable=True)
    zip = Column(String(200), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (UniqueConstraint("email", name="uq_lead_email"),)

class OutboundMailbox(Base):
    id = Column(Integer, primary_key=True)
    label = Column(String)  # "John - Gmail #1" (optional)
    email_address = Column(String, unique=True)
    provider = Column(String)  # smtp, gmail, outlook

    # Auth
    smtp_host = Column(String)
    smtp_port = Column(Integer)
    username = Column(String)
    password = Column(String)  # encrypted or env reference

    # Sending logic
    daily_limit = Column(Integer, default=150)
    sends_today = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    last_reset_at = Column(DateTime)

    # Warmup
    warmup_enabled = Column(Boolean, default=False)
    warmup_stage = Column(Integer, default=0)
    warmup_step_size = Column(Integer, default=3)

    # Health & Automation
    health_score = Column(Integer, default=1)
    disabled = Column(Boolean, default=False)
    failure_count = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("email_address", name="uq_outbound_mailbox_email_address"),)

    def get_remaining_sends(self) -> int:
        return self.daily_limit - self.sends_today

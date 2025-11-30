# Vello – Email Outreach System (MVP)

**Vello** is a purpose-built email outreach system originally developed for internal use at **NovaLare**. It provides a minimal but extensible foundation for building, scheduling, and analyzing cold email campaigns. The project is released under a **source-available license**, allowing community review and contributions while prohibiting commercial use or hosting Vello as a service.

This repository is intended as an early-stage MVP to support internal outreach workflows and serve as the foundation for a future standalone SaaS product.

---

## Features

- **Multi-step Campaigns**
  Create sequential outreach flows with configurable delays between steps.

- **Lead and Recipient Management**
  Import and manage leads with structured variables for template substitution.

- **Email Delivery Tracking**
  Log send attempts, results, and errors for each email sent.

- **Response Analysis**
  Detect intent in replies using basic linguistic classification.

- **Template Rendering**
  Jinja2-based HTML/text templates with variable injection.

- **Lightweight Data Layer**
  SQLite-backed storage suitable for local development and small deployments.

---

## Project Structure

```
vello/
├── models.py               # SQLAlchemy ORM models
├── db.py                   # Database session handling and initialization
├── config.py               # Environment-driven configuration loader
├── analysis.py             # Response intent analysis
├── template_loader.py      # Email template rendering utilities
├── api/
│   └── add_new_lead.py     # Example API endpoint for managing leads
├── email/                  # Email sending and delivery utilities
├── templates/              # Email templates
└── examples/               # Example scripts and usage patterns
```

---

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

Clone the repository:

```bash
git clone <your-repo-url>
cd vello
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy and configure environment variables:

```bash
cp .env.example .env
```

Example `.env` configuration:

```env
DATABASE_URL=sqlite:///vello.db
DEBUG=True

EMAIL_PROVIDER=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True

SYSTEM_AUTO_ACT_ON_RESPONSE=False
SYSTEM_AUTO_ROTATE_INBOX=False
SYSTEM_AUTO_GENERATE_TXT_FROM_HTML=False
```

Initialize the database:

```python
from db import init_db
init_db()
```

---

## Usage Examples

### Creating a Campaign

```python
from db import get_session
from models import Campaign, CampaignStep

with get_session() as session:
    campaign = Campaign(name="Initial Outreach")

    step = CampaignStep(
        campaign=campaign,
        position=0,
        delay_minutes=0,
        subject="Introduction",
        body_html="<p>Hello {{name}},</p>"
    )

    session.add(campaign)
    session.commit()
```

### Adding a Recipient

```python
from db import get_session
from models import Recipient

with get_session() as session:
    recipient = Recipient(
        campaign_id=1,
        email="lead@example.com",
        name="John Doe",
        vars_json='{"company": "Acme Corp"}'
    )
    session.add(recipient)
    session.commit()
```

### Analyzing a Response

```python
from analysis import analyze_response_intent

print(analyze_response_intent(
    "Thanks for reaching out — I'm interested in learning more."
))
```

---

## Database Models

- **Campaign** – Overall outreach sequence container.
- **CampaignStep** – Individual email steps with timing and content.
- **Recipient** – Lead data and template variables.
- **Delivery** – Logs for each email send attempt.
- **Response** – Stored replies with intent classification.

---

## Configuration

All application settings are defined in `.env`. See the included example file for defaults and documentation.

---

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

This MVP uses basic SQLAlchemy models without a migration layer. For production usage, integrating Alembic is recommended.

---

## Roadmap

- Web dashboard for campaign creation and monitoring
- Delivery analytics and improved reporting
- Support for additional email providers (SES, SendGrid, Mailgun)
- A/B template testing
- Webhooks for delivery events
- Automated sending throttles and rate limits
- Unsubscribe and compliance management
- Inbox rotation and domain warmup features

---

## License

Vello is released under the **Vello Source Available License**, which allows personal and internal business use, modification, and contributions, but restricts commercial use, resale, and hosting Vello as a service.
See **LICENSE** for full terms.

---

## Contributing

Contributions are welcome. Please submit issues or pull requests via GitHub.
Before contributing, review the LICENSE and ensure your usage aligns with permitted use.

---

## Support

For questions, feedback, or issues, open a GitHub issue.

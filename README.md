# Vello – Automation-First Email Outreach System (MVP)

**Vello** is an automation-first email outreach engine developed by **NovaLare**.
It is designed to handle cold email campaigns programmatically, with an emphasis on:

- automated decision-making
- deliverability-safe sending patterns
- dynamic campaign logic
- smart response handling

Vello was originally built as an internal outreach system but is released as a **source-available project** to support transparency, community feedback, and future open-core development.

A dedicated web interface (Next.js) is planned as part of the roadmap, allowing non-technical users to manage campaigns visually.

---

## Key Concepts

### Automation-First Architecture

Vello is built around a set of configurable automation behaviors.
These control how the system:

- classifies and reacts to email responses
- rotates between sending inboxes
- generates plaintext versions of email bodies
- adjusts sending times and pacing
- warms up inboxes gradually
- cleans or maintains email lists

This approach allows Vello to operate closer to a "programmatic SDR," reducing manual workload and making high-volume outreach safer and more consistent.

### Extensible Campaign System

Campaigns consist of a sequence of steps, each with its own timing, subject, and template.
Vello is designed to be extended into more advanced workflows, including conditional branching, nurturing paths, and adaptive follow-up logic.

### Transparent and Source-Available

The application is source-available for review, auditing, and contribution.
Self-hosting for personal or internal use is permitted, while commercial hosting or resale is restricted by the Vello Source-Available License.

---

## Project Structure

This is a monorepo structure separating the Python backend and Next.js frontend:

```
vello/
├── backend/                    # Python backend
│   ├── .env                    # Environment variables
│   ├── requirements.txt        # Python dependencies
│   ├── setup.py                # Package installation config
│   ├── src/
│   │   └── vello/              # Main package
│   │       ├── core/           # Database, models, config
│   │       ├── services/       # Business logic
│   │       ├── utils/          # Utility functions
│   │       ├── email/          # Email sending providers
│   │       └── api/            # REST API endpoints
│   ├── examples/               # Usage examples
│   └── templates/              # Email templates
└── frontend/                   # Next.js web GUI (planned)
    ├── src/
    │   ├── app/                # Next.js App Router
    │   ├── components/         # React components
    │   ├── lib/                # Utilities and API client
    │   └── types/              # TypeScript types
    └── public/                 # Static assets
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

Navigate to the backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Install the package in development mode:

```bash
pip install -e .
```

Copy and configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Initialize the database:

```python
from vello.core.db import init_db
init_db()
```

---

## Configuration

All configuration is managed through `backend/.env`.

Vello exposes both standard system settings (database, SMTP configuration, debug mode) and a set of **automation flags** that control intelligent behavior. Examples include:

- automatically classifying replies (positive, neutral, negative)
- unsubscribing leads who request removal
- rotating sender inboxes
- adjusting send times to recipient local time
- protecting deliverability by pausing risky campaigns
- warming up inboxes with safe volume increases

These automation controls allow Vello to function with minimal human intervention while maintaining safe sending practices.

---

## Usage Examples

### Running Example Scripts

From the `backend` directory:

```bash
# Test intent analysis
python examples/test_analysis.py

# Test template loading
python examples/example_template_usage.py

# Test email sending (requires .env configuration)
python examples/example_email_usage.py
```

### Using the Package

```python
from vello.core.db import init_db, get_db
from vello.core.models import Campaign, Recipient
from vello.services import analyze_intent
from vello.utils import get_template_loader
from vello.email import get_email_provider

# Initialize database
init_db()

# Use services
intent = analyze_intent("Yes, I'm interested!")

# Load templates
loader = get_template_loader()
html, text = loader.render_email("welcome_series/initial_outreach", {"name": "John"})

# Send emails
provider = get_email_provider()
result = provider.send_email(
    to="user@example.com",
    subject="Hello",
    body_text="Test email"
)
```

---

## Roadmap

- Next.js web interface for managing campaigns
- Inbox rotation management via UI
- Delivery analytics and reporting
- Additional email provider support (SES, Mailgun, SendGrid)
- Template versioning and A/B testing
- Advanced follow-up and branching logic
- Webhooks and event relay
- Automated send-time optimization
- Smart lead enrichment
- Full open-core model for community extensibility

---

## License

Vello is released under the **Vello Source-Available License**, allowing personal and internal use, modification, and contribution, while prohibiting commercial resale or offering Vello as a hosted service.
See the **LICENSE** file for details.

---

## Contributing

Feedback, suggestions, and pull requests are welcome. Before contributing, review the license to ensure your use case aligns with permitted usage.

---

## Support

For issues or inquiries, please open a GitHub issue.

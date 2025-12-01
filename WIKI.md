# Vello Codebase Wiki

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Patterns](#architecture--design-patterns)
3. [Directory Structure](#directory-structure)
4. [Coding Patterns](#coding-patterns)
5. [Design Choices](#design-choices)
6. [Core Components](#core-components)
7. [Configuration System](#configuration-system)
8. [Database Models](#database-models)
9. [Email Provider System](#email-provider-system)
10. [Services & Utilities](#services--utilities)
11. [API Layer](#api-layer)

---

## Project Overview

**Vello** is an automation-first email outreach system designed for cold email campaigns. The system emphasizes:

- **Automated decision-making** - Classifies responses, manages inboxes, adjusts sending patterns
- **Deliverability-safe sending** - Warmup management, inbox rotation, pacing controls
- **Dynamic campaign logic** - Multi-step campaigns with configurable timing
- **Smart response handling** - Intent analysis, automatic unsubscription, response classification

The codebase follows a modular, extensible architecture that separates concerns and allows for easy extension.

---

## Architecture & Design Patterns

### 1. **Protocol-Based Design (Structural Typing)**

**Location**: `backend/src/vello/email/base.py`

Instead of using abstract base classes or inheritance, Vello uses Python's `Protocol` for structural typing. This allows any class that implements the required methods to be used as an email provider without explicit inheritance.

```python
class EmailProvider(Protocol):
    def send_email(...) -> EmailResult: ...
    def validate_config(self) -> bool: ...
```

**Why this pattern?**

- **Flexibility**: Providers don't need to inherit from a base class
- **Dependency Injection**: Easy to swap implementations
- **Type Safety**: Type checkers can verify protocol compliance
- **Loose Coupling**: Providers are independent implementations

### 2. **Factory Pattern**

**Location**: `backend/src/vello/email/factory.py`

The factory pattern is used to create provider instances based on configuration:

```python
def get_email_provider() -> EmailProvider:
    provider_name = config.EMAIL_PROVIDER.lower()
    if provider_name == "smtp":
        return create_smtp_provider()
    # ...
```

**Why this pattern?**

- **Centralized Creation**: Single point for provider instantiation
- **Configuration-Driven**: Provider selection based on config, not code
- **Easy Extension**: Add new providers without changing client code

### 3. **Singleton Pattern (Template Loader)**

**Location**: `backend/src/vello/utils/template_loader.py`

The template loader uses a singleton pattern via a module-level function:

```python
_loader = None

def get_template_loader() -> TemplateLoader:
    global _loader
    if _loader is None:
        _loader = TemplateLoader()
    return _loader
```

**Why this pattern?**

- **Resource Efficiency**: Jinja2 environment created once
- **Consistent State**: Same template directory across the application
- **Simple API**: Easy access via `get_template_loader()`

### 4. **Repository Pattern (Database Access)**

**Location**: `backend/src/vello/core/db.py`

Database access follows a repository-like pattern with session management:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Why this pattern?**

- **Resource Management**: Ensures database connections are properly closed
- **Dependency Injection**: Can be used with FastAPI or other frameworks
- **Transaction Safety**: Proper session lifecycle management

### 5. **Configuration Layering**

**Location**: `backend/src/vello/core/config.py`

Configuration uses a layered approach:

1. **JSON Files** (`backend/config/*.json`) - Default values
2. **Environment Variables** (`.env`) - Override JSON defaults
3. **Runtime Constants** - Final configuration values

**Why this pattern?**

- **Flexibility**: Different configs for dev/staging/prod
- **Security**: Sensitive values in `.env` (not committed)
- **Defaults**: JSON files provide sensible defaults
- **Override Capability**: Environment variables take precedence

---

## Directory Structure

```
backend/
├── config/                      # Configuration JSON files
│   ├── automation.json          # Automation behavior flags
│   ├── warmup.json              # Warmup manager settings
│   └── user.json                # User-specific config (empty by default)
│
├── src/vello/                   # Main package
│   ├── __init__.py              # Package exports
│   │
│   ├── core/                    # Core functionality
│   │   ├── __init__.py          # Core module exports
│   │   ├── config.py            # Configuration management
│   │   ├── db.py                # Database setup & session management
│   │   └── models.py            # SQLAlchemy ORM models
│   │
│   ├── email/                   # Email provider system
│   │   ├── __init__.py          # Email module exports
│   │   ├── base.py              # EmailProvider protocol & EmailResult
│   │   ├── factory.py           # Provider factory function
│   │   ├── smtp_provider.py     # SMTP implementation
│   │   └── sendgrid_provider.py # SendGrid implementation (stub)
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py          # Services exports
│   │   ├── analysis.py          # Intent analysis (response classification)
│   │   └── warmup_manager.py    # Warmup logic (empty, planned)
│   │
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py          # Utils exports
│   │   └── template_loader.py   # Jinja2 template loading
│   │
│   └── api/                     # API endpoints
│       ├── __init__.py          # API exports
│       └── add_new_lead.py      # Lead import functionality
│
├── examples/                    # Usage examples
│   ├── example_email_usage.py
│   ├── example_template_usage.py
│   └── test_analysis.py
│
├── templates/                   # Email templates (Jinja2)
│   └── [template files]
│
├── .env                         # Environment variables (not in git)
├── requirements.txt             # Python dependencies
└── setup.py                     # Package installation config
```

---

## Coding Patterns

### 1. **Module Organization**

Each package follows a consistent structure:

- `__init__.py` - Exports public API
- Implementation files - Actual functionality
- Clear separation of concerns

**Example**: `vello/email/__init__.py`

```python
from vello.email.base import EmailProvider, EmailResult
from vello.email.factory import get_email_provider

__all__ = ['get_email_provider', 'EmailProvider', 'EmailResult']
```

### 2. **Type Hints**

The codebase uses type hints throughout for better IDE support and type checking:

```python
def send_email(
    self,
    to: str,
    subject: str,
    body_text: Optional[str] = None,
    **kwargs
) -> EmailResult:
```

### 3. **Dataclasses for Data Transfer**

`EmailResult` uses `@dataclass` for clean data structures:

```python
@dataclass
class EmailResult:
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
```

### 4. **Error Handling**

Providers return `EmailResult` objects instead of raising exceptions:

```python
try:
    # Send email
    return EmailResult(success=True, message_id=message_id)
except Exception as e:
    return EmailResult(success=False, error=str(e))
```

**Why?**

- **Consistent API**: All providers return the same result type
- **Error Information**: Errors are captured, not lost
- **Non-Breaking**: Callers can handle errors without try/except

### 5. **Enum Usage**

Status values use Python enums for type safety:

```python
class DeliveryStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
```

### 6. **Path Resolution**

Template and config paths use relative resolution from file location:

```python
_backend_dir = Path(__file__).parent.parent.parent.parent
TEMPLATE_DIR = _backend_dir / "templates"
```

**Why?**

- **Portability**: Works regardless of working directory
- **Reliability**: Paths resolve correctly in different environments

---

## Design Choices

### 1. **Protocol Over Inheritance**

**Decision**: Use `Protocol` instead of abstract base classes for email providers.

**Rationale**:

- Providers don't share implementation code
- Each provider (SMTP, SendGrid, SES) has different dependencies
- Protocol allows duck typing - "if it quacks like a duck, it's a duck"
- Easier to test with mocks

**Trade-offs**:

- ✅ More flexible
- ✅ Less coupling
- ❌ No shared implementation (but providers don't need it)

### 2. **Factory Function Over Class**

**Decision**: Use a simple factory function instead of a factory class.

**Rationale**:

- Simple use case - just selecting a provider type
- No need for complex factory hierarchies
- Function is easier to test and mock
- Matches Python's "simple is better" philosophy

**Trade-offs**:

- ✅ Simple and straightforward
- ✅ Easy to understand
- ❌ Less extensible for complex scenarios (but not needed here)

### 3. **SQLAlchemy ORM**

**Decision**: Use SQLAlchemy ORM instead of raw SQL or other ORMs.

**Rationale**:

- Industry standard for Python
- Excellent relationship handling
- Good migration support
- Type-safe query building
- Works with multiple database backends

**Trade-offs**:

- ✅ Powerful and flexible
- ✅ Good documentation
- ❌ Slight performance overhead (acceptable for this use case)

### 4. **Jinja2 for Templates**

**Decision**: Use Jinja2 for email template rendering.

**Rationale**:

- Industry standard templating engine
- Powerful template inheritance
- Good security features (auto-escaping)
- Familiar syntax
- Works well with HTML and text templates

**Trade-offs**:

- ✅ Feature-rich
- ✅ Secure by default
- ❌ Learning curve (but minimal for simple use cases)

### 5. **JSON + Environment Variable Config**

**Decision**: Use JSON files for defaults, environment variables for overrides.

**Rationale**:

- JSON files provide readable defaults
- Environment variables for secrets (not committed)
- Easy to override in different environments
- Supports 12-factor app principles

**Trade-offs**:

- ✅ Flexible configuration
- ✅ Secure (secrets in .env)
- ❌ Two sources of truth (but clear precedence rules)

### 6. **Separate Config Files for Features**

**Decision**: Split configuration into `automation.json` and `warmup.json`.

**Rationale**:

- Logical grouping of related settings
- Easy to understand what each file controls
- Can be managed separately
- Clear separation of concerns

**Trade-offs**:

- ✅ Organized and maintainable
- ✅ Easy to find relevant config
- ❌ More files to manage (but better organization)

### 7. **Enum for Status Values**

**Decision**: Use Python enums for status values instead of strings or integers.

**Rationale**:

- Type safety - can't use invalid values
- IDE autocomplete support
- Self-documenting code
- Database storage as strings (readable)

**Trade-offs**:

- ✅ Type-safe
- ✅ Self-documenting
- ❌ Slightly more verbose (but worth it)

### 8. **Result Objects Instead of Exceptions**

**Decision**: Email providers return `EmailResult` objects instead of raising exceptions.

**Rationale**:

- Consistent API across all providers
- Errors are part of the return value, not exceptional cases
- Easier to handle in batch operations
- More functional programming style

**Trade-offs**:

- ✅ Consistent error handling
- ✅ Easier batch processing
- ❌ Must check `success` field (but clear and explicit)

---

## Core Components

### Configuration (`core/config.py`)

**Purpose**: Centralized configuration management with layered defaults.

**Key Features**:

- Loads from JSON files in `backend/config/`
- Overrides with environment variables
- Type conversion (strings to bools, ints, floats)
- Path resolution for config directory

**Usage**:

```python
from vello.core import config

if config.AUTO_CLASSIFY_RESPONSES:
    # Classify responses automatically
```

### Database (`core/db.py`)

**Purpose**: SQLAlchemy setup and session management.

**Key Features**:

- Engine creation with configurable echo (SQL logging)
- Session factory for dependency injection
- Database initialization function
- Support for in-memory database (testing)

**Usage**:

```python
from vello.core.db import init_db, get_db

init_db()  # Create tables
db = next(get_db())  # Get session
```

### Models (`core/models.py`)

**Purpose**: SQLAlchemy ORM models for database schema.

**Key Models**:

- `Campaign` - Email campaign definition
- `CampaignStep` - Individual steps in a campaign
- `Recipient` - Email recipients
- `Delivery` - Email delivery tracking
- `Response` - Email responses
- `Lead` - Lead management
- `OutboundMailbox` - Sender inbox management

**Design Notes**:

- Uses `declarative_base()` for ORM
- Relationships defined with `relationship()`
- Unique constraints prevent duplicates
- Enums for status values
- Timestamps with `datetime.utcnow`

---

## Configuration System

### Configuration Files

**Location**: `backend/config/`

1. **`automation.json`** - Automation behavior flags
   - `auto_act_on_response` - Automatically act on responses
   - `auto_classify_responses` - Classify response intent
   - `auto_unsubscribe_on_request` - Auto-unsubscribe
   - `auto_rotate_inboxes` - Rotate sending inboxes
   - `auto_adjust_send_times` - Adjust to recipient timezone
   - `auto_pause_risky_campaigns` - Pause risky campaigns

2. **`warmup.json`** - Inbox warmup settings
   - `enabled` - Enable warmup
   - `start_volume` - Initial daily send volume
   - `max_volume` - Maximum daily volume
   - `daily_increase` - Volume increase per day
   - `warmup_duration_days` - Total warmup period
   - `min_delay_minutes` / `max_delay_minutes` - Send delay range
   - `reply_rate_target` - Target reply rate
   - `bounce_rate_threshold` - Max bounce rate
   - `spam_complaint_threshold` - Max spam complaint rate

3. **`user.json`** - User-specific configuration (currently empty)

### Environment Variables

**Location**: `backend/.env`

Key variables:

- `DATABASE_URL` - Database connection string
- `EMAIL_PROVIDER` - Provider type (smtp, sendgrid, ses)
- `EMAIL_HOST`, `EMAIL_PORT` - SMTP settings
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - SMTP credentials
- `DEBUG` - Enable debug mode
- `IN_MEMORY_DB` - Use in-memory database (testing)

### Configuration Precedence

1. **Environment Variables** (highest priority)
2. **JSON Config Files** (defaults)
3. **Hardcoded Defaults** (fallback)

---

## Database Models

### Campaign System

**Campaign** → **CampaignStep** → **Delivery**

- One campaign has many steps
- Each step has many deliveries
- Steps are ordered by `position`

**Campaign** → **Recipient** → **Delivery**

- One campaign has many recipients
- Each recipient has many deliveries (one per step)

### Response Tracking

**Recipient** → **Response**

- Responses are linked to recipients
- Optional link to specific `Delivery`
- Status enum: `PENDING`, `POSITIVE`, `NEGATIVE`, `OPENED`, `CLICKED`, etc.

### Lead Management

**Lead** - Standalone lead storage

- Unique email constraint
- Rich lead data (company, title, address, etc.)
- `is_active` flag for suppression

### Inbox Management

**OutboundMailbox** - Sender inbox configuration

- SMTP credentials
- Daily sending limits
- Warmup configuration
- Health tracking
- Rotation support

### Design Patterns in Models

1. **Cascade Deletes**: Related records deleted when parent is deleted
2. **Unique Constraints**: Prevent duplicate recipients, duplicate step positions
3. **Indexes**: On foreign keys and frequently queried fields
4. **Timestamps**: `created_at`, `updated_at` for audit trail
5. **Enums**: Type-safe status values stored as strings

---

## Email Provider System

### Architecture

```
EmailProvider (Protocol)
    ↓
    ├── SMTPProvider (implements)
    ├── SendGridProvider (implements, stub)
    └── SESProvider (planned)
```

### Provider Interface

**Location**: `backend/src/vello/email/base.py`

```python
class EmailProvider(Protocol):
    def send_email(...) -> EmailResult: ...
    def validate_config(self) -> bool: ...
```

### Current Implementations

1. **SMTPProvider** (`email/smtp_provider.py`)
   - Works with Gmail, Outlook, any SMTP server
   - Supports TLS and SSL
   - Creates MIME multipart messages
   - Returns generated message ID

2. **SendGridProvider** (`email/sendgrid_provider.py`)
   - Stub implementation (not yet functional)
   - Structure ready for SendGrid API integration

### Factory Pattern

**Location**: `backend/src/vello/email/factory.py`

```python
def get_email_provider() -> EmailProvider:
    provider_name = config.EMAIL_PROVIDER.lower()
    if provider_name == "smtp":
        return create_smtp_provider()
    # ...
```

**Usage**:

```python
from vello.email import get_email_provider

provider = get_email_provider()
result = provider.send_email(to="user@example.com", ...)
```

### Adding a New Provider

1. Create provider class implementing `EmailProvider` protocol
2. Add factory function (e.g., `create_xyz_provider()`)
3. Add case in `get_email_provider()` factory
4. Add configuration variables in `config.py`

---

## Services & Utilities

### Intent Analysis (`services/analysis.py`)

**Purpose**: Classify email responses by intent.

**Algorithm**:

1. Check for unsubscribe patterns (highest priority)
2. Check for negative patterns
3. Check for positive patterns
4. Default to `PENDING` if no match

**Pattern Matching**:

- Uses regex patterns for intent detection
- Case-insensitive matching
- Priority-based classification

**Returns**: `ResponseStatus` enum value

### Template Loader (`utils/template_loader.py`)

**Purpose**: Load and render Jinja2 email templates.

**Features**:

- FileSystemLoader for template directory
- Auto-escaping for HTML/XML
- Renders both HTML and text versions
- Template listing functionality

**Usage**:

```python
from vello.utils import get_template_loader

loader = get_template_loader()
html, text = loader.render_email("welcome_series/initial_outreach", {"name": "John"})
```

**Template Structure**:

- Templates in `backend/templates/`
- HTML: `template_name.html`
- Text: `template_name.txt` (optional)

---

## API Layer

### Current Endpoints

**Location**: `backend/src/vello/api/`

1. **`add_new_lead.py`** - Lead import from CSV
   - Reads CSV file
   - Validates email addresses
   - Adds recipients to campaign
   - Handles duplicates

**Design Notes**:

- Simple file-based API (not REST yet)
- Can be called as script or imported
- Error handling with rollback

### Future API Structure

The API layer is designed to be extended with:

- REST endpoints (FastAPI planned)
- Webhook handlers
- Event processing
- Batch operations

---

## Key Design Principles

1. **Separation of Concerns**
   - Core (database, config) separate from business logic
   - Email providers isolated from campaign logic
   - Services separate from utilities

2. **Dependency Injection**
   - Providers injected via factory
   - Database sessions via generator
   - Configuration via module import

3. **Extensibility**
   - Protocol-based design allows new providers
   - Configuration-driven behavior
   - Modular package structure

4. **Type Safety**
   - Type hints throughout
   - Enums for status values
   - Protocol for interfaces

5. **Error Handling**
   - Result objects instead of exceptions (providers)
   - Try/except with rollback (database)
   - Graceful degradation (config loading)

6. **Configuration Over Code**
   - Behavior controlled by config files
   - Environment-specific settings
   - Feature flags for automation

---

## Common Patterns & Conventions

### Import Style

```python
# Package-level imports
from vello.core import config, db, models
from vello.email import get_email_provider
from vello.services import analyze_intent
```

### Naming Conventions

- **Classes**: PascalCase (`EmailProvider`, `TemplateLoader`)
- **Functions**: snake_case (`get_email_provider`, `analyze_intent`)
- **Constants**: UPPER_SNAKE_CASE (`EMAIL_PROVIDER`, `DATABASE_URL`)
- **Private**: Leading underscore (`_loader`, `_backend_dir`)

### File Organization

- One class/primary function per file (when logical)
- `__init__.py` exports public API
- Implementation details in module files

### Error Messages

- Descriptive error messages
- Include context (file paths, values)
- Return errors in result objects (providers)

---

## Extension Points

### Adding a New Email Provider

1. Create `email/xyz_provider.py`
2. Implement `EmailProvider` protocol
3. Add `create_xyz_provider()` function
4. Update `factory.py`
5. Add config variables

### Adding a New Service

1. Create `services/xyz_service.py`
2. Implement business logic
3. Export from `services/__init__.py`
4. Use in campaign logic

### Adding a New Model

1. Add model class to `core/models.py`
2. Define relationships
3. Add indexes/constraints
4. Run migration (manual for now)

### Adding Configuration

1. Add to JSON file in `backend/config/`
2. Load in `core/config.py`
3. Allow `.env` override
4. Document in this wiki

---

## Testing Considerations

### Testability Features

1. **Protocol-based providers** - Easy to mock
2. **Factory functions** - Can be replaced in tests
3. **In-memory database** - `IN_MEMORY_DB` config
4. **Dependency injection** - Easy to inject test doubles

### Test Structure (Recommended)

```
tests/
├── unit/
│   ├── test_analysis.py
│   ├── test_template_loader.py
│   └── test_providers.py
├── integration/
│   ├── test_campaign_flow.py
│   └── test_email_sending.py
└── fixtures/
    └── test_data.py
```

---

## Future Considerations

### Planned Features

1. **Warmup Manager** - Currently empty, planned implementation
2. **SendGrid Provider** - Stub exists, needs implementation
3. **REST API** - FastAPI endpoints planned
4. **Web Interface** - Next.js frontend planned
5. **Advanced Campaign Logic** - Conditional branching, nurturing paths

### Architecture Evolution

- Current: Simple, functional MVP
- Future: May need message queues for async processing
- Future: May need caching layer for templates/config
- Future: May need event system for webhooks

---

## Quick Reference

### Where to Find Things

| What | Where |
|------|-------|
| Database models | `backend/src/vello/core/models.py` |
| Configuration | `backend/src/vello/core/config.py` |
| Email providers | `backend/src/vello/email/` |
| Business logic | `backend/src/vello/services/` |
| Templates | `backend/templates/` |
| Config files | `backend/config/` |
| Examples | `backend/examples/` |

### Common Tasks

**Add a new email provider**: See [Extension Points](#extension-points)

**Change configuration**: Edit `backend/config/*.json` or `.env`

**Add a campaign step**: Create `CampaignStep` with `campaign_id` and `position`

**Classify a response**: Use `analyze_intent()` from `vello.services`

**Load a template**: Use `get_template_loader().render_email()`

**Send an email**: Use `get_email_provider().send_email()`

---

## Contributing Guidelines

When adding code to Vello:

1. **Follow existing patterns** - Use protocols, factories, type hints
2. **Update this wiki** - Document new patterns or design choices
3. **Add type hints** - All public functions should have type hints
4. **Export from `__init__.py`** - Make new functionality accessible
5. **Update config** - Add new settings to appropriate JSON files
6. **Write examples** - Add usage examples in `examples/` directory

---

*Last Updated: Based on codebase analysis*
*Maintained by: Vello Development Team*

Code Organization Plan for Vello MVP
Overview
Reorganize the Vello codebase into a monorepo structure that separates the Python backend and Next.js frontend. This will improve maintainability, make imports clearer, enable independent deployment, and prepare the codebase for future growth.

Current Structure Issues
Empty
api.py
file cluttering root directory
Core modules (
models.py
,
db.py
,
config.py
) scattered in root
No proper package structure with
init.py
files
Unclear separation between core logic, services, and utilities
No accommodation for upcoming Next.js web GUI
Proposed New Structure (Monorepo)
vello/
├── .gitignore # [MODIFY] Add Next.js ignores
├── README.md # [MODIFY] Update structure docs
├── backend/ # [NEW] Python backend
│ ├── .env # [MOVED] from root
│ ├── requirements.txt # [MOVED] from root
│ ├── setup.py # [NEW] Package installation config
│ ├── src/
│ │ └── vello/
│ │ ├── **init**.py # [NEW] Main package init
│ │ ├── core/ # [NEW] Core database and config
│ │ │ ├── **init**.py
│ │ │ ├── models.py # [MOVED] from root
│ │ │ ├── db.py # [MOVED] from root
│ │ │ └── config.py # [MOVED] from root
│ │ ├── services/ # [NEW] Business logic services
│ │ │ ├── **init**.py
│ │ │ └── analysis.py # [MOVED] from root
│ │ ├── utils/ # [NEW] Utility functions
│ │ │ ├── **init**.py
│ │ │ └── template_loader.py # [MOVED] from root
│ │ ├── email/ # [MOVED] from root
│ │ │ ├── **init**.py
│ │ │ ├── base.py
│ │ │ ├── factory.py
│ │ │ ├── smtp_provider.py
│ │ │ └── sendgrid_provider.py
│ │ └── api/ # [MOVED] from root - REST API for frontend
│ │ ├── **init**.py # [NEW]
│ │ └── add_new_lead.py
│ ├── examples/ # [MOVED] from root
│ │ ├── example_email_usage.py
│ │ ├── example_template_usage.py
│ │ └── test_analysis.py
│ └── templates/ # [MOVED] from root (email templates)
│ ├── follow_up/
│ ├── re_engagement/
│ └── welcome_series/
└── frontend/ # [NEW] Next.js web GUI
├── .env.local # [NEW] Frontend env vars
├── .gitignore # [NEW] Next.js specific
├── package.json # [NEW] Will be created by Next.js
├── next.config.js # [NEW] Will be created by Next.js
├── tsconfig.json # [NEW] TypeScript config
├── src/
│ ├── app/ # [NEW] Next.js App Router
│ ├── components/ # [NEW] React components
│ ├── lib/ # [NEW] Utilities and API client
│ └── types/ # [NEW] TypeScript types
└── public/ # [NEW] Static assets
Proposed Changes
Core Package Structure
[NEW]
setup.py
Create a minimal setup file for package installation in development mode.

[NEW]
src/vello/init.py
Main package initialization exposing key components.

Core Module
[NEW]
src/vello/core/init.py
Export core components (models, db, config).

[MOVE]
src/vello/core/models.py
Move from root
models.py
.

[MOVE]
src/vello/core/db.py
Move from root
db.py
.

[MOVE]
src/vello/core/config.py
Move from root
config.py
.

Services Module
[NEW]
src/vello/services/init.py
Export service components.

[MOVE]
src/vello/services/analysis.py
Move from root
analysis.py
and update imports.

Utils Module
[NEW]
src/vello/utils/init.py
Export utility functions.

[MOVE]
src/vello/utils/template_loader.py
Move from root
template_loader.py
and update imports.

Email Module
[MODIFY]
src/vello/email/init.py
Update to export email components properly.

[MODIFY]
src/vello/email/base.py
Update imports to use new package structure.

[MODIFY]
src/vello/email/factory.py
Update imports to use new package structure.

[MODIFY]
src/vello/email/smtp_provider.py
Update imports to use new package structure.

[MODIFY]
src/vello/email/sendgrid_provider.py
Update imports to use new package structure.

API Module
[NEW]
src/vello/api/init.py
Export API endpoints.

[MODIFY]
src/vello/api/add_new_lead.py
Update imports to use new package structure.

Examples
[MODIFY]
examples/example_email_usage.py
Update imports to use vello package.

[MODIFY]
examples/example_template_usage.py
Update imports to use vello package.

[MODIFY]
examples/test_analysis.py
Update imports to use vello package.

Cleanup
[DELETE]
api.py
Remove empty file.

[MODIFY]
README.md
Update project structure documentation and installation instructions.

Verification Plan
Automated Tests

# Install package in development mode

pip install -e .

# Run example scripts to verify imports work

python examples/test_analysis.py
python examples/example_template_usage.py
python examples/example_email_usage.py
Manual Verification
Verify all imports resolve correctly
Ensure database initialization still works
Check that template loading finds templates in correct location
Confirm email providers can be instantiated

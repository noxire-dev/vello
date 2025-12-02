"""
Example of using the template loader.
"""

import sys
from pathlib import Path

# Add backend/src to path so we can import vello package
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from vello.utils import get_template_loader

# Get the template loader
loader = get_template_loader()

# Example variables (would come from Recipient.vars_json in real usage)
variables = {
    "name": "Sina Dilek",
    "company": "Acme Corp",
    "product_name": "Vello",
    "benefit_1": "Automate your outreach campaigns",
    "benefit_2": "Track engagement and responses",
    "benefit_3": "Increase conversion rates by 3x",
    "sender_name": "Sina Dilek",
    "sender_title": "CTO",
    "sender_company": "Vello",
    "unsubscribe_link": "https://vello.com/unsubscribe?id=123",
}

# Render both HTML and text versions
html_content, text_content = loader.render_email(
    "vello_promo/initial_outreach", variables
)

print("=== HTML Version ===")
print(html_content)
print("\n=== Text Version ===")
print(text_content)

# List all available templates
print("\n=== Available Templates ===")
templates = loader.list_templates()
for template in templates:
    print(f"  - {template}")

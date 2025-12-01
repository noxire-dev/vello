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
    "name": "John Doe",
    "company": "Acme Corp",
    "product_name": "Nexlio",
    "benefit_1": "Automate your outreach campaigns",
    "benefit_2": "Track engagement and responses",
    "benefit_3": "Increase conversion rates by 3x",
    "sender_name": "Jane Smith",
    "sender_title": "Sales Director",
    "sender_company": "Nexlio",
    "unsubscribe_link": "https://nexlio.com/unsubscribe?id=123"
}

# Render both HTML and text versions
html_content, text_content = loader.render_email(
    "welcome_series/initial_outreach",
    variables
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

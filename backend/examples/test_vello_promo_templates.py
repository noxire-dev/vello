"""
Test script for Vello promotional email templates.
Demonstrates how to use the promotional templates with sample data.
"""

import sys
from pathlib import Path

# Add backend/src to path so we can import vello package
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from vello.utils import get_template_loader

# Get the template loader
loader = get_template_loader()

# Sample variables for testing (would come from Recipient.vars_json in real usage)
sample_variables = {
    "name": "John Doe",
    "company": "Acme Corp",
    "unsubscribe_link": "https://vello.com/unsubscribe?id=12345",
}

# List all available promo templates
print("=" * 60)
print("Available Vello Promo Templates:")
print("=" * 60)
templates = loader.list_templates("vello_promo")
for template in templates:
    print(f"  ✓ {template}")

print("\n" + "=" * 60)
print("Testing Template Rendering:")
print("=" * 60)

# Test each template
for template_name in templates:
    print(f"\n📧 Rendering: {template_name}")
    print("-" * 60)

    try:
        html_content, text_content = loader.render_email(
            template_name, sample_variables
        )

        print(f"✓ HTML version: {len(html_content)} characters")
        print(f"✓ Text version: {len(text_content)} characters")

        # Show a preview of the text version
        preview = (
            text_content[:200] + "..." if len(text_content) > 200 else text_content
        )
        print(f"\nPreview:\n{preview}")

    except Exception as e:
        print(f"✗ Error rendering template: {e}")

print("\n" + "=" * 60)
print("Template Testing Complete!")
print("=" * 60)
print("\nTo use these templates in a campaign:")
print("  template_name = 'vello_promo/initial_outreach'")
print("  html, text = loader.render_email(template_name, variables)")

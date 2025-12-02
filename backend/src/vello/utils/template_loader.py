"""
Template loader using Jinja2 for email templates.
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Optional, Dict, Any
import os

from vello.utils.html_to_text import html_to_text

# Template directory - now relative to backend directory
# From backend/src/vello/utils/template_loader.py -> backend/templates
_backend_dir = Path(__file__).parent.parent.parent.parent
TEMPLATE_DIR = _backend_dir / "templates"


class TemplateLoader:
    """Loads and renders email templates using Jinja2."""

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize the template loader.

        Args:
            template_dir: Path to templates directory (defaults to backend/templates)
        """
        self.template_dir = template_dir or TEMPLATE_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_path: str, variables: Dict[str, Any]) -> str:
        """
        Render a template with the given variables.

        Args:
            template_path: Path to template relative to template_dir
                          (e.g., "welcome_series/initial_outreach.html")
            variables: Dictionary of variables to pass to the template

        Returns:
            Rendered template as string
        """
        template = self.env.get_template(template_path)
        return template.render(**variables)

    def render_email(
        self, template_name: str, variables: Dict[str, Any], include_text: bool = True
    ) -> tuple[str, Optional[str]]:
        """
        Render both HTML and text versions of an email template.

        Args:
            template_name: Template path without extension
                          (e.g., "welcome_series/initial_outreach")
            variables: Dictionary of variables to pass to the template
            include_text: Whether to render text version

        Returns:
            Tuple of (html_content, text_content)
        """
        html_path = f"{template_name}.html"
        html_content = self.render(html_path, variables)

        text_content = None
        if include_text:
            text_path = f"{template_name}.txt"
            try:
                text_content = self.render(text_path, variables)
            except Exception:
                # If no .txt file exists, generate from HTML
                text_content = html_to_text(html_content)

        return html_content, text_content

    def list_templates(self, category: Optional[str] = None) -> list[str]:
        """
        List available templates.

        Args:
            category: Optional category to filter by (e.g., "welcome_series")

        Returns:
            List of template paths
        """
        templates = []
        search_dir = self.template_dir / category if category else self.template_dir

        for file_path in search_dir.rglob("*.html"):
            relative_path = file_path.relative_to(self.template_dir)
            # Remove .html extension
            template_name = str(relative_path).replace(".html", "")
            templates.append(template_name)

        return sorted(templates)


# Singleton instance
_loader = None


def get_template_loader() -> TemplateLoader:
    """Get the global template loader instance."""
    global _loader
    if _loader is None:
        _loader = TemplateLoader()
    return _loader

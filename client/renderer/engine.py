from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..models import MediaInfo


class Renderer:
    """SVG renderer using Jinja2 templates."""

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the renderer.

        Args:
            template_dir: Directory containing SVG templates. If None, uses default.
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"

        self.template_dir = Path(template_dir)

        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_svg(
        self,
        media_info: Optional[MediaInfo] = None,
        template_name: str = "default",
        custom_css: Optional[str] = None,
    ) -> str:
        """
        Render an SVG using the specified template and media information.

        Args:
            media_info: Current media information, or None if nothing is playing
            template_name: Name of the template to use (without .svg extension)
            custom_css: Optional custom CSS to inject into the template

        Returns:
            Rendered SVG as a string
        """
        # Ensure template has .svg extension
        if not template_name.endswith(".svg"):
            template_name += ".svg"

        try:
            # Load template
            template = self.env.get_template(template_name)

            # Prepare template context
            context = {
                "media_info": media_info,
                "custom_css": custom_css or "",
                "is_playing": media_info is not None and media_info.is_playing
                if media_info
                else False,
            }

            # Render and return
            return template.render(context)

        except Exception as e:
            # Return error SVG if template rendering fails
            return self._render_error_svg(f"Template error: {str(e)}")

    def _render_error_svg(self, error_message: str) -> str:
        """Render an error SVG with the given error message."""
        return f"""
        <svg width="400" height="120" xmlns="http://www.w3.org/2000/svg">
            <style>
                .error-text {{ font-family: Arial, sans-serif; font-size: 14px; fill: #ff4444; }}
            </style>
            <rect width="400" height="120" fill="#2a2a2a" />
            <text x="10" y="30" class="error-text">Error rendering template:</text>
            <text x="10" y="50" class="error-text">{error_message}</text>
        </svg>
        """

    def list_templates(self) -> list:
        """List available templates."""
        if not self.template_dir.exists():
            return []

        return [f.stem for f in self.template_dir.glob("*.svg")]

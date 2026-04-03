"""
Dashboard Framework for RiskOptimizer

This module provides a flexible dashboard framework:
1. Dashboard - container for dashboard components
2. ChartComponent - chart visualization component
3. DashboardManager - manages multiple dashboards (CRUD)
4. DashboardRenderer - renders dashboards to HTML using Jinja2 templates
"""

import base64
import json
import logging
import os
import uuid
import warnings
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")


class ChartComponent:
    """Chart component for dashboards."""

    def __init__(
        self,
        title: str,
        chart_type: str = "line",
        data: Any = None,
        options: Optional[Dict[str, Any]] = None,
        width: int = 12,
        height: int = 4,
        position: Union[Tuple[int, int], None] = None,
    ) -> None:
        """
        Initialize chart component.

        Args:
            title: Component title
            chart_type: Chart type ('line', 'bar', 'scatter', 'pie', 'histogram')
            data: Chart data (DataFrame, Series, or dict)
            options: Chart rendering options
            width: Component width in grid units
            height: Component height in grid units
            position: (x, y) grid position tuple or None
        """
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.chart_type = chart_type
        self.data = data
        self.options = options or {}
        self.width = width
        self.height = height
        self.component_type = "chart"
        self.data_source: Optional[Dict[str, Any]] = None
        self.rendered_content: Optional[str] = None

        # Normalize position to dict
        if position is not None:
            if isinstance(position, (tuple, list)) and len(position) >= 2:
                self.position = {
                    "x": int(position[0]),
                    "y": int(position[1]),
                    "w": width,
                    "h": height,
                }
            elif isinstance(position, dict):
                self.position = position
            else:
                self.position = {"x": 0, "y": 0, "w": width, "h": height}
        else:
            self.position = {"x": 0, "y": 0, "w": width, "h": height}

    def set_data_source(self, data_source: Dict[str, Any]) -> "ChartComponent":
        """Set data source for the component."""
        self.data_source = data_source
        return self

    def set_position(self, x: int, y: int, w: int, h: int) -> "ChartComponent":
        """Set grid position and size."""
        self.position = {"x": x, "y": y, "w": w, "h": h}
        return self

    def render(self, data: Any = None) -> str:
        """
        Render the chart to HTML (base64 embedded PNG).

        Args:
            data: Optional data override

        Returns:
            HTML string with embedded chart image
        """
        chart_data = data if data is not None else self.data
        if chart_data is None and self.data_source:
            return f'<div class="chart-placeholder"><p>{self.title}: Data source configured</p></div>'

        try:
            fig = self._create_figure(chart_data)
            if fig is None:
                return (
                    f'<div class="chart-placeholder"><p>{self.title}: No data</p></div>'
                )
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=96)
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
            self.rendered_content = f'<img src="data:image/png;base64,{img_b64}" alt="{self.title}" style="max-width:100%;">'
            return self.rendered_content
        except Exception as e:
            logger.warning(f"Could not render chart '{self.title}': {e}")
            return f'<div class="chart-placeholder"><p>{self.title}: Render error</p></div>'

    def _create_figure(self, data: Any) -> Optional[plt.Figure]:
        """Create matplotlib figure from data."""
        if data is None:
            return None
        fig, ax = plt.subplots(figsize=(self.width, self.height))
        try:
            if isinstance(data, pd.DataFrame):
                if self.chart_type == "line":
                    data.plot(ax=ax)
                elif self.chart_type == "bar":
                    data.plot(kind="bar", ax=ax)
                elif self.chart_type == "scatter" and data.shape[1] >= 2:
                    ax.scatter(data.iloc[:, 0], data.iloc[:, 1])
                elif self.chart_type == "histogram":
                    data.hist(ax=ax)
                else:
                    data.plot(ax=ax)
            elif isinstance(data, pd.Series):
                if self.chart_type == "pie":
                    data.plot(kind="pie", ax=ax)
                elif self.chart_type == "bar":
                    data.plot(kind="bar", ax=ax)
                else:
                    data.plot(ax=ax)
            elif isinstance(data, (list, np.ndarray)):
                arr = np.array(data)
                if self.chart_type == "histogram":
                    ax.hist(arr, bins=30)
                elif self.chart_type == "bar" and arr.ndim == 1:
                    ax.bar(range(len(arr)), arr)
                else:
                    ax.plot(arr)
            ax.set_title(self.title)
            if self.options.get("xlabel"):
                ax.set_xlabel(self.options["xlabel"])
            if self.options.get("ylabel"):
                ax.set_ylabel(self.options["ylabel"])
            if self.options.get("legend"):
                ax.legend()
            plt.tight_layout()
        except Exception as e:
            logger.warning(f"Error creating figure for '{self.title}': {e}")
            plt.close(fig)
            return None
        return fig

    def to_dict(self) -> Dict[str, Any]:
        """Serialize component to dict (excluding raw data)."""
        return {
            "id": self.id,
            "title": self.title,
            "chart_type": self.chart_type,
            "component_type": self.component_type,
            "width": self.width,
            "height": self.height,
            "position": self.position,
            "options": self.options,
            "data_source": self.data_source,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChartComponent":
        """Deserialize component from dict."""
        component = cls(
            title=data["title"],
            chart_type=data.get("chart_type", "line"),
            options=data.get("options", {}),
            width=data.get("width", 12),
            height=data.get("height", 4),
        )
        component.id = data.get("id", component.id)
        component.component_type = data.get("component_type", "chart")
        component.position = data.get("position", {"x": 0, "y": 0, "w": 12, "h": 4})
        component.data_source = data.get("data_source")
        return component


class Dashboard:
    """Dashboard container for components."""

    def __init__(
        self,
        title: str,
        description: str = "",
        layout: str = "grid",
    ) -> None:
        """
        Initialize Dashboard.

        Args:
            title: Dashboard title
            description: Dashboard description
            layout: Layout type ('grid', 'flex')
        """
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.layout = layout
        self.components: List[ChartComponent] = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def add_component(self, component: ChartComponent) -> "Dashboard":
        """Add a component to the dashboard."""
        self.components.append(component)
        self.updated_at = datetime.now().isoformat()
        return self

    def remove_component(self, component_id: str) -> bool:
        """Remove a component by ID. Returns True if found and removed."""
        for i, comp in enumerate(self.components):
            if comp.id == component_id:
                self.components.pop(i)
                self.updated_at = datetime.now().isoformat()
                return True
        return False

    def get_component(self, component_id: str) -> Optional[ChartComponent]:
        """Get a component by ID."""
        for comp in self.components:
            if comp.id == component_id:
                return comp
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize dashboard to dict."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "layout": self.layout,
            "components": [c.to_dict() for c in self.components],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def save(self, filepath: str) -> bool:
        """Save dashboard to JSON file."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Dashboard saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving dashboard: {e}")
            return False

    @classmethod
    def load(cls, filepath: str) -> "Dashboard":
        """Load dashboard from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        dashboard = cls(
            title=data["title"],
            description=data.get("description", ""),
            layout=data.get("layout", "grid"),
        )
        dashboard.id = data.get("id", dashboard.id)
        dashboard.created_at = data.get("created_at", dashboard.created_at)
        dashboard.updated_at = data.get("updated_at", dashboard.updated_at)
        for comp_data in data.get("components", []):
            dashboard.components.append(ChartComponent.from_dict(comp_data))
        return dashboard


class DashboardManager:
    """Manages multiple dashboards with persistent storage."""

    def __init__(
        self,
        storage_dir: Optional[str] = None,
        dashboard_dir: Optional[str] = None,
    ) -> None:
        """
        Initialize DashboardManager.

        Args:
            storage_dir: Directory for storing dashboard files (primary arg name)
            dashboard_dir: Alias for storage_dir for backward compatibility
        """
        # Support both arg names
        self.storage_dir = storage_dir or dashboard_dir or "dashboards"
        os.makedirs(self.storage_dir, exist_ok=True)
        self._dashboards: Dict[str, Dashboard] = {}
        self._load_all()

    def _dashboard_path(self, dashboard_id: str) -> str:
        return os.path.join(self.storage_dir, f"{dashboard_id}.json")

    def _load_all(self) -> None:
        """Load all dashboards from storage directory."""
        if not os.path.isdir(self.storage_dir):
            return
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    dashboard = Dashboard.load(filepath)
                    self._dashboards[dashboard.id] = dashboard
                except Exception as e:
                    logger.warning(f"Could not load dashboard from {filepath}: {e}")

    def create_dashboard(
        self, title: str, description: str = "", layout: str = "grid"
    ) -> Dashboard:
        """Create a new dashboard and persist it."""
        dashboard = Dashboard(title=title, description=description, layout=layout)
        self._dashboards[dashboard.id] = dashboard
        dashboard.save(self._dashboard_path(dashboard.id))
        return dashboard

    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Retrieve a dashboard by ID."""
        return self._dashboards.get(dashboard_id)

    def update_dashboard(self, dashboard: Dashboard) -> bool:
        """Persist an updated dashboard."""
        dashboard.updated_at = datetime.now().isoformat()
        self._dashboards[dashboard.id] = dashboard
        return dashboard.save(self._dashboard_path(dashboard.id))

    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard by ID."""
        if dashboard_id not in self._dashboards:
            return False
        self._dashboards.pop(dashboard_id)
        filepath = self._dashboard_path(dashboard_id)
        if os.path.exists(filepath):
            os.remove(filepath)
        return True

    def list_dashboards(self) -> List[Dict[str, Any]]:
        """Return a summary list of all dashboards."""
        return [
            {
                "id": d.id,
                "title": d.title,
                "description": d.description,
                "component_count": len(d.components),
                "created_at": d.created_at,
                "updated_at": d.updated_at,
            }
            for d in self._dashboards.values()
        ]


class DashboardRenderer:
    """Renders dashboards to HTML using Jinja2 templates."""

    def __init__(self, template_dir: Optional[str] = None) -> None:
        """
        Initialize DashboardRenderer.

        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir
        self._env = None
        if template_dir and os.path.isdir(template_dir):
            try:
                import jinja2

                self._env = jinja2.Environment(
                    loader=jinja2.FileSystemLoader(template_dir),
                    autoescape=jinja2.select_autoescape(["html"]),
                )
            except ImportError:
                logger.warning("jinja2 not available; will use built-in template")

    def render_dashboard(
        self,
        dashboard: Dashboard,
        data: Any = None,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Render a dashboard to HTML.

        Args:
            dashboard: Dashboard instance
            data: Data dict to inject into components
            output_path: Optional path to write HTML file

        Returns:
            Rendered HTML string
        """
        # Render each component
        rendered_components = []
        for component in dashboard.components:
            component_data = None
            if data and component.data_source:
                component_data = self._resolve_data(
                    data, component.data_source.get("path", "")
                )
            html = component.render(component_data)
            rendered_components.append({"component": component, "html": html})

        if self._env:
            try:
                template = self._env.get_template("dashboard_template.html")
                html_content = template.render(
                    dashboard=dashboard,
                    components=[
                        {"title": rc["component"].title, "rendered_content": rc["html"]}
                        for rc in rendered_components
                    ],
                )
            except Exception as e:
                logger.warning(f"Template render failed: {e}, using fallback")
                html_content = self._render_fallback(dashboard, rendered_components)
        else:
            html_content = self._render_fallback(dashboard, rendered_components)

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(html_content)

        return html_content

    def _resolve_data(self, data: Any, path: str) -> Any:
        """Resolve a dot-notation data path."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def _render_fallback(
        self, dashboard: Dashboard, rendered_components: List[Dict]
    ) -> str:
        """Render using a built-in fallback HTML template."""
        components_html = "\n".join(
            f'<div class="component"><h2>{rc["component"].title}</h2>{rc["html"]}</div>'
            for rc in rendered_components
        )
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{dashboard.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .component {{ margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 4px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; }}
        .chart-placeholder {{ background: #f5f5f5; padding: 20px; text-align: center; color: #999; }}
    </style>
</head>
<body>
    <h1>{dashboard.title}</h1>
    <p>{dashboard.description}</p>
    {components_html}
</body>
</html>"""

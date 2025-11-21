"""
Reporting Framework for RiskOptimizer

This module provides a flexible reporting framework:
1. Customizable report templates
2. HTML and PDF report generation
3. Interactive report components
4. Report scheduling and distribution
5. Report versioning and comparison
"""

import base64
import datetime
import json
import logging
import os
import uuid
import warnings
from io import BytesIO

import jinja2
import markdown
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("reporting_framework")

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


class ReportTemplate:
    """Report template for risk reports"""

    def __init__(self, title, sections=None, description="", author="", version="1.0"):
        """
        Initialize report template

        Args:
            title: Report title
            sections: List of section dictionaries
            description: Report description
            author: Report author
            version: Report version
        """
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.sections = sections or []
        self.description = description
        self.author = author
        self.version = version
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at

    def add_section(self, title, content="", section_type="text", position=None):
        """
        Add section to template

        Args:
            title: Section title
            content: Section content
            section_type: Section type ('text', 'chart', 'table', 'code')
            position: Position to insert section (None = append)

        Returns:
            self: The template instance
        """
        section = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "content": content,
            "type": section_type,
        }

        if position is None:
            self.sections.append(section)
        else:
            self.sections.insert(position, section)

        self.updated_at = datetime.datetime.now().isoformat()

        return self

    def update_section(self, section_id, title=None, content=None, section_type=None):
        """
        Update section in template

        Args:
            section_id: ID of section to update
            title: New section title (optional)
            content: New section content (optional)
            section_type: New section type (optional)

        Returns:
            success: Whether update was successful
        """
        for section in self.sections:
            if section["id"] == section_id:
                if title is not None:
                    section["title"] = title
                if content is not None:
                    section["content"] = content
                if section_type is not None:
                    section["type"] = section_type

                self.updated_at = datetime.datetime.now().isoformat()
                return True

        return False

    def remove_section(self, section_id):
        """
        Remove section from template

        Args:
            section_id: ID of section to remove

        Returns:
            success: Whether removal was successful
        """
        for i, section in enumerate(self.sections):
            if section["id"] == section_id:
                self.sections.pop(i)
                self.updated_at = datetime.datetime.now().isoformat()
                return True

        return False

    def to_dict(self):
        """
        Convert template to dictionary

        Returns:
            dict: Template as dictionary
        """
        return {
            "id": self.id,
            "title": self.title,
            "sections": self.sections,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def save(self, filepath):
        """
        Save template to file

        Args:
            filepath: Path to save template

        Returns:
            success: Whether save was successful
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

            # Save template
            with open(filepath, "w") as f:
                json.dump(self.to_dict(), f, indent=2)

            logger.info(f"Template saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            return False

    @classmethod
    def load(cls, filepath):
        """
        Load template from file

        Args:
            filepath: Path to load template from

        Returns:
            template: Template instance
        """
        try:
            # Load template
            with open(filepath, "r") as f:
                data = json.load(f)

            # Create template
            template = cls(
                title=data["title"],
                sections=data.get("sections", []),
                description=data.get("description", ""),
                author=data.get("author", ""),
                version=data.get("version", "1.0"),
            )

            # Set additional attributes
            template.id = data.get("id", template.id)
            template.created_at = data.get("created_at", template.created_at)
            template.updated_at = data.get("updated_at", template.updated_at)

            logger.info(f"Template loaded from {filepath}")
            return template
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return None


class ReportGenerator:
    """Report generator for risk reports"""

    def __init__(self, template):
        """
        Initialize report generator

        Args:
            template: Report template
        """
        self.template = template
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )

    def generate_html(self, output_path, data=None):
        """
        Generate HTML report

        Args:
            output_path: Path to save HTML report
            data: Data for report generation

        Returns:
            success: Whether generation was successful
        """
        try:
            # Get HTML template
            template_str = self._get_html_template()

            # Prepare context
            context = self._prepare_context(data)

            # Render HTML
            html = self._render_html(template_str, context)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            # Save to file
            with open(output_path, "w") as f:
                f.write(html)

            return True
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return False

    def generate_pdf(self, filepath, data=None):
        """
        Generate PDF report

        Args:
            filepath: Path to save PDF report
            data: Data for report generation

        Returns:
            success: Whether generation was successful
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

            # Generate HTML first
            html_filepath = filepath.replace(".pdf", ".html")
            if not self.generate_html(html_filepath, data):
                return False

            # Ensure HTML file exists before proceeding
            if not os.path.exists(html_filepath):
                logger.error(f"HTML file not found: {html_filepath}")
                return False

            # Convert HTML to PDF
            try:
                from weasyprint import HTML

                HTML(filename=html_filepath).write_pdf(filepath)
                logger.info(f"PDF report saved to {filepath}")
                return True
            except ImportError:
                logger.error("WeasyPrint not available for PDF generation")
                return False
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return False

    def _create_html_template(self):
        """
        Create HTML template

        Returns:
            template: HTML template string
        """
        # Create basic HTML template
        template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1, h2, h3 {
                    color: #2c3e50;
                }
                .header {
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }
                .section {
                    margin-bottom: 30px;
                }
                .section-title {
                    border-bottom: 1px solid #eee;
                    padding-bottom: 5px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                .chart {
                    max-width: 100%;
                    height: auto;
                }
                .footer {
                    border-top: 1px solid #eee;
                    padding-top: 10px;
                    margin-top: 30px;
                    font-size: 0.8em;
                    color: #777;
                }
                pre {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }
                code {
                    font-family: Consolas, Monaco, 'Andale Mono', monospace;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ title }}</h1>
                <p>{{ description }}</p>
                <p><strong>Date:</strong> {{ date }}</p>
                {% if author %}
                <p><strong>Author:</strong> {{ author }}</p>
                {% endif %}
            </div>

            {% for section in sections %}
            <div class="section">
                <h2 class="section-title">{{ section.title }}</h2>
                {% if section.type == 'text' %}
                    {{ section.content|safe }}
                {% elif section.type == 'chart' %}
                    <img class="chart" src="data:image/png;base64,{{ section.content }}" alt="{{ section.title }}">
                {% elif section.type == 'table' %}
                    {{ section.content|safe }}
                {% elif section.type == 'code' %}
                    <pre><code>{{ section.content }}</code></pre>
                {% endif %}
            </div>
            {% endfor %}

            <div class="footer">
                <p>Generated on {{ generated_at }} | Version {{ version }}</p>
            </div>
        </body>
        </html>
        """

        return template

    def _prepare_context(self, data=None):
        """
        Prepare context for template rendering

        Args:
            data: Data for report generation

        Returns:
            context: Context dictionary
        """
        # Initialize context with template data
        context = {
            "title": self.template.title,
            "description": self.template.description,
            "author": self.template.author,
            "version": self.template.version,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sections": [],
        }

        # Add data if provided
        if data:
            context.update(data)

        # Process sections
        for section in self.template.sections:
            processed_section = {
                "title": section["title"],
                "type": section["type"],
                "content": section["content"],
            }

            # Process content based on type
            if section["type"] == "text":
                # Convert markdown to HTML if content looks like markdown
                if "##" in section["content"] or "*" in section["content"]:
                    processed_section["content"] = markdown.markdown(section["content"])

            elif section["type"] == "chart":
                # Generate chart if content is a chart specification
                if (
                    isinstance(section["content"], dict)
                    and "chart_type" in section["content"]
                ):
                    chart_spec = section["content"]
                    chart_data = data.get(chart_spec.get("data_key", ""), None)

                    if chart_data is not None:
                        chart_image = self._generate_chart(
                            chart_type=chart_spec["chart_type"],
                            data=chart_data,
                            options=chart_spec.get("options", {}),
                        )
                        processed_section["content"] = chart_image

            elif section["type"] == "table":
                # Generate table if content is a table specification
                if (
                    isinstance(section["content"], dict)
                    and "data_key" in section["content"]
                ):
                    table_spec = section["content"]
                    table_data = data.get(table_spec.get("data_key", ""), None)

                    if table_data is not None:
                        table_html = self._generate_table(
                            data=table_data, options=table_spec.get("options", {})
                        )
                        processed_section["content"] = table_html

            context["sections"].append(processed_section)

        return context

    def _render_html(self, template_str, context):
        """
        Render HTML from template and context

        Args:
            template_str: Template string
            context: Context dictionary

        Returns:
            html: Rendered HTML
        """
        # Create template from string
        template = jinja2.Template(template_str)

        # Render HTML
        html = template.render(**context)

        return html

    def _generate_chart(self, chart_type, data, options=None):
        """
        Generate chart image

        Args:
            chart_type: Type of chart ('line', 'bar', 'scatter', 'pie', 'heatmap')
            data: Chart data
            options: Chart options

        Returns:
            image_base64: Base64 encoded image
        """
        # Set default options
        options = options or {}

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot based on chart type
        if chart_type == "line":
            if isinstance(data, pd.DataFrame):
                data.plot(ax=ax)
            elif isinstance(data, dict) and "x" in data and "y" in data:
                ax.plot(data["x"], data["y"])
            else:
                ax.text(
                    0.5,
                    0.5,
                    "Invalid data format for line chart",
                    ha="center",
                    va="center",
                    fontsize=12,
                )

        elif chart_type == "bar":
            if isinstance(data, pd.DataFrame):
                data.plot(kind="bar", ax=ax)
            elif isinstance(data, dict) and "x" in data and "y" in data:
                ax.bar(data["x"], data["y"])
            else:
                ax.text(
                    0.5,
                    0.5,
                    "Invalid data format for bar chart",
                    ha="center",
                    va="center",
                    fontsize=12,
                )

        elif chart_type == "scatter":
            if isinstance(data, pd.DataFrame) and len(data.columns) >= 2:
                ax.scatter(data.iloc[:, 0], data.iloc[:, 1])
            elif isinstance(data, dict) and "x" in data and "y" in data:
                ax.scatter(data["x"], data["y"])
            else:
                ax.text(
                    0.5,
                    0.5,
                    "Invalid data format for scatter chart",
                    ha="center",
                    va="center",
                    fontsize=12,
                )

        elif chart_type == "pie":
            if isinstance(data, pd.DataFrame) and len(data.columns) >= 2:
                ax.pie(data.iloc[:, 1], labels=data.iloc[:, 0], autopct="%1.1f%%")
            elif isinstance(data, dict) and "values" in data and "labels" in data:
                ax.pie(data["values"], labels=data["labels"], autopct="%1.1f%%")
            else:
                ax.text(
                    0.5,
                    0.5,
                    "Invalid data format for pie chart",
                    ha="center",
                    va="center",
                    fontsize=12,
                )

        elif chart_type == "heatmap":
            if isinstance(data, pd.DataFrame):
                im = ax.imshow(data)
                plt.colorbar(im, ax=ax)
            else:
                ax.text(
                    0.5,
                    0.5,
                    "Invalid data format for heatmap",
                    ha="center",
                    va="center",
                    fontsize=12,
                )

        else:
            ax.text(
                0.5,
                0.5,
                f"Unsupported chart type: {chart_type}",
                ha="center",
                va="center",
                fontsize=12,
            )

        # Apply options
        if "title" in options:
            ax.set_title(options["title"])
        if "xlabel" in options:
            ax.set_xlabel(options["xlabel"])
        if "ylabel" in options:
            ax.set_ylabel(options["ylabel"])
        if "grid" in options and options["grid"]:
            ax.grid(True)
        if "legend" in options and options["legend"]:
            ax.legend()

        # Save to buffer
        buffer = BytesIO()
        plt.tight_layout()
        fig.savefig(buffer, format="png")
        plt.close(fig)

        # Convert to base64
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        return image_base64

    def _generate_table(self, data, options=None):
        """
        Generate HTML table

        Args:
            data: Table data (DataFrame or dict)
            options: Table options

        Returns:
            table_html: HTML table
        """
        # Set default options
        options = options or {}

        # Convert to DataFrame if dict
        if isinstance(data, dict):
            data = pd.DataFrame(data)

        # Generate HTML table
        if isinstance(data, pd.DataFrame):
            table_html = data.to_html(
                index=options.get("show_index", True),
                classes=options.get("classes", "table table-striped"),
            )
            return table_html
        else:
            return "<p>Invalid data format for table</p>"


class ReportScheduler:
    """Scheduler for automated report generation"""

    def __init__(self, storage_dir=None):
        """
        Initialize report scheduler

        Args:
            storage_dir: Directory for report storage
        """
        self.storage_dir = storage_dir or os.path.join(
            os.path.expanduser("~"), ".reports"
        )
        os.makedirs(self.storage_dir, exist_ok=True)
        self.schedules = self._load_schedules()

    def _load_schedules(self):
        """
        Load schedules from storage

        Returns:
            schedules: Dictionary of schedules
        """
        schedule_path = os.path.join(self.storage_dir, "schedules.json")

        if os.path.exists(schedule_path):
            try:
                with open(schedule_path, "r") as f:
                    return json.load(f)
            except:
                return {}
        else:
            return {}

    def _save_schedules(self):
        """
        Save schedules to storage

        Returns:
            success: Whether save was successful
        """
        schedule_path = os.path.join(self.storage_dir, "schedules.json")

        try:
            with open(schedule_path, "w") as f:
                json.dump(self.schedules, f, indent=2)
            return True
        except:
            return False

    def add_schedule(
        self,
        name,
        template_path,
        output_path,
        frequency,
        data_provider=None,
        recipients=None,
    ):
        """
        Add report schedule

        Args:
            name: Schedule name
            template_path: Path to report template
            output_path: Path for generated reports
            frequency: Schedule frequency ('daily', 'weekly', 'monthly')
            data_provider: Function to provide data for report
            recipients: List of email recipients

        Returns:
            success: Whether addition was successful
        """
        schedule_id = str(uuid.uuid4())[:8]

        self.schedules[schedule_id] = {
            "name": name,
            "template_path": template_path,
            "output_path": output_path,
            "frequency": frequency,
            "data_provider": data_provider,
            "recipients": recipients or [],
            "last_run": None,
            "next_run": self._calculate_next_run(frequency),
            "created_at": datetime.datetime.now().isoformat(),
        }

        return self._save_schedules()

    def remove_schedule(self, schedule_id):
        """
        Remove report schedule

        Args:
            schedule_id: ID of schedule to remove

        Returns:
            success: Whether removal was successful
        """
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            return self._save_schedules()
        else:
            return False

    def list_schedules(self):
        """
        List all schedules

        Returns:
            schedules: List of schedule summaries
        """
        return [
            {
                "id": id,
                "name": schedule["name"],
                "frequency": schedule["frequency"],
                "last_run": schedule["last_run"],
                "next_run": schedule["next_run"],
            }
            for id, schedule in self.schedules.items()
        ]

    def run_scheduled_reports(self):
        """
        Run all due scheduled reports

        Returns:
            results: Dictionary of results
        """
        now = datetime.datetime.now()
        results = {}

        for id, schedule in self.schedules.items():
            next_run = datetime.datetime.fromisoformat(schedule["next_run"])

            if next_run <= now:
                # Run report
                result = self.run_report(id)
                results[id] = result

                # Update schedule
                self.schedules[id]["last_run"] = now.isoformat()
                self.schedules[id]["next_run"] = self._calculate_next_run(
                    schedule["frequency"], now
                )

        # Save updated schedules
        self._save_schedules()

        return results

    def run_report(self, schedule_id):
        """
        Run specific scheduled report

        Args:
            schedule_id: ID of schedule to run

        Returns:
            result: Report generation result
        """
        if schedule_id not in self.schedules:
            return {"success": False, "error": "Schedule not found"}

        schedule = self.schedules[schedule_id]

        try:
            # Load template
            template = ReportTemplate.load(schedule["template_path"])
            if template is None:
                return {"success": False, "error": "Failed to load template"}

            # Create generator
            generator = ReportGenerator(template)

            # Get data
            data = None
            if schedule["data_provider"]:
                try:
                    # This is a simplified approach; in practice, you'd need a more robust way to call the data provider
                    data = eval(schedule["data_provider"])()
                except:
                    return {
                        "success": False,
                        "error": "Failed to get data from provider",
                    }

            # Generate report
            output_path = schedule["output_path"]
            if output_path.endswith(".pdf"):
                success = generator.generate_pdf(output_path, data)
            else:
                success = generator.generate_html(output_path, data)

            # Send report if recipients specified
            if success and schedule["recipients"]:
                self._send_report(output_path, schedule["recipients"])

            return {"success": success, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_next_run(self, frequency, from_date=None):
        """
        Calculate next run date

        Args:
            frequency: Schedule frequency ('daily', 'weekly', 'monthly')
            from_date: Date to calculate from (default: now)

        Returns:
            next_run: Next run date as ISO string
        """
        if from_date is None:
            from_date = datetime.datetime.now()

        if frequency == "daily":
            next_run = from_date + datetime.timedelta(days=1)
        elif frequency == "weekly":
            next_run = from_date + datetime.timedelta(days=7)
        elif frequency == "monthly":
            # Add one month (approximate)
            if from_date.month == 12:
                next_run = datetime.datetime(from_date.year + 1, 1, from_date.day)
            else:
                next_run = datetime.datetime(
                    from_date.year, from_date.month + 1, from_date.day
                )
        else:
            # Default to daily
            next_run = from_date + datetime.timedelta(days=1)

        # Set time to midnight
        next_run = datetime.datetime(
            next_run.year, next_run.month, next_run.day, 0, 0, 0
        )

        return next_run.isoformat()

    def _send_report(self, report_path, recipients):
        """
        Send report to recipients

        Args:
            report_path: Path to report file
            recipients: List of email recipients

        Returns:
            success: Whether sending was successful
        """
        # This is a placeholder for email sending functionality
        # In a real implementation, you would use a library like smtplib
        logger.info(f"Sending report {report_path} to {recipients}")
        return True


class ReportArchive:
    """Archive for report versioning and comparison"""

    def __init__(self, archive_dir=None):
        """
        Initialize report archive

        Args:
            archive_dir: Directory for report archive
        """
        self.archive_dir = archive_dir or os.path.join(
            os.path.expanduser("~"), ".report_archive"
        )
        os.makedirs(self.archive_dir, exist_ok=True)

    def archive_report(self, report_path, report_type, metadata=None):
        """
        Archive report

        Args:
            report_path: Path to report file
            report_type: Type of report
            metadata: Additional metadata

        Returns:
            archive_path: Path to archived report
        """
        # Create archive directory for report type
        report_type_dir = os.path.join(self.archive_dir, report_type)
        os.makedirs(report_type_dir, exist_ok=True)

        # Generate archive filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(report_path)
        base_name, ext = os.path.splitext(filename)
        archive_filename = f"{base_name}_{timestamp}{ext}"
        archive_path = os.path.join(report_type_dir, archive_filename)

        # Copy report to archive
        try:
            import shutil

            shutil.copy2(report_path, archive_path)

            # Save metadata
            if metadata:
                metadata_path = archive_path + ".meta"
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)

            logger.info(f"Report archived to {archive_path}")
            return archive_path
        except Exception as e:
            logger.error(f"Error archiving report: {e}")
            return None

    def list_archived_reports(self, report_type=None, limit=10):
        """
        List archived reports

        Args:
            report_type: Type of report to list (None = all)
            limit: Maximum number of reports to list

        Returns:
            reports: List of archived reports
        """
        reports = []

        if report_type:
            # List reports of specific type
            report_type_dir = os.path.join(self.archive_dir, report_type)
            if os.path.exists(report_type_dir):
                reports.extend(
                    self._list_reports_in_dir(report_type_dir, report_type, limit)
                )
        else:
            # List all reports
            for dir_name in os.listdir(self.archive_dir):
                dir_path = os.path.join(self.archive_dir, dir_name)
                if os.path.isdir(dir_path):
                    reports.extend(self._list_reports_in_dir(dir_path, dir_name, limit))

        # Sort by timestamp (newest first)
        reports.sort(key=lambda r: r["timestamp"], reverse=True)

        # Apply limit
        return reports[:limit]

    def _list_reports_in_dir(self, dir_path, report_type, limit):
        """
        List reports in directory

        Args:
            dir_path: Directory path
            report_type: Type of report
            limit: Maximum number of reports to list

        Returns:
            reports: List of reports
        """
        reports = []

        for filename in os.listdir(dir_path):
            if filename.endswith(".meta"):
                continue

            file_path = os.path.join(dir_path, filename)
            if os.path.isfile(file_path):
                # Extract timestamp from filename
                parts = filename.split("_")
                if len(parts) >= 2:
                    try:
                        timestamp_str = parts[-2] + "_" + parts[-1].split(".")[0]
                        timestamp = datetime.datetime.strptime(
                            timestamp_str, "%Y%m%d_%H%M%S"
                        )
                    except:
                        timestamp = datetime.datetime.fromtimestamp(
                            os.path.getmtime(file_path)
                        )
                else:
                    timestamp = datetime.datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    )

                # Get metadata if available
                metadata = {}
                metadata_path = file_path + ".meta"
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                    except:
                        pass

                reports.append(
                    {
                        "path": file_path,
                        "filename": filename,
                        "report_type": report_type,
                        "timestamp": timestamp,
                        "metadata": metadata,
                    }
                )

        return reports

    def get_report(self, report_path):
        """
        Get archived report

        Args:
            report_path: Path to archived report

        Returns:
            content: Report content
        """
        try:
            with open(report_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading report: {e}")
            return None

    def compare_reports(self, report_path1, report_path2):
        """
        Compare two archived reports

        Args:
            report_path1: Path to first report
            report_path2: Path to second report

        Returns:
            diff: Report difference
        """
        try:
            # Read reports
            with open(report_path1, "r") as f:
                content1 = f.read()

            with open(report_path2, "r") as f:
                content2 = f.read()

            # Compare reports
            import difflib

            diff = difflib.unified_diff(
                content1.splitlines(),
                content2.splitlines(),
                fromfile=os.path.basename(report_path1),
                tofile=os.path.basename(report_path2),
                lineterm="",
            )

            return "\n".join(diff)
        except Exception as e:
            logger.error(f"Error comparing reports: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Create report template
    template = ReportTemplate(
        title="Risk Analysis Report",
        description="Analysis of portfolio risk metrics",
        author="RiskOptimizer",
    )

    # Add sections
    template.add_section(
        title="Portfolio Overview",
        content="This report provides an analysis of portfolio risk metrics.",
        section_type="text",
    )

    template.add_section(
        title="Risk Metrics",
        content={"data_key": "risk_metrics", "options": {"show_index": False}},
        section_type="table",
    )

    template.add_section(
        title="Returns Distribution",
        content={
            "chart_type": "histogram",
            "data_key": "returns",
            "options": {
                "title": "Returns Distribution",
                "xlabel": "Return",
                "ylabel": "Frequency",
                "grid": True,
            },
        },
        section_type="chart",
    )

    # Save template
    template.save("risk_report_template.json")

    # Create sample data
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 1000)

    risk_metrics = pd.DataFrame(
        {
            "Metric": [
                "Volatility",
                "VaR (95%)",
                "ES (95%)",
                "Sharpe Ratio",
                "Max Drawdown",
            ],
            "Value": [0.02, 0.033, 0.041, 0.8, 0.15],
        }
    )

    # Create report generator
    generator = ReportGenerator(template)

    # Generate HTML report
    generator.generate_html(
        "risk_report.html",
        data={
            "portfolio_name": "Sample Portfolio",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "returns": returns,
            "risk_metrics": risk_metrics,
        },
    )

    print("Report generated: risk_report.html")

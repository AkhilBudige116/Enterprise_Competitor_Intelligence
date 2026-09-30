"""Reports and PDF generation package."""
from reports.pdf_generator import generate_executive_pdf
from reports.templates import NumberedCanvas, get_report_styles

__all__ = ["generate_executive_pdf", "NumberedCanvas", "get_report_styles"]

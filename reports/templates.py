"""ReportLab document styles, colors, and dynamic canvas."""
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Executive Color Palette
PRIMARY_COLOR = colors.HexColor("#0F2942")     # Deep Navy
SECONDARY_COLOR = colors.HexColor("#1E3A8A")   # Executive Blue
ACCENT_COLOR = colors.HexColor("#2563EB")      # Vibrant Blue
GOLD_ACCENT = colors.HexColor("#D97706")       # Gold/Bronze
BG_LIGHT = colors.HexColor("#F8FAFC")          # Off-white / Slate Light
BG_ALT = colors.HexColor("#EDF2F7")            # Alternate table row
TEXT_DARK = colors.HexColor("#0F172A")         # Dark slate body
TEXT_MUTED = colors.HexColor("#64748B")        # Gray subtext
BORDER_COLOR = colors.HexColor("#CBD5E1")      # Border gray
SUCCESS_COLOR = colors.HexColor("#16A34A")     # Green
WARNING_COLOR = colors.HexColor("#EA580C")     # Amber/Orange
DANGER_COLOR = colors.HexColor("#DC2626")      # Red

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and stamp 'Page X of Y' on footers."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)
        
        # Don't draw header/footer on cover page (Page 1)
        if self._pageNumber > 1:
            # Header
            self.drawString(54, 750, "Enterprise Multi-Agent Competitor Intelligence Briefing")
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Footer
            self.line(54, 48, 558, 48)
            self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — STRICTLY FOR EXECUTIVE REVIEW")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 36, page_text)
            
        self.restoreState()

def get_report_styles():
    """Retrieve styled paragraph specifications."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=PRIMARY_COLOR,
        alignment=0,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=SECONDARY_COLOR,
        alignment=0,
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=PRIMARY_COLOR,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name="SubsectionHeader",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=SECONDARY_COLOR,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name="BodyDark",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name="CalloutText",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=PRIMARY_COLOR
    ))

    styles.add(ParagraphStyle(
        name="TableHead",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=TEXT_DARK
    ))

    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=TEXT_DARK
    ))

    styles.add(ParagraphStyle(
        name="AuditBadge",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.white,
        alignment=1
    ))

    return styles

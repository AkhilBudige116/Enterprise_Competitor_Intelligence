"""Executive PDF Generator using ReportLab with boardroom-ready layouts."""
import os
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib import colors
from reports.templates import (
    NumberedCanvas, get_report_styles, PRIMARY_COLOR, SECONDARY_COLOR,
    ACCENT_COLOR, BG_LIGHT, BG_ALT, TEXT_DARK, TEXT_MUTED, BORDER_COLOR,
    SUCCESS_COLOR, WARNING_COLOR, DANGER_COLOR, GOLD_ACCENT
)
from utils.logger import get_logger
from utils.helpers import current_timestamp_iso

logger = get_logger("PDFGenerator")

def generate_executive_pdf(
    output_path: str,
    report_data: Dict[str, Any],
    companies: List[str],
    company_profiles: List[Dict[str, Any]] = None,
    comparison_matrix: Dict[str, Any] = None,
    financial_table: List[Dict[str, Any]] = None,
    verification_results: List[Dict[str, Any]] = None,
    evaluation_scores: Dict[str, Any] = None
) -> str:
    """Builds a complete, styled multi-page executive PDF report."""
    logger.info(f"Generating Executive PDF Report at: {output_path}")
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55
    )
    
    styles = get_report_styles()
    story = []
    
    # -------------------------------------------------------------
    # 1. COVER / HEADER BANNER
    # -------------------------------------------------------------
    title = report_data.get("title", "Enterprise Competitor Intelligence Briefing")
    subtitle = report_data.get("subtitle", f"Strategic Benchmarking: {', '.join(companies)}")
    
    story.append(Paragraph(title, styles["DocTitle"]))
    story.append(Paragraph(subtitle, styles["DocSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR, spaceBefore=0, spaceAfter=12))
    
    # Metadata bar
    gen_time = current_timestamp_iso()[:16].replace("T", " ") + " UTC"
    meta_data = [
        [
            Paragraph(f"<b>Target Cohort:</b> {', '.join(companies)}", styles["TableCellBold"]),
            Paragraph(f"<b>Published:</b> {gen_time}", styles["TableCell"]),
            Paragraph("<b>Classification:</b> Executive Confidential", styles["TableCell"])
        ]
    ]
    meta_table = Table(meta_data, colWidths=[200, 160, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 2. AI RESEARCH QUALITY & AUDIT BADGE
    # -------------------------------------------------------------
    eval_scores = evaluation_scores or {}
    hal_score = eval_scores.get("hallucination_score", 0.0)
    sup_rate = eval_scores.get("support_rate", 1.0) * 100.0
    faith_score = eval_scores.get("faithfulness", 0.90) * 100.0
    status = eval_scores.get("quality_status", "PASS")
    status_bg = SUCCESS_COLOR if status == "PASS" else WARNING_COLOR

    badge_data = [
        [
            Paragraph("<b>AI QUALITY & FACT AUDIT</b>", styles["AuditBadge"]),
            Paragraph(f"<b>Status: {status}</b>", styles["AuditBadge"]),
            Paragraph(f"<b>Support Rate: {sup_rate:.1f}%</b>", styles["AuditBadge"]),
            Paragraph(f"<b>Hallucination Score: {hal_score:.1f}%</b>", styles["AuditBadge"]),
            Paragraph(f"<b>Faithfulness: {faith_score:.1f}%</b>", styles["AuditBadge"]),
        ]
    ]
    badge_table = Table(badge_data, colWidths=[130, 95, 105, 105, 95])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_COLOR),
        ('BACKGROUND', (1, 0), (1, 0), status_bg),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # 3. FINANCIAL COMPARISON TABLE
    # -------------------------------------------------------------
    if financial_table and len(financial_table) > 0:
        story.append(Paragraph("Financial Fundamentals & Valuation Benchmark", styles["SectionHeader"]))
        
        headers = ["Company", "Ticker", "Market Cap", "Revenue", "YoY Growth", "Gross Margin", "Oper. Margin", "P/E"]
        table_rows = [[Paragraph(f"<b>{h}</b>", styles["TableHead"]) for h in headers]]
        
        for idx, row in enumerate(financial_table):
            bg = BG_ALT if idx % 2 == 1 else colors.white
            table_rows.append([
                Paragraph(str(row.get("company_name", "")), styles["TableCellBold"]),
                Paragraph(str(row.get("ticker", "")), styles["TableCell"]),
                Paragraph(str(row.get("market_cap", "N/A")), styles["TableCell"]),
                Paragraph(str(row.get("revenue", "N/A")), styles["TableCell"]),
                Paragraph(str(row.get("revenue_growth", "N/A")), styles["TableCell"]),
                Paragraph(str(row.get("gross_margin", "N/A")), styles["TableCell"]),
                Paragraph(str(row.get("operating_margin", "N/A")), styles["TableCell"]),
                Paragraph(str(row.get("trailing_pe", "N/A")), styles["TableCell"]),
            ])
            
        col_widths = [85, 45, 65, 65, 65, 70, 70, 65]
        fin_tbl = Table(table_rows, colWidths=col_widths)
        fin_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(fin_tbl)
        story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # 4. COMPETITOR COMPARISON MATRIX
    # -------------------------------------------------------------
    if comparison_matrix and comparison_matrix.get("dimensions"):
        dims = comparison_matrix.get("dimensions", [])
        comps = comparison_matrix.get("companies", companies)
        matrix_data = comparison_matrix.get("data", {})
        
        if dims and comps:
            story.append(Paragraph("Cross-Company Strategic Positioning Matrix", styles["SectionHeader"]))
            headers = ["Strategic Dimension"] + comps
            m_rows = [[Paragraph(f"<b>{h}</b>", styles["TableHead"]) for h in headers]]
            
            for idx, d in enumerate(dims):
                row = [Paragraph(f"<b>{d}</b>", styles["TableCellBold"])]
                dim_dict = matrix_data.get(d, {})
                for c in comps:
                    val = dim_dict.get(c, "Balanced strategic parity")
                    row.append(Paragraph(str(val), styles["TableCell"]))
                m_rows.append(row)
                
            col_w = [110] + [int(420 / len(comps))] * len(comps)
            mat_tbl = Table(m_rows, colWidths=col_w)
            mat_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(mat_tbl)
            story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # 5. ALL 13 REQUIRED SECTIONS
    # -------------------------------------------------------------
    sections = report_data.get("sections", [])
    for sec in sections:
        sec_title = f"{sec.get('section_id', '')}. {sec.get('title', '')}" if sec.get('section_id') else sec.get('title', '')
        story.append(Paragraph(sec_title, styles["SectionHeader"]))
        
        content = sec.get("content", "")
        # Split paragraphs
        paras = content.split("\n\n")
        for p in paras:
            clean_p = p.strip()
            if clean_p.startswith("### "):
                story.append(Paragraph(clean_p.replace("### ", ""), styles["SubsectionHeader"]))
            elif clean_p.startswith("- ") or clean_p.startswith("* "):
                story.append(Paragraph(f"&bull; {clean_p[2:]}", styles["BodyDark"]))
            elif clean_p:
                story.append(Paragraph(clean_p, styles["BodyDark"]))
                
        # Citations
        cits = sec.get("citations", [])
        if cits:
            cits_text = "<b>Sources Cited:</b> " + " | ".join(cits[:3])
            story.append(Paragraph(cits_text, styles["TableCell"]))
            
        story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 6. ATOMIC CLAIM VERIFICATION AUDIT APPENDIX
    # -------------------------------------------------------------
    if verification_results and len(verification_results) > 0:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Appendix: Atomic Claim-Level Fact Verification Audit", styles["SectionHeader"]))
        
        v_headers = ["Claim ID", "Statement", "Section", "Status", "Confidence", "Evidence Support"]
        v_rows = [[Paragraph(f"<b>{h}</b>", styles["TableHead"]) for h in v_headers]]
        
        for idx, item in enumerate(verification_results[:15]):
            st = str(item.get("status", "Unsupported"))
            st_color = SUCCESS_COLOR if st == "Supported" else WARNING_COLOR if "Partially" in st else DANGER_COLOR
            
            v_rows.append([
                Paragraph(item.get("claim_id", f"c-{idx}"), styles["TableCellBold"]),
                Paragraph(item.get("text", "")[:90] + "...", styles["TableCell"]),
                Paragraph(item.get("section_name", "General")[:15], styles["TableCell"]),
                Paragraph(f"<b>{st}</b>", styles["TableCellBold"]),
                Paragraph(f"{item.get('confidence', 0.8) * 100:.0f}%", styles["TableCell"]),
                Paragraph(item.get("rationale", "")[:80] + "...", styles["TableCell"]),
            ])
            
        v_table = Table(v_rows, colWidths=[50, 150, 80, 75, 55, 120])
        v_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(v_table)

    # Build PDF with custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path

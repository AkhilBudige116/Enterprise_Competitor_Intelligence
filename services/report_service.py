"""Report Service: Utility methods to export markdown, HTML, and JSON representations."""
import json
from typing import Dict, Any, List

class ReportService:
    """Helper to convert graph state into presentable formats."""

    @staticmethod
    def state_to_markdown(final_report: Dict[str, Any]) -> str:
        """Converts structured 13-section report dictionary into full markdown."""
        title = final_report.get("title", "Enterprise Competitor Intelligence Report")
        subtitle = final_report.get("subtitle", "")
        
        md_lines = [
            f"# {title}",
            f"*{subtitle}*\n",
            "---",
            f"**Generated:** {final_report.get('generated_at', '')}  ",
            f"**Target Companies:** {', '.join(final_report.get('companies', []))}\n"
        ]

        # Quality Summary Badge
        eval_scores = final_report.get("evaluation_scores", {})
        if eval_scores:
            md_lines.extend([
                "### AI Quality & Verification Audit",
                f"- **Quality Status:** `{eval_scores.get('quality_status', 'PASS')}`",
                f"- **Support Rate:** `{eval_scores.get('support_rate', 1.0)*100:.1f}%`",
                f"- **Hallucination Score:** `{eval_scores.get('hallucination_score', 0.0):.1f}%`",
                f"- **Faithfulness Metric:** `{eval_scores.get('faithfulness', 0.9)*100:.1f}%`\n"
            ])

        # Report Sections
        sections = final_report.get("sections", [])
        for s in sections:
            sec_num = s.get("section_id", "")
            sec_title = s.get("title", "")
            header = f"## {sec_num}. {sec_title}" if sec_num else f"## {sec_title}"
            md_lines.append(header)
            md_lines.append(s.get("content", ""))
            
            cits = s.get("citations", [])
            if cits:
                md_lines.append(f"\n*Sources: {', '.join(cits)}*\n")
            else:
                md_lines.append("\n")

        return "\n".join(md_lines)

    @staticmethod
    def state_to_json(final_report: Dict[str, Any]) -> str:
        """Serializes report data to formatted JSON."""
        return json.dumps(final_report, indent=2, default=str)

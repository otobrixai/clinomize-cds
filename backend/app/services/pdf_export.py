"""
Improved PDF export service with professional formatting.
"""
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import os
from datetime import datetime

class PDFExportService:
    """Generate professional PDF reports for transfusion recommendations."""
    
    def __init__(self):
        self._setup_styles()
        self._register_fonts()
    
    def _setup_styles(self):
        """Setup professional styles for the PDF."""
        self.styles = getSampleStyleSheet()
        
        # Title style
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=1  # Center
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=18,
            alignment=1  # Center
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'Section',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=6,
            spaceBefore=12,
            leftIndent=0
        )
        
        # Component header style
        self.component_style = ParagraphStyle(
            'Component',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=4,
            spaceBefore=8,
            leftIndent=10
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'Normal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=4
        )
        
        # Bold text style
        self.bold_style = ParagraphStyle(
            'Bold',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        
        # Warning style
        self.warning_style = ParagraphStyle(
            'Warning',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#92400e'),
            backColor=colors.HexColor('#fef3c7'),
            borderPadding=6,
            spaceAfter=4
        )
        
        # MTP style
        self.mtp_style = ParagraphStyle(
            'MTP',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#991b1b'),
            backColor=colors.HexColor('#fee2e2'),
            borderPadding=8,
            spaceAfter=8,
            alignment=1  # Center
        )
        
        # Footer style
        self.footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            spaceBefore=20,
            alignment=1  # Center
        )
    
    def _register_fonts(self):
        """Register additional fonts if available."""
        try:
            # Try to register Arial for better readability
            font_paths = [
                Path("fonts/arial.ttf"),
                Path("fonts/Arial.ttf"),
                Path("/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"),
            ]
            
            for font_path in font_paths:
                if font_path.exists():
                    pdfmetrics.registerFont(TTFont("Arial", str(font_path)))
                    pdfmetrics.registerFont(TTFont("Arial-Bold", str(font_path)))
                    break
        except:
            pass  # Use default Helvetica
    
    def _clean_text(self, text: str) -> str:
        """Clean text for PDF rendering."""
        if not text:
            return ""
        
        # Replace emojis and special characters
        replacements = {
            '×10⁹': '×10⁹',
            '⚠️': '[WARNING]',
            '⚠': '[WARNING]',
            '❌': '[CONTRAINDICATION]',
            '✅': '[RECOMMENDED]',
            '→': '→',
            '•': '•',
            '–': '-',
            '—': '-',
        }
        
        cleaned = str(text)
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned
    
    def _create_patient_table(self, encounter_data: Dict[str, Any]) -> Table:
        """Create a professional patient information table."""
        data = [
            ['Patient Information', ''],
            ['Age', f"{encounter_data.get('age_years', 'N/A')} years"],
            ['Weight', f"{encounter_data.get('weight_kg', 'N/A')} kg"],
            ['Sex', encounter_data.get('sex', 'N/A')],
            ['Setting', self._format_setting(encounter_data.get('setting', 'N/A'))],
        ]
        
        # Add active conditions
        if encounter_data.get('active_bleeding'):
            data.append(['Active Conditions', 'Active Bleeding'])
        if encounter_data.get('hemodynamic_instability'):
            cond = data[-1][1] if len(data) > 5 and data[-1][0] == 'Active Conditions' else ''
            if cond:
                data[-1][1] = f"{cond}, Hemodynamic Instability"
            else:
                data.append(['Active Conditions', 'Hemodynamic Instability'])
        
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1d4ed8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return table
    
    def _format_setting(self, setting: str) -> str:
        """Format setting for display."""
        settings = {
            'ward': 'Ward',
            'icu': 'ICU',
            'or': 'Operating Room',
            'er': 'Emergency Room'
        }
        return settings.get(setting.lower(), setting)
    
    def generate_recommendation_pdf(
        self,
        recommendation: Dict[str, Any],
        encounter_data: Dict[str, Any],
        output_path: str,
        language: str = 'en'
    ) -> str:
        """
        Generate professional PDF recommendation.
        
        Args:
            recommendation: Recommendation data
            encounter_data: Patient encounter data
            output_path: Path to save PDF
            language: Language (always English now)
        
        Returns:
            Path to generated PDF
        """
        # Create document with proper margins
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        
        # Header with logo and timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        story.append(Paragraph("TransfusionIQ", self.title_style))
        story.append(Paragraph("Clinical Decision Support System", self.subtitle_style))
        story.append(Paragraph(f"Generated: {timestamp}", self.subtitle_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Add disclaimer
        disclaimer = Paragraph(
            "<b>CLINICAL DECISION SUPPORT ONLY</b> - Confirm with local hospital policy and clinical judgment.",
            self.warning_style
        )
        story.append(disclaimer)
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information Section
        story.append(Paragraph("Patient Information", self.section_style))
        story.append(self._create_patient_table(encounter_data))
        story.append(Spacer(1, 0.3*inch))
        
        # MTP Protocol Warning (if applicable)
        if recommendation.get("mtp_protocol"):
            mtp_warning = Paragraph(
                "<b>⚠️ MASSIVE TRANSFUSION PROTOCOL (MTP) ACTIVATED</b><br/>"
                "Multiple component transfusion required. Activate institutional MTP protocol.",
                self.mtp_style
            )
            story.append(mtp_warning)
            story.append(Spacer(1, 0.2*inch))
        
        # Recommendations Section
        story.append(Paragraph("Transfusion Recommendations", self.section_style))
        
        components = recommendation.get("components", [])
        
        # Separate contraindications and positive recommendations
        contraindications = [c for c in components if c.get("action") == "contraindicate"]
        positive_components = [c for c in components if c.get("component") and c.get("action") != "contraindicate"]
        no_transfusion = [c for c in components if not c.get("component") and c.get("action") != "contraindicate"]
        
        # Contraindications
        if contraindications:
            story.append(Paragraph("Contraindications", self.component_style))
            for contra in contraindications:
                story.append(Paragraph(
                    f"<b>[CONTRAINDICATION]</b> {self._clean_text(contra.get('dose_text', 'N/A'))}",
                    self.bold_style
                ))
                if contra.get("why"):
                    for reason in contra.get("why", [])[:3]:
                        story.append(Paragraph(f"• {self._clean_text(reason)}", self.normal_style))
                story.append(Spacer(1, 0.1*inch))
        
        # Positive Recommendations
        if positive_components:
            for idx, comp in enumerate(positive_components, 1):
                story.append(Paragraph(
                    f"Component {idx}: {self._clean_text(comp.get('component', 'N/A'))}",
                    self.component_style
                ))
                
                # Create component details table
                comp_data = [
                    ['Dose', self._clean_text(comp.get('dose_text', 'N/A'))],
                ]
                
                if comp.get('units'):
                    comp_data.append(['Units', f"{comp['units']}"])
                if comp.get('volume_ml'):
                    comp_data.append(['Volume', f"{comp['volume_ml']} mL"])
                if comp.get('expected_increment'):
                    comp_data.append(['Expected Increment', self._clean_text(comp['expected_increment'])])
                
                comp_table = Table(comp_data, colWidths=[1.5*inch, 4*inch])
                comp_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbeafe')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                    ('PADDING', (0, 0), (-1, -1), 4),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(comp_table)
                story.append(Spacer(1, 0.1*inch))
                
                # Rationale
                if comp.get("why"):
                    story.append(Paragraph("<b>Rationale:</b>", self.bold_style))
                    for point in comp.get("why", [])[:4]:
                        story.append(Paragraph(f"• {self._clean_text(point)}", self.normal_style))
                
                # Recheck Plan
                if comp.get("recheck_plan"):
                    story.append(Paragraph(f"<b>Recheck Plan:</b> {self._clean_text(comp['recheck_plan'])}", self.bold_style))
                
                # Warnings
                if comp.get("warnings"):
                    story.append(Spacer(1, 0.05*inch))
                    for warning in comp.get("warnings", []):
                        story.append(Paragraph(f"[WARNING] {self._clean_text(warning)}", self.warning_style))
                
                # Rule IDs
                if comp.get("rule_ids"):
                    story.append(Spacer(1, 0.05*inch))
                    story.append(Paragraph(
                        f"<b>Rule IDs:</b> {', '.join(comp['rule_ids'])}",
                        ParagraphStyle('Small', parent=self.normal_style, fontSize=8, textColor=colors.gray)
                    ))
                
                if idx < len(positive_components):
                    story.append(Spacer(1, 0.2*inch))
                    story.append(Paragraph("─" * 50, self.normal_style))
                    story.append(Spacer(1, 0.2*inch))
        
        # No Transfusion
        if no_transfusion and not positive_components:
            story.append(Paragraph("No Transfusion Recommended", self.component_style))
            for nt in no_transfusion:
                if nt.get("why"):
                    for reason in nt.get("why", []):
                        story.append(Paragraph(f"• {self._clean_text(reason)}", self.normal_style))
                if nt.get("recheck_plan"):
                    story.append(Paragraph(f"<b>Plan:</b> {self._clean_text(nt['recheck_plan'])}", self.bold_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Overall Warnings
        overall_warnings = recommendation.get("overall_warnings", [])
        all_warnings = overall_warnings.copy()
        for comp in components:
            all_warnings.extend(comp.get("warnings", []))
        
        if all_warnings:
            unique_warnings = list(dict.fromkeys(all_warnings))  # Remove duplicates while preserving order
            story.append(Paragraph("Additional Warnings", self.component_style))
            for warning in unique_warnings[:5]:  # Limit to 5 most important
                story.append(Paragraph(f"• {self._clean_text(warning)}", self.warning_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Footer with rule version
        rule_version = recommendation.get("rule_version", "N/A")
        if rule_version != "N/A":
            story.append(Paragraph(
                f"<b>Rule Version:</b> {rule_version}",
                ParagraphStyle('Footer', parent=self.footer_style, fontSize=9, alignment=0)
            ))
        
        # References (from first component)
        if components and components[0].get("references"):
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph("<b>References:</b>", self.bold_style))
            for ref in components[0].get("references", [])[:3]:  # Limit to 3 references
                story.append(Paragraph(f"• {ref}", self.normal_style))
        
        # Final footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            "TransfusionIQ CDS • Evidence-based transfusion guidance • Not a substitute for clinical judgment",
            self.footer_style
        ))
        
        # Build the PDF
        try:
            doc.build(story)
            return output_path
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error building PDF: {str(e)}", exc_info=True)
            raise
    
    def generate_quick_pdf(self, data: Dict[str, Any], output_path: str) -> str:
        """Generate a quick one-page PDF (simplified version)."""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph("Transfusion Recommendation", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add content based on data
        if data.get("components"):
            for comp in data["components"]:
                story.append(Paragraph(f"<b>{comp.get('component', 'Recommendation')}:</b>", styles['Normal']))
                story.append(Paragraph(comp.get('dose_text', ''), styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        return output_path
"""
Professional Premium PDF Generator for Job Cards
Creates beautiful, print-ready PDF documents with modern design.
"""

import io
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, HRFlowable, KeepTogether, PageBreak
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
import qrcode
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Premium color palette
COLORS = {
    'primary': colors.HexColor('#1E3A5F'),
    'primary_light': colors.HexColor('#2E5A8F'),
    'secondary': colors.HexColor('#00C896'),
    'accent': colors.HexColor('#FF6B35'),
    'background': colors.HexColor('#F8FAFC'),
    'card_bg': colors.HexColor('#FFFFFF'),
    'text': colors.HexColor('#1A1A2E'),
    'text_light': colors.HexColor('#6B7280'),
    'border': colors.HexColor('#E2E8F0'),
    'success': colors.HexColor('#10B981'),
    'warning': colors.HexColor('#F59E0B'),
    'danger': colors.HexColor('#EF4444'),
    'info': colors.HexColor('#3B82F6'),
    'header_bg': colors.HexColor('#1E3A5F'),
    'row_alt': colors.HexColor('#F8FAFC'),
}


class NumberedCanvas(canvas.Canvas):
    """Canvas that adds page numbers and headers/footers."""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            self.draw_page_elements()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
        """Draw page number at bottom center."""
        self.setFont("Helvetica", 9)
        self.setFillColor(COLORS['text_light'])
        page_num = f"Page {self._pageNumber} of {page_count}"
        self.drawCentredString(A4[0] / 2, 15 * mm, page_num)
    
    def draw_page_elements(self):
        """Draw header and footer elements on each page."""
        # Header line
        self.setStrokeColor(COLORS['primary'])
        self.setLineWidth(2)
        self.line(20 * mm, A4[1] - 15 * mm, A4[0] - 20 * mm, A4[1] - 15 * mm)


def make_qr_image(data: str, width: float = 80) -> Image:
    """Generate QR code image."""
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(data)
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Image(buf, width=width, height=width)


def create_gradient_rect(d: Drawing, x: float, y: float, width: float, height: float, 
                         color1: colors.Color, color2: colors.Color):
    """Create a rectangle with gradient effect using multiple rectangles."""
    steps = 10
    for i in range(steps):
        ratio = i / steps
        r = color1.red + (color2.red - color1.red) * ratio
        g = color1.green + (color2.green - color1.green) * ratio
        b = color1.blue + (color2.blue - color1.blue) * ratio
        step_height = height / steps
        rect = Rect(x, y + i * step_height, width, step_height + 1,
                   fillColor=colors.Color(r, g, b), strokeColor=None)
        d.add(rect)


def generate_premium_pdf(
    company_name: str,
    company_address: str,
    logo_file: Any,
    vendor_id: str,
    vendor_company: str,
    vendor_person: str,
    vendor_mobile: str,
    vendor_gst: str,
    vendor_address: str,
    job_no: str,
    job_date: str,
    dispatch_location: str,
    qr_bytes: bytes,
    items_df,
    materials_df,
    grn_df,
    tolerance: str,
    surface_finish: str,
    hardness: str,
    thread_check: bool,
    expected_date: str = None,
    operations: List[str] = None,
    machine_details: Dict = None,
    grn_entries_data: List = None,
    quality_notes: str = ""
) -> bytes:
    """
    Generate a premium, professional-looking PDF for a job card.
    
    Args:
        company_name: Company name
        company_address: Company address
        logo_file: Company logo file
        vendor_id: Vendor ID
        vendor_company: Vendor company name
        vendor_person: Contact person
        vendor_mobile: Mobile number
        vendor_gst: GST number
        vendor_address: Vendor address
        job_no: Job card number
        job_date: Job card date
        dispatch_location: Dispatch location
        qr_bytes: QR code image bytes
        items_df: Items dataframe
        materials_df: Materials dataframe
        grn_df: GRN dataframe
        tolerance: Tolerance specification
        surface_finish: Surface finish requirement
        hardness: Hardness requirement
        thread_check: Thread check required
        expected_date: Expected delivery date
        operations: List of selected operations
        machine_details: Machine details dictionary
        quality_notes: Additional quality notes
    
    Returns:
        PDF as bytes
    """
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        textColor=COLORS['primary'],
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=COLORS['text_light'],
        spaceAfter=20
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        leading=14,
        textColor=COLORS['card_bg'],
        fontName='Helvetica-Bold',
        backColor=COLORS['primary'],
        leftIndent=5,
        rightIndent=5,
        spaceBefore=10,
        spaceAfter=5
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=COLORS['text_light'],
        fontName='Helvetica'
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=COLORS['text'],
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'NormalCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=COLORS['text']
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=COLORS['text_light']
    )
    
    story = []
    
    # ==================== HEADER SECTION ====================
    header_elements = []
    
    # Logo and company info in header
    if logo_file:
        try:
            logo_img = Image(logo_file, width=60, height=60)
            logo_img.hAlign = 'LEFT'
        except:
            logo_img = None
    else:
        logo_img = None
    
    # Company name as header
    company_header_data = [
        [Paragraph(f"<b>{company_name or 'Company Name'}</b>", title_style)],
        [Paragraph(f"<font color='#{COLORS['text_light'].hexval()[2:]}'>{company_address or 'Company Address'}</font>", subtitle_style)]
    ]
    company_header = Table(company_header_data, colWidths=[A4[0] - 50 * mm])
    company_header.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    # Create header table with logo
    if logo_img:
        header_table_data = [[logo_img, company_header]]
        header_table = Table(header_table_data, colWidths=[70, A4[0] - 100 * mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        header_elements.append(header_table)
    else:
        header_elements.append(company_header)
    
    # Decorative line
    header_elements.append(Spacer(1, 3 * mm))
    header_elements.append(HRFlowable(
        width="100%", 
        thickness=3, 
        color=COLORS['secondary'],
        spaceAfter=3 * mm
    ))
    header_elements.append(HRFlowable(
        width="100%", 
        thickness=1, 
        color=COLORS['primary'],
        spaceAfter=8 * mm
    ))
    
    # Title banner
    title_banner_data = [[Paragraph("<b>JOB CARD</b>", ParagraphStyle(
        'Banner',
        fontSize=18,
        alignment=TA_CENTER,
        textColor=COLORS['card_bg'],
        fontName='Helvetica-Bold'
    ))]]
    title_banner = Table(title_banner_data, colWidths=[A4[0] - 30 * mm])
    title_banner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['primary']),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))
    header_elements.append(title_banner)
    header_elements.append(Spacer(1, 6 * mm))
    
    for elem in header_elements:
        story.append(elem)
    
    # ==================== JOB CARD INFO + QR ====================
    # Job info box
    job_info_data = [
        [Paragraph("<b>Job Card No:</b>", label_style), 
         Paragraph(f"<b>{job_no}</b>", value_style),
         Paragraph("<b>Date:</b>", label_style),
         Paragraph(f"<b>{job_date}</b>", value_style)],
        [Paragraph("Dispatch Location:", label_style),
         Paragraph(dispatch_location or "-", normal_style),
         Paragraph("Expected Delivery:", label_style),
         Paragraph(expected_date or "-", normal_style)],
    ]
    job_info_table = Table(job_info_data, colWidths=[35 * mm, 50 * mm, 35 * mm, 50 * mm])
    job_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['background']),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
        ('SPAN', (1, 1), (1, 1)),
        ('SPAN', (3, 1), (3, 1)),
    ]))
    
    # QR Code
    qr_img = None
    if qr_bytes:
        qr_img = Image(io.BytesIO(qr_bytes), width=50, height=50)
    
    # Combine job info and QR
    if qr_img:
        qr_cell = qr_img
    else:
        qr_cell = Paragraph("QR", label_style)
    
    top_row_data = [[job_info_table, qr_cell]]
    top_row = Table(top_row_data, colWidths=[A4[0] - 70 * mm, 60 * mm])
    top_row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(top_row)
    story.append(Spacer(1, 5 * mm))
    
    # ==================== VENDOR DETAILS ====================
    story.append(create_section_header("VENDOR DETAILS", COLORS['primary']))
    
    vendor_data = [
        [Paragraph("<b>Vendor ID:</b>", label_style), Paragraph(vendor_id or "-", normal_style),
         Paragraph("<b>GST No:</b>", label_style), Paragraph(vendor_gst or "-", normal_style)],
        [Paragraph("<b>Company:</b>", label_style), Paragraph(vendor_company or "-", normal_style),
         Paragraph("<b>Mobile:</b>", label_style), Paragraph(vendor_mobile or "-", normal_style)],
        [Paragraph("<b>Contact:</b>", label_style), Paragraph(vendor_person or "-", normal_style),
         Paragraph("<b>Address:</b>", label_style), Paragraph(vendor_address or "-", normal_style)],
    ]
    vendor_table = Table(vendor_data, colWidths=[30 * mm, 65 * mm, 30 * mm, 50 * mm])
    vendor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['card_bg']),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, COLORS['border']),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [COLORS['card_bg'], COLORS['background']]),
    ]))
    story.append(vendor_table)
    story.append(Spacer(1, 5 * mm))
    
    # ==================== ITEMS TABLE ====================
    story.append(create_section_header("ITEM DETAILS", COLORS['secondary']))
    
    # Prepare items data
    if items_df is not None and not items_df.empty:
        items_data = [["Description", "Drawing No.", "Drawing Link", "Grade", "Qty", "UOM"]]
        for _, row in items_df.iterrows():
            items_data.append([
                str(row.get("Description", ""))[:50],
                str(row.get("Drawing No.", ""))[:20],
                str(row.get("Drawing Link", ""))[:30],
                str(row.get("Grade", ""))[:15],
                str(row.get("Qty", "")),
                str(row.get("UOM", "Nos"))[:10]
            ])
        
        items_table = Table(items_data, colWidths=[65 * mm, 30 * mm, 35 * mm, 25 * mm, 15 * mm, 15 * mm])
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['card_bg']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Data
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (4, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (3, -1), 'LEFT'),
            # Styling
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('BOX', (0, 0), (-1, -1), 1, COLORS['primary']),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, COLORS['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['card_bg'], COLORS['background']]),
        ]))
        story.append(items_table)
    else:
        story.append(Paragraph("No items added.", normal_style))
    story.append(Spacer(1, 5 * mm))
    
    # ==================== MATERIALS TABLE ====================
    story.append(create_section_header("MATERIAL ISSUED", COLORS['accent']))
    
    if materials_df is not None and not materials_df.empty:
        materials_data = [["Raw Material", "Heat No.", "Dia/Size", "Weight", "Qty", "Remark"]]
        for _, row in materials_df.iterrows():
            materials_data.append([
                str(row.get("Raw Material", ""))[:40],
                str(row.get("Heat No.", ""))[:20],
                str(row.get("Dia/Size", ""))[:15],
                str(row.get("Weight", "")),
                str(row.get("Qty", "")),
                str(row.get("Remark", ""))[:20]
            ])
        
        materials_table = Table(materials_data, colWidths=[45 * mm, 30 * mm, 25 * mm, 20 * mm, 15 * mm, 40 * mm])
        materials_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['accent']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['card_bg']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (3, 1), (4, -1), 'CENTER'),
            ('ALIGN', (0, 1), (2, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('BOX', (0, 0), (-1, -1), 1, COLORS['accent']),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, COLORS['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['card_bg'], COLORS['background']]),
        ]))
        story.append(materials_table)
    else:
        story.append(Paragraph("No materials issued.", normal_style))
    story.append(Spacer(1, 5 * mm))
    
    # ==================== OPERATIONS CHECKLIST ====================
    if operations:
        story.append(create_section_header("OPERATIONS CHECKLIST", COLORS['info']))
        
        op_data = []
        row = []
        for idx, op in enumerate(operations):
            row.append(f"☐  {op}")
            if len(row) == 3:
                op_data.append(row)
                row = []
        if row:
            while len(row) < 3:
                row.append("")
            op_data.append(row)
        
        op_table = Table(op_data, colWidths=[60 * mm, 60 * mm, 60 * mm])
        op_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['background']),
            ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(op_table)
        story.append(Spacer(1, 5 * mm))
    
    # ==================== MACHINE DETAILS ====================
    if machine_details:
        story.append(create_section_header("MACHINE DETAILS", COLORS['warning']))
        
        machine_data = []
        for key, value in machine_details.items():
            if value:
                machine_data.append([
                    Paragraph(f"<b>{key}:</b>", label_style),
                    Paragraph(str(value), normal_style)
                ])
        
        if machine_data:
            machine_table = Table(machine_data, colWidths=[40 * mm, 130 * mm])
            machine_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLORS['background']),
                ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, COLORS['border']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(machine_table)
        story.append(Spacer(1, 5 * mm))
    
    # ==================== QUALITY INSTRUCTIONS ====================
    story.append(create_section_header("QUALITY INSTRUCTIONS", COLORS['success']))
    
    quality_data = [
        [Paragraph("<b>Tolerance:</b>", label_style), Paragraph(tolerance or "-", normal_style),
         Paragraph("<b>Surface Finish:</b>", label_style), Paragraph(surface_finish or "-", normal_style)],
        [Paragraph("<b>Hardness:</b>", label_style), Paragraph(hardness or "-", normal_style),
         Paragraph("<b>Thread Check:</b>", label_style), 
         Paragraph("✓ GO/NO-GO Required" if thread_check else "Not Applicable", normal_style)],
    ]
    quality_table = Table(quality_data, colWidths=[30 * mm, 60 * mm, 35 * mm, 50 * mm])
    quality_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['card_bg']),
        ('BOX', (0, 0), (-1, -1), 1, COLORS['success']),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, COLORS['border']),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(quality_table)
    story.append(Spacer(1, 5 * mm))
    
    # ==================== GRN / QC SECTION ====================
    if grn_df is not None and not grn_df.empty:
        story.append(create_section_header("GOODS RECEIVED / QC", COLORS['danger']))
        
        grn_data = [["Date", "Qty Received", "OK Qty", "Rejected", "Remarks", "QC By"]]
        for _, row in grn_df.iterrows():
            grn_data.append([
                str(row.get("Date", "")),
                str(row.get("Qty Received", 0)),
                str(row.get("OK Qty", 0)),
                str(row.get("Rejected Qty", 0)),
                str(row.get("Remarks", ""))[:25],
                str(row.get("QC Approved By", ""))[:20]
            ])
        
        grn_table = Table(grn_data, colWidths=[25 * mm, 30 * mm, 20 * mm, 25 * mm, 45 * mm, 30 * mm])
        grn_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['danger']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['card_bg']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('BOX', (0, 0), (-1, -1), 1, COLORS['danger']),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, COLORS['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['card_bg'], COLORS['background']]),
        ]))
        story.append(grn_table)
        story.append(Spacer(1, 5 * mm))
    
    # ==================== SIGNATURES ====================
    story.append(create_section_header("AUTHORIZATION", COLORS['primary']))
    
    sig_data = [
        ["", "", ""],
        ["________________", "________________", "________________"],
        [Paragraph("<b>Prepared By</b>", ParagraphStyle('Sig', fontSize=9, alignment=TA_CENTER)),
         Paragraph("<b>QC Approved By</b>", ParagraphStyle('Sig', fontSize=9, alignment=TA_CENTER)),
         Paragraph("<b>Vendor Sign</b>", ParagraphStyle('Sig', fontSize=9, alignment=TA_CENTER))],
        ["", "", ""],
        ["Date: ____________", "Date: ____________", "Date: ____________"],
    ]
    sig_table = Table(sig_data, colWidths=[60 * mm, 60 * mm, 60 * mm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
        ('LINEAFTER', (0, 0), (1, -1), 0.5, COLORS['border']),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 8 * mm))
    
    # ==================== FOOTER ====================
    story.append(HRFlowable(width="100%", thickness=2, color=COLORS['primary'], spaceBefore=5, spaceAfter=5))
    
    footer_text = f"""
    <font color='#{COLORS['text_light'].hexval()[2:]}'>
    This is a system-generated document. Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </font>
    """
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()


def create_section_header(text: str, bg_color: colors.Color) -> Table:
    """Create a styled section header table."""
    header_data = [[Paragraph(f"<b>{text}</b>", ParagraphStyle(
        'SectionHeader',
        fontSize=11,
        alignment=TA_LEFT,
        textColor=COLORS['card_bg'],
        fontName='Helvetica-Bold',
        leading=14
    ))]]
    header_table = Table(header_data, colWidths=[A4[0] - 30 * mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return header_table


# Utility function for simple PDF generation
def generate_simple_pdf(data: Dict[str, Any]) -> bytes:
    """Generate a simple PDF from job card data dictionary."""
    return generate_premium_pdf(
        company_name=data.get('company_name', ''),
        company_address=data.get('company_address', ''),
        logo_file=data.get('logo_file'),
        vendor_id=data.get('vendor_id', ''),
        vendor_company=data.get('vendor_company', ''),
        vendor_person=data.get('vendor_person', ''),
        vendor_mobile=data.get('vendor_mobile', ''),
        vendor_gst=data.get('vendor_gst', ''),
        vendor_address=data.get('vendor_address', ''),
        job_no=data.get('job_no', ''),
        job_date=str(data.get('job_date', '')),
        dispatch_location=data.get('dispatch_location', ''),
        qr_bytes=data.get('qr_bytes'),
        items_df=data.get('items_df'),
        materials_df=data.get('materials_df'),
        grn_df=data.get('grn_df'),
        tolerance=data.get('tolerance', ''),
        surface_finish=data.get('surface_finish', ''),
        hardness=data.get('hardness', ''),
        thread_check=data.get('thread_check', False),
        expected_date=str(data.get('expected_date', '')) if data.get('expected_date') else None,
        operations=data.get('operations'),
        machine_details=data.get('machine_details'),
        quality_notes=data.get('quality_notes', '')
    )

import base64
import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
from reportlab.platypus import Image as RLImage  # only used earlier; left for compatibility
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from datetime import date as dt_date

st.set_page_config(page_title="Dynamic Vendor Job Card", layout="wide")
PRIMARY_COLOR = "#0d6efd"

# -----------------------------
# Safe session state initialization
# -----------------------------
if 'items' not in st.session_state or not isinstance(st.session_state['items'], list):
    st.session_state['items'] = []
if 'materials' not in st.session_state or not isinstance(st.session_state['materials'], list):
    st.session_state['materials'] = []
if 'grn_entries' not in st.session_state or not isinstance(st.session_state['grn_entries'], list):
    st.session_state['grn_entries'] = []

# -----------------------------
# Helper functions
# -----------------------------
def make_qr_bytes(data):
    qr = qrcode.QRCode(box_size=4)
    qr.add_data(data)
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue(), img

def rows_to_df(rows, columns):
    if rows is None or len(rows) == 0:
        return pd.DataFrame(columns=columns)
    safe_rows = []
    for r in rows:
        if r is None:
            r = [""] * len(columns)
        elif len(r) < len(columns):
            r = r + [""] * (len(columns) - len(r))
        elif len(r) > len(columns):
            r = r[:len(columns)]
        safe_rows.append(r)
    return pd.DataFrame(safe_rows, columns=columns)

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["Input", "Preview", "PDF Export"])

# -----------------------------
# TAB 1: Input
# -----------------------------
with tab1:
    st.markdown(f"<h1 style='color:{PRIMARY_COLOR}'>Vendor Job Card Input</h1>", unsafe_allow_html=True)

    # Company Header
    st.subheader("Company Header")
    col_logo, col_name = st.columns([1,5])
    with col_logo:
        logo_file = st.file_uploader("Upload Company Logo", type=["png","jpg","jpeg"])
        logo_bytes = None
        logo_b64 = ""
        if logo_file is not None:
            # read bytes once and keep for reuse
            logo_bytes = logo_file.read()
            logo_b64 = base64.b64encode(logo_bytes).decode("utf-8")
    with col_name:
        company_name = st.text_input("Your Company Name")
        company_address = st.text_area("Your Company Address")

    # Vendor Details
    st.subheader("Vendor Details")
    colv1, colv2 = st.columns(2)
    with colv1:
        vendor_id = st.text_input("Vendor ID")
        vendor_company = st.text_input("Vendor Company Name")
        vendor_person = st.text_input("Contact Person")
        vendor_mobile = st.text_input("Mobile Number")
    with colv2:
        vendor_gst = st.text_input("GST Number")
        vendor_address = st.text_area("Vendor Address")

    # Job Details
    st.subheader("Job Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        job_no = st.text_input("Job Card No.", value=f"JC-{dt_date.today().strftime('%Y%m%d')}")
    with col2:
        job_date = st.date_input("Date", dt_date.today())
    with col3:
        dispatch_location = st.text_input("Dispatch Location")

    # QR Code
    qr_text_input = f"JobNo: {job_no} | Date: {job_date} | Dispatch: {dispatch_location} | VendorID: {vendor_id}"
    qr_bytes, qr_img = make_qr_bytes(qr_text_input)
    st.image(qr_bytes, width=120, caption="QR Code Preview")

    # Item Table
    st.subheader("Item Details")
    new_item = st.columns([1,1,1,1,1,1])
    desc = new_item[0].text_input("Description")
    drawing_no = new_item[1].text_input("Drawing No")
    drawing_link = new_item[2].text_input("Drawing Link")
    grade = new_item[3].text_input("Grade")
    qty = new_item[4].number_input("Qty", value=0, min_value=0)
    uom = new_item[5].text_input("UOM", value="Nos")
    if st.button("Add Item"):
        if 'items' not in st.session_state or not isinstance(st.session_state['items'], list):
            st.session_state['items'] = []
        st.session_state['items'].append([desc, drawing_no, drawing_link, grade, qty, uom])
    if st.session_state['items']:
        st.dataframe(rows_to_df(st.session_state['items'], ["Description","Drawing No","Drawing Link","Grade","Qty","UOM"]), use_container_width=True)
        if st.button("Clear Items"):
            st.session_state['items'] = []

    # Material Issued
    st.subheader("Material Issued")
    new_mat = st.columns([1,1,1,1,1,1])
    rm = new_mat[0].text_input("Raw Material")
    heat = new_mat[1].text_input("Heat No")
    dia = new_mat[2].text_input("Dia/Size")
    weight = new_mat[3].number_input("Weight", value=0)
    mqty = new_mat[4].number_input("Qty", value=0)
    remark = new_mat[5].text_input("Remark")
    if st.button("Add Material"):
        if 'materials' not in st.session_state or not isinstance(st.session_state['materials'], list):
            st.session_state['materials'] = []
        st.session_state['materials'].append([rm, heat, dia, weight, mqty, remark])
    if st.session_state['materials']:
        st.dataframe(rows_to_df(st.session_state['materials'], ["Raw Material","Heat No","Dia/Size","Weight","Qty","Remark"]), use_container_width=True)
        if st.button("Clear Materials"):
            st.session_state['materials'] = []

    # Operations
    st.subheader("Operation Checklist")
    operations = ["Cutting","Turning (Traub/CNC)","Milling","Threading","Drilling","Punching","Deburring","Plating","Packing"]
    op_selected = {op: st.checkbox(op) for op in operations}

    # Machine Details
    st.subheader("Machine Specific Details (Optional)")
    show_machine = st.checkbox("Show Machine Details")
    machine_details = {}
    if show_machine:
        machine_type = st.selectbox("Machine Type", ["Traub", "CNC", "VMC", "Lathe", "Milling"])
        cycle_time = st.text_input("Cycle Time (sec)")
        rpm = st.text_input("RPM")
        feed = st.text_input("Feed Rate")
        machine_details = {"Machine Type": machine_type, "Cycle Time": cycle_time, "RPM": rpm, "Feed": feed}
        if machine_type == "Traub":
            gear_setup = st.text_input("Traub Gear Setup")
            machine_details["Traub Gear Setup"] = gear_setup

    # Quality
    st.subheader("Quality Instructions")
    tolerance = st.text_input("Tolerance")
    surface_finish = st.text_input("Surface Finish")
    hardness = st.text_input("Hardness Requirement")
    thread_check = st.checkbox("Thread GO/NO-GO")

    # Delivery
    st.subheader("Delivery Schedule")
    expected_date = st.date_input("Expected Delivery Date")

    # Goods Received / QC
    st.subheader("Goods Received / QC")
    grn_cols = ["Date","Qty Received","OK Qty","Rejected Qty","Remarks","QC Approved By"]
    grn_new = st.columns([1,1,1,1,1,1])
    grn_vals = [grn_new[i].text_input(grn_cols[i]) if i==0 else grn_new[i].number_input(grn_cols[i], value=0) for i in range(6)]
    if st.button("Add GRN Entry"):
        if 'grn_entries' not in st.session_state or not isinstance(st.session_state['grn_entries'], list):
            st.session_state['grn_entries'] = []
        st.session_state['grn_entries'].append(grn_vals)
    if st.session_state['grn_entries']:
        st.dataframe(rows_to_df(st.session_state['grn_entries'], grn_cols), use_container_width=True)
        if st.button("Clear GRN Entries"):
            st.session_state['grn_entries'] = []

# -----------------------------
# TAB 2: Preview (HTML-based, PDF friendly)
# -----------------------------
# -----------------------------
# TAB 2: Preview (FIXED)
# -----------------------------
# -----------------------------
# TAB 2: Preview
# -----------------------------
with tab2:
    st.markdown(f"<h1 style='color:{PRIMARY_COLOR}'>Preview Job Card</h1>", unsafe_allow_html=True)
    col_logo, col_header = st.columns([1,5])
    with col_logo: 
        if logo_file: st.image(logo_file, width=80)
    with col_header: st.markdown(f"**{company_name}**\n\n{company_address}")
    st.markdown("---")
    st.subheader("Vendor Details")
    st.markdown(f"""
    **Vendor ID:** {vendor_id}  
    **Company:** {vendor_company}  
    **Contact Person:** {vendor_person}  
    **Mobile:** {vendor_mobile}  
    **GST:** {vendor_gst}  
    **Address:** {vendor_address}
    """)
    st.markdown("---")
    st.subheader("Job Details")
    st.markdown(f"**Job No:** {job_no}  \n**Date:** {job_date}  \n**Dispatch Location:** {dispatch_location}")
    st.image(qr_bytes, width=150, caption="QR Code")
    st.subheader("Item Details")
    st.dataframe(rows_to_df(st.session_state['items'], ["Description","Drawing No","Drawing Link","Grade","Qty","UOM"]), use_container_width=True)
    st.subheader("Material Issued")
    st.dataframe(rows_to_df(st.session_state['materials'], ["Raw Material","Heat No","Dia/Size","Weight","Qty","Remark"]), use_container_width=True)
    st.subheader("Operations")
    st.write(', '.join([op for op, sel in op_selected.items() if sel]) or "None")
    if show_machine and machine_details:
        st.subheader("Machine Details")
        for k,v in machine_details.items(): st.write(f"**{k}:** {v}")
    st.subheader("Quality Instructions")
    st.write(f"Tolerance: {tolerance}")
    st.write(f"Surface Finish: {surface_finish}")
    st.write(f"Hardness: {hardness}")
    if thread_check: st.write("Thread: GO/NO-GO Required")
    st.subheader("Goods Received / QC")
    st.dataframe(rows_to_df(st.session_state['grn_entries'], ["Date","Qty Received","OK Qty","Rejected Qty","Remarks","QC Approved By"]), use_container_width=True)
# -----------------------------
# TAB 3: PDF EXPORT (WeasyPrint)
# -----------------------------
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.barcode import qr, code128
from reportlab.pdfgen.canvas import Canvas
import base64
from io import BytesIO


# -------------------------------------------------------
# PAGE NUMBERING FUNCTION
# -------------------------------------------------------
class NumberedCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        Canvas.showPage(self)

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            Canvas.showPage(self)
        Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawCentredString(
            300, 20, f"Page {self._pageNumber} of {page_count}"
        )


# -------------------------------------------------------
# MAIN PDF GENERATOR FUNCTION
# -------------------------------------------------------
def generate_jobcard_pdf(
    company_name, company_address, logo_file,
    vendor_id, vendor_company, vendor_person, vendor_mobile, vendor_gst, vendor_address,
    job_no, job_date, dispatch_location, qr_bytes,
    items_df, materials_df, grn_df,
    tolerance, surface_finish, hardness, thread_check):
        
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    story = []

    # ---------------------------------------------------
    # HEADER SECTION (Gradient + Logo With Border)
    # ---------------------------------------------------
    story.append(Spacer(1, 10))

    # Logo block
    if logo_file:
        img = Image(logo_file, width=80, height=80)
        img.hAlign = "LEFT"

        # Add border rectangle
        d = Drawing(100, 100)
        d.add(Rect(0, 0, 90, 90, strokeColor=colors.HexColor("#003366"), fillColor=None, strokeWidth=2))
        d.add(img)
        story.append(d)

    header_style = ParagraphStyle(
        "header",
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=colors.HexColor("#0A284B"),
        spaceAfter=10,
    )
    story.append(Paragraph(f"<b>{company_name}</b>", header_style))
    story.append(Paragraph(f"{company_address}", styles["Normal"]))

    story.append(Spacer(1, 12))

    # ---------------------------------------------------
    # JOB DETAILS + QR + BARCODE
    # ---------------------------------------------------
    barcode_value = f"{job_no}-{vendor_id}"
    barcode = code128.Code128(barcode_value, barHeight=40, barWidth=1.2)

   # ---------------- QR CODE ----------------
if qr_bytes:
    qr_img = Image(BytesIO(qr_bytes), width=120, height=120)
    story.append(Paragraph("<b>QR Code</b>", label_style))
    story.append(qr_img)
    story.append(Spacer(1, 10))


    top_table = Table([
        [
            Paragraph(f"""
                <b>Job No:</b> {job_no}<br/>
                <b>Date:</b> {job_date}<br/>
                <b>Dispatch:</b> {dispatch_location}
            """, styles["Normal"]),
            qr_draw,
            barcode,
        ]
    ], colWidths=[200, 120, 120])

    top_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP")
    ]))

    story.append(top_table)
    story.append(Spacer(1, 12))

    # ---------------------------------------------------
    # SUMMARY BOX (Premium Look)
    # ---------------------------------------------------
    summary = Table([
        [Paragraph("<b>Quality Summary</b>", styles["Heading4"])],
        [f"Tolerance: {tolerance}"],
        [f"Surface Finish: {surface_finish}"],
        [f"Hardness: {hardness}"],
        ["Thread Check: GO/NO-GO Required" if thread_check else "Thread: Not Applicable"]
    ], colWidths=[450])

    summary.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#DCE6F2")),
        ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#003366")),
        ("INNERGRID", (0,0), (-1,-1), 0.2, colors.gray),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
    ]))
    story.append(summary)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------
    # VENDOR DETAILS
    # ---------------------------------------------------
    story.append(Paragraph("<b>Vendor Details</b>", styles["Heading4"]))
    vendor_html = f"""
        <b>ID:</b> {vendor_id}<br/>
        <b>Company:</b> {vendor_company}<br/>
        <b>Contact Person:</b> {vendor_person}<br/>
        <b>Mobile:</b> {vendor_mobile}<br/>
        <b>GST:</b> {vendor_gst}<br/>
        <b>Address:</b> {vendor_address}<br/>
    """
    story.append(Paragraph(vendor_html, styles["Normal"]))
    story.append(Spacer(1, 12))

    # ---------------------------------------------------
    # ITEMS TABLE
    # ---------------------------------------------------
    story.append(Paragraph("<b>Item Details</b>", styles["Heading4"]))
    items_table = Table([items_df.columns.tolist()] + items_df.values.tolist(), repeatRows=1)
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0A284B")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.gray),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------
    # MATERIAL TABLE
    # ---------------------------------------------------
    story.append(Paragraph("<b>Material Issued</b>", styles["Heading4"]))
    materials_table = Table([materials_df.columns.tolist()] + materials_df.values.tolist(), repeatRows=1)
    materials_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0A284B")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.gray),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    story.append(materials_table)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------
    # GRN TABLE
    # ---------------------------------------------------
    story.append(Paragraph("<b>Goods Received / QC</b>", styles["Heading4"]))
    grn_table = Table([grn_df.columns.tolist()] + grn_df.values.tolist(), repeatRows=1)
    grn_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0A284B")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.gray),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    story.append(grn_table)
    story.append(Spacer(1, 20))

    # ---------------------------------------------------
    # SIGNATURE SECTION
    # ---------------------------------------------------
    story.append(Paragraph("<b>Signatures</b>", styles["Heading4"]))

    sig = Table([
        ["__________________", "__________________", "__________________"],
        ["Prepared By", "QC Approved", "Vendor Sign"]
    ], colWidths=[150,150,150])

    sig.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("ALIGN", (0,1), (-1,1), "CENTER")
    ]))

    story.append(sig)

    # ---------------------------------------------------
    # BUILD PDF
    # ---------------------------------------------------
    doc.build(story, canvasmaker=NumberedCanvas)

return buffer.getvalue()


# -------------------------------------------------------
# STREAMLIT DOWNLOAD BUTTON
# -------------------------------------------------------
if st.button("📄 Download Premium PDF"):
    pdf_data = generate_jobcard_pdf(
        company_name, company_address, logo_file,
        vendor_id, vendor_company, vendor_person, vendor_mobile, vendor_gst, vendor_address,
        job_no, job_date, dispatch_location, qr_bytes,
        rows_to_df(st.session_state["items"], ["Description","Drawing No","Drawing Link","Grade","Qty","UOM"]),
        rows_to_df(st.session_state["materials"], ["Raw Material","Heat No","Dia/Size","Weight","Qty","Remark"]),
        rows_to_df(st.session_state["grn_entries"], ["Date","Qty Received","OK Qty","Rejected Qty","Remarks","QC Approved By"]),
        tolerance, surface_finish, hardness, thread_check
    )

    st.download_button(
        "⬇ Download Job Card PDF",
        data=pdf_data,
        file_name=f"JobCard_{job_no}.pdf",
        mime="application/pdf"
    )

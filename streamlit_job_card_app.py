import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from datetime import date as dt_date

st.set_page_config(page_title="Dynamic Vendor Job Card", layout="wide")
PRIMARY_COLOR = "#0d6efd"

# -----------------------------
# Initialize session state safely
# -----------------------------
for key in ['items', 'materials', 'grn_entries']:
    if key not in st.session_state or st.session_state[key] is None:
        st.session_state[key] = []

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
    """
    Converts a list of rows into a DataFrame safely.
    Handles None, empty, or malformed rows.
    """
    if not isinstance(rows, list) or len(rows) == 0:
        return pd.DataFrame(columns=columns)
    
    safe_rows = []
    for r in rows:
        # Ensure each row is a list
        if not isinstance(r, list):
            r = [""] * len(columns)
        elif len(r) < len(columns):
            r = r + [""] * (len(columns) - len(r))
        elif len(r) > len(columns):
            r = r[:len(columns)]
        safe_rows.append(r)
    
    return pd.DataFrame(safe_rows, columns=columns)

def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(A4[0]-20*mm, 10*mm, f"Page {page_num}")

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
    st.subheader("Company Header (Constant)")
    col_logo, col_name = st.columns([1,5])
    with col_logo:
        logo_file = st.file_uploader("Upload Company Logo", type=["png","jpg","jpeg"])
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
    with col1: job_no = st.text_input("Job Card No.", value=f"JC-{dt_date.today().strftime('%Y%m%d')}")
    with col2: job_date = st.date_input("Date", dt_date.today())
    with col3: dispatch_location = st.text_input("Dispatch Location")

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
        st.session_state.items.append([desc, drawing_no, drawing_link, grade, qty, uom])
    if st.session_state.items:
        st.dataframe(rows_to_df(st.session_state.items, ["Description","Drawing No","Drawing Link","Grade","Qty","UOM"]), use_container_width=True)
        if st.button("Clear Items"): st.session_state.items = []

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
        st.session_state.materials.append([rm, heat, dia, weight, mqty, remark])
    if st.session_state.materials:
        st.dataframe(rows_to_df(st.session_state.materials, ["Raw Material","Heat No","Dia/Size","Weight","Qty","Remark"]), use_container_width=True)
        if st.button("Clear Materials"): st.session_state.materials = []

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
    if st.button("Add GRN Entry"): st.session_state.grn_entries.append(grn_vals)
    if st.session_state.grn_entries:
        st.dataframe(rows_to_df(st.session_state.grn_entries, grn_cols), use_container_width=True)
        if st.button("Clear GRN Entries"): st.session_state.grn_entries = []

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
    st.dataframe(rows_to_df(st.session_state.items, ["Description","Drawing No","Drawing Link","Grade","Qty","UOM"]), use_container_width=True)
    st.subheader("Material Issued")
    st.dataframe(rows_to_df(st.session_state.materials, ["Raw Material","Heat No","Dia/Size","Weight","Qty","Remark"]), use_container_width=True)
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
    st.dataframe(rows_to_df(st.session_state.grn_entries, ["Date","Qty Received","OK Qty","Rejected Qty","Remarks","QC Approved By"]), use_container_width=True)
    st.markdown(f"<button onclick='window.print()' style='background-color:{PRIMARY_COLOR};color:white;padding:8px 20px;border:none;border-radius:4px;'>🖨️ Print Job Card</button>", unsafe_allow_html=True)

# -----------------------------
# TAB 3: PDF Export
# -----------------------------
with tab3:
    st.markdown(f"<h1 style='color:{PRIMARY_COLOR}'>Export Professional Job Card PDF</h1>", unsafe_allow_html=True)
    if st.button("Generate PDF"):
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=40, bottomMargin=30)
        styles = getSampleStyleSheet()
        story = []

        def header_footer(canvas, doc):
            if logo_file:
                logo = Image.open(logo_file)
                logo.thumbnail((50,50))
                canvas.drawInlineImage(logo, 20, A4[1]-60)
            canvas.setFont('Helvetica-Bold', 14)
            canvas.drawString(80, A4[1]-40, company_name)
            canvas.setFont('Helvetica', 10)
            canvas.drawString(80, A4[1]-55, company_address)
            add_page_number(canvas, doc)

        # Vendor Table
        vendor_data = [["Vendor ID", vendor_id],["Company", vendor_company],["Contact", vendor_person],
                       ["Mobile", vendor_mobile],["GST", vendor_gst],["Address", vendor_address]]
        tbl = Table(vendor_data, colWidths=[120, 300])
        tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black),
                                 ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#dbe5f1")),
                                 ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
        story.append(tbl)
        story.append(Spacer(1,10))

        # Job Details Table
        job_data = [["Job No", job_no],["Date", job_date],["Dispatch Location", dispatch_location]]
        tbl = Table(job_data, colWidths=[120,300])
        tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black),
                                 ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#f2f2f2"))]))
        story.append(tbl)
        story.append(Spacer(1,6))

        # QR
        qr_rl = RLImage(BytesIO(qr_bytes), width=100, height=100)
        story.append(qr_rl)
        story.append(Spacer(1,12))

        # Items Table
        items_df = rows_to_df(st.session_state.items, ["Description","Drawing No","Drawing Link","Grade","Qty","UOM"])
        if not items_df.empty:
            data = [items_df.columns.tolist()] + items_df.fillna("").values.tolist()
            tbl = Table(data, colWidths=[120,80,80,60,40,40])
            tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black),
                                     ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#a7c7e7")),
                                     ('ALIGN',(0,0),(-1,-1),'CENTER')]))
            story.append(tbl)
            story.append(Spacer(1,10))

        # Materials Table
        mat_df = rows_to_df(st.session_state.materials, ["Raw Material","Heat No","Dia/Size","Weight","Qty","Remark"])
        if not mat_df.empty:
            data = [mat_df.columns.tolist()] + mat_df.fillna("").values.tolist()
            tbl = Table(data, colWidths=[100,60,50,50,40,60])
            tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black),
                                     ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#cfe2f3")),
                                     ('ALIGN',(0,0),(-1,-1),'CENTER')]))
            story.append(tbl)
            story.append(Spacer(1,10))

        # Operations
        story.append(Paragraph("Operations Selected", styles['Heading2']))
        ops_text = ', '.join([op for op, sel in op_selected.items() if sel]) or "None"
        story.append(Paragraph(ops_text, styles['Normal']))
        story.append(Spacer(1,10))

        # Machine
        if show_machine and machine_details:
            story.append(Paragraph("Machine Details", styles['Heading2']))
            for k,v in machine_details.items(): story.append(Paragraph(f"{k}: {v}", styles['Normal']))
            story.append(Spacer(1,10))

        # Quality
        story.append(Paragraph("Quality Instructions", styles['Heading2']))
        story.append(Paragraph(f"Tolerance: {tolerance}", styles['Normal']))
        story.append(Paragraph(f"Surface Finish: {surface_finish}", styles['Normal']))
        story.append(Paragraph(f"Hardness: {hardness}", styles['Normal']))
        if thread_check: story.append(Paragraph("Thread: GO/NO-GO Required", styles['Normal']))
        story.append(Spacer(1,10))

        # GRN
        grn_df = rows_to_df(st.session_state.grn_entries, ["Date","Qty Received","OK Qty","Rejected Qty","Remarks","QC Approved By"])
        if not grn_df.empty:
            data = [grn_df.columns.tolist()] + grn_df.fillna("").values.tolist()
            tbl = Table(data, colWidths=[70,50,50,50,80,80])
            tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black),
                                     ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#e2f0d9")),
                                     ('ALIGN',(0,0),(-1,-1),'CENTER')]))
            story.append(tbl)
            story.append(Spacer(1,12))

        doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
        buf.seek(0)
        st.download_button("⬇️ Download Multi-Page Job Card PDF", buf, "vendor_job_card.pdf", mime="application/pdf")


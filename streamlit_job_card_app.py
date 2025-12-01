import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Dynamic Vendor Job Card", layout="wide")

st.title("📦 Vendor Job Card – Dynamic Generator")

# --- Header ---
st.subheader("Company Header")
company_name = st.text_input("Company Name")
company_address = st.text_area("Company Address")

# QR Code
data_for_qr = st.text_input("QR Code Data (Job No., Vendor ID, etc.)")
qr_img = None
if data_for_qr:
    qr = qrcode.QRCode(box_size=4)
    qr.add_data(data_for_qr)
    qr.make()
    qr_img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    st.image(buf.getvalue(), width=120, caption="QR Code Preview")

# --- Job Card Info ---
st.subheader("Job Card Details")
col1, col2, col3 = st.columns(3)
with col1:
    job_no = st.text_input("Job Card No.")
with col2:
    date = st.date_input("Date")
with col3:
    vendor_name = st.text_input("Vendor Name")

# --- Item Details ---
st.subheader("Item Details")
item_table = st.data_editor(pd.DataFrame({
    "Description": [""],
    "Drawing No.": [""],
    "Drawing Link": [""],
    "Grade": [""],
    "Qty": [0],
    "UOM": ["Nos"]
}))

# Material Issued
st.subheader("Material Issued to Vendor")
material_table = st.data_editor(pd.DataFrame({
    "Raw Material": [""],
    "Heat No.": [""],
    "Dia/Size": [""],
    "Weight": [0],
    "Qty": [0],
    "Remark": [""]
}))

# --- Operation Plan with checkboxes ---
st.subheader("Operation Plan")
operations = ["Cutting", "Turning (Traub/CNC)", "Milling", "Threading", "Drilling", "Punching", "Deburring", "Plating", "Packing"]
op_selected = {}
for op in operations:
    op_selected[op] = st.checkbox(op)

# Machine-specific optional block
st.subheader("Machine Specific Details (Optional)")
show_machine = st.checkbox("Show Machine Details")
if show_machine:
    machine_type = st.selectbox("Machine Type", ["Traub", "CNC", "VMC", "Lathe", "Milling"])
    colm1, colm2, colm3 = st.columns(3)
    with colm1:
        cycle_time = st.text_input("Cycle Time (sec)")
    with colm2:
        rpm = st.text_input("RPM")
    with colm3:
        feed = st.text_input("Feed Rate")
    if machine_type == "Traub":
        gear = st.text_input("Traub Gear Setup Details")

# Quality Instructions
st.subheader("Quality Instructions")
tolerance = st.text_input("Tolerance")
finish = st.text_input("Surface Finish")
hardness = st.text_input("Hardness Requirement")
thread_gauges = st.checkbox("Thread must pass GO gauge and fail NO-GO gauge")

# Delivery Schedule
st.subheader("Delivery Schedule")
exp_date = st.date_input("Expected Delivery Date")
dispatch_loc = st.text_input("Dispatch Location")

# Goods Received Table
st.subheader("Goods Received From Vendor")
grv_table = st.data_editor(pd.DataFrame({
    "Date": [""],
    "Qty Received": [0],
    "OK Qty": [0],
    "Rejected Qty": [0],
    "Remarks": [""],
    "QC Approved By": [""]
}))

# Generate PDF
st.subheader("Generate Job Card PDF")

def make_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles['Title']))
    story.append(Spacer(1, 12))

    # Job details
    story.append(Paragraph(f"<b>Job Card No:</b> {job_no}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {date}", styles['Normal']))
    story.append(Paragraph(f"<b>Vendor:</b> {vendor_name}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Item details
    story.append(Paragraph("<b>Item Details:</b>", styles['Heading2']))
    story.append(Paragraph(item_table.to_html(), styles['Normal']))

    # Material issued
    story.append(Paragraph("<b>Material Issued:</b>", styles['Heading2']))
    story.append(Paragraph(material_table.to_html(), styles['Normal']))

    # Operations
    story.append(Paragraph("<b>Operations Selected:</b> " + ", ".join([op for op, val in op_selected.items() if val]), styles['Normal']))

    # Machine details if any
    if show_machine:
        story.append(Paragraph(f"Machine Type: {machine_type}", styles['Normal']))
        story.append(Paragraph(f"Cycle Time: {cycle_time}", styles['Normal']))

    # Quality
    story.append(Paragraph("<b>Quality Instructions:</b>", styles['Heading2']))
    story.append(Paragraph(f"Tolerance: {tolerance}", styles['Normal']))
    story.append(Paragraph(f"Finish: {finish}", styles['Normal']))

    # Delivery
    story.append(Paragraph("<b>Delivery Details:</b>", styles['Heading2']))
    story.append(Paragraph(f"Expected Date: {exp_date}", styles['Normal']))
    story.append(Paragraph(f"Dispatch: {dispatch_loc}", styles['Normal']))

    # Goods Received Table
    story.append(Paragraph("<b>GRN Table:</b>", styles['Heading2']))
    story.append(Paragraph(grv_table.to_html(), styles['Normal']))

    # QR Code info (if generated)
    if qr_img:
        story.append(Spacer(1, 20))
        story.append(Paragraph("QR Code:", styles['Heading2']))

    doc.build(story)
    buffer.seek(0)
    return buffer

if st.button("Generate PDF"):
    pdf_bytes = make_pdf().getvalue()
    st.download_button("Download Job Card PDF", pdf_bytes, file_name="job_card.pdf", mime="application/pdf")


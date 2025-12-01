import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Dynamic Vendor Job Card", layout="wide")

# ----------------------------------------------------
# COMPANY HEADER (STATIC + LOGO)
# ----------------------------------------------------
st.title("📦 Vendor Job Card – Dynamic Generator")

st.subheader("Company Header (Constant)")
logo_file = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])
company_name = st.text_input("Your Company Name (Header)")
company_address = st.text_area("Your Company Address (Header)")

# ----------------------------------------------------
# VENDOR DETAILS SECTION
# ----------------------------------------------------
st.subheader("Vendor Details")
vendor_id = st.text_input("Vendor ID")
colv1, colv2 = st.columns(2)
with colv1:
    vendor_company = st.text_input("Vendor Company Name")
    vendor_person = st.text_input("Vendor Contact Person")
    vendor_mobile = st.text_input("Vendor Mobile Number")
with colv2:
    vendor_gst = st.text_input("Vendor GST Number")
    vendor_address = st.text_area("Vendor Address")

# QR Code for vendor/job
generated_qr = f"JobNo: {job_no} | Date: {date} | Dispatch: {dispatch_location}"
st.write("QR Code auto-generated from Job No + Date + Dispatch Location")
qr = qrcode.QRCode(box_size=4)
qr.add_data(generated_qr)
qr.make()
qr_img = qr.make_image(fill_color="black", back_color="white")
buf = BytesIO()
qr_img.save(buf, format="PNG")
st.image(buf.getvalue(), width=120, caption="QR Code Preview")
# ----------------------------------------------------
# JOB CARD INFO
# ----------------------------------------------------
st.subheader("Job Card Details")
col1, col2, col3 = st.columns(3)
with col1:
    job_no = st.text_input("Job Card No.")
with col2:
    date = st.date_input("Date")
with col3:
    dispatch_location = st.text_input("Dispatch Location")

# ----------------------------------------------------
# ITEM DETAILS
# ----------------------------------------------------
st.subheader("Item Details")
item_table = st.data_editor(pd.DataFrame({
    "Description": [""],
    "Drawing No": [""],
    "Drawing Link": [""],
    "Grade": [""],
    "Qty": [0],
    "UOM": ["Nos"]
}))

# ----------------------------------------------------
# MATERIAL ISSUED
# ----------------------------------------------------
st.subheader("Material Issued to Vendor")
material_table = st.data_editor(pd.DataFrame({
    "Raw Material": [""],
    "Heat No": [""],
    "Dia/Size": [""],
    "Weight": [0],
    "Qty": [0],
    "Remark": [""]
}))

# ----------------------------------------------------
# OPERATIONS
# ----------------------------------------------------
st.subheader("Operation Checklist")
operations = [
    "Cutting", "Turning (Traub/CNC)", "Milling", "Threading", "Drilling",
    "Punching", "Deburring", "Plating", "Packing"
]
op_selected = {}
for op in operations:
    op_selected[op] = st.checkbox(op)

# ----------------------------------------------------
# MACHINE DETAILS (OPTIONAL, DYNAMIC)
# ----------------------------------------------------
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
        gear_setup = st.text_input("Traub Gear Setup Details")

# ----------------------------------------------------
# QUALITY
# ----------------------------------------------------
st.subheader("Quality Instructions")
tolerance = st.text_input("Tolerance")
finish = st.text_input("Surface Finish")
hardness = st.text_input("Hardness Requirement")
thread_check = st.checkbox("Thread must pass GO gauge and fail NO-GO gauge")

# ----------------------------------------------------
# DELIVERY
# ----------------------------------------------------
st.subheader("Delivery Schedule")
expected_date = st.date_input("Expected Delivery Date")

# ----------------------------------------------------
# GOODS RECEIVED
# ----------------------------------------------------
st.subheader("Goods Received From Vendor")
grv_table = st.data_editor(pd.DataFrame({
    "Date": [""],
    "Qty Received": [0],
    "OK Qty": [0],
    "Rejected Qty": [0],
    "Remarks": [""],
    "QC Approved By": [""]
}))

# ----------------------------------------------------
# PDF GENERATION
# ----------------------------------------------------
st.subheader("Generate Job Card PDF")

def make_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Company Header with Logo
    if logo_file:
        logo = RLImage(logo_file, width=80, height=80)
        story.append(logo)
    story.append(Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles['Title']))
    story.append(Spacer(1, 12))

    # Vendor
    story.append(Paragraph(f"<b>Vendor Company:</b> {vendor_company}", styles['Normal']))
    story.append(Paragraph(f"<b>Vendor Person:</b> {vendor_person}", styles['Normal']))
    story.append(Paragraph(f"<b>Mobile:</b> {vendor_mobile}", styles['Normal']))
    story.append(Paragraph(f"<b>GST:</b> {vendor_gst}", styles['Normal']))
    story.append(Paragraph(f"<b>Address:</b> {vendor_address}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Job details
    story.append(Paragraph(f"<b>Job No:</b> {job_no}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {date}", styles['Normal']))
    story.append(Paragraph(f"<b>Dispatch Location:</b> {dispatch_location}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Tables
    story.append(Paragraph("<b>Item Details:</b>", styles['Heading2']))
    story.append(Paragraph(item_table.to_html(), styles['Normal']))

    story.append(Paragraph("<b>Material Issued:</b>", styles['Heading2']))
    story.append(Paragraph(material_table.to_html(), styles['Normal']))

    story.append(Paragraph("<b>Operations:</b> " + ", ".join([op for op, v in op_selected.items() if v]), styles['Normal']))

    if show_machine:
        story.append(Paragraph(f"<b>Machine:</b> {machine_type}", styles['Normal']))
        story.append(Paragraph(f"Cycle Time: {cycle_time}", styles['Normal']))
        story.append(Paragraph(f"RPM: {rpm}", styles['Normal']))
        story.append(Paragraph(f"Feed: {feed}", styles['Normal']))
        if machine_type == "Traub":
            story.append(Paragraph(f"Gear Setup: {gear_setup}", styles['Normal']))

    # Quality
    story.append(Paragraph("<b>Quality:</b>", styles['Heading2']))
    story.append(Paragraph(f"Tolerance: {tolerance}", styles['Normal']))
    story.append(Paragraph(f"Finish: {finish}", styles['Normal']))
    story.append(Paragraph(f"Hardness: {hardness}", styles['Normal']))

    # GRN
    story.append(Paragraph("<b>Goods Received:</b>", styles['Heading2']))
    story.append(Paragraph(grv_table.to_html(), styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

if st.button("Generate PDF"):
    pdf_data = make_pdf().getvalue()
    st.download_button("⬇️ Download Job Card PDF", pdf_data, "job_card.pdf", mime="application/pdf")

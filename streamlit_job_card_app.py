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
colv1, colv2 = st.columns(2)
with colv1:
    vendor_id = st.text_input("Vendor ID")
    vendor_company = st.text_input("Vendor Company Name")
    vendor_person = st.text_input("Vendor Contact Person")
    vendor_mobile = st.text_input("Vendor Mobile Number")
with colv2:
    vendor_gst = st.text_input("Vendor GST Number")
    vendor_address = st.text_area("Vendor Address")

# ----------------------------------------------------
# JOB CARD INFO
# ----------------------------------------------------
st.subheader("Job Card Details")
col1, col2, col3 = st.columns(3)
with col1:
    job_no = st.text_input("Job Card No.", value=f"JC-{pd.Timestamp.now().strftime('%Y%m%d-%H%M%S')}")
with col2:
    date = st.date_input("Date")
with col3:
    dispatch_location = st.text_input("Dispatch Location")

# After job info, auto-generate QR combining JobNo, Date, Dispatch, Vendor ID
qr_img = None
if job_no and date and dispatch_location:
    qr_text = f"JobNo:{job_no} | Date:{date} | Dispatch:{dispatch_location} | VendorID:{vendor_id}"
    qr = qrcode.QRCode(box_size=4)
    qr.add_data(qr_text)
    qr.make()
    qr_img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    st.image(buf.getvalue(), width=140, caption="QR Code Preview")
    st.caption("QR encodes: JobNo | Date | Dispatch Location | VendorID")
else:
    st.info("QR will auto-generate when Job No, Date and Dispatch Location are filled")

# ----------------------------------------------------
# ITEM DETAILS (dynamic add/delete)
# ----------------------------------------------------
st.subheader("Item Details")
if 'item_rows' not in st.session_state:
    st.session_state.item_rows = []

if st.button("Add Item"):
    st.session_state.item_rows.append({"description":"","drawing_no":"","drawing_link":"","grade":"","qty":0.0,"uom":"Nos"})

for i, row in enumerate(st.session_state.item_rows):
    st.markdown(f"### Item {i+1}")
    col1, col2, col3 = st.columns(3)
    row["description"] = col1.text_input("Description", row["description"], key=f"desc_{i}")
    row["drawing_no"] = col2.text_input("Drawing No.", row["drawing_no"], key=f"draw_{i}")
    row["drawing_link"] = col3.text_input("Drawing Link", row["drawing_link"], key=f"link_{i}")
    col4, col5, col6 = st.columns(3)
    row["grade"] = col4.text_input("Grade", row["grade"], key=f"grade_{i}")
    row["qty"] = col5.number_input("Qty", value=float(row.get("qty",0.0)), key=f"qty_{i}")
    row["uom"] = col6.text_input("UOM", row["uom"], key=f"uom_{i}")
    if st.button(f"Delete Item {i+1}"):
        st.session_state.item_rows.pop(i)
        st.experimental_rerun()

# If no dynamic items, show an editable table fallback
if not st.session_state.item_rows:
    item_table = st.data_editor(pd.DataFrame({
        "Description": [""],
        "Drawing No": [""],
        "Drawing Link": [""],
        "Grade": [""],
        "Qty": [0],
        "UOM": ["Nos"]
    }))
else:
    item_table = pd.DataFrame(st.session_state.item_rows)

# ----------------------------------------------------
# MATERIAL ISSUED (dynamic add/delete)
# ----------------------------------------------------
st.subheader("Material Issued to Vendor")
if 'mat_rows' not in st.session_state:
    st.session_state.mat_rows = []

if st.button("Add Material"):
    st.session_state.mat_rows.append({"raw":"","heat":"","size":"","weight":0.0,"qty":0.0,"remark":""})

for j, row in enumerate(st.session_state.mat_rows):
    st.markdown(f"### Material {j+1}")
    col1, col2, col3 = st.columns(3)
    row["raw"] = col1.text_input("Raw Material", row["raw"], key=f"mat_raw_{j}")
    row["heat"] = col2.text_input("Heat No.", row["heat"], key=f"mat_heat_{j}")
    row["size"] = col3.text_input("Dia / Size", row["size"], key=f"mat_size_{j}")
    col4, col5, col6 = st.columns(3)
    row["weight"] = col4.number_input("Weight", value=float(row.get("weight",0.0)), key=f"mat_weight_{j}")
    row["qty"] = col5.number_input("Qty", value=float(row.get("qty",0.0)), key=f"mat_qty_{j}")
    row["remark"] = col6.text_input("Remark", row["remark"], key=f"mat_remark_{j}")
    if st.button(f"Delete Material {j+1}"):
        st.session_state.mat_rows.pop(j)
        st.experimental_rerun()

# If no dynamic materials, show editable table fallback
if not st.session_state.mat_rows:
    material_table = st.data_editor(pd.DataFrame({
        "Raw Material": [""],
        "Heat No": [""],
        "Dia/Size": [""],
        "Weight": [0.0],
        "Qty": [0.0],
        "Remark": [""]
    }))
else:
    material_table = pd.DataFrame(st.session_state.mat_rows)

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
if 'grn_rows' not in st.session_state:
    st.session_state.grn_rows = []

if st.button("Add GRN Entry"):
    st.session_state.grn_rows.append({"date":"","qty_received":0.0,"ok_qty":0.0,"rejected_qty":0.0,"remarks":"","qc_by":""})

for k, row in enumerate(st.session_state.grn_rows):
    st.markdown(f"### GRN {k+1}")
    col1, col2, col3 = st.columns(3)
    row["date"] = col1.text_input("Date", row["date"], key=f"grn_date_{k}")
    row["qty_received"] = col2.number_input("Qty Received", value=float(row.get("qty_received",0.0)), key=f"grn_qty_{k}")
    row["ok_qty"] = col3.number_input("OK Qty", value=float(row.get("ok_qty",0.0)), key=f"grn_ok_{k}")
    col4, col5, col6 = st.columns(3)
    row["rejected_qty"] = col4.number_input("Rejected Qty", value=float(row.get("rejected_qty",0.0)), key=f"grn_rej_{k}")
    row["remarks"] = col5.text_input("Remarks", row["remarks"], key=f"grn_rem_{k}")
    row["qc_by"] = col6.text_input("QC Approved By", row["qc_by"], key=f"grn_qc_{k}")
    if st.button(f"Delete GRN {k+1}"):
        st.session_state.grn_rows.pop(k)
        st.experimental_rerun()

if not st.session_state.grn_rows:
    grv_table = st.data_editor(pd.DataFrame({
        "Date": [""],
        "Qty Received": [0],
        "OK Qty": [0],
        "Rejected Qty": [0],
        "Remarks": [""],
        "QC Approved By": [""]
    }))
else:
    grv_table = pd.DataFrame(st.session_state.grn_rows)

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
        try:
            logo = RLImage(logo_file, width=80, height=80)
            story.append(logo)
        except Exception:
            pass
    story.append(Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles['Title']))
    story.append(Spacer(1, 12))

    # Vendor
    story.append(Paragraph(f"<b>Vendor ID:</b> {vendor_id}", styles['Normal']))
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
    story.append(Paragraph(item_table.to_html(index=False), styles['Normal']))

    story.append(Paragraph("<b>Material Issued:</b>", styles['Heading2']))
    story.append(Paragraph(material_table.to_html(index=False), styles['Normal']))

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
    story.append(Paragraph(grv_table.to_html(index=False), styles['Normal']))

    # Include QR image in PDF (if available)
    if qr_img:
        try:
            qr_buf = BytesIO()
            qr_img.save(qr_buf, format='PNG')
            qr_buf.seek(0)
            rl_qr = RLImage(qr_buf, width=100, height=100)
            story.append(Spacer(1, 12))
            story.append(rl_qr)
        except Exception:
            pass

    doc.build(story)
    buffer.seek(0)
    return buffer

if st.button("Generate PDF"):
    pdf_data = make_pdf().getvalue()
    st.download_button("⬇️ Download Job Card PDF", pdf_data, "job_card.pdf", mime="application/pdf")

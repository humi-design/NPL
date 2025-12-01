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
        # st.experimental_rerun()  # Removed to prevent Streamlit Cloud AttributeError

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
        # st.experimental_rerun()  # Removed to prevent Streamlit Cloud AttributeError

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
        # st.experimental_rerun()  # Removed to prevent Streamlit Cloud AttributeError

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
# PDF GENERATION (IMPROVED, STRUCTURED, ATTRACTIVE)
# ----------------------------------------------------
st.subheader("Generate Job Card PDF")
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

def make_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []

    # Company Header Block
    header_data = []
    if logo_file:
        header_data.append([RLImage(logo_file, width=60, height=60), Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles['Title'])])
    else:
        header_data.append(["", Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles['Title'])])

    header_table = Table(header_data, colWidths=[70, 430])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12)
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    # Job Card Title Bar
    story.append(Paragraph('<para alignment="center"><b><font size=16>VENDOR JOB CARD</font></b></para>', styles['Title']))
    story.append(Spacer(1, 12))

    # Vendor Info Block
    vendor_block = [
        ['Vendor ID', vendor_id],
        ['Vendor Company', vendor_company],
        ['Contact Person', vendor_person],
        ['Mobile', vendor_mobile],
        ['GST Number', vendor_gst],
        ['Address', vendor_address]
    ]
    vendor_table = Table(vendor_block, colWidths=[120, 380])
    vendor_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    story.append(vendor_table)
    story.append(Spacer(1, 18))

    # Job Details Block
    job_block = [
        ['Job Card No', job_no],
        ['Date', str(date)],
        ['Dispatch Location', dispatch_location]
    ]
    job_table = Table(job_block, colWidths=[150, 350])
    job_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(job_table)
    story.append(Spacer(1, 18))

    # QR Code
    if qr_img:
        buf_qr = BytesIO()
        qr_img.save(buf_qr, format='PNG')
        story.append(RLImage(buf_qr, width=90, height=90))
        story.append(Spacer(1, 12))

    # ITEM DETAILS TABLE
    story.append(Paragraph('<b>Item Details</b>', styles['Heading2']))
    item_tbl = Table([item_table.columns.tolist()] + item_table.values.tolist(), repeatRows=1)
    item_tbl.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(item_tbl)
    story.append(Spacer(1, 18))

    # MATERIAL ISSUED
    story.append(Paragraph('<b>Material Issued to Vendor</b>', styles['Heading2']))
    material_tbl = Table([material_table.columns.tolist()] + material_table.values.tolist(), repeatRows=1)
    material_tbl.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgreen),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(material_tbl)
    story.append(Spacer(1, 18))

    # OPERATIONS
    story.append(Paragraph('<b>Operations Selected</b>', styles['Heading2']))
    selected_ops = ', '.join([op for op, val in op_selected.items() if val]) or 'None'
    story.append(Paragraph(selected_ops, styles['Normal']))
    story.append(Spacer(1, 12))

    # MACHINE DETAILS
    if show_machine:
        story.append(Paragraph('<b>Machine Details</b>', styles['Heading2']))
        machine_data = [
            ['Machine Type', machine_type],
            ['Cycle Time', cycle_time],
            ['RPM', rpm],
            ['Feed', feed]
        ]
        if machine_type == 'Traub':
            machine_data.append(['Traub Gear Setup', gear_setup])

        machine_tbl = Table(machine_data, colWidths=[150, 350])
        machine_tbl.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightpink)
        ]))
        story.append(machine_tbl)
        story.append(Spacer(1, 18))

    # QUALITY
    story.append(Paragraph('<b>Quality Instructions</b>', styles['Heading2']))
    quality_items = f"Tolerance: {tolerance}<br/>Surface Finish: {finish}<br/>Hardness: {hardness}"
    story.append(Paragraph(quality_items, styles['Normal']))
    story.append(Spacer(1, 18))

    # GOODS RECEIVED
    story.append(Paragraph('<b>Goods Received</b>', styles['Heading2']))
    grv_tbl = Table([grv_table.columns.tolist()] + grv_table.values.tolist(), repeatRows=1)
    grv_tbl.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.orange),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    story.append(grv_tbl)

    doc.build(story)
    buffer.seek(0)
    return buffer

if st.button("Generate PDF"):
    pdf_data = make_pdf().getvalue()
    st.download_button("⬇️ Download Job Card PDF", pdf_data, "job_card.pdf", mime="application/pdf")

import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import base64
from datetime import datetime

# Page config
st.set_page_config(page_title="Vendor Job Card", layout="wide")

# Theme colors
PRIMARY_COLOR = "#1e3a8a"  # Blue
ACCENT_COLOR = "#6b7280"   # Grey

# -------------------------------
# Initialize session state safely
# -------------------------------
if "next_job_no" not in st.session_state:
    st.session_state.next_job_no = datetime.now().strftime("JC-%Y%m%d-%H%M%S")

for key in ("items", "materials", "grn_entries"):
    if key not in st.session_state or not isinstance(st.session_state[key], list):
        st.session_state[key] = []

# -----------------------------------------
# Helper: QR bytes
# -----------------------------------------
def make_qr_bytes(text, size=300):
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue(), img

# -----------------------------------------
# Helper: convert list-of-dicts to dataframe
# -----------------------------------------
def rows_to_df(rows, columns):
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows)

# -----------------------------------------
# Tabs: Input | Preview | PDF
# -----------------------------------------
tab1, tab2, tab3 = st.tabs(["✍️ Input", "👁️ Preview", "📄 PDF Export"])

# -------------------------
# TAB 1: INPUT
# -------------------------
with tab1:
    st.markdown(f"<h1 style='color:{PRIMARY_COLOR}'>Vendor Job Card - Input</h1>", unsafe_allow_html=True)

    # Header
    col_logo, col_header = st.columns([1, 5])
    with col_logo:
        logo_file = st.file_uploader("Company Logo (png/jpg)", type=["png", "jpg", "jpeg"])
    with col_header:
        st.subheader("Company Header (Constant)")
        company_name = st.text_input("Company Name", value="Your Company Pvt Ltd")
        company_address = st.text_area("Company Address", value="Street, City, State\nPin - 400xxx")

    st.markdown("---")

    # Vendor Details
    st.subheader("Vendor Details")
    v1, v2 = st.columns(2)
    with v1:
        vendor_id = st.text_input("Vendor ID")
        vendor_company = st.text_input("Vendor Company Name")
        vendor_person = st.text_input("Vendor Contact Person")
    with v2:
        vendor_mobile = st.text_input("Vendor Mobile Number")
        vendor_gst = st.text_input("Vendor GST Number")
        vendor_address = st.text_area("Vendor Address")

    st.markdown("---")

    # Job Details
    st.subheader("Job Details")
    j1, j2, j3 = st.columns(3)
    with j1:
        job_no = st.text_input("Job Card No.", value=st.session_state.next_job_no)
    with j2:
        job_date = st.date_input("Date", value=pd.to_datetime("today"))
    with j3:
        dispatch_location = st.text_input("Dispatch Location")

    st.markdown("---")

    # Items (dynamic)
    st.subheader("Item Details (Add/Delete rows)")
    if st.button("➕ Add Item"):
        st.session_state.items.append({"Description": "", "Drawing No": "", "Drawing Link": "", "Grade": "", "Qty": 0, "UOM": "Nos"})

    remove_idx = None
    for i, it in enumerate(st.session_state.items):
        cols = st.columns([3,2,2,1,1,0.5])
        it["Description"] = cols[0].text_input(f"Description #{i+1}", value=it.get("Description",""), key=f"item_desc_{i}")
        it["Drawing No"] = cols[1].text_input("Drawing No", value=it.get("Drawing No",""), key=f"item_draw_{i}")
        it["Drawing Link"] = cols[2].text_input("Drawing Link", value=it.get("Drawing Link",""), key=f"item_link_{i}")
        it["Grade"] = cols[3].text_input("Grade", value=it.get("Grade",""), key=f"item_grade_{i}")
        it["Qty"] = cols[4].number_input("Qty", value=float(it.get("Qty",0)), key=f"item_qty_{i}")
        if cols[5].button("🗑️", key=f"del_item_{i}"):
            remove_idx = i
    if remove_idx is not None:
        st.session_state.items.pop(remove_idx)

    st.markdown("---")

    # Material Issued
    st.subheader("Material Issued to Vendor (Add/Delete rows)")
    if st.button("➕ Add Material"):
        st.session_state.materials.append({"Raw Material": "", "Heat No": "", "Dia/Size": "", "Weight": 0.0, "Qty": 0.0, "Remark": ""})
    remove_m = None
    for j, mt in enumerate(st.session_state.materials):
        cols = st.columns([2,2,1,1,1,0.5])
        mt["Raw Material"] = cols[0].text_input(f"Raw Material #{j+1}", value=mt.get("Raw Material",""), key=f"mat_raw_{j}")
        mt["Heat No"] = cols[1].text_input("Heat No", value=mt.get("Heat No",""), key=f"mat_heat_{j}")
        mt["Dia/Size"] = cols[2].text_input("Dia/Size", value=mt.get("Dia/Size",""), key=f"mat_size_{j}")
        mt["Weight"] = cols[3].number_input("Weight", value=float(mt.get("Weight",0.0)), key=f"mat_weight_{j}")
        mt["Qty"] = cols[4].number_input("Qty", value=float(mt.get("Qty",0.0)), key=f"mat_qty_{j}")
        if cols[5].button("🗑️", key=f"del_mat_{j}"):
            remove_m = j
    if remove_m is not None:
        st.session_state.materials.pop(remove_m)

    st.markdown("---")

    # Operations
    st.subheader("Operation Checklist")
    operations = [
        "Cutting", "Turning (Traub/CNC)", "Milling", "Threading", "Drilling",
        "Punching", "Deburring", "Plating", "Packing"
    ]
    op_selected = {}
    cols_ops = st.columns(3)
    for idx, op in enumerate(operations):
        op_selected[op] = cols_ops[idx % 3].checkbox(op, value=False, key=f"op_{op}")

    st.markdown("---")

    # Machine Details
    st.subheader("Machine Specific Details (Optional)")
    show_machine = st.checkbox("Show Machine Details")
    machine_details = {}
    if show_machine:
        machine_type = st.selectbox("Machine Type", ["Traub", "CNC", "VMC", "Lathe", "Milling"])
        mc1, mc2, mc3 = st.columns(3)
        cycle_time = mc1.text_input("Cycle Time (sec)")
        rpm = mc2.text_input("RPM")
        feed = mc3.text_input("Feed Rate")
        if machine_type == "Traub":
            gear_setup = st.text_input("Traub Gear Setup")
            machine_details = {"Machine Type": machine_type, "Cycle Time": cycle_time, "RPM": rpm, "Feed": feed, "Gear Setup": gear_setup}
        else:
            machine_details = {"Machine Type": machine_type, "Cycle Time": cycle_time, "RPM": rpm, "Feed": feed}

    st.markdown("---")

    # Quality Instructions
    st.subheader("Quality Instructions")
    tolerance = st.text_input("Tolerance (as per drawing)")
    surface_finish = st.text_input("Surface Finish (Ra µm)")
    hardness = st.text_input("Hardness Requirement (HRC)")
    thread_check = st.checkbox("Thread must pass GO and fail NO-GO")

    st.markdown("---")

    # Goods Received / GRN
    st.subheader("Goods Received / QC (Add/Delete rows)")
    if st.button("➕ Add GRN Entry"):
        st.session_state.grn_entries.append({"Date": "", "Qty Received": 0.0, "OK Qty": 0.0, "Rejected Qty": 0.0, "Remarks": "", "QC Approved By": ""})
    remove_grn = None
    for k, gr in enumerate(st.session_state.grn_entries):
        cols = st.columns([2,1,1,1,2,1])
        gr["Date"] = cols[0].text_input(f"GRN Date #{k+1}", value=gr.get("Date",""), key=f"grn_date_{k}")
        gr["Qty Received"] = cols[1].number_input("Qty Received", value=float(gr.get("Qty Received",0.0)), key=f"grn_qty_{k}")
        gr["OK Qty"] = cols[2].number_input("OK Qty", value=float(gr.get("OK Qty",0.0)), key=f"grn_ok_{k}")
        gr["Rejected Qty"] = cols[3].number_input("Rejected Qty", value=float(gr.get("Rejected Qty",0.0)), key=f"grn_rej_{k}")
        gr["Remarks"] = cols[4].text_input("Remarks", value=gr.get("Remarks",""), key=f"grn_rem_{k}")
        gr["QC Approved By"] = cols[5].text_input("QC Approved By", value=gr.get("QC Approved By",""), key=f"grn_qc_{k}")
        if cols[5].button("🗑️ Delete", key=f"del_grn_{k}"):
            remove_grn = k
    if remove_grn is not None:
        st.session_state.grn_entries.pop(remove_grn)

    st.markdown("---")

# -------------------------
# TAB 2: PREVIEW
# -------------------------
with tab2:
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR}'>Job Card Preview</h2>", unsafe_allow_html=True)
    # Build preview QR
    qr_text = f"JobNo:{job_no}|Date:{job_date}|Dispatch:{dispatch_location}|VendorID:{vendor_id}"
    qr_bytes, qr_img_pil = make_qr_bytes(qr_text)

    item_df = rows_to_df(st.session_state.items, ["Description", "Drawing No", "Drawing Link", "Grade", "Qty", "UOM"])
    mat_df = rows_to_df(st.session_state.materials, ["Raw Material", "Heat No", "Dia/Size", "Weight", "Qty", "Remark"])
    grn_df = rows_to_df(st.session_state.grn_entries, ["Date", "Qty Received", "OK Qty", "Rejected Qty", "Remarks", "QC Approved By"])

    preview_html = f"""
    <div style="padding:18px; border-radius:12px; border:2px solid {PRIMARY_COLOR}; background:#f8fafb;">
      <h2 style="text-align:center; color:{PRIMARY_COLOR}; margin-top:6px;">{company_name}</h2>
      <div style="display:flex; gap:16px;">
        <div style="flex:2;">
          <h4 style="color:{PRIMARY_COLOR};">Vendor Details</h4>
          <b>ID:</b> {vendor_id}<br/>
          <b>Company:</b> {vendor_company}<br/>
          <b>Contact:</b> {vendor_person} | {vendor_mobile}<br/>
          <b>GST:</b> {vendor_gst}<br/>
          <b>Address:</b> {vendor_address}<br/>
        </div>
        <div style="flex:1; text-align:right;">
          <img src="data:image/png;base64,{base64.b64encode(qr_bytes).decode()}" width="120"/>
        </div>
      </div>
      <hr style="border:1px solid #e6eef8; margin:10px 0;"/>
      <div style="display:flex; gap:18px;">
        <div style="flex:1;">
          <b>Job Card No:</b> {job_no}<br/>
          <b>Date:</b> {job_date}<br/>
        </div>
        <div style="flex:1;">
          <b>Dispatch Location:</b> {dispatch_location}<br/>
        </div>
      </div>
      <h4 style="color:{PRIMARY_COLOR}; margin-top:14px;">Items</h4>
      {item_df.to_html(index=False, border=1)}
      <h4 style="color:{PRIMARY_COLOR}; margin-top:12px;">Material Issued</h4>
      {mat_df.to_html(index=False, border=1)}
      <h4 style="color:{PRIMARY_COLOR}; margin-top:12px;">Operations</h4>
      <div>{', '.join([op for op, v in op_selected.items() if v]) or 'None'}</div>
    """

    if show_machine and machine_details:
        preview_html += "<h4 style='color:{}; margin-top:12px;'>Machine Details</h4>".format(PRIMARY_COLOR)
        for k, v in machine_details.items():
            preview_html += f"<b>{k}:</b> {v}<br/>"

    preview_html += f"""
      <h4 style="color:{PRIMARY_COLOR}; margin-top:12px;">Quality Instructions</h4>
      <b>Tolerance:</b> {tolerance}<br/>
      <b>Surface Finish:</b> {surface_finish}<br/>
      <b>Hardness:</b> {hardness}<br/>
      <h4 style="color:{PRIMARY_COLOR}; margin-top:12px;">Goods Received / QC</h4>
      {grn_df.to_html(index=False, border=1)}
      <br/>
      <div style="text-align:center; margin-top:18px;">
        <button onclick="window.print()" style="background:{PRIMARY_COLOR}; color:white; padding:10px 22px; border-radius:8px; border:none;">🖨️ Print Job Card</button>
      </div>
    </div>
    """
    st.markdown(preview_html, unsafe_allow_html=True)

# -------------------------
# TAB 3: PDF EXPORT
# -------------------------
with tab3:
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR}'>PDF Export</h2>", unsafe_allow_html=True)
    st.write("Click to generate a structured PDF.")

    if st.button("🔁 Generate PDF"):
        # prepare tables
        item_df = rows_to_df(st.session_state.items, ["Description", "Drawing No", "Drawing Link", "Grade", "Qty", "UOM"])
        mat_df = rows_to_df(st.session_state.materials, ["Raw Material", "Heat No", "Dia/Size", "Weight", "Qty", "Remark"])
        grn_df = rows_to_df(st.session_state.grn_entries, ["Date", "Qty Received", "OK Qty", "Rejected Qty", "Remarks", "QC Approved By"])

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=25, rightMargin=25, topMargin=25, bottomMargin=25)
        styles = getSampleStyleSheet()
        story = []

        # Header with logo
        header_cells = []
        if logo_file:
            try:
                logo_bytes = logo_file.getvalue()
                header_cells.append([RLImage(BytesIO(logo_bytes), width=60, height=60),
                                     Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles['Title'])])
            except Exception:
                header_cells.append(["", Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles['Title'])])
        else:
            header_cells.append(["", Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles['Title'])])

        header_tbl = Table(header_cells, colWidths=[70, 430])
        header_tbl.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        story.append(header_tbl)
        story.append(Spacer(1, 8))

        # Job table
        job_block = [
            ['Job Card No', job_no],
            ['Date', str(job_date)],
            ['Dispatch Location', dispatch_location]
        ]
        job_tbl = Table(job_block, colWidths=[140, 360])
        job_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d9e1f2')),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.4, colors.grey)
        ]))
        story.append(job_tbl)
        story.append(Spacer(1, 10))

        # Vendor table
        vendor_block = [
            ['Vendor ID', vendor_id],
            ['Vendor Company', vendor_company],
            ['Contact Person', vendor_person],
            ['Mobile', vendor_mobile],
            ['GST', vendor_gst],
            ['Address', vendor_address]
        ]
        vendor_tbl = Table(vendor_block, colWidths=[140, 360])
        vendor_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fce4d6')),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.4, colors.grey)
        ]))
        story.append(vendor_tbl)
        story.append(Spacer(1, 12))

        # Items table
        story.append(Paragraph("Item Details", styles['Heading2']))
        if item_df.empty:
            story.append(Paragraph("No items added.", styles['Normal']))
        else:
            data = [item_df.columns.tolist()] + item_df.fillna('').values.tolist()
            tbl = Table(data, colWidths=[120,80,80,60,40,40])
            tbl.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dbe5f1'))
            ]))
            story.append(tbl)
        story.append(Spacer(1, 10))

        # Material table
        story.append(Paragraph("Material Issued", styles['Heading2']))
        if mat_df.empty:
            story.append(Paragraph("No materials added.", styles['Normal']))
        else:
            data = [mat_df.columns.tolist()] + mat_df.fillna('').values.tolist()
            tbl = Table(data, colWidths=[100,60,50,50,40,60])
            tbl.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f2f2f2'))
            ]))
            story.append(tbl)
        story.append(Spacer(1, 10))

        # Operations
        story.append(Paragraph("Operations Selected", styles['Heading2']))
        ops_text = ', '.join([op for op, v in op_selected.items() if v]) or "None"
        story.append(Paragraph(ops_text, styles['Normal']))
        story.append(Spacer(1, 8))

        # Machine Details
        if show_machine and machine_details:
            story.append(Paragraph("Machine Details", styles['Heading2']))
            for k,v in machine_details.items():
                story.append(Paragraph(f"{k}: {v}", styles['Normal']))
            story.append(Spacer(1, 8))

        # Quality
        story.append(Paragraph("Quality Instructions", styles['Heading2']))
        story.append(Paragraph(f"Tolerance: {tolerance}", styles['Normal']))
        story.append(Paragraph(f"Surface Finish: {surface_finish}", styles['Normal']))
        story.append(Paragraph(f"Hardness: {hardness}", styles['Normal']))
        if thread_check:
            story.append(Paragraph(f"Thread: GO/NO-GO Check Required", styles['Normal']))
        story.append(Spacer(1, 8))

        # GRN
        story.append(Paragraph("Goods Received / QC", styles['Heading2']))
        if grn_df.empty:
            story.append(Paragraph("No entries added.", styles['Normal']))
        else:
            data = [grn_df.columns.tolist()] + grn_df.fillna('').values.tolist()
            tbl = Table(data, colWidths=[70,50,50,50,80,80])
            tbl.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f8ff'))
            ]))
            story.append(tbl)
        story.append(Spacer(1, 12))

        doc.build(story)
        buf.seek(0)
        st.download_button("⬇️ Download PDF", buf, "vendor_job_card.pdf", mime="application/pdf")

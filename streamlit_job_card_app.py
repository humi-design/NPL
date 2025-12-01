import base64
import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
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
    st.subheader("Company Header")
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
        st.session_state['items'].append([desc, drawing_no, drawing_link, grade, qty, uom])
    if st.session_state['items']:
        st.dataframe(rows_to_df(st.session_state['items'], ["Description","Drawing No","Drawing Link","Grade","Qty","UOM"]), use_container_width=True)
        if st.button("Clear Items"): st.session_state['items'] = []

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
        st.session_state['materials'].append([rm, heat, dia, weight, mqty, remark])
    if st.session_state['materials']:
        st.dataframe(rows_to_df(st.session_state['materials'], ["Raw Material","Heat No","Dia/Size","Weight","Qty","Remark"]), use_container_width=True)
        if st.button("Clear Materials"): st.session_state['materials'] = []

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
        st.session_state['grn_entries'].append(grn_vals)
    if st.session_state['grn_entries']:
        st.dataframe(rows_to_df(st.session_state['grn_entries'], grn_cols), use_container_width=True)
        if st.button("Clear GRN Entries"): st.session_state['grn_entries'] = []

# -----------------------------
# TAB 2: Preview
# -----------------------------
# -----------------------------------------------------
# TAB 2: Preview  (HTML-based, PDF friendly)
# -----------------------------------------------------
with tab2:

    st.markdown(f"<h1 style='color:{PRIMARY_COLOR}'>Preview Job Card</h1>", unsafe_allow_html=True)

    # Build HTML string for preview + PDF export
    html = f"""
    <div style='font-family:Arial; padding:20px; border:2px solid #ccc; border-radius:10px; background:#f8f9fb;'>

        <!-- HEADER -->
        <div style='display:flex; align-items:center; gap:20px;'>
            <div style='width:100px;'>
                {"<img src='data:image/png;base64," + base64.b64encode(logo_file.read()).decode() + "' style='width:100px;'/>" if logo_file else ""}
            </div>
            <div style='font-size:18px; font-weight:bold;'>
                {company_name}<br>
                <span style='font-size:14px; font-weight:normal;'>{company_address}</span>
            </div>
        </div>

        <hr>

        <!-- VENDOR DETAILS -->
        <h2 style='color:{PRIMARY_COLOR}; margin-bottom:5px;'>Vendor Details</h2>
        <table style='width:100%; border-collapse: collapse;'>
            <tr><td><b>Vendor ID</b></td><td>{vendor_id}</td></tr>
            <tr><td><b>Company</b></td><td>{vendor_company}</td></tr>
            <tr><td><b>Contact Person</b></td><td>{vendor_person}</td></tr>
            <tr><td><b>Mobile</b></td><td>{vendor_mobile}</td></tr>
            <tr><td><b>GST</b></td><td>{vendor_gst}</td></tr>
            <tr><td><b>Address</b></td><td>{vendor_address}</td></tr>
        </table>

        <hr>

        <!-- JOB DETAILS -->
        <h2 style='color:{PRIMARY_COLOR}; margin-bottom:5px;'>Job Details</h2>
        <table style='width:100%; border-collapse: collapse;'>
            <tr><td><b>Job No</b></td><td>{job_no}</td></tr>
            <tr><td><b>Date</b></td><td>{job_date}</td></tr>
            <tr><td><b>Dispatch Location</b></td><td>{dispatch_location}</td></tr>
        </table>

        <br>
       # Convert QR bytes to base64 for HTML preview + PDF export
qr_b64 = base64.b64encode(qr_bytes).decode("utf-8")

# Add to preview HTML string
html = ""
html += "<h3>QR Code</h3>"
html += f"<img src='data:image/png;base64,{qr_b64}' width='150'>"

        <hr>

        <!-- ITEM DETAILS -->
        <h2 style='color:{PRIMARY_COLOR}; margin-bottom:5px;'>Item Details</h2>
        <table style='width:100%; border:1px solid #000; border-collapse:collapse;'>
            <tr style='background:#d9e3f0;'>
                <th>Description</th><th>Drawing No</th><th>Drawing Link</th>
                <th>Grade</th><th>Qty</th><th>UOM</th>
            </tr>
            {
                "".join([
                    f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>"
                    for r in st.session_state['items']
                ])
            }
        </table>

        <hr>

        <!-- MATERIAL ISSUED -->
        <h2 style='color:{PRIMARY_COLOR}; margin-bottom:5px;'>Material Issued</h2>
        <table style='width:100%; border:1px solid #000; border-collapse:collapse;'>
            <tr style='background:#d9e3f0;'>
                <th>Raw Material</th><th>Heat No</th><th>Dia/Size</th>
                <th>Weight</th><th>Qty</th><th>Remark</th>
            </tr>
            {
                "".join([
                    f"<tr><td>{m[0]}</td><td>{m[1]}</td><td>{m[2]}</td><td>{m[3]}</td><td>{m[4]}</td><td>{m[5]}</td></tr>"
                    for m in st.session_state['materials']
                ])
            }
        </table>

        <hr>

        <!-- OPERATIONS -->
        <h2 style='color:{PRIMARY_COLOR}; margin-bottom:5px;'>Operations</h2>
        <p>{", ".join([op for op, sel in op_selected.items() if sel]) or "None"}</p>

        {"<h2 style='color:"+PRIMARY_COLOR+";'>Machine Details</h2>" if show_machine else ""}
        {
            "".join([f"<p><b>{k}:</b> {v}</p>" for k,v in machine_details.items()]) 
            if show_machine else ""
        }

        <hr>

        <!-- QUALITY -->
        <h2 style='color:{PRIMARY_COLOR}; margin-bottom:5px;'>Quality Instructions</h2>
        <p><b>Tolerance:</b> {tolerance}</p>
        <p><b>Surface Finish:</b> {surface_finish}</p>
        <p><b>Hardness:</b> {hardness}</p>
        {"<p><b>Thread:</b> GO/NO-GO Required</p>" if thread_check else ""}

        <hr>

        <!-- GOODS RECEIVED -->
        <h2 style='color:{PRIMARY_COLOR}; margin-bottom:5px;'>Goods Received / QC</h2>
        <table style='width:100%; border:1px solid #000; border-collapse:collapse;'>
            <tr style='background:#d9e3f0;'>
                <th>Date</th><th>Qty Received</th><th>OK Qty</th>
                <th>Rejected Qty</th><th>Remarks</th><th>QC Approved By</th>
            </tr>
            {
                "".join([
                    f"<tr><td>{g[0]}</td><td>{g[1]}</td><td>{g[2]}</td><td>{g[3]}</td><td>{g[4]}</td><td>{g[5]}</td></tr>"
                    for g in st.session_state['grn_entries']
                ])
            }
        </table>

    </div>
    """

    # Display Preview
    st.markdown(html, unsafe_allow_html=True)

    # Save HTML for PDF generation in tab3
    st.session_state["preview_html"] = html

# -----------------------------
# TAB 3: PDF Export (HTML-to-PDF)
# -----------------------------
# -----------------------------------------------------
# TAB 3: PDF EXPORT (WeasyPrint)
# -----------------------------------------------------
with tab3:
    st.markdown(f"<h1 style='color:{PRIMARY_COLOR}'>Download PDF</h1>", unsafe_allow_html=True)

    if "preview_html" not in st.session_state:
        st.warning("Please fill the form and open the Preview tab first.")
    else:
        html = st.session_state["preview_html"]

        # Add global print styles for PDF
        styled_html = f"""
        <html>
        <head>
        <style>
            @page {{
                size: A4;
                margin: 20mm;
            }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 13px;
            }}
            table, th, td {{
                border: 1px solid #000;
                border-collapse: collapse;
                padding: 6px;
            }}
            th {{
                background: #d9e3f0;
            }}
        </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """

        if st.button("Generate PDF"):
            from weasyprint import HTML
            pdf_bytes = HTML(string=styled_html).write_pdf()

            st.success("PDF generated successfully!")

            st.download_button(
                label="⬇️ Download Job Card PDF",
                data=pdf_bytes,
                file_name=f"JobCard_{job_no}.pdf",
                mime="application/pdf"
            )

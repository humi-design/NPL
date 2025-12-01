import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
import io
from datetime import datetime

st.set_page_config(page_title="Dynamic Vendor Job Card", layout="wide")

# --- Helper functions -----------------------------------------------------

def generate_qr(data_str: str, size: int = 300) -> Image.Image:
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size))
    return img


def df_to_excel_bytes(dfs: dict) -> bytes:
    # dfs: {sheet_name: dataframe}
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=str(name)[:31], index=False)
    return output.getvalue()


# Simple PDF generator fallback using reportlab (optional)
def make_pdf_bytes(summary_text: str, qr_img: Image.Image = None) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
    except Exception as e:
        st.warning("reportlab not installed. Install 'reportlab' to enable PDF export.")
        return None

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 40

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, height - margin, "Vendor Job Card")

    c.setFont("Helvetica", 9)
    textobject = c.beginText(margin, height - margin - 30)
    for line in summary_text.splitlines():
        textobject.textLine(line)
    c.drawText(textobject)

    if qr_img is not None:
        qr_buf = io.BytesIO()
        qr_img.save(qr_buf, format="PNG")
        qr_buf.seek(0)
        img_reader = ImageReader(qr_buf)
        c.drawImage(img_reader, width - 150, height - 200, width=120, height=120)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# --- UI ------------------------------------------------------------------
st.title("🔧 Dynamic Vendor Job Card — Streamlit")
st.caption("Fill fields below. Use checkboxes to enable machine sections and QR / drawing links.")

# Header and Job details
with st.expander("Company Header & Job Info", expanded=True):
    cols = st.columns([3, 2, 1])
    with cols[0]:
        company_name = st.text_input("Company Name", "Your Company Pvt Ltd")
        address = st.text_area("Address", "Street, City, State\nPin: ")
        contact = st.text_input("Contact / Email / GST", "")
    with cols[1]:
        job_card_no = st.text_input("Job Card No.", f"JC-{datetime.now().strftime('%Y%m%d-%H%M')}")
        date = st.date_input("Date", datetime.now())
        vendor_name = st.text_input("Vendor Name", "")
    with cols[2]:
        qr_for = st.selectbox("QR content type", ["Job Info", "Drawing Link", "ERP Link", "Custom Text"])
        drawing_link = st.text_input("Drawing Link (URL)")
        custom_qr_text = st.text_input("Custom QR text (used if QR type=Custom Text)")

# ITEM DETAILS - editable table
st.subheader("Item Details")
if "item_df" not in st.session_state:
    st.session_state.item_df = pd.DataFrame(
        columns=["Sr", "Item Description", "Material", "Grade", "Qty", "Unit", "Drawing No.", "Drawing Link", "Revision", "Heat No."]
    )

with st.expander("Edit Item Details (Data Editor)", expanded=True):
    st.session_state.item_df = st.data_editor(st.session_state.item_df, num_rows="dynamic")

# OPERATIONS with checkboxes and details
st.subheader("Operations")
ops = [
    "Cutting", "Turning - Traub", "Turning - CNC", "Milling", "Drilling",
    "Punching", "Boring", "Grinding", "Knurling", "Grooving",
    "Parting", "Deburring", "Threading", "Heat Treatment", "Plating", "Inspection", "Packing"
]

selected_ops = {}
cols_ops = st.columns(4)
for i, op in enumerate(ops):
    with cols_ops[i % 4]:
        checked = st.checkbox(op)
        if checked:
            # show small param inputs inline
            with st.expander(f"{op} - Operation Details", expanded=False):
                param1 = st.text_input(f"{op} — Machine Type / Tooling", key=f"tool_{op}")
                param2 = st.text_input(f"{op} — Parameters (RPM/Feed/Depth)", key=f"param_{op}")
            selected_ops[op] = {"machine": param1, "params": param2}

# MACHINE-SPECIFIC OPTIONAL DETAILS
st.subheader("Machine-specific Details (Optional)")
show_machine = st.checkbox("Show Machine Details Section")
machine_details = {}
if show_machine:
    machine_type = st.selectbox("Select Machine to configure", ["Traub", "CNC Lathe", "VMC / Milling", "Drilling", "Grinding", "Press / Punching", "Heat Treatment", "Plating"], index=0)
    st.markdown("---")
    if machine_type == "Traub":
        c1, c2, c3 = st.columns(3)
        with c1:
            traub_model = st.text_input("Traub Model", "A25/A32/A42")
            bar_dia = st.text_input("Bar Diameter")
            collet_size = st.text_input("Collet Size")
        with c2:
            main_gear = st.text_input("Main Gear No.")
            feed_gear = st.text_input("Feed Gear No.")
            slotting_gear = st.text_input("Slotting Gear")
        with c3:
            rpm = st.text_input("RPM")
            feed = st.text_input("Feed")
            doc = st.text_input("Depth of Cut (DOC)")
        tool_layout = st.text_area("Tool Layout (one per line)")
        cycle_time = st.text_input("Expected Cycle Time (sec/pc)")
        machine_details = dict(model=traub_model, bar_dia=bar_dia, collet=collet_size, gears=dict(main=main_gear, feed=feed_gear, slot=slotting_gear), rpm=rpm, feed=feed, doc=doc, tools=tool_layout, cycle_time=cycle_time)
    elif machine_type == "CNC Lathe":
        cn1, cn2 = st.columns(2)
        with cn1:
            program_no = st.text_input("Program No.")
            controller = st.text_input("Controller (Fanuc/Siemens)")
            spindle_speed = st.text_input("Spindle Speed (RPM)")
        with cn2:
            feed_mm = st.text_input("Feed (mm/rev or mm/min)")
            tool_offsets = st.text_input("Tool Offsets (e.g. G54)")
            coolant = st.selectbox("Coolant", ["Yes", "No"], index=0)
        machine_details = dict(program=program_no, controller=controller, rpm=spindle_speed, feed=feed_mm, offsets=tool_offsets, coolant=coolant)
    elif machine_type == "VMC / Milling":
        mv1, mv2 = st.columns(2)
        with mv1:
            program_no = st.text_input("Program No.")
            cutter = st.text_input("Cutter Type / Dia")
            rpm = st.text_input("RPM")
        with mv2:
            feed_rate = st.text_input("Feed Rate (mm/min)")
            step_over = st.text_input("Step Over")
            fixture = st.text_input("Fixture Used")
        machine_details = dict(program=program_no, cutter=cutter, rpm=rpm, feed_rate=feed_rate, step_over=step_over, fixture=fixture)
    elif machine_type == "Drilling":
        d1, d2 = st.columns(2)
        with d1:
            drill_size = st.text_input("Drill Size (mm)")
            depth = st.text_input("Depth (mm)")
        with d2:
            rpm = st.text_input("RPM")
            coolant = st.selectbox("Coolant", ["Yes", "No"], index=0)
        machine_details = dict(drill_size=drill_size, depth=depth, rpm=rpm, coolant=coolant)
    elif machine_type == "Grinding":
        g1, g2 = st.columns(2)
        with g1:
            wheel = st.text_input("Wheel Type / No.")
            grit = st.text_input("Grit")
        with g2:
            speed = st.text_input("Wheel Speed")
            dressing = st.text_input("Dressing Frequency")
        machine_details = dict(wheel=wheel, grit=grit, speed=speed, dressing=dressing)
    elif machine_type == "Press / Punching":
        p1, p2 = st.columns(2)
        with p1:
            capacity = st.text_input("Press Capacity (T)")
            stroke = st.text_input("Stroke Length")
        with p2:
            die_no = st.text_input("Die No.")
            punch_no = st.text_input("Punch No.")
        machine_details = dict(capacity=capacity, stroke=stroke, die_no=die_no, punch_no=punch_no)
    elif machine_type == "Heat Treatment":
        ht1, ht2 = st.columns(2)
        with ht1:
            furnace = st.text_input("Furnace Type")
            temp = st.text_input("Temperature (°C)")
        with ht2:
            hold = st.text_input("Hold Time")
            quench = st.text_input("Quenching Medium")
        machine_details = dict(furnace=furnace, temp=temp, hold=hold, quench=quench)

# QUALITY REQUIREMENTS
st.subheader("Quality Requirements")
col_q1, col_q2 = st.columns(2)
with col_q1:
    tolerances = st.text_input("Tolerances (as per drawing)")
    surface_finish = st.text_input("Surface finish (Ra µm)")
    hardness = st.text_input("Hardness (HRC)")
with col_q2:
    plating = st.text_input("Plating / Surface finish spec")
    salt_spray = st.text_input("Salt spray hrs")
    special_instructions = st.text_area("Special Instructions / Notes")

# PACKING
st.subheader("Packing Instructions")
pack_inner = st.text_input("Inner Packing")
pack_outer = st.text_input("Outer Packing")
qty_per_packet = st.text_input("Qty per packet")
rust_prev = st.radio("Rust preventive/VP required?", ["Yes", "No"], index=1)
labeling = st.multiselect("Labeling options", ["Sticker", "Barcode", "QR Code"], default=["Sticker"]) 

# DELIVERY
st.subheader("Delivery & Dispatch")
due_date = st.date_input("Expected Date / Delivery Date")
dispatch_loc = st.text_input("Dispatch Location")
transport_mode = st.selectbox("Transport Mode", ["Truck", "Courier", "Self", "Other"]) 

# QC / Goods Received
st.subheader("Goods Received / QC Entry")
if "qc_df" not in st.session_state:
    st.session_state.qc_df = pd.DataFrame(columns=["Date", "Qty Received", "OK Qty", "Rejected Qty", "Defect Code", "Defect Description", "Lot No.", "QC Approved By"]) 
with st.expander("QC Log / Goods Received (editable)", expanded=False):
    st.session_state.qc_df = st.data_editor(st.session_state.qc_df, num_rows="dynamic")

# SUMMARY & QR generation
st.subheader("Preview & Export")
colp1, colp2 = st.columns([2,1])
with colp1:
    st.markdown("### Job Card Preview")
    st.markdown(f"**Company:** {company_name}  ")
    st.markdown(f"**Vendor:** {vendor_name} | **Job Card No.:** {job_card_no}  ")
    st.markdown(f"**Date:** {date}  ")
    st.markdown("---")
    st.markdown("**Items:**")
    st.dataframe(st.session_state.item_df)
    st.markdown("**Selected Operations & Parameters:**")
    if selected_ops:
        for op, details in selected_ops.items():
            st.write(f"- **{op}** — Machine/Tool: {details['machine']} | Params: {details['params']}")
    else:
        st.write("No operations selected.")
    if show_machine:
        st.markdown("---")
        st.markdown(f"**Machine ({machine_type}) details:**")
        st.json(machine_details)
    st.markdown("---")
    st.markdown("**Quality Requirements**")
    st.write(f"Tolerances: {tolerances} | Surface finish: {surface_finish} | Hardness: {hardness}")
    st.write(f"Plating: {plating} | Salt Spray: {salt_spray}")

with colp2:
    # QR generation
    if qr_for == "Job Info":
        qr_text = f"JC:{job_card_no}|Vendor:{vendor_name}|Date:{date}|Items:{len(st.session_state.item_df)}"
    elif qr_for == "Drawing Link":
        qr_text = drawing_link or ""
    elif qr_for == "ERP Link":
        qr_text = f"ERP://job/{job_card_no}"
    else:
        qr_text = custom_qr_text

    qr_img = generate_qr(qr_text)
    st.image(qr_img, caption="QR Code", use_column_width=False)
    st.download_button("Download QR (PNG)", data=io.BytesIO(qr_img.tobytes()), file_name=f"qr_{job_card_no}.png")

# Prepare export data
export_dfs = {
    "Job_Details": pd.DataFrame([{"Company": company_name, "Vendor": vendor_name, "Job Card No": job_card_no, "Date": str(date)}]),
    "Items": st.session_state.item_df,
    "QC_Log": st.session_state.qc_df
}

# Add operations and machine details as small tables
ops_rows = []
for op, d in selected_ops.items():
    ops_rows.append({"Operation": op, "Machine/Tool": d['machine'], "Params": d['params']})
export_dfs['Operations'] = pd.DataFrame(ops_rows)
if show_machine:
    export_dfs['Machine_Details'] = pd.DataFrame([machine_details])

# Excel export
excel_bytes = df_to_excel_bytes(export_dfs)
st.download_button("Download Job Card as Excel (.xlsx)", data=excel_bytes, file_name=f"jobcard_{job_card_no}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# PDF export (simple summary)
summary_lines = []
summary_lines.append(f"Company: {company_name}")
summary_lines.append(f"Vendor: {vendor_name}")
summary_lines.append(f"Job Card: {job_card_no}    Date: {date}")
summary_lines.append("")
summary_lines.append("Items:")
for _, row in st.session_state.item_df.iterrows():
    summary_lines.append(f" - {row.get('Item Description','')} | QTY: {row.get('Qty','')}")
summary_text = "\n".join(summary_lines)

pdf_bytes = make_pdf_bytes(summary_text, qr_img=qr_img)
if pdf_bytes:
    st.download_button("Download Summary PDF", data=pdf_bytes, file_name=f"jobcard_{job_card_no}.pdf", mime="application/pdf")

st.success("Job card ready. Use the downloads to save or share. You can edit fields and re-download.")

# Footer / tips
st.markdown("---")
st.caption("Tip: For Excel formulas, open the downloaded file and add formulas in your master template. You can also extend this app to save jobs to a DB or ERP.")

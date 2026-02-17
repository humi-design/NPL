import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import date as dt_date

from erp_database import initialize_database, load_sheet, save_sheet

initialize_database()

st.set_page_config(page_title="Vendor Job Card ERP", layout="wide")

# -----------------------------
# SESSION STATE
# -----------------------------
if "items" not in st.session_state:
    st.session_state.items = []

if "materials" not in st.session_state:
    st.session_state.materials = []

if "grn" not in st.session_state:
    st.session_state.grn = []

# -----------------------------
# QR FUNCTION
# -----------------------------
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["Input", "Preview"])

# =========================================================
# TAB 1 — INPUT
# =========================================================
with tab1:

    st.title("Vendor Job Card")

    # -------- Vendor Dropdown --------
    vendors_df = load_sheet("Vendors")
    vendor_list = ["New Vendor"] + vendors_df["VendorID"].dropna().tolist()

    selected_vendor = st.selectbox("Select Vendor", vendor_list)

    if selected_vendor != "New Vendor":
        v = vendors_df[vendors_df["VendorID"] == selected_vendor].iloc[0]
        vendor_id = v["VendorID"]
        vendor_company = v["Company"]
        vendor_person = v["Person"]
        vendor_mobile = v["Mobile"]
        vendor_gst = v["GST"]
        vendor_address = v["Address"]

        st.success("Existing vendor loaded")

    else:
        vendor_id = st.text_input("Vendor ID")
        vendor_company = st.text_input("Company Name")
        vendor_person = st.text_input("Contact Person")
        vendor_mobile = st.text_input("Mobile")
        vendor_gst = st.text_input("GST")
        vendor_address = st.text_area("Address")

        if st.button("Save Vendor"):
            new_vendor = pd.DataFrame([{
                "VendorID": vendor_id,
                "Company": vendor_company,
                "Person": vendor_person,
                "Mobile": vendor_mobile,
                "GST": vendor_gst,
                "Address": vendor_address
            }])

            vendors_df = pd.concat([vendors_df, new_vendor], ignore_index=True)
            save_sheet("Vendors", vendors_df)
            st.success("Vendor saved")

    st.divider()

    # -------- Job Details --------
    job_no = st.text_input(
        "Job Card No",
        value=f"JC-{dt_date.today().strftime('%Y%m%d')}"
    )

    job_date = st.date_input("Date", dt_date.today())
    dispatch = st.text_input("Dispatch Location")

    qr_bytes = make_qr(f"{job_no}-{vendor_id}")

    st.image(qr_bytes, width=120)

    # -------- Items --------
    st.subheader("Items")

    desc = st.text_input("Description")
    drawing = st.text_input("Drawing No")
    grade = st.text_input("Grade")
    qty = st.number_input("Qty", min_value=0)
    uom = st.text_input("UOM", "Nos")

    if st.button("Add Item"):
        st.session_state.items.append([desc, drawing, grade, qty, uom])

    if st.session_state.items:
        st.dataframe(
            pd.DataFrame(
                st.session_state.items,
                columns=["Description","Drawing","Grade","Qty","UOM"]
            )
        )

    # -------- Materials --------
    st.subheader("Material Issued")

    mat = st.text_input("Material")
    heat = st.text_input("Heat No")
    size = st.text_input("Size")
    weight = st.number_input("Weight", min_value=0)
    mqty = st.number_input("Material Qty", min_value=0)
    remark = st.text_input("Remark")

    if st.button("Add Material"):
        st.session_state.materials.append(
            [mat, heat, size, weight, mqty, remark]
        )

    # -------- GRN --------
    st.subheader("Goods Received")

    g_date = st.text_input("Date")
    rec = st.number_input("Received", min_value=0)
    ok = st.number_input("OK Qty", min_value=0)
    rej = st.number_input("Rejected Qty", min_value=0)
    rmk = st.text_input("Remarks")
    qc = st.text_input("QC By")

    if st.button("Add GRN"):
        st.session_state.grn.append(
            [g_date, rec, ok, rej, rmk, qc]
        )

    st.divider()

    # -------- SAVE JOB CARD --------
    if st.button("SAVE JOB CARD TO ERP"):

        # Job Card
        job_df = load_sheet("JobCards")
        job_df.loc[len(job_df)] = [
            job_no, job_date, vendor_id, dispatch
        ]
        save_sheet("JobCards", job_df)

        # Items
        items_df = load_sheet("Items")
        for r in st.session_state.items:
            items_df.loc[len(items_df)] = [job_no] + r
        save_sheet("Items", items_df)

        # Materials
        mat_df = load_sheet("Materials")
        for r in st.session_state.materials:
            mat_df.loc[len(mat_df)] = [job_no] + r
        save_sheet("Materials", mat_df)

        # GRN
        grn_df = load_sheet("GRN")
        for r in st.session_state.grn:
            grn_df.loc[len(grn_df)] = [job_no] + r
        save_sheet("GRN", grn_df)

        st.success("Job Card saved successfully!")

# =========================================================
# TAB 2 — PREVIEW
# =========================================================
with tab2:

    st.title("Preview Job Card")

    st.write("Job No:", job_no)
    st.write("Vendor:", vendor_company)
    st.write("Dispatch:", dispatch)

    st.image(qr_bytes, width=150)

    st.subheader("Items")
    st.dataframe(
        pd.DataFrame(
            st.session_state.items,
            columns=["Description","Drawing","Grade","Qty","UOM"]
        )
    )

    st.subheader("Materials")
    st.dataframe(
        pd.DataFrame(
            st.session_state.materials,
            columns=["Material","Heat","Size","Weight","Qty","Remark"]
        )
    )

    st.subheader("GRN")
    st.dataframe(
        pd.DataFrame(
            st.session_state.grn,
            columns=["Date","Received","OK","Rejected","Remarks","QC"]
        )
    )

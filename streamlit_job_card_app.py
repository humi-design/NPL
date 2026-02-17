import streamlit as st
import psycopg2
import base64
from io import BytesIO
from datetime import date
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Factory Job Card System",
                   page_icon="🏭",
                   layout="wide")

DB_URL = "postgresql://postgres:Ralpana09876@db.ibfqpjpvyxnvditlaayg.supabase.co:5432/postgres?sslmode=require"

# -----------------------------
# DB CONNECTION
# -----------------------------
@st.cache_resource
def get_conn():
    return psycopg2.connect(DB_URL)

conn = get_conn()
cur = conn.cursor()

# -----------------------------
# PREMIUM CSS
# -----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}
.stButton>button {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color: white;
    border-radius: 8px;
    font-weight: bold;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.title("🏭 Factory Vendor Job Card System")

# -----------------------------
# COMPANY PROFILE
# -----------------------------
st.header("🏢 Company Profile")

cur.execute("SELECT * FROM company_profile LIMIT 1")
company = cur.fetchone()

if not company:
    name = st.text_input("Company Name")
    address = st.text_area("Address")
    logo = st.file_uploader("Upload Logo")

    if st.button("Save Company Profile"):
        logo_bytes = logo.read() if logo else None
        cur.execute(
            "INSERT INTO company_profile (company_name,address,logo) VALUES (%s,%s,%s)",
            (name, address, logo_bytes)
        )
        conn.commit()
        st.success("Saved! Reload page.")
else:
    st.success("Company Profile Loaded")

    col1, col2 = st.columns([1,4])

    with col1:
        if company[3]:
            st.image(company[3], width=120)

    with col2:
        st.subheader(company[1])
        st.write(company[2])

# -----------------------------
# VENDOR MASTER
# -----------------------------
st.header("👥 Vendor Master")

cur.execute("SELECT vendor_id, company_name FROM vendors ORDER BY company_name")
vendors = cur.fetchall()

vendor_options = ["Add New"] + [f"{v[1]} ({v[0]})" for v in vendors]

choice = st.selectbox("Select Vendor", vendor_options)

if choice == "Add New":
    vid = st.text_input("Vendor ID")
    cname = st.text_input("Company Name")
    person = st.text_input("Contact Person")
    mobile = st.text_input("Mobile")
    gst = st.text_input("GST")
    addr = st.text_area("Address")

    if st.button("Save Vendor"):
        cur.execute(
            "INSERT INTO vendors VALUES (%s,%s,%s,%s,%s,%s,NOW())",
            (vid, cname, person, mobile, gst, addr)
        )
        conn.commit()
        st.success("Vendor Saved")
else:
    vid = choice.split("(")[-1].replace(")", "")
    st.info(f"Selected Vendor ID: {vid}")

# -----------------------------
# JOB CARD
# -----------------------------
st.header("📋 Create Job Card")

job_no = st.text_input("Job No", f"JC-{date.today().strftime('%Y%m%d')}")
job_date = st.date_input("Date", date.today())
dispatch = st.text_input("Dispatch Location")
tolerance = st.text_input("Tolerance")
finish = st.text_input("Surface Finish")
hardness = st.text_input("Hardness")
thread = st.checkbox("Thread GO/NO-GO")
delivery = st.date_input("Expected Delivery")

if st.button("💾 Save Job Card"):
    cur.execute(
        "INSERT INTO job_cards VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'OPEN',NOW())",
        (job_no, vid, job_date, dispatch,
         tolerance, finish, hardness,
         thread, delivery)
    )
    conn.commit()
    st.success("Job Card Saved")

# -----------------------------
# AMAZING PDF GENERATOR
# -----------------------------
def create_pdf(job_no):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []

    title_style = ParagraphStyle(
        "title",
        fontSize=20,
        alignment=1,
        textColor=colors.HexColor("#003366")
    )

    story.append(Paragraph("JOB CARD", title_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>Job No:</b> {job_no}", getSampleStyleSheet()["Normal"]))
    story.append(Paragraph(f"<b>Date:</b> {job_date}", getSampleStyleSheet()["Normal"]))
    story.append(Paragraph(f"<b>Vendor ID:</b> {vid}", getSampleStyleSheet()["Normal"]))
    story.append(Paragraph(f"<b>Dispatch:</b> {dispatch}", getSampleStyleSheet()["Normal"]))

    doc.build(story)
    return buffer.getvalue()

if st.button("📄 Generate Premium PDF"):
    pdf = create_pdf(job_no)

    st.download_button(
        "⬇ Download Job Card",
        pdf,
        file_name=f"{job_no}.pdf",
        mime="application/pdf"
    )

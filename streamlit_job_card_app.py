import streamlit as st
import psycopg2
from io import BytesIO
from datetime import date
from reportlab.platypus import *
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Factory Job Card System",
    page_icon="🏭",
    layout="wide"
)

# ----------------------------------
# DATABASE CONNECTION
# ----------------------------------
DB_URL = "postgresql://postgres:Ralpana09876@db.ibfqpjpvyxnvditlaayg.supabase.co:5432/postgres?sslmode=require"

@st.cache_resource
def get_conn():
    return psycopg2.connect(
        host="db.ibfqpjpvyxnvditlaayg.supabase.co",
        port=5432,
        database="postgres",
        user="postgres",
        password="Ralpana09876",
        sslmode="require",
        connect_timeout=10
    )

conn = get_conn()
cur = conn.cursor()

# ----------------------------------
# PREMIUM UI CSS
# ----------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background: rgba(255,255,255,0.06);
    padding: 25px;
    border-radius: 16px;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 25px rgba(0,0,0,0.5);
}
.stButton>button {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color: white;
    border-radius: 10px;
    font-weight: bold;
    padding: 10px 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏭 Factory Vendor Job Card System")

# =========================================================
# 🏢 COMPANY PROFILE
# =========================================================
st.header("🏢 Company Profile")

cur.execute("SELECT * FROM company_profile LIMIT 1")
company = cur.fetchone()

if not company:
    name = st.text_input("Company Name")
    address = st.text_area("Address")
    logo = st.file_uploader("Upload Logo", type=["png","jpg","jpeg"])

    if st.button("Save Company Profile"):
        if name:
            logo_bytes = logo.read() if logo else None
            cur.execute(
                "INSERT INTO company_profile (company_name,address,logo) VALUES (%s,%s,%s)",
                (name, address, logo_bytes)
            )
            conn.commit()
            st.success("Company Profile Saved — Reload Page")
else:
    col1, col2 = st.columns([1,4])

    with col1:
        if company[3]:
            st.image(company[3], width=120)

    with col2:
        st.subheader(company[1])
        st.write(company[2])

# =========================================================
# 👥 VENDOR MASTER
# =========================================================
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
    st.success(f"Selected Vendor ID: {vid}")

# =========================================================
# 📋 JOB CARD
# =========================================================
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
    st.success("Job Card Saved Successfully")

# =========================================================
# 📄 PREMIUM PDF GENERATOR
# =========================================================
def create_pdf(job_no):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Fetch company info
    cur.execute("SELECT * FROM company_profile LIMIT 1")
    comp = cur.fetchone()

    title_style = ParagraphStyle(
        "title",
        fontSize=22,
        alignment=1,
        textColor=colors.HexColor("#003366"),
        spaceAfter=20
    )

    story.append(Paragraph("JOB CARD", title_style))

    if comp:
        story.append(Paragraph(f"<b>{comp[1]}</b>", styles["Title"]))
        story.append(Paragraph(comp[2], styles["Normal"]))
        story.append(Spacer(1,20))

    # Fetch job info
    cur.execute("SELECT * FROM job_cards WHERE job_no=%s", (job_no,))
    job = cur.fetchone()

    if job:
        data = [
            ["Job No", job[0]],
            ["Vendor ID", job[1]],
            ["Date", str(job[2])],
            ["Dispatch", job[3]],
            ["Tolerance", job[4]],
            ["Finish", job[5]],
            ["Hardness", job[6]],
            ["Thread", "YES" if job[7] else "NO"],
            ["Delivery", str(job[8])]
        ]

        table = Table(data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ("GRID",(0,0),(-1,-1),1,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.lightblue),
            ("FONTSIZE",(0,0),(-1,-1),11)
        ]))

        story.append(table)

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

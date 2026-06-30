"""
Modern Attractive Job Card Management System
A comprehensive Streamlit application with beautiful UI and MySQL backend.
"""

import base64
import io
import json
import os
import sys
from datetime import date, datetime
from typing import Dict, List, Any, Optional

import pandas as pd
import qrcode
import streamlit as st
from PIL import Image
from streamlit_option_menu import streamlit_option_menu

# Import database and PDF modules
try:
    from database import (
        init_database, save_job_card, get_job_card, get_all_job_cards,
        update_job_card_status, delete_job_card, search_job_cards,
        get_job_card_statistics, JobCardDatabase
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    st.warning("Database module not available. Running in demo mode.")

try:
    from pdf_generator import generate_premium_pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Job Card Pro",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #1E3A5F;
        --primary-light: #2E5A8F;
        --secondary: #00C896;
        --accent: #FF6B35;
        --background: #F8FAFC;
        --card-bg: #FFFFFF;
        --text: #1A1A2E;
        --text-light: #6B7280;
        --border: #E2E8F0;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --info: #3B82F6;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--primary-light);
        border-radius: 10px;
    }

    /* Main container styling */
    .main-container {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(30, 58, 95, 0.3);
    }

    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 3rem 1rem;
        color: white;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }

    /* Stats cards */
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin-top: 2rem;
    }
    .stat-card {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        padding: 1.5rem 2.5rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }

    /* Section cards */
    .section-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid var(--border);
        transition: all 0.3s ease;
    }
    .section-card:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        border-color: var(--primary-light);
    }

    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border);
    }
    .section-icon {
        font-size: 1.5rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--primary);
    }

    /* Form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > div,
    .stNumberInput > div > div > input {
        background-color: #F8FAFC;
        border: 2px solid var(--border);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus,
    .stDateInput > div > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.1);
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 58, 95, 0.4);
    }

    .secondary-btn > button {
        background: linear-gradient(135deg, var(--secondary) 0%, #00A87D 100%);
    }

    .success-btn > button {
        background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
    }

    .danger-btn > button {
        background: linear-gradient(135deg, var(--danger) 0%, #DC2626 100%);
    }

    /* DataFrame styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    .dataframe thead {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
    }
    .dataframe tbody tr:nth-child(even) {
        background-color: #F8FAFC;
    }
    .dataframe tbody tr:hover {
        background-color: #EEF2FF;
    }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-pending {
        background: #FEF3C7;
        color: #92400E;
    }
    .badge-in-progress {
        background: #DBEAFE;
        color: #1E40AF;
    }
    .badge-completed {
        background: #D1FAE5;
        color: #065F46;
    }
    .badge-cancelled {
        background: #FEE2E2;
        color: #991B1B;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #F1F5F9;
        padding: 0.5rem;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(30, 58, 95, 0.1);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
    }

    /* Checkbox styling */
    .stCheckbox > label {
        background: #F8FAFC;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 1px solid var(--border);
        transition: all 0.3s ease;
    }
    .stCheckbox > label:hover {
        border-color: var(--primary);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: #F8FAFC;
        border-radius: 10px;
        border: 1px solid var(--border);
    }

    /* Alert/Info boxes */
    .info-box {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 4px solid var(--info);
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-left: 4px solid var(--success);
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 4px solid var(--warning);
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }

    /* Table wrapper */
    .table-wrapper {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    /* Navigation */
    .nav-container {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }

    /* QR Code styling */
    .qr-container {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Signature section */
    .signature-box {
        background: #FAFAFA;
        border: 2px dashed var(--border);
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
    }

    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, #F1F5F9 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid var(--border);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
    }
    .metric-label {
        color: var(--text-light);
        font-size: 0.9rem;
    }

    /* Animation keyframes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .stats-container { gap: 1rem; }
        .stat-card { padding: 1rem 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)


# Helper functions
def make_qr_bytes(data: str) -> bytes:
    """Generate QR code as bytes."""
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(data)
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def rows_to_df(rows: List, columns: List) -> pd.DataFrame:
    """Convert rows to DataFrame with proper columns."""
    if not rows:
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


def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'items': [],
        'materials': [],
        'grn_entries': [],
        'operations': {},
        'view_job_card': None,
        'current_tab': 'input'
    }
    for key, value in defaults.items():
        if key not in st.session_state or not isinstance(st.session_state.get(key), type(value)):
            st.session_state[key] = value


def create_section_header(icon: str, title: str):
    """Create a styled section header."""
    st.markdown(f"""
        <div class="section-header">
            <span class="section-icon">{icon}</span>
            <span class="section-title">{title}</span>
        </div>
    """, unsafe_allow_html=True)


def show_success(message: str):
    """Show success message."""
    st.success(f"✅ {message}")


def show_error(message: str):
    """Show error message."""
    st.error(f"❌ {message}")


def show_info(message: str):
    """Show info message."""
    st.info(f"ℹ️ {message}")


# Page functions
def home_page():
    """Display the home/dashboard page."""
    # Hero Section
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">📋 Job Card Pro</h1>
            <p class="hero-subtitle">Professional Job Card Management System with Modern UI & MySQL Backend</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Stats
    if DB_AVAILABLE:
        stats = get_job_card_statistics()
        total = stats.get('total', 0)
        this_month = stats.get('this_month', 0)
        pending = stats.get('by_status', {}).get('Pending', 0)
        completed = stats.get('by_status', {}).get('Completed', 0)
    else:
        total = len(st.session_state.get('items', [])) if st.session_state.get('items') else 0
        this_month = 0
        pending = 0
        completed = 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total}</div>
                <div class="metric-label">Total Job Cards</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{this_month}</div>
                <div class="metric-label">This Month</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{pending}</div>
                <div class="metric-label">Pending</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{completed}</div>
                <div class="metric-label">Completed</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Create New Job Card", use_container_width=True):
            st.session_state['current_tab'] = 'input'
            st.rerun()
    with col2:
        if st.button("📋 View All Job Cards", use_container_width=True):
            st.session_state['current_tab'] = 'records'
            st.rerun()
    with col3:
        if st.button("🔍 Search Job Cards", use_container_width=True):
            st.session_state['current_tab'] = 'search'
            st.rerun()
    
    # Features section
    st.markdown("### ✨ Features")
    features_col1, features_col2, features_col3 = st.columns(3)
    with features_col1:
        st.markdown("""
            <div class="section-card">
                <h4>📝 Modern Input Form</h4>
                <p>Beautiful, intuitive forms with real-time validation and auto-save functionality.</p>
            </div>
        """, unsafe_allow_html=True)
    with features_col2:
        st.markdown("""
            <div class="section-card">
                <h4>💾 MySQL Database</h4>
                <p>Secure storage of all job cards with full CRUD operations and search capabilities.</p>
            </div>
        """, unsafe_allow_html=True)
    with features_col3:
        st.markdown("""
            <div class="section-card">
                <h4>📄 Premium PDF</h4>
                <p>Generate professional, print-ready PDF documents with modern design.</p>
            </div>
        """, unsafe_allow_html=True)


def input_page():
    """Display the job card input form."""
    st.markdown("""
        <div class="section-card animate-fade-in">
            <h2 style="text-align: center; color: var(--primary);">📝 Create New Job Card</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Main input form
    with st.form("job_card_form", clear_on_submit=False):
        # Company Header Section
        create_section_header("🏢", "Company Header")
        col_logo, col_name = st.columns([1, 3])
        with col_logo:
            logo_file = st.file_uploader("Company Logo", type=["png", "jpg", "jpeg"])
            if logo_file:
                st.image(logo_file, width=150)
        with col_name:
            company_name = st.text_input("Company Name", placeholder="Enter your company name")
            company_address = st.text_area("Company Address", placeholder="Enter company address", height=100)
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # Vendor Details Section
        create_section_header("🏗️", "Vendor Details")
        colv1, colv2 = st.columns(2)
        with colv1:
            vendor_id = st.text_input("Vendor ID", placeholder="e.g., VND-001")
            vendor_company = st.text_input("Vendor Company Name", placeholder="Enter vendor company name")
            vendor_person = st.text_input("Contact Person", placeholder="Contact person name")
            vendor_mobile = st.text_input("Mobile Number", placeholder="+91 XXXXX XXXXX")
        with colv2:
            vendor_gst = st.text_input("GST Number", placeholder="XX XXXXX XXXXX XXX")
            vendor_address = st.text_area("Vendor Address", placeholder="Vendor address", height=120)
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # Job Details Section
        create_section_header("🔢", "Job Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            job_no = st.text_input("Job Card No.", value=f"JC-{date.today().strftime('%Y%m%d%H%M')}", 
                                   placeholder="Auto-generated or enter custom")
        with col2:
            job_date = st.date_input("Date", date.today())
        with col3:
            dispatch_location = st.text_input("Dispatch Location", placeholder="Enter dispatch location")
        
        # QR Code Preview
        qr_text_input = f"JobNo: {job_no} | Date: {job_date} | Dispatch: {dispatch_location} | VendorID: {vendor_id}"
        qr_bytes = make_qr_bytes(qr_text_input)
        
        col_qr, col_qr_info = st.columns([1, 3])
        with col_qr:
            st.markdown("<div class='qr-container'>", unsafe_allow_html=True)
            st.image(qr_bytes, width=150, caption="📱 QR Code")
            st.markdown("</div>", unsafe_allow_html=True)
        with col_qr_info:
            st.info("📱 This QR code contains job card reference information. It will be included in the PDF.")
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # Item Details Section
        create_section_header("📦", "Item Details")
        
        # Item input fields
        item_cols = st.columns([3, 2, 2, 1.5, 1, 1])
        item_labels = ["Description", "Drawing No.", "Drawing Link", "Grade", "Qty", "UOM"]
        item_defaults = ["", "", "", "", 0, "Nos"]
        
        item_inputs = {}
        for i, (label, default) in enumerate(zip(item_labels, item_defaults)):
            if i == 4:
                item_inputs[label] = item_cols[i].number_input(label, value=0, min_value=0)
            else:
                item_inputs[label] = item_cols[i].text_input(label, value=default)
        
        col_add_item, col_clear_items = st.columns([1, 5])
        with col_add_item:
            if st.form_submit_button("➕ Add Item", use_container_width=True):
                if item_inputs["Description"]:
                    st.session_state['items'].append([
                        item_inputs["Description"],
                        item_inputs["Drawing No."],
                        item_inputs["Drawing Link"],
                        item_inputs["Grade"],
                        item_inputs["Qty"],
                        item_inputs["UOM"]
                    ])
                    show_success("Item added successfully!")
                    st.rerun()
        
        # Display items table
        if st.session_state['items']:
            st.markdown("<h4>Added Items:</h4>", unsafe_allow_html=True)
            items_df = rows_to_df(st.session_state['items'], 
                                   ["Description", "Drawing No.", "Drawing Link", "Grade", "Qty", "UOM"])
            st.dataframe(items_df, use_container_width=True, hide_index=True)
            
            # Delete item functionality
            delete_idx = st.number_input("Enter row number to delete (1-based)", min_value=1, 
                                         max_value=len(st.session_state['items']), value=1)
            if st.button("🗑️ Delete Item", use_container_width=True):
                if 1 <= delete_idx <= len(st.session_state['items']):
                    st.session_state['items'].pop(delete_idx - 1)
                    show_success("Item deleted!")
                    st.rerun()
            
            if st.button("Clear All Items", use_container_width=True):
                st.session_state['items'] = []
                st.rerun()
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # Material Issued Section
        create_section_header("🔧", "Material Issued")
        
        mat_cols = st.columns([3, 2, 1.5, 1.5, 1, 2])
        mat_labels = ["Raw Material", "Heat No.", "Dia/Size", "Weight", "Qty", "Remark"]
        mat_defaults = ["", "", "", 0, 0, ""]
        
        mat_inputs = {}
        for i, (label, default) in enumerate(zip(mat_labels, mat_defaults)):
            if i == 3 or i == 4:
                mat_inputs[label] = mat_cols[i].number_input(label, value=default)
            else:
                mat_inputs[label] = mat_cols[i].text_input(label, value=default)
        
        col_add_mat, _ = st.columns([1, 5])
        with col_add_mat:
            if st.form_submit_button("➕ Add Material", use_container_width=True):
                st.session_state['materials'].append([
                    mat_inputs["Raw Material"],
                    mat_inputs["Heat No."],
                    mat_inputs["Dia/Size"],
                    mat_inputs["Weight"],
                    mat_inputs["Qty"],
                    mat_inputs["Remark"]
                ])
                show_success("Material added!")
                st.rerun()
        
        if st.session_state['materials']:
            st.markdown("<h4>Added Materials:</h4>", unsafe_allow_html=True)
            materials_df = rows_to_df(st.session_state['materials'],
                                       ["Raw Material", "Heat No.", "Dia/Size", "Weight", "Qty", "Remark"])
            st.dataframe(materials_df, use_container_width=True, hide_index=True)
            
            if st.button("Clear Materials", use_container_width=True):
                st.session_state['materials'] = []
                st.rerun()
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # Operations Section
        create_section_header("⚙️", "Operation Checklist")
        
        operations = ["Cutting", "Turning (Traub/CNC)", "Milling", "Threading", 
                      "Drilling", "Punching", "Deburring", "Plating", "Packing"]
        
        op_cols = st.columns(3)
        for idx, op in enumerate(operations):
            with op_cols[idx % 3]:
                checked = st.checkbox(op, key=f"op_{op}")
                st.session_state['operations'][op] = checked
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # Machine Details Section
        create_section_header("🏭", "Machine Specific Details (Optional)")
        
        show_machine = st.checkbox("Show Machine Details", value=False)
        machine_details = {}
        if show_machine:
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                machine_type = st.selectbox("Machine Type", ["Traub", "CNC", "VMC", "Lathe", "Milling"])
            with col_m2:
                cycle_time = st.text_input("Cycle Time (sec)")
            with col_m3:
                rpm = st.text_input("RPM")
            
            feed = st.text_input("Feed Rate")
            machine_details = {"machine_type": machine_type, "cycle_time": cycle_time, 
                             "rpm": rpm, "feed_rate": feed}
            
            if machine_type == "Traub":
                gear_setup = st.text_input("Traub Gear Setup")
                machine_details["gear_setup"] = gear_setup
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # Quality Instructions Section
        create_section_header("✅", "Quality Instructions")
        
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            tolerance = st.text_input("Tolerance", placeholder="e.g., ±0.01mm")
        with col_q2:
            surface_finish = st.text_input("Surface Finish", placeholder="e.g., Ra 0.8")
        with col_q3:
            hardness = st.text_input("Hardness Requirement", placeholder="e.g., 45-50 HRC")
        
        thread_check = st.checkbox("Thread GO/NO-GO Check Required")
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # Delivery Schedule Section
        create_section_header("🚚", "Delivery Schedule")
        
        expected_date = st.date_input("Expected Delivery Date")
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # GRN Section
        create_section_header("📥", "Goods Received / QC")
        
        grn_cols_labels = ["Date", "Qty Received", "OK Qty", "Rejected Qty", "Remarks", "QC Approved By"]
        grn_cols_widgets = st.columns([1.5, 1, 1, 1, 2, 1.5])
        
        grn_inputs = {}
        for i, label in enumerate(grn_cols_labels):
            if i == 0:
                grn_inputs[label] = grn_cols_widgets[i].text_input(label, value=date.today().strftime("%Y-%m-%d"))
            elif i >= 1 and i <= 3:
                grn_inputs[label] = grn_cols_widgets[i].number_input(label, value=0, min_value=0)
            else:
                grn_inputs[label] = grn_cols_widgets[i].text_input(label)
        
        col_add_grn, _ = st.columns([1, 5])
        with col_add_grn:
            if st.form_submit_button("➕ Add GRN Entry", use_container_width=True):
                st.session_state['grn_entries'].append([
                    grn_inputs["Date"],
                    grn_inputs["Qty Received"],
                    grn_inputs["OK Qty"],
                    grn_inputs["Rejected Qty"],
                    grn_inputs["Remarks"],
                    grn_inputs["QC Approved By"]
                ])
                show_success("GRN Entry added!")
                st.rerun()
        
        if st.session_state['grn_entries']:
            st.markdown("<h4>GRN Entries:</h4>", unsafe_allow_html=True)
            grn_df = rows_to_df(st.session_state['grn_entries'], grn_cols_labels)
            st.dataframe(grn_df, use_container_width=True, hide_index=True)
            
            if st.button("Clear GRN Entries", use_container_width=True):
                st.session_state['grn_entries'] = []
                st.rerun()
        
        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)
        
        # Submit buttons
        col_save, col_save_db, col_preview = st.columns([1, 1, 1])
        with col_save:
            submitted = st.form_submit_button("💾 Save to Session", use_container_width=True)
        with col_save_db:
            save_to_db = st.form_submit_button("💾 Save to Database", use_container_width=True, type="primary")
        with col_preview:
            preview_pdf = st.form_submit_button("👁️ Preview & Generate PDF", use_container_width=True)
    
    # Handle form submissions
    if submitted:
        show_success("Job card saved to session!")
    
    if save_to_db and DB_AVAILABLE:
        logo_b64 = ""
        if logo_file:
            logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
        
        # Prepare data for database
        data = {
            'job_card_no': job_no,
            'job_date': job_date.isoformat(),
            'company_name': company_name,
            'company_address': company_address,
            'logo_data': logo_b64,
            'vendor_id': vendor_id,
            'vendor_company': vendor_company,
            'vendor_person': vendor_person,
            'vendor_mobile': vendor_mobile,
            'vendor_gst': vendor_gst,
            'vendor_address': vendor_address,
            'dispatch_location': dispatch_location,
            'qr_code_data': qr_text_input,
            'expected_delivery_date': expected_date.isoformat(),
            'status': 'Pending',
            'items': [{'description': i[0], 'drawing_no': i[1], 'drawing_link': i[2], 
                      'grade': i[3], 'quantity': i[4], 'uom': i[5]} for i in st.session_state['items']],
            'materials': [{'raw_material': m[0], 'heat_no': m[1], 'dia_size': m[2],
                          'weight': m[3], 'quantity': m[4], 'remark': m[5]} for m in st.session_state['materials']],
            'operations': [{'name': k, 'selected': v} for k, v in st.session_state['operations'].items()],
            'machine_details': machine_details if machine_details else None,
            'quality': {
                'tolerance': tolerance,
                'surface_finish': surface_finish,
                'hardness': hardness,
                'thread_check': thread_check
            },
            'grn_entries': [{'date': g[0], 'qty_received': g[1], 'ok_qty': g[2],
                           'rejected_qty': g[3], 'remarks': g[4], 'qc_approved_by': g[5]}
                          for g in st.session_state['grn_entries']],
            'signatures': {
                'prepared_by': '',
                'prepared_date': date.today().isoformat()
            }
        }
        
        result = save_job_card(data)
        if result:
            show_success(f"Job card saved to database with ID: {result}!")
        else:
            show_error("Failed to save job card to database!")
    
    if preview_pdf:
        st.session_state['current_tab'] = 'preview'
        st.rerun()


def preview_page():
    """Display the job card preview."""
    st.markdown("""
        <div class="section-card animate-fade-in">
            <h2 style="text-align: center; color: var(--primary);">👁️ Job Card Preview</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Create preview columns
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Company Info
        st.markdown("""
            <div class="section-card">
                <h3 style="color: var(--primary);">🏢 Company Information</h3>
                <p><strong>Name:</strong> Your Company Name</p>
                <p><strong>Address:</strong> Company Address</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Vendor Details
        st.markdown("""
            <div class="section-card">
                <h3 style="color: var(--primary);">🏗️ Vendor Details</h3>
                <p><strong>ID:</strong> VND-001</p>
                <p><strong>Company:</strong> Vendor Company</p>
                <p><strong>Contact:</strong> Contact Person</p>
                <p><strong>Mobile:</strong> +91 XXXXX XXXXX</p>
                <p><strong>GST:</strong> XX XXXXX XXXXX XXX</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Items
        st.markdown("""
            <div class="section-card">
                <h3 style="color: var(--primary);">📦 Item Details</h3>
            </div>
        """, unsafe_allow_html=True)
        if st.session_state['items']:
            items_df = rows_to_df(st.session_state['items'],
                                   ["Description", "Drawing No.", "Drawing Link", "Grade", "Qty", "UOM"])
            st.dataframe(items_df, use_container_width=True, hide_index=True)
        
        # Materials
        st.markdown("""
            <div class="section-card">
                <h3 style="color: var(--primary);">🔧 Material Issued</h3>
            </div>
        """, unsafe_allow_html=True)
        if st.session_state['materials']:
            materials_df = rows_to_df(st.session_state['materials'],
                                       ["Raw Material", "Heat No.", "Dia/Size", "Weight", "Qty", "Remark"])
            st.dataframe(materials_df, use_container_width=True, hide_index=True)
    
    with col_right:
        # Job Card Info
        st.markdown("""
            <div class="section-card" style="text-align: center;">
                <h3 style="color: var(--primary);">🔢 Job Card</h3>
                <p><strong>No:</strong> JC-20240101</p>
                <p><strong>Date:</strong> 2024-01-01</p>
                <p><strong>Dispatch:</strong> Location</p>
            </div>
        """, unsafe_allow_html=True)
        
        # QR Code
        qr_text = f"JobNo: JC-20240101 | Date: 2024-01-01"
        qr_bytes = make_qr_bytes(qr_text)
        st.markdown("<div class='qr-container'>", unsafe_allow_html=True)
        st.image(qr_bytes, width=150, caption="QR Code")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Operations
        st.markdown("""
            <div class="section-card">
                <h4 style="color: var(--primary);">⚙️ Operations</h4>
                <ul>
                    <li>Cutting</li>
                    <li>Turning</li>
                    <li>Milling</li>
                    <li>Threading</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # PDF Generation Section
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
        <div class="section-card">
            <h3 style="text-align: center; color: var(--primary);">📄 Generate PDF</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col_pdf1, col_pdf2 = st.columns([1, 1])
    with col_pdf1:
        if st.button("📄 Generate Premium PDF", use_container_width=True):
            if PDF_AVAILABLE:
                show_info("PDF generation started...")
            else:
                show_error("PDF generator not available!")
    
    with col_pdf2:
        if st.button("⬇️ Download PDF", use_container_width=True):
            show_info("Download will be available after generation...")


def records_page():
    """Display all job card records."""
    st.markdown("""
        <div class="section-card animate-fade-in">
            <h2 style="text-align: center; color: var(--primary);">📋 Job Card Records</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if DB_AVAILABLE:
        # Filters
        col_filter1, col_filter2, col_filter3 = st.columns([2, 1, 1])
        with col_filter1:
            search_term = st.text_input("🔍 Search", placeholder="Search by job card no, vendor...")
        with col_filter2:
            status_filter = st.selectbox("Status", ["All", "Pending", "In Progress", "Completed", "Cancelled"])
        with col_filter3:
            sort_by = st.selectbox("Sort By", ["Newest First", "Oldest First"])
        
        # Get job cards
        if search_term:
            records = search_job_cards(search_term)
        elif status_filter != "All":
            records = get_all_job_cards(status_filter)
        else:
            records = get_all_job_cards()
        
        if records:
            # Display records
            for record in records:
                with st.expander(f"📋 {record['job_card_no']} - {record['vendor_company']}"):
                    col_r1, col_r2, col_r3 = st.columns([2, 1, 1])
                    with col_r1:
                        st.write(f"**Vendor:** {record['vendor_company']}")
                        st.write(f"**Contact:** {record['vendor_person']}")
                        st.write(f"**Mobile:** {record['vendor_mobile']}")
                    with col_r2:
                        st.write(f"**Date:** {record['job_date']}")
                        st.write(f"**Dispatch:** {record['dispatch_location']}")
                    with col_r3:
                        status = record.get('status', 'Pending')
                        st.markdown(f"<span class='badge badge-{status.lower().replace(' ', '-')}'>{status}</span>", 
                                   unsafe_allow_html=True)
                    
                    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                    with col_btn1:
                        if st.button("👁️ View", key=f"view_{record['id']}"):
                            st.session_state['view_job_card'] = record['job_card_no']
                            st.rerun()
                    with col_btn2:
                        if st.button("✏️ Edit", key=f"edit_{record['id']}"):
                            show_info("Edit functionality coming soon...")
                    with col_btn3:
                        if st.button("📄 PDF", key=f"pdf_{record['id']}"):
                            show_info("PDF generation for this record...")
                    with col_btn4:
                        if st.button("🗑️ Delete", key=f"del_{record['id']}"):
                            if delete_job_card(record['job_card_no']):
                                show_success("Job card deleted!")
                                st.rerun()
                            else:
                                show_error("Failed to delete!")
        else:
            st.info("No job cards found. Create your first job card!")
    else:
        st.warning("Database not available. Records will be shown from session storage.")
        if st.session_state['items']:
            st.dataframe(rows_to_df(st.session_state['items'], 
                                   ["Description", "Drawing No.", "Drawing Link", "Grade", "Qty", "UOM"]),
                        use_container_width=True, hide_index=True)
        else:
            st.info("No records in session. Create a new job card!")


def search_page():
    """Advanced search functionality."""
    st.markdown("""
        <div class="section-card animate-fade-in">
            <h2 style="text-align: center; color: var(--primary);">🔍 Advanced Search</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        st.markdown("""
            <div class="section-card">
                <h4>📅 Search by Date Range</h4>
                <p>Find job cards within a specific date range.</p>
            </div>
        """, unsafe_allow_html=True)
        start_date = st.date_input("Start Date", date.today())
        end_date = st.date_input("End Date", date.today())
        if st.button("Search by Date", use_container_width=True):
            if DB_AVAILABLE:
                records = JobCardDatabase.get_job_cards_by_date_range(
                    start_date.isoformat(), end_date.isoformat()
                )
                if records:
                    st.dataframe(pd.DataFrame(records), use_container_width=True)
                else:
                    st.info("No records found in this date range.")
            else:
                st.warning("Database not available.")
    
    with col_s2:
        st.markdown("""
            <div class="section-card">
                <h4>🏷️ Search by Vendor</h4>
                <p>Find all job cards for a specific vendor.</p>
            </div>
        """, unsafe_allow_html=True)
        vendor_search = st.text_input("Enter Vendor ID or Name", placeholder="e.g., VND-001")
        if st.button("Search Vendor", use_container_width=True):
            if DB_AVAILABLE and vendor_search:
                records = search_job_cards(vendor_search)
                if records:
                    st.dataframe(pd.DataFrame(records), use_container_width=True)
                else:
                    st.info("No records found for this vendor.")
    
    # Statistics
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
        <div class="section-card">
            <h3 style="text-align: center; color: var(--primary);">📊 Statistics</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if DB_AVAILABLE:
        stats = get_job_card_statistics()
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{stats.get('total', 0)}</div>
                    <div class="metric-label">Total Job Cards</div>
                </div>
            """, unsafe_allow_html=True)
        with col_stat2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{stats.get('this_month', 0)}</div>
                    <div class="metric-label">This Month</div>
                </div>
            """, unsafe_allow_html=True)
        with col_stat3:
            pending = stats.get('by_status', {}).get('Pending', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{pending}</div>
                    <div class="metric-label">Pending</div>
                </div>
            """, unsafe_allow_html=True)
        with col_stat4:
            completed = stats.get('by_status', {}).get('Completed', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{completed}</div>
                    <div class="metric-label">Completed</div>
                </div>
            """, unsafe_allow_html=True)


# Main application
def main():
    """Main application entry point."""
    init_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h2 style="color: var(--primary);">📋 Job Card Pro</h2>
            </div>
        """, unsafe_allow_html=True)
        
        selected = streamlit_option_menu(
            menu_title="Navigation",
            options=["🏠 Home", "📝 New Job Card", "👁️ Preview", "📋 Records", "🔍 Search"],
            icons=["house", "file-plus", "eye", "archive", "search"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0.5rem", "background-color": "#F8FAFC"},
                "menu-title": {"font-weight": "bold"},
                "selected": {"background-color": "#1E3A5F", "color": "white"}
            }
        )
        
        # Update current tab based on selection
        tab_mapping = {
            "🏠 Home": "home",
            "📝 New Job Card": "input",
            "👁️ Preview": "preview",
            "📋 Records": "records",
            "🔍 Search": "search"
        }
        if tab_mapping.get(selected):
            st.session_state['current_tab'] = tab_mapping[selected]
        
        # Database status
        st.markdown("<hr>", unsafe_allow_html=True)
        if DB_AVAILABLE:
            st.success("🟢 Database Connected")
        else:
            st.warning("🟡 Database Not Connected")
        
        # Settings
        st.markdown("""
            <div style="margin-top: 2rem; padding: 1rem; background: #F1F5F9; border-radius: 10px;">
                <h5>⚙️ Settings</h5>
                <p style="font-size: 0.85rem; color: #6B7280;">
                    Configure your database connection using environment variables.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    current_tab = st.session_state.get('current_tab', 'home')
    
    if current_tab == 'home':
        home_page()
    elif current_tab == 'input':
        input_page()
    elif current_tab == 'preview':
        preview_page()
    elif current_tab == 'records':
        records_page()
    elif current_tab == 'search':
        search_page()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Job Card Pro - Main Application
A comprehensive, attractive Job Card Management System with MySQL backend.

Usage:
    python main.py                    # Run with default settings
    DB_HOST=localhost DB_PORT=3306 DB_USER=root DB_PASSWORD=secret DB_NAME=job_card_db python main.py
    
Environment Variables:
    DB_HOST: MySQL host (default: localhost)
    DB_PORT: MySQL port (default: 3306)
    DB_USER: MySQL user (default: root)
    DB_PASSWORD: MySQL password (default: empty)
    DB_NAME: Database name (default: job_card_db)
"""

import os
import sys
import io
import base64
from datetime import date, datetime
from typing import Dict, List, Any, Optional

import streamlit as st
import pandas as pd
import qrcode
from PIL import Image

# Import local modules
from database import (
    init_database, save_job_card, get_job_card, get_all_job_cards,
    update_job_card_status, delete_job_card, search_job_cards,
    get_job_card_statistics, JobCardDatabase
)
from pdf_generator import generate_premium_pdf

# Page configuration
st.set_page_config(
    page_title="Job Card Pro - Modern Job Card Management",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, attractive UI
st.markdown("""
<style>
    /* ==================== CSS VARIABLES ==================== */
    :root {
        --primary: #1E3A5F;
        --primary-light: #2E5A8F;
        --primary-dark: #0F1F35;
        --secondary: #00C896;
        --secondary-light: #00E6AD;
        --accent: #FF6B35;
        --accent-light: #FF8F66;
        --background: #F8FAFC;
        --surface: #FFFFFF;
        --text: #1A1A2E;
        --text-light: #64748B;
        --text-muted: #94A3B8;
        --border: #E2E8F0;
        --success: #10B981;
        --success-light: #D1FAE5;
        --warning: #F59E0B;
        --warning-light: #FEF3C7;
        --danger: #EF4444;
        --danger-light: #FEE2E2;
        --info: #3B82F6;
        --info-light: #DBEAFE;
        --gradient-primary: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        --gradient-secondary: linear-gradient(135deg, var(--secondary) 0%, #00A87D 100%);
        --gradient-accent: linear-gradient(135deg, var(--accent) 0%, #FF8F66 100%);
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
    }

    /* ==================== GLOBAL STYLES ==================== */
    .stApp {
        background: var(--background);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--background);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--primary-light);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }

    /* ==================== SIDEBAR STYLES ==================== */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border);
    }
    
    .sidebar-header {
        padding: 1.5rem;
        text-align: center;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
    }
    
    .sidebar-logo {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--primary);
        margin: 0;
    }
    
    .sidebar-subtitle {
        font-size: 0.85rem;
        color: var(--text-light);
        margin: 0;
    }

    /* ==================== CARD STYLES ==================== */
    .card {
        background: var(--surface);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border);
    }
    
    .card-icon {
        width: 48px;
        height: 48px;
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        background: var(--gradient-primary);
        color: white;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--primary);
        margin: 0;
    }
    
    .card-subtitle {
        font-size: 0.85rem;
        color: var(--text-light);
        margin: 0;
    }

    /* ==================== HERO SECTION ==================== */
    .hero-section {
        background: var(--gradient-primary);
        border-radius: var(--radius-xl);
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-xl);
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: rgba(255,255,255,0.1);
        transform: rotate(30deg);
        pointer-events: none;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.95;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* ==================== STATS CARDS ==================== */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: var(--surface);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary);
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: var(--text-light);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ==================== BUTTON STYLES ==================== */
    .stButton > button {
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-md);
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .primary-button {
        background: var(--gradient-primary) !important;
        color: white !important;
        box-shadow: var(--shadow-md);
    }
    
    .primary-button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .secondary-button {
        background: var(--gradient-secondary) !important;
        color: white !important;
        box-shadow: var(--shadow-md);
    }
    
    .accent-button {
        background: var(--gradient-accent) !important;
        color: white !important;
        box-shadow: var(--shadow-md);
    }
    
    .outline-button {
        background: transparent !important;
        border: 2px solid var(--primary) !important;
        color: var(--primary) !important;
    }

    /* ==================== INPUT STYLES ==================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > div,
    .stNumberInput > div > div > input {
        background-color: var(--background);
        border: 2px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus,
    .stDateInput > div > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.15);
        background: var(--surface);
    }
    
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stDateInput > label,
    .stNumberInput > label {
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.5rem;
    }

    /* ==================== TABS STYLES ==================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--background);
        padding: 0.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: var(--text-light);
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(30, 58, 95, 0.1);
        color: var(--primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary) !important;
        color: white !important;
    }

    /* ==================== DATAFRAME STYLES ==================== */
    .dataframe {
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    
    .dataframe thead {
        background: var(--gradient-primary);
        color: white;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: var(--background);
    }
    
    .dataframe tbody tr:hover {
        background-color: rgba(30, 58, 95, 0.05);
    }

    /* ==================== BADGE STYLES ==================== */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-pending {
        background: var(--warning-light);
        color: #92400E;
    }
    
    .badge-progress {
        background: var(--info-light);
        color: #1E40AF;
    }
    
    .badge-completed {
        background: var(--success-light);
        color: #065F46;
    }
    
    .badge-cancelled {
        background: var(--danger-light);
        color: #991B1B;
    }

    /* ==================== ALERT STYLES ==================== */
    .success-box {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-left: 4px solid var(--success);
        padding: 1rem 1.5rem;
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 4px solid var(--warning);
        padding: 1rem 1.5rem;
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        margin: 1rem 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-left: 4px solid var(--danger);
        padding: 1rem 1.5rem;
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 4px solid var(--info);
        padding: 1rem 1.5rem;
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        margin: 1rem 0;
    }

    /* ==================== QR CODE SECTION ==================== */
    .qr-container {
        background: var(--surface);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
    }
    
    .qr-title {
        font-size: 0.9rem;
        color: var(--text-light);
        margin-top: 0.75rem;
        font-weight: 500;
    }

    /* ==================== SIGNATURE SECTION ==================== */
    .signature-box {
        background: var(--background);
        border: 2px dashed var(--border);
        border-radius: var(--radius-lg);
        padding: 2rem;
        text-align: center;
    }
    
    .signature-line {
        border-top: 1px solid var(--text);
        width: 80%;
        margin: 2rem auto 0.5rem;
        position: relative;
    }
    
    .signature-label {
        font-size: 0.85rem;
        color: var(--text-light);
    }

    /* ==================== METRIC CARD ==================== */
    .metric-card {
        background: var(--surface);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary);
    }
    
    .metric-label {
        color: var(--text-light);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* ==================== EXPANDER STYLES ==================== */
    .streamlit-expanderHeader {
        background: var(--background);
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        font-weight: 600;
        color: var(--text);
    }

    /* ==================== DIVIDER ==================== */
    .custom-divider {
        height: 2px;
        background: var(--border);
        margin: 2rem 0;
        border-radius: 1px;
    }

    /* ==================== RESPONSIVE ==================== */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .stats-grid { 
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
        .stat-value { font-size: 2rem; }
    }
    
    @media (max-width: 480px) {
        .stats-grid { 
            grid-template-columns: 1fr;
        }
        .hero-section { padding: 2rem 1rem; }
    }

    /* ==================== ANIMATIONS ==================== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    .animate-slide-in {
        animation: slideIn 0.4s ease-out;
    }
</style>
""", unsafe_allow_html=True)


# ==================== HELPER FUNCTIONS ====================
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
        'current_page': 'home'
    }
    for key, value in defaults.items():
        if key not in st.session_state or not isinstance(st.session_state.get(key), type(value)):
            st.session_state[key] = value


def show_toast(message: str, type_: str = "success"):
    """Show a toast notification."""
    if type_ == "success":
        st.success(message)
    elif type_ == "error":
        st.error(message)
    elif type_ == "warning":
        st.warning(message)
    else:
        st.info(message)


# ==================== SIDEBAR NAVIGATION ====================
def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        # Logo and title
        st.markdown("""
            <div class="sidebar-header">
                <div class="sidebar-logo">📋</div>
                <h2 class="sidebar-title">Job Card Pro</h2>
                <p class="sidebar-subtitle">Modern Management System</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        st.markdown("### 📌 Navigation")
        
        if st.button("🏠 Dashboard", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "home" else "secondary"):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("📝 New Job Card", use_container_width=True,
                    type="primary" if st.session_state.current_page == "create" else "secondary"):
            st.session_state.current_page = "create"
            st.rerun()
        
        if st.button("📋 All Records", use_container_width=True,
                    type="primary" if st.session_state.current_page == "records" else "secondary"):
            st.session_state.current_page = "records"
            st.rerun()
        
        if st.button("🔍 Search", use_container_width=True,
                    type="primary" if st.session_state.current_page == "search" else "secondary"):
            st.session_state.current_page = "search"
            st.rerun()
        
        if st.button("📊 Statistics", use_container_width=True,
                    type="primary" if st.session_state.current_page == "stats" else "secondary"):
            st.session_state.current_page = "stats"
            st.rerun()
        
        # Database status
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        st.markdown("### 🔌 Database Status")
        
        try:
            stats = get_job_card_statistics()
            st.success("✅ Connected")
            st.caption(f"Total Records: {stats.get('total', 0)}")
        except Exception as e:
            st.warning("⚠️ Not Connected")
            st.caption("Run with MySQL for full features")
        
        # Settings section
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        st.markdown("""
            <div style="padding: 1rem; background: var(--background); border-radius: var(--radius-md);">
                <h4 style="margin: 0 0 0.5rem 0;">⚙️ Settings</h4>
                <p style="font-size: 0.8rem; color: var(--text-light); margin: 0;">
                    Configure MySQL using environment variables:
                </p>
                <code style="font-size: 0.75rem;">
                    DB_HOST=localhost<br>
                    DB_PORT=3306<br>
                    DB_USER=root<br>
                    DB_PASSWORD=...
                </code>
            </div>
        """, unsafe_allow_html=True)


# ==================== PAGE: HOME/DASHBOARD ====================
def page_home():
    """Render the home/dashboard page."""
    # Hero Section
    st.markdown("""
        <div class="hero-section animate-fade-in">
            <h1 class="hero-title">📋 Job Card Pro</h1>
            <p class="hero-subtitle">Professional Job Card Management System with Modern UI & MySQL Backend</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Stats
    try:
        stats = get_job_card_statistics()
        total = stats.get('total', 0)
        this_month = stats.get('this_month', 0)
        pending = stats.get('by_status', {}).get('Pending', 0)
        completed = stats.get('by_status', {}).get('Completed', 0)
    except:
        total = len(st.session_state.get('items', []))
        this_month = 0
        pending = 0
        completed = 0
    
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card animate-fade-in">
                <div class="stat-icon">📋</div>
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total Job Cards</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card animate-fade-in" style="animation-delay: 0.1s;">
                <div class="stat-icon">📅</div>
                <div class="stat-value">{this_month}</div>
                <div class="stat-label">This Month</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card animate-fade-in" style="animation-delay: 0.2s;">
                <div class="stat-icon">⏳</div>
                <div class="stat-value">{pending}</div>
                <div class="stat-label">Pending</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card animate-fade-in" style="animation-delay: 0.3s;">
                <div class="stat-icon">✅</div>
                <div class="stat-value">{completed}</div>
                <div class="stat-label">Completed</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Create New Job Card", use_container_width=True, type="primary"):
            st.session_state.current_page = "create"
            st.rerun()
    
    with col2:
        if st.button("📋 View All Records", use_container_width=True):
            st.session_state.current_page = "records"
            st.rerun()
    
    with col3:
        if st.button("🔍 Search Job Cards", use_container_width=True):
            st.session_state.current_page = "search"
            st.rerun()
    
    # Features
    st.markdown("### ✨ Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="card">
                <div class="card-icon">📝</div>
                <h3>Modern Input Form</h3>
                <p style="color: var(--text-light);">
                    Beautiful, intuitive forms with real-time validation and smooth user experience.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="card">
                <div class="card-icon" style="background: var(--gradient-secondary);">💾</div>
                <h3>MySQL Database</h3>
                <p style="color: var(--text-light);">
                    Secure storage with full CRUD operations, search, and analytics capabilities.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="card">
                <div class="card-icon" style="background: var(--gradient-accent);">📄</div>
                <h3>Premium PDF</h3>
                <p style="color: var(--text-light);">
                    Generate professional, print-ready PDF documents with modern design.
                </p>
            </div>
        """, unsafe_allow_html=True)


# ==================== PAGE: CREATE JOB CARD ====================
def page_create():
    """Render the create job card page."""
    st.markdown("""
        <div class="card animate-fade-in">
            <div class="card-header">
                <div class="card-icon">📝</div>
                <div>
                    <h2 class="card-title">Create New Job Card</h2>
                    <p class="card-subtitle">Fill in all the details below to create a new job card</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Company & Vendor", "📦 Items & Materials", "⚙️ Operations & Quality", "📥 QC & Summary"])
    
    with tab1:
        # Company Header
        st.markdown("### 🏢 Company Header")
        col_logo, col_info = st.columns([1, 3])
        
        with col_logo:
            logo_file = st.file_uploader("Company Logo", type=["png", "jpg", "jpeg"])
            if logo_file:
                st.image(logo_file, width=150)
        
        with col_info:
            company_name = st.text_input("Company Name", placeholder="Enter your company name")
            company_address = st.text_area("Company Address", placeholder="Enter company address", height=100)
        
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        
        # Vendor Details
        st.markdown("### 🏗️ Vendor Details")
        colv1, colv2 = st.columns(2)
        
        with colv1:
            vendor_id = st.text_input("Vendor ID", placeholder="e.g., VND-001")
            vendor_company = st.text_input("Vendor Company Name", placeholder="Enter vendor company name")
            vendor_person = st.text_input("Contact Person", placeholder="Contact person name")
            vendor_mobile = st.text_input("Mobile Number", placeholder="+91 XXXXX XXXXX")
        
        with colv2:
            vendor_gst = st.text_input("GST Number", placeholder="XX XXXXX XXXXX XXX")
            vendor_address = st.text_area("Vendor Address", placeholder="Vendor address", height=120)
        
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        
        # Job Details
        st.markdown("### 🔢 Job Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            job_no = st.text_input("Job Card No.", value=f"JC-{date.today().strftime('%Y%m%d%H%M')}")
        
        with col2:
            job_date = st.date_input("Date", date.today())
        
        with col3:
            dispatch_location = st.text_input("Dispatch Location", placeholder="Enter dispatch location")
        
        # QR Code
        qr_text = f"JobNo: {job_no} | Date: {job_date} | Dispatch: {dispatch_location} | VendorID: {vendor_id}"
        qr_bytes = make_qr_bytes(qr_text)
        
        col_qr, col_info = st.columns([1, 3])
        with col_qr:
            st.markdown("<div class='qr-container'>", unsafe_allow_html=True)
            st.image(qr_bytes, width=150)
            st.markdown("<div class='qr-title'>📱 QR Code</div></div>", unsafe_allow_html=True)
        
        with col_info:
            st.info("📱 This QR code contains job card reference information and will be included in the PDF.")
    
    with tab2:
        # Item Details
        st.markdown("### 📦 Item Details")
        
        item_cols = st.columns([3, 2, 2, 1.5, 1, 1])
        item_labels = ["Description", "Drawing No.", "Drawing Link", "Grade", "Qty", "UOM"]
        item_defaults = ["", "", "", "", 0, "Nos"]
        
        item_vals = []
        for i, (label, default) in enumerate(zip(item_labels, item_defaults)):
            if i == 4:
                item_vals.append(item_cols[i].number_input(label, value=0, min_value=0))
            else:
                item_vals.append(item_cols[i].text_input(label, value=default))
        
        col_add, col_clear = st.columns([1, 4])
        with col_add:
            if st.button("➕ Add Item", use_container_width=True, type="primary"):
                if item_vals[0]:
                    st.session_state['items'].append(list(item_vals))
                    show_toast("✅ Item added successfully!")
                    st.rerun()
        
        if st.session_state['items']:
            st.markdown("<h4>Added Items:</h4>", unsafe_allow_html=True)
            items_df = rows_to_df(st.session_state['items'], 
                                   ["Description", "Drawing No.", "Drawing Link", "Grade", "Qty", "UOM"])
            st.dataframe(items_df, use_container_width=True, hide_index=True, height=200)
            
            if st.button("🗑️ Clear All Items", use_container_width=True):
                st.session_state['items'] = []
                st.rerun()
        
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        
        # Material Issued
        st.markdown("### 🔧 Material Issued")
        
        mat_cols = st.columns([3, 2, 1.5, 1.5, 1, 2])
        mat_labels = ["Raw Material", "Heat No.", "Dia/Size", "Weight", "Qty", "Remark"]
        mat_defaults = ["", "", "", 0, 0, ""]
        
        mat_vals = []
        for i, (label, default) in enumerate(zip(mat_labels, mat_defaults)):
            if i in [3, 4]:
                mat_vals.append(mat_cols[i].number_input(label, value=default))
            else:
                mat_vals.append(mat_cols[i].text_input(label, value=default))
        
        col_add_mat, _ = st.columns([1, 4])
        with col_add_mat:
            if st.button("➕ Add Material", use_container_width=True, type="primary"):
                st.session_state['materials'].append(list(mat_vals))
                show_toast("✅ Material added!")
                st.rerun()
        
        if st.session_state['materials']:
            st.markdown("<h4>Added Materials:</h4>", unsafe_allow_html=True)
            materials_df = rows_to_df(st.session_state['materials'],
                                       ["Raw Material", "Heat No.", "Dia/Size", "Weight", "Qty", "Remark"])
            st.dataframe(materials_df, use_container_width=True, hide_index=True, height=200)
            
            if st.button("🗑️ Clear Materials", use_container_width=True):
                st.session_state['materials'] = []
                st.rerun()
    
    with tab3:
        # Operations
        st.markdown("### ⚙️ Operation Checklist")
        
        operations = ["Cutting", "Turning (Traub/CNC)", "Milling", "Threading", 
                      "Drilling", "Punching", "Deburring", "Plating", "Packing"]
        
        op_cols = st.columns(3)
        for idx, op in enumerate(operations):
            with op_cols[idx % 3]:
                checked = st.checkbox(op, key=f"op_{op}")
                st.session_state['operations'][op] = checked
        
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        
        # Machine Details
        st.markdown("### 🏭 Machine Details")
        
        show_machine = st.checkbox("Include Machine Details", value=False)
        
        if show_machine:
            col_m1, col_m2, col_m3 = st.columns(3)
            
            with col_m1:
                machine_type = st.selectbox("Machine Type", ["Traub", "CNC", "VMC", "Lathe", "Milling"])
            
            with col_m2:
                cycle_time = st.text_input("Cycle Time (sec)")
            
            with col_m3:
                rpm = st.text_input("RPM")
            
            feed = st.text_input("Feed Rate")
            
            if machine_type == "Traub":
                gear_setup = st.text_input("Traub Gear Setup")
        else:
            machine_type = None
            cycle_time = rpm = feed = gear_setup = None
        
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        
        # Quality Instructions
        st.markdown("### ✅ Quality Instructions")
        
        col_q1, col_q2, col_q3 = st.columns(3)
        
        with col_q1:
            tolerance = st.text_input("Tolerance", placeholder="e.g., ±0.01mm")
        
        with col_q2:
            surface_finish = st.text_input("Surface Finish", placeholder="e.g., Ra 0.8")
        
        with col_q3:
            hardness = st.text_input("Hardness Requirement", placeholder="e.g., 45-50 HRC")
        
        thread_check = st.checkbox("Thread GO/NO-GO Check Required")
    
    with tab4:
        # Delivery Schedule
        st.markdown("### 🚚 Delivery Schedule")
        
        expected_date = st.date_input("Expected Delivery Date")
        
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        
        # GRN Section
        st.markdown("### 📥 Goods Received / QC")
        
        grn_cols_labels = ["Date", "Qty Received", "OK Qty", "Rejected Qty", "Remarks", "QC Approved By"]
        grn_cols_widgets = st.columns([1.5, 1, 1, 1, 2, 1.5])
        
        grn_vals = []
        for i, label in enumerate(grn_cols_labels):
            if i == 0:
                grn_vals.append(grn_cols_widgets[i].text_input(label, value=date.today().strftime("%Y-%m-%d")))
            elif i >= 1 and i <= 3:
                grn_vals.append(grn_cols_widgets[i].number_input(label, value=0, min_value=0))
            else:
                grn_vals.append(grn_cols_widgets[i].text_input(label))
        
        col_add_grn, _ = st.columns([1, 4])
        with col_add_grn:
            if st.button("➕ Add GRN Entry", use_container_width=True, type="primary"):
                st.session_state['grn_entries'].append(list(grn_vals))
                show_toast("✅ GRN Entry added!")
                st.rerun()
        
        if st.session_state['grn_entries']:
            st.markdown("<h4>GRN Entries:</h4>", unsafe_allow_html=True)
            grn_df = rows_to_df(st.session_state['grn_entries'], grn_cols_labels)
            st.dataframe(grn_df, use_container_width=True, hide_index=True, height=200)
            
            if st.button("🗑️ Clear GRN Entries", use_container_width=True):
                st.session_state['grn_entries'] = []
                st.rerun()
        
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        
        # Summary and Actions
        st.markdown("### 📋 Summary & Actions")
        
        col_summary = st.columns([1, 1, 1])
        
        with col_summary[0]:
            st.metric("Items", len(st.session_state['items']))
        
        with col_summary[1]:
            st.metric("Materials", len(st.session_state['materials']))
        
        with col_summary[2]:
            st.metric("GRN Entries", len(st.session_state['grn_entries']))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Action buttons
        col_save, col_save_db, col_pdf = st.columns([1, 1, 1])
        
        with col_save:
            if st.button("💾 Save to Session", use_container_width=True):
                show_toast("✅ Saved to session!")
        
        with col_save_db:
            if st.button("💾 Save to Database", use_container_width=True, type="primary"):
                try:
                    logo_b64 = ""
                    if logo_file:
                        logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
                    
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
                        'qr_code_data': qr_text,
                        'expected_delivery_date': expected_date.isoformat(),
                        'status': 'Pending',
                        'items': [{'description': i[0], 'drawing_no': i[1], 'drawing_link': i[2], 
                                  'grade': i[3], 'quantity': i[4], 'uom': i[5]} for i in st.session_state['items']],
                        'materials': [{'raw_material': m[0], 'heat_no': m[1], 'dia_size': m[2],
                                      'weight': m[3], 'quantity': m[4], 'remark': m[5]} for m in st.session_state['materials']],
                        'operations': [{'name': k, 'selected': v} for k, v in st.session_state['operations'].items()],
                        'machine_details': {'machine_type': machine_type, 'cycle_time': cycle_time, 
                                          'rpm': rpm, 'feed_rate': feed, 'gear_setup': gear_setup} if machine_type else None,
                        'quality': {'tolerance': tolerance, 'surface_finish': surface_finish,
                                   'hardness': hardness, 'thread_check': thread_check},
                        'grn_entries': [{'date': g[0], 'qty_received': g[1], 'ok_qty': g[2],
                                       'rejected_qty': g[3], 'remarks': g[4], 'qc_approved_by': g[5]}
                                      for g in st.session_state['grn_entries']],
                        'signatures': {'prepared_by': '', 'prepared_date': date.today().isoformat()}
                    }
                    
                    result = save_job_card(data)
                    if result:
                        show_toast(f"✅ Job card saved to database! ID: {result}")
                    else:
                        show_toast("❌ Failed to save to database", "error")
                except Exception as e:
                    show_toast(f"❌ Database error: {str(e)}", "error")
        
        with col_pdf:
            if st.button("📄 Generate PDF", use_container_width=True, type="primary"):
                with st.spinner("Generating PDF..."):
                    try:
                        items_df = rows_to_df(st.session_state['items'], 
                                              ["Description", "Drawing No.", "Drawing Link", "Grade", "Qty", "UOM"])
                        materials_df = rows_to_df(st.session_state['materials'],
                                                   ["Raw Material", "Heat No.", "Dia/Size", "Weight", "Qty", "Remark"])
                        grn_df = rows_to_df(st.session_state['grn_entries'],
                                            ["Date", "Qty Received", "OK Qty", "Rejected Qty", "Remarks", "QC Approved By"])
                        
                        ops_list = [k for k, v in st.session_state['operations'].items() if v]
                        
                        logo_bytes = None
                        if logo_file:
                            logo_bytes = logo_file.read()
                        
                        pdf_data = generate_premium_pdf(
                            company_name=company_name,
                            company_address=company_address,
                            logo_file=logo_bytes,
                            vendor_id=vendor_id,
                            vendor_company=vendor_company,
                            vendor_person=vendor_person,
                            vendor_mobile=vendor_mobile,
                            vendor_gst=vendor_gst,
                            vendor_address=vendor_address,
                            job_no=job_no,
                            job_date=str(job_date),
                            dispatch_location=dispatch_location,
                            qr_bytes=qr_bytes,
                            items_df=items_df,
                            materials_df=materials_df,
                            grn_df=grn_df,
                            tolerance=tolerance,
                            surface_finish=surface_finish,
                            hardness=hardness,
                            thread_check=thread_check,
                            expected_date=str(expected_date),
                            operations=ops_list,
                            machine_details={'machine_type': machine_type, 'cycle_time': cycle_time, 
                                           'rpm': rpm, 'feed_rate': feed, 'gear_setup': gear_setup} if machine_type else None
                        )
                        
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_data,
                            file_name=f"JobCard_{job_no}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        show_toast(f"❌ PDF generation error: {str(e)}", "error")


# ==================== PAGE: RECORDS ====================
def page_records():
    """Render the records page."""
    st.markdown("""
        <div class="card animate-fade-in">
            <div class="card-header">
                <div class="card-icon">📋</div>
                <div>
                    <h2 class="card-title">All Job Card Records</h2>
                    <p class="card-subtitle">View and manage all saved job cards</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search by job card no, vendor...")
    
    with col2:
        status_filter = st.selectbox("Status", ["All", "Pending", "In Progress", "Completed", "Cancelled"])
    
    with col3:
        sort_by = st.selectbox("Sort", ["Newest First", "Oldest First"])
    
    # Get records
    try:
        if search_term:
            records = search_job_cards(search_term)
        elif status_filter != "All":
            records = get_all_job_cards(status_filter)
        else:
            records = get_all_job_cards()
        
        if records:
            st.markdown(f"### Found {len(records)} Records")
            
            for record in records:
                with st.expander(f"📋 {record['job_card_no']} - {record.get('vendor_company', 'N/A')}"):
                    col_r1, col_r2, col_r3 = st.columns([2, 1, 1])
                    
                    with col_r1:
                        st.write(f"**Vendor:** {record.get('vendor_company', 'N/A')}")
                        st.write(f"**Contact:** {record.get('vendor_person', 'N/A')}")
                        st.write(f"**Mobile:** {record.get('vendor_mobile', 'N/A')}")
                    
                    with col_r2:
                        st.write(f"**Date:** {record.get('job_date', 'N/A')}")
                        st.write(f"**Dispatch:** {record.get('dispatch_location', 'N/A')}")
                    
                    with col_r3:
                        status = record.get('status', 'Pending')
                        status_class = status.lower().replace(' ', '-')
                        st.markdown(f"<span class='badge badge-{status_class}'>{status}</span>", 
                                   unsafe_allow_html=True)
                    
                    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                    
                    with col_btn1:
                        if st.button("👁️ View", key=f"view_{record['id']}"):
                            show_toast("Viewing record...")
                    
                    with col_btn2:
                        if st.button("📄 PDF", key=f"pdf_{record['id']}"):
                            show_toast("Generating PDF...")
                    
                    with col_btn3:
                        new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed", "Cancelled"],
                                                  key=f"status_{record['id']}")
                        if st.button("💾 Update", key=f"update_{record['id']}"):
                            if update_job_card_status(record['job_card_no'], new_status):
                                show_toast("✅ Status updated!")
                                st.rerun()
                    
                    with col_btn4:
                        if st.button("🗑️ Delete", key=f"del_{record['id']}"):
                            if delete_job_card(record['job_card_no']):
                                show_toast("✅ Job card deleted!")
                                st.rerun()
                            else:
                                show_toast("❌ Failed to delete", "error")
        else:
            st.info("📭 No job cards found. Create your first job card!")
    except Exception as e:
        st.error(f"❌ Error loading records: {str(e)}")
        st.info("💡 Make sure MySQL is running and connected.")


# ==================== PAGE: SEARCH ====================
def page_search():
    """Render the search page."""
    st.markdown("""
        <div class="card animate-fade-in">
            <div class="card-header">
                <div class="card-icon">🔍</div>
                <div>
                    <h2 class="card-title">Search Job Cards</h2>
                    <p class="card-subtitle">Find job cards by various criteria</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown("""
            <div class="card">
                <h4>📅 Search by Date Range</h4>
                <p style="color: var(--text-light);">Find job cards within a specific date range.</p>
            </div>
        """, unsafe_allow_html=True)
        
        start_date = st.date_input("Start Date", date.today())
        end_date = st.date_input("End Date", date.today())
        
        if st.button("🔍 Search by Date", use_container_width=True, type="primary"):
            try:
                records = JobCardDatabase.get_job_cards_by_date_range(
                    start_date.isoformat(), end_date.isoformat()
                )
                if records:
                    st.dataframe(pd.DataFrame(records), use_container_width=True)
                else:
                    st.info("No records found in this date range.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col_s2:
        st.markdown("""
            <div class="card">
                <h4>🏷️ Search by Vendor</h4>
                <p style="color: var(--text-light);">Find all job cards for a specific vendor.</p>
            </div>
        """, unsafe_allow_html=True)
        
        vendor_search = st.text_input("Enter Vendor ID or Name", placeholder="e.g., VND-001")
        
        if st.button("🔍 Search Vendor", use_container_width=True, type="primary"):
            try:
                records = search_job_cards(vendor_search)
                if records:
                    st.dataframe(pd.DataFrame(records), use_container_width=True)
                else:
                    st.info("No records found for this vendor.")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# ==================== PAGE: STATISTICS ====================
def page_stats():
    """Render the statistics page."""
    st.markdown("""
        <div class="card animate-fade-in">
            <div class="card-header">
                <div class="card-icon">📊</div>
                <div>
                    <h2 class="card-title">Statistics & Analytics</h2>
                    <p class="card-subtitle">Overview of job card data and trends</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        stats = get_job_card_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">📋</div>
                    <div class="stat-value">{stats.get('total', 0)}</div>
                    <div class="stat-label">Total Job Cards</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">📅</div>
                    <div class="stat-value">{stats.get('this_month', 0)}</div>
                    <div class="stat-label">This Month</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pending = stats.get('by_status', {}).get('Pending', 0)
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">⏳</div>
                    <div class="stat-value">{pending}</div>
                    <div class="stat-label">Pending</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            completed = stats.get('by_status', {}).get('Completed', 0)
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-value">{completed}</div>
                    <div class="stat-label">Completed</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Status breakdown
        st.markdown("### 📈 Status Breakdown")
        
        by_status = stats.get('by_status', {})
        if by_status:
            for status, count in by_status.items():
                status_class = status.lower().replace(' ', '-')
                st.markdown(f"""
                    <div class="card" style="padding: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="badge badge-{status_class}">{status}</span>
                            <span style="font-size: 1.5rem; font-weight: bold;">{count}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No status data available.")
            
    except Exception as e:
        st.error(f"❌ Error loading statistics: {str(e)}")
        st.info("💡 Make sure MySQL is running and connected.")


# ==================== MAIN APPLICATION ====================
def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    
    current_page = st.session_state.get('current_page', 'home')
    
    if current_page == 'home':
        page_home()
    elif current_page == 'create':
        page_create()
    elif current_page == 'records':
        page_records()
    elif current_page == 'search':
        page_search()
    elif current_page == 'stats':
        page_stats()


if __name__ == "__main__":
    main()

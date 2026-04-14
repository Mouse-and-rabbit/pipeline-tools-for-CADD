import streamlit as st
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from streamlit_lottie import st_lottie
from Bio.PDB import PDBParser, PPBuilder, PDBList
from Bio.SeqUtils import ProtParam
from docx import Document
from docx.shared import Inches, RGBColor
from streamlit_molstar import st_molstar

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Enzyme Optimization Hub", layout="wide", page_icon="🧬")

# Function to load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# High-quality Lab Animations
lottie_scanning = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_m6cu9zoc.json")
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_6lim7atv.json")

# Custom CSS for a "Vibrant Lab" look
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .main-header { 
        font-size: 32px; font-weight: 800; 
        background: linear-gradient(90deg, #1E3A8A, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        border-bottom: 3px solid #00d4ff; padding-bottom: 10px; margin-bottom: 20px;
    }
    .stButton>button { 
        border-radius: 12px; font-weight: bold; height: 3.5em; 
        background: white; border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        border: 2px solid #00d4ff; color: #00d4ff; 
        transform: translateY(-2px); box-shadow: 0px 4px 15px rgba(0, 212, 255, 0.3);
    }
    .sidebar-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. REPORT GENERATOR (Unchanged) ---
def create_prof_report(title, methodology, formulas, df, plot_buf=None):
    doc = Document()
    header = doc.add_heading(title, 0)
    header.runs[0].font.color.rgb = RGBColor(30, 58, 170)
    # ... (Same internal logic as your current working function)
    doc.add_heading('Methodology', level=1)
    doc.add_paragraph(methodology)
    if formulas:
        doc.add_heading('Mathematical Basis', level=2)
        for f in formulas: doc.add_paragraph(f, style='Quote')
    doc.add_heading('Results', level=1)
    table = doc.add_table(df.shape[0] + 1, df.shape[1])
    table.style = 'Table Grid'
    for j, col in enumerate(df.columns): table.cell(0, j).text = str(col)
    for i, row in enumerate(df.values):
        for j, val in enumerate(row): table.cell(i + 1, j).text = str(val)
    if plot_buf:
        doc.add_heading('Visualization', level=1)
        doc.add_picture(plot_buf, width=Inches(5))
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 3. UI LAYOUT ---
if 'active_file' not in st.session_state: st.session_state.active_file = None
if 'active_name' not in st.session_state: st.session_state.active_name = "Target_Enzyme"

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.markdown('<p class="main-header">🧬 Research Input</p>', unsafe_allow_html=True)
    
    with st.container():
        # Ensure this line is exactly like this:
        input_mode = st.radio("Select Analysis Protocol", ["Upload PDB", "enter PDB ID"])
        
        if input_mode == "Upload PDB":
            uploaded_file = st.file_uploader("Drop PDB File Here", type=['pdb'])
            # ... rest of the code

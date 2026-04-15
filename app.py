import streamlit as st
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from streamlit_lottie import st_lottie
from Bio.PDB import PDBParser, PPBuilder, PDBList, SASA
from Bio.SeqUtils import ProtParam
from docx import Document
from docx.shared import Inches, RGBColor
from streamlit_molstar import st_molstar
from matplotlib.patches import RegularPolygon

# --- 1. SCHRÖDINGER-INSPIRED CONFIG ---
st.set_page_config(page_title="BioMumo | Enzyme Optimization Hub", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .hero-text { text-align: center; padding: 20px 0px; background: linear-gradient(180deg, #0b0f19 0%, #161e2d 100%); }
    .main-title { font-family: 'Inter', sans-serif; font-size: 40px; font-weight: 800; background: linear-gradient(90deg, #00d4ff, #ffffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
    .sub-title { font-size: 14px; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase; }
    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff; font-weight: 600; height: 3em; text-transform: uppercase; }
    .stButton>button:hover { background-color: #00d4ff; color: #0b0f19; box-shadow: 0 0 15px rgba(0, 212, 255, 0.4); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #0f172a; border-radius: 4px; color: #94a3b8; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #00d4ff !important; border-bottom-color: #00d4ff !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE UTILITIES ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_scan = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_m6cu9zoc.json")

def create_prof_report(title, methodology, formulas, df, plot_buf=None):
    doc = Document()
    header = doc.add_heading(title, 0)
    header.runs[0].font.color.rgb = RGBColor(30, 58, 170)
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

# --- 3. LOGO GENERATOR (STRETCHED HORIZONTAL DESIGN) ---
def generate_biomumo_logo():
    # Increased width (16) and decreased height (3) for a sleek banner look
    fig, ax = plt.subplots(figsize=(16, 2.5), facecolor='#0b0f19')
    ax.set_facecolor('#0b0f19')
    ax.set_xlim(-6, 25)
    ax.set_ylim(-4, 4)
    ax.axis('off')
    
    chem_color, accent_color = '#ffffff', '#00d4ff'
    
    # Compressed Polycyclic structure (4 rings in a row to save height)
    ring_centers = [(-3.0, 0), (-0.5, 0), (2.0, 0), (4.5, 0)]
    letters = ["M", "U", "M", "O"]
    
    for center, letter in zip(ring_centers, letters):
        ring = RegularPolygon(center, numVertices=6, radius=1.3, orientation=0, 
                              edgecolor=chem_color, facecolor='none', lw=2)
        ax.add_patch(ring)
        ax.text(center[0], center[1], letter, color=accent_color, fontsize=18, 
                fontweight='black', ha='center', va='center')
    
    # Side chain detail
    ax.plot([4.5, 5.5, 6.5], [-1.1, -1.8, -1.1], color=chem_color, lw=2)
    
    # Horizontal Branding Text
    ax.text(8, 0.4, "MUMO CORE", color='#ffffff', fontsize=55, fontweight='black')
    ax.text(8, -1.2, "INTEGRATED PIPELINE ECOSYSTEM | VINAYAKA MISSION'S COLLEGE OF PHARMACY", 
            color='#94a3b8', fontsize=14, fontweight='bold', letterspacing=1)
    
    return fig

# --- 4. RENDER LOGO ---
plt.close('all') 
logo_fig = generate_biomumo_logo()
logo_buf = io.BytesIO()
logo_fig.savefig(logo_buf, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True)
logo_buf.seek(0)

st.image(logo_buf, use

import streamlit as st
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from matplotlib.patches import RegularPolygon
from Bio.PDB import PDBParser, PPBuilder, PDBList, SASA
from Bio.SeqUtils import ProtParam
from docx import Document
from docx.shared import Inches, RGBColor
from streamlit_molstar import st_molstar

# --- 1. CONFIG & REFINED STYLING ---
st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    .main-title { color: #00d4ff; font-weight: 800; text-align: center; }
    .pipeline-title { color: #ffffff; font-weight: 600; font-size: 20px; text-align: center; margin-bottom: 10px; }
    .info-box { background-color: rgba(0, 212, 255, 0.1); border-left: 5px solid #00d4ff; padding: 15px; border-radius: 5px; margin: 10px 0; }
    .benzene-container { display: flex; flex-direction: column; align-items: center; padding: 10px; }
    .hexagon {
        width: 180px; height: 210px;
        background: rgba(0, 212, 255, 0.05);
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex; align-items: center; justify-content: center;
        border: 1px solid #00d4ff; 
        transition: 0.3s;
    }
    .hexagon img { width: 150px; height: 150px; object-fit: cover; }
    
    /* Button Customization */
    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff; font-weight: 600; }
    .stButton>button:hover { background-color: #00d4ff !important; color: #0b0f19 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE UTILITIES ---
def create_prof_report(title, methodology, df):
    doc = Document()
    header = doc.add_heading(title, 0)
    header.runs[0].font.color.rgb = RGBColor(30, 58, 170)
    doc.add_heading('Methodology', level=1)
    doc.add_paragraph(methodology)
    doc.add_heading('Results', level=1)
    table = doc.add_table(df.shape[0] + 1, df.shape[1])
    table.style = 'Table Grid'
    for j, col in enumerate(df.columns): table.cell(0, j).text = str(col)
    for i, row in enumerate(df.values):
        for j, val in enumerate(row): table.cell(i + 1, j).text = str(val)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def generate_momu_sketch_logo():
    fig, ax = plt.subplots(figsize=(12, 3), facecolor='#0b0f19')
    ax.set_facecolor('#0b0f19')
    ax.set_xlim(-6, 25)
    ax.set_ylim(-5, 5)
    ax.axis('off')
    
    # Diamond Cluster Coordinates for U-M-M-O
    coords = [(0, 2.2), (-1.9, 0), (1.9, 0), (0, -2.2)]
    labels = ["U", "M", "M", "O"]
    accent_color = '#00d4ff'
    
    for (x, y), label in zip(coords, labels):
        ring = RegularPolygon((x, y), numVertices=6, radius=1.3, orientation=0, 
                              edgecolor='#ffffff', facecolor='none', lw=1.2)
        ax.add_patch(ring)
        ax.text(x, y, label, color=accent_color, fontsize=15, fontweight='bold', ha='center', va='center')

    # Add Free Radical Dot
    ax.plot(1.1, -2.9, marker='o', markersize=6, color=accent_color) 
    
    # Text Branding
    ax.text(5.5, 0.8, "MOMU", color='#ffffff', fontsize=42, fontweight='black')
    ax.text(5.5, -0.6, "THE INTEGRATED MOLECULAR ANALYZING PIPELINE", color='#94a3b8', fontsize=12, fontweight='bold')
    
    return fig

# --- 3. SESSION STATE ---
if "show_desc" not in st.session_state:
    st.session_state.show_desc = {"p1": False, "p2": False, "p3": False}
if "active_file" not in

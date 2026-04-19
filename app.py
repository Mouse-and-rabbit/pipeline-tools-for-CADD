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
from matplotlib.patches import RegularPolygon

# --- 1. CONFIG & SCHRÖDINGER-INSPIRED STYLING ---
# --- 1. CONFIG & REFINED STYLING ---
st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")

st.markdown("""
@@ -23,10 +20,12 @@
    .benzene-container { display: flex; flex-direction: column; align-items: center; padding: 10px; }
    .hexagon {
        width: 180px; height: 210px;
        background: linear-gradient(45deg, #00d4ff, #005f73);
        background: rgba(0, 212, 255, 0.05);
        /* Thinner border style */
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex; align-items: center; justify-content: center;
        border: 2px solid #ffffff;
        border: 1px solid #00d4ff; 
        transition: 0.3s;
    }
    .hexagon img {
        width: 150px; height: 150px;
@@ -38,39 +37,36 @@
    
    /* Button Customization */
    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff; font-weight: 600; }
    .stButton>button:hover { background-color: #00d4ff; color: #0b0f19; }
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

def generate_biomumo_logo():
    fig, ax = plt.subplots(figsize=(18, 2.0), facecolor='#0b0f19')
# --- 2. EXACT LOGO GENERATOR (From User Sketch) ---
def generate_momu_sketch_logo():
    fig, ax = plt.subplots(figsize=(10, 3), facecolor='#0b0f19')
    ax.set_facecolor('#0b0f19')
    ax.set_xlim(-8, 28); ax.set_ylim(-4, 4); ax.axis('off')
    chem_color, accent_color = '#ffffff', '#00d4ff'
    ring_centers = [(-4, 0), (-1, 0), (2, 0), (5, 0)]
    letters = ["M", "U", "M", "O"]
    for center, letter in zip(ring_centers, letters):
        ring = RegularPolygon(center, numVertices=6, radius=1.3, orientation=0, edgecolor=chem_color, facecolor='none', lw=2)
    ax.set_xlim(-6, 18); ax.set_ylim(-5, 5); ax.axis('off')
    
    # Diamond Cluster Coordinates for U-M-M-O
    # Top, Left, Right, Bottom
    coords = [(0, 2.2), (-1.9, 0), (1.9, 0), (0, -2.2)]
    labels = ["U", "M", "M", "O"]
    
    # Draw Ring Cluster
    for (x, y), label in zip(coords, labels):
        # Thinner line width (lw=1) as requested
        ring = RegularPolygon((x, y), numVertices=6, radius=1.3, orientation=0, 
                              edgecolor='#ffffff', facecolor='none', lw=1.2)
        ax.add_patch(ring)
        ax.text(center[0], center[1], letter, color=accent_color, fontsize=16, fontweight='black', ha='center', va='center')
    ax.text(11, 0.5, "MUMO CORE", color='#ffffff', fontsize=48, fontweight='black')
        ax.text(x, y, label, color='#00d4ff', fontsize=15, fontweight='bold', ha='center', va='center')

    # Add Free Radical Dot (at the bottom right vertex of the cluster)
    ax.plot(1.1, -2.9, marker='o', markersize=6, color="#00d4ff") 
    
    # Text Branding (MOMU - The integrated molecular Analyzing pipeline)
    ax.text(5.5, 0.8, "MOMU", color='#ffffff', fontsize=42, fontweight='black')
    ax.text(5.5, -0.6, "THE INTEGRATED MOLECULAR ANALYZING PIPELINE", color='#94a3b8', fontsize=12, fontweight='bold')
    
    return fig

# --- 3. SESSION STATE ---
@@ -80,11 +76,11 @@
    st.session_state.active_file = None

# --- 4. RENDER UI ---
st.pyplot(generate_biomumo_logo())
st.pyplot(generate_momu_sketch_logo())
tabs = st.tabs(["🏠 HOME / PIPELINE", "📜 DESCRIPTIONS", "👥 ABOUT US", "📚 REFERENCES", "📧 CONTACT"])

with tabs[0]:
    st.markdown('<h1 class="main-title">BioMumo: Molecular Discovery Pipeline</h1>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">BioMumo: Molecular Discovery Platform</h1>', unsafe_allow_html=True)

    # Target Selection
    col_in, col_viz = st.columns([1, 2])
@@ -116,11 +112,13 @@
    # --- PIPELINE GRID ---
    c1, c2, c3 = st.columns(3)

    # PIPELINE 1
    # PIPELINE 1: Protein Analysis
    with c1:
        st.markdown('<p class="pipeline-title">Protein Analysis</p>', unsafe_allow_html=True)
        st.markdown('<div class="benzene-container"><div class="hexagon"><img src="https://rcsb.org/pdb/images/3fxi_asym_r_500.jpg"></div></div>', unsafe_allow_html=True)
        if st.button("Click Here", key="btn1"): st.session_state.show_desc["p1"] = not st.session_state.show_desc["p1"]
        if st.button("Click Here", key="btn1"): 
            st.session_state.show_desc["p1"] = not st.session_state.show_desc["p1"]
        
        if st.session_state.show_desc["p1"]:
            st.markdown('<div class="info-box">1. Extracts sequence data.<br>2. Calculates MW (kDa).<br>3. Computes pI.<br>4. Measures Instability Index.<br>5. Evaluates hydrophobicity.</div>', unsafe_allow_html=True)
            if st.button("▶ Run Protein Analysis") and st.session_state.active_file:
@@ -132,11 +130,13 @@
                df = pd.DataFrame({'Parameter': ['MW', 'pI', 'Instability'], 'Value': [f"{ana.molecular_weight()/1000:.2f} kDa", f"{ana.isoelectric_point():.2f}", f"{ana.instability_index():.2f}"]})
                st.table(df)

    # PIPELINE 2
    # PIPELINE 2: Active Site Prediction
    with c2:
        st.markdown('<p class="pipeline-title">Active Site Prediction</p>', unsafe_allow_html=True)
        st.markdown('<div class="benzene-container"><div class="hexagon"><img src="https://cdn.rcsb.org/images/structures/8/8m5s/8m5s_assembly-1.jpeg"></div></div>', unsafe_allow_html=True)
        if st.button("Click Here", key="btn2"): st.session_state.show_desc["p2"] = not st.session_state.show_desc["p2"]
        if st.button("Click Here", key="btn2"): 
            st.session_state.show_desc["p2"] = not st.session_state.show_desc["p2"]
        
        if st.session_state.show_desc["p2"]:
            st.markdown('<div class="info-box">1. Computes SASA.<br>2. Identifies pocket residues.<br>3. Ranks by exposure.<br>4. Predicts binding affinity.<br>5. Maps catalytic sites.</div>', unsafe_allow_html=True)
            if st.button("▶ Run Site Mapping") and st.session_state.active_file:
@@ -147,11 +147,13 @@
                sites = [{'Residue': f"{res.get_resname()}{res.id[1]}", 'SASA': round(res.sasa, 2)} for res in structure.get_residues() if hasattr(res, 'sasa')]
                st.dataframe(pd.DataFrame(sites).nlargest(10, 'SASA'), use_container_width=True)

    # PIPELINE 3
    # PIPELINE 3: Mutation Prediction
    with c3:
        st.markdown('<p class="pipeline-title">Mutation Prediction</p>', unsafe_allow_html=True)
        st.markdown('<div class="benzene-container"><div class="hexagon"><img src="https://cdn.rcsb.org/images/structures/1/1aie/1aie_assembly-1.jpeg"></div></div>', unsafe_allow_html=True)
        if st.button("Click Here", key="btn3"): st.session_state.show_desc["p3"] = not st.session_state.show_desc["p3"]
        if st.button("Click Here", key="btn3"): 
            st.session_state.show_desc["p3"] = not st.session_state.show_desc["p3"]
        
        if st.session_state.show_desc["p3"]:
            st.markdown('<div class="info-box">1. Analyzes B-factors.<br>2. Finds flexible regions.<br>3. Predicts mutation impact.<br>4. Suggests substitutions.<br>5. Heatmap visualization.</div>', unsafe_allow_html=True)
            if st.button("▶ Run Mutation Analysis") and st.session_state.active_file:
@@ -161,18 +163,18 @@
                df_mut = pd.DataFrame(res_data).groupby('Pos').mean().reset_index()
                st.line_chart(df_mut.set_index('Pos')['B'])

# --- RE-ADDING ORIGINAL DESCRIPTIONS TAB ---
# --- (REMAINING TABS KEPT FOR COMPLETENESS) ---
with tabs[1]:
    st.markdown('<h2 class="main-title">Methodology & Mathematical Basis</h2>', unsafe_allow_html=True)
    st.info("**Isoelectric Point (pI):** $pI = (pK_i + pK_j)/2$. Determines pH where the enzyme has no net charge.")
    st.info("**B-factor Analysis:** Represents thermal displacement. High B-factors = High flexibility.")
    st.info("**Isoelectric Point (pI):** $pI = (pK_i + pK_j)/2$.")
    st.info("**B-factor Analysis:** Represents thermal displacement.")

with tabs[2]:
    st.write("### Vinayaka Mission's College of Pharmacy")
    st.write("Developed by Mowriss.M.G & Mugilarasi.C. Bridging Pharmacy with Computational Proteomics.")
    st.write("Developed by Mowriss.M.G & Mugilarasi.C.")

with tabs[3]:
    st.write("1. Biopython: Bioinformatics tools. 2. ExPASy ProtParam algorithm. 3. AlphaFold 3 (Reference).")
    st.write("1. Biopython tools. 2. ExPASy ProtParam. 3. AlphaFold 3.")

with tabs[4]:
    st.write("Contact: Mowriss.M.G & Mugilarasi.C | VMCP Research Scholars.")

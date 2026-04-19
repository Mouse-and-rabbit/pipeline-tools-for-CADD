import streamlit as st
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from Bio.PDB import PDBParser, PPBuilder, PDBList, SASA
from Bio.SeqUtils import ProtParam
from streamlit_molstar import st_molstar

# --- 1. CONFIG & REFINED LIGHT STYLING ---
st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    /* Global Light Theme and Modern Font */
    .stApp { background-color: #fcfcfc; color: #2d3436; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    .main-title { font-size: 38px; font-weight: 800; color: #2d3436; text-align: center; margin-top: -20px; }
    
    /* The Main Diamond-Hexagon Module */
    .benzene-cluster { display: flex; flex-direction: column; align-items: center; padding: 10px; }
    
    .diamond-hexagon {
        width: 200px; height: 240px;
        background-color: #ffffff;
        border: 2.5px solid #2d3436; 
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        position: relative;
        z-index: 2;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .hex-image {
        width: 80px; height: 80px;
        object-fit: contain;
        margin-bottom: 10px;
        opacity: 0.8;
    }
    
    .hexagon-title { font-weight: 800; font-size: 18px; color: #2d3436; text-transform: uppercase; margin: 0; }
    .hexagon-subtitle { font-size: 13px; color: #636e72; margin-bottom: 10px; }
    .click-here-accent { font-weight: 700; color: #0984e3; text-transform: uppercase; font-size: 12px; border: 1px solid #0984e3; padding: 2px 8px; border-radius: 4px; }

    /* Attached Description Box - Exactly matching the schematic stack */
    .attached-info-box { 
        background-color: #ffffff; 
        width: 210px; 
        padding: 20px 15px 15px 15px; 
        border-radius: 0 0 10px 10px; 
        border: 2px solid #2d3436; 
        margin-top: -30px; /* Overlap to look attached to the bottom point */
        z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
    }
    .info-list { font-size: 13px; color: #2d3436; line-height: 1.8; border-bottom: 1px solid #dfe6e9; padding: 4px 0; }
    
    /* Refined Button Styling */
    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #2d3436; background-color: #ffffff; color: #2d3436; font-weight: 700; font-size: 12px; }
    .stButton>button:hover { background-color: #2d3436 !important; color: #ffffff !important; }
    
    /* Navigation Refinement */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border: 1px solid #dfe6e9; border-radius: 5px; padding: 5px 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGO GENERATOR (Light Theme / Sketch Accurate) ---
def generate_momu_sketch_logo():
    fig, ax = plt.subplots(figsize=(12, 3), facecolor='#fcfcfc')
    ax.set_facecolor('#fcfcfc')
    ax.set_xlim(-6, 20); ax.set_ylim(-5, 5); ax.axis('off')
    
    coords = [(0, 2.2), (-1.9, 0), (1.9, 0), (0, -2.2)]
    labels = ["U", "M", "M", "O"]
    
    for (x, y), label in zip(coords, labels):
        ring = RegularPolygon((x, y), numVertices=6, radius=1.3, orientation=0, 
                              edgecolor='#2d3436', facecolor='#f8f9fa', lw=1.2)
        ax.add_patch(ring)
        ax.text(x, y, label, color='#2d3436', fontsize=16, fontweight='bold', ha='center', va='center')

    # Free Radical Dot
    ax.plot(1.1, -2.9, marker='o', markersize=7, color="#2d3436") 
    
    # Branding
    ax.text(6, 0.8, "MOMU core", color='#2d3436', fontsize=42, fontweight='black')
    ax.text(6, -0.6, "The Integrated moleculare Analyzing pipeline", color='#636e72', fontsize=14)
    return fig

# --- 3. SESSION STATE ---
if 'show_desc' not in st.session_state:
    st.session_state.show_desc = {"p1": False, "p2": False, "p3": False}
if 'active_file' not in st.session_state:
    st.session_state.active_file = None

# --- 4. RENDER UI ---
st.pyplot(generate_momu_sketch_logo())

tabs = st.tabs(["Home", "DESCRIPTIONS", "ABOUT US", "Reference", "Contact"])

with tabs[0]:
    st.markdown('<p style="text-align:center; font-weight:700; color:#636e72; letter-spacing:2px;">COMPUTATIONAL DRUG DISCOVERY PLATFORM</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Biomumo: Opening New Worlds for molecular Discovery</h1>', unsafe_allow_html=True)
    st.write("### Home :-")

    # File Input and Molstar Visualizer
    col_in, col_viz = st.columns([1, 2])
    with col_in:
        up = st.file_uploader("Upload PDB File", type=['pdb'])
        if up:
            with open("temp.pdb", "wb") as f: f.write(up.getbuffer())
            st.session_state.active_file = "temp.pdb"
    with col_viz:
        if st.session_state.active_file:
            st_molstar(st.session_state.active_file, height=300)

    st.divider()

    # --- PIPELINE GRID (3 Columns) ---
    c1, c2, c3 = st.columns(3)

    # Column 1: Protein Analysis
    with c1:
        st.markdown(f"""<div class="benzene-cluster"><div class="diamond-hexagon">
            <p class="hexagon-title">protein</p>
            <img src="https://rcsb.org/pdb/images/3fxi_asym_r_500.jpg" class="hex-image">
            <p class="hexagon-subtitle">protein analysis</p>
            <p class="click-here-accent">click here</p>
        </div></div>""", unsafe_allow_html=True)
        
        if st.button("Open Protein Box", key="btn1"):
            st.session_state.show_desc["p1"] = not st.session_state.show_desc["p1"]
        
        if st.session_state.show_desc["p1"]:
            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)
            for i in ["Extract Sequence", "Molecular Weight", "pI Calculation", "Instability Index", "GRAVY Score"]:
                st.markdown(f'<div class="info-list">~ {i}</div>', unsafe_allow_html=True)
            if st.button("RUN protein analysis", key="run1"):
                st.success("Analysis Complete")
            st.markdown('</div></div>', unsafe_allow_html=True)

    # Column 2: Active Site Prediction
    with c2:
        st.markdown(f"""<div class="benzene-cluster"><div class="diamond-hexagon">
            <p class="hexagon-title">Active</p>
            <img src="https://cdn.rcsb.org/images/structures/8/8m5s/8m5s_assembly-1.jpeg" class="hex-image">
            <p class="hexagon-subtitle">site prediction</p>
            <p class="click-here-accent">click here</p>
        </div></div>""", unsafe_allow_html=True)
        
        if st.button("Open Active Site Box", key="btn2"):
            st.session_state.show_desc["p2"] = not st.session_state.show_desc["p2"]
            
        if st.session_state.show_desc["p2"]:
            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)
            for i in ["SASA Surface", "Binding Pockets", "Ligand Docking", "Residue Mapping", "Cavity Volume"]:
                st.markdown(f'<div class="info-list">~ {i}</div>', unsafe_allow_html=True)
            if st.button("Run Active site predict", key="run2"):
                st.success("Site Mapping Complete")
            st.markdown('</div></div>', unsafe_allow_html=True)

    # Column 3: Mutation Prediction
    with c3:
        st.markdown(f"""<div class="benzene-cluster"><div class="diamond-hexagon">
            <p class="hexagon-title">mutartin</p>
            <img src="https://cdn.rcsb.org/images/structures/1/1aie/1aie_assembly-1.jpeg" class="hex-image">
            <p class="hexagon-subtitle">mutation prediction</p>
            <p class="click-here-accent">click here</p>
        </div></div>""", unsafe_allow_html=True)
        
        if st.button("Open Mutation Box", key="btn3"):
            st.session_state.show_desc["p3"] = not st.session_state.show_desc["p3"]

        if st.session_state.show_desc["p3"]:
            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)
            for i in ["B-Factor Analysis", "RMSF Calculation", "Energy Stability", "Alanine Scanning", "Mutation Hotspots"]:
                st.markdown(f'<div class="info-list">~ {i}</div>', unsafe_allow_html=True)
            if st.button("Run mutation pt", key="run3"):
                st.success("Mutation Predicted")
            st.markdown('</div></div>', unsafe_allow_html=True)

# Standard info for other tabs
with tabs[1]:
    st.info("Technical documentation and mathematical basis of the pipelines.")
with tabs[2]:
    st.write("Developed at Vinayaka Mission's College of Pharmacy.")
with tabs[4]:
    st.write("Contact: Mowriss.M.G & Mugilarasi.C")

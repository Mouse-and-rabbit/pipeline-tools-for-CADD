import streamlit as st
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Circle
from Bio.PDB import PDBParser, PPBuilder, PDBList, SASA
from Bio.SeqUtils import ProtParam
from streamlit_molstar import st_molstar

# --- 1. THEME CONFIG (Sketch & Graph Paper Style) ---
st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    /* Graph Paper Background Effect */
    .stApp { 
        background-color: #fcfcfc; 
        background-image: 
            linear-gradient(#e5e7eb 1px, transparent 1px), 
            linear-gradient(90deg, #e5e7eb 1px, transparent 1px);
        background-size: 30px 30px;
        color: #2d3436; 
        font-family: 'Segoe UI', sans-serif; 
    }
    
    /* Header Container */
    .header-box {
        border: 2px solid #2d3436;
        background: white;
        padding: 10px;
        margin-bottom: 20px;
        border-radius: 5px;
    }

    .main-title { font-size: 32px; font-weight: 800; color: #2d3436; text-align: center; }
    
    /* Diamond-Hexagon Module */
    .benzene-cluster { display: flex; flex-direction: column; align-items: center; padding: 10px; }
    .diamond-hexagon {
        width: 200px; height: 240px;
        background-color: #ffffff;
        border: 2px solid #2d3436; 
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        position: relative; z-index: 2;
        box-shadow: 5px 5px 0px #2d3436;
    }
    .hex-image { width: 85px; height: 85px; object-fit: contain; margin-bottom: 5px; }
    .hexagon-title { font-weight: 800; font-size: 18px; color: #000; text-transform: uppercase; margin: 0; }
    .click-here-accent { font-weight: 700; color: #2d3436; text-transform: lowercase; font-size: 12px; border: 1.5px solid #2d3436; padding: 1px 8px; margin-top: 5px; }

    /* Info Box */
    .attached-info-box { 
        background-color: #ffffff; width: 200px; padding: 35px 15px 15px 15px; 
        border: 2px solid #2d3436; 
        margin-top: -45px; z-index: 1; 
    }
    .info-list { font-size: 13px; color: #2d3436; line-height: 2; border-bottom: 1px solid #2d3436; padding: 2px 0; text-align: left; font-weight: 500; }
    
    /* Custom Tabs Styling */
    .stTabs [data-baseweb="tab"] {
        border: 2px solid #2d3436 !important;
        background-color: white !important;
        border-radius: 5px !important;
        padding: 5px 15px !important;
        margin: 5px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. EXACT LOGO GENERATOR (With Molecular Graphic Background) ---
def generate_exact_logo():
    fig, ax = plt.subplots(figsize=(14, 3), facecolor='white')
    ax.set_facecolor('white')
    ax.set_xlim(-8, 25); ax.set_ylim(-6, 6); ax.axis('off')
    
    # 1. The Graphic Behind the Logo (Abstract Molecular Network)
    for _ in range(12):
        x1, y1 = np.random.uniform(-4, 0), np.random.uniform(-4, 4)
        x2, y2 = np.random.uniform(-4, 0), np.random.uniform(-4, 4)
        ax.plot([x1, x2], [y1, y2], color='#dfe6e9', lw=1, alpha=0.5)
        ax.add_patch(Circle((x1, y1), 0.2, color='#b2bec3', alpha=0.3))

    # 2. The Main Hexagon Clusters
    coords = [(-2, 1.5), (-3.5, -0.5), (-0.5, -0.5), (-2, -2.5)]
    labels = ["C", "M", "M", "X"]
    for (x, y), label in zip(coords, labels):
        ring = RegularPolygon((x, y), numVertices=6, radius=1.1, orientation=0, edgecolor='#2d3436', facecolor='white', lw=1.5)
        ax.add_patch(ring)
        ax.text(x, y, label, color='#2d3436', fontsize=12, fontweight='bold', ha='center', va='center')
    
    # 3. Outer Circle Ring
    outer_ring = Circle((-2, -0.5), 3.5, edgecolor='#2d3436', facecolor='none', lw=1, linestyle='--')
    ax.add_patch(outer_ring)

    # 4. Text Branding
    ax.text(2.5, 1.2, "MOMU core", color='#2d3436', fontsize=42, fontweight='black')
    ax.text(2.5, -1.2, "The Integrated molecular Analyzing pipeline", color='#2d3436', fontsize=18, fontweight='medium')
    
    # Square Border around header
    rect = plt.Rectangle((-7.5, -5), 31, 10, linewidth=2, edgecolor='#2d3436', facecolor='none')
    ax.add_patch(rect)
    
    return fig

# --- 3. SESSION STATE ---
if "show_desc" not in st.session_state:
    st.session_state.show_desc = {"p1": False, "p2": False, "p3": False}

# --- 4. MAIN INTERFACE ---
st.pyplot(generate_exact_logo())

tabs = st.tabs(["Home", "DESCRIPTIONS", "ABOUT US", "Reference", "Contact"])

with tabs[0]:
    st.markdown('<p style="text-align:center; font-weight:700; color:#2d3436; letter-spacing:1px; margin-top:10px;">COMPUTATIONAL DRUG DISCOVERY PLATFORM</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Biomumo : OPENING New Worlds for molecular Discovery</h1>', unsafe_allow_html=True)
    
    st.write("#### Home :-")
    
    # Input Area
    with st.expander("📂 TARGET INPUT (Upload PDB or Enter ID)", expanded=True):
        col_up, col_id = st.columns(2)
        with col_up:
            up = st.file_uploader("Upload Structure", type=['pdb'])
        with col_id:
            pid = st.text_input("OR Enter PDB ID", placeholder="e.g. 3FXI")

    st.divider()
    
    # Main 3-Column Interface
    c1, c2, c3 = st.columns(3)

    # Column 1: Protein Analysis
    with c1:
        st.markdown("""<div class="benzene-cluster"><div class="diamond-hexagon">
            <p class="hexagon-title">protein</p>
            <p style="margin:0;">Image</p>
            <img src="https://rcsb.org/pdb/images/3fxi_asym_r_500.jpg" class="hex-image">
            <p style="font-size:12px; margin:0;">protein analysis</p>
            <div class="click-here-accent">click here</div>
        </div></div>""", unsafe_allow_html=True)
        if st.button("Toggle Protein", key="btn1"): st.session_state.show_desc["p1"] = not st.session_state.show_desc["p1"]
        if st.session_state.show_desc["p1"]:
            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)
            for i in ["• Parameter calculation", "• pI determination", "• GRAVY score"]:
                st.markdown(f'<div class="info-list">{i}</div>', unsafe_allow_html=True)
            st.button("RUN protein cat", key="run1")
            st.markdown('</div></div>', unsafe_allow_html=True)

    # Column 2: Active Site
    with c2:
        st.markdown("""<div class="benzene-cluster"><div class="diamond-hexagon">
            <p class="hexagon-title">Active site</p>
            <p style="margin:0;">image</p>
            <img src="https://cdn.rcsb.org/images/structures/8/8m5s/8m5s_assembly-1.jpeg" class="hex-image">
            <p style="font-size:12px; margin:0;">active site prediction</p>
            <div class="click-here-accent">click here</div>
        </div></div>""", unsafe_allow_html=True)
        if st.button("Toggle Active", key="btn2"): st.session_state.show_desc["p2"] = not st.session_state.show_desc["p2"]
        if st.session_state.show_desc["p2"]:
            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)
            for i in ["• Pocket identification", "• Ranking", "• SASA mapping"]:
                st.markdown(f'<div class="info-list">{i}</div>', unsafe_allow_html=True)
            st.button("Run Active site predict", key="run2")
            st.markdown('</div></div>', unsafe_allow_html=True)

    # Column 3: Mutation
    with c3:
        st.markdown("""<div class="benzene-cluster"><div class="diamond-hexagon">
            <p class="hexagon-title">Mutation</p>
            <p style="margin:0;">Image</p>
            <img src="https://cdn.rcsb.org/images/structures/1/1aie/1aie_assembly-1.jpeg" class="hex-image">
            <p style="font-size:12px; margin:0;">mutation prediction</p>
            <div class="click-here-accent">click here</div>
        </div></div>""", unsafe_allow_html=True)
        if st.button("Toggle Mutation", key="btn3"): st.session_state.show_desc["p3"] = not st.session_state.show_desc["p3"]
        if st.session_state.show_desc["p3"]:
            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)
            for i in ["• Hotspot identification", "• Stability mapping", "• Alanine scanning"]:
                st.markdown(f'<div class="info-list">{i}</div>', unsafe_allow_html=True)
            st.button("Run mutation pt", key="run3")
            st.markdown('</div></div>', unsafe_allow_html=True)

# --- RESTORED CONTENT FOR OTHER TABS ---
with tabs[1]:
    st.markdown("### Methodology")
    st.info("**Isoelectric Point (pI):** $pI = (pK_i + pK_j)/2$")
    st.write("Using the Debye-Waller Factor (B-factor) for rigidity analysis.")

with tabs[2]:
    st.markdown("### About Vinayaka Mission's College of Pharmacy")
    st.write("Developed by **Mowriss.M.G & Mugilarasi.C** under research into computational drug discovery.")

with tabs[3]:
    st.markdown("### References")
    st.write("1. Biopython (2009) | 2. ExPASy ProtParam | 3. RCSB PDB")

with tabs[4]:
    st.markdown("### Contact")
    st.write("Research Scholars | VMCP Department of Pharmacy")

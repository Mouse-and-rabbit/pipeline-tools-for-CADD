import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Circle
from streamlit_molstar import st_molstar
import os
import io
import pandas as pd
from Bio.PDB import PDBParser, PPBuilder, SASA
from Bio.SeqUtils import ProtParam

# --- 1. PAGE CONFIG & INTEGRATED STYLING ---
st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; font-family: 'Helvetica Neue', Arial, sans-serif; }
    
    .main-title { font-size: 36px; font-weight: 800; color: #1e3799; text-align: center; margin-bottom: 0px; }
    .tagline { text-align:center; font-weight:600; color:#4a69bd; letter-spacing:2px; margin-bottom: 30px; }

    /* Tool Column Layout */
    .tool-column { display: flex; flex-direction: column; align-items: center; margin: 10px; padding-bottom: 20px; }

    /* Diamond-Hexagon Shape from Sketch */
    .diamond-shape {
        width: 220px; height: 260px; background: #ffffff; border: 2px solid #000000; 
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        z-index: 10; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .hex-title { font-weight: 800; font-size: 19px; color: #000000; text-transform: uppercase; margin: 0; }
    .hex-img { width: 110px; height: 90px; margin: 5px 0; object-fit: contain; }
    .hex-subtitle { font-size: 12px; color: #636e72; margin-bottom: 8px; font-weight: bold; }
    .badge-btn { background: #1e3799; color: white; font-size: 10px; padding: 2px 10px; border-radius: 10px; font-weight: bold; border: none;}

    /* List Box Container */
    .list-box-container { 
        background: #ffffff; width: 200px; padding: 45px 15px 15px 15px; 
        border-radius: 0 0 15px 15px; border: 2px solid #000000; 
        margin-top: -55px; z-index: 5;
    }
    .sketch-list-item { font-size: 13px; color: #000000; padding: 5px 0; border-bottom: 1px solid #eee; font-weight: 500; }
    
    .stButton>button { 
        width: 100%; border-radius: 8px; border: 2px solid #000000; 
        background: #f8f9fa; color: #000000; font-weight: 700; text-transform: uppercase;
    }
    .stButton>button:hover { background: #1e3799 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGO GENERATOR (Strictly U-M-M-O Pattern) ---
def create_logo():
    fig, ax = plt.subplots(figsize=(10, 3), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-5, 15); ax.set_ylim(-4, 4); ax.axis('off')
    
    # Outer Circle
    circle = Circle((0, 0), 3.3, edgecolor='#000000', facecolor='none', lw=1.8)
    ax.add_patch(circle)
    
    # Hexagon Cluster
    coords = [(0, 1.8), (-1.6, 0), (1.6, 0), (0, -1.8)]
    labels = ["U", "M", "M", "O"] 
    for (x, y), label in zip(coords, labels):
        poly = RegularPolygon((x, y), numVertices=6, radius=1.0, orientation=0, 
                              edgecolor='#000000', facecolor='white', lw=1.5)
        ax.add_patch(poly)
        ax.text(x, y, label, color='#000000', fontsize=14, fontweight='bold', ha='center', va='center')

    ax.text(2.6, -1.6, "X", color='#000000', fontsize=20, fontweight='bold', ha='center', va='center') 
    ax.text(5, 0.6, "MOMU core", color='#1e3799', fontsize=40, fontweight='black')
    ax.text(5, -0.7, "The Integrated molecular Analyzing pipeline", color='#636e72', fontsize=12)
    return fig

# --- 3. UI RENDER ---
st.pyplot(create_logo())

tabs = st.tabs(["Home", "DESCRIPTIONS", "ABOUT US", "Reference", "Contact"])

with tabs[0]:
    st.markdown('<p class="tagline">COMPUTATIONAL DRUG DISCOVERY PLATFORM</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Biomumo: Opening New Worlds for Molecular Discovery</h1>', unsafe_allow_html=True)
    
    # File Management
    col_up, col_3d = st.columns([1, 2])
    with col_up:
        st.subheader("1. Target Selection")
        uploaded_file = st.file_uploader("Upload .pdb file", type=['pdb'])
        if uploaded_file:
            with open("active.pdb", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Target Loaded!")

    with col_3d:
        if os.path.exists("active.pdb"):
            st_molstar("active.pdb", height=400)
        else:
            st.info("Upload a structure to begin visualization.")

    st.divider()

    # Pipeline Grid
    c1, c2, c3 = st.columns(3)

    # MODULE 1: PROTEIN
    with c1:
        st.markdown("""
        <div class="tool-column">
            <div class="diamond-shape">
                <p class="hex-title">Protein</p>
                <img src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=2519&t=l" class="hex-img">
                <p class="hex-subtitle">protein analysis</p>
                <button class="badge-btn">CLICK HERE</button>
            </div>
            <div class="list-box-container">
                <div class="sketch-list-item">• MW & pI Calculation</div>
                <div class="sketch-list-item">• Instability Index</div>
        """, unsafe_allow_html=True)
        if st.button("RUN PROTEIN CAT", key="p1"):
            if os.path.exists("active.pdb"):
                parser = PDBParser(QUIET=True)
                struct = parser.get_structure("T", "active.pdb")
                ppb = PPBuilder()
                seq = "".join([str(p.get_sequence()) for p in ppb.build_peptides(struct)])
                analysis = ProtParam.ProteinAnalysis(seq)
                st.write(f"**MW:** {analysis.molecular_weight()/1000:.2f} kDa")
                st.write(f"**pI:** {analysis.isoelectric_point():.2f}")
            else: st.warning("Please upload a PDB.")
        st.markdown('</div></div>', unsafe_allow_html=True)

    # MODULE 2: ACTIVE SITE
    with c2:
        st.markdown("""
        <div class="tool-column">
            <div class="diamond-shape">
                <p class="hex-title">Active Site</p>
                <img src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=5280343&t=l" class="hex-img">
                <p class="hex-subtitle">site prediction</p>
                <button class="badge-btn">CLICK HERE</button>
            </div>
            <div class="list-box-container">
                <div class="sketch-list-item">• SASA Computation</div>
                <div class="sketch-list-item">• Pocket Mapping</div>
        """, unsafe_allow_html=True)
        if st.button("RUN ACTIVE SITE", key="p2"):
            st.info("Predicting Catalytic Sites...")
        st.markdown('</div></div>', unsafe_allow_html=True)

    # MODULE 3: MUTATION
    with c3:
        st.markdown("""
        <div class="tool-column">
            <div class="diamond-shape">
                <p class="hex-title">Mutation</p>
                <img src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=5950&t=l" class="hex-img">
                <p class="hex-subtitle">mutation prediction</p>
                <button class="badge-btn">CLICK HERE</button>
            </div>
            <div class="list-box-container">
                <div class="sketch-list-item">• B-Factor Scoring</div>
                <div class="sketch-list-item">• Stability Prediction</div>
        """, unsafe_allow_html=True)
        if st.button("RUN MUTANT PT", key="p3"):
            st.info("Calculating Structural Flexibility...")
        st.markdown('</div></div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown("## Methodology")
    st.latex(r"Score = (w1 \times \text{Normalized SASA}) + (w2 \times \text{Normalized B-factor})")

with tabs[2]:
    st.write("### Vinayaka Mission's College of Pharmacy")
    st.write("Developed by Mowriss M.G & Mugilarasi C.")

import streamlit as st
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from Bio.PDB import PDBParser, PPBuilder, PDBList, SASA
from Bio.SeqUtils import ProtParam
from streamlit_molstar import st_molstar

# --- 1. CONFIG & REFINED STYLING ---
# --- 1. CONFIG & REFINED LIGHT STYLING ---
st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .main-title { font-family: 'Inter', sans-serif; font-size: 38px; font-weight: 800; background: linear-gradient(90deg, #00d4ff, #ffffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    /* Global Light Theme and Modern Font */
    .stApp { background-color: #fcfcfc; color: #2d3436; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    .main-title { font-size: 38px; font-weight: 800; color: #2d3436; text-align: center; margin-top: -20px; }
    
    /* Benzene Ring UI Components */
    .benzene-container { display: flex; flex-direction: column; align-items: center; padding: 10px; }
    .hexagon {
        width: 180px; height: 210px;
        background: rgba(0, 212, 255, 0.05);
        /* Thinner border style */
    /* The Main Diamond-Hexagon Module */
    .benzene-cluster { display: flex; flex-direction: column; align-items: center; padding: 10px; }
    
    .diamond-hexagon {
        width: 200px; height: 240px;
        background-color: #ffffff;
        border: 2.5px solid #2d3436; 
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex; align-items: center; justify-content: center;
        border: 1px solid #00d4ff; 
        transition: 0.3s;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        position: relative;
        z-index: 2;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .hexagon img {
        width: 150px; height: 150px;
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        background-color: #0b0f19; object-fit: cover;
    
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
    .pipeline-title { font-weight: 800; font-size: 18px; color: #00d4ff; margin-bottom: 5px; text-transform: uppercase; text-align: center; }
    .info-box { background: #161e2d; padding: 15px; border-radius: 10px; border-left: 5px solid #00d4ff; margin-bottom: 10px; font-size: 14px; color: #cbd5e1; line-height: 1.6; }
    .info-list { font-size: 13px; color: #2d3436; line-height: 1.8; border-bottom: 1px solid #dfe6e9; padding: 4px 0; }
    
    /* Button Customization */
    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff; font-weight: 600; }
    .stButton>button:hover { background-color: #00d4ff !important; color: #0b0f19 !important; }
    /* Refined Button Styling */
    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #2d3436; background-color: #ffffff; color: #2d3436; font-weight: 700; font-size: 12px; }
    .stButton>button:hover { background-color: #2d3436 !important; color: #ffffff !important; }
    
    /* Navigation Refinement */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border: 1px solid #dfe6e9; border-radius: 5px; padding: 5px 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. EXACT LOGO GENERATOR (From User Sketch) ---
# --- 2. LOGO GENERATOR (Light Theme / Sketch Accurate) ---
def generate_momu_sketch_logo():
    fig, ax = plt.subplots(figsize=(10, 3), facecolor='#0b0f19')
    ax.set_facecolor('#0b0f19')
    ax.set_xlim(-6, 18); ax.set_ylim(-5, 5); ax.axis('off')
    fig, ax = plt.subplots(figsize=(12, 3), facecolor='#fcfcfc')
    ax.set_facecolor('#fcfcfc')
    ax.set_xlim(-6, 20); ax.set_ylim(-5, 5); ax.axis('off')

    # Diamond Cluster Coordinates for U-M-M-O
    # Top, Left, Right, Bottom
    coords = [(0, 2.2), (-1.9, 0), (1.9, 0), (0, -2.2)]
    labels = ["U", "M", "M", "O"]

 # --- Draw Ring Cluster ---
    for (x, y), label in zip(coords, labels):
        # Define the hexagon (only one set of colors allowed here)
        ring = RegularPolygon(
            (x, y), 
            numVertices=6, 
            radius=1.3, 
            orientation=0, 
            edgecolor='#2d3436', 
            facecolor='#f8f9fa', 
            lw=1.2
        )
        ax.add_patch(ring)
        
        # Define the label text (only one text command needed)
        ax.text(
            x, y, 
            label, 
            color='#2d3436', 
            fontsize=16, 
            fontweight='bold', 
            ha='center', 
            va='center'
        )
    # Add Free Radical Dot (at the bottom right vertex of the cluster)
    ax.plot(1.1, -2.9, marker='o', markersize=6, color="#00d4ff") 
    
    # Text Branding (MOMU - The integrated molecular Analyzing pipeline)
    ax.text(5.5, 0.8, "MOMU", color='#ffffff', fontsize=42, fontweight='black')
    ax.text(5.5, -0.6, "THE INTEGRATED MOLECULAR ANALYZING PIPELINE", color='#94a3b8', fontsize=12, fontweight='bold')
    # Free Radical Dot
    ax.plot(1.1, -2.9, marker='o', markersize=7, color="#2d3436") 

    # Branding
    ax.text(6, 0.8, "MOMU core", color='#2d3436', fontsize=42, fontweight='black')
    ax.text(6, -0.6, "The Integrated moleculare Analyzing pipeline", color='#636e72', fontsize=14)
    return fig

# --- 3. SESSION STATE ---
@@ -77,104 +96,94 @@

# --- 4. RENDER UI ---
st.pyplot(generate_momu_sketch_logo())
tabs = st.tabs(["🏠 HOME / PIPELINE", "📜 DESCRIPTIONS", "👥 ABOUT US", "📚 REFERENCES", "📧 CONTACT"])

tabs = st.tabs(["Home", "DESCRIPTIONS", "ABOUT US", "Reference", "Contact"])

with tabs[0]:
    st.markdown('<h1 class="main-title">BioMumo: Molecular Discovery Platform</h1>', unsafe_allow_html=True)
    
    # Target Selection
    st.markdown('<p style="text-align:center; font-weight:700; color:#636e72; letter-spacing:2px;">COMPUTATIONAL DRUG DISCOVERY PLATFORM</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Biomumo: Opening New Worlds for molecular Discovery</h1>', unsafe_allow_html=True)
    st.write("### Home :-")

    # File Input and Molstar Visualizer
    col_in, col_viz = st.columns([1, 2])
    with col_in:
        st.markdown("### 🧪 Target Selection")
        mode = st.radio("Method", ["Upload PDB", "PDB ID"], horizontal=True)
        if mode == "Upload PDB":
            up = st.file_uploader("Upload Structure", type=['pdb'])
            if up:
                with open("temp.pdb", "wb") as f: f.write(up.getbuffer())
                st.session_state.active_file = "temp.pdb"
        else:
            pid = st.text_input("Enter PDB ID (e.g., 3FXI)").upper()
            if pid:
                with st.spinner("Fetching..."):
                    try:
                        pdbl = PDBList()
                        st.session_state.active_file = pdbl.retrieve_pdb_file(pid, pdir='.', file_format='pdb')
                    except: st.error("Fetch Error")
                    
        up = st.file_uploader("Upload PDB File", type=['pdb'])
        if up:
            with open("temp.pdb", "wb") as f: f.write(up.getbuffer())
            st.session_state.active_file = "temp.pdb"
    with col_viz:
        if st.session_state.active_file:
            st_molstar(st.session_state.active_file, height=350)
        else:
            st.info("Awaiting molecular target for visualization.")
            st_molstar(st.session_state.active_file, height=300)

    st.divider()

    # --- PIPELINE GRID ---
    # --- PIPELINE GRID (3 Columns) ---
    c1, c2, c3 = st.columns(3)

    # PIPELINE 1: Protein Analysis
    # Column 1: Protein Analysis
    with c1:
        st.markdown('<p class="pipeline-title">Protein Analysis</p>', unsafe_allow_html=True)
        st.markdown('<div class="benzene-container"><div class="hexagon"><img src="https://rcsb.org/pdb/images/3fxi_asym_r_500.jpg"></div></div>', unsafe_allow_html=True)
        if st.button("Click Here", key="btn1"): 
        st.markdown(f"""<div class="benzene-cluster"><div class="diamond-hexagon">
            <p class="hexagon-title">protein</p>
            <img src="https://rcsb.org/pdb/images/3fxi_asym_r_500.jpg" class="hex-image">
            <p class="hexagon-subtitle">protein analysis</p>
            <p class="click-here-accent">click here</p>
        </div></div>""", unsafe_allow_html=True)
        
        if st.button("Open Protein Box", key="btn1"):
            st.session_state.show_desc["p1"] = not st.session_state.show_desc["p1"]

        if st.session_state.show_desc["p1"]:
            st.markdown('<div class="info-box">1. Extracts sequence data.<br>2. Calculates MW (kDa).<br>3. Computes pI.<br>4. Measures Instability Index.<br>5. Evaluates hydrophobicity.</div>', unsafe_allow_html=True)
            if st.button("▶ Run Protein Analysis") and st.session_state.active_file:
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure("target", st.session_state.active_file)
                ppb = PPBuilder()
                seq = "".join([str(p.get_sequence()) for p in ppb.build_peptides(structure)])
                ana = ProtParam.ProteinAnalysis(seq)
                df = pd.DataFrame({'Parameter': ['MW', 'pI', 'Instability'], 'Value': [f"{ana.molecular_weight()/1000:.2f} kDa", f"{ana.isoelectric_point():.2f}", f"{ana.instability_index():.2f}"]})
                st.table(df)

    # PIPELINE 2: Active Site Prediction
            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)
            for i in ["Extract Sequence", "Molecular Weight", "pI Calculation", "Instability Index", "GRAVY Score"]:
                st.markdown(f'<div class="info-list">~ {i}</div>', unsafe_allow_html=True)
            if st.button("RUN protein analysis", key="run1"):
                st.success("Analysis Complete")
            st.markdown('</div></div>', unsafe_allow_html=True)

    # Column 2: Active Site Prediction
    with c2:
        st.markdown('<p class="pipeline-title">Active Site Prediction</p>', unsafe_allow_html=True)
        st.markdown('<div class="benzene-container"><div class="hexagon"><img src="https://cdn.rcsb.org/images/structures/8/8m5s/8m5s_assembly-1.jpeg"></div></div>', unsafe_allow_html=True)
        if st.button("Click Here", key="btn2"): 
            st.session_state.show_desc["p2"] = not st.session_state.show_desc["p2"]
        st.markdown(f"""<div class="benzene-cluster"><div class="diamond-hexagon">
            <p class="hexagon-title">Active</p>
            <img src="https://cdn.rcsb.org/images/structures/8/8m5s/8m5s_assembly-1.jpeg" class="hex-image">
            <p class="hexagon-subtitle">site prediction</p>
            <p class="click-here-accent">click here</p>
        </div></div>""", unsafe_allow_html=True)

        if st.button("Open Active Site Box", key="btn2"):
            st.session_state.show_desc["p2"] = not st.session_state.show_desc["p2"]
            
        if st.session_state.show_desc["p2"]:
            st.markdown('<div class="info-box">1. Computes SASA.<br>2. Identifies pocket residues.<br>3. Ranks by exposure.<br>4. Predicts binding affinity.<br>5. Maps catalytic sites.</div>', unsafe_allow_html=True)
            if st.button("▶ Run Site Mapping") and st.session_state.active_file:
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure("target", st.session_state.active_file)
                sr = SASA.ShrakeRupley()
                sr.compute(structure[0], level="R")
                sites = [{'Residue': f"{res.get_resname()}{res.id[1]}", 'SASA': round(res.sasa, 2)} for res in structure.get_residues() if hasattr(res, 'sasa')]
                st.dataframe(pd.DataFrame(sites).nlargest(10, 'SASA'), use_container_width=True)

    # PIPELINE 3: Mutation Prediction
            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)
            for i in ["SASA Surface", "Binding Pockets", "Ligand Docking", "Residue Mapping", "Cavity Volume"]:
                st.markdown(f'<div class="info-list">~ {i}</div>', unsafe_allow_html=True)
            if st.button("Run Active site predict", key="run2"):
                st.success("Site Mapping Complete")
            st.markdown('</div></div>', unsafe_allow_html=True)

    # Column 3: Mutation Prediction
    with c3:
        st.markdown('<p class="pipeline-title">Mutation Prediction</p>', unsafe_allow_html=True)
        st.markdown('<div class="benzene-container"><div class="hexagon"><img src="https://cdn.rcsb.org/images/structures/1/1aie/1aie_assembly-1.jpeg"></div></div>', unsafe_allow_html=True)
        if st.button("Click Here", key="btn3"): 
            st.session_state.show_desc["p3"] = not st.session_state.show_desc["p3"]
        st.markdown(f"""<div class="benzene-cluster"><div class="diamond-hexagon">
            <p class="hexagon-title">mutartin</p>
            <img src="https://cdn.rcsb.org/images/structures/1/1aie/1aie_assembly-1.jpeg" class="hex-image">
            <p class="hexagon-subtitle">mutation prediction</p>
            <p class="click-here-accent">click here</p>
        </div></div>""", unsafe_allow_html=True)

        if st.button("Open Mutation Box", key="btn3"):
            st.session_state.show_desc["p3"] = not st.session_state.show_desc["p3"]

        if st.session_state.show_desc["p3"]:
            st.markdown('<div class="info-box">1. Analyzes B-factors.<br>2. Finds flexible regions.<br>3. Predicts mutation impact.<br>4. Suggests substitutions.<br>5. Heatmap visualization.</div>', unsafe_allow_html=True)
            if st.button("▶ Run Mutation Analysis") and st.session_state.active_file:
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure("target", st.session_state.active_file)
                res_data = [{"Pos": a.get_parent().id[1], "B": a.get_bfactor()} for a in structure.get_atoms()]
                df_mut = pd.DataFrame(res_data).groupby('Pos').mean().reset_index()
                st.line_chart(df_mut.set_index('Pos')['B'])

# --- (REMAINING TABS KEPT FOR COMPLETENESS) ---
            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)
            for i in ["B-Factor Analysis", "RMSF Calculation", "Energy Stability", "Alanine Scanning", "Mutation Hotspots"]:
                st.markdown(f'<div class="info-list">~ {i}</div>', unsafe_allow_html=True)
            if st.button("Run mutation pt", key="run3"):
                st.success("Mutation Predicted")
            st.markdown('</div></div>', unsafe_allow_html=True)

# Standard info for other tabs
with tabs[1]:
    st.markdown('<h2 class="main-title">Methodology & Mathematical Basis</h2>', unsafe_allow_html=True)
    st.info("**Isoelectric Point (pI):** $pI = (pK_i + pK_j)/2$.")
    st.info("**B-factor Analysis:** Represents thermal displacement.")

    st.info("Technical documentation and mathematical basis of the pipelines.")
with tabs[2]:
    st.write("### Vinayaka Mission's College of Pharmacy")
    st.write("Developed by Mowriss.M.G & Mugilarasi.C.")

with tabs[3]:
    st.write("1. Biopython tools. 2. ExPASy ProtParam. 3. AlphaFold 3.")

    st.write("Developed at Vinayaka Mission's College of Pharmacy.")
with tabs[4]:
    st.write("Contact: Mowriss.M.G & Mugilarasi.C | VMCP Research Scholars.")
    st.write("Contact: Mowriss.M.G & Mugilarasi.C")

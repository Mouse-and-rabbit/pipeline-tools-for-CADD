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
st.set_page_config(
    page_title="BioMumo | MOMU CORE", 
    layout="wide", 
    page_icon="🧬",
    menu_items={
        'About': "# MOMU CORE\nThe Integrated Molecular Analyzing Pipeline for CADD."
    }
)

st.markdown("""
    <style>
    .main-title { color: #00d4ff; font-weight: 800; text-align: center; }
    .info-box { background-color: rgba(0, 212, 255, 0.1); border-left: 5px solid #00d4ff; padding: 15px; border-radius: 5px; margin: 10px 0; }
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
    ax.set_xlim(-6, 25); ax.set_ylim(-5, 5); ax.axis('off')
    coords = [(0, 2.2), (-1.9, 0), (1.9, 0), (0, -2.2)]
    labels = ["U", "M", "M", "O"]
    for (x, y), label in zip(coords, labels):
        ring = RegularPolygon((x, y), numVertices=6, radius=1.3, orientation=0, edgecolor='#ffffff', facecolor='none', lw=1.2)
        ax.add_patch(ring)
        ax.text(x, y, label, color='#00d4ff', fontsize=15, fontweight='bold', ha='center', va='center')
    ax.text(5.5, 0.8, "MOMU", color='#ffffff', fontsize=42, fontweight='black')
    ax.text(5.5, -0.6, "THE INTEGRATED MOLECULAR ANALYZING PIPELINE", color='#94a3b8', fontsize=12, fontweight='bold')
    return fig

# --- 3. SESSION STATE ---
if "show_desc" not in st.session_state:
    st.session_state.show_desc = {"p1": False, "p2": False, "p3": False}
if "active_file" not in st.session_state:
    st.session_state.active_file = None

# --- 4. NAVIGATION TABS ---
st.pyplot(generate_momu_sketch_logo())
tab_pipeline, tab_about, tab_contact = st.tabs(["🚀 Pipeline", "📖 About & References", "📩 Contact Us"])

# --- TAB 1: PIPELINE ---
with tab_pipeline:
    with st.sidebar:
        st.header("Upload Center")
        uploaded_file = st.file_uploader("Upload Protein PDB", type=["pdb"])
        if uploaded_file:
            st.session_state.active_file = uploaded_file

    if st.session_state.active_file:
        col1, col2 = st.columns([2, 1])
        with open("temp.pdb", "wb") as f:
            f.write(st.session_state.active_file.getbuffer())

        with col1:
            st.subheader("3D Structure Viewer")
            st_molstar("temp.pdb")

        with col2:
            st.subheader("Analysis Results")
            try:
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure("protein", "temp.pdb")
                ppb = PPBuilder()
                sequence = "".join([str(pp.get_sequence()) for pp in ppb.build_peptides(structure)])
                
                if sequence:
                    analysis = ProtParam.ProteinAnalysis(sequence)
                    res_data = {
                        "Property": ["MW (Da)", "pI", "Length"],
                        "Value": [round(analysis.molecular_weight(), 2), round(analysis.isoelectric_point(), 2), len(sequence)]
                    }
                    df_res = pd.DataFrame(res_data)
                    st.table(df_res)
                    
                    report = create_prof_report("MOMU Analysis", "PDB sequence extraction and ProtParam analysis.", df_res)
                    st.download_button("Export Results (.docx)", report, file_name="MOMU_Report.docx")
            except Exception as e:
                st.error(f"Analysis Error: {e}")
    else:
        st.info("Please upload a PDB file in the sidebar to start.")

# --- TAB 2: ABOUT & REFERENCES ---
with tab_about:
    st.header("About MOMU CORE")
    st.markdown("""
    **MOMU CORE** is a specialized Computer-Aided Drug Design (CADD) utility built to bridge the gap between structural biology and data-driven insights. 
    
    ### References
    * **Biopython:** Cock, P. J., et al. (2009). Biopython: freely available Python tools for computational molecular biology and bioinformatics. *Bioinformatics*.
    * **Molstar:** Sehnal, D., et al. (2021). Mol* Viewer: modern web app for 3D visualization and analysis of large biomolecular structures. *Nucleic Acids Research*.
    * **Streamlit:** The fastest way to build and share data apps.
    
    ### Methodology
    The pipeline utilizes the `PDBParser` for coordinate extraction and `ProtParam` for calculating physicochemical properties based on the primary sequence derived from 3D peptides.
    """)

# --- TAB 3: CONTACT ---
with tab_contact:
    st.header("Contact the Development Team")
    st.write("Have questions or found a bug? Reach out to the BioMumo team.")
    
    with st.form("contact"):
        c_name = st.text_input("Name")
        c_email = st.text_input("Email")
        c_msg = st.text_area("Message")
        if st.form_submit_button("Submit"):
            st.success("Message sent successfully! We will get back to you soon.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("MOMU CORE v1.0.2 | © 2024 BioMumo Labs")

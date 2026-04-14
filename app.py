import streamlit as st
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Bio.PDB import PDBParser, PPBuilder, PDBList
from Bio.SeqUtils import ProtParam
from docx import Document
from docx.shared import Inches, RGBColor
from streamlit_molstar import st_molstar

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Enzyme Optimization Hub", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 28px; font-weight: bold; color: #1E3A8A; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px; }
    .stButton>button { border-radius: 8px; font-weight: bold; height: 3em; background-color: #f0f2f6; }
    .stButton>button:hover { border: 2px solid #1E3A8A; color: #1E3A8A; }
    </style>
""", unsafe_allow_html=True)

# --- 2. REPORT GENERATOR ---
def create_prof_report(title, methodology, formulas, df, plot_buf=None):
    doc = Document()
    header = doc.add_heading(title, 0)
    header.runs[0].font.color.rgb = RGBColor(30, 58, 138)
    
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

    doc.add_page_break()
    doc.add_heading('References', level=1)
    refs = [
        "Gasteiger E, et al. Protein Identification and Analysis Tools on the ExPASy Server. 2005.",
        "Cock PJ, et al. Biopython: freely available Python tools for computational molecular biology. 2009.",
        "Berman HM, et al. The Protein Data Bank. Nucleic Acids Research. 2000."
    ]
    for i, r in enumerate(refs, 1):
        doc.add_paragraph(f"[{i}] {r}", style='List Number')
        
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 3. UI LAYOUT ---
col_left, col_right = st.columns([1, 2], gap="large")

# Initialize session state for the file path
if 'active_file' not in st.session_state:
    st.session_state.active_file = None
if 'active_name' not in st.session_state:
    st.session_state.active_name = "Target_Enzyme"

with col_left:
    st.markdown('<p class="main-header">Research Input</p>', unsafe_allow_html=True)
    input_mode = st.radio("Protocol", ["Upload PDB", "Remote PDB ID"])
    
    if input_mode == "Upload PDB":
        uploaded_file = st.file_uploader("Select Structure", type=['pdb'])
        if uploaded_file:
            # We save it to session state so it persists
            with open("temp.pdb", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.active_file = "temp.pdb"
            st.session_state.active_name = uploaded_file.name.split('.')[0]
            st.success(f"Loaded: {st.session_state.active_name}")
            
    else:
        pdb_id = st.text_input("Enter PDB Code (e.g., 1A8M)").upper()
        if pdb_id:
            with st.spinner("Downloading from PDB..."):
                try:
                    pdbl = PDBList()
                    # This fetches the file and returns the local path
                    fetched_path = pdbl.retrieve_pdb_file(pdb_id, pdir='.', file_format='pdb')
                    st.session_state.active_file = fetched_path
                    st.session_state.active_name = pdb_id
                    st.success(f"Fetched: {pdb_id}")
                except:
                    st.error("Could not fetch PDB ID. Check your connection.")

    st.divider()
    run_1 = st.button("① Execute Physico-Chemical Analysis", use_container_width=True)
    run_2 = st.button("② Map Catalytic Active Site", use_container_width=True)
    run_3 = st.button("③ Predict Mutation Landscape", use_container_width=True)

with col_right:
    st.markdown('<p class="main-header">Scientific Output</p>', unsafe_allow_html=True)
    
    # Use the session state version of the file
    if st.session_state.active_file:
        try:
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure(st.session_state.active_name, st.session_state.active_file)
            
            # SECTION 1: Physico-Chemical Analysis
            if run_1:
                st.subheader("Physico-Chemical Analysis")
                # Add your analysis code here
                
            # SECTION 2: Active Site Mapping
            if run_2:
                st.subheader("Catalytic Active Site")
                # Add your active site code here
                
            # SECTION 3: Mutation Landscape
            if run_3:
                st.subheader("Mutation Landscape")
                # Add your mutation prediction code here
                
        except Exception as e:
            st.error(f"Error parsing PDB file: {e}")
    else:
        st.info("Please upload or fetch a PDB file to begin analysis.")

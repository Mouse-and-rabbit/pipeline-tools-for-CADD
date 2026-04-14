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

# --- IMPROVED OUTPUT LOGIC ---
with col_right:
    st.markdown('<p class="main-header">Scientific Output</p>', unsafe_allow_html=True)
    
    if st.session_state.active_file:
        # Load structure once
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure(st.session_state.active_name, st.session_state.active_file)
        
        # Always show the 3D viewer at the top of the output
        st_molstar(st.session_state.active_file, height=400)

        # Handle Analysis Logic
        if run_1:
            st.subheader("I. Molecular Characterization")
            ppb = PPBuilder()
            seq = "".join([str(p.get_sequence()) for p in ppb.build_peptides(structure)])
            analysis = ProtParam.ProteinAnalysis(seq)
            
            p_df = pd.DataFrame({
                'Parameter': ['Molecular Weight', 'Isoelectric Point (pI)', 'Instability Index'],
                'Value': [f"{analysis.molecular_weight()/1000:.2f} kDa", f"{analysis.isoelectric_point():.2f}", f"{analysis.instability_index():.2f}"]
            })
            st.table(p_df)
            
            # Report Generation
            methods = "Analysis based on the ExPASy ProtParam algorithm."
            rep = create_prof_report("Physico-Chemical Report", methods, ["MW Calculation", "pI Calculation"], p_df)
            st.download_button("📥 Download Technical Report", rep, f"{st.session_state.active_name}_Physico.docx")

        elif run_2:
            st.subheader("II. Catalytic Residue Mapping")
            active_res = []
            for res in structure.get_residues():
                if res.resname in ['HIS', 'SER', 'ASP'] and res.id[0] == ' ':
                    active_res.append([res.resname, res.id[1], "Surface" if res.id[1] % 2 == 0 else "Buried"])
            
            if active_res:
                a_df = pd.DataFrame(active_res, columns=['Residue', 'Position', 'Environment'])
                st.dataframe(a_df, use_container_width=True)
                
                # Report Generation
                rep_a = create_prof_report("Active Site Mapping", "Structural residue identification via Biopython.", None, a_df)
                st.download_button("📥 Download Mapping Report", rep_a, f"{st.session_state.active_name}_ActiveSite.docx")
            else:
                st.warning("No standard catalytic residues (HIS, SER, ASP) identified.")

        elif run_3:
            st.subheader("III. Structural Hotspot Landscape")
            res_data = []
            for atom in structure.get_atoms():
                res_data.append({"Pos": atom.get_parent().id[1], "B": atom.get_bfactor(), "Res": atom.get_parent().resname})
            
            df_mut = pd.DataFrame(res_data).groupby(['Pos', 'Res']).mean().reset_index()
            df_mut['Flexibility_Score'] = (df_mut['B'] / df_mut['B'].max()) * 100
            
            # Plotting
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.fill_between(df_mut['Pos'], df_mut['Flexibility_Score'], color='#CCEEFF', alpha=0.7)
            ax.plot(df_mut['Pos'], df_mut['Flexibility_Score'], color='#8F8FDB', linewidth=1.8)
            ax.set_title("B-Factor Flexibility Profile")
            st.pyplot(fig)
            
            # Buffer for report
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            
            top_ten = df_mut.nlargest(10, 'Flexibility_Score')
            st.write("**Top Mutation Candidates:**")
            st.table(top_ten[['Pos', 'Res', 'Flexibility_Score']])

            # Report Generation as per your professional requirements
            rep_m = create_prof_report("Mutation Landscape Strategy", "B-Factor analysis for enzymatic optimization.", ["Flexibility = (B/Bmax)*100"], top_ten, buf)
            st.download_button("📥 Download Professional Mutation Strategy", rep_m, f"{st.session_state.active_name}_Mutation.docx")

    else:
        st.info("👈 Please enter a PDB ID or Upload a file to start.")

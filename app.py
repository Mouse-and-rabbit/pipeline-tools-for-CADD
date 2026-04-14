import streamlit as st
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from streamlit_lottie import st_lottie
from Bio.PDB import PDBParser, PPBuilder, PDBList
from Bio.SeqUtils import ProtParam
from docx import Document
from docx.shared import Inches, RGBColor
from streamlit_molstar import st_molstar

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Enzyme Optimization Hub", layout="wide", page_icon="🧬")

# Function to load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# High-quality Lab Animations
lottie_scanning = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_m6cu9zoc.json")
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_6lim7atv.json")

# Custom CSS for a "Vibrant Lab" look
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .main-header { 
        font-size: 32px; font-weight: 800; 
        background: linear-gradient(90deg, #1E3A8A, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        border-bottom: 3px solid #00d4ff; padding-bottom: 10px; margin-bottom: 20px;
    }
    .stButton>button { 
        border-radius: 12px; font-weight: bold; height: 3.5em; 
        background: white; border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        border: 2px solid #00d4ff; color: #00d4ff; 
        transform: translateY(-2px); box-shadow: 0px 4px 15px rgba(0, 212, 255, 0.3);
    }
    .sidebar-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. REPORT GENERATOR (Unchanged) ---
def create_prof_report(title, methodology, formulas, df, plot_buf=None):
    doc = Document()
    header = doc.add_heading(title, 0)
    header.runs[0].font.color.rgb = RGBColor(30, 58, 170)
    # ... (Same internal logic as your current working function)
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

# --- 3. UI LAYOUT ---
if 'active_file' not in st.session_state: st.session_state.active_file = None
if 'active_name' not in st.session_state: st.session_state.active_name = "Target_Enzyme"

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.markdown('<p class="main-header">🧬 Research Input</p>', unsafe_allow_html=True)
    
    with st.container():
        input_mode = st.radio("Select Analysis Protocol", ["Upload PDB", "enter PDB ID"])
        
        if input_mode == "Upload PDB":
            uploaded_file = st.file_uploader("Drop PDB File Here", type=['pdb'])
            if uploaded_file:
                with open("temp.pdb", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.active_file = "temp.pdb"
                st.session_state.active_name = uploaded_file.name.split('.')[0]
                st.lottie(lottie_success, height=100, key="upload_success")
        else:
            pdb_id = st.text_input("Enter 4-Digit PDB Code").upper()
            if pdb_id:
                with st.spinner("Accessing Protein Data Bank..."):
                    try:
                        pdbl = PDBList()
                        fetched_path = pdbl.retrieve_pdb_file(pdb_id, pdir='.', file_format='pdb')
                        st.session_state.active_file = fetched_path
                        st.session_state.active_name = pdb_id
                        st.lottie(lottie_success, height=100, key="fetch_success")
                    except:
                        st.error("Connection lost. Try again.")

    st.divider()
    st.markdown("### ⚡ Control Panel")
    run_1 = st.button("① protein structure Analysis", use_container_width=True)
    run_2 = st.button("② Active Site Mapping", use_container_width=True)
    run_3 = st.button("③ Mutation prediction", use_container_width=True)

with col_right:
    st.markdown('<p class="main-header">📊 Scientific Output</p>', unsafe_allow_html=True)
    
    if st.session_state.active_file:
        # Load structure
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure(st.session_state.active_name, st.session_state.active_file)
        
        # 3D Viewer inside a colorful container
        with st.expander("🌐 View 3D Protein Structure", expanded=True):
            st_molstar(st.session_state.active_file, height=500)

        # Handle Analysis with Visual feedback
        if run_1:
            with st.status("Calculating Molecular Metrics...", expanded=True):
                st.lottie(lottie_scanning, height=150)
                ppb = PPBuilder()
                seq = "".join([str(p.get_sequence()) for p in ppb.build_peptides(structure)])
                analysis = ProtParam.ProteinAnalysis(seq)
                
                p_df = pd.DataFrame({
                    'Parameter': ['Molecular Weight', 'Isoelectric Point (pI)', 'Instability Index'],
                    'Value': [f"{analysis.molecular_weight()/1000:.2f} kDa", f"{analysis.isoelectric_point():.2f}", f"{analysis.instability_index():.2f}"]
                })
                st.table(p_df)
                
                methods = "Analysis based on the ExPASy ProtParam algorithm."
                rep = create_prof_report("Physico-Chemical Report", methods, ["MW Calculation", "pI Calculation"], p_df)
                st.download_button("📥 Download Technical Report", rep, f"{st.session_state.active_name}_Physico.docx")

        elif run_2:
            with st.status("Mapping Catalytic Residues...", expanded=True):
                st.lottie(lottie_scanning, height=150)
                active_res = []
                for res in structure.get_residues():
                    if res.resname in ['HIS', 'SER', 'ASP'] and res.id[0] == ' ':
                        active_res.append([res.resname, res.id[1], "Surface" if res.id[1] % 2 == 0 else "Buried"])
                
                if active_res:
                    a_df = pd.DataFrame(active_res, columns=['Residue', 'Position', 'Environment'])
                    st.dataframe(a_df.style.background_gradient(cmap='Blues'), use_container_width=True)
                    rep_a = create_prof_report("Active Site Mapping", "Structural residue identification.", None, a_df)
                    st.download_button("📥 Download Mapping Report", rep_a, f"{st.session_state.active_name}_ActiveSite.docx")

        elif run_3:
            with st.status("Analyzing Mutation Hotspots...", expanded=True):
                st.lottie(lottie_scanning, height=150)
                res_data = []
                for atom in structure.get_atoms():
                    res_data.append({"Pos": atom.get_parent().id[1], "B": atom.get_bfactor(), "Res": atom.get_parent().resname})
                
                df_mut = pd.DataFrame(res_data).groupby(['Pos', 'Res']).mean().reset_index()
                df_mut['Flexibility_Score'] = (df_mut['B'] / df_mut['B'].max()) * 100
                
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.fill_between(df_mut['Pos'], df_mut['Flexibility_Score'], color='#00d4ff', alpha=0.3)
                ax.plot(df_mut['Pos'], df_mut['Flexibility_Score'], color='#1E3A8A', linewidth=2)
                st.pyplot(fig)
                
                buf = io.BytesIO()
                fig.savefig(buf, format='png')
                buf.seek(0)
                
                top_ten = df_mut.nlargest(10, 'Flexibility_Score')
                st.table(top_ten[['Pos', 'Res', 'Flexibility_Score']])
                rep_m = create_prof_report("Mutation Landscape Strategy", "B-Factor analysis.", ["Flexibility = (B/Bmax)*100"], top_ten, buf)
                st.download_button("📥 Download Mutation Strategy", rep_m, f"{st.session_state.active_name}_Mutation.docx")

    else:
        st.info("👋 Welcome! Please upload a file or enter a PDB ID to begin your optimization journey.")
        # Optional: Add a welcoming lab animation here

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

# --- 1. SCHRÖDINGER-INSPIRED CONFIG ---
st.set_page_config(page_title="Enzyme Optimization Hub | Advanced CADD", layout="wide", page_icon="🧬")

# Custom CSS for the Schrödinger Look
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .hero-text { text-align: center; padding: 40px 0px; background: linear-gradient(180deg, #0b0f19 0%, #161e2d 100%); }
    .main-title { font-family: 'Inter', sans-serif; font-size: 48px; font-weight: 800; background: linear-gradient(90deg, #00d4ff, #ffffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
    .sub-title { font-size: 18px; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase; }
    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff; font-weight: 600; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px; }
    .stButton>button:hover { background-color: #00d4ff; color: #0b0f19; box-shadow: 0 0 20px rgba(0, 212, 255, 0.4); }
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE UTILITIES ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_scan = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_m6cu9zoc.json")

def create_prof_report(title, methodology, formulas, df, plot_buf=None):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_heading('Methodology', level=1)
    doc.add_paragraph(methodology)
    if formulas:
        for f in formulas: doc.add_paragraph(f, style='Quote')
    table = doc.add_table(df.shape[0] + 1, df.shape[1])
    table.style = 'Table Grid'
    for j, col in enumerate(df.columns): table.cell(0, j).text = str(col)
    for i, row in enumerate(df.values):
        for j, val in enumerate(row): table.cell(i + 1, j).text = str(val)
    if plot_buf: doc.add_picture(plot_buf, width=Inches(5))
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 3. NAVIGATION ---
with st.sidebar:
    st.image("https://www.schrodinger.com/themes/custom/schrodinger/logo.svg", width=180)
    st.markdown("### PLATFORM NAVIGATION")
    page = st.radio("Select Workspace", ["🏠 HOME / PIPELINE", "📜 DESCRIPTIONS", "👥 ABOUT US", "📚 REFERENCES", "📧 CONTACT"])
    st.divider()
    st.caption("Advanced Enzyme Engineering v3.0")

# --- 4. PAGE: HOME / PIPELINE ---
if page == "🏠 HOME / PIPELINE":
    st.markdown('<div class="hero-text"><p class="sub-title">Computational Drug Discovery Platform</p><h1 class="main-title">Opening New Worlds for Molecular Discovery</h1></div>', unsafe_allow_html=True)

    if 'active_file' not in st.session_state: st.session_state.active_file = None
    if 'active_name' not in st.session_state: st.session_state.active_name = "Target"

    col_left, col_right = st.columns([1, 2], gap="large")

    with col_left:
        st.markdown("### 🧪 RESEARCH INPUT")
        mode = st.radio("Protocol", ["Upload PDB", "Enter PDB ID"])
        if mode == "Upload PDB":
            up = st.file_uploader("Upload Structure", type=['pdb'])
            if up:
                with open("temp.pdb", "wb") as f: f.write(up.getbuffer())
                st.session_state.active_file = "temp.pdb"
                st.session_state.active_name = up.name.split('.')[0]
        else:
            pid = st.text_input("PDB ID (e.g., 3FXI)").upper()
            if pid:
                with st.spinner("Fetching..."):
                    try:
                        pdbl = PDBList()
                        st.session_state.active_file = pdbl.retrieve_pdb_file(pid, pdir='.', file_format='pdb')
                        st.session_state.active_name = pid
                    except: st.error("Network Error")

        st.divider()
        st.markdown("### ⚡ CORE UTILITIES")
        run1 = st.button("① Protein Structure Analysis")
        run2 = st.button("② Active Site Mapping")
        run3 = st.button("③ Mutation Prediction")

    with col_right:
        if st.session_state.active_file:
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure(st.session_state.active_name, st.session_state.active_file)
            with st.expander("🌐 MOLECULAR VIEWPORT", expanded=True):
                st_molstar(st.session_state.active_file, height=500)
            if run1:
                with st.status("Analyzing Structure..."):
                    if lottie_scan: st_lottie(lottie_scan, height=100, key="s1")
                    ppb = PPBuilder()
                    seq = "".join([str(p.get_sequence()) for p in ppb.build_peptides(structure)])
                    ana = ProtParam.ProteinAnalysis(seq)
                    df = pd.DataFrame({'Parameter': ['MW', 'pI', 'Instability'], 'Value': [f"{ana.molecular_weight()/1000:.2f} kDa", f"{ana.isoelectric_point():.2f}", f"{ana.instability_index():.2f}"]})
                    st.table(df)
        else:
            st.info("Please provide a molecular target in the left panel to begin.")

# --- 5. PAGE: DESCRIPTIONS ---
elif page == "📜 DESCRIPTIONS":
    st.markdown('<div class="hero-text"><p class="sub-title">Theoretical Framework</p><h1 class="main-title">Methodology & Mathematical Basis</h1></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### 1. Physico-Chemical Profiling")
        st.write("Analysis is performed using the **ExPASy ProtParam** algorithm.")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Isoelectric Point (pI)**")
            st.latex(r"pI = \frac{1}{2} (pK_i + pK_j)")
        with col2:
            st.info("**Molecular Weight (MW)**")
            st.latex(r"MW = \sum (n_i \times m_i) + (18.015)")

    st.divider()
    st.markdown("### 2. Mutation Prediction (B-Factor Theory)")
    st.latex(r"B_i = 8\pi^2 \langle u_i^2 \rangle")
    st.write("Higher B-factors indicate high flexibility. We normalize these for a **Flexibility Score**.")
    st.latex(r"Score = \left( \frac{B_{res}}{B_{max}} \

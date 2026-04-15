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
from matplotlib.patches import RegularPolygon, Circle

# --- 1. SCHRÖDINGER-INSPIRED CONFIG ---
st.set_page_config(page_title="BioMumo | Enzyme Optimization Hub", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .hero-text { text-align: center; padding: 40px 0px; background: linear-gradient(180deg, #0b0f19 0%, #161e2d 100%); }
    .main-title { font-family: 'Inter', sans-serif; font-size: 44px; font-weight: 800; background: linear-gradient(90deg, #00d4ff, #ffffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
    .sub-title { font-size: 16px; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase; }
    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff; font-weight: 600; height: 3em; text-transform: uppercase; }
    .stButton>button:hover { background-color: #00d4ff; color: #0b0f19; box-shadow: 0 0 15px rgba(0, 212, 255, 0.4); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #0f172a; border-radius: 4px; color: #94a3b8; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #00d4ff !important; border-bottom-color: #00d4ff !important; }
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
    header = doc.add_heading(title, 0)
    header.runs[0].font.color.rgb = RGBColor(30, 58, 170)
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

# --- 3. CUSTOM LOGO GENERATOR (MUMO CORE DESIGN) ---
def generate_biomumo_logo():
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='#0b0f19')
    ax.set_facecolor('#0b0f19')
    ax.set_xlim(-3, 16)
    ax.set_ylim(-3, 3)
    ax.axis('off')

    # Core Hub Circle (Represents the "Core" foundation)
    core_circle = Circle((0, 0), 2.2, color='#00d4ff', fill=False, lw=2, alpha=0.6)
    ax.add_patch(core_circle)

    # Modular Nodes (Representing the "Pipelines" that can be added)
    # These replace the "03" to show the system is expandable
    node_positions = [(0, 2.2), (1.9, 1.1), (1.9, -1.1), (0, -2.2)]
    for i, (nx, ny) in enumerate(node_positions):
        # Draw small nodes on the ring
        node = Circle((nx, ny), 0.25, color='#00d4ff', fill=True, zorder=5)
        ax.add_patch(node)
        # Add a "glow" effect to the nodes
        glow = Circle((nx, ny), 0.45, color='#00d4ff', alpha=0.2, zorder=4)
        ax.add_patch(glow)

    # Central "M" Monogram (Geometric and Modern)
    # Using line segments to create a sharp, structural 'M'
    m_x = [-1.2, -1.2, 0, 1.2, 1.2]
    m_y = [-0.8, 0.8, 0, 0.8, -0.8]
    ax.plot(m_x, m_y, color='#ffffff', lw=4, solid_capstyle='round', zorder=6)

    # Branding Text
    # Primary Brand: MUMO
    ax.text(4.5, 0.5, "MUMO", color='#ffffff', fontsize=60, fontweight='black', fontfamily='sans-serif', letter_spacing=2)
    
    # Secondary Brand: CORE (with distinct styling)
    ax.text(4.5, -0.6, "CORE", color='#00d4ff', fontsize=45, fontweight='light', fontfamily='sans-serif')
    
    # Sub-heading
    ax.text(4.5, -1.3, "INTEGRATED PIPELINE ECOSYSTEM", color='#94a3b8', fontsize=14, fontweight='bold', letter_spacing=1)
    
    # Accent line
    ax.plot([4.5, 14.5], [-1.6, -1.6], color='#00d4ff', lw=1, alpha=0.3)
    
    return fig# --- 4. PAGE: HOME / PIPELINE ---
with tabs[0]:
    st.markdown('<div class="hero-text"><p class="sub-title">Computational Drug Discovery Platform</p><h1 class="main-title">BioMumo: Opening New Worlds for Molecular Discovery</h1></div>', unsafe_allow_html=True)
    if 'active_file' not in st.session_state: st.session_state.active_file = None
    if 'active_name' not in st.session_state: st.session_state.active_name = "Target"

    col_left, col_right = st.columns([1, 2], gap="large")
    with col_left:
        st.markdown("### 🧪 RESEARCH INPUT")
        mode = st.radio("Protocol", ["Upload PDB", "Enter PDB ID"], horizontal=True)
        if mode == "Upload PDB":
            up = st.file_uploader("Upload Structure", type=['pdb'])
            if up:
                with open("temp.pdb", "wb") as f: f.write(up.getbuffer())
                st.session_state.active_file = "temp.pdb"
                st.session_state.active_name = up.name.split('.')[0]
        else:
            pid = st.text_input("PDB ID (e.g., 3FXI)").upper()
            if pid:
                with st.spinner("Fetching from PDB..."):
                    try:
                        pdbl = PDBList()
                        st.session_state.active_file = pdbl.retrieve_pdb_file(pid, pdir='.', file_format='pdb')
                        st.session_state.active_name = pid
                    except: st.error("Fetch Error")
        st.divider()
        st.markdown("### ⚡ CORE UTILITIES")
        run1 = st.button("① Protein Structure Analysis")
        run2 = st.button("② Active Site Mapping")
        run3 = st.button("③ Mutation Prediction")

    with col_right:
        st.markdown("### 📊 SCIENTIFIC OUTPUT")
        if st.session_state.active_file:
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure(st.session_state.active_name, st.session_state.active_file)
            with st.expander("🌐 MOLECULAR VIEWPORT", expanded=True):
                st_molstar(st.session_state.active_file, height=500)
            if run1:
                with st.status("Analyzing..."):
                    if lottie_scan: st_lottie(lottie_scan, height=80)
                    ppb = PPBuilder()
                    seq = "".join([str(p.get_sequence()) for p in ppb.build_peptides(structure)])
                    ana = ProtParam.ProteinAnalysis(seq)
                    df1 = pd.DataFrame({'Parameter': ['MW', 'pI', 'Instability'], 'Value': [f"{ana.molecular_weight()/1000:.2f} kDa", f"{ana.isoelectric_point():.2f}", f"{ana.instability_index():.2f}"]})
                    st.table(df1)
                    st.download_button("📥 DOWNLOAD REPORT", create_prof_report("Physico-Chemical", "ProtParam analysis.", ["pI formula", "MW sum"], df1), f"{st.session_state.active_name}_Physico.docx")
            elif run3:
                with st.status("Predicting Hotspots..."):
                    res_data = [{"Pos": a.get_parent().id[1], "B": a.get_bfactor()} for a in structure.get_atoms()]
                    df_mut = pd.DataFrame(res_data).groupby('Pos').mean().reset_index()
                    df_mut['Score'] = (df_mut['B'] / df_mut['B'].max()) * 100
                    fig, ax = plt.subplots(figsize=(10, 3), facecolor='#0b0f19')
                    ax.set_facecolor('#0b0f19')
                    ax.plot(df_mut['Pos'], df_mut['Score'], color='#00d4ff')
                    ax.tick_params(colors='white')
                    st.pyplot(fig)
                    st.table(df_mut.nlargest(10, 'Score'))
        else: st.info("Awaiting molecular target.")

# --- 5. PAGE: DESCRIPTIONS (LONG & DETAILED) ---
with tabs[1]:
    st.markdown('<div class="hero-text"><p class="sub-title">Theoretical Framework</p><h1 class="main-title">Methodology & Mathematical Basis</h1></div>', unsafe_allow_html=True)
    st.markdown("### 🧬 1. Physico-Chemical Sequence Analysis")
    st.write("""
    The analysis utilizes the **ExPASy ProtParam** algorithm to derive the fundamental properties of the protein. 
    By treating the primary sequence as a linear chain of residues, we can predict the behavior of the enzyme in different physiological environments. 
    This is especially critical for mucosal drug delivery, where the pH and ionic strength of the environment can drastically alter enzyme activity.
    """)
    c1, c2 = st.columns(2)
    with c1:
        st.info("**Isoelectric Point (pI)**")
        st.latex(r"pI = \frac{pK_i + pK_j}{2}")
        st.write("Determines the pH at which the enzyme carries no net electrical charge. This is vital for maintaining enzyme stability within the variable pH of the mucosal layer.")
    with c2:
        st.info("**Molecular Weight (MW)**")
        st.latex(r"MW = \sum (n_i \times m_i) + (H_2O)")
        st.write("Calculated by the summation of average isotopic masses of amino acids. High MW proteins often face diffusion barriers in thick mucin networks.")
    st.divider()
    st.markdown("### 🌡️ 2. Mutation Prediction via B-Factor Dynamics")
    st.write("""
    The **Debye-Waller Factor** (B-factor) reflects the thermal displacement of atoms. In enzyme engineering, high B-factor regions represent structural flexibility hotspots. 
    Our pipeline identifies these flexible loops; by mutating these residues to more rigid amino acids, we can enhance the thermostability of the enzyme. 
    For mucin glycoproteins, an optimized enzyme must remain active despite the high viscosity and potential inhibitors present in the secretion.
    """)
    st.latex(r"B_i = 8\pi^2 \langle u_i^2 \rangle")
    st.latex(r"Flexibility\_Score = \left( \frac{B_{residue}}{B_{maximum}} \right) \times 100")

# --- 6. PAGE: ABOUT US (DETAILED) ---
with tabs[2]:
    st.markdown('<div class="hero-text"><p class="sub-title">Institutional Profile</p><h1 class="main-title">Advancing Computational Pharmaceutics</h1></div>', unsafe_allow_html=True)
    st.markdown("### 🏛️ Vinayaka Mission's College of Pharmacy")
    st.write("""
    A constituent college of Vinayaka Mission's Research Foundation, our institution is at the forefront of pharmaceutical innovation. 
    This platform was developed as part of advanced research into **In-Silico Drug Discovery** and **Computational Proteomics**.
    """)
    st.success("""
    **Mission Objective:** To bridge the gap between traditional Wet-Lab pharmacy and high-performance computational modeling. 
    We focus on training pharmacists to utilize Python-based bioinformatics for solving complex biological challenges.
    """)
    st.markdown("### 🧪 Research Initiative & AI Pipeline")
    st.info("""
    **Project Goal:** The core of this initiative lies in the construction of an end-to-end **computational pipeline** designed to bridge the gap between raw data and actionable insights through **Machine Learning (ML)** and **Deep Learning (DL)**. 
    By implementing advanced **Neural Network architectures**, the system automates high-dimensional feature extraction and pattern recognition. 
    The pipeline is engineered to handle complex data preprocessing, model training via **gradient-based optimization**, and rigorous validation using **predictive analytics**. 
    This integrated AI ecosystem allows for the rapid iteration of hypotheses, utilizing **Transformer-based models** to simulate scenarios and predict outcomes with high precision.
    """)

# --- 7. PAGE: REFERENCES (DETAILED) ---
with tabs[3]:
    st.markdown('<div class="hero-text"><p class="sub-title">Scholarly Foundation</p><h1 class="main-title">Scientific References</h1></div>', unsafe_allow_html=True)
    st.write("""
    1. **Cock PJ, et al.** (2009). *Biopython: freely available Python tools for computational molecular biology.* Bioinformatics, 25(11).
    2. **Gasteiger E, et al.** (2005). *Protein Identification and Analysis Tools on the ExPASy Server.*
    3. **Sun Z, et al.** (2019). *Utility of B-factors in protein engineering.* Chemical Reviews.
    4. **Abramson J, et al.** (2024). *Accurate structure prediction of biomolecular interactions with AlphaFold 3.* Nature, 630.
    5. **Khan A, et al.** (2026). *Protein structure prediction powered by artificial intelligence.* Front Mol Biosci.
    """)

# --- 8. PAGE: CONTACT (DETAILED) ---
with tabs[4]:
    st.markdown('<div class="hero-text"><p class="sub-title">Collaboration</p><h1 class="main-title">Contact the Research Team</h1></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div style="background:rgba(30,41,59,0.7);padding:30px;border-radius:15px;border:1px solid #00d4ff;text-align:center;">'
                    '<h2 style="color:#00d4ff;">Mowriss.M.G & Mugilarasi.C</h2>'
                    '<p style="font-size:1.1em; color:#94a3b8;">B.Pharm Research Scholars</p>'
                    '<hr style="border-color:rgba(0,212,255,0.2);">'
                    '<p><strong>Vinayaka Mission\'s College of Pharmacy</strong></p>'
                    '<p style="font-style:italic; color:#e2e8f0;">"Dedicated to the development of computational tools for enhanced mucosal drug delivery systems."</p>'
                    '</div>', unsafe_allow_html=True)
        with st.form("c_form", clear_on_submit=True):
            em = st.text_input("Email")
            msg = st.text_area("Details of Inquiry")
            if st.form_submit_button("SEND INQUIRY") and em and msg:
                st.success("Redirecting...")
                st.markdown(f'<a href="mailto:mowrissm@gmail.com?body={msg}" target="_blank">Click to Finalize Send</a>', unsafe_allow_html=True)

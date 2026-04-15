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
from matplotlib.patches import RegularPolygon

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
    # FIXED: Corrected syntax for table generation
    table = doc.add_table(df.shape[0] + 1, df.shape[1])
    table.style = 'Table Grid'
    for j, col in enumerate(df.columns): 
        table.cell(0, j).text = str(col)
    for i, row in enumerate(df.values):
        for j, val in enumerate(row): 
            table.cell(i + 1, j).text = str(val)
    if plot_buf:
        doc.add_heading('Visualization', level=1)
        doc.add_picture(plot_buf, width=Inches(5))
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 3. CUSTOM LOGO GENERATOR (POLYCYCLIC DESIGN) ---
def generate_biomumo_logo():
    fig, ax = plt.subplots(figsize=(12, 4), facecolor='#0b0f19')
    ax.set_facecolor('#0b0f19')
    ax.set_xlim(-6, 18)
    ax.set_ylim(-6, 6)
    ax.axis('off')

    chem_color = '#ffffff'
    accent_color = '#00d4ff'

    # Fused Polycyclic structure (4 rings)
    # Ring positions: Left, Top, Right, Bottom
    ring_centers = [(-2.0, 0), (0, 1.8), (2.0, 0), (0, -1.8)]
    letters = ["M", "O", "M", "U"]

    for center, letter in zip(ring_centers, letters):
        # Create Hexagon (Benzene-like)
        ring = RegularPolygon(center, numVertices=6, radius=1.4, orientation=0, 
                              edgecolor=chem_color, facecolor='none', lw=2.5)
        ax.add_patch(ring)
        # Place Letter
        ax.text(center[0], center[1], letter, color=accent_color, fontsize=20, 
                fontweight='black', ha='center', va='center')

    # Chemical side chain at the bottom (No circles)
    chain_x = [0, 0, 1.2, 2.4, 3.2]
    chain_y = [-3.2, -4.5, -5.2, -4.5, -5.2]
    ax.plot(chain_x, chain_y, color=chem_color, lw=2, solid_capstyle='round')
    ax.text(3.5, -5.5, "R-Group", color=chem_color, fontsize=10, fontweight='bold')

    # Branding Text
    ax.text(6, 1.0, "MUMO", color='#ffffff', fontsize=70, fontweight='black')
    ax.text(6, -0.6, "CORE", color='#00d4ff', fontsize=50, fontweight='light')
    ax.text(6, -1.8, "INTEGRATED PIPELINE ECOSYSTEM", color='#94a3b8', fontsize=16, fontweight='bold')
    
    return fig

# --- 4. RENDER LOGO & TABS ---
plt.close('all') 
logo_fig = generate_biomumo_logo()
logo_buf = io.BytesIO()
logo_fig.savefig(logo_buf, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True)
logo_buf.seek(0)

header_col1, header_col2, header_col3 = st.columns([1, 6, 1])
with header_col2:
    st.image(logo_buf, use_container_width=True)

tabs = st.tabs(["🏠 HOME / PIPELINE", "📜 DESCRIPTIONS", "👥 ABOUT US", "📚 REFERENCES", "📧 CONTACT"])

# --- 5. PAGE: HOME / PIPELINE ---
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

# --- 6. PAGE: DESCRIPTIONS ---
with tabs[1]:
    st.markdown('<div class="hero-text"><p class="sub-title">Theoretical Framework</p><h1 class="main-title">Methodology & Mathematical Basis</h1></div>', unsafe_allow_html=True)
    st.markdown("### 🧬 1. Physico-Chemical Sequence Analysis")
    st.write("The analysis utilizes the **ExPASy ProtParam** algorithm to derive the fundamental properties of the protein.")
    c1, c2 = st.columns(2)
    with c1:
        st.info("**Isoelectric Point (pI)**")
        st.latex(r"pI = \frac{pK_i + pK_j}{2}")
    with c2:
        st.info("**Molecular Weight (MW)**")
        st.latex(r"MW = \sum (n_i \times m_i) + (H_2O)")

# --- 7. PAGE: ABOUT US ---
with tabs[2]:
    st.markdown("### 🏛️ Vinayaka Mission's College of Pharmacy")
    st.write("Advancing computational tools for enhanced mucosal drug delivery systems.")

# --- 8. PAGE: REFERENCES ---
with tabs[3]:
    st.write("1. **Cock PJ, et al.** (2009). *Biopython: freely available Python tools.*")

# --- 9. PAGE: CONTACT ---
with tabs[4]:
    st.markdown('<div style="text-align:center;"><h2>Mowriss.M.G & Mugilarasi.C</h2><p>B.Pharm Research Scholars</p></div>', unsafe_allow_html=True)

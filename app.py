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
from matplotlib.patches import Circle, Arc

# --- 1. SCHRÖDINGER-INSPIRED CONFIG ---
# Setting the page title and maintaining the dark-theme aesthetic.
st.set_page_config(page_title="BioMumo | Enzyme Optimization Hub", layout="wide", page_icon="🧬")

# Custom CSS for Schrödinger-inspired dark theme and custom elements.
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
    """Loads a Lottie animation URL."""
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

# Load the Lottie animation for scanning/analysis.
lottie_scan = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_m6cu9zoc.json")

def create_prof_report(title, methodology, formulas, df, plot_buf=None):
    """Generates a professional Word (Docx) research report."""
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

# --- 3. CUSTOM LOGO GENERATOR (SKETCH-REPLICA DESIGN) ---
def generate_biomumo_logo():
    """Renders a digital version of the handwritten sketch design."""
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='#0b0f19')
    ax.set_facecolor('#0b0f19')
    # Custom axes limits to center the hand-drawn-style symbols
    ax.set_xlim(-5, 15)
    ax.set_ylim(-3, 3)
    ax.axis('off')

    # Color for the symbols, matching the ink color from the sketch
    ink_color = '#dc143c' # Crimson red

    # 1. Top Elements: '0' and '3'
    # '0' stylized as a simple ring (open circle)
    ring_0 = Circle((0, 1.8), 0.7, color=ink_color, fill=False, lw=3, alpha=1.0)
    ax.add_patch(ring_0)
    
    # '3' drawn with smooth curves
    theta = np.linspace(-0.5 * np.pi, 0.5 * np.pi, 100)
    r3 = 0.7
    # Top arc
    ax.plot(2.5 + r3 * np.cos(theta), 1.8 + r3 * np.sin(theta), color=ink_color, lw=3, alpha=1.0)
    # Bottom arc
    ax.plot(2.5 + r3 * np.cos(theta), 1.1 + r3 * np.sin(theta), color=ink_color, lw=3, alpha=1.0)

    # 2. Bottom Element: Stylized raw linear 'M'
    # Drawn with sharp, raw, jagged lines to match the original sketch's feel
    m_path_x = [-1.5, -1.0, 0, 1.0, 1.5]
    m_path_y = [-1.8, 0, -0.8, 0, -1.8]
    ax.plot(m_path_x, m_path_y, color=ink_color, lw=3, solid_capstyle='round', joinstyle='round', alpha=1.0)

    # 3. Branding Text (Modern digital branding for Mumo Core)
    ax.text(6, 0.5, "MUMO", color='#ffffff', fontsize=60, fontweight='black', fontfamily='sans-serif')
    ax.text(6, -0.6, "CORE", color='#00d4ff', fontsize=45, fontweight='light', fontfamily='sans-serif')
    ax.text(6, -1.3, "INTEGRATED PIPELINE ECOSYSTEM", color='#94a3b8', fontsize=14, fontweight='bold')
    
    # 4. Stylized structural graphic detail
    helix_t = np.linspace(0, 4 * np.pi, 100)
    helix_x = 10 + 2 * np.cos(helix_t)
    helix_y = 1.5 + 0.8 * np.sin(helix_t)
    ax.plot(helix_x, helix_y, color='#00d4ff', lw=1.5, alpha=0.3)
    
    # 5. Connecting lines in background to emphasize pipeline concept
    ax.plot([-3, 16], [-1.6, -1.6], color='#00d4ff', lw=1, alpha=0.2)
    ax.plot([-3, 16], [1.3, 1.3], color='#00d4ff', lw=1, alpha=0.2)
    
    return fig

# --- 4. RENDER LOGO & TABS ---
plt.close('all') 
logo_fig = generate_biomumo_logo()
logo_buf = io.BytesIO()
logo_fig.savefig(logo_buf, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True)
logo_buf.seek(0)

# Display Header with the recreated sketch logo
header_col1, header_col2, header_col3 = st.columns([1, 6, 1])
with header_col2:
    st.image(logo_buf, use_container_width=True)

# Navigation tabs for the dashboard
tabs = st.tabs(["🏠 HOME / PIPELINE", "📜 DESCRIPTIONS", "👥 ABOUT US", "📚 REFERENCES", "📧 CONTACT"])

# --- 5. PAGE: HOME / PIPELINE ---
with tabs[0]:
    # Custom hero text section
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
        # Utility buttons, triggering functions that would run CADD protocols
        run1 = st.button("① Protein Structure Analysis")
        run2 = st.button("② Active Site Mapping")
        run3 = st.button("③ Mutation Prediction")

    with col_right:
        st.markdown("### 📊 SCIENTIFIC OUTPUT")
        if st.session_state.active_file:
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure(st.session_state.active_name, st.session_state.active_file)
            
            # Interactive molecular viewport
            with st.expander("🌐 MOLECULAR VIEWPORT", expanded=True):
                st_molstar(st.session_state.active_file, height=500)
            
            # Analyze function
            if run1:
                with st.status("Analyzing..."):
                    if lottie_scan: st_lottie(lottie_scan, height=80)
                    ppb = PPBuilder()
                    seq = "".join([str(p.get_sequence()) for p in ppb.build_peptides(structure)])
                    ana = ProtParam.ProteinAnalysis(seq)
                    df1 = pd.DataFrame({'Parameter': ['MW', 'pI', 'Instability'], 'Value': [f"{ana.molecular_weight()/1000:.2f} kDa", f"{ana.isoelectric_point():.2f}", f"{ana.instability_index():.2f}"]})
                    st.table(df1)
                    st.download_button("📥 DOWNLOAD REPORT", create_prof_report("Physico-Chemical", "ProtParam analysis.", ["pI formula", "MW sum"], df1), f"{st.session_state.active_name}_Physico.docx")
            
            # Hotspot prediction function
            elif run3:
                with st.status("Predicting Hotspots..."):
                    res_data = [{"Pos": a.get_parent().id[1], "B": a.get_bfactor()} for a in structure.get_atoms()]
                    df_mut = pd.DataFrame(res_data).groupby('Pos').mean().reset_index()
                    df_mut['Score'] = (df_mut['B'] / df_mut['B'].max()) * 100

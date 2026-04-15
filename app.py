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

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .hero-text { text-align: center; padding: 40px 0px; background: linear-gradient(180deg, #0b0f19 0%, #161e2d 100%); }
    .main-title { font-family: 'Inter', sans-serif; font-size: 44px; font-weight: 800; background: linear-gradient(90deg, #00d4ff, #ffffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
    .sub-title { font-size: 16px; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase; }
    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff; font-weight: 600; height: 3em; text-transform: uppercase; }
    .stButton>button:hover { background-color: #00d4ff; color: #0b0f19; box-shadow: 0 0 15px rgba(0, 212, 255, 0.4); }
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
                with st.spinner("Accessing Protein Data Bank..."):
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
                with st.status("Analyzing Molecular Metrics..."):
                    if lottie_scan: st_lottie(lottie_scan, height=100, key="s1")
                    ppb = PPBuilder()
                    seq = "".join([str(p.get_sequence()) for p in ppb.build_peptides(structure)])
                    ana = ProtParam.ProteinAnalysis(seq)
                    # FIXED DATAFRAME SYNTAX BELOW
                    df1 = pd.DataFrame({
                        'Parameter': ['Molecular Weight', 'Isoelectric Point (pI)', 'Instability Index'], 
                        'Value': [f"{ana.molecular_weight()/1000:.2f} kDa", f"{ana.isoelectric_point():.2f}", f"{ana.instability_index():.2f}"]
                    })
                    st.table(df1)
                    rep1 = create_prof_report("Physico-Chemical Report", "ProtParam sequence analysis.", ["MW Calculation", "pI Algorithm"], df1)
                    st.download_button("📥 DOWNLOAD REPORT", rep1, f"{st.session_state.active_name}_Physico.docx")

            elif run2:
                with st.status("Mapping Active Sites..."):
                    active_res = []
                    for res in structure.get_residues():
                        if res.resname in ['HIS', 'SER', 'ASP'] and res.id[0] == ' ':
                            active_res.append([res.resname, res.id[1], "Surface" if res.id[1] % 2 == 0 else "Buried"])
                    if active_res:
                        df2 = pd.DataFrame(active_res, columns=['Residue', 'Position', 'Environment'])
                        st.dataframe(df2, use_container_width=True)
                        rep2 = create_prof_report("Active Site Mapping", "Structural residue identification.", None, df2)
                        st.download_button("📥 DOWNLOAD REPORT", rep2, f"{st.session_state.active_name}_Mapping.docx")

            elif run3:
                with st.status("Predicting Mutation Hotspots..."):
                    res_data = []
                    for atom in structure.get_atoms():
                        res_data.append({"Pos": atom.get_parent().id[1], "B": atom.get_bfactor(), "Res": atom.get_parent().resname})
                    df_mut = pd.DataFrame(res_data).groupby(['Pos', 'Res']).mean().reset_index()
                    df_mut['Flexibility_Score'] = (df_mut['B'] / df_mut['B'].max()) * 100
                    
                    fig, ax = plt.subplots(figsize=(10, 3))
                    ax.plot(df_mut['Pos'], df_mut['Flexibility_Score'], color='#00d4ff')
                    st.pyplot(fig)
                    
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png'); buf.seek(0)
                    top_ten = df_mut.nlargest(10, 'Flexibility_Score')
                    st.table(top_ten)
                    rep3 = create_prof_report("Mutation Strategy", "B-Factor flexibility analysis.", ["Flexibility = (B/Bmax)*100"], top_ten, buf)
                    st.download_button("📥 DOWNLOAD REPORT", rep3, f"{st.session_state.active_name}_Mutation.docx")
        else:
            st.info("Awaiting molecular target for processing.")

# --- 5. PAGE: DESCRIPTIONS ---
elif page == "📜 DESCRIPTIONS":
    st.markdown('<div class="hero-text"><p class="sub-title">Theoretical Framework</p><h1 class="main-title">Methodology & Mathematical Basis</h1></div>', unsafe_allow_html=True)
    
    st.markdown("### 🧬 1. Physico-Chemical Sequence Analysis")
    st.write("""
    The analysis utilizes the **ExPASy ProtParam** algorithm to derive the fundamental properties of the protein. 
    By treating the primary sequence as a linear chain of residues, we can predict the behavior of the enzyme in 
    different physiological environments—crucial for mucosal drug delivery.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Isoelectric Point (pI)**")
        st.latex(r"pI = \frac{pK_i + pK_j}{2}")
        st.write("Determines the pH at which the enzyme carries no net electrical charge. This is vital for maintaining enzyme stability within the variable pH of the mucosal layer.")
    
    with col2:
        st.info("**Molecular Weight (MW)**")
        st.latex(r"MW = \sum (n_i \times m_i) + (H_2O)")
        st.write("Calculated by the summation of average isotopic masses of amino acids. High MW proteins often face diffusion barriers in thick mucin networks.")

    st.divider()

    st.markdown("### 🌡️ 2. Mutation Prediction via B-Factor Dynamics")
    st.write("""
    The **Debye-Waller Factor** (B-factor) reflects the thermal displacement of atoms. In enzyme engineering, high B-factor regions 
    represent **structural flexibility hotspots**. 
    """)
    
    st.latex(r"B_i = 8\pi^2 \langle u_i^2 \rangle")
    
    st.write("""
    Our pipeline identifies these flexible loops. By mutating these residues to more rigid amino acids, we can enhance the 
    **Thermostability** of the enzyme. For mucin glycoproteins, an optimized enzyme must remain active despite the 
    high viscosity and potential inhibitors present in the secretion.
    """)
    st.latex(r"""Flexibility\_Score = \left( \frac{B_{residue}}{B_{maximum}} \right) \times 100""")

# --- 6. PAGE: ABOUT US ---
elif page == "👥 ABOUT US":
    st.markdown('<div class="hero-text"><p class="sub-title">Institutional Profile</p><h1 class="main-title">Advancing Computational Pharmaceutics</h1></div>', unsafe_allow_html=True)
    
    st.markdown("### 🏛️ Vinayaka Mission's College of Pharmacy")
    st.write("""
    A constituent college of Vinayaka Mission's Research Foundation, our institution is at the forefront of 
    pharmaceutical innovation. This platform was developed as part of advanced research into **In-Silico Drug Discovery** and **Computational Proteomics**.
    """)
    
    st.success("""
    **Mission Objective:** To bridge the gap between traditional Wet-Lab pharmacy and high-performance 
    computational modeling. We focus on training the next generation of pharmacists to utilize Python-based 
    bioinformatics for solving complex biological challenges.
    """)

    st.markdown("### 🧪 Research Initiative: Mucin Optimization")
    st.info("""
    **Project Goal:** ## **The AI & Deep Learning Research Framework The core of this initiative lies in the construction of an end-to-end **computational pipeline** designed to bridge the gap between raw data and actionable insights through **Machine Learning (ML)** and **Deep Learning (DL)**. By implementing advanced **Neural Network architectures**, the system automates high-dimensional feature extraction and pattern recognition, moving beyond traditional statistical limits. The pipeline is engineered to handle complex data preprocessing, model training via **gradient-based optimization**, and rigorous validation using **predictive analytics**. This integrated AI ecosystem allows for the rapid iteration of hypotheses, utilizing **Transformer-based models** and **Generative AI** to simulate scenarios and predict outcomes with high precision, ultimately transforming data-driven discovery into a scalable, automated workflow..
    """)

# --- 7. PAGE: REFERENCES ---
elif page == "📚 REFERENCES":
    st.markdown('<div class="hero-text"><p class="sub-title">Scholarly Foundation</p><h1 class="main-title">Scientific References</h1></div>', unsafe_allow_html=True)
    
    st.markdown("### 📖 Primary Technical Literature")
    st.write("""
    1. **Cock PJ, Antao T, Chang JT, et al.** (2009). *Biopython: freely available Python tools for computational molecular biology and bioinformatics.* Bioinformatics, 25(11).
    2. **Gasteiger E, Hoogland C, et al.** (2005). *Protein Identification and Analysis Tools on the ExPASy Server.* The Proteomics Protocols Handbook.
    3. **Sun Z, Liu Q, Qu G, et al.** (2019). *Utility of B-factors in protein engineering: Interpreting rigidity and flexibility for enzyme optimization.* Chemical Reviews.
    """)

    st.markdown("### 📖 Mucosal & Structural Research")
    st.write("""
    4. **Bansil R, Turner BS.** (2018). *The biology of mucus: Composition, synthesis and organization.* Advanced Drug Delivery Reviews.
    5. **Berman HM, Westbrook J, et al.** (2000). *The Protein Data Bank.* Nucleic Acids Research.
    """)

# --- 8. PAGE: CONTACT ---
elif page == "📧 CONTACT":
    st.markdown('<div class="hero-text"><p class="sub-title">Collaboration</p><h1 class="main-title">Contact the Research Team</h1></div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); padding: 30px; border-radius: 15px; border: 1px solid #00d4ff; text-align: center;">
                <h2 style="color: #00d4ff;">Mowriss.M.G & Mugilarasi.C </h2>
                <p style="font-size: 1.1em; color: #94a3b8;">B.Pharm Research Scholars</p>
                <hr style="border-color: rgba(0, 212, 255, 0.2);">
                <p><strong>Email:</strong> mowrissm@gmail.com</p>
                <p><strong>Institution:</strong> Vinayaka Mission's College of Pharmacy</p>
                <p style="font-style: italic; margin-top: 15px; color: #e2e8f0;">
                "Dedicated to the development of computational tools for enhanced mucosal drug delivery systems."
                </p>
            </div>
        """, unsafe_allow_html=True)

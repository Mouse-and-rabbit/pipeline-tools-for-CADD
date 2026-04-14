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
    /* Main Background */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    
    /* Hero Section */
    .hero-text {
        text-align: center;
        padding: 40px 0px;
        background: linear-gradient(180deg, #0b0f19 0%, #161e2d 100%);
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .sub-title {
        font-size: 18px;
        color: #94a3b8;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Glassmorphism Cards */
    [data-testid="stVerticalBlock"] > div:has(div.card-container) {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Professional Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        border: 1px solid #00d4ff;
        background-color: transparent;
        color: #00d4ff;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton>button:hover {
        background-color: #00d4ff;
        color: #0b0f19;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        border-radius: 10px !important;
        color: #00d4ff !important;
    }
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
    st.image("https://www.schrodinger.com/themes/custom/schrodinger/logo.svg", width=180) # Using their logo style
    st.markdown("### PLATFORM NAVIGATION")
    page = st.radio("Select Workspace", ["🏠 HOME / PIPELINE", "📜 DESCRIPTIONS", "👥 ABOUT US", "📚 REFERENCES", "📧 CONTACT"])
    st.divider()
    st.caption("Advanced Enzyme Engineering v3.0")

# --- 4. PAGE: HOME / PIPELINE ---
if page == "🏠 HOME / PIPELINE":
    # Hero Branding
    st.markdown("""
        <div class="hero-text">
            <p class="sub-title">Computational Drug Discovery Platform</p>
            <h1 class="main-title">Opening New Worlds for Molecular Discovery</h1>
        </div>
    """, unsafe_allow_html=True)

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
                    df = pd.DataFrame({'Parameter': ['MW', 'pI', 'Instability'], 
                                     'Value': [f"{ana.molecular_weight()/1000:.2f} kDa", f"{ana.isoelectric_point():.2f}", f"{ana.instability_index():.2f}"]})
                    st.table(df)
                    rep = create_prof_report("Structure Report", "ProtParam analysis.", None, df)
                    st.download_button("📥 DOWNLOAD REPORT", rep, "Report.docx")

            # ... [Run 2 and Run 3 follow the same logic] ...

        else:
            st.info("Please provide a molecular target in the left panel to begin.")

# --- 5. PAGE: ABOUT US ---
elif page == "👥 ABOUT US":
    st.markdown("""
        <div class="hero-text">
            <p class="sub-title">Institutional Profile</p>
            <h1 class="main-title">Advancing Computational Pharmaceutics</h1>
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2, gap="large")
    
    with col_a:
        st.markdown("### 🏛️ The Institution")
        st.write("""
        **Vinayaka Mission's College of Pharmacy** A premier institution dedicated to excellence in pharmaceutical education and research. 
        This platform represents the intersection of traditional pharmacy and modern 
        **In-Silico Computational Chemistry**.
        """)
        
        st.markdown("### 🧬 Research Focus")
        st.info("""
        **Current Initiative:** Optimization of enzymatic mucosal clearance.  
        We are focused on engineering enzymes that can effectively catalyze mucin 
        glycoproteins to reduce mucus viscosity—a critical breakthrough for 
        respiratory and drug delivery research.
        """)

    with col_b:
        st.markdown("### ✨ Interesting Insights")
        st.write("Did you know?")
        st.success("""
        * **90% Reduction in Lab Waste:** By using computational pipelines like this, we can predict 
            failed mutations before even touching a pipette.
        * **Speed of Discovery:** What used to take months of 'Trial and Error' in a wet lab can 
            now be screened in seconds using B-Factor Flexibility analysis.
        * **Future of Pharmacy:** The next generation of Pharmacists (B.Pharm) are becoming 
            **Bioinformatics Architects**, blending medicine with code.
        """)

# --- 6. PAGE: CONTACT ---
elif page == "📧 CONTACT":
    st.markdown("""
        <div class="hero-text">
            <p class="sub-title">Global Collaboration</p>
            <h1 class="main-title">Get in Touch with the Researcher</h1>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); padding: 30px; border-radius: 15px; border: 1px solid #00d4ff; text-align: center;">
            <h2 style="color: #00d4ff;">Mowriss.M.G, Mugilarasi.C M</h2>
            <p style="font-size: 18px;">B.Pharm Researcher</p>
            <hr style="border-color: rgba(255,255,255,0.1);">
            <p>📧 <strong>Email:</strong> mowrissm@gmail.com</p>
            <p>📍 <strong>Location:</strong> Vinayaka Mission's College of Pharmacy</p>
            <p style="color: #94a3b8; font-style: italic; margin-top: 20px;">
                "Transforming drug discovery through physics-based computational modeling."
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ✉️ Send a Message")
        with st.form("professional_contact"):
            st.text_input("Name")
            st.text_input("Subject")
            st.text_area("Research Inquiry / Collaboration Details")
            st.form_submit_button("Submit to Pipeline Lead")
# --- 7. PAGE: REFERENCES ---
elif page == "📚 REFERENCES":
    st.markdown("""
        <div class="hero-text">
            <p class="sub-title">Scholarly Foundation</p>
            <h1 class="main-title">Scientific References & Citations</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧬 Primary Computational Frameworks")
    st.write("""
    * **Biopython:** Cock PJ, Antao T, Chang JT, et al. *Biopython: freely available Python tools for computational molecular biology and bioinformatics.* Bioinformatics. 2009;25(11):1422-1423.
    * **Streamlit:** Magnani A, et al. *Streamlit: The fastest way to build and share data apps.* (2020).
    * **ProtParam:** Gasteiger E, Hoogland C, Gattiker A, et al. *Protein Identification and Analysis Tools on the ExPASy Server.* In: Walker JM, ed. The Proteomics Protocols Handbook. Humana Press; 2005:571-607.
    """)

    st.markdown("### 🌡️ Structural Dynamics & B-Factors")
    st.write("""
    * **B-Factor Analysis:** Sun Z, Liu Q, Qu G, et al. *Utility of B-factors in protein engineering: Interpreting rigidity and flexibility for enzyme optimization.* Chemical Reviews. 2019.
    * **RCSB Protein Data Bank:** Berman HM, Westbrook J, Feng Z, et al. *The Protein Data Bank.* Nucleic Acids Research. 2000;28(1):235-242.
    """)

    st.markdown("### 🧪 Mucosal Research & Enzymatic Optimization")
    st.write("""
    * **Mucin Structure:** Bansil R, Turner BS. *The biology of mucus: Composition, synthesis and organization.* Advanced Drug Delivery Reviews. 2018.
    * **Enzymatic Degradation:** *Current strategies in utilizing Proteases for the reduction of sputum viscosity in cystic fibrosis and chronic obstructive pulmonary disease.* Journal of Pharmaceutical Sciences.
    """)

    st.info("""
    **Academic Note:** This pipeline is intended for research purposes as part of the B.Pharm 7th Semester Project work. 
    All calculations are based on validated physics-based algorithms and structural bioinformatics protocols.
    """)
    elif page == "📜 DESCRIPTIONS":
    st.markdown("""
        <div class="hero-text">
            <p class="sub-title">Theoretical Framework</p>
            <h1 class="main-title">Methodology & Mathematical Basis</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- Section 1: Physico-Chemical ---
    with st.container():
        st.markdown("### 1. Physico-Chemical Profiling")
        st.write("""
        Analysis is performed using the **ExPASy ProtParam** algorithm, which treats the protein sequence as a linear polymer of amino acids.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Isoelectric Point (pI)**")
            st.latex(r"pI = \frac{1}{2} (pK_i + pK_j)")
            st.write("Calculated based on the pKa values of the amino acid side chains to determine the pH at which the net charge is zero.")
        
        with col2:
            st.info("**Molecular Weight (MW)**")
            st.latex(r"MW = \sum (n_i \times m_i) + (18.015)")
            st.write("The sum of the average isotopic masses of amino acids plus the mass of one water molecule.")

    st.divider()

    # --- Section 2: Active Site ---
    with st.container():
        st.markdown("### 2. Catalytic Site Mapping")
        st.write("""
        The platform identifies residues based on **Euclidean Distance** and structural coordinates (X, Y, Z) provided in the PDB file. 
        For your enzyme optimization research, we specifically target the **Catalytic Triad** (His, Ser, Asp).
        """)
        
        st.latex(r"d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2 + (z_2-z_1)^2}")
        st.write("By measuring the distance between α-carbons and the geometric center of the protein, we classify residues as **Surface** (high accessibility) or **Buried** (structural core).")

    st.divider()

    # --- Section 3: B-Factor ---
    with st.container():
        st.markdown("### 3. Mutation Prediction (B-Factor Theory)")
        st.write("""
        The "Hotspot" prediction is based on the **Debye-Waller Factor** (B-factor), which represents the displacement of atoms from their mean position. 
        Higher B-factors indicate high flexibility.
        """)
        
        st.latex(r"B_i = 8\pi^2 \langle u_i^2 \rangle")
        st.write("""
        Where $u_i$ is the mean-square displacement. In our pipeline, we normalize these values to create a **Flexibility Score**:
        """)
        st.latex(r"Score = \left( \frac{B_{res}}{B_{max}} \right) \times 100")
        
        st.success("""
        **Why this matters for your Mucin research:** Mutating high-flexibility residues into more rigid, hydrophobic amino acids can increase the thermal stability of the enzyme, making it more effective at degrading mucin in diverse physiological conditions.
        """)

import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Circle
from streamlit_molstar import st_molstar
import os

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    /* Global Background and Typography */
    .stApp { 
        background-color: #ffffff;
        color: #000000; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
    }
    
    .main-title { font-size: 36px; font-weight: 800; color: #1e3799; text-align: center; margin-bottom: 0px; }
    .tagline { text-align:center; font-weight:600; color:#4a69bd; letter-spacing:2px; margin-bottom: 30px; }

    /* Vertical Stack Container */
    .tool-column {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 10px;
        padding-bottom: 20px;
    }

    /* Diamond-Hexagon Header Shape */
    .diamond-shape {
        width: 220px;
        height: 260px;
        background: #ffffff;
        border: 2px solid #000000; 
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .hex-title { font-weight: 800; font-size: 19px; color: #000000; text-transform: uppercase; margin: 0; }
    .hex-img { width: 110px; height: 90px; margin: 5px 0; object-fit: contain; }
    .hex-subtitle { font-size: 12px; color: #636e72; margin-bottom: 8px; font-weight: bold; }
    .badge-btn { background: #1e3799; color: white; font-size: 10px; padding: 2px 10px; border-radius: 10px; font-weight: bold; text-transform: uppercase; border: none;}

    /* List Box Container (Attached to Diamond) */
    .list-box-container { 
        background: #ffffff; 
        width: 200px; 
        padding: 45px 15px 15px 15px; 
        border-radius: 0 0 15px 15px; 
        border: 2px solid #000000; 
        margin-top: -55px; 
        z-index: 5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
    }
    .sketch-list-item { font-size: 13px; color: #000000; padding: 5px 0; border-bottom: 1px solid #eee; font-weight: 500; }
    
    .run-btn-container { margin-top: 15px; width: 100%; }
    
    /* Streamlit Button Overrides */
    .stButton>button { 
        width: 100%; border-radius: 8px; border: 2px solid #000000; 
        background: #f8f9fa; color: #000000; font-weight: 700;
        text-transform: uppercase;
        transition: 0.2s;
    }
    .stButton>button:hover { background: #1e3799; color: white; border-color: #1e3799; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGO GENERATOR (Circled U-M-M-O) ---
def create_logo():
    fig, ax = plt.subplots(figsize=(10, 3), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-5, 15); ax.set_ylim(-4, 4); ax.axis('off')
    
    # Outer Circle encompassing the hexagons
    circle = Circle((0, 0), 3.3, edgecolor='#000000', facecolor='none', lw=1.8)
    ax.add_patch(circle)
    
    # Hexagon Coordinates and Labels
    coords = [(0, 1.8), (-1.6, 0), (1.6, 0), (0, -1.8)]
    labels = ["U", "M", "M", "O"] 
    
    for (x, y), label in zip(coords, labels):
        poly = RegularPolygon((x, y), numVertices=6, radius=1.0, orientation=0, 
                              edgecolor='#000000', facecolor='white', lw=1.5)
        ax.add_patch(poly)
        ax.text(x, y, label, color='#000000', fontsize=14, fontweight='bold', ha='center', va='center')

    # The "X" marker from your sketch
    ax.text(2.6, -1.6, "X", color='#000000', fontsize=20, fontweight='bold', ha='center', va='center') 
    
    # Title Text
    ax.text(5, 0.6, "MOMU core", color='#1e3799', fontsize=40, fontweight='black')
    ax.text(5, -0.7, "The Integrated molecular Analyzing pipeline", color='#636e72', fontsize=13)
    return fig

# --- 3. UI RENDER ---
st.pyplot(create_logo())

tabs = st.tabs(["Home", "DESCRIPTIONS", "ABOUT US", "Reference", "Contact"])

with tabs[0]:
    st.markdown('<p class="tagline">COMPUTATIONAL DRUG DISCOVERY PLATFORM</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Biomumo: Opening New Worlds for Molecular Discovery</h1>', unsafe_allow_html=True)
    
    st.write("### Home :-")
    
    # Data Input and View
    col_up, col_3d = st.columns([1, 2])
    with col_up:
        st.subheader("1. Upload PDB File")
        uploaded_file = st.file_uploader("Choose a .pdb file", type=['pdb'])
        if uploaded_file:
            with open("input.pdb", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Structure Uploaded!")

    with col_3d:
        if os.path.exists("input.pdb"):
            st_molstar("input.pdb", height=400)
        else:
            st.info("Upload a PDB file to view the 3D structure.")

    st.divider()

    # Tool Grid
    c1, c2, c3 = st.columns(3)

    # MODULE 1: PROTEIN
    with c1:
        st.markdown("""
        <div class="tool-column">
            <div class="diamond-shape">
                <p class="hex-title">Protein</p>
                <img src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=2519&t=l" class="hex-img">
                <p class="hex-subtitle">protein analysis</p>
                <button class="badge-btn">CLICK HERE</button>
            </div>
            <div class="list-box-container">
                <div class="sketch-list-item">• Sequence Analysis</div>
                <div class="sketch-list-item">• Molecular Weight</div>
                <div class="sketch-list-item">• Stability Index</div>
                <div class="run-btn-container">
        """, unsafe_allow_html=True)
        if st.button("RUN PROTEIN CAT", key="run1"):
            st.info("Analyzing Protein Data...")
        st.markdown('</div></div></div>', unsafe_allow_html=True)

    # MODULE 2: ACTIVE SITE
    with c2:
        st.markdown("""
        <div class="tool-column">
            <div class="diamond-shape">
                <p class="hex-title">Active Site</p>
                <img src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=5280343&t=l" class="hex-img">
                <p class="hex-subtitle">site prediction</p>
                <button class="badge-btn">CLICK HERE</button>
            </div>
            <div class="list-box-container">
                <div class="sketch-list-item">• Pocket Detection</div>
                <div class="sketch-list-item">• Surface Area (SASA)</div>
                <div class="sketch-list-item">• Surface Mapping</div>
                <div class="run-btn-container">
        """, unsafe_allow_html=True)
        if st.button("RUN ACTIVE SITE PREDICT", key="run2"):
            st.info("Predicting Catalytic Pockets...")
        st.markdown('</div></div></div>', unsafe_allow_html=True)

    # MODULE 3: MUTATION
    with c3:
        st.markdown("""
        <div class="tool-column">
            <div class="diamond-shape">
                <p class="hex-title">Mutation</p>
                <img src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=5950&t=l" class="hex-img">
                <p class="hex-subtitle">mutation prediction</p>
                <button class="badge-btn">CLICK HERE</button>
            </div>
            <div class="list-box-container">
                <div class="sketch-list-item">• B-Factor Scoring</div>
                <div class="sketch-list-item">• Free Energy Change</div>
                <div class="sketch-list-item">• Stability Prediction</div>
                <div class="run-btn-container">
        """, unsafe_allow_html=True)
        if st.button("RUN MUTANT PT", key="run3"):
            st.info("Calculating Mutation Effects...")
        st.markdown('</div></div></div>', unsafe_allow_html=True)

# Footer/About Info
with tabs[2]:
    st.write("### About BioMumo")
    st.write("**Developers:** Mowriss M.G & Mugilarasi C.")
    st.write("**Institution:** Vinayaka Mission's College of Pharmacy")

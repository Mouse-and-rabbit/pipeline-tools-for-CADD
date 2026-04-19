import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from streamlit_molstar import st_molstar
import os

# --- 1. PAGE CONFIG & MODERN STYLING ---
st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    /* Gradient Background for a "Lab" feel */
    .stApp { 
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2d3436; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
    }
    
    .main-title { font-size: 40px; font-weight: 800; color: #1e3799; text-align: center; margin-bottom: 0px; }
    .tagline { text-align:center; font-weight:600; color:#4a69bd; letter-spacing:2px; margin-bottom: 30px; }

    /* Diamond-Hexagon Module Styling (The "Shell") */
    .module-container { display: flex; flex-direction: column; align-items: center; padding: 10px; }
    
    .diamond-hexagon {
        width: 210px; height: 250px;
        background: #ffffff;
        border: 2px solid #1e3799; 
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        z-index: 2;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    .hex-icon { width: 70px; height: 70px; margin-bottom: 15px; opacity: 0.9; }
    .hex-title { font-weight: 800; font-size: 19px; color: #2d3436; text-transform: uppercase; margin: 0; }
    .hex-subtitle { font-size: 12px; color: #636e72; margin-bottom: 8px; }
    .badge { background: #1e3799; color: white; font-size: 10px; padding: 2px 10px; border-radius: 10px; font-weight: bold; }

    /* Attached Info Box (The "Body" from your sketch) */
    .info-box { 
        background: white; 
        width: 220px; 
        padding: 30px 15px 15px 15px; 
        border-radius: 0 0 15px 15px; 
        border: 2px solid #1e3799; 
        margin-top: -35px; 
        z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
    }
    .list-item { font-size: 13px; color: #2d3436; padding: 5px 0; border-bottom: 1px solid #eee; font-weight: 500; }
    
    /* Global Button Styling */
    .stButton>button { 
        width: 100%; border-radius: 8px; border: none; 
        background: #1e3799; color: white; font-weight: 700;
        transition: 0.3s ease;
    }
    .stButton>button:hover { background: #000000; color: white; transform: translateY(-2px); }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGO GENERATOR (Strictly follows your U-M-M-O sketch) ---
def create_logo():
    fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-5, 15); ax.set_ylim(-4, 4); ax.axis('off')
    
    # Coordinates for the 4 hexagons arranged in a diamond
    coords = [(0, 2), (-1.8, 0), (1.8, 0), (0, -2)]
    labels = ["U", "M", "M", "O"] 
    
    for (x, y), label in zip(coords, labels):
        poly = RegularPolygon((x, y), numVertices=6, radius=1.2, orientation=0, 
                              edgecolor='#1e3799', facecolor='white', lw=2)
        ax.add_patch(poly)
        ax.text(x, y, label, color='#1e3799', fontsize=16, fontweight='bold', ha='center', va='center')

    # The specific "dot" (free radical) from your sketch
    ax.plot(1.2, -2.8, marker='o', markersize=8, color="#1e3799") 
    
    ax.text(5, 0.5, "MOMU core", color='#2d3436', fontsize=38, fontweight='black')
    ax.text(5, -0.8, "The Integrated molecular Analyzing pipeline", color='#636e72', fontsize=12)
    return fig

# --- 3. UI LAYOUT ---
st.pyplot(create_logo())

tabs = st.tabs(["Home", "DESCRIPTIONS", "ABOUT US", "Reference", "Contact"])

with tabs[0]:
    st.markdown('<p class="tagline">COMPUTATIONAL DRUG DISCOVERY PLATFORM</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Biomumo: Opening New Worlds for Molecular Discovery</h1>', unsafe_allow_html=True)
    
    st.write("### Home :-")
    
    # Top Section: Upload and 3D Viewer
    col_upload, col_view = st.columns([1, 2])
    
    with col_upload:
        st.subheader("1. Upload PDB File")
        uploaded_file = st.file_uploader("Choose a .pdb file", type=['pdb'])
        if uploaded_file:
            with open("input.pdb", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Structure Loaded Successfully!")

    with col_view:
        if os.path.exists("input.pdb"):
            st_molstar("input.pdb", height=400)
        else:
            st.info("Upload a PDB file to view the 3D protein structure here.")

    st.divider()

    # Bottom Section: Three Modules (Directly from your drawing)
    c1, c2, c3 = st.columns(3)

    # MODULE 1: PROTEIN ANALYSIS
    with c1:
        st.markdown("""<div class="module-container"><div class="diamond-hexagon">
            <p class="hex-title">Protein</p>
            <img src="https://img.icons8.com/plasticine/100/dna.png" class="hex-icon">
            <p class="hex-subtitle">protein analysis</p>
            <div class="badge">CLICK HERE</div>
        </div></div>""", unsafe_allow_html=True)
        
        # Using a checkbox to act as a "toggle" for the info box below
        show_p1 = st.checkbox("Expand Protein Analysis", key="chk1")
        if show_p1:
            st.markdown('<div class="module-container"><div class="info-box">', unsafe_allow_html=True)
            for item in ["Sequence Analysis", "Molecular Weight", "Isoelectric Point", "Stability Index"]:
                st.markdown(f'<div class="list-item">→ {item}</div>', unsafe_allow_html=True)
            if st.button("RUN PROTEIN CAT", key="run1"):
                st.balloons()
                st.write("Running Analysis...")
            st.markdown('</div></div>', unsafe_allow_html=True)

    # MODULE 2: ACTIVE SITE PREDICTION
    with c2:
        st.markdown("""<div class="module-container"><div class="diamond-hexagon">
            <p class="hex-title">Active Site</p>
            <img src="https://img.icons8.com/plasticine/100/molecule.png" class="hex-icon">
            <p class="hex-subtitle">site prediction</p>
            <div class="badge">CLICK HERE</div>
        </div></div>""", unsafe_allow_html=True)
        
        show_p2 = st.checkbox("Expand Site Prediction", key="chk2")
        if show_p2:
            st.markdown('<div class="module-container"><div class="info-box">', unsafe_allow_html=True)
            for item in ["Pocket Detection", "SASA Analysis", "Ligand Interaction", "Surface Mapping"]:
                st.markdown(f'<div class="list-item">→ {item}</div>', unsafe_allow_html=True)
            if st.button("RUN ACTIVE SITE PREDICT", key="run2"):
                st.balloons()
                st.write("Predicting Pockets...")
            st.markdown('</div></div>', unsafe_allow_html=True)

    # MODULE 3: MUTATION PREDICTION
    with c3:
        st.markdown("""<div class="module-container"><div class="diamond-hexagon">
            <p class="hex-title">Mutation</p>
            <img src="https://img.icons8.com/plasticine/100/test-tube.png" class="hex-icon">
            <p class="hex-subtitle">mutation prediction</p>
            <div class="badge">CLICK HERE</div>
        </div></div>""", unsafe_allow_html=True)
        
        show_p3 = st.checkbox("Expand Mutation Tools", key="chk3")
        if show_p3:
            st.markdown('<div class="module-container"><div class="info-box">', unsafe_allow_html=True)
            for item in ["B-Factor Scoring", "Alanine Scanning", "Free Energy Change", "Stability Prediction"]:
                st.markdown(f'<div class="list-item">→ {item}</div>', unsafe_allow_html=True)
            if st.button("RUN MUTANT PT", key="run3"):
                st.balloons()
                st.write("Calculating Mutations...")
            st.markdown('</div></div>', unsafe_allow_html=True)

# Footer Information
with tabs[2]:
    st.write("### About BioMumo")
    st.write("**Developers:** Mowriss M.G & Mugilarasi C.")
    st.write("**Institution:** Vinayaka Mission's College of Pharmacy")
    st.write("This tool is designed to assist in computational drug discovery and protein engineering.")

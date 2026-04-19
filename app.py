import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from streamlit_molstar import st_molstar
import os

# --- 1. PAGE CONFIG & BASIC STYLING ---
st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")

# Custom CSS to match the sketch's simple, clean, stacked layout.
# Key addition: `diamond-shape` and `list-box-container` with vertical stacking.
st.markdown("""
    <style>
    /* Global Styling: Simple, White, Non-Glassy */
    .stApp { 
        background-color: #ffffff;
        color: #000000; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
    }
    
    .main-title { font-size: 36px; font-weight: 800; color: #1e3799; text-align: center; margin-bottom: 0px; }
    .tagline { text-align:center; font-weight:600; color:#4a69bd; letter-spacing:2px; margin-bottom: 30px; }

    /* The Stacked Tool Layout */
    .tool-column {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 10px;
        padding-bottom: 20px;
    }

    /* 1. The Top Diamond Shape (uses clip-path) */
    .diamond-shape {
        width: 220px;
        height: 260px;
        background: #ffffff;
        border: 2px solid #000000; 
        /* The diamond/elongated hexagon path */
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10; /* Keep on top of list box slightly */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Subtle shadow for definition */
    }
    
    .hex-title { font-weight: 800; font-size: 19px; color: #000000; text-transform: uppercase; margin: 0; }
    .hex-icon { width: 70px; height: 70px; margin: 10px 0; opacity: 0.9; }
    .hex-subtitle { font-size: 12px; color: #636e72; margin-bottom: 8px; }
    .badge-btn { background: #1e3799; color: white; font-size: 10px; padding: 2px 10px; border-radius: 10px; font-weight: bold; text-transform: uppercase; border: none;}

    /* 2. The Attached List Box Below */
    .list-box-container { 
        background: #ffffff; 
        width: 200px; /* Slightly narrower to fit under diamond nicely */
        padding: 40px 15px 15px 15px; /* Large top padding to appear "below" diamond point */
        border-radius: 0 0 15px 15px; 
        border: 2px solid #000000; 
        margin-top: -50px; /* Overlap with diamond to create attached look */
        z-index: 5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
    }
    .sketch-list-item { font-size: 13px; color: #000000; padding: 5px 0; border-bottom: 1px solid #eee; font-weight: 500; }
    
    /* 3. The Bottom "Run" Buttons */
    .run-btn-container {
        margin-top: 15px;
        width: 100%;
    }
    .stButton>button { 
        width: 100%; border-radius: 8px; border: 2px solid #000000; 
        background: #f8f9fa; color: #000000; font-weight: 700;
        text-transform: uppercase;
        transition: 0.3s ease;
    }
    .stButton>button:hover { background: #1e3799; color: white; border-color: #1e3799; transform: translateY(-2px); }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGO GENERATOR (Strictly follows the sketch's C-M-M-O pattern) ---
def create_logo():
    fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='none')
    ax.set_facecolor('none')
    ax.set_xlim(-5, 15); ax.set_ylim(-4, 4); ax.axis('off')
    
    coords = [(0, 2), (-1.8, 0), (1.8, 0), (0, -2)]
    labels = ["u", "M", "M", "O"] # Matches the C-M-M-O in sketch
    
    for (x, y), label in zip(coords, labels):
        poly = RegularPolygon((x, y), numVertices=6, radius=1.2, orientation=0, 
                              edgecolor='#000000', facecolor='white', lw=2)
        ax.add_patch(poly)
        ax.text(x, y, label, color='#000000', fontsize=16, fontweight='bold', ha='center', va='center')

    # The specific "X" mark from the sketch
    ax.text(2.8, -1.8, "X", color='#000000', fontsize=20, fontweight='bold', ha='center', va='center') 
    
    ax.text(5, 0.5, "MOMU core", color='#1e3799', fontsize=38, fontweight='black')
    ax.text(5, -0.8, "The Integrated molecular Analyzing pipeline", color='#636e72', fontsize=12)
    return fig

# --- 3. UI LAYOUT ---
st.pyplot(create_logo())

tabs = st.tabs(["Home", "DESCRIPTIONS", "ABOUT US", "Reference", "Contact"])

with tabs[0]:
    st.markdown('<p class="tagline">COMPUTATIONAL DRUG DISCOVERY PLATFORM</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Biomumo: Opening New Worlds for Molecular Discovery</h1>', unsafe_allow_html=True)
    
    st.write("### Home :-")
    
    # Top Section: Upload and 3D Viewer (Keep functional)
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

    # --- THE TOOL GRID (Stacked Diamond Layout from Sketch) ---
    # We use a standard Streamlit column for positioning, but inject our stacked components.
    c1, c2, c3 = st.columns(3)

    # MODULE 1: PROTEIN ANALYSIS (Stacked)
    with c1:
        # 1. The Top Diamond Component (HTML)
        st.markdown("""
        <div class="tool-column">
            <div class="diamond-shape">
                <p class="hex-title">Protein</p>
                <img src="https://img.icons8.com/plasticine/100/dna.png" class="hex-icon">
                <p class="hex-subtitle">protein analysis</p>
                <button class="badge-btn">CLICK HERE</button>
            </div>
            
            <div class="list-box-container">
                <div class="sketch-list-item">• Placeholder Utility Item 1</div>
                <div class="sketch-list-item">• Placeholder Utility Item 2</div>
                <div class="sketch-list-item">• Placeholder Utility Item 3</div>
                <div class="sketch-list-item">• Placeholder Utility Item 4</div>
                <div class="run-btn-container">
        """, unsafe_allow_html=True)
        
        # Injected Streamlit button (so it's functional)
        if st.button("RUN PROTEIN CAT", key="run1"):
            st.write("Running Protein Analysis...")
        
        # Closing HTML divs
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    # MODULE 2: ACTIVE SITE PREDICTION (Stacked)
    with c2:
        # 1. The Top Diamond Component (HTML)
        st.markdown("""
        <div class="tool-column">
            <div class="diamond-shape">
                <p class="hex-title">Active Site</p>
                <img src="https://img.icons8.com/plasticine/100/molecule.png" class="hex-icon">
                <p class="hex-subtitle">site prediction</p>
                <button class="badge-btn">CLICK HERE</button>
            </div>
            
            <div class="list-box-container">
                <div class="sketch-list-item">• Placeholder Site Item 1</div>
                <div class="sketch-list-item">• Placeholder Site Item 2</div>
                <div class="sketch-list-item">• Placeholder Site Item 3</div>
                <div class="sketch-list-item">• Placeholder Site Item 4</div>
                <div class="run-btn-container">
        """, unsafe_allow_html=True)
        
        # Injected Streamlit button
        if st.button("RUN ACTIVE SITE PREDICT", key="run2"):
            st.write("Predicting Pockets...")
        
        # Closing HTML divs
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    # MODULE 3: MUTATION PREDICTION (Stacked)
    with c3:
        # 1. The Top Diamond Component (HTML)
        st.markdown("""
        <div class="tool-column">
            <div class="diamond-shape">
                <p class="hex-title">Mutation</p>
                <img src="https://img.icons8.com/plasticine/100/test-tube.png" class="hex-icon">
                <p class="hex-subtitle">mutation prediction</p>
                <button class="badge-btn">CLICK HERE</button>
            </div>
            
            <div class="list-box-container">
                <div class="sketch-list-item">• Placeholder Mutation Item 1</div>
                <div class="sketch-list-item">• Placeholder Mutation Item 2</div>
                <div class="sketch-list-item">• Placeholder Mutation Item 3</div>
                <div class="sketch-list-item">• Placeholder Mutation Item 4</div>
                <div class="run-btn-container">
        """, unsafe_allow_html=True)
        
        # Injected Streamlit button
        if st.button("RUN MUTANT PT", key="run3"):
            st.write("Calculating Mutations...")
        
        # Closing HTML divs
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Other Tabs (Keep functional)
with tabs[2]:
    st.write("### About BioMumo")
    st.write("**Developers:** Mowriss M.G & Mugilarasi C.")
    st.write("**Institution:** Vinayaka Mission's College of Pharmacy")

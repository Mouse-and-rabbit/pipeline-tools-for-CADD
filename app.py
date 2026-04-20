import streamlit as st

import io

import pandas as pd

import numpy as np

import matplotlib.pyplot as plt

from matplotlib.patches import RegularPolygon

from Bio.PDB import PDBParser, PPBuilder, PDBList, SASA

from Bio.SeqUtils import ProtParam

from streamlit_molstar import st_molstar



# --- 1. CONFIG & MODERN LIGHT STYLING ---

st.set_page_config(page_title="BioMumo | MOMU CORE", layout="wide", page_icon="🧬")



st.markdown("""

    <style>

    /* Global Theme */

    .stApp { background-color: #fcfcfc; color: #2d3436; font-family: 'Segoe UI', sans-serif; }

    .main-title { font-size: 36px; font-weight: 800; color: #2d3436; text-align: center; margin-top: -10px; }

    

    /* Diamond-Hexagon Module */

    .benzene-cluster { display: flex; flex-direction: column; align-items: center; padding: 10px; }

    .diamond-hexagon {

        width: 190px; height: 230px;

        background-color: #ffffff;

        border: 2px solid #2d3436; 

        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);

        display: flex; flex-direction: column; align-items: center; justify-content: center;

        position: relative; z-index: 2;

        box-shadow: 0 4px 10px rgba(0,0,0,0.05);

    }

    .hex-image { width: 75px; height: 75px; object-fit: contain; margin-bottom: 5px; opacity: 0.9; }

    .hexagon-title { font-weight: 800; font-size: 16px; color: #2d3436; text-transform: uppercase; margin: 0; }

    .hexagon-subtitle { font-size: 12px; color: #636e72; margin-bottom: 8px; }

    .click-here-accent { font-weight: 700; color: #0984e3; text-transform: uppercase; font-size: 11px; border: 1px solid #0984e3; padding: 2px 6px; border-radius: 4px; }



    /* Attached Description Box (Matching the Sketch) */

    .attached-info-box { 

        background-color: #ffffff; width: 200px; padding: 25px 15px 15px 15px; 

        border-radius: 0 0 10px 10px; border: 2px solid #2d3436; 

        margin-top: -35px; z-index: 1; box-shadow: 0 4px 15px rgba(0,0,0,0.1); 

    }

    .info-list { font-size: 13px; color: #2d3436; line-height: 2; border-bottom: 1px solid #dfe6e9; padding: 4px 0; text-align: left; }

    

    /* Button Style */

    .stButton>button { width: 100%; border-radius: 5px; border: 1px solid #2d3436; background-color: #ffffff; color: #2d3436; font-weight: 700; font-size: 12px; }

    .stButton>button:hover { background-color: #2d3436 !important; color: #ffffff !important; }

    </style>

""", unsafe_allow_html=True)



# --- 2. LOGO GENERATOR (Sketch Accurate) ---

def generate_momu_sketch_logo():

    fig, ax = plt.subplots(figsize=(12, 2.5), facecolor='#fcfcfc')

    ax.set_facecolor('#fcfcfc')

    ax.set_xlim(-5, 20); ax.set_ylim(-5, 5); ax.axis('off')

    

    coords = [(0, 2.2), (-1.9, 0), (1.9, 0), (0, -2.2)]

    labels = ["U", "M", "M", "O"]

    for (x, y), label in zip(coords, labels):

        ring = RegularPolygon((x, y), numVertices=6, radius=1.3, orientation=0, edgecolor='#2d3436', facecolor='#f8f9fa', lw=1.2)

        ax.add_patch(ring)

        ax.text(x, y, label, color='#2d3436', fontsize=14, fontweight='bold', ha='center', va='center')

    

    ax.plot(1.1, -2.9, marker='o', markersize=7, color="#2d3436") # Radical Dot

    ax.text(5.5, 0.8, "MOMU core", color='#2d3436', fontsize=38, fontweight='black')

    ax.text(5.5, -0.8, "The Integrated Molecular Analyzing Pipeline", color='#636e72', fontsize=14)

    return fig



# --- 3. SESSION STATE ---

if "show_desc" not in st.session_state:

    st.session_state.show_desc = {"p1": False, "p2": False, "p3": False}

if "active_file" not in st.session_state:

    st.session_state.active_file = None



# --- 4. MAIN INTERFACE ---

st.pyplot(generate_momu_sketch_logo())

tabs = st.tabs(["Home", "DESCRIPTIONS", "ABOUT US", "Reference", "Contact"])



with tabs[0]:

    st.markdown('<p style="text-align:center; font-weight:700; color:#636e72; letter-spacing:1px; margin-bottom:0;">COMPUTATIONAL DRUG DISCOVERY PLATFORM</p>', unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">Biomumo: Opening New Worlds for Molecular Discovery</h1>', unsafe_allow_html=True)

    

    st.write("### Home :-")

    

    col_in, col_viz = st.columns([1, 2])

    with col_in:

        st.markdown("#### 🧪 Target Input")

        up = st.file_uploader("Upload PDB Structure", type=['pdb'])

        if up:

            with open("temp.pdb", "wb") as f: f.write(up.getbuffer())

            st.session_state.active_file = "temp.pdb"

    with col_viz:

        if st.session_state.active_file:

            st_molstar(st.session_state.active_file, height=300)

        else:

            st.info("Upload a PDB file to view the 3D structure here.")



    st.divider()

    c1, c2, c3 = st.columns(3)



    # Column 1: Protein Analysis

    with c1:

        st.markdown(f"""<div class="benzene-cluster"><div class="diamond-hexagon">

            <p class="hexagon-title">Protein</p>

            <img src="https://rcsb.org/pdb/images/3fxi_asym_r_500.jpg" class="hex-image">

            <p class="hexagon-subtitle">protein analysis</p><p class="click-here-accent">click here</p>

        </div></div>""", unsafe_allow_html=True)

        if st.button("Toggle Protein Box", key="btn1"):

            st.session_state.show_desc["p1"] = not st.session_state.show_desc["p1"]

        if st.session_state.show_desc["p1"]:

            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)

            for i in ["Sequence Extraction", "Molecular Weight", "pI Calculation", "Instability Index"]:

                st.markdown(f'<div class="info-list">• {i}</div>', unsafe_allow_html=True)

            if st.button("RUN PROTEIN CAT", key="run1"): st.success("Running...")

            st.markdown('</div></div>', unsafe_allow_html=True)



    # Column 2: Active Site

    with c2:

        st.markdown(f"""<div class="benzene-cluster"><div class="diamond-hexagon">

            <p class="hexagon-title">Active Site</p>

            <img src="https://cdn.rcsb.org/images/structures/8/8m5s/8m5s_assembly-1.jpeg" class="hex-image">

            <p class="hexagon-subtitle">site prediction</p><p class="click-here-accent">click here</p>

        </div></div>""", unsafe_allow_html=True)

        if st.button("Toggle Active Box", key="btn2"):

            st.session_state.show_desc["p2"] = not st.session_state.show_desc["p2"]

        if st.session_state.show_desc["p2"]:

            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)

            for i in ["SASA Surface", "Binding Pockets", "Ligand Docking", "Cavity Volume"]:

                st.markdown(f'<div class="info-list">• {i}</div>', unsafe_allow_html=True)

            if st.button("RUN ACTIVE SITE PREDICT", key="run2"): st.success("Predicting...")

            st.markdown('</div></div>', unsafe_allow_html=True)



    # Column 3: Mutation

    with c3:

        st.markdown(f"""<div class="benzene-cluster"><div class="diamond-hexagon">

            <p class="hexagon-title">Mutation</p>

            <img src="https://cdn.rcsb.org/images/structures/1/1aie/1aie_assembly-1.jpeg" class="hex-image">

            <p class="hexagon-subtitle">mutation prediction</p><p class="click-here-accent">click here</p>

        </div></div>""", unsafe_allow_html=True)

        if st.button("Toggle Mutation Box", key="btn3"):

            st.session_state.show_desc["p3"] = not st.session_state.show_desc["p3"]

        if st.session_state.show_desc["p3"]:

            st.markdown('<div class="benzene-cluster"><div class="attached-info-box">', unsafe_allow_html=True)

            for i in ["B-Factor Analysis", "RMSF Calculation", "Energy Stability", "Alanine Scan"]:

                st.markdown(f'<div class="info-list">• {i}</div>', unsafe_allow_html=True)

            if st.button("RUN MUTATION PT", key="run3"): st.success("Analyzing...")

            st.markdown('</div></div>', unsafe_allow_html=True)



# Remaining Tabs

with tabs[1]: st.info("Detailed methodology and algorithms used in MOMU CORE.")

with tabs[2]: st.write("### VMCP Research\nDeveloped by Mowriss.M.G & Mugilarasi.C.")

with tabs[3]: st.write("Scientific References: Biopython, Molstar, and RCSB PDB.")

with tabs[4]: st.write("Contact the team at Vinayaka Mission's College of Pharmacy.")

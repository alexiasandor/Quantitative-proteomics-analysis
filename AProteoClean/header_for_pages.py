import streamlit as st

def header_for_pages():
    st.set_page_config(page_title="AProteoClean – Preprocessing", layout="wide")

    # === Sidebar ===
    with st.sidebar:
        st.image("images/logo.png", width=140)
        st.markdown("---")
        st.markdown("### 📂 Navigation")
        st.markdown("- 🧪 Preprocessing")
        st.markdown("- 🛠️ Imputation")
        st.markdown("- 📈 Analysis")

def title_for_processing():

    st.markdown("<h2 style='color:#008080;'>🧪 Preprocessing</h2>", unsafe_allow_html=True)
    st.markdown("Clean your proteomic data by selecting relevant columns and applying log2 transformation.")
    st.markdown("---")



def title_for_imputations():

    st.markdown("<h2 style='color:#008080;'>🛠️ Imputation</h2>", unsafe_allow_html=True)
    st.markdown( "This module automatically applies imputation methods to:\n- 🧬 Diseased proteins\n- 🧠 Healthy proteins")
    st.markdown("---")

def title_for_analysis():
    st.markdown("<h2 style='color:#008080;'>📊  Similarity Analysis Between Imputation Methods</h2>",
                unsafe_allow_html=True)
    st.markdown("Select a similarity metric and run the analysis on all imputed files from a merged folder.")
    st.markdown("---")

def title_for_analysis_by_deviation():
    st.markdown("<h2 style='color:#008080;'>📊 Evaluate Imputation Methods</h2>", unsafe_allow_html=True)
    st.markdown(
        "For each protein with missing values, compare the mean and standard deviation before and after imputation.")
    st.markdown("---")

def title_for_analysis_by_missing():
    st.markdown("<h2 style='color:#008080;'>📈 Missingness Rate – Best Methods</h2>", unsafe_allow_html=True)



def title_for_view_imp():
    st.markdown("<h2 style='color:#008080;'>🔍 Compare Imputations (Merge All Methods)</h2>", unsafe_allow_html=True)


def title_for_view_file():
    st.markdown("<h2 style='color:#008080;'>📂 View Processed Files</h2>", unsafe_allow_html=True)
    st.markdown("Here you can browse and inspect already processed files stored in the `data/processed/` folder.")
    st.markdown("---")

def title_for_home():
    st.markdown("<h1 style='color:#008080; text-align:center;'>🧬 ProteoClean</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>A lightweight app for proteomic data cleaning & analysis</h4>",
                unsafe_allow_html=True)
    st.markdown("---")

def introduction():
    st.markdown("""
        Welcome to **ProteoClean** – your assistant for cleaning and analyzing proteomic data.

    This app allows you to:

    ✅ Upload Excel files containing proteomic data  
    ✅ Select and preprocess relevant columns  
    ✅ Apply multiple imputation strategies for missing values  
    ✅ Perform differential analysis (e.g., E. coli contamination detection)  
    ✅ Export clean, analyzed datasets
    """)
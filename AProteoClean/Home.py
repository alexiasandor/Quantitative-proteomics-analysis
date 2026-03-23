import streamlit as st
from header_for_pages import *
from messages import *


header_for_pages()  ## adaugam heaader-ul standard pentru paginile proiectului
## adaugam titlul
title_for_home()
# adugam introducerea
introduction()

#explicatii suplimentare
st.markdown("### 🚀 How to get started:")
st.markdown("""
1. Go to **Preprocessing** page to clean and log-transform your data  
2. Proceed to **Imputation** to apply various missing data methods  
3. Finally, visit **Analysis** to detect differentially expressed proteins
""")

# info alert
st.info("ℹ️ Use the sidebar menu on the left to access each step of the pipeline.")

# incheiere
st.markdown("---")
st.markdown("<div style='text-align:center;'>Created with ❤️ for proteomic research</div>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import os

from header_for_pages import *
from messages import *
header_for_pages()  ## adaugam heaader-ul standard pentru paginile proiectului
title_for_view_file()  ## adaugam titlul

#selectare folder aferent
processed_base ="data/processed"
available_folders = sorted([
    f for f in os.listdir(processed_base) if os.path.isdir(os.path.join(processed_base, f))
])
if not available_folders:
    st.warning()

if not available_folders:
    st.warning(MESSAGES["view_processed"]["folder_not_found"])
    st.stop()
selected_proc_folder = st.selectbox(MESSAGES["view_processed"]["select_folder_1"], available_folders)
folder_path = os.path.join(processed_base, selected_proc_folder)

#afisam toate fisierle din folderul curent
xlsx_files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]

if not xlsx_files:
    st.info(MESSAGES["view_processed"]["no_xlsx"])
    st.stop()

selected_file = st.selectbox(MESSAGES["view_processed"]["select_file_processed"], xlsx_files)
file_path = os.path.join(folder_path, selected_file)

#incarcam si afisam fisierul selectat

df_existing = pd.read_excel(file_path)
st.write(f"{MESSAGES['view_processed']['show']} {selected_file}`:")
st.dataframe(df_existing)

# === Download button ===
with open(file_path, "rb") as f:
    st.download_button(MESSAGES["view_processed"]["download"], data=f, file_name=selected_file)

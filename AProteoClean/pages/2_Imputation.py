import streamlit as st
import pandas as pd
import numpy as np
import os
from imputation_methods import imputations, apply_imputation
from header_for_pages import *
from messages import *


header_for_pages()  ## adaugam heaader-ul standard pentru paginile proiectului
title_for_imputations()  ## adaugam titlul


# selectarea folderului aferent fisierului procesat

base_path ="data/processed"
os.makedirs(base_path, exist_ok=True)
available_folders = sorted([f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))])
selected_folder = st.selectbox(MESSAGES["imputation_messages"]["select_folder"], available_folders)

# buton pentru incarcarea fisierelor din folderul creat
if"load_triggered" not in st.session_state:
    st.session_state.load_triggered = False

if st.button(MESSAGES["imputation_messages"]["load_files"]):
    st.session_state.load_triggered = True
    st.session_state.selected_folder = selected_folder

# selectare si completare
if st.session_state.get("load_triggered"):
    folder_path =  os.path.join(base_path, st.session_state.selected_folder)
    files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]

    if not files:
        st.warning(MESSAGES["imputation_messages"]["file_not_found"])
        st.stop()

    selected_diseased = st.selectbox(MESSAGES["imputation_messages"]["select_d"], files, key = "diseased_file")
    selected_healthy = st.selectbox(MESSAGES["imputation_messages"]["select_h"], files, key="healthy_file")

    if selected_diseased and selected_healthy:
        df_diseased = pd.read_excel(os.path.join(folder_path, selected_diseased))
        df_healthy = pd.read_excel(os.path.join(folder_path, selected_healthy))
        st.success(f"{MESSAGES['imputation_messages']['loaded']} '{selected_diseased}' and '{selected_healthy}'")

       # folderele de output
        output_root = os.path.join("data", "imputations", selected_folder)
        output_diseased_folder = os.path.join(output_root, "Diseased")
        output_healthy_folder = os.path.join(output_root, "Healthy")
        output_merge_folder = os.path.join(output_root, "merge")

        #functie de creare si salvare
        def apply_and_save(df, label, output_folder):
            os.makedirs(output_folder, exist_ok=True)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            for method_name, method_func in imputations.items():
                df_copy = df.copy()
                try:
                    df_copy[numeric_cols] = apply_imputation(df_copy,numeric_cols,method_name, method_func, chunk_size=500, st_logger= st)
                    path = os.path.join(output_folder, f"{method_name}_{label.lower()}.xlsx")
                    df_copy.to_excel(path, index=False)
                    st.success(f"{MESSAGES['imputation_messages']['v']} -> saved: '{path}'")
                except Exception as e:
                    st.error(f"{MESSAGES['imputation_messages']['error']} : {e}")

        run = st.button(MESSAGES["imputation_messages"]["run"])
        if run:
            apply_and_save(df_diseased, "Diseased", output_diseased_folder)
            apply_and_save(df_healthy, "Healthy", output_healthy_folder)
            st.balloons()
            st.success(f"{MESSAGES['imputation_messages']['success_message']}")

        if st.button(MESSAGES["imputation_messages"]["merge"]):
            os.makedirs(output_merge_folder, exist_ok=True)

            diseased_files = [f for f in os.listdir(output_diseased_folder) if f.endswith(".xlsx")]
            healthy_files = [f for f in os.listdir(output_diseased_folder) if f.endswith(".xlsx")]

            diseased_methods = {f.replace("_diseased.xlsx", "") for f in diseased_files}
            healthy_methods = {f.replace("_healthy.xlsx", "") for f in healthy_files}
            common_methods = diseased_methods & healthy_methods

            if not common_methods:
                st.warning(MESSAGES["imputation_messages"]["no_matching"])
            else:
                for method in common_methods:
                    df_d = pd.read_excel(os.path.join(output_diseased_folder, f"{method}_diseased.xlsx"))
                    df_h = pd.read_excel(os.path.join(output_healthy_folder, f"{method}_healthy.xlsx"))

                    if "Entry.name" in df_d.columns and "Entry.name" in df_h.columns:
                        df_d = df_d.set_index("Entry.name")
                        df_h = df_h.set_index("Entry.name")

                        merged = pd.concat([df_d, df_h], axis = 1, join="outer").reset_index()
                    else:
                        merged = pd.concat([df_d, df_h], axis = 0, ignore_index = True)

                    merged_file = os.path.join(output_merge_folder, f"merged_{method}.xlsx")
                    merged.to_excel(merged_file, index=False)
                    st.success(f"{MESSAGES['imputation_messages']['saved']} : '{merged_file}' ")
                st.balloons()
                st.success(MESSAGES["imputation_messages"]["merge_completed"])


else:
    st.info(MESSAGES["imputation_messages"]["info"])

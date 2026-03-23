import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
from utils import process_xls_file
from header_for_pages import *
from messages import *

header_for_pages()  ## adaugam heaader-ul standard pentru paginile proiectului
title_for_processing()  ## adaugam titlul


#cream foldere aferente fiecarui set de date introdus in aplicatie
def get_new_processed_folder(base_root="data/processed"):
    os.makedirs(base_root, exist_ok=True)
    index = 1
    while os.path.exists(os.path.join(base_root, f"processed_{index}")):
        index += 1
    folder_path = os.path.join(base_root, f"processed_{index}")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


uploaded_file = st.file_uploader(MESSAGES["processing_messages"]["upload"], type=['xlsx'])

if uploaded_file:
    df_excel_file = pd.read_excel(uploaded_file)
    st.success(MESSAGES["processing_messages"]["upload_success"])

    keep_cols = st.multiselect(MESSAGES["processing_messages"]["keep_cols"], df_excel_file.columns.tolist())
    log_cols = st.multiselect(MESSAGES["processing_messages"]["log_cols"], df_excel_file.columns.tolist())

    if st.button(MESSAGES["processing_messages"]["apply_btn"]):
        df_processed = process_xls_file(df_excel_file, keep_cols, log_cols)

        numeric_cols = df_processed.select_dtypes(include=["float64", "int64"]).columns
        df_processed = df_processed[~df_processed[numeric_cols].isna().all(axis=1)]

        st.session_state["df_processed"] = df_processed
        st.session_state["workflow_time"] =datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        processed_folder = get_new_processed_folder()
        st.session_state["processed_folder"] = processed_folder

        output_path= os.path.join(processed_folder, f"processed_excel_file_{st.session_state['workflow_time']}.xlsx")
        df_processed.to_excel(output_path, index=False)
        st.session_state["main_file"] =output_path

        st.write(MESSAGES["processing_messages"]["rows_after"]+ ":" + str(df_processed.shape[0]))
        st.write(MESSAGES["processing_messages"]["nan_nr"])
        st.dataframe(df_processed[numeric_cols].isna().sum().reset_index().rename(columns={"index": "Column", 0: "NaN Count"}))

        st.success(MESSAGES["processing_messages"]["success_msg"])
        st.info(MESSAGES["processing_messages"]["success_msg"] + processed_folder + " as " + str(os.path.basename(output_path)))
        st.dataframe(df_processed)


#split data
if "df_processed" in st.session_state:
    df = st.session_state["df_processed"]
    processed_folder = st.session_state["processed_folder"]
    workflow_time = st.session_state["workflow_time"]
    st.markdown(MESSAGES['processing_messages']['split_msg'])

    if "Taxonomy" in df.columns:
        st.markdown("### Split by Taxonomy")
        taxonomy_values = df["Taxonomy"].dropna().unique().tolist()

        diseased_val = st.selectbox(MESSAGES["processing_messages"]["value_for_disease"], taxonomy_values, key = "d_tax")
        healthy_val = st.selectbox(MESSAGES["processing_messages"]["value_for_healthy"], [v for v in taxonomy_values if v!= diseased_val], key = "h_tax")

        if st.button(MESSAGES["processing_messages"]["split_by_taxonomy"]):
            df_diseased = df[df["Taxonomy"] == diseased_val].copy()
            df_healthy = df[df["Taxonomy"] == healthy_val].copy()

            numeric_d_cols = df_diseased.select_dtypes(include=["float64", "int64"]).columns
            numeric_h_cols = df_healthy.select_dtypes(include=["float64", "int64"]).columns

            empty_in_d = df_diseased[numeric_d_cols].isna().all(axis=1)
            empty_in_h = df_healthy[numeric_h_cols].isna().all(axis=1)

            rows_to_remove = empty_in_d[empty_in_d].index.union(empty_in_h[empty_in_h].index)

            df_diseased = df_diseased.drop(rows_to_remove, errors= "ignore")
            df_healthy = df_healthy.drop(rows_to_remove, errors= "ignore")
            df = df.drop(index=rows_to_remove, errors="ignore")
            st.session_state["df_processed"]=df

            clean_path = os.path.join(processed_folder, f"clean_processed_{workflow_time}.xlsx")
            df.to_excel(clean_path, index=False)

            diseased_file = os.path.join(processed_folder, f"diseased_only_{workflow_time}.xlsx")
            healthy_file = os.path.join(processed_folder, f"healthy_only_{workflow_time}.xlsx")

            df_diseased.to_excel(diseased_file, index=False)
            df_healthy.to_excel(healthy_file, index=False)

            st.success(MESSAGES["processing_messages"]["split"])
            st.info(f"{MESSAGES['processing_messages']['removed']} {len(rows_to_remove)}  {MESSAGES['processing_messages']['removed_proteins']}")

    else:
            st.markdown(MESSAGES["processing_messages"]["split_by"])

            available_cols = df.columns.tolist()
            diseased_cols = st.multiselect(MESSAGES["processing_messages"]["value_for_disease"] , available_cols, key= "cols_diseased")
            healthy_cols = st.multiselect(MESSAGES["processing_messages"]["value_for_healthy"] , available_cols, key= "cols_healthy")

            if st.button(MESSAGES["processing_messages"]["generate_files"]):
                if not diseased_cols or not healthy_cols:
                    st.warning(MESSAGES["processing_messages"]["select_col"])
                else:
                    df_diseased = df[diseased_cols].copy()
                    df_healthy = df[healthy_cols].copy()

                    numeric_d_cols = df_diseased.select_dtypes(include=["float64", "int64"]).columns
                    numeric_h_cols = df_healthy.select_dtypes(include=["float64", "int64"]).columns

                    empty_in_d = df_diseased[numeric_d_cols].isna().all(axis=1)
                    empty_in_h = df_healthy[numeric_h_cols].isna().all(axis=1)

                    rows_to_remove = empty_in_d[empty_in_d].index.union(empty_in_h[empty_in_h].index)

                    df_diseased = df_diseased.drop(rows_to_remove, errors="ignore")
                    df_healthy = df_healthy.drop(rows_to_remove, errors="ignore")
                    df = df.drop(index=rows_to_remove, errors="ignore")
                    st.session_state["df_processed"] = df

                    clean_path = os.path.join(processed_folder, f"clean_processed_{workflow_time}.xlsx")
                    df.to_excel(clean_path, index=False)

                    diseased_file = os.path.join(processed_folder, f"diseased_only_{workflow_time}.xlsx")
                    healthy_file = os.path.join(processed_folder, f"healthy_only_{workflow_time}.xlsx")

                    df_diseased.to_excel(diseased_file, index=False)
                    df_healthy.to_excel(healthy_file, index=False)

                    st.success(MESSAGES["processing_messages"]["files_created"])
                    st.info(
                    f"{MESSAGES['processing_messages']['removed']} {len(rows_to_remove)}  {MESSAGES['processing_messages']['removed_proteins']}")

# buton pentru resetare workflow

st.markdown("---")
if st.button(MESSAGES["processing_messages"]["reset_workflow"]):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

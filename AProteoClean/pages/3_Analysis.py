import os
import json
import pandas as pd
import streamlit as st
from calculate_similarity import calculate_similarity_on_imputed
from header_for_pages import *
from messages import *

header_for_pages()  ## adaugam heaader-ul standard pentru paginile proiectului
title_for_analysis()  ## adaugam titlul

# definim liste cu metricile de similaritate
metrics = ['Pearson', 'Spearman', 'Kendall', 'Euclidean', 'Manhattan', 'Cosine', 'Canberra']
selected_metric = st.selectbox('Select metric', metrics)

#selectare folder aferent
processed_base ="data/processed"
available_processed_folders = sorted([
    f for f in os.listdir(processed_base) if os.path.isdir(os.path.join(processed_base, f))
])
selected_processed = st.selectbox(MESSAGES["analysis_messages"]["select_folder_1"], available_processed_folders)

#selectare folder merge
merge_base_path ="data/imputations"
available_merge_folders = sorted([
    f for f in os.listdir(merge_base_path) if os.path.isdir(os.path.join(merge_base_path, f))
])
selected_merge_folder = st.selectbox(MESSAGES["analysis_messages"]["select_folder_2"], available_merge_folders)


#selectare fisier initial
initial_file = None
if selected_processed:
    full_processed_path = os.path.join(processed_base, selected_processed)
    xlsx_files = [f for f in os.listdir(full_processed_path) if f.endswith(".xlsx")]

    selected_file = st.selectbox(MESSAGES["analysis_messages"]["select_file"], xlsx_files)

    if selected_file:
        initial_file = os.path.join(full_processed_path, selected_file)

run_analysis = st.button(MESSAGES["analysis_messages"]["run"])

#implementare analiza
if run_analysis and selected_merge_folder:
    input_folder = os.path.join(merge_base_path, selected_merge_folder)
    merge_subfolder = os.path.join(input_folder, "merge")
    input_files = [f for f in os.listdir(merge_subfolder) if f.endswith('.xlsx')]


    # creare subfoldere pentru masti si calcule intermediare
    def get_next_subfolder(base, prefix):
        index=1
        while os.path.exists(os.path.join(base, f"{prefix}_{index}")):
            index+=1
        return os.path.join(base, f"{prefix}_{index}")

    masks_folder = get_next_subfolder(input_folder, "masks")
    intermediars_folder = get_next_subfolder(input_folder, "intermediars")
    os.makedirs(masks_folder, exist_ok=True)
    os.makedirs(intermediars_folder, exist_ok=True)

    st.info(MESSAGES["analysis_messages"]["run_info"])

    result_df, messages, top_pairs_df, top_methods = calculate_similarity_on_imputed(
        initial_file, merge_subfolder, input_files, selected_metric,
        masks_folder =  masks_folder,
        intermediars_folder=intermediars_folder
    )

    st.success(MESSAGES["analysis_messages"]["similarity_success"])

    if messages:
        st.markdown(MESSAGES["analysis_messages"]["view_tab"])
        top_pairs_df["Score"] = top_pairs_df["Score"].map(lambda x: f"{x:.6f}")
        st.dataframe(top_pairs_df)

    #salvam in json in ordinea dataset-ului si a metricilor
    json_file = 'top_methods.json'
    dataset_key = selected_processed  # folosește folderul processed_X drept cheie

    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            all_data = json.load(f)
    else:
        all_data = {}

    # creează sub-dict dacă nu există
    if dataset_key not in all_data:
        all_data[dataset_key] = {}

    all_data[dataset_key][selected_metric] = top_methods

    with open(json_file, 'w') as f:
        json.dump(all_data, f, indent=4)

#afisarea metodelor comune
if 'show_common' not in st.session_state:
    st.session_state.show_common = False

if st.button('Show common top methods'):
    st.session_state.show_common = not st.session_state.show_common

if st.session_state.show_common:
    json_file = 'top_methods.json'
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)

        if selected_processed not in data:
            st.error(f"{MESSAGES['analysis_messages']['no_saved']}")
        else:
            dataset_data = data[selected_processed]
            metric_methods = [set(methods) for key, methods in dataset_data.items()]
            if metric_methods:
                common_methods = sorted(set.intersection(*metric_methods))
                if common_methods:
                    st.subheader(f"{MESSAGES['analysis_messages']['common_methods']}")
                    selected_methods = set()
                    all_selected = st.checkbox(MESSAGES['analysis_messages']['select_methods'])
                    for method in common_methods:
                        if all_selected or st.checkbox(method, key=f"chk_{method}"):
                            selected_methods.add(method)

                    if selected_methods:
                        df_selected = pd.DataFrame(sorted(selected_methods), columns=["Method"])
                        csv = df_selected.to_csv(index=False)
                        st.download_button(
                            label=f"{MESSAGES['analysis_messages']['download_methods']}",
                            data=csv,
                            file_name='selected_methods.csv',
                            mime='text/csv'
                        )

                        st.markdown("---")
                        st.markdown(MESSAGES["analysis_messages"]["download_file"])
                        for method in sorted(selected_methods):
                            file_path = os.path.join(merge_base_path, selected_merge_folder, "merge", f"merged_{method}.xlsx")
                            if os.path.exists(file_path):
                                with open(file_path, 'rb') as f:
                                    st.download_button(
                                        label=f"{MESSAGES['analysis_messages']['no_methods']} '{method}.xlsx'",
                                        data=f,
                                        file_name=f"{method}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key=f"dl_{method}"
                                    )
                            else:

                                st.warning(
                                    f"{MESSAGES['analysis_messages']['no_methods']} '{method}' {MESSAGES['analysis_messages']['not_exist']}")
                    else:
                        st.info(MESSAGES["analysis_messages"]["select"])
                else:
                    st.warning(MESSAGES["analysis_messages"]["no_methods"])
            else:
                st.warning(MESSAGES["analysis_messages"]["no_data"])
    else:
        st.error(MESSAGES["analysis_messages"]["file_not_found"])

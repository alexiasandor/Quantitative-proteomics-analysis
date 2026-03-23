import streamlit as st
import pandas as pd
import numpy as np
import os

from header_for_pages import *
from messages import *

header_for_pages()  ## adaugam heaader-ul standard pentru paginile proiectului
title_for_analysis_by_missing()  ## adaugam titlul

#selectarea folder-ului aferent fisierului pe care il prelucram la momenttul respectiv
processed_base = "data/processed"
available_processed_folders = sorted([
    f for f in os.listdir(processed_base) if os.path.isdir(os.path.join(processed_base, f))
])
selected_processed = st.selectbox(MESSAGES["analysis_by_miss_rate_messages"]["select_folder_1"],
                                  available_processed_folders)

# selectarea folder-ului de merge
merge_base = "data/imputations"
available_merge_folders = sorted([
    f for f in os.listdir(merge_base) if os.path.isdir(os.path.join(merge_base, f))
])
selected_merge_folder = st.selectbox(MESSAGES["analysis_by_miss_rate_messages"]["select_folder_2"],
                                     available_merge_folders)

df_initial = None
if selected_processed:
    folder_path = os.path.join(processed_base, selected_processed)
    files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]
    selected_file = st.selectbox(MESSAGES["analysis_by_miss_rate_messages"]["select_file_processed"], files)

    if selected_file:
        df_initial = pd.read_excel(os.path.join(folder_path, selected_file))

if df_initial is not None and selected_merge_folder:
    # identificam coloanele dupa id
    text_cols = [col for col in df_initial.columns if df_initial[col].dtype == 'object']
    id_column = (
        "Gene names" if "Gene names" in df_initial.columns
        else "Entry.name" if "Entry.name" in df_initial.columns
        else st.selectbox(MESSAGES["analysis_by_miss_rate_messages"]["select_col"], text_cols)
    )

    # identificam si salvam coloanele numerice

    intensity_cols = [col for col in df_initial.columns if
                      col not in [id_column, "Taxonomy"] and df_initial[col].dtype in [np.float64, np.int64]]

    if st.button(MESSAGES["analysis_by_miss_rate_messages"]["run"]):
        # calculam rata de valori lipsa: nr valori lipsa/nr tot
        df_initial["missing_rate"] = df_initial[intensity_cols].isna().sum(axis=1) / len(intensity_cols)

        #definim grupurile in functie de procentul valorilor lipsa
        conditions = [
            (df_initial["missing_rate"] <= 0.33),
            (df_initial["missing_rate"] > 0.33) & (df_initial["missing_rate"] <= 0.66),
            (df_initial["missing_rate"] > 0.66)
        ]

        choices = np.array(["Low", "Medium", "High"], dtype=object)
        df_initial["missing_group"] = np.select(conditions, choices, default="Unknow")

        #extragem valorile completate pentru a incepe procesul de identificare

        merge_folder = os.path.join(merge_base, selected_merge_folder, "merge")
        threshold_delta = 0.5
        threshold_std = 0.7

        results = []
        method_performance = {"Low": [], "Medium": [], "High": []}

        for file in os.listdir(merge_folder):
            if not file.endswith(".xlsx"):
                continue
            method = file.replace("merged_", "").replace(".xlsx", "")
            df_imp = pd.read_excel(os.path.join(merge_folder, file))

            if id_column not in df_imp.columns:
                st.warning(f"Method {method} : ID column {id_column} is missing from imputed file")
                continue

            for group in ["Low", "Medium", "High"]:
                genes = df_initial[df_initial["missing_group"] == group][id_column]
                df_init_sub = df_initial[df_initial[id_column].isin(genes)]
                df_imp_sub = df_imp[df_imp[id_column].isin(genes)]

                diffs, stds = [], []

                for gene in genes:
                    row_init = df_init_sub[df_init_sub[id_column] == gene][intensity_cols]
                    row_imp = df_imp_sub[df_imp_sub[id_column] == gene][intensity_cols]
                    if row_init.empty or row_imp.empty:
                        st.text(
                            f"Skipped gene '{gene}' in method '{method}', group '{group}' - not found. ")
                        continue

                    try:
                        mean_init = np.nanmean(row_init.values.flatten())
                        mean_imp = np.nanmean(row_imp.values.flatten())
                        std_imp = np.nanstd(row_imp.values.flatten())

                        diffs.append(abs(mean_imp - mean_init))
                        stds.append(std_imp)
                    except Exception as e:
                        st.error(f"Error for genne {gene} in method {method}: {e}")

                if not diffs:
                    st.warning(f"No valid genes for method `{method}`, group `{group}`.")
                    continue
                else:
                    st.success(f"✅ Method `{method}` - Group `{group}`: {len(diffs)} genes evaluated")

                avg_diff = np.mean(diffs)
                avg_std = np.mean(stds)
                results.append({
                    "Method": method,
                    "Group": group,
                    "|Mean|": round(avg_diff, 3),
                    "STD": round(avg_std, 3)
                })

                if avg_diff < threshold_delta and avg_std < threshold_std:
                    method_performance[group].append(method)

        st.markdown(MESSAGES["analysis_by_miss_rate_messages"]["method_perf"])
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True)

        # === Recommendations
        st.markdown(MESSAGES["analysis_by_miss_rate_messages"]["recommended"])
        for group in ["Low", "Medium", "High"]:
            methods = method_performance[group]
            if methods:
                st.markdown(f"{MESSAGES['analysis_by_miss_rate_messages']['good_methods']}, '{group}' missingness . ")
                st.markdown("<ul>" + "".join([f"<li>{m}</li>" for m in methods]) + "</ul>", unsafe_allow_html=True)
            else:
                st.warning(f"{MESSAGES['analysis_by_miss_rate_messages']['no_methods']}, '{group}' missingness . ")

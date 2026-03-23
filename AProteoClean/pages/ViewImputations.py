import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from adjustText import adjust_text


from header_for_pages import *
from messages import *
header_for_pages()  ## adaugam heaader-ul standard pentru paginile proiectului
title_for_view_imp()  ## adaugam titlul


#selectare folder aferent
processed_base ="data/processed"
available_processed_folders = sorted([
    f for f in os.listdir(processed_base) if os.path.isdir(os.path.join(processed_base, f))
])
selected_proc_folder = st.selectbox(MESSAGES["view_imputations"]["select_folder_1"], available_processed_folders)

#selectare folder merge
merge_base ="data/imputations"
available_merge_folders = sorted([
    f for f in os.listdir(merge_base) if os.path.isdir(os.path.join(merge_base, f, "merge"))
])
selected_merge_folder = st.selectbox(MESSAGES["view_imputations"]["select_folder_2"], available_merge_folders)


#selectare fisier initial
selected_file = None
if selected_proc_folder:
    full_proc_path = os.path.join(processed_base, selected_proc_folder)
    xlsx_files = [f for f in os.listdir(full_proc_path) if f.endswith(".xlsx")]

    selected_file = st.selectbox(MESSAGES["view_imputations"]["select_file"], xlsx_files)

    if selected_file:
        df_initial = pd.read_excel(os.path.join(full_proc_path, selected_file))

# afisam doar daca toate folderele si fisiere au fost selectate/ alese:

if selected_merge_folder and selected_file:
    merge_path = os.path.join(merge_base, selected_merge_folder, "merge")
    merged_files_list = [f for f in os.listdir(merge_path) if f.endswith(".xlsx")]

    lfq_cols = [col for col in df_initial.columns if "intensity" in col.lower()]
    gene_col = "Gene names" if "Gene names" in df_initial.columns else (
        "Entry.name" if "Entry.name" in df_initial.columns else df_initial.select_dtypes(include='object').columns[0]
    )

    df_initial["row_index"] = df_initial.index
    missing_combos = set()
    for col in lfq_cols:
        missing_rows = df_initial[df_initial[col].isna()]
        for idx in missing_rows["row_index"]:
            missing_combos.add(f"{idx} - {col}")
    combo_list = sorted(list(missing_combos))

    st.markdown("---")
    st.subheader(MESSAGES["view_imputations"]["view_merged"])
    selected_merged_file = st.selectbox("Select merged file to view:", merged_files_list)
    df_selected = pd.read_excel(os.path.join(merge_path, selected_merged_file))
    st.write(f" {MESSAGES['view_imputations']['view_merged']}`{selected_merged_file}`:")
    st.dataframe(df_selected)

  #comparam proteinele intre ele
    st.markdown("---")

    st.header(MESSAGES["view_imputations"]["comparison"])
    if combo_list:
        protein_combo_list = []
        for col in lfq_cols:
            missing_rows = df_initial[df_initial[col].isna()]
            for gene in missing_rows[gene_col].dropna().unique():
                protein_combo_list.append(f"{gene} - {col}")
        protein_combo_list = sorted(set(protein_combo_list))

        selected_protein_combo = st.selectbox(MESSAGES["view_imputations"]["select"], protein_combo_list)
        exclude_missing = st.checkbox(MESSAGES["view_imputations"]["exclude"], value=True)

        if selected_protein_combo:
            gene_name, lfq_column = selected_protein_combo.split(" - ")
            gene_name = gene_name.strip()
            lfq_column = lfq_column.strip()

            plot_data = []
            for file in merged_files_list:
                method = file.replace("merged_", "").replace(".xlsx", "")
                df = pd.read_excel(os.path.join(merge_path, file))
                match = df[df[gene_col].astype(str).str.strip() == gene_name]
                if not match.empty and lfq_column in match.columns:
                    value = match[lfq_column].values[0]
                    plot_data.append({"method": method, "value": value if pd.notna(value) else np.nan})
                else:
                    plot_data.append({"method": method, "value": np.nan})

            df_plot = pd.DataFrame(plot_data)
            method_order = [f.replace("merged_", "").replace(".xlsx", "") for f in merged_files_list]
            df_plot["method"] = pd.Categorical(df_plot["method"], categories=method_order, ordered=True)
            df_plot = df_plot.sort_values("method")

            if exclude_missing:
                df_plot = df_plot.dropna()

            if not df_plot.empty:
                fig, ax = plt.subplots(figsize=(20, 10))
                sns.barplot(data=df_plot, x="method", y="value", ax=ax, order=method_order)
                ax.set_title(f"Imputed values for {gene_name} — {lfq_column}")
                ax.set_xlabel("Method")
                ax.set_ylabel("Value")
                ax.tick_params(axis='x', rotation=45)
                st.pyplot(fig)
            else:
                st.info(MESSAGES["view_imputations"]["val_not_found"])
    else:
        st.info(MESSAGES["view_imputations"]["file_not_found"])

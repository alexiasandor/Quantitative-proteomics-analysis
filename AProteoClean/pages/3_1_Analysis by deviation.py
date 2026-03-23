import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="AProteoClean – Evaluate Imputations", layout="wide")

with st.sidebar:
    st.image("images/logo.png", width=140)
    st.markdown("---")
    st.markdown("### 📂 Navigation")
    st.markdown("- 🧪 Preprocessing")
    st.markdown("- 🛠️ Imputation")
    st.markdown("- 📊 Evaluate")
    st.markdown("- 📈 Analysis")

st.markdown("<h2 style='color:#008080;'>📊 Evaluate Imputation Methods</h2>", unsafe_allow_html=True)
st.markdown("For each protein with missing values, compare the mean and standard deviation before and after imputation.")
st.markdown("---")

# === Select processed file ===
processed_base = "data/processed"
processed_folders = sorted([f for f in os.listdir(processed_base) if os.path.isdir(os.path.join(processed_base, f))])
selected_proc_folder = st.selectbox("📁 Select processed folder:", processed_folders)

selected_file = None
if selected_proc_folder:
    full_proc_path = os.path.join(processed_base, selected_proc_folder)
    xlsx_files = [f for f in os.listdir(full_proc_path) if f.endswith(".xlsx")]
    selected_file = st.selectbox("📄 Select processed file:", xlsx_files)
    df_initial = pd.read_excel(os.path.join(full_proc_path, selected_file))

# === Select merge folder ===
imput_base = "data/imputations"
merge_folders = sorted([f for f in os.listdir(imput_base) if os.path.isdir(os.path.join(imput_base, f, "merge"))])
selected_merge = st.selectbox("🔀 Select merge folder:", merge_folders)

# === When everything is selected
if selected_file and selected_merge:
    merge_folder_path = os.path.join(imput_base, selected_merge, "merge")

    text_cols = [col for col in df_initial.columns if df_initial[col].dtype == 'object']
    id_column = (
        "Gene names" if "Gene names" in df_initial.columns
        else "Entry name" if "Entry name" in df_initial.columns
        else text_cols[0]
    )

    intensity_cols = [col for col in df_initial.columns if 'intensity' in col.lower()]
    proteins_with_nans = df_initial[df_initial[intensity_cols].isna().any(axis=1)][id_column].dropna().unique().tolist()

    selected_protein = st.selectbox("🔍 Select protein with missing values:", sorted(proteins_with_nans))

    if st.button("🚀 Run analysis"):
        @st.cache_data
        def calc_protein_stats(selected_protein):
            results = []
            initial_row = df_initial[df_initial[id_column] == selected_protein]
            if initial_row.empty:
                return pd.DataFrame()

            initial_vals = initial_row[intensity_cols].values.flatten()
            initial_mean = np.nanmean(initial_vals)
            n_missing = np.sum(np.isnan(initial_vals))

            for file in os.listdir(merge_folder_path):
                if file.startswith("merged_") and file.endswith(".xlsx"):
                    method = file.replace("merged_", "").replace(".xlsx", "")
                    df = pd.read_excel(os.path.join(merge_folder_path, file))
                    row = df[df[id_column] == selected_protein]
                    if row.empty:
                        continue
                    vals = row[intensity_cols].values.flatten()
                    imputed_mean = np.nanmean(vals)
                    std = np.nanstd(vals)
                    results.append({
                        "Method": method,
                        "Initial Mean": round(initial_mean, 3),
                        "Imputed Mean": round(imputed_mean, 3),
                        "Imputed STD": round(std, 3),
                        "Initial Missing Count": int(n_missing),
                        "Is Method Good?": "YES" if std < 0.5 else "NO"
                    })
            return pd.DataFrame(results)

        def prepare_plot_data(protein_name):
            records = []
            initial_row = df_initial[df_initial[id_column] == protein_name]
            if initial_row.empty:
                return pd.DataFrame()
            initial_vals = initial_row[intensity_cols].values.flatten()
            records += [{"Value": v, "Method": "Original (raw)"} for v in initial_vals if not pd.isna(v)]

            for file in os.listdir(merge_folder_path):
                if file.startswith("merged_") and file.endswith(".xlsx"):
                    method = file.replace("merged_", "").replace(".xlsx", "")
                    df = pd.read_excel(os.path.join(merge_folder_path, file))
                    row = df[df[id_column] == protein_name]
                    if row.empty:
                        continue
                    vals = row[intensity_cols].values.flatten()
                    records += [{"Value": v, "Method": method} for v in vals if not pd.isna(v)]

            return pd.DataFrame(records)

        st.markdown(f"### 📋 Results for `{selected_protein}`")
        stats_df = calc_protein_stats(selected_protein)

        if not stats_df.empty:
            st.download_button(
                label="⬇️ Download results as CSV",
                data=stats_df.to_csv(index=False).encode("utf-8"),
                file_name=f"{selected_protein}_evaluation.csv",
                mime="text/csv"
            )
            st.dataframe(stats_df, use_container_width=True)

            plot_df = prepare_plot_data(selected_protein)
            if not plot_df.empty:
                st.markdown("### 🛆 Value Distribution (Boxplot)")
                fig1, ax1 = plt.subplots(figsize=(12, 5))
                sns.boxplot(data=plot_df, x="Method", y="Value", ax=ax1)
                ax1.set_title(f"Boxplot – {selected_protein}")
                ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")
                st.pyplot(fig1)

                st.markdown("### 🔍 Estimated Distribution (Density Plot)")
                fig2, ax2 = plt.subplots(figsize=(20, 8))
                for method in plot_df["Method"].unique():
                    subset = plot_df[plot_df["Method"] == method]["Value"]
                    sns.kdeplot(subset, label=method, ax=ax2)
                ax2.set_title(f"Value Density – {selected_protein}")
                ax2.legend()
                st.pyplot(fig2)
            else:
                st.warning("⚠️ No values found for plots.")
        else:
            st.warning("⚠️ Protein not found in imputed files.")

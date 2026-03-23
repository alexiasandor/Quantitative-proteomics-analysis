MESSAGES = {
    "processing_messages": {
        "upload": "📂 Upload your Excel file (.xlsx)",
        "upload_success": "✅ File successfully uploaded!",
        "rows_before": f"📊 Rows before processing:",
        "keep_cols": "✅ Select columns to KEEP:",
        "log_cols": "🔢 Select columns to apply log2:",
        "apply_btn": "🧪🚀🔢Apply Preprocessing",
        "rows_after": f"📊 Rows after processing:",
        "nan_nr": "ℹ️ Number of Nans per numeric column",
        "success_msg": "✅ File procesed and saved",
        "saved": "📂 Saved in",
        "split_msg": "🧬 Split Processed File",
        "value_for_disease": "💊Select value for 'Diseased': ",
        "value_for_healthy": "🧠Select value for 'Healthy': ",
        "split": "🧬 Files split and saved as diseased/healthy!",
        "removed": "🔍 Removed",
        "split_by_taxonomy": " 🔬 Split by selected taxonomy)",
        "split_by": "Split by selected column sets(structure only)",
        "generate_files": "📂 Generate Files by Column Selection",
        "select_col": "⚠️Please select at least one column for each gorup",
        "files_created": "✅ Files created with selected columns only",
        "removed_proteins": " rows with all Nans from either group",
        "reset_workflow": "🔄 Reset Workflow"
    },

    "imputation_messages": {
        "select_folder": "📁 Select a processed folder:",
        "load_files": "🔍 Load Files",
        "file_not_found": "⚠️ No Excel files found in selected folder.",
        "select_d": "💊 Select DISEASED file:",
        "select_h": "🧬 Select HEALTHY file:",
        "loaded": "✅ Loaded:",
        "run": "🚀 Run Imputation Methods",
        "v": "✅",
        "error": "❌ Error running",
        "success_message": "🎉 All imputations completed and saved!",
        "merge": "🔗 Merge Healthy + Diseased per method",
        "no_matching": "⚠️ No matching imputation methods found.",
        "saved": f"✅ Merged and saved:",
        "merge_completed": "🎉 Merging complete!",
        "info": "ℹ️ Select a folder and press **Load Files** to begin."

    },
    "analysis_messages": {
        "select_folder_1": "📁 Select  processed folder:",
        "select_folder_2": "📁 Select merged folder:",
        "run": "▶ Run Similarity Analysis",
        "select_file": "📄 Select clean file:",
        "run_info": "🔄 Running similarity analysis...",
        "view_tab": " 📊 Tabular view of top pairs",
        "no_saved": "No saved results for dataset",
        "similarity_success": "✅ Similarity analysis completed!",
        "common_methods": "✅ Common top methods across metrics:",
        "select_methods": "🔘 Select all methods",
        "download_methods": "📥 Download selected methods ",
        "download_file": " 📂 Download associated merged files:",
        "download": "⬇ Download",
        "file": "❌ File for",
        "not_exist": "does not exist.",
        "select": "☑ Select at least one method to download.",
        "no_methods": "⚠ No common methods found across metrics.",
        "no_data": "⚠ Not enough data to compute common methods.",
        "file_not_found": "Top methods file not found. Please run the analysis first."

    },
    "analysis_by_deviation_messages": {
        "select_folder_1": "📁 Select  processed folder:",
        "select_file_processed": "📄 Select processed file:",
        "select_folder_2": "🔀 Select merged folder:",
        "select_protein": "🔍 Select protein with missing values:",
        "run": "🚀 Run analysis",
        "results": "📋 Results for",
        "download": "⬇️ Download results as CSV",
        "value_distribution": "🛆 Value Distribution (Boxplot)",
        "estimated": "🔍 Estimated Distribution (Density Plot)",
        "no_values": "⚠️ No values found for plots.",
        "no_protein": "⚠️ Protein not found in imputed files."

    },
    "analysis_by_miss_rate_messages": {
        "select_folder_1": "📁 Select  processed folder:",
        "select_file_processed": "📄 Select processed file:",
        "select_folder_2": "🔀 Select merged folder:",
        "select_col": "🔢 Select the column identifying proteins:",
        "run": "🚀 Run analysis",
        "method_perf": "📄 Method Performance Summary",
        "recommended": "💡 Recommended Methods Based on Missingness Rate",
        "good_methods": " ✅ Good methods for ",
        "no_methods": "⚠️ No methods passed the threshold for"
    },
    "view_imputations": {
        "select_folder_1": "📁 Select  processed folder:",
        "select_file": "📄 Select processed file:",
        "select_folder_2": "🔀 Select merged folder:",
        "view_merged": "🔍 View Merged Files Individually",
        "preview": "📄 Preview of",
        "comparison": " 🔬 Protein-Level Comparison (by Gene/Entry name)",
        "select": "Select Gene/Entry name and LFQ column:",
        "exclude": "Exclude methods with missing values",
        "val_not_found": "No imputed values found for this selection.",
        "file_not_found": "Initial file not found or no missing values detected."

    },
    "view_processed": {
        "select_folder_1": "📁 Select  processed folder:",
        "folder_not_found": "❌ No folders found in `data/processed/`.",
        "no_xlsx": "📂 No `.xlsx` files found in the selected folder.",
        "select_file_processed": "📄 Select a processed file to view:",
        "show": "📄 Showing contents of ",
        "download": "📥 Download this file"
    },
    "calc_sim": {
        "warning_msg": "⚠️ No data to comper. Imputed matrix is empty. Please check input files and mask alignment !",
        "sim": "📊 Similiarity matrix shape"
    }

}

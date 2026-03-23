
import gc
import re
import pandas as pd
import numpy as np

# functie helper pentru mad imputer
def mad_imputer_column(col):
    mad = np.median(np.abs(col.dropna() - col.median())) # calculam mad fara valori lipsa
    # cream un vector cu valori in jurul lui mad
    random_values = col.median() + np.random.uniform(-1, 1, size=col.shape[0]) * mad
    # inlocuim valorile lipsa cu cele generate
    return col.where(~col.isna(), random_values)

# functie helper pentru identificarea grupului din coloana
def extract_column_group(col_name):
    match = re.search(r"Intensity.([A-Z]+)", col_name)
    if match:
        return match.group(1)
    match= re.search(r"LFQ intensity ([HL])", col_name)
    if match:
        return match.group(1)
    return None


#functie helper pentru groupwise median
def groupwise_median_from_column_prefix(row):
    group_map = {col: extract_column_group(col) for col in row.index}
    row_copy = row.copy()

    for group in set(group_map.values()):
        if group is None:
            continue
        group_cols = [col for col in row.index if group_map[col] == group]
        if group_cols:
            median_val = row[group_cols].median()
            row_copy[group_cols] = row[group_cols].fillna(median_val)

        return row_copy

# definirea unei liste cu metodele complexe

heavy_methods = {
    "iterative_bayesianridge",
    "bpca_imputer",
    "mice_linear",
    "iterative_imputer_10",
    "soft_impute",
    "missforest_equivalent",
    "mice_tree"
}
# functie helper pentru imputare pe chunk-uri
def impute_in_chunks(df,cols, method_func, chunk_size =500):
    results = []
    for start in range(0,len(df), chunk_size):
        end = start + chunk_size
        chunk = df.iloc[start:end]
        chunk_imputed = method_func(chunk.copy(), cols)
        results.append(chunk_imputed)
        del chunk, chunk_imputed
        gc.collect()
    return pd.concat(results, axis=0)

# functie helper care decide daca aplica pe bucati sau nu
def apply_imputation(df, cols, method_name, method_func, chunk_size = 500, st_logger = None):
    if method_name in heavy_methods:
        if st_logger:
            st_logger.info(f" Running {method_name} in chunks ({chunk_size}) proteins per chunk")
            return impute_in_chunks(df, cols, method_func, chunk_size)

    else:
        result = method_func(df, cols)
        gc.collect()
        return result

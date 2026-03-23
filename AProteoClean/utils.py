import numpy as np


def process_xls_file(df, keep_cols=None, log_cols=None):
    df = df.copy()
    if keep_cols:
        df = df[keep_cols]  ## pastram in noul dataframe doar coloanele selectate

    if log_cols:
        for col in log_cols:
            if col in df.columns:
                df[col] = df[col].replace(0, np.nan)
                df[col] = np.log2(df[col])

    return df

import os
import json
import pandas as pd
import numpy as np
from metrics import (
    pearson_similarity, spearman_similarity, kendall_similarity,
    euclidean_distance, manhattan_distance, cosine_similarity,
    canberra_distance
)
import streamlit as st
from messages import *
# functie pentru crearea mastilor

def create_mask(initial_file):
    initial_df = pd.read_excel(initial_file) #citim fisierul initial
    initial_df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    intensity_cols = [col for col in initial_df.columns if 'intensity' in col.lower()]
    df_intensity_only = initial_df[intensity_cols]
    mask = df_intensity_only.notna().astype(int)
    return mask, df_intensity_only

#functie pentru crearea matricii aferente

def build_imputed_matrix(initial_file, input_folder, input_files, masks_folder=None, intermediars_folder=None):

    mask,_ = create_mask(initial_file)

    os.makedirs(masks_folder, exist_ok=True)
    os.makedirs(intermediars_folder, exist_ok=True)

    mask_file_name = os.path.splitext(os.path.basename(initial_file))[0]
    mask.to_excel(os.path.join(masks_folder, f'mask_{mask_file_name}.xlsx'), index=False)

    merged_df = pd.DataFrame()
    print("fisiere de analizat", input_files)

    for file in input_files:
        method_name = file.replace('.xlsx', '')
        df=pd.read_excel(os.path.join(input_folder, file))
        intensity_cols = [col for col in df.columns if 'intensity' in col.lower()]
        df_intensity = df[intensity_cols]

        impute_only = df_intensity.where(mask==0)
        method_mask = df_intensity.copy()

        for col in method_mask.columns:
            method_mask[col]= method_mask[col].where(mask[col] == 0, other =1)

        method_mask.to_excel(os.path.join(masks_folder, f'mask_{method_name}.xlsx'), index=False)

        impute_only_long= impute_only.copy()
        impute_only_long.index = df.index
        merged_df[method_name]=impute_only.stack()

        merged_df_reset = merged_df.reset_index()
        merged_df_reset.to_excel(os.path.join(intermediars_folder, f'intermediar_{method_name}.xlsx'), index=False)

    merged_df.dropna(how='all', inplace=True)
    return merged_df

# functie helper pentru calculul similaritatii
def calculate_similarity_on_imputed(initial_file, input_folder, input_files, selected_metric,  masks_folder=None, intermediars_folder=None):

    # selectare folder pentru masti
    parent_dir = os.path.dirname(input_folder)

    #extragere subfolder daca exista

    def find_existing_subfolder(base_dir, prefix):
        for name in sorted(os.listdir(base_dir)):
            if name.startswith(prefix) and os.path.isdir(os.path.join(base_dir, name)):
                return os.path.join(base_dir, name)
        return None

    #crearea folder daca nu exista
    def create_new_subfolder(base_dir, prefix):
        index = 1
        while os.path.exists(os.path.join(base_dir, f"{prefix}_{index}")):
            index += 1
        path = os.path.join(base_dir, f"{prefix}_{index}")
        os.makedirs(path, exist_ok=True)
        return path

    #crearea folderului daca nu exista
    if masks_folder is None:
        masks_folder = find_existing_subfolder(parent_dir, "masks")
        if not masks_folder:
            masks_folder = create_new_subfolder(parent_dir, "masks")

    # crearea folderului pentru rezultate intermediare
        intermediars_folder = find_existing_subfolder(parent_dir, "intermediars")
        if not intermediars_folder:
            intermediars_folder = create_new_subfolder(parent_dir, "intermediars")

    #matricea de imputari
    data_df = build_imputed_matrix(initial_file, input_folder, input_files, masks_folder=masks_folder, intermediars_folder=intermediars_folder)

    if data_df.empty:
        # stcker-ul a fost preluat din panoul pus la dispozitie de windows prin combinatia de taste Win+.
        st.warning(MESSAGES["calc_sim"]["warning_msg"])
        return pd.DataFrame(), [], pd.DataFrame(), []


    #apelarea metricii selectate
    if selected_metric == 'Pearson':
        result_df = pearson_similarity(data_df)
    elif selected_metric == 'Spearman':
        result_df = spearman_similarity(data_df)
    elif selected_metric == 'Kendall':
        result_df = kendall_similarity(data_df)
    elif selected_metric == 'Euclidean':
        result_df = euclidean_distance(data_df)
    elif selected_metric == 'Manhattan':
        result_df = manhattan_distance(data_df)
    elif selected_metric == 'Cosine':
        result_df = cosine_similarity(data_df)
    elif selected_metric == 'Canberra':
        result_df = canberra_distance(data_df)
    else:
        raise ValueError(f'Selected metric {selected_metric} not implemented')

    ascending = selected_metric in ['Euclidean', 'Manhattan', 'Canberra']
    # cutarea metodelor celor mai bune

    if intermediars_folder:
        result_df.to_excel(os.path.join(intermediars_folder, f'intermediar_similarity_{selected_metric}.xlsx'), index=True)

    messages, top_pairs_df, method_list = extract_top_pairs(result_df, top_n=5,ascending=ascending)
    st.write(MESSAGES["calc_sim"]["sim"], result_df.shape)
    st.dataframe(result_df.style.format(precision=6))
    # salvare in json
    json_file = 'top_methods.json'
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            try:
                top_methods = json.load(f)
                if isinstance(top_methods, list):
                    top_methods = {"legacy": top_methods}
            except json.decoder.JSONDecodeError:
                top_methods ={}
    else:
        top_methods = {}

    top_methods[selected_metric] = method_list

    with open(json_file, 'w') as f:
        json.dump(top_methods, f, indent=4)

    return result_df,messages,top_pairs_df, method_list

    # extragera metodelor cu cel mai mare scor
def extract_top_pairs(matrix_df, top_n=5, ascending=False):
    pairs = matrix_df.unstack().reset_index()
    pairs.columns = ['Method1', 'Method2', 'Score']
    pairs = pairs[pairs['Method1'] != pairs['Method2']]
    pairs['pair'] = pairs.apply(lambda row: tuple(sorted([row['Method1'], row['Method2']])) , axis=1)
    pairs = pairs.drop_duplicates('pair')
    pairs = pairs.sort_values('Score', ascending=ascending).reset_index(drop=True)

    unique_scores = pairs['Score'].unique()[:top_n]
    top_pairs = pairs[pairs['Score'].isin(unique_scores)].reset_index(drop=True)

    messages = [
        f" * {row['Method1']}  <-> {row['Method2']} -> Score: {row['Score']:.4f}"
        for _, row in top_pairs.iterrows()
    ]
    
    method_set = set(top_pairs['Method1']).union(set(top_pairs['Method2']))
    return messages, top_pairs, list(method_set)
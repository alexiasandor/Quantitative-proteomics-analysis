import pandas as pd
import numpy as np
import dcor
from scipy.spatial.distance import pdist, squareform
from scipy.spatial.distance import canberra


#definirea metricilor

#metrici de corelatie
def pearson_similarity(df):
    return df.corr(method='pearson')


def spearman_similarity(df):
    return df.corr(method='spearman')


def kendall_similarity(df):
    return df.corr(method='kendall')


#merici de distanta
def euclidean_distance(df):
    dist_matrix = pd.DataFrame(
        squareform(pdist(df.T, metric='euclidean')), # calculam transpusa
        index=df.columns,
        columns=df.columns
    )
    return dist_matrix


def manhattan_distance(df):
    dist_matrix = pd.DataFrame(
        squareform(pdist(df.T, metric='cityblock')),
        index=df.columns, # simetrie pentru dataframe
        columns=df.columns
    )
    return dist_matrix


def cosine_similarity(df):
    cosine_matrix = pd.DataFrame(
        1 - squareform(pdist(df.T, metric='cosine')), # folosim formula 1- distanta pentru a obtine similaritatea
        index=df.columns,
        columns=df.columns
    )
    return cosine_matrix

def canberra_distance(df):
    methods = df.columns # selectam numele coloanelor
    result = pd.DataFrame(index = methods, columns = methods, dtype = float) #construim matricea finala
    #parcurgem perechile de coloane si calculam distanta
    for method1 in methods:
        for method2 in methods:
            result.loc[method1,method2] = canberra(df[method1], df[method2])

    return result

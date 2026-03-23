import pandas as pd
import numpy as np
import re
import gc

from imputation_helper import *
from fancyimpute import SoftImpute, IterativeSVD
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, IterativeImputer
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import BayesianRidge, LinearRegression




# dictionarul metodelor de completare automata

imputations = {
    #comletare cu media
    "fillna_mean" : lambda df, cols: df[cols].apply(lambda row: row.fillna(row.mean()), axis=1),
    #completare cu mediana
    "replace_median" :lambda df, cols: df[cols].apply(lambda row: row.fillna(row.median()), axis=1),
    #completare cu KNN 10
    "knn_imputer_10": lambda df, cols: pd.DataFrame(
        KNNImputer(n_neighbors=10).fit_transform(df[cols].T).T, columns = cols, index = df.index),
    #completare cu KNN 20
    "knn_imputer_20": lambda df, cols: pd.DataFrame(
        KNNImputer(n_neighbors=20).fit_transform(df[cols].T).T, columns=cols, index=df.index),
    #completare cu mice+bayesian ridge
    "iterative_bayesianridge": lambda df, cols: pd.DataFrame(
        IterativeImputer(estimator= BayesianRidge(), max_iter=25, tol =1e-4, random_state=0,verbose=0).
        fit_transform(df[cols].astype(np.float32).T).T, columns=cols, index=df.index),

    # completare cu mice simplu
    "iterative_imputer_10": lambda df, cols: pd.DataFrame(
      IterativeImputer(max_iter=10,tol =1e-4, random_state=0)
      .fit_transform(df[cols].T).T, columns=cols, index=df.index),

    #completare cu soft impute
    "soft_impute": lambda df, cols: pd.DataFrame(
      SoftImpute(max_iters=50, convergence_threshold=1e-5, init_fill_method="mean", verbose=False)
        .fit_transform(df[cols].T).T, columns=cols, index=df.index
    ),

    #completare cu miss forest
    "missforest_equivalent": lambda df, cols: pd.DataFrame(
        IterativeImputer(estimator=ExtraTreesRegressor(n_estimators=10, random_state=0), max_iter=20, tol =1e-4, random_state=0, verbose=0)
        .fit_transform(df[cols].T).T, columns=cols, index=df.index
    ),

    # mice + decision trees

    "mice_tree": lambda df, cols: pd.DataFrame(
        IterativeImputer(estimator=DecisionTreeRegressor(random_state=0), max_iter=20, tol =1e-4, random_state=0, verbose=0)
        .fit_transform(df[cols].T).T, columns=cols, index=df.index),
    # implementare groupwise
    "groupwise_median_by_prefix": lambda df, cols:df[cols].apply(groupwise_median_from_column_prefix, axis=1),

    # min fraction
    "min_fraction":lambda df, cols:df[cols].apply(
        lambda col: col.fillna(col.min() * np.random.uniform(0.3, 0.7))),

    # implementare lod
    "lod_imputer": lambda df, cols:df[cols].apply(
        lambda col: col.fillna(np.random.normal(loc=np.percentile(col.dropna(), 1), scale = 0.3 *np.nanstd(col.dropna()) ))),

    # implementare quantille
    "quantile_normal": lambda df, cols: df[cols].apply(
        lambda col: col.fillna(np.random.normal(loc=col.mean() - 1.8 * col.std(), scale = 0.3*col.std()))),

    #beta imputation
    "beta_imputer": lambda df, cols:df[cols].apply(
        lambda col:col.where(~col.isna(), pd.Series(np.random.beta(2,5, size = col.isna().sum())
                *  (col.max() - col.min()) + col.min(), index=col.index[col.isna()]))
    ),

    # implementare hotdeck
    "hotdeck_imputer": lambda df, cols:df[cols].apply(
        lambda col: col.where(~col.isna(),
        pd.Series(np.random.choice(col.dropna(), size=col.isna().sum(), replace=True), index=col.index[col.isna()]))
    ),

    #implementare trimmed mean
    "trimmed_mean": lambda df, cols:df[cols].apply(
        lambda col:col.fillna(col[(col>col.quantile(0.1)) & (col < col.quantile(0.9))].mean())
    ),

    #implementare mad imputer
    "mad_imputer":lambda df, cols:df[cols].apply(mad_imputer_column),

    # implementare bpca
    "bpca_imputer": lambda df, cols: pd.DataFrame(
        IterativeSVD(rank=3, max_iters=50, convergence_threshold=1e-5, init_fill_method="mean", verbose=False)
        .fit_transform(df[cols].T).T, columns=cols, index=df.index
    ),

    # mice linea
    "mice_linear": lambda df, cols: pd.DataFrame(
        IterativeImputer(estimator=LinearRegression(), max_iter=25, tol=1e-4, random_state=0, verbose=0)
        .fit_transform(df[cols].T).T, columns=cols, index=df.index
    ),

    # metoda empirical
    "empirical_sampling": lambda df,cols:df[cols].apply(
        lambda col : col.where(~col.isna(), pd.Series(np.random.choice(col.dropna(), size=col.isna().sum(), replace=True), index=col.index[col.isna()]))
    ),

    # minprob imputation
    "minprob_imputer": lambda df, cols:df[cols].apply(
        lambda col: col.fillna(np.random.normal(loc=col.mean() - 1.8* col.std(), scale=0.3 * col.std())),
    )
}
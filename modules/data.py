from ucimlrepo import fetch_ucirepo
import pandas as pd
import streamlit as st
from itertools import combinations
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_recall_fscore_support
import numpy as np

# Fetch data for UCI Machine Learning Repository
iris = fetch_ucirepo(id = 53)
iris.data.keys()
# Generate pandas DataFrame
default_df = pd.DataFrame(
    data = iris.data.features,
    columns = iris.data.headers)

default_df['species'] = iris.data.targets
default_df = default_df.drop('class', axis = 1)
default_df.columns = default_df.columns.str.replace(' ', '_')

def col_score(data:pd.DataFrame, X:list, y:str, avg: str, k: int = 6):
    col_score_bar = st.progress(0, 'Computing data...')
    col_score_dict = {'variable':[],
                      'accuracy':[],
                      'precision':[],
                      'recall':[],
                      'f1':[]}
    
    for index, item in enumerate(X):
        
        col_score_bar.progress(value = round(index/len(X), 1),
                               text = f'Computing data... {round(index/len(X) * 100, 1)}%')
        
        X_train, X_test, y_train, y_test = train_test_split(
            data[item].values.reshape(-1, 1),
            np.ravel(data[y].values.reshape(-1, 1)),
            train_size = .2,
            stratify = data[y].values.reshape(-1, 1),
            random_state = 17)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        knn = KNeighborsClassifier(n_neighbors = k, n_jobs = -1)
        knn.fit(X_train_scaled, y_train)
        col_score_dict['variable'].append(item)
        acc = round(knn.score(X_test_scaled, y_test), 2)
        
        y_pred = knn.predict(X_test_scaled)
        
        prec, recall, f1, support = precision_recall_fscore_support(
            y_true = y_test,
            y_pred = y_pred,
            average = avg)
        
        for key, var in {'accuracy': acc,
                    'precision': prec,
                    'recall': recall,
                    'f1':f1}.items():
            
            col_score_dict[key].append(var)
            
    col_score_df = pd.DataFrame(col_score_dict).sort_values(
        by = 'accuracy', ascending = False).reset_index(drop = True)
    
    col_score_bar.empty()
    
    return col_score_df

def k_score(data: pd.DataFrame, X: list, y: str, k_max: int):
    
    k_score_dict = {'k':[], 'accuracy_test':[], 'accuracy_train':[]}
    
    if len(X) == 1:
            X_reshaped = data[X].values.reshape(-1, 1)
    else:
        X_reshaped = data[X].values
        
    X_train, X_test, y_train, y_test = train_test_split(
        X_reshaped,
        np.ravel(data[y].values.reshape(-1, 1)),
        train_size = .2,
        random_state = 17,
        stratify = data[y].values.reshape(-1, 1))
    
    
    scaler = StandardScaler()
    scaler.fit_transform(X_train)
    scaler.transform(X_test)
    
    for k_value in np.arange(1, k_max + 1):
        
        knn = KNeighborsClassifier(k_value)
        knn.fit(X_train, y_train)
        score_train = knn.score(X_train, y_train)
        score_test = knn.score(X_test, y_test)
        
        k_score_dict['k'].append(k_value)
        k_score_dict['accuracy_test'].append(score_test)
        k_score_dict['accuracy_train'].append(score_train)
    
    return pd.DataFrame(k_score_dict)

def gen_knn(data: pd.DataFrame,
            X: list, X_to_pred: list, y:str, k: int):
    
    if len(X) == 1:
        X_reshaped = data[X].values.reshape(-1, 1)
        X_to_pred_reshaped = np.array(X_to_pred).reshape(-1, 1)
        
    else:
        X_reshaped = data[X].values
        X_to_pred_reshaped = np.array(X_to_pred)
    
    y_train = np.ravel(data[y].values.reshape(-1,1))
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_reshaped)
    X_to_pred_scaled = scaler.transform(X_to_pred_reshaped)
    
    knn = KNeighborsClassifier(n_neighbors = k)
    knn.fit(X_scaled, y_train)
    prediction = knn.predict(X_to_pred_scaled)
    
    return prediction
            
# def knn_global_metric(data: pd.DataFrame, X: list, y: str, k: int,
#                       key_metric: str):
    
#     X_train, X_test, y_train, y_test = train_test_split(
#         data[X].values,
#         data[y].values.reshape(-1, 1),
#         test_size = .2,
#         stratify = data[y].values.reshape(-1, 1))
    
#     knn = KNeighborsClassifier(n_neighbors = k)
#     scaler = StandardScaler()

#     X_train = scaler.fit_transform(X_train)
#     X_test = scaler.transform(X_test)

#     knn.fit(X_train, np.ravel(y_train))
#     y_pred = knn.predict(X_test)

#     accuracy = accuracy_score(y_test, y_pred)
#     precision = precision_score(y_test, y_pred, average = 'weighted')
#     recall = recall_score(y_test, y_pred, average = 'weighted')
    
#     key_metric_allowed_values = ['prec', 'recall', 'none']
    
#     if key_metric not in key_metric_allowed_values:
#         raise ValueError(
#             f'Invalid "key_metric" value. Allowed values are {key_metric_allowed_values}')
    
#     if key_metric == 'prec':
#         mean_metric = (.2 * accuracy + .5 * precision + .3 * recall)
        
#     elif key_metric == 'recall':
#         mean_metric = (.2 * accuracy + .3 * precision + .5 * recall)
        
#     elif key_metric == 'none':
#         mean_metric = (.2 * accuracy + .4 * precision + .4 * recall)
        
#     return mean_metric

# k_mean_values_dict = {}

# knn_global_metric(default_df, list(default_df.columns.drop('Cover_Type')), 'Cover_Type', 9, 'str')
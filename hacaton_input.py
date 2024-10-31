import pandas as pd
import datetime
import os
from hacaton_preproc import class_cluster, time_borders, dist_cluster, sell_cluster, optim_clust
from hacaton_preproc import preproc_delivery_time, construct_column_from_lookup

def lots_distr(input_path, metr=False):
    
    data_input = pd.read_excel(input_path)
    
    #change these paths to your local ones when adding!
    hist_path = 'data/Исторические совершенные закупки товаров.csv'
    df_mtr = pd.read_excel('data/Кабель справочник МТР.xlsx')
    df_deliv = pd.read_excel('data/КТ-516 Разделительная ведомость на поставку МТР с учетом нормативных сроков поставки.xlsx', header=23)
    df_cargo = pd.read_excel('data/Справочник грузополучателей.xlsx')
        
    data = preproc_delivery_time(data_input, df_mtr, df_deliv, df_cargo)
    data_hist = pd.read_csv(hist_path)
    
    label_encoder = LabelEncoder()
    data_preprocessed = pd.DataFrame()
    data_preprocessed['Код класса МТР'] = data['Код класса МТР'].copy()
    data_preprocessed['Кредитор'] = construct_column_from_lookup(data.copy(), data_hist, 'Код класса МТР', 'Поставщик')

    data['lat'] = data['Код класса МТР'].copy()
    data['lon'] = data['Код класса МТР'].copy()

    data_preprocessed['Дата заявки'] = data['Дата заявки'].copy()
    data_preprocessed['Срок поставки'] = data['Срок поставки'].copy()

    #make clusters from MTR class as dict = {'Class': Dataframe}
    datasets = class_cluster(data)
    datasets_preprocessed = class_cluster(data_preprocessed)

    #make clusters for each "request month" - "delivery month" pair (list inside every Dataframe in dict)
    for Class in datasets.keys():
        datasets[Class] = time_borders(datasets[Class])
        datasets_preprocessed[Class] = time_borders(datasets_preprocessed[Class])
    
    #make clusters for each distance group (list inside previously mentioned list) 
    cords_path = 'data/cwc.csv'
    clients_path = 'data/clients.csv'
    error_lines = []
    ds_dist = datasets.copy()
    ds_pr_dist = datasets_preprocessed.copy()

    for Class in datasets.keys():
        for i in range(len(datasets[Class])):
            ds_dist[Class][i], cluster_labels, errors, error_index = dist_cluster(ds_dist[Class][i], cords_path, clients_path)
            error_lines.append(errors)
            print(ds_dist[Class][i])
            print(ds_pr_dist[Class][i])
            ds_pr_dist[Class][i] = ds_pr_dist[Class][i].reset_index(drop=True)
            ds_pr_dist[Class][i] = ds_pr_dist[Class][i].drop(index=error_index)
            ds_pr_dist[Class][i]['dist'] = cluster_labels
            ds_dist[Class][i] = ds_dist[Class][i].drop(columns=['lat', 'lon']) # and 'dist'
            ds_pr_dist[Class][i] = ds_pr_dist[Class][i].drop(columns=['Дата заказа', 'Срок поставки'])
            
    for Class in ds_dist.keys():
        for i in range(len(ds_dist[Class])):
            ds_pr_dist[Class][i] = [ds_pr_dist[Class][i][ds_pr_dist[Class][i]['dist'] == dist_num] for dist_num in range(ds_pr_dist[Class][i]['dist'].nunique())]
            ds_dist[Class][i] = [ds_dist[Class][i][ds_dist[Class][i]['dist'] == dist_num] for dist_num in range(ds_dist[Class][i]['dist'].nunique())]

    #delete unnesesary column
    for Class in ds_dist.keys():
        for i in range(len(ds_dist[Class])):
            for j in range(len(ds_dist[Class][i])):
                ds_pr_dist[Class][i][j] = ds_pr_dist[Class][i][j].drop(columns='dist')
                
    
    #create lots
    lots = []

    for Class in ds_dist.keys():
        for i in range(len(ds_dist[Class])):
            data_entries = ds_dist[Class][i]
            prepr_entries = ds_pr_dist[Class][i]
            
            if isinstance(data_entries, list):
                for j in range(len(data_entries)):
                    data_orig = data_entries[j]
                    data_prepr = prepr_entries[j]
                    optimised_data = optim_clust(data_orig, data_prepr, metr)
                    
                    if optimised_data is not None:
                        for num in optimised_data['cluster'].unique():
                            lot = optimised_data[optimised_data['cluster'] == num]
                            lots.append(lot)
                    else:
                        print(f"Clustering failed for Class {Class}, i={i}, j={j}")
            else:
                data_orig = data_entries
                data_prepr = prepr_entries
                optimised_data = optim_clust(data_orig, data_prepr, metr)
                
                if optimised_data is not None:
                    for num in optimised_data['cluster'].unique():
                        lot = optimised_data[optimised_data['cluster'] == num]
                        lots.append(lot)
                else:
                    print(f"Clustering failed for Class {Class}, i={i}")
                    
    #delete redundant columns
    for i in range(len(lots)):
        lots[i] = lots[i].drop(columns=['dist', 'cluster'])

    metr_dict = 0
    
    if metr:
        return lots, metr_dict
    else:
        return data

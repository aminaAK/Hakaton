import numpy as np
import pandas as pd
import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from .input_file_preprocessing import preproc_delivery_time

file_path = 'main/processed_new_Исторические_данные_по_офертам_поставщиков_на_лот.csv'
data = pd.read_csv(file_path)

manual_lot_count = 4996
manual_avg_price = 910874

label_encoder = LabelEncoder()
data_preprocessed = pd.DataFrame()
data_preprocessed['Класс'] = label_encoder.fit_transform(data['Класс'])
data_preprocessed['Кредитор'] = label_encoder.fit_transform(data['Кредитор'])

scaler = StandardScaler()
data_scaled = scaler.fit_transform(data_preprocessed)

k = 1500

kmeans = KMeans(n_clusters=k, random_state=42)
data['cluster'] = kmeans.fit_predict(data_scaled)

data['Материал_Класс'] = data['Класс'].astype(str)
data['pairs_per_clust'] = data.groupby('cluster')['Материал_Класс'].transform('nunique')
data['pairs_by_cred'] = data.groupby(['Кредитор', 'cluster'])['Материал_Класс'].transform('nunique')
data['perc_cov'] = (data['pairs_by_cred'] / data['pairs_per_clust']) * 100

def categorize_coverage(percentage):
    if 80 > percentage >= 50:
        return '≥ 50%'
    elif 100 > percentage >= 80:
        return '≥ 80%'
    elif percentage == 100:
        return '100%'

data['cov_cat'] = data['perc_cov'].apply(categorize_coverage)

# Group by cluster and calculate the number of creditors in each category
creditor_counts_by_category = data.groupby(['cluster', 'cov_cat'])['Кредитор'].nunique().reset_index()
cred_count = data.groupby(['cluster', 'cov_cat'])['Кредитор'].transform('nunique')
data['num_creditors'] = cred_count
creditor_counts_by_category.columns = ['cluster', 'cov_cat', 'num_creditors']
avg_creditors_per_category = creditor_counts_by_category.groupby('cov_cat')['num_creditors'].mean().reset_index()

average_creditors_le_50 = avg_creditors_per_category.loc[
    (avg_creditors_per_category['cov_cat'] == '≥ 50%') | 
    (avg_creditors_per_category['cov_cat'] == '≥ 80%') | 
    (avg_creditors_per_category['cov_cat'] == '100%'), 
    'num_creditors'
    ].values[0]
average_creditors_50_to_80 = avg_creditors_per_category.loc[
    (avg_creditors_per_category['cov_cat'] == '≥ 80%') |
    (avg_creditors_per_category['cov_cat'] == '100%'),
    'num_creditors'
    ].values[0]
average_creditors_ge_80 = avg_creditors_per_category.loc[avg_creditors_per_category['cov_cat'] == '100%', 'num_creditors'].values[0]
average_creditors_per_lot = data.groupby('cluster')['Кредитор'].nunique().mean()

num_lots = data['cluster'].nunique()
average_price_per_lot = data.groupby('cluster')['Сумма во ВВ'].sum().mean()

MQ = 0.5 * ((1 - num_lots / manual_lot_count) + (1 - manual_avg_price / average_price_per_lot))

MS = (2 * average_creditors_le_50 + 3 * average_creditors_50_to_80 + 4 * average_creditors_ge_80) / average_creditors_per_lot

data_input = pd.read_excel('main/Test_input_file.xlsx')
df_mtr = pd.read_excel('main/Кабель справочник МТР.xlsx')
df_deliv = pd.read_excel('main/КТ-516 Разделительная ведомость на поставку МТР с учетом нормативных сроков поставки.xlsx', header=23)

data_final = preproc_delivery_time(data_input, df_mtr, df_deliv)

lots = []
for i in range(len(data_final)):
    if data_final.iloc[i]['Ошибка'] == 0 and data_final.iloc[i]['Доставка: да/нет'] == 'Да':
        all_sublots = data[data['Класс'] == data_final.iloc[i]['Код класса МТР']]
        unique_clusters = all_sublots['cluster'].unique()
        dataframes_by_cluster = [all_sublots[all_sublots['cluster'] == cluster] for cluster in unique_clusters]
        result_df = [data_final.iloc[i], dataframes_by_cluster]
        lots.append(result_df)
    else:
        lots.append([data_final.iloc[i]])

#structure of lots:
#lots[i] -- одна заявка и все лоты для нее
#lots[i][0] -- датафрейм из 1 строки, сама заявка
#lots[i][1] -- одит датафрейм или лист из датафреймов, лоты для каждой заявки
#lots[i][1][j] -- конкретная строка внутри лота

# for i in range(1):
#     for j in range(5):
#      print(type(lots[i][0][j]))
# req = pd.DataFrame(len(lots))
# for i in range(len(lots)):  
#     req[i] = lots[i][0]
# print(req)

def Lot():
    return lots
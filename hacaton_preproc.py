import pandas as pd
import datetime
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import DBSCAN
import numpy as np


def construct_column_from_lookup(df1, df2, lookup_col, target_col):
    # Initialize an empty list to store the result
    result_values = []
    
    # Go through each element in the lookup column of df1
    for element in df1[lookup_col]:
        # Search for the element in df2's lookup column
        match_row = df2[df2[lookup_col] == element]
        
        # If a match is found, get the value from the target column (first match only)
        if not match_row.empty:
            result_values.append(match_row[target_col].values[0])
        else:
            # If no match is found, append NaN or a placeholder value
            result_values.append(np.nan)
    
    # Add the result list as a new column in df1
    return result_values


def class_cluster(data):
    class_names = ['G2104', 'G2105', 'G2106', 'G2107', 'G2108', 'G2109', 'G2110', 'G2111', 'G2112', 'G2114', 'G2160', 'G2170']

    datasets = {}

    for class_name in class_names:
        # Filtering the initial dataset for each class
        datasets[class_name] = data[data['Код класса МТР'].str.contains(class_name)]
        
    return datasets


def time_borders(df):
    '''
    This function groups rows of the input DataFrame based on matching request and delivery months across all rows in each group.
    
    Input: df - DataFrame with columns 'Дата заказа' (request date) and 'Срок поставки' (delivery date)
    
    Output: res - A list of DataFrames, where each element contains requests grouped by the same request month and delivery month
    '''
    res = []
    df['Даты: заявка, поставка'] = 0
    
    # Create a new column for the request month and delivery month pair
    for ind in df.index:
        date_request = datetime.datetime.strptime(df['Дата заказа'][ind], '%Y-%m-%d').date()
        date_cargo = datetime.datetime.strptime(df['Срок поставки'][ind], '%Y-%m-%d').date()
        
        # Store only the (request month, delivery month) pair
        df.loc[ind, 'Даты: заявка, поставка'] = f"{date_request.month} {date_cargo.month}"
    
    # Get unique month pairs (request month, delivery month)
    months_request_cargo = df['Даты: заявка, поставка'].unique()
    
    # Group by unique pairs and drop helper column
    for elem in months_request_cargo:
        group_df = df[df['Даты: заявка, поставка'] == elem].drop(columns=['Даты: заявка, поставка'])
        res.append(group_df)
    
    return res


def dist_cluster(data, cords_path, clients_path):
    coords_df = pd.read_csv(cords_path)
    cl = pd.read_csv(clients_path)
    
    data = data.reset_index(drop=True)
    
    for i in range(len(data)):
        cl_city = 'no_city'
        try:
            buyer_value = int(round(data.loc[i, 'Грузополучатель']))
            cl_city = cl.loc[cl['buyer'] == buyer_value, 'city'].values[0]
        except Exception as e:
            # print('\033[91mТакого кредитора/покупателя нет в базе')
            cl_city = 'no_city'
        
        try:
            data.loc[i, 'lat'], data.loc[i, 'lon'] = coords_df.loc[coords_df['city'] == cl_city, ['lat', 'lon']].values[0]
        except IndexError:
            data.loc[i, 'lat'], data.loc[i, 'lon'] = (np.nan, np.nan)
    
    data['lat'] = pd.to_numeric(data['lat'], errors='coerce')
    data['lon'] = pd.to_numeric(data['lon'], errors='coerce')
    
    kms_per_radian = 6371.0088
    epsilon = 25 / kms_per_radian
    
    # Identify rows where 'lat' or 'lon' are NaN or zero
    error_condition = data['lat'].isna() | data['lon'].isna() | (data['lat'] == 0) | (data['lon'] == 0)
    data_error = data[error_condition].copy()
    data_error_index = data_error.index
    data_fixed = data.drop(index=data_error_index).copy()
    
    coords = data_fixed[['lat', 'lon']].values
    if len(coords) > 0:
        db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
        cluster_labels = db.labels_
        data_fixed['dist'] = cluster_labels
    else:
        cluster_labels = np.array([])
        data_fixed['dist'] = np.nan
    
    # Return consistent outputs
    return data_fixed, cluster_labels, data_error, data_error_index


def sell_cluster(data_orig, data_prepr, k, metrics=False):
    label_encoder = LabelEncoder()
    data_prepr['Код класса МТР'] = label_encoder.fit_transform(data_prepr['Код класса МТР'])
    data_prepr['Кредитор'] = label_encoder.fit_transform(data_prepr['Кредитор'])
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_prepr)

    data = data_orig.copy()
    kmeans = KMeans(n_clusters=k, random_state=42)
    data['cluster'] = kmeans.fit_predict(data_scaled)
    
    if metrics:
        data['Код класса МТР'] = data['Код класса МТР'].astype(str)
        data['pairs_per_clust'] = data.groupby('cluster')['Код класса МТР'].transform('nunique')
        data['pairs_by_cred'] = data.groupby(['Поставщик', 'cluster'])['Код класса МТР'].transform('nunique')
        data['perc_cov'] = (data['pairs_by_cred'] / data['pairs_per_clust']) * 100

        def categorize_coverage(percentage):
            if 80 > percentage >= 50:
                return '≥ 50%'
            elif 100 > percentage >= 80:
                return '≥ 80%'
            elif percentage == 100:
                return '100%'
            else:
                return None  # Return None for percentages below 50%

        data['cov_cat'] = data['perc_cov'].apply(categorize_coverage)

        # Remove rows where 'cov_cat' is None to focus on defined categories
        data_filtered = data.dropna(subset=['cov_cat'])

        # Group and calculate the average number of creditors per category
        creditor_counts_by_category = (
            data_filtered.groupby(['cluster', 'cov_cat'])['Поставщик']
            .nunique()
            .reset_index(name='num_creditors')
        )

        avg_creditors_per_category = (
            creditor_counts_by_category.groupby('cov_cat')['num_creditors']
            .mean()
            .reset_index()
        )

        # Helper function to get the mean or return 0 if category is missing
        def get_avg_creditors(df, category_list):
            selection = df[df['cov_cat'].isin(category_list)]
            if not selection.empty:
                return selection['num_creditors'].mean()
            else:
                return 0

        # Calculate average creditors for each category
        average_creditors_le_50 = get_avg_creditors(
            avg_creditors_per_category, ['≥ 50%', '≥ 80%', '100%']
        )
        average_creditors_50_to_80 = get_avg_creditors(
            avg_creditors_per_category, ['≥ 80%', '100%']
        )
        average_creditors_ge_80 = get_avg_creditors(
            avg_creditors_per_category, ['100%']
        )

        # Calculate average creditors per lot, handle division by zero
        average_creditors_per_lot = data.groupby('cluster')['Поставщик'].nunique().mean()
        if average_creditors_per_lot == 0 or pd.isna(average_creditors_per_lot):
            average_creditors_per_lot = 1  # Prevent division by zero

        num_lots = data['cluster'].nunique()
        average_price_per_lot = data.groupby('cluster')['План.цена с НДС'].sum().mean()
        if average_price_per_lot == 0 or pd.isna(average_price_per_lot):
            average_price_per_lot = 1  # Prevent division by zero

        # Calculations as done manually
        manual_avg_price = data.groupby('ID лота')['План.цена с НДС'].sum().mean()
        manual_lot_count = data['ID лота'].nunique()
        if manual_avg_price == 0 or pd.isna(manual_avg_price):
            manual_avg_price = 1  # Prevent division by zero
        if manual_lot_count == 0 or pd.isna(manual_lot_count):
            manual_lot_count = 1  # Prevent division by zero

        data = data.drop(
            columns=['pairs_per_clust', 'pairs_by_cred', 'perc_cov', 'cov_cat']
        )
        
        # Calculate MQ, handle potential division by zero
        MQ = 0.5 * (
            (1 - num_lots / manual_lot_count)
            + (1 - manual_avg_price / average_price_per_lot)
        )

        # Calculate MS, handle division by zero
        MS = (
            2 * average_creditors_le_50
            + 3 * average_creditors_50_to_80
            + 4 * average_creditors_ge_80
        ) / average_creditors_per_lot

        metr = {'MQ': MQ, 'MS': MS}

        return data, metr
    else:
        return data


def optim_clust(data_orig, data_prepr, metrics=False):
    k_best = None
    MS_best = float('-inf')
    MQ_best = float('-inf')
    data_best = None

    max_k = max(2, data_prepr['Код класса МТР'].nunique() * 2)
    
    if metrics:
        for k in range(1, max_k):
            try:
                data_clustered, metr = sell_cluster(data_orig, data_prepr, k, metrics=metrics)
                # print(f"k={k}, MQ={metr['MQ']}, MS={metr['MS']}")
                
                if metr['MS'] > MS_best:
                    k_best = k
                    MS_best = metr['MS']
                    MQ_best = metr['MQ']
                    data_best = data_clustered.copy()

                if metr['MQ'] < 0.5:
                    print(f"Optimal clustering found with k={k_best}, MQ={MQ_best}, MS={MS_best}")
                    break  # Exit the loop when criteria are satisfied

            except Exception as e:
                print(f"Error clustering with k={k}: {e}")
                continue
    else:
        k_best = max_k
        data_best = sell_cluster(data_orig, data_prepr, k_best, metrics=metrics)

    if data_best is None:
        data_best = data_orig.copy()
        data_best['cluster'] = 0
        print("No suitable clustering found; assigning all data to one cluster.")

    return data_best


def preproc_delivery_time(
    df_in: 'pd.DataFrame',
    df_mtr: 'pd.DataFrame',
    df_delivery: 'pd.DataFrame',
    df_cargo: 'pd.DataFrame')-> 'pd.DataFrame':
  """
  Функция обрабатывает входной датафрейм и добавляет три столбца:
  'Код класса МТР' - соответствующий материалу;
  'Доставка: да/нет' - укладывается ли нормативный срок поставки в ожидаемый;
  'Ошибка' - код ошибки или 0 если ошибки нет
  Коды ошибки:
  0 = Ошибок не обнаружено
  1 = Нормативный срок поставки превышает требуемый
  2 = Необходимо указать подкласс товара
  3 = Указанный материал не найден в справочных данных
  4 = Указанный грузополучатель не найден в справочных данных

  Parameters:
  df_in (pd.DataFrame): DataFrame из входного файла.
  df_mtr (pd.DataFrame): DataFrame из 'Кабель справочник МТР.xlsx'.
  df_delivery (pd.DataFrame): DataFrame из 'КТ-516 Разделительная ведомость
  на поставку МТР с учетом нормативных сроков поставки.xlsx'
  df_cargo (pd.DataFrame): DataFrame из 'Справочник грузополучателей.xlsx'

  Returns:
  pd.DataFrame: preprocessed input file.
  """
  res = df_in.copy()
  res = res.drop(columns='Unnamed: 0')
  res['Код класса МТР'] = ''
  res['Доставка: да/нет'] = ''
  res['Ошибка'] = 0
  res['Описание ошибки'] = 'Ошибок не обнаружено'
  for ind in res.index:
    material = res['Материал'][ind]
    if material not in df_mtr['Материал'].unique():
      res.loc[ind, 'Ошибка'] = 3
      res.loc[ind, 'Описание ошибки'] = 'Указанный материал не найден в справочных данных'
    elif int(res['Грузополучатель'][ind]) not in df_cargo['Код грузополучателя'].unique().astype(int):
      res.loc[ind, 'Ошибка'] = 4
      res.loc[ind, 'Описание ошибки'] = 'Указанный грузополучатель не найден в справочных данных'
    else:
      code = df_mtr[df_mtr['Материал'] == material]['Класс'].values[0]
      res.loc[ind, 'Код класса МТР'] = code
      date_request = datetime.datetime.strptime(res['Дата заказа'][ind],
                                              '%Y-%m-%d').date()
      date_delivery_want = datetime.datetime.strptime(res['Срок поставки'][ind],
                                                    '%Y-%m-%d').date()
      delivery_time = df_delivery[df_delivery['Класс в ЕСМ'] == code][
          'Нормативный срок поставки МТР, отсчитываемый с даты инициирования процедуры закупки  (календарные дни)**'].values[0]
      if delivery_time == 'Необходимо использовать подкласс':
        res.loc[ind, 'Ошибка'] = 2
        res.loc[ind, 'Описание ошибки'] = 'Необходимо указать подкласс товара'
      else:
        date_delivery_real = date_request + datetime.timedelta(days=int(delivery_time))
        if date_delivery_real <= date_delivery_want:
          res.loc[ind, 'Доставка: да/нет'] = 'Да'
        else:
          res.loc[ind, 'Доставка: да/нет'] = 'Нет'
          res.loc[ind, 'Ошибка'] = 1
          res.loc[ind, 'Описание ошибки'] = 'Нормативный срок поставки превышает требуемый'
  return res

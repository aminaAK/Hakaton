import pandas as pd
import datetime

#df_in = pd.read_excel('Test_input_file.xlsx')
#df_mtr = pd.read_excel('Кабель справочник МТР.xlsx')
#df_deliv = pd.read_excel('КТ-516 Разделительная ведомость на поставку МТР с учетом нормативных сроков поставки.xlsx', header=23)
#df_cargo = pd.read_excel('Справочник грузополучателей.xlsx')

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

#df_in_preprocessed = preproc_delivery_time(df_in, df_mtr, df_deliv, df_cargo)

#print(df_in_preprocessed[df_in_preprocessed['Ошибка'] > 0])

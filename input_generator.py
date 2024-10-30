from random import sample
import pandas as pd
import datetime

def generate_input(df: 'pd.DataFrame', size: 'int', add_errors: 'bool'=False)-> 'pd.DataFrame':
  '''
  Функция создаёт входной файл требуемого размера из рандомных строк исторического файла

  Input:
  df: 'pd.DataFrame' - датафрейм из "processed_Исторические совершенные закупки товаров.csv"
  size: 'int' - размер выходного датафрейма (input файла)
  add_errors: 'bool'=False - если True, добавляет некорректного грузополучателя в 1ю строку
    и некорректный материал в последнюю строку (ошибки кода 3 и 4)

  Output:
  res: 'pd.DataFrame' - выходной датафрейм (input файл)
  '''
  my_columns = ['Клиент', 'Материал', 'Краткий текст материала', 'ЕИ',
             'Общее количество', 'Месяц поставки', 'Год поставки',
             'Полугодие', 'Срок поставки', 'Грузополучатель', 'Цена',
             'Способ закупки', '№ заказа', '№ позиции', 'Дата заказа']
  my_column_dict = {'Клиент' : 'Клиент', 'Материал' : 'Материал',
                 'Краткий текст материала' : 'Материал Имя',
                 'ЕИ' : 'Базисная ЕИ',
                 'Общее количество' : 'Кол-во к закупу, БЕИ',
                 'Месяц поставки' : 'Срок поставки',
                 'Год поставки' : 'Срок поставки',
                 'Полугодие' : 'Срок поставки',
                 'Срок поставки' : 'Срок поставки',
                 'Грузополучатель' : 'Грузополучатель',
                 'Цена' : 'Пл.цена с НДС за АЕИ',
                 'Способ закупки' : 'ГПЗ Способ закупки',
                 '№ заказа' : 'Заявка на закупку', '№ позиции' : 'Позиц.',
                 'Дата заказа' : 'Дата заявки'}
  res = pd.DataFrame(columns=my_columns)
  ind = sample(df.index.to_list(), size)
  for i in ind:
    for col in my_columns:
      res.loc[i, col] = df[my_column_dict[col]][i]
    date = datetime.datetime.strptime(res['Срок поставки'][i],
                                                  '%Y-%m-%d').date()
    res.loc[i, 'Месяц поставки'] = date.month
    res.loc[i, 'Год поставки'] = date.year
    if date.month <= 6:
      res.loc[i, 'Полугодие'] = 1
    else:
      res.loc[i, 'Полугодие'] = 2
  if add_errors:
    res.loc[res.index[0], 'Грузополучатель'] = 94039455855858    #just random number
    res.loc[res.index[-1], 'Материал'] = 94039455855858          #just random number
  return res

#df_history = pd.read_csv('/content/processed_Исторические совершенные закупки товаров.csv')

#df_new = generate_input(df_history, 42)
#df_new.to_excel('input_without_errors34.xlsx', index=False)
#df_new = generate_input(df_history, 158, True)
#df_new.to_excel('input_with_errors34.xlsx', index=False)
import pandas as pd
import datetime

def time_borders(df):
  '''
  Функция разбивает строки входного датафрейма по сопадению пар (месяц заявки, месяц поставки)

  Input: df - датафрейм вида входного файла

  Output: res - список из датафреймов, каждый элемент списка содержит заявки,
  сгруппированные по совпадению пар (месяц заявки, месяц поставки)
  '''
  res = []
  df['Даты: заявка, поставка'] = 0
  for ind in df.index:
    date_request = datetime.datetime.strptime(df['Дата заказа'][ind],
                                                  '%Y-%m-%d').date()
    date_cargo = datetime.datetime.strptime(df['Срок поставки'][ind],
                                                  '%Y-%m-%d').date()
    df.loc[ind, 'Даты: заявка, поставка'] = str(date_request.year) + '-' + \
    str(date_request.month) + ' ' + str(date_cargo.year) + '-' + \
    str(date_cargo.month)
  months_request_cargo = df['Даты: заявка, поставка'].unique()
  for elem in months_request_cargo:
    res.append(df[df['Даты: заявка, поставка'] == elem].drop(columns=['Даты: заявка, поставка']))
  return res

#df = pd.read_excel('/content/input_with_errors34 (3).xlsx')
#df1 = time_borders(df)
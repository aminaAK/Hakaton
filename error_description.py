import pandas as pd

#df_input_preprocessed = pd.read_excel('Preprocessed_input_all_errors.xlsx')

def error_description(df: 'pd.DataFrame')-> list:
  """
  Функция обрабатывает входной датафрейм и возвращает список пар:
  [(индекс строки с ошибкой (int), описание ошибки (str)), ...]

  Parameters:
  df (pd.DataFrame): DataFrame из preprocessed входного файла

  Returns: list of pairs
  """
  res = []
  for ind in df.index:
    if df['Ошибка'][ind] == 1:
      res.append((ind, 'Нормативный срок поставки превышает требуемый'))
    elif df['Ошибка'][ind] == 2:
      res.append((ind, 'Необходимо указать подкласс товара'))
    elif df['Ошибка'][ind] == 3:
      res.append((ind, 'Указанный материал не найден в справочных данных'))
    elif df['Ошибка'][ind] == 4:
      res.append((ind, 'Указанный грузополучатель не найден в справочных данных'))
  return res

#print(error_description(df_input_preprocessed))
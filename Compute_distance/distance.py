import numpy as np
import pandas as pd


coords = pd.read_csv('cwc.csv')
c = pd.read_csv('clients.csv')
s = pd.read_excel('suppliers_with_city.xlsx')

def compute(lat1, lon1, lat2, lon2, R=6371):
    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)
    lon1 = np.radians(lon1)
    lon2 = np.radians(lon2)

    a = np.sin(lat1)*np.sin(lat2) + np.cos(lat1)*np.cos(lat2)*np.cos(lon2-lon1)
    a = np.arccos(a)

    return a * R


def distance(id_cr: 'int',
             id_buy: 'int',
             coords: 'pd.DataFrame',
             cl: 'pd.DataFrame',
             su: 'pd.DataFrame'):
    
    try:
        su_city = su[su['Кредитор'] == str(id_cr)]['Город'].values[0]
        cl_city = cl[cl['buyer'] == id_buy]['city'].values[0]
    except:
        print('\033[91mТакого кредитора/покупателя нет в базе')
        return -1
        
    lat1, lon1 = coords[coords['city'] == su_city][['lat', 'lon']].values[0]
    lat2, lon2 = coords[coords['city'] == cl_city][['lat', 'lon']].values[0]

    dist = compute(lat1, lon1, lat2, lon2)

    return dist.round(2)


'''
омск ноябрьск
921.28 в км
'''
distance(27645, 20000222, coords, c, s)
import pandas as pd
import numpy as np
from .hacaton import Lot

def table():    
    data = Lot()
    req = []
    for i in range(len(data)):
        lot = data[i]
        req.append([i,lot[0].iloc[15],len(lot),lot[0].iloc[17]]) 
    
    return(pd.DataFrame(req, columns=['№', 'Дата', 'Количество лотов', 'Доставка']))

def request_lot(i):    
    data = Lot()
    return(data[i][0])
def lots_from_requaest(i):    
    data = Lot()
    return(data[i][1])
 

  
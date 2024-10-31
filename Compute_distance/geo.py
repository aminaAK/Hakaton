import pandas as pd
import folium

clients = pd.read_csv("clients_with_location.csv")
def add_tack(lat, lon, text, map, radius=20, fill_color='blue'):
    #popup - при нажатии, tooltip - при наведении
    folium.CircleMarker(
        location=(lat, lon),
        popup=text,
        tooltip=text,
        radius=radius,
        color='black',
        fill_color=fill_color
    ).add_to(map)

def buyer_coords(buyer_id):
    lat, lon = clients[clients["buyer_id"]==buyer_id][['lat', 'lon']].values[0]       
    return lat, lon

def add_locations(buyers: pd.Series, map):
    for buyer_id in buyers:
        lat, lon = buyer_coords(buyer_id)
        if (lat is None or lon is None):
            print('\033[91m', f'Местоположение грузополучателя {buyer_id} отсутствует в базе','\033[0m')
        else:            
            add_tack(lat, lon, f"Грузополучатель {buyer_id}", map, fill_color='red')

def lot_map(lot: pd.DataFrame) -> str:
    '''
    Принимает DataFrame из заявок
    Отмечает всех грузополучателей красными кругами на карте
    Возвращает html-код карты в виде строки
    '''
    buyers = lot["Грузополучатель"]
    mapa = folium.Map(location=(67., 93.), zoom_start=3, attributionControl=0)
    add_locations(buyers, mapa)
    return mapa._repr_html_()

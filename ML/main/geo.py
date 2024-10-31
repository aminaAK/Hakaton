import pandas as pd
import folium

clients = pd.read_csv("main/data/clients_with_location.csv")
def add_tack(lat, lon, text, map, radius=20, fill_color='blue'):
    #popup - при нажатии, tooltip - при наведении
    folium.CircleMarker(
        location=(lat, lon),
        popup=text,
        tooltip=text,
        radius=radius,
        color='black',
        fill_color=fill_color,
        fill_opacity=0.9
    ).add_to(map)

def buyer_coords(buyer_id):
    lat, lon = clients[clients["buyer_id"]==buyer_id][['lat', 'lon']].values[0]       
    return lat, lon

def add_locations(buyers: pd.Series, map, color='red', add_text='') -> None:
    for buyer_id in buyers:
        lat, lon = buyer_coords(buyer_id)
        if (lat is None or lon is None):
            print('\033[91m', f'Местоположение грузополучателя {buyer_id} отсутствует в базе','\033[0m')
        else:            
            add_tack(lat, lon, f"Грузополучатель {buyer_id}" + '\n' + add_text, map, fill_color=color)

def lot_map(lot: pd.DataFrame) -> str:
    '''
    Принимает DataFrame из заявок
    Отмечает всех грузополучателей красными кругами на карте
    Возвращает html-код карты в виде строки
    '''
    buyers = lot["Грузополучатель"]
    f = folium.Figure(width='100%', height= 400)
    mapa = folium.Map(location=(67., 93.), zoom_start=3, attributionControl=0).add_to(f)
    add_locations(buyers, mapa)
    return mapa._repr_html_()

def lots_map(lots: list):
    '''
    Принимает список лотов (датафреймов)
    Отмечает кругами разного цвета грузополучателей в разных лотах
    Возвращает html-код карты в виде строки
    '''
    f = folium.Figure(width='100%', height= 400)

    mapa = folium.Map(location=(67., 93.), zoom_start=3, attributionControl=0).add_to(f)
    colors=[ "#FBF8CC",
        "#FDE4CF",
        "#FFCFD2",
        "#F1C0E8",
        "#CFBAF0",
        "#A34CF3",
        "#90DBF4",
        "#8EECF5",
        "#98F5E1",
        "#B9FBC0"]
    for i, lot in enumerate(lots):
        buyers = lot["Грузополучатель"]
        color = colors[i%len(colors)]
        add_locations(buyers, mapa, color=color, add_text=f"Лот #{i}")
    return mapa._repr_html_()

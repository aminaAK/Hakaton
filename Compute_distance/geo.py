import pandas as pd
import folium

cities = pd.read_csv("cwc.csv")
buyers = pd.read_csv("clients.csv")
creditors = pd.read_excel("suppliers_with_city.xlsx")

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
    try:
        city = buyers[buyers["buyer"] == buyer_id]["city"].values[0]
    except:
        print(f'\033[91mАдрес покупателя {buyer_id} отсутствует в базе')  # \033[91m делает текст красным
        return None, None
    lat, lon = cities[cities["city"] == city.lower()][['lat', 'lon']].values[0]
    return lat, lon

def creditor_coords(creditor_id):
    try:
        city = creditors[creditors["Кредитор"] == creditor_id]["Город"].values[0]
    except:
        print(f'\033[91mАдрес кредитора {creditor_id} отсутствует в базе')  # \033[91m делает текст красным
        return None, None
    lat, lon = cities[cities["city"] == city.lower()][['lat', 'lon']].values[0]
    return lat, lon

def add_locations(buyers: pd.Series, creditors: pd.Series, map):
    for buyer_id in buyers:
        lat, lon = buyer_coords(buyer_id)
        add_tack(lat, lon, f"Грузополучатель {buyer_id}", map, fill_color='red')

    for creditor_id in creditors:
        lat, lon = creditor_coords(creditor_id)
        add_tack(lat, lon, f"Поставщик {creditor_id}", map, fill_color='blue')
        
    
mapa = folium.Map(location=(55., 37.), attributionControl=0) #Москва

add_locations(pd.Series([20000770, 8536, 20000751]), pd.Series(["11", "47"]), mapa)

mapa.show_in_browser()
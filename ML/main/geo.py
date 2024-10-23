import pandas as pd
import folium

df1 = pd.read_csv("city.csv")
df = df1[["city", "fias_level", "geo_lat", "geo_lon"]]
df = df.rename({"geo_lat":"lat", "geo_lon":"lon"}, axis=1)
df.head()

def add_tack(lat, lon, text, level, map):
    folium.Circle(
        location=(lat, lon),
        popup=text,
        tooltip=text,
        radius = 200/level
    ).add_to(map)

mapa = folium.Map(location=(55., 37.)) #Москва
for _, row in df.iterrows():
    add_tack(row["lat"], row["lon"], row["city"], row["fias_level"], mapa)

mapa.save("ML/main/template/main/map.html")
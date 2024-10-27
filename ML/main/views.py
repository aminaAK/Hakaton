from django.shortcuts import render
import pandas as pd
from .models import MyFiles, Row
import folium
from .Tables import table, request_lot, lots_from_requaest
from .hacaton import Lot


def index(request):
    datapoints = [
        { "label": "Online Store",  "y": 27  },
        { "label": "Offline Store", "y": 25  },        
        { "label": "Discounted Sale",  "y": 30  },
        { "label": "B2B Channel", "y": 8  },
        { "label": "Others",  "y": 10  }
    ]

    lots = table()


    
    if request.method == 'POST':
        row = request.POST['row'].split()
        row_id = int(row[1]) 
        tables(request, row_id)
        return tables(request, row_id)

    # --------------- map --------------
    df1 = pd.read_csv("main/city.csv")
    df = df1[["city", "fias_level", "geo_lat", "geo_lon"]]
    df = df.rename({"geo_lat":"lat", "geo_lon":"lon"}, axis=1)
    def add_tack(lat, lon, text, level, map):
        folium.Circle(
            location=(lat, lon),
            popup=text,
            tooltip=text,
            radius = 200/level
        ).add_to(map)
    f = folium.Figure(width='100%', height= 400)
    mapa = folium.Map(location=(55., 37.)).add_to(f) #Москва
    for _, row in df.iterrows():
        add_tack(row["lat"], row["lon"], row["city"], row["fias_level"], mapa)
    mapa = mapa._repr_html_()
    # --------------- map --------------


    context={'map': mapa, 'df': lots, "datapoints" : datapoints}
    return render(request, 'main/index.html', context)


def download(request):
    if request.POST:
        print(request.FILES.get('file'))
    MyFiles.objects.create(
        file = request.FILES.get('file')
    )
    return render(request, 'main/download.html')

def tables(request, id):
    req = request_lot(id)
    lots = lots_from_requaest(id)
    return render(request, 'main/tables.html', {'data':req, 'id':id, 'lots':lots})

    





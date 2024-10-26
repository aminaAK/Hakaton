from django.shortcuts import render
import pandas as pd
from .models import MyFiles
import folium
from .test import result


def index(request):
    datapoints = [
        { "label": "Online Store",  "y": 27  },
        { "label": "Offline Store", "y": 25  },        
        { "label": "Discounted Sale",  "y": 30  },
        { "label": "B2B Channel", "y": 8  },
        { "label": "Others",  "y": 10  }
    ]
    data = {
        "calories": [420, 380, 390,400,5000,600,400,200,420, 380, 390,400,5000,600,400,200],
        "duration": [50, 40, 45,12,12,12,12,12,50, 40, 45,12,12,12,12,12],
        "name": ['Amina', 'Alex', 'Anton', 'Amina', 'Alex', 'Anton','Alex', 'Alex','Amina', 'Alex', 'Anton', 'Amina', 'Alex', 'Anton','Alex', 'Alex'],
        "skills": ['web', 'ml', 'python','web', 'ml', 'python','web', 'ml','web', 'ml', 'python','web', 'ml', 'python','web', 'ml'],
        "hollydays": [15, 24, 35, 15, 24, 35, 15, 24,15, 24, 35, 15, 24, 35, 15, 24],

    }
    df_gb = pd.DataFrame(data)
    test = result(data).get_data()
   

    # context = {'df': df_gb}
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
    context={'map': mapa, 'df': df_gb, "datapoints" : datapoints, 'test': test}
    return render(request, 'main/index.html', context)

def download(request):
    if request.POST:
        print(request.FILES.get('file'))
    MyFiles.objects.create(
        file = request.FILES.get('file')
    )
    return render(request, 'main/download.html')

    





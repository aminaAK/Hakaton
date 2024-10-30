from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
import pandas as pd
from .models import MyFiles
import folium
# from .Tables import  request_lot, lots_from_requaest
from .hacaton import Lot
import os
import datetime #added by rita!



name = ''

def index(request):
    
    data = Lot(name)
    req = []
    for i in range(len(data)):
        lot = data[i]
        req.append([i,lot[0].iloc[15],lot[0].iloc[12],lot[0].iloc[17]]) 
    
    lots = pd.DataFrame(req, columns=['№', 'Дата','Способ закупки', 'Доставка'])


    
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

    #------------------- input file plots ---------------------------
    data_input = pd.read_excel('main/Test_input_file.xlsx')   ####change!!!
    data_input['Год заявки'] = 0
    data_input['Год заявки'] = 0
    for i in data_input.index:
        date = datetime.datetime.strptime(data_input['Дата заказа'][i],
                                                  '%Y-%m-%d').date()
        data_input.loc[i, 'Месяц заявки'] = date.month
        data_input.loc[i, 'Год заявки'] = date.year

    #для кругового графика кол-ва поставок по годам
    years = data_input['Год поставки'].unique()
    data_1 = [{"label": f"{year}", "y": int(data_input[data_input['Год поставки'] == year]['№ заказа'].count())} for year in years]

    #для столбчатого графика кол-ва заявок по месяцам (срок поставки)
    months = [i for i in range(1, 13)]
    labels_2 = []
    counts_2 = []
    for year in years:
        for month in months:
            labels_2.append(f"{month}/{year}")
            counts_2.append(data_input[(data_input['Год поставки'] == year) & (data_input['Месяц поставки'] == month)]['№ заказа'].count())
    data_2 = [{"label": f"{labels_2[i]}", "y": int(counts_2[i])} for i in range(len(labels_2))]

    #для кругового графика кол-ва заявок по годам
    years = data_input['Год заявки'].unique()
    data_3 = [{"label": f"{year}", "y": int(data_input[data_input['Год заявки'] == year]['№ заказа'].count())} for year in years]

    #для столбчатого графика кол-ва заявок по месяцам (срок заявки)
    months = [i for i in range(1, 13)]
    labels_2 = []
    counts_2 = []
    for year in years:
        for month in months:
            labels_2.append(f"{month}/{year}")
            counts_2.append(data_input[(data_input['Год заявки'] == year) & (data_input['Месяц заявки'] == month)]['№ заказа'].count())
    data_4 = [{"label": f"{labels_2[i]}", "y": int(counts_2[i])} for i in range(len(labels_2))]

    #для графика по классам товаров
    df_mtr = pd.read_excel('main/Кабель справочник МТР.xlsx')
    data_input['Название класса МТР'] = ''
    for ind in data_input.index:
        material = data_input['Материал'][ind]
        code = df_mtr[df_mtr['Материал'] == material]['Название'].values[0]
    data_input.loc[ind, 'Название класса МТР'] = code
    class_code = data_input['Название класса МТР'].unique()
    class_count = []
    for cl_c in class_code:
        class_count.append(data_input[(data_input['Название класса МТР'] == cl_c)]['№ заказа'].count())
    class_code_sorted = [x for _, x in sorted(zip(class_count, class_code))]
    class_count_sorted =sorted(class_count)
    if len(class_code) > 10:
        other_count = sum(class_count_sorted[:-10])
        data_5 = [{"label": class_code_sorted[i], "y": int(class_count_sorted[i])} for i in range(-10, 0)]
        data_5.append({"label": "Другие", "y": int(other_count)})
    else:
        data_5 = [{"label": class_code_sorted[i], "y": int(class_count_sorted[i])} for i in range(len(class_code_sorted))]
    
    #для графика по клиентам
    cargo_code = data_input['Клиент'].unique()
    cargo_count = []
    for cl_c in cargo_code:
        cargo_count.append(data_input[(data_input['Клиент'] == cl_c)]['№ заказа'].count())
    cargo_code_sorted = [x for _, x in sorted(zip(cargo_count, cargo_code))]
    cargo_count_sorted =sorted(cargo_count)
    if len(cargo_code) > 10:
        other_count = sum(cargo_count_sorted[:-10])
        data_6 = [{"label": f"Клиент {str(cargo_code_sorted[i])}", "y": int(cargo_count_sorted[i])} for i in range(-10, 0)]
        data_6.append({"label": "Другие", "y": int(other_count)})
    else:
        data_6 = [{"label": str(cargo_code_sorted[i]), "y": int(cargo_count_sorted[i])} for i in range(len(cargo_code_sorted))]
    #------------------- input file plots ---------------------------



    context={'map': mapa, 'df': lots, "data1": data_1, "data2": data_2, "data3": data_3, "data4": data_4, "data5": data_5, "data6": data_6}
    return render(request, 'main/index.html', context)


def download(request):
    global name 

    if request.method == 'POST' and 'run_script' in request.POST:
        MyFiles.objects.create(
            file = request.FILES.get('file')
        )
        f = MyFiles.objects.create(
            file = request.FILES.get('file')
        )
        name = f.file.name

    if name != "":
        print('пошел процесс', name)
        #------------------- input file plots ---------------------------
        data_input = pd.read_excel('./media/'+name)   ####changed
        data_input['Год заявки'] = 0
        data_input['Год заявки'] = 0
        for i in data_input.index:
            date = datetime.datetime.strptime(data_input['Дата заказа'][i],
                                                    '%Y-%m-%d').date()
            data_input.loc[i, 'Месяц заявки'] = date.month
            data_input.loc[i, 'Год заявки'] = date.year

        #для кругового графика кол-ва поставок по годам
        years = data_input['Год поставки'].unique()
        data_1 = [{"label": f"{year}", "y": int(data_input[data_input['Год поставки'] == year]['№ заказа'].count())} for year in years]

        #для столбчатого графика кол-ва заявок по месяцам (срок поставки)
        months = [i for i in range(1, 13)]
        labels_2 = []
        counts_2 = []
        for year in years:
            for month in months:
                labels_2.append(f"{month}/{year}")
                counts_2.append(data_input[(data_input['Год поставки'] == year) & (data_input['Месяц поставки'] == month)]['№ заказа'].count())
        data_2 = [{"label": f"{labels_2[i]}", "y": int(counts_2[i])} for i in range(len(labels_2))]

        #для кругового графика кол-ва заявок по годам
        years = data_input['Год заявки'].unique()
        data_3 = [{"label": f"{year}", "y": int(data_input[data_input['Год заявки'] == year]['№ заказа'].count())} for year in years]

        #для столбчатого графика кол-ва заявок по месяцам (срок заявки)
        months = [i for i in range(1, 13)]
        labels_2 = []
        counts_2 = []
        for year in years:
            for month in months:
                labels_2.append(f"{month}/{year}")
                counts_2.append(data_input[(data_input['Год заявки'] == year) & (data_input['Месяц заявки'] == month)]['№ заказа'].count())
        data_4 = [{"label": f"{labels_2[i]}", "y": int(counts_2[i])} for i in range(len(labels_2))]

        #для графика по классам товаров
        df_mtr = pd.read_excel('main/Кабель справочник МТР.xlsx')
        data_input['Название класса МТР'] = ''
        for ind in data_input.index:
            material = data_input['Материал'][ind]
            code = df_mtr[df_mtr['Материал'] == material]['Название'].values[0]
        data_input.loc[ind, 'Название класса МТР'] = code
        class_code = data_input['Название класса МТР'].unique()
        class_count = []
        for cl_c in class_code:
            class_count.append(data_input[(data_input['Название класса МТР'] == cl_c)]['№ заказа'].count())
        class_code_sorted = [x for _, x in sorted(zip(class_count, class_code))]
        class_count_sorted =sorted(class_count)
        if len(class_code) > 10:
            other_count = sum(class_count_sorted[:-10])
            data_5 = [{"label": class_code_sorted[i], "y": int(class_count_sorted[i])} for i in range(-10, 0)]
            data_5.append({"label": "Другие", "y": int(other_count)})
        else:
            data_5 = [{"label": class_code_sorted[i], "y": int(class_count_sorted[i])} for i in range(len(class_code_sorted))]
        
        #для графика по клиентам
        cargo_code = data_input['Клиент'].unique()
        cargo_count = []
        for cl_c in cargo_code:
            cargo_count.append(data_input[(data_input['Клиент'] == cl_c)]['№ заказа'].count())
        cargo_code_sorted = [x for _, x in sorted(zip(cargo_count, cargo_code))]
        cargo_count_sorted =sorted(cargo_count)
        if len(cargo_code) > 10:
            other_count = sum(cargo_count_sorted[:-10])
            data_6 = [{"label": f"Клиент {str(cargo_code_sorted[i])}", "y": int(cargo_count_sorted[i])} for i in range(-10, 0)]
            data_6.append({"label": "Другие", "y": int(other_count)})
        else:
            data_6 = [{"label": str(cargo_code_sorted[i]), "y": int(cargo_count_sorted[i])} for i in range(len(cargo_code_sorted))]
        
        #------------------- input file plots ---------------------------

    if request.method == 'POST' and 'run_script_download' in request.POST:
        return download_file(request, './media/'+name)
    
        
    if name =="":
     context={"name": name}
    else:

     context={"name": name, "data1": data_1, "data2": data_2, "data3": data_3, "data4": data_4, "data5": data_5, "data6": data_6}

    return render(request, 'main/download.html', context)

# def remove_file(name):
#     os.remove('./media' + name)

def tables(request, id):
    data = Lot(name)
    req = data[id][0]
    lots = data[id][1]
    return render(request, 'main/tables.html', {'data':req, 'id':id, 'lots':lots})


def download_file(request, name):
    file_path = name
    if os.path.exists(name):
        with open(name, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/xlsx")
            response['Content-Disposition'] = 'inline; filename=' + name
            return response
    raise Http404
    





from django.shortcuts import render
import pandas as pd
from .models import MyFiles

def index(request):
    data = {
        "calories": [420, 380, 390],
        "duration": [50, 40, 45],
        "name": ['Amina', 'Alex', 'Anton'],
        "skills": ['web', 'ml', 'python']

    }
    df_gb = pd.DataFrame(data)

    context = {'df': df_gb}

    return render(request, 'main/index.html', context)

def download(request):
    if request.POST:
        print(request.FILES.get('file'))
    MyFiles.objects.create(
        file = request.FILES.get('file')
    )
    return render(request, 'main/download.html')


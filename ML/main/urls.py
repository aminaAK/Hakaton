from . import views
from django.urls import path


urlpatterns = [

    path('index/', views.index, name="index"),
    path('', views.download, name="download"),
    path('tables/', views.tables, name="tables"),
    
    

]
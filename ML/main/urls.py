from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('download/', views.download, name="download"),
    path('tables/', views.tables, name="tables"),
    

]
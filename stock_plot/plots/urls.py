from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='index'),
    path('intraday', views.intraDay, name="intraday")
]
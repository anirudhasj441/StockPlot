from django.urls import path
from . import views

urlpatterns = [
    path('timeseries',views.timeseries,name='timeseries'),
    # APIs
    path('intraday', views.intraDay, name="intraday"),
    path('search', views.searchSymbols, name="search")
]
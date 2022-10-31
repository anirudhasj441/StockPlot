from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock),
    #APIs
    path('search', views.searchStock),
    path('news', views.getNews)
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock),
    path('news_content/<str:id>', views.newsContent),
    #APIs
    path('search', views.searchStock),
    path('news', views.getNews)
]
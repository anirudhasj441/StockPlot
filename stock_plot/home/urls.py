from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    #APIs
    path('signin', views.userLogin),
    path('signup', views.userSignUp),
    path('logout', views.userLogout),
    path('add_watchlist', views.addToWatchlist)
]
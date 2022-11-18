from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    #APIs
    path('signin', views.userLogin),
    path('signup', views.userSignUp),
    path('logout', views.userLogout),
    path('add_watchlist', views.addToWatchlist),
    path('remove_watchlist', views.removeFromWatchlist),
    path('check_watchlist', views.checkStockInWatchlist),
    path('get_wathlist', views.getWatchlist),
]
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('signin', views.userLogin),
    path('signup', views.userSignUp),
    path('logout', views.userLogout),
]
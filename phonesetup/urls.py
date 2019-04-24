from django.urls import path
from . import views

urlpatterns = [
    path('buttons/', views.buttonUpdate, name='Phone-Setup'),
    path('files/', views.listFiles, name='Phone-Setup'),
    path('', views.listFiles, name='Phone-Setup'),
]

# scraper/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('buscar/', views.buscar_wikipedia, name='buscar_wikipedia'),
    path('enviar-resultados/', views.enviar_resultados_email, name='enviar_resultados_email'),
]
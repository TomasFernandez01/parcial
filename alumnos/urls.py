# alumnos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('eliminar/<int:alumno_id>/', views.eliminar_alumno, name='eliminar_alumno'),
    path('pdf/<int:alumno_id>/', views.descargar_pdf, name='descargar_pdf'),
    path('enviar-email/<int:alumno_id>/', views.enviar_pdf_email, name='enviar_pdf_email'),
]
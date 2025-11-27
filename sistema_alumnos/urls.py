from django.contrib import admin
from django.urls import path, include
from usuarios.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('usuarios/', include('usuarios.urls')),
    path('', include('alumnos.urls')),
    path('scraper/', include('scraper.urls')),
]
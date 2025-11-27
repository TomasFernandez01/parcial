# scraper/views.py
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def buscar_wikipedia(request):
    resultados = []
    termino = ""
    
    if request.method == 'POST':
        termino = request.POST.get('termino', '').strip()
        
        if termino:
            try:
                # USAR API DE BÚSQUEDA DE WIKIPEDIA (más resultados)
                url_api = "https://es.wikipedia.org/w/api.php"
                params = {
                    'action': 'query',
                    'list': 'search',
                    'srsearch': termino,
                    'format': 'json',
                    'utf8': 1,
                    'srlimit': 10,  # ↑ AUMENTAMOS A 10 RESULTADOS ↑
                    'srprop': 'snippet'  # Incluir fragmentos
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url_api, params=params, headers=headers, timeout=10)
                data = response.json()
                
                if 'query' in data and data['query']['search']:
                    for item in data['query']['search']:
                        titulo = item['title']
                        
                        # Obtener URL completa del artículo
                        url_articulo = f"https://es.wikipedia.org/wiki/{titulo.replace(' ', '_')}"
                        
                        # Obtener resumen más completo
                        try:
                            url_resumen = f"https://es.wikipedia.org/api/rest_v1/page/summary/{titulo.replace(' ', '_')}"
                            response_resumen = requests.get(url_resumen, headers=headers, timeout=5)
                            if response_resumen.status_code == 200:
                                articulo_data = response_resumen.json()
                                resumen = articulo_data.get('extract', 'No hay resumen disponible')
                            else:
                                resumen = item.get('snippet', 'Haz clic para ver el artículo completo') + '...'
                        except:
                            resumen = item.get('snippet', 'Haz clic para ver el artículo completo') + '...'
                        
                        resultados.append({
                            'titulo': titulo,
                            'resumen': resumen,
                            'url': url_articulo
                        })
                    
                    messages.success(request, f'✅ Se encontraron {len(resultados)} resultados para "{termino}"')
                    
                else:
                    messages.warning(request, f'❌ No se encontraron resultados para "{termino}"')
                    
            except Exception as e:
                messages.error(request, f'❌ Error en la búsqueda: {str(e)}')
    
    context = {
        'resultados': resultados,
        'termino': termino
    }
    return render(request, 'scraper/buscar.html', context)

# @login_required
# def buscar_wikipedia(request):
#     resultados = []
#     termino = ""
    
#     if request.method == 'POST':
#         termino = request.POST.get('termino', '').strip()    
#         if termino:
#             try:
#                 # URL de búsqueda de Wikipedia
#                 url = f"https://es.wikipedia.org/wiki/{termino.replace(' ', '_')}"
#                 headers = {
#                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#                 }
#                 response = requests.get(url, headers=headers, timeout=10)
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
#                     # Extraer título
#                     titulo = soup.find('h1')
#                     titulo_texto = titulo.text if titulo else termino
#                     # Extraer párrafos relevantes
#                     parrafos = soup.find_all('p')
#                     resumen = ""
#                     for p in parrafos:
#                         texto = p.get_text().strip()
#                         if len(texto) > 50:  # Solo párrafos con contenido
#                             resumen = texto[:300] + "..." if len(texto) > 300 else texto
#                             break
#                     if not resumen:
#                         resumen = "No se pudo extraer resumen del artículo."
#                     resultados.append({
#                         'titulo': titulo_texto,
#                         'resumen': resumen,
#                         'url': url
#                     })
#                     messages.success(request, f'Artículo encontrado: {titulo_texto}')
                    
#                 else:
#                     # Si no encuentra el artículo directo, buscar en página de desambiguación
#                     url_busqueda = f"https://es.wikipedia.org/w/index.php?search={termino.replace(' ', '+')}"
#                     response_busqueda = requests.get(url_busqueda, headers=headers, timeout=10)
#                     if response_busqueda.status_code == 200:
#                         soup_busqueda = BeautifulSoup(response_busqueda.content, 'html.parser')
#                         # Buscar primeros resultados
#                         resultados_div = soup_busqueda.find('ul', class_='mw-search-results') or soup_busqueda.find('div', class_='searchresults')
                        
#                         if resultados_div:
#                             items = resultados_div.find_all('li', limit=3)
#                             for item in items:
#                                 titulo_elem = item.find('a')
#                                 if titulo_elem:
#                                     titulo_texto = titulo_elem.get('title', '')
#                                     if titulo_texto:
#                                         resultados.append({
#                                             'titulo': titulo_texto,
#                                             'resumen': 'Haz clic en "Ver en Wikipedia" para ver el artículo completo',
#                                             'url': "https://es.wikipedia.org" + titulo_elem.get('href', '')
#                                         })
                        
#                         if resultados:
#                             messages.success(request, f'Se encontraron {len(resultados)} resultados para "{termino}"')
#                         else:
#                             messages.warning(request, f'No se encontró el artículo específico para "{termino}". Intenta con términos más específicos.')
#                     else:
#                         messages.error(request, 'Error al conectarse con Wikipedia')
#             except Exception as e:
#                 messages.error(request, f'Error en la búsqueda: {str(e)}')
#     context = {
#         'resultados': resultados,
#         'termino': termino
#     }
#     return render(request, 'scraper/buscar.html', context)

@login_required
def enviar_resultados_email(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '')
        url = request.POST.get('url', '')
        
        try:
            email = EmailMessage(
                subject=f'Artículo de Wikipedia: {titulo}',
                body=f'''
                Hola {request.user.username}, Te enviamos el artículo que solicitaste:
                📖 {titulo} : 🔗 {url}
                Puedes ver el artículo completo haciendo clic en el link anterior.
                Saludos, Sistema de Búsqueda Wikipedia.
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[request.user.email],
            )
            email.send()
            messages.success(request, f'Artículo "{titulo}" enviado a tu email!')
            
        except Exception as e:
            messages.error(request, f'Error al enviar email: {str(e)}')
    
    return redirect('buscar_wikipedia')
# alumnos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Alumno
from .forms import AlumnoForm
from .utils import generar_pdf_alumno

@login_required
def dashboard(request):
    # Obtener alumnos del usuario actual
    alumnos = Alumno.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.user = request.user
            alumno.save()
            messages.success(request, f'Alumno {alumno.nombre} creado exitosamente!')
            return redirect('dashboard')
    else:
        form = AlumnoForm()
    
    context = {
        'alumnos': alumnos,
        'form': form
    }
    return render(request, 'alumnos/dashboard.html', context)

@login_required
def eliminar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, user=request.user)
    if request.method == 'POST':
        alumno.delete()
        messages.success(request, f'Alumno {alumno.nombre} eliminado!')
    return redirect('dashboard')

@login_required
def descargar_pdf(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, user=request.user)
    
    try:
        # Generar el PDF
        buffer = generar_pdf_alumno(alumno_id)
        
        # Crear respuesta
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ficha_{alumno.nombre}_{alumno.id}.pdf"'
        
        return response
    except Exception as e:
        messages.error(request, f'Error al generar PDF: {str(e)}')
        return redirect('dashboard')

@login_required
def enviar_pdf_email(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, user=request.user)
    
    try:
        # 1. Generar el PDF
        pdf_buffer = generar_pdf_alumno(alumno_id)
        
        # 2. Crear el email
        email = EmailMessage(
            subject=f'Ficha de Alumno - {alumno.nombre}',
            body=f'''
            Hola {request.user.username},
            
            Adjuntamos la ficha del alumno {alumno.nombre}.
            
            Carrera: {alumno.carrera}
            Email: {alumno.email}
            
            Saludos,
            Sistema de Alumnos
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[request.user.email],  # Se envía al usuario logueado
        )
        
        # 3. Adjuntar PDF
        email.attach(f'ficha_{alumno.nombre}.pdf', pdf_buffer.getvalue(), 'application/pdf')
        
        # 4. Enviar
        email.send()
        
        messages.success(request, f'PDF de {alumno.nombre} enviado a tu email!')
    except Exception as e:
        messages.error(request, f'Error al enviar email: {str(e)}')
    
    return redirect('dashboard')
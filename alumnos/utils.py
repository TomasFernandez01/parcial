from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
import io
from django.http import HttpResponse
from .models import Alumno

def generar_pdf_alumno(alumno_id):
    # Obtener el alumno
    alumno = Alumno.objects.get(id=alumno_id)
    
    # Crear el response con el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        textColor=colors.darkblue
    )
    
    estilo_subtitulo = ParagraphStyle(
        'CustomSubtitle', 
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Contenido del PDF
    titulo = Paragraph("FICHA DE ALUMNO", estilo_titulo)
    elements.append(titulo)
    
    # Datos de la institución
    institucion = Paragraph("<b>INSTITUCIÓN EDUCATIVA</b><br/>Sistema de Gestión Académica", styles["Normal"])
    elements.append(institucion)
    elements.append(Spacer(1, 20))
    
    # Datos del alumno
    datos_alumno = [
        ["<b>Nombre:</b>", alumno.nombre],
        ["<b>Email:</b>", alumno.email],
        ["<b>Carrera:</b>", alumno.carrera],
        ["<b>Fecha de registro:</b>", alumno.fecha_creacion.strftime("%d/%m/%Y")],
        ["<b>Código de alumno:</b>", f"ALU-{alumno.id:04d}"]
    ]
    
    # Crear tabla de datos
    tabla = Table(datos_alumno, colWidths=[4*cm, 10*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
    ]))
    
    elements.append(tabla)
    elements.append(Spacer(1, 30))
    
    # Pie de página
    pie = Paragraph(f"<i>Documento generado el {alumno.fecha_creacion.strftime('%d/%m/%Y a las %H:%M')}</i>", styles["Italic"])
    elements.append(pie)
    
    # Generar PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
import flet as ft
import json
import os
from datetime import datetime
from collections import Counter

def main(page: ft.Page):
    page.title = "Panel de Administrador"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.Colors.GREY_50
    
    # Variables para los contenedores de datos
    tabla_accesos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Hora", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Detalles", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
        horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
        heading_row_color=ft.Colors.BLUE_50,
    )
    
    tabla_busquedas = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Descripción Búsqueda", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Resultado", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Hora", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
        horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
        heading_row_color=ft.Colors.GREEN_50,
    )
    
    # Contenedores para estadísticas
    total_accesos = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
    total_busquedas = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
    usuarios_activos = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700)
    
    def cargar_logs():
        """Carga los logs del sistema"""
        try:
            archivo_log = "sistema_logs.json"
            if os.path.exists(archivo_log):
                with open(archivo_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error al cargar logs: {e}")
            return []
    
    def actualizar_estadisticas():
        """Actualiza las estadísticas del panel"""
        logs = cargar_logs()
        
        # Contar diferentes tipos de eventos
        accesos = [log for log in logs if log['tipo'] in ['login_admin', 'login_usuario']]
        busquedas = [log for log in logs if log['tipo'] == 'busqueda']
        usuarios_unicos = set([log['usuario'] for log in logs if log['tipo'] in ['login_admin', 'login_usuario']])
        
        total_accesos.value = str(len(accesos))
        total_busquedas.value = str(len(busquedas))
        usuarios_activos.value = str(len(usuarios_unicos))
    
    def actualizar_tabla_accesos():
        """Actualiza la tabla de accesos"""
        logs = cargar_logs()
        accesos = [log for log in logs if log['tipo'] in ['login_admin', 'login_usuario', 'login_fallido']]
        
        # Ordenar por fecha más reciente
        accesos.sort(key=lambda x: x['timestamp'], reverse=True)
        
        tabla_accesos.rows.clear()
        for log in accesos[:50]:  # Mostrar últimos 50 accesos
            color_tipo = ft.Colors.GREEN_100 if log['tipo'] == 'login_usuario' else \
                        ft.Colors.BLUE_100 if log['tipo'] == 'login_admin' else ft.Colors.RED_100
            
            tabla_accesos.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(log['usuario'])),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                log['tipo'].replace('_', ' ').title(),
                                color=ft.Colors.WHITE,
                                size=11
                            ),
                            bgcolor=color_tipo,
                            padding=5,
                            border_radius=5
                        )),
                        ft.DataCell(ft.Text(log['fecha'])),
                        ft.DataCell(ft.Text(log['hora'])),
                        ft.DataCell(ft.Text(log.get('detalles', '-'), max_lines=2)),
                    ]
                )
            )
    
    def actualizar_tabla_busquedas():
        """Actualiza la tabla de búsquedas"""
        logs = cargar_logs()
        busquedas = [log for log in logs if log['tipo'] == 'busqueda']
        
        # Ordenar por fecha más reciente
        busquedas.sort(key=lambda x: x['timestamp'], reverse=True)
        
        tabla_busquedas.rows.clear()
        for log in busquedas[:50]:  # Mostrar últimas 50 búsquedas
            detalles = json.loads(log.get('detalles', '{}'))
            descripcion = detalles.get('descripcion', 'N/A')
            resultado = detalles.get('resultado', 'N/A')
            
            # Limitar longitud de descripción
            if len(descripcion) > 50:
                descripcion = descripcion[:50] + "..."
            
            tabla_busquedas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(log['usuario'])),
                        ft.DataCell(ft.Text(descripcion)),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                resultado.upper(),
                                color=ft.Colors.WHITE,
                                size=11,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=ft.Colors.RED_400 if resultado.lower() == 'arrufo' else ft.Colors.BLUE_400,
                            padding=5,
                            border_radius=5
                        )),
                        ft.DataCell(ft.Text(log['fecha'])),
                        ft.DataCell(ft.Text(log['hora'])),
                    ]
                )
            )
    
    def generar_reporte(e):
        """Genera un reporte completo en formato PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            
            logs = cargar_logs()
            
            # Análisis de datos
            accesos = [log for log in logs if log['tipo'] in ['login_admin', 'login_usuario']]
            busquedas = [log for log in logs if log['tipo'] == 'busqueda']
            usuarios_unicos = set([log['usuario'] for log in accesos])
            
            # Contar búsquedas por usuario
            busquedas_por_usuario = Counter([log['usuario'] for log in busquedas])
            
            # Contar tipos de resultados
            resultados = []
            for busqueda in busquedas:
                try:
                    detalles = json.loads(busqueda.get('detalles', '{}'))
                    resultado = detalles.get('resultado', 'desconocido')
                    resultados.append(resultado)
                except:
                    pass
            
            contador_resultados = Counter(resultados)
            
            # Crear PDF
            nombre_archivo = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Estilos personalizados
            titulo_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1E40AF'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            subtitulo_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1E40AF'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )
            
            fecha_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.gray,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            # Título
            titulo = Paragraph("REPORTE DEL SISTEMA DE ANÁLISIS DE FISURAS", titulo_style)
            story.append(titulo)
            
            # Fecha
            fecha_reporte = datetime.now().strftime("%d de %B de %Y - %H:%M:%S")
            fecha_texto = Paragraph(f"Generado el: {fecha_reporte}", fecha_style)
            story.append(fecha_texto)
            story.append(Spacer(1, 0.3*inch))
            
            # ESTADÍSTICAS GENERALES
            story.append(Paragraph("📊 ESTADÍSTICAS GENERALES", subtitulo_style))
            
            data_stats = [
                ['Métrica', 'Valor'],
                ['Total de Accesos al Sistema', str(len(accesos))],
                ['Total de Búsquedas Realizadas', str(len(busquedas))],
                ['Usuarios Activos', str(len(usuarios_unicos))]
            ]
            
            tabla_stats = Table(data_stats, colWidths=[4*inch, 2*inch])
            tabla_stats.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')])
            ]))
            story.append(tabla_stats)
            story.append(Spacer(1, 0.3*inch))
            
            # ACTIVIDAD POR USUARIO
            story.append(Paragraph("👥 ACTIVIDAD POR USUARIO", subtitulo_style))
            
            data_usuarios = [['Usuario', 'Accesos', 'Búsquedas']]
            for usuario in sorted(usuarios_unicos):
                num_accesos = len([log for log in accesos if log['usuario'] == usuario])
                num_busquedas = busquedas_por_usuario.get(usuario, 0)
                data_usuarios.append([usuario, str(num_accesos), str(num_busquedas)])
            
            tabla_usuarios = Table(data_usuarios, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            tabla_usuarios.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')])
            ]))
            story.append(tabla_usuarios)
            story.append(Spacer(1, 0.3*inch))
            
            # ANÁLISIS DE RESULTADOS
            story.append(Paragraph("🔍 ANÁLISIS DE RESULTADOS", subtitulo_style))
            story.append(Paragraph("Distribución de Clasificaciones:", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            data_resultados = [['Tipo', 'Cantidad', 'Porcentaje']]
            for tipo, cantidad in contador_resultados.most_common():
                porcentaje = (cantidad / len(resultados) * 100) if resultados else 0
                data_resultados.append([
                    tipo.upper(),
                    str(cantidad),
                    f"{porcentaje:.1f}%"
                ])
            
            tabla_resultados = Table(data_resultados, colWidths=[2.5*inch, 1.5*inch, 2*inch])
            tabla_resultados.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')])
            ]))
            story.append(tabla_resultados)
            story.append(PageBreak())
            
            # ÚLTIMAS BÚSQUEDAS
            story.append(Paragraph("📝 ÚLTIMAS BÚSQUEDAS REALIZADAS", subtitulo_style))
            story.append(Spacer(1, 0.2*inch))
            
            data_busquedas = [['#', 'Usuario', 'Fecha/Hora', 'Resultado']]
            for i, busqueda in enumerate(busquedas[-10:], 1):
                try:
                    detalles = json.loads(busqueda.get('detalles', '{}'))
                    resultado = detalles.get('resultado', 'N/A')
                    fecha_hora = f"{busqueda['fecha']}\n{busqueda['hora']}"
                    
                    data_busquedas.append([
                        str(i),
                        busqueda['usuario'],
                        fecha_hora,
                        resultado.upper()
                    ])
                except:
                    pass
            
            if len(data_busquedas) > 1:
                tabla_busquedas = Table(data_busquedas, colWidths=[0.5*inch, 1.5*inch, 2*inch, 1.5*inch])
                tabla_busquedas.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B5CF6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')])
                ]))
                story.append(tabla_busquedas)
            
            # Detalles de búsquedas
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("Detalles de las Búsquedas:", styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))
            
            for i, busqueda in enumerate(busquedas[-10:], 1):
                try:
                    detalles = json.loads(busqueda.get('detalles', '{}'))
                    descripcion = detalles.get('descripcion', 'N/A')
                    resultado = detalles.get('resultado', 'N/A')
                    probabilidad = detalles.get('probabilidad', 'N/A')
                    
                    texto = f"<b>{i}. {busqueda['usuario']}</b> - {busqueda['fecha']} {busqueda['hora']}<br/>"
                    texto += f"<i>Descripción:</i> {descripcion}<br/>"
                    texto += f"<i>Resultado:</i> {resultado.upper()} ({probabilidad})"
                    
                    story.append(Paragraph(texto, styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))
                except:
                    pass
            
            # Pie de página
            story.append(Spacer(1, 0.5*inch))
            footer = Paragraph(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br/>"
                "<b>Sistema de Análisis de Fisuras</b> - Reporte Generado Automáticamente",
                fecha_style
            )
            story.append(footer)
            
            # Construir PDF
            doc.build(story)
            
            # Mostrar mensaje de éxito
            page.open(
                ft.SnackBar(
                    content=ft.Text(f"✓ Reporte PDF generado: {nombre_archivo}"),
                    bgcolor=ft.Colors.GREEN_600,
                    duration=3000
                )
            )
            
        except ImportError:
            # Si reportlab no está instalado
            page.open(
                ft.SnackBar(
                    content=ft.Text("Error: Instala reportlab con 'pip install reportlab'"),
                    bgcolor=ft.Colors.RED_600,
                    duration=5000
                )
            )
        except Exception as e:
            page.open(
                ft.SnackBar(
                    content=ft.Text(f"Error al generar reporte PDF: {e}"),
                    bgcolor=ft.Colors.RED_600,
                    duration=3000
                )
            )
    
    def actualizar_todo(e):
        """Actualiza todas las tablas y estadísticas"""
        actualizar_estadisticas()
        actualizar_tabla_accesos()
        actualizar_tabla_busquedas()
        page.update()
    
    def cerrar_sesion(e):
        """Cierra la sesión del administrador y regresa al login"""
        import subprocess
        import sys
        import os
        
        # Obtener la ruta del archivo de inicio de sesión
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        archivo_login = os.path.join(directorio_actual, "inicio_sesion_mejorado.py")
        
        # Abrir la pantalla de login
        if os.path.exists(archivo_login):
            subprocess.Popen([sys.executable, archivo_login])
        
        # Cerrar la ventana actual
        page.window_close()
    
    # Crear contenido principal
    def create_main_content():
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=40, color=ft.Colors.BLUE_700),
                                ft.Column(
                                    controls=[
                                        ft.Text("Panel de Administrador", size=24, weight=ft.FontWeight.BOLD),
                                        ft.Text("Monitoreo y Control del Sistema", size=14, color=ft.Colors.GREY_600),
                                    ],
                                    spacing=0
                                ),
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    "🔄 Actualizar",
                                    on_click=actualizar_todo,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.BLUE_600,
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "📄 Generar Reporte PDF",
                                    on_click=generar_reporte,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.GREEN_600,
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "🚪 Cerrar Sesión",
                                    on_click=cerrar_sesion,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.RED_600,
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.only(bottom=ft.border.BorderSide(2, ft.Colors.BLUE_200))
                    ),
                    
                    # Estadísticas
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                # Card Total Accesos
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Icon(ft.Icons.LOGIN, size=40, color=ft.Colors.BLUE_700),
                                            total_accesos,
                                            ft.Text("Total Accesos", size=14, color=ft.Colors.GREY_600),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5
                                    ),
                                    bgcolor=ft.Colors.BLUE_50,
                                    padding=20,
                                    border_radius=10,
                                    expand=1,
                                ),
                                # Card Total Búsquedas
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Icon(ft.Icons.SEARCH, size=40, color=ft.Colors.GREEN_700),
                                            total_busquedas,
                                            ft.Text("Total Búsquedas", size=14, color=ft.Colors.GREY_600),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5
                                    ),
                                    bgcolor=ft.Colors.GREEN_50,
                                    padding=20,
                                    border_radius=10,
                                    expand=1,
                                ),
                                # Card Usuarios Activos
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Icon(ft.Icons.PEOPLE, size=40, color=ft.Colors.ORANGE_700),
                                            usuarios_activos,
                                            ft.Text("Usuarios Activos", size=14, color=ft.Colors.GREY_600),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5
                                    ),
                                    bgcolor=ft.Colors.ORANGE_50,
                                    padding=20,
                                    border_radius=10,
                                    expand=1,
                                ),
                            ],
                            spacing=20,
                        ),
                        padding=20,
                    ),
                    
                    # Tablas
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                # Tabla de Accesos
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("📊 Historial de Accesos", size=20, weight=ft.FontWeight.BOLD),
                                            ft.Container(
                                                content=ft.Column(
                                                    controls=[tabla_accesos],
                                                    scroll=ft.ScrollMode.AUTO,
                                                ),
                                                height=250,
                                            ),
                                        ],
                                        spacing=10
                                    ),
                                    bgcolor=ft.Colors.WHITE,
                                    padding=20,
                                    border_radius=10,
                                ),
                                
                                # Tabla de Búsquedas
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("🔍 Historial de Búsquedas", size=20, weight=ft.FontWeight.BOLD),
                                            ft.Container(
                                                content=ft.Column(
                                                    controls=[tabla_busquedas],
                                                    scroll=ft.ScrollMode.AUTO,
                                                ),
                                                height=250,
                                            ),
                                        ],
                                        spacing=10
                                    ),
                                    bgcolor=ft.Colors.WHITE,
                                    padding=20,
                                    border_radius=10,
                                ),
                            ],
                            spacing=20,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=20,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    # Cargar datos iniciales
    actualizar_estadisticas()
    actualizar_tabla_accesos()
    actualizar_tabla_busquedas()
    
    # Agregar al page
    page.add(create_main_content())

if __name__ == "__main__":
    ft.app(target=main)
# Ecuador_interfaz_mejorado.py
import flet as ft
import sys
import os
import json
from datetime import datetime

def main(page: ft.Page):
    # Recibir el nombre de usuario si fue pasado desde el login
    if len(sys.argv) > 1:
        nombre_usuario = sys.argv[1]
    else:
        nombre_usuario = "Usuario"

    # Configuración de la página
    page.title = f"Sistema de Análisis - {nombre_usuario}"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.Colors.WHITE

    # Función para registrar búsquedas
    def registrar_busqueda(descripcion, resultado, probabilidad):
        """Registra una búsqueda en el sistema de logs"""
        try:
            archivo_log = "sistema_logs.json"
            
            # Leer logs existentes
            if os.path.exists(archivo_log):
                with open(archivo_log, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Crear detalles de la búsqueda
            detalles = json.dumps({
                "descripcion": descripcion,
                "resultado": resultado,
                "probabilidad": f"{probabilidad:.2%}" if probabilidad else "N/A"
            }, ensure_ascii=False)
            
            # Crear nuevo evento
            evento = {
                "usuario": nombre_usuario,
                "tipo": "busqueda",
                "detalles": detalles,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "hora": datetime.now().strftime("%H:%M:%S"),
                "timestamp": datetime.now().isoformat()
            }
            
            logs.append(evento)
            
            # Guardar logs actualizados
            with open(archivo_log, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error al registrar búsqueda: {e}")

    # Variables para el modelo (se cargan solo cuando sea necesario)
    modelo_cargado = False
    tokenizer = None
    model = None
    
    # Variable para almacenar el historial de descripciones
    historial_descripciones = []

    def cargar_modelo():
        """Carga el modelo solo cuando sea necesario"""
        nonlocal modelo_cargado, tokenizer, model
        try:
            # Importar aquí para evitar cargarlos al inicio
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            modelo_path = "./fisuras_classifier"
            if os.path.exists(modelo_path):
                tokenizer = AutoTokenizer.from_pretrained(modelo_path)
                model = AutoModelForSequenceClassification.from_pretrained(modelo_path)
                modelo_cargado = True
                return True
            else:
                print(f"Modelo no encontrado en: {modelo_path}")
                return False
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            return False

    # Función para clasificar fisura
    def clasificar_fisura(texto):
        if not texto or not texto.strip():
            return None, None, None

        # Cargar modelo si no está cargado
        if not modelo_cargado:
            if not cargar_modelo():
                return None, None, None

        try:
            import torch

            # Tokenizar el texto
            inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True, max_length=128)

            # Realizar predicción
            with torch.no_grad():
                outputs = model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # Obtener probabilidades (ajusta índices según tu modelo)
            prob_arrufo = float(predictions[0][0].item())
            prob_puntual = float(predictions[0][1].item())

            # Determinar clase
            if prob_arrufo > prob_puntual:
                clase = "arrufo"
                probabilidad = prob_arrufo
            else:
                clase = "puntual"
                probabilidad = prob_puntual

            return clase, probabilidad, {"arrufo": prob_arrufo, "puntual": prob_puntual}
        except Exception as e:
            print(f"Error en clasificación: {e}")
            return None, None, None

    # Función para crear un gráfico de pastel personalizado
    def crear_pie_chart(probabilidades):
        arrufo_percent = probabilidades.get('arrufo', 0) * 100
        puntual_percent = probabilidades.get('puntual', 0) * 100

        tamaño = 150
        return ft.Container(
            width=tamaño,
            height=tamaño,
            content=ft.Stack([
                # Fondo del pastel
                ft.Container(
                    width=tamaño,
                    height=tamaño,
                    border_radius=tamaño/2,
                    bgcolor=ft.Colors.GREY_300,
                ),
                # Segmento de Arrufo (rojo)
                ft.Container(
                    width=tamaño,
                    height=tamaño,
                    border_radius=tamaño/2,
                    gradient=ft.SweepGradient(
                        center=ft.alignment.center,
                        start_angle=0,
                        end_angle=probabilidades.get('arrufo', 0) * 360,
                        colors=[ft.Colors.RED, ft.Colors.RED] if probabilidades.get('arrufo', 0) > 0 else [ft.Colors.TRANSPARENT, ft.Colors.TRANSPARENT],
                    ),
                ),
                # Segmento de Puntual (azul)
                ft.Container(
                    width=tamaño,
                    height=tamaño,
                    border_radius=tamaño/2,
                    gradient=ft.SweepGradient(
                        center=ft.alignment.center,
                        start_angle=probabilidades.get('arrufo', 0) * 360,
                        end_angle=360,
                        colors=[ft.Colors.BLUE, ft.Colors.BLUE] if probabilidades.get('puntual', 0) > 0 else [ft.Colors.TRANSPARENT, ft.Colors.TRANSPARENT],
                    ),
                ),
                # Centro blanco para efecto de dona
                ft.Container(
                    width=tamaño - 40,
                    height=tamaño - 40,
                    border_radius=(tamaño - 40) / 2,
                    bgcolor=ft.Colors.WHITE,
                    top=20,
                    left=20,
                ),
                # Texto en el centro
                ft.Container(
                    width=tamaño,
                    height=tamaño,
                    content=ft.Column([
                        ft.Text(
                            f"{max(arrufo_percent, puntual_percent):.0f}%",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK87,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            "ARRUFO" if probabilidades.get('arrufo', 0) > probabilidades.get('puntual', 0) else "PUNTUAL",
                            size=12,
                            color=ft.Colors.BLACK54,
                            text_align=ft.TextAlign.CENTER
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                )
            ])
        )

    # Función de ayuda
    def mostrar_ayuda_fisura(e):
        contenido_ayuda = ft.Column([
            ft.Text("📋 GUÍA PARA DESCRIBIR FISURAS",
                   size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Divider(),
            ft.Text("Para una descripción efectiva, incluye:",
                   size=14, weight=ft.FontWeight.BOLD),
            ft.Text("📍 Ubicación exacta:", size=12, weight=ft.FontWeight.BOLD),
            ft.Text("   - Ej: 'columna izquierda, piso superior, muro norte'", size=12),
            ft.Text("📏 Dimensiones:", size=12, weight=ft.FontWeight.BOLD),
            ft.Text("   - Ej: '15cm de largo, 2mm de ancho, 5mm de profundidad'", size=12),
            ft.Text("🧭 Dirección y orientación:", size=12, weight=ft.FontWeight.BOLD),
            ft.Text("   - Ej: 'vertical, diagonal, horizontal, en zig-zag'", size=12),
            ft.Text("🔍 Características visibles:", size=12, weight=ft.FontWeight.BOLD),
            ft.Text("   - Ej: 'bordes irregulares, línea recta, con desprendimientos'", size=12),
            ft.Divider(),
            ft.Text("📝 EJEMPLO COMPLETO:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
            ft.Text(
                "'Fisura vertical de 20cm en columna izquierda del primer piso, "
                "con 3mm de ancho y profundidad superficial, presenta bordes irregulares "
                "y se ubica cerca del encuentro con la viga principal'",
                size=11,
                color=ft.Colors.BLACK87,
                italic=True
            ),
        ], scroll=ft.ScrollMode.AUTO)

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Ayuda"),
            content=ft.Container(
                content=contenido_ayuda,
                width=500,
                height=400
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: page.close(dialogo)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dialogo)

    # Función para cerrar sesión
    def cerrar_sesion(e):
        """Cierra sesión y regresa a la pantalla de login"""
        import subprocess
        import sys
        import os
        
        # Obtener la ruta del archivo de inicio de sesión
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        archivo_login = os.path.join(directorio_actual, "inicio_sesion_mejorado.py")
        
        # Primero abrir la pantalla de login
        if os.path.exists(archivo_login):
            subprocess.Popen([sys.executable, archivo_login])
        else:
            print(f"No se encontró el archivo de login: {archivo_login}")
        
        # Pequeña pausa para asegurar que el nuevo proceso inicie
        import time
        time.sleep(0.5)
        
        # Cerrar completamente la ventana actual
        page.window_destroy()

    # Contenido principal
    def create_main_content():
        # Elementos de la interfaz
        texto_fisura = ft.TextField(
            label="Describe la fisura encontrada",
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="Ejemplo: Fisura vertical de 15cm en la columna del lado izquierdo...",
            border_color=ft.Colors.BLUE_400,
        )

        resultado_texto = ft.Text(
            value="",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLACK87
        )

        probabilidad_texto = ft.Text(
            value="",
            size=14,
            color=ft.Colors.BLACK54
        )

        pie_chart_container = ft.Container(
            content=ft.Text(""),
            visible=False
        )

        leyenda_container = ft.Container(
            content=ft.Column([]),
            visible=False
        )
        
        # Contenedor para mensajes del chat
        chat_container = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            visible=False,
            spacing=10
        )
        
        # Variable para la tarjeta del chat (se asignará después)
        chat_card = None
        
        # Campo de texto para mejorar la descripción
        texto_mejora = ft.TextField(
            label="Mejora tu descripción aquí",
            multiline=True,
            min_lines=2,
            max_lines=4,
            hint_text="Agrega más detalles: ubicación exacta, dimensiones, orientación...",
            border_color=ft.Colors.BLUE_400,
            visible=False
        )
        
        boton_enviar_mejora = ft.ElevatedButton(
            text="📤 Enviar descripción mejorada",
            on_click=None,  # Se asignará después
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600,
            ),
            height=40,
            visible=False
        )

        def agregar_mensaje_chat(mensaje, es_sistema=True):
            """Agrega un mensaje al chat"""
            color_fondo = ft.Colors.BLUE_50 if es_sistema else ft.Colors.GREEN_50
            icono = "🤖" if es_sistema else "👤"
            
            mensaje_card = ft.Container(
                content=ft.Row([
                    ft.Text(icono, size=20),
                    ft.Text(
                        mensaje,
                        size=13,
                        color=ft.Colors.BLACK87,
                        expand=True
                    )
                ]),
                bgcolor=color_fondo,
                border_radius=10,
                padding=15,
                border=ft.border.all(1, ft.Colors.BLUE_200 if es_sistema else ft.Colors.GREEN_200)
            )
            
            chat_container.controls.append(mensaje_card)
            chat_container.visible = True
            if chat_card:
                chat_card.visible = True
            page.update()

        def procesar_mejora(e):
            """Procesa la descripción mejorada"""
            mejora = texto_mejora.value.strip()
            
            if not mejora:
                page.open(
                    ft.SnackBar(
                        content=ft.Text("Por favor, agrega más detalles a tu descripción"),
                        bgcolor=ft.Colors.ORANGE_400
                    )
                )
                return
            
            # Agregar la mejora al historial
            if historial_descripciones:
                descripcion_completa = historial_descripciones[-1] + " " + mejora
            else:
                descripcion_completa = mejora
            
            historial_descripciones.append(descripcion_completa)
            
            # Agregar mensaje del usuario al chat
            agregar_mensaje_chat(f"Descripción mejorada: {mejora}", es_sistema=False)
            
            # Clasificar con la descripción mejorada
            clase, probabilidad, probabilidades = clasificar_fisura(descripcion_completa)
            
            if clase:
                if probabilidad < 0.90:
                    # Aún es baja la confianza
                    agregar_mensaje_chat(
                        f"Recibí tu descripción. La confianza es del {probabilidad:.1%}. "
                        "Sé más específico: ¿Puedes describir mejor la ubicación exacta, "
                        "las dimensiones aproximadas (largo, ancho, profundidad) y la orientación "
                        "de la fisura (vertical, horizontal, diagonal)?",
                        es_sistema=True
                    )
                    texto_mejora.value = ""
                else:
                    # Confianza suficiente
                    agregar_mensaje_chat(
                        f"¡Excelente! Ahora la confianza es del {probabilidad:.1%}. "
                        f"La fisura ha sido clasificada como: {clase.upper()}",
                        es_sistema=True
                    )
                    
                    # Actualizar resultados
                    resultado_texto.value = f"Clasificación: {clase.upper()}"
                    resultado_texto.color = ft.Colors.RED_700 if clase == "arrufo" else ft.Colors.BLUE_700
                    probabilidad_texto.value = f"Confianza: {probabilidad:.1%}"
                    
                    # Actualizar gráfico
                    pie_chart_container.content = crear_pie_chart(probabilidades)
                    pie_chart_container.visible = True
                    
                    # Actualizar leyenda
                    leyenda_container.content = ft.Column([
                        ft.Row([
                            ft.Container(width=20, height=20, bgcolor=ft.Colors.RED, border_radius=5),
                            ft.Text(f"Arrufo: {probabilidades['arrufo']:.1%}", size=12)
                        ]),
                        ft.Row([
                            ft.Container(width=20, height=20, bgcolor=ft.Colors.BLUE, border_radius=5),
                            ft.Text(f"Puntual: {probabilidades['puntual']:.1%}", size=12)
                        ])
                    ])
                    leyenda_container.visible = True
                    
                    # Ocultar campos de mejora
                    texto_mejora.visible = False
                    boton_enviar_mejora.visible = False
                    if chat_card:
                        chat_card.visible = False
                    
                    # Registrar búsqueda
                    registrar_busqueda(descripcion_completa, clase, probabilidad)
            
            page.update()
        
        # Asignar la función al botón
        boton_enviar_mejora.on_click = procesar_mejora

        def analizar_fisura(e):
            descripcion = texto_fisura.value.strip()
            
            if not descripcion:
                page.open(
                    ft.SnackBar(
                        content=ft.Text("Por favor, describe la fisura"),
                        bgcolor=ft.Colors.RED_400
                    )
                )
                return

            # Limpiar historial y chat
            historial_descripciones.clear()
            historial_descripciones.append(descripcion)
            chat_container.controls.clear()
            chat_container.visible = False
            if chat_card:
                chat_card.visible = False

            # Clasificar
            clase, probabilidad, probabilidades = clasificar_fisura(descripcion)

            if clase:
                # Verificar si la confianza es menor al 90%
                if probabilidad < 0.90:
                    # Mostrar mensaje de chatbot
                    agregar_mensaje_chat(
                        f"He analizado tu descripción y la confianza es del {probabilidad:.1%}. "
                        "Sé más específico en tu descripción para mejorar la precisión. "
                        "Por favor, describe mejor la fisura incluyendo: ubicación exacta, "
                        "dimensiones (largo, ancho, profundidad) y orientación (vertical, horizontal, diagonal).",
                        es_sistema=True
                    )
                    
                    # Mostrar campos para mejorar descripción
                    texto_mejora.visible = True
                    texto_mejora.value = ""
                    boton_enviar_mejora.visible = True
                    
                    # Mostrar resultados preliminares
                    resultado_texto.value = f"Clasificación preliminar: {clase.upper()} (Baja confianza)"
                    resultado_texto.color = ft.Colors.ORANGE_700
                    probabilidad_texto.value = f"Confianza: {probabilidad:.1%} - Necesita más detalles"
                    
                    pie_chart_container.visible = False
                    leyenda_container.visible = False
                    
                else:
                    # Confianza suficiente
                    resultado_texto.value = f"Clasificación: {clase.upper()}"
                    resultado_texto.color = ft.Colors.RED_700 if clase == "arrufo" else ft.Colors.BLUE_700
                    probabilidad_texto.value = f"Confianza: {probabilidad:.1%}"

                    # Actualizar gráfico
                    pie_chart_container.content = crear_pie_chart(probabilidades)
                    pie_chart_container.visible = True

                    # Actualizar leyenda
                    leyenda_container.content = ft.Column([
                        ft.Row([
                            ft.Container(width=20, height=20, bgcolor=ft.Colors.RED, border_radius=5),
                            ft.Text(f"Arrufo: {probabilidades['arrufo']:.1%}", size=12)
                        ]),
                        ft.Row([
                            ft.Container(width=20, height=20, bgcolor=ft.Colors.BLUE, border_radius=5),
                            ft.Text(f"Puntual: {probabilidades['puntual']:.1%}", size=12)
                        ])
                    ])
                    leyenda_container.visible = True
                    
                    # Ocultar campos de mejora
                    texto_mejora.visible = False
                    boton_enviar_mejora.visible = False
                    chat_container.visible = False
                    if chat_card:
                        chat_card.visible = False

                    # **REGISTRAR LA BÚSQUEDA EN EL SISTEMA**
                    registrar_busqueda(descripcion, clase, probabilidad)

            else:
                resultado_texto.value = "Error al clasificar"
                resultado_texto.color = ft.Colors.RED
                probabilidad_texto.value = ""
                pie_chart_container.visible = False
                leyenda_container.visible = False
                texto_mejora.visible = False
                boton_enviar_mejora.visible = False
                chat_container.visible = False
                if chat_card:
                    chat_card.visible = False

            page.update()

        boton_analizar = ft.ElevatedButton(
            text="🔍 Analizar Fisura",
            on_click=analizar_fisura,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_600,
            ),
            height=50,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Sección de entrada
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Descripción de la Fisura",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLACK87
                                    ),
                                    texto_fisura,
                                    boton_analizar,
                                ],
                                spacing=15
                            ),
                            padding=20
                        ),
                        margin=ft.margin.only(bottom=20)
                    ),

                    # Sección Resultados
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Resultados del Análisis",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLACK87
                                    ),

                                    # Resultados de Clasificación
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Text(
                                                    "Clasificación Detectada",
                                                    size=16,
                                                    weight=ft.FontWeight.W_500,
                                                    color=ft.Colors.BLACK87
                                                ),
                                                resultado_texto,
                                                # Gráfico de pastel y leyenda
                                                ft.Row([
                                                    pie_chart_container,
                                                    ft.VerticalDivider(width=20, color=ft.Colors.TRANSPARENT),
                                                    leyenda_container,
                                                ], alignment=ft.MainAxisAlignment.CENTER),
                                            ],
                                            spacing=10
                                        ),
                                        padding=15,
                                        bgcolor=ft.Colors.GREY_50,
                                        border_radius=8,
                                        margin=ft.margin.only(top=10)
                                    ),

                                    # Probabilidad
                                    ft.Container(
                                        content=probabilidad_texto,
                                        padding=15,
                                        bgcolor=ft.Colors.GREY_50,
                                        border_radius=8,
                                        margin=ft.margin.only(top=10)
                                    )
                                ],
                                spacing=0
                            ),
                            padding=20
                        )
                    ),
                    
                    # Sección de Chat (visible solo cuando se necesita mejorar)
                    chat_card := ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "💬 Asistente de Mejora",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_700
                                    ),
                                    ft.Container(
                                        content=chat_container,
                                        height=200,
                                        bgcolor=ft.Colors.WHITE,
                                        border_radius=8,
                                        border=ft.border.all(1, ft.Colors.GREY_300),
                                        padding=10
                                    ),
                                    texto_mejora,
                                    boton_enviar_mejora,
                                ],
                                spacing=10
                            ),
                            padding=20
                        ),
                        visible=False
                    )
                ],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            expand=True,
            padding=20
        )

    # Barra lateral
    def create_sidebar():
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Información del usuario
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Container(
                                    width=60,
                                    height=60,
                                    border_radius=30,
                                    bgcolor=ft.Colors.BLUE_600,
                                    content=ft.Text(
                                        nombre_usuario[0].upper(),
                                        size=24,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    alignment=ft.alignment.center
                                ),
                                ft.Text(
                                    f"Bienvenido, {nombre_usuario}",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLACK87,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.Text(
                                    "Usuario Regular",
                                    size=14,
                                    color=ft.Colors.GREY_600,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.Divider(),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            text="Análisis",
                                            style=ft.ButtonStyle(
                                                color=ft.Colors.WHITE,
                                                bgcolor=ft.Colors.BLUE_600,
                                            )
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                )
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=20,
                        border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY_300))
                    ),

                    # Cerrar Sesión
                    ft.Container(
                        content=ft.ElevatedButton(
                            text="🚪 Cerrar Sesión",
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.RED_600,
                            ),
                            on_click=cerrar_sesion,
                            width=200
                        ),
                        padding=20,
                        alignment=ft.alignment.center
                    ),

                    # Línea divisoria
                    ft.Divider(height=1, color=ft.Colors.GREY_300),

                    # Botón de ayuda
                    ft.Container(
                        content=ft.ElevatedButton(
                            text="❓ ¿Cómo describir fisuras?",
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLUE_600,
                                bgcolor=ft.Colors.TRANSPARENT,
                            ),
                            on_click=mostrar_ayuda_fisura,
                            width=200
                        ),
                        padding=20,
                        alignment=ft.alignment.center
                    )
                ],
                spacing=0
            ),
            width=280,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.GREY_300))
        )

    # Diseño principal
    page.add(
        ft.Row(
            controls=[
                create_sidebar(),
                create_main_content()
            ],
            expand=True,
            spacing=0
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
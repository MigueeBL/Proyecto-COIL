# Part 1
import flet as ft
import sys
import subprocess
import os

def main(page: ft.Page):
    # Recibir el nombre de usuario si fue pasado desde el login
    if len(sys.argv) > 1:
        nombre_usuario = sys.argv[1]
    else:
        nombre_usuario = "Ing."

    # Configuración de la página
    page.title = f"Sistema de Análisis - {nombre_usuario}"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.Colors.WHITE

    # Variables para el modelo (se cargan solo cuando sea necesario)
    modelo_cargado = False
    tokenizer = None
    model = None

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
# Part 2
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
                # Segmento de Arrufo (rojo) - simplificado usando SweepGradient
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

    # FUNCIÓN DE AYUDA CORREGIDA - MÁS SIMPLE (usa page.open)
    def mostrar_ayuda_fisura(e):
        # Crear contenido de ayuda
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
                color=ft.Colors.BLUE_GREY,
                selectable=True
            ),
        ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE)

        dialogo = ft.AlertDialog(
            title=ft.Text("🎓 Ayuda para Fisuras"),
            content=contenido_ayuda,
            actions=[
                ft.TextButton("ENTENDIDO", on_click=lambda e: page.close(dialogo))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # ABRIR DIALOGO: forma correcta en Flet 0.28.3
        page.open(dialogo)
# Part 3
    # Elementos de la interfaz
    campo_fisura = ft.TextField(
        label="Descripción de la Fisura",
        hint_text="Describe detalladamente la fisura que deseas analizar...",
        multiline=True,
        min_lines=4,
        max_lines=6,
        expand=True
    )

    resultado_texto = ft.Text(
        "Ingresa una descripción detallada de la fisura y haz clic en 'Analizar' para ver los resultados de la clasificación.",
        size=14,
        color=ft.Colors.BLACK54
    )

    # Contenedor para el gráfico de pastel
    pie_chart_container = ft.Container(
        content=ft.Text(""),  # Inicialmente vacío
        visible=False,
        padding=15,
        margin=ft.margin.only(top=10),
        alignment=ft.alignment.center
    )

    # Contenedor para la leyenda (inicial)
    leyenda_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(width=20, height=20, bgcolor=ft.Colors.RED, border_radius=5),
                ft.Text("Arrufo: 0.0%", size=14, weight=ft.FontWeight.BOLD),
            ]),
            ft.Row([
                ft.Container(width=20, height=20, bgcolor=ft.Colors.BLUE, border_radius=5),
                ft.Text("Puntual: 0.0%", size=14, weight=ft.FontWeight.BOLD),
            ]),
        ], spacing=8),
        visible=False,
        padding=10
    )

    probabilidad_texto = ft.Text(
        "Esperando análisis...",
        size=16,
        weight=ft.FontWeight.W_500,
        color=ft.Colors.BLACK87
    )

    # Función para actualizar el gráfico y la leyenda (reconstruye la leyenda)
    def actualizar_grafica(probabilidades):
        arrufo_percent = probabilidades.get('arrufo', 0) * 100
        puntual_percent = probabilidades.get('puntual', 0) * 100

        # Crear y actualizar el gráfico de pastel
        pie_chart_container.content = crear_pie_chart(probabilidades)
        pie_chart_container.visible = True

        # Reconstruir la leyenda (más fiable que mutar controles anidados)
        nueva_leyenda = ft.Column([
            ft.Row([
                ft.Container(width=20, height=20, bgcolor=ft.Colors.RED, border_radius=5),
                ft.Text(f"Arrufo: {arrufo_percent:.1f}%", size=14, weight=ft.FontWeight.BOLD),
            ]),
            ft.Row([
                ft.Container(width=20, height=20, bgcolor=ft.Colors.BLUE, border_radius=5),
                ft.Text(f"Puntual: {puntual_percent:.1f}%", size=14, weight=ft.FontWeight.BOLD),
            ]),
        ], spacing=8)

        leyenda_container.content = nueva_leyenda
        leyenda_container.visible = True
        page.update()

    # Función para analizar la fisura
    def analizar_fisura(e):
        texto_fisura = campo_fisura.value

        if not texto_fisura or not texto_fisura.strip():
            # Mostrar error si el campo está vacío
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Por favor, describe la fisura antes de analizar."),
                duration=2000
            )
            page.snack_bar.open = True
            page.update()
            return

        # Mostrar indicador simple (barra de progreso temporal)
        page.splash = ft.ProgressBar()
        resultado_texto.value = "Analizando fisura..."
        pie_chart_container.visible = False
        leyenda_container.visible = False
        probabilidad_texto.value = "Calculando probabilidad..."
        page.update()

        # Clasificar la fisura
        clase, probabilidad, probs = clasificar_fisura(texto_fisura)

        # Ocultar indicador de carga
        page.splash = None

        if clase is not None and probs is not None:
            # Actualizar resultados
            resultado_texto.value = f"Tipo de fisura detectado: {clase.upper()}\n\nDescripción analizada:\n{texto_fisura}"

            # Actualizar gráfica
            actualizar_grafica(probs)

            # Actualizar probabilidad
            probabilidad_texto.value = f"Probabilidad de {clase}: {probabilidad * 100:.2f}%"

            # Mostrar mensaje de éxito
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Análisis completado exitosamente!"),
                duration=2000
            )
            page.snack_bar.open = True

        else:
            resultado_texto.value = ("Error: No se pudo clasificar la fisura. Verifique que:\n"
                                     "• El modelo esté disponible en ./movie_classifier\n"
                                     "• La descripción sea lo suficientemente detallada\n"
                                     "• Las dependencias estén instaladas correctamente")
            pie_chart_container.visible = False
            leyenda_container.visible = False
            probabilidad_texto.value = "Probabilidad: No disponible"

            # Mostrar mensaje de error
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Error en el análisis. Verifique la consola para más detalles."),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True

        page.update()
# Part 4
    # Función para cerrar sesión
    def cerrar_sesion(e):
        mostrar_dialogo_confirmacion()

    def mostrar_dialogo_confirmacion():
        def confirmar_cerrar_sesion(e):
            dialog.open = False
            page.update()
            abrir_login()

        def cancelar_cerrar_sesion(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar cierre de sesión"),
            content=ft.Text("¿Estás seguro de que quieres cerrar sesión?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_cerrar_sesion),
                ft.TextButton("Sí, cerrar sesión", on_click=confirmar_cerrar_sesion),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.open(dialog)

    def abrir_login():
        # Buscar el archivo de login en el mismo directorio
        try:
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            directorio_actual = os.getcwd()
        archivo_login = os.path.join(directorio_actual, "inicio_sesion.py")

        if os.path.exists(archivo_login):
            subprocess.Popen([sys.executable, archivo_login])
            # Cerrar la ventana actual después de un breve retraso
            import threading
            import time
            def cerrar_ventana():
                time.sleep(1)
                page.window_close()
            threading.Thread(target=cerrar_ventana, daemon=True).start()
        else:
            print(f"No se encontró el archivo de login: {archivo_login}")
            page.snack_bar = ft.SnackBar(content=ft.Text("Archivo de login no encontrado"))
            page.snack_bar.open = True
            page.update()

    # Contenido principal
    def create_main_content():
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Título Análisis
                    ft.Container(
                        content=ft.Text(
                            "Sistema de Análisis de Fisuras Estructurales",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900
                        ),
                        padding=ft.padding.only(bottom=20)
                    ),

                    # Describe tu Fisura
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Describe la Fisura",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLACK87
                                ),
                                campo_fisura,
                                ft.Container(
                                    content=ft.ElevatedButton(
                                        text="🔍 Analizar Fisura",
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.WHITE,
                                            bgcolor=ft.Colors.BLUE_600,
                                            padding=20,
                                        ),
                                        width=200,
                                        height=50,
                                        on_click=analizar_fisura
                                    ),
                                    alignment=ft.alignment.center,
                                    padding=10
                                )
                            ]),
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
                                    f"Rol: {obtener_rol_usuario(nombre_usuario)}",
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
                                        ft.ElevatedButton(
                                            text="Reporte",
                                            style=ft.ButtonStyle(
                                                color=ft.Colors.BLUE_600,
                                                bgcolor=ft.Colors.TRANSPARENT,
                                            )
                                        )
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

                    # BOTÓN DE AYUDA - CORREGIDO
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

    # Función para obtener el rol del usuario
    def obtener_rol_usuario(usuario):
        roles = {
            "admin": "Administrador",
            "supervisor": "Supervisor",
            "analista": "Analista",
            "usuario1": "Usuario Regular",
            "usuario2": "Usuario Regular"
        }
        return roles.get(usuario, "Usuario")

    # Diseño principal: añadir filas al page
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

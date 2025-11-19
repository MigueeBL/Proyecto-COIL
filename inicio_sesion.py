import flet as ft
import subprocess
import sys
import os

def main(page: ft.Page):
    page.title = "Inicio de Sesión"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 500
    
    # Base de datos de usuarios
    USUARIOS = {
        "admin": "1234",
        "Aitana": "321123",
        "Andrea": "andy123",
        "Miguel": "migue123",
        "Tona": "tona123"
    }
    
    # Campo de usuario
    usuario_field = ft.TextField(
        label="Usuario",
        width=300,
        prefix_icon=ft.Icons.PERSON,
        border_color=ft.Colors.BLUE_400,
    )
    
    # Campo de contraseña
    contrasena_field = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        width=300,
        prefix_icon=ft.Icons.LOCK,
        border_color=ft.Colors.BLUE_400,
    )
    
    # Texto para mensajes de error
    mensaje_error = ft.Text(
        value="",
        color=ft.Colors.RED_400,
        size=14,
        weight=ft.FontWeight.BOLD,
    )
    
    # Texto para mensaje de éxito
    mensaje_exito = ft.Text(
        value="",
        color=ft.Colors.GREEN_400,
        size=16,
        weight=ft.FontWeight.BOLD,
    )
    
    def verificar_login(e):
        usuario = usuario_field.value.strip()
        contrasena = contrasena_field.value
        
        # Limpiar mensajes previos
        mensaje_error.value = ""
        mensaje_exito.value = ""
        
        # Validar campos vacíos
        if not usuario or not contrasena:
            mensaje_error.value = "Por favor, completa todos los campos"
            page.update()
            return
        
        # Verificar credenciales
        if usuario in USUARIOS and USUARIOS[usuario] == contrasena:
            # Mostrar mensaje de éxito
            mensaje_exito.value = "✓ Inicio de sesión exitoso"
            page.update()
            
            # Abrir la aplicación principal después de un breve delay
            def abrir_aplicacion_principal():
                # Usar el directorio actual para encontrar el archivo
                directorio_actual = os.path.dirname(os.path.abspath(__file__))
                archivo_interfaz = os.path.join(directorio_actual, "Ecuador_interfaz.py")
                
                if os.path.exists(archivo_interfaz):
                    subprocess.Popen([sys.executable, archivo_interfaz, usuario])
                else:
                    # Si no encuentra el archivo, mostrar mensaje
                    mensaje_error.value = f"No se encontró el archivo: {archivo_interfaz}"
                    mensaje_exito.value = ""
                    page.update()
            
            # Ejecutar después de 1 segundo para que se vea el mensaje de éxito
            import threading
            threading.Timer(1.0, abrir_aplicacion_principal).start()
            
        else:
            mensaje_error.value = "Usuario o contraseña incorrectos"
            page.update()
    
    # Botón de login
    boton_login = ft.ElevatedButton(
        text="Iniciar Sesión",
        width=300,
        height=50,
        on_click=verificar_login,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_600,
        ),
    )
    
    # Texto informativo con credenciales

    
    # Contenedor principal
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(name=ft.Icons.ACCOUNT_CIRCLE, size=80, color=ft.Colors.BLUE_600),
                    ft.Text("Bienvenido", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Inicia sesión para continuar", size=14, color=ft.Colors.GREY_600),
                    ft.Container(height=20),
                    usuario_field,
                    contrasena_field,
                    mensaje_error,
                    mensaje_exito,
                    ft.Container(height=10),
                    boton_login
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=30,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
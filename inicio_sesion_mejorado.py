import flet as ft
import subprocess
import sys
import os
import json
from datetime import datetime

def main(page: ft.Page):
    page.title = "Inicio de Sesión - Sistema de Análisis"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 550
    
    # Base de datos de usuarios regulares
    USUARIOS = {
        "Aitana": "321123",
        "Andrea": "andy123",
        "Miguel": "migue123",
        "Tona": "tona123"
    }
    
    # Credenciales del administrador (separadas)
    ADMIN_USER = "superadmin"
    ADMIN_PASSWORD = "admin123"
    
    def registrar_evento(usuario, tipo_evento, detalles=""):
        """Registra eventos del sistema en un archivo JSON"""
        try:
            archivo_log = "sistema_logs.json"
            
            # Leer logs existentes
            if os.path.exists(archivo_log):
                with open(archivo_log, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Crear nuevo evento
            evento = {
                "usuario": usuario,
                "tipo": tipo_evento,
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
            print(f"Error al registrar evento: {e}")
    
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
        
        # Verificar si es el administrador
        if usuario == ADMIN_USER and contrasena == ADMIN_PASSWORD:
            mensaje_exito.value = "✓ Acceso de Administrador concedido"
            page.update()
            
            # Registrar acceso de administrador
            registrar_evento(usuario, "login_admin", "Acceso al panel de administración")
            
            # Abrir panel de administrador
            def abrir_panel_admin():
                directorio_actual = os.path.dirname(os.path.abspath(__file__))
                archivo_admin = os.path.join(directorio_actual, "panel_administrador.py")
                
                if os.path.exists(archivo_admin):
                    subprocess.Popen([sys.executable, archivo_admin, usuario])
                    # Esperar un momento antes de cerrar
                    import time
                    time.sleep(0.5)
                    # Cerrar completamente la ventana de login
                    page.window_destroy()
                    
                else:
                    mensaje_error.value = f"No se encontró el panel de administrador"
                    mensaje_exito.value = ""
                    page.update()
            
            import threading
            threading.Timer(1.0, abrir_panel_admin).start()
            return
        
        # Verificar credenciales de usuarios regulares
        if usuario in USUARIOS and USUARIOS[usuario] == contrasena:
            mensaje_exito.value = "✓ Inicio de sesión exitoso"
            page.update()
            
            # Registrar acceso de usuario regular
            registrar_evento(usuario, "login_usuario", "Acceso al sistema de análisis")
            
            # Abrir la aplicación principal
            def abrir_aplicacion_principal():
                directorio_actual = os.path.dirname(os.path.abspath(__file__))
                archivo_interfaz = os.path.join(directorio_actual, "Ecuador_interfaz_mejorado.py")
                
                if os.path.exists(archivo_interfaz):
                    # Abrir la interfaz pasando el nombre de usuario
                    subprocess.Popen([sys.executable, archivo_interfaz, usuario])
                    # Esperar un momento antes de cerrar
                    import time
                    time.sleep(0.5)
                    # Cerrar completamente la ventana de login
                    page.window_destroy()
                else:
                    mensaje_error.value = f"No se encontró el archivo de interfaz"
                    mensaje_exito.value = ""
                    page.update()
            
            import threading
            threading.Timer(1.0, abrir_aplicacion_principal).start()
            
        else:
            mensaje_error.value = "Usuario o contraseña incorrectos"
            registrar_evento(usuario if usuario else "desconocido", "login_fallido", "Intento de acceso fallido")
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
                    boton_login,
                    ft.Container(height=10),
                    ft.Text(
                        "👤 Admin: superadmin / admin123",
                        size=10,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=30,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
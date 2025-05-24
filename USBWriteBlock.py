# Bloqueador de Escritura USB
# Copyright (C) 2025 Jose Freddy G.
# Licenciado bajo la Licencia Pública General GNU v3.0
# Puedes obtener una copia en https://www.gnu.org/licenses/gpl-3.0.txt

import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu
import winreg
import ctypes
import sys
import os
import datetime # Para timestamps en el log
import webbrowser  # Para abrir el repositorio


# [Tus clases y funciones existentes aquí...]
def resource_path(relative_path):
    """ Obtiene la ruta absoluta para recursos """
    try:
        base_path = sys._MEIPASS  # Carpeta temporal de PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# -----------------------------------
def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("Acerca de")
    about_window.geometry("400x300")
    
    info_text = """

Bloqueador de Escritura USB v1.0.0

Desarrollado por: [Jose Freddy G.]
Fecha: [ 01/01/2025]
Licencia: [Tipo de Licencia GPL V3]

Este software permite controlar la protección contra escritura
en dispositivos USB mediante modificación del registro de Windows.

Repositorio: github.com/freedmx/USBWriteBlocker/
    """
    
    about_label = tk.Label(about_window, text=info_text, justify=tk.LEFT, padx=20, pady=20)
    about_label.pack()
    
    repo_button = tk.Button(about_window, text="Abrir Repositorio", 
                          command=lambda: webbrowser.open("https://github.com/freedmx/USBWriteBlocker/"))
    repo_button.pack(pady=10)
    
    close_button = tk.Button(about_window, text="Cerrar", command=about_window.destroy)
    close_button.pack()


# --- Clase para redirigir stdout/stderr al widget de texto ---
class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag # Podría usarse para colorear stdout vs stderr

    def write(self, str_output):
        self.widget.configure(state='normal') # Habilitar escritura
        # Añadir timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.widget.insert(tk.END, f"[{timestamp}] {str_output}", (self.tag,))
        self.widget.see(tk.END) # Autoscroll
        self.widget.configure(state='disabled') # Deshabilitar escritura para el usuario

    def flush(self):
        # Generalmente necesario para streams basados en archivos,
        # pero Tkinter Text widget se actualiza con insert.
        pass

# --- Funciones de Lógica (sin cambios mayores, solo se añadirán prints) ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

REG_PATH = r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"
REG_KEY_NAME = "WriteProtect"

def set_write_protect(enable):
    if not is_admin():
        print("Error: Se requieren privilegios de administrador.")
        messagebox.showerror("Error de Privilegios", "Esta aplicación necesita ejecutarse como administrador para modificar el registro.")
        return

    action = "activar" if enable else "desactivar"
    new_value = 1 if enable else 0
    print(f"Iniciando proceso para {action} la protección contra escritura USB...")

    try:
        print(f"Accediendo al registro: HKLM\\{REG_PATH}")
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH) # Crea o abre la clave

        if enable:
            winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_DWORD, 1)
            print(f"Valor '{REG_KEY_NAME}' establecido a 1 (Activado).")
        else:
            # Para desactivar, podemos intentar eliminar el valor o establecerlo en 0.
            # El script original usaba "WriteProtect"=- que implica eliminar.
            # Si la clave no existe, QueryValueEx o DeleteValue fallarán.
            # SetValueEx con 0 es seguro. Opcionalmente, intentar eliminar primero.
            try:
                # Intentamos eliminar primero para ser más fieles al "WriteProtect"=-
                winreg.DeleteValue(key, REG_KEY_NAME)
                print(f"Valor '{REG_KEY_NAME}' eliminado del registro.")
            except FileNotFoundError:
                print(f"Valor '{REG_KEY_NAME}' no encontrado para eliminar (lo cual es válido para desactivar).")
                # Si no se encontró y queremos asegurarnos de que esté desactivado (o la política es que 0 es off)
                # winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_DWORD, 0)
                # print(f"Valor '{REG_KEY_NAME}' establecido a 0 (Desactivado) como fallback.")
            except Exception as e_del: # Otra excepción al eliminar
                 print(f"Error al intentar eliminar '{REG_KEY_NAME}': {e_del}. Se intentará establecer a 0.")
                 winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_DWORD, 0)
                 print(f"Valor '{REG_KEY_NAME}' establecido a 0 (Desactivado).")


        winreg.CloseKey(key)
        print(f"Operación completada: Protección USB {action.upper()}DA.")
        messagebox.showinfo("Estado", f"Protección contra escritura USB {action.upper()}DA.")
        update_status_display()

    except PermissionError:
        print("Error de Permiso: No se pudo modificar el registro. Asegúrate de ejecutar como administrador.")
        messagebox.showerror("Error de Permiso", "No se pudo modificar el registro. Asegúrate de ejecutar como administrador.")
    except Exception as e:
        print(f"Error inesperado durante la operación de registro: {e}")
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

def check_current_status():
    print("Verificando estado actual de la protección contra escritura USB...")
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(key, REG_KEY_NAME)
        winreg.CloseKey(key)
        if value == 1:
            print("Estado actual: ACTIVADO (Valor 'WriteProtect' es 1).")
            return "Estado: ACTIVADO", "green"
        else:
            print(f"Estado actual: DESACTIVADO (Valor 'WriteProtect' es {value}).")
            return "Estado: DESACTIVADO", "red"
    except FileNotFoundError:
        print(f"Estado actual: DESACTIVADO (Clave '{REG_PATH}' o valor '{REG_KEY_NAME}' no encontrado).")
        return "Estado: DESACTIVADO (no configurado)", "orange"
    except Exception as e:
        print(f"Error al leer el estado del registro: {e}")
        return "Estado: Desconocido (error al leer)", "black"

def update_status_display():
    s_text, s_color = check_current_status()
    status_label.config(text=s_text, fg=s_color)

# --- Interfaz Gráfica ---
root = tk.Tk()
root.title("Bloqueador de Escritura USB v1.0.0")
root.geometry("550x500") # Ajustar tamaño para la terminal

# ====== AQUÍ DEBES COLOCAR EL ICONO ======
try:
    # Ruta relativa (el archivo icono.ico debe estar en la misma carpeta que tu script)
    root.iconbitmap("assets/USBWriteBlocker.ico")
    
    # O si está en una subcarpeta "assets":
    # root.iconbitmap("assets/icono.ico")
    
    # Para mayor robustez (manejo de rutas absolutas/relativas):
    # import os
    # base_path = os.path.dirname(__file__)
    # icon_path = os.path.join(base_path, "icono.ico")
    # root.iconbitmap(icon_path)
except Exception as e:
    print(f"No se pudo cargar el icono: {e}")

try:
    icon_path = resource_path("assets/USBWriteBlocker.ico")
    root.iconbitmap(icon_path)
except Exception as e:
    print(f"Error al cargar el icono: {e}")

# Añadir menú superior
menubar = Menu(root)

# Añadir menú superior
menubar = Menu(root)
root.config(menu=menubar)

# Menú Ayuda
helpmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Ayuda", menu=helpmenu)
helpmenu.add_command(label="Acerca de...", command=show_about)

# --- Sección Superior (Controles) ---
top_frame = tk.Frame(root)
top_frame.pack(pady=10, padx=10, fill="x")

if not is_admin():
     info_admin = tk.Label(top_frame, text="ATENCIÓN: Ejecute como administrador para funcionalidad completa.", fg="red", font=("Arial", 9, "bold"))
     info_admin.pack(pady=(0,5))

title_label = tk.Label(top_frame, text="Bloqueador de Escritura USB v1.0.0", font=("Arial", 16, "bold"))
title_label.pack()

info_text = (
    "Inicie el bloqueador ANTES de conectar la unidad USB.\n"
    "No cambie la configuración con una unidad USB conectada."
)
info_label = tk.Label(top_frame, text=info_text, justify=tk.CENTER)
info_label.pack(pady=5)

status_label = tk.Label(top_frame, text="Cargando estado...", font=("Arial", 12, "bold"), fg="blue")
status_label.pack(pady=(5,10))

btn_frame = tk.Frame(top_frame)
btn_frame.pack(pady=10)

enable_button = tk.Button(btn_frame, text="Activar Protección (ON)", command=lambda: set_write_protect(True), width=20, height=2)
enable_button.pack(side=tk.LEFT, padx=10)

disable_button = tk.Button(btn_frame, text="Desactivar Protección (OFF)", command=lambda: set_write_protect(False), width=20, height=2)
disable_button.pack(side=tk.LEFT, padx=10)

# --- Sección de la Mini Terminal ---
terminal_frame = tk.LabelFrame(root, text="Registro de Procesos", padx=5, pady=5)
terminal_frame.pack(pady=10, padx=10, fill="both", expand=True)

terminal_widget = scrolledtext.ScrolledText(terminal_frame, wrap=tk.WORD, state='disabled', height=10)
terminal_widget.pack(fill="both", expand=True)
terminal_widget.configure(font=("Consolas", 9)) # O alguna otra fuente monoespaciada

# Redirigir stdout y stderr a la mini terminal
# Es importante instanciar el redirector DESPUÉS de que terminal_widget exista.
stdout_redirector = TextRedirector(terminal_widget, "stdout")
stderr_redirector = TextRedirector(terminal_widget, "stderr") # Podrías darle un color diferente

sys.stdout = stdout_redirector
sys.stderr = stderr_redirector # Opcional, si quieres capturar errores también aquí

# --- Botón de Salir ---
exit_button = tk.Button(root, text="Salir", command=root.quit, width=10)
exit_button.pack(pady=(0,10))

# --- Inicialización ---
print("Aplicación iniciada.")
print(f"Fecha y Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
if is_admin():
    print("Ejecutando con privilegios de administrador.")
else:
    print("ADVERTENCIA: No se está ejecutando con privilegios de administrador. Algunas funciones pueden fallar.")

update_status_display() # Actualizar el estado al inicio y mostrar en log

root.mainloop()


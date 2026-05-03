# Bloqueador de Escritura USB
# Copyright (C) 2025 Jose Freddy G.
# Licenciado bajo la Licencia Pública General GNU v3.0
# Puedes obtener una copia en https://www.gnu.org/licenses/gpl-3.0.txt

import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu, filedialog, ttk
import winreg
import ctypes
import sys
import os
import datetime
import webbrowser
import hashlib
import socket
import getpass
import platform
import string

# =========================
# Configuración
# =========================
APP_NAME = "Bloqueador de Escritura USB"
APP_VERSION = "1.1.0"

REG_PATH = r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"
REG_KEY_NAME = "WriteProtect"
TEST_FILE_NAME = "__usb_writeblock_test.tmp"
REPO_URL = "https://github.com/freedmx/USBWriteBlocker/"
ICON_RELATIVE_PATH = "assets/USBWriteBlocker.ico"
APP_USER_MODEL_ID = "freedmx.usbwriteblocker.1.1.0"

# =========================
# Estilo visual
# =========================
COLOR_BG = "#f4f6f8"
COLOR_CARD = "#ffffff"
COLOR_HEADER = "#1f2937"
COLOR_TEXT = "#111827"
COLOR_MUTED = "#374151"
COLOR_SUBTLE = "#6b7280"
COLOR_BORDER = "#d1d5db"
COLOR_BLUE = "#2563eb"
COLOR_BLUE_HOVER = "#1d4ed8"
COLOR_GREEN = "#16a34a"
COLOR_RED = "#dc2626"
COLOR_ORANGE = "#f59e0b"
COLOR_LIGHT_GRAY = "#e5e7eb"
COLOR_LIGHT_BLUE = "#eff6ff"
COLOR_LIGHT_RED = "#fef2f2"
COLOR_LOG_BG = "#0f172a"
COLOR_LOG_FG = "#e5e7eb"

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 10)
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 9)

# =========================
# Utilidades
# =========================
def resource_path(relative_path):
    """Obtiene la ruta absoluta para recursos (PyInstaller-friendly)."""
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def configure_windows_app_id():
    """
    Configura el AppUserModelID de Windows.

    Esto ayuda a que Windows asocie correctamente el icono del proceso
    con la ventana, la barra de tareas y la vista Alt+Tab cuando la
    aplicación se ejecuta como .exe generado con PyInstaller.
    """
    if os.name != "nt":
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except Exception:
        # No detenemos la aplicación si Windows no permite establecer el ID.
        pass


def apply_window_icon(window):
    """
    Aplica el icono de la aplicación a una ventana Tkinter.

    Importante:
    - El parámetro --icon de PyInstaller solo cambia el icono del .exe.
    - root.iconbitmap() / window.iconbitmap() cambia el icono de la ventana.
    - resource_path() permite que el icono funcione en modo script y en modo .exe.
    """
    try:
        icon_path = resource_path(ICON_RELATIVE_PATH)
        window.iconbitmap(icon_path)
    except Exception:
        # No rompemos la app si el icono no existe o no puede cargarse.
        pass


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def restart_as_admin():
    """Reinicia la app con privilegios de administrador."""
    if is_admin():
        messagebox.showinfo("Admin", "Ya se está ejecutando como administrador.")
        return

    try:
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        root.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo elevar privilegios: {e}")


def get_system_metadata():
    """Metadatos para encabezados periciales."""
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": getpass.getuser(),
        "hostname": socket.gethostname(),
        "os": platform.platform(),
        "windows_version": platform.version(),
        "admin": str(bool(is_admin())),
    }


def center_window(window, width, height):
    window.update_idletasks()
    try:
        x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    except Exception:
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def style_button(btn, bg, fg="white", active_bg=None):
    btn.configure(
        bg=bg,
        fg=fg,
        activebackground=active_bg or bg,
        activeforeground=fg,
        relief="flat",
        bd=0,
        font=FONT_BUTTON,
        padx=14,
        pady=8,
        cursor="hand2",
        highlightthickness=0,
    )


def make_card(parent, padx=18, pady=16):
    outer = tk.Frame(parent, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
    inner = tk.Frame(outer, bg=COLOR_CARD)
    inner.pack(fill="both", expand=True, padx=padx, pady=pady)
    return outer, inner

# =========================
# Sobre / Acerca de
# =========================
def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("Acerca de")
    apply_window_icon(about_window)
    about_window.minsize(560, 560)
    about_window.configure(bg=COLOR_BG)
    about_window.transient(root)
    about_window.grab_set()
    center_window(about_window, 560, 560)

    main_frame = tk.Frame(about_window, bg=COLOR_BG)
    main_frame.pack(fill="both", expand=True, padx=22, pady=22)

    header = tk.Frame(main_frame, bg=COLOR_HEADER, height=95)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text=APP_NAME, bg=COLOR_HEADER, fg="white", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(18, 2))
    tk.Label(header, text=f"USB Write Blocker  •  Versión {APP_VERSION}", bg=COLOR_HEADER, fg="#cbd5e1", font=FONT_SUBTITLE).pack(anchor="w", padx=22)

    card, content = make_card(main_frame, padx=22, pady=18)
    card.pack(fill="both", expand=True, pady=(18, 15))

    tk.Label(content, text="Información del proyecto", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")

    info_text = (
        "Herramienta diseñada para controlar la protección contra escritura en dispositivos USB "
        "mediante la modificación controlada del registro de Windows.\n\n"
        "Desarrollado por: Jose Freddy G.\n"
        "Licencia: GPL v3\n\n"
        "Ruta del registro utilizada:"
    )
    tk.Label(content, text=info_text, bg=COLOR_CARD, fg=COLOR_MUTED, justify="left", wraplength=480, font=FONT_NORMAL).pack(anchor="w", pady=(12, 8))

    reg_frame = tk.Frame(content, bg="#f3f4f6")
    reg_frame.pack(fill="x", pady=(0, 14))
    reg_box = tk.Text(reg_frame, height=3, bg="#f3f4f6", fg=COLOR_TEXT, font=FONT_MONO, relief="flat", wrap="none")
    reg_box.insert("1.0", f"HKLM\\{REG_PATH}\\{REG_KEY_NAME}")
    reg_box.configure(state="disabled")
    reg_box.pack(fill="x", padx=8, pady=6)

    tk.Label(content, text="Repositorio oficial:", bg=COLOR_CARD, fg=COLOR_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w")
    repo_label = tk.Label(content, text=REPO_URL, bg=COLOR_CARD, fg=COLOR_BLUE, cursor="hand2", font=("Segoe UI", 10, "underline"))
    repo_label.pack(anchor="w", pady=(4, 0))
    repo_label.bind("<Button-1>", lambda e: webbrowser.open(REPO_URL))

    button_frame = tk.Frame(main_frame, bg=COLOR_BG)
    button_frame.pack(fill="x", side="bottom")

    open_btn = tk.Button(button_frame, text="Abrir repositorio", command=lambda: webbrowser.open(REPO_URL))
    style_button(open_btn, COLOR_BLUE, "white", COLOR_BLUE_HOVER)
    open_btn.pack(side="left")

    close_btn = tk.Button(button_frame, text="Cerrar", command=about_window.destroy)
    style_button(close_btn, COLOR_LIGHT_GRAY, COLOR_TEXT, "#d1d5db")
    close_btn.pack(side="right")

# =========================
# Mini terminal
# =========================
class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str_output):
        if not str_output:
            return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, f"[{timestamp}] {str_output}", (self.tag,))
        self.widget.see(tk.END)
        self.widget.configure(state="disabled")

    def flush(self):
        pass


def log(msg: str):
    print(msg)

# =========================
# Estado del registro
# =========================
def check_current_status():
    log("Verificando estado actual de la protección contra escritura USB...")
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(key, REG_KEY_NAME)
        winreg.CloseKey(key)

        if value == 1:
            log("Estado actual: ACTIVADO (WriteProtect=1).")
            return "ACTIVADO", COLOR_GREEN, value
        else:
            log(f"Estado actual: DESACTIVADO (WriteProtect={value}).")
            return "DESACTIVADO", COLOR_RED, value

    except FileNotFoundError:
        log("Estado actual: DESACTIVADO (clave o valor no encontrado).")
        return "DESACTIVADO", COLOR_ORANGE, None
    except Exception as e:
        log(f"Error al leer el estado del registro: {e}")
        return "DESCONOCIDO", COLOR_SUBTLE, None


def update_status_display():
    s_text, s_color, _ = check_current_status()
    status_value_label.config(text=s_text, fg=s_color)
    status_indicator.config(bg=s_color)
    status_description.config(
        text="La protección contra escritura USB está activa." if s_text == "ACTIVADO" else "La protección contra escritura USB está desactivada o no configurada."
    )


def set_write_protect(enable: bool):
    if not is_admin():
        log("Error: Se requieren privilegios de administrador.")
        messagebox.showerror("Error de Privilegios", "Esta aplicación necesita ejecutarse como administrador para modificar el registro.")
        return

    action = "activar" if enable else "desactivar"
    log(f"Iniciando proceso para {action} la protección contra escritura USB...")

    try:
        log(f"Accediendo al registro: HKLM\\{REG_PATH}")
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)

        if enable:
            winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_DWORD, 1)
            log(f"Valor '{REG_KEY_NAME}' establecido a 1 (Activado).")
        else:
            try:
                winreg.DeleteValue(key, REG_KEY_NAME)
                log(f"Valor '{REG_KEY_NAME}' eliminado del registro.")
            except FileNotFoundError:
                log(f"Valor '{REG_KEY_NAME}' no encontrado para eliminar (válido para desactivar).")
            except Exception as e_del:
                log(f"Error al eliminar '{REG_KEY_NAME}': {e_del}. Se intentará establecer a 0.")
                winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_DWORD, 0)
                log(f"Valor '{REG_KEY_NAME}' establecido a 0 (Desactivado).")

        winreg.CloseKey(key)
        log(f"Operación completada: Protección USB {action.upper()}DA.")
        messagebox.showinfo("Estado", f"Protección contra escritura USB {action.upper()}DA.")
        update_status_display()

    except PermissionError:
        log("Error de Permiso: No se pudo modificar el registro.")
        messagebox.showerror("Error de Permiso", "No se pudo modificar el registro. Ejecuta como administrador.")
    except Exception as e:
        log(f"Error inesperado durante la operación de registro: {e}")
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# =========================
# USB y prueba de escritura
# =========================
kernel32 = ctypes.windll.kernel32

DRIVE_REMOVABLE = 2


def get_drive_type(root_path: str) -> int:
    return kernel32.GetDriveTypeW(ctypes.c_wchar_p(root_path))


def get_volume_info(root_path: str):
    vol_name_buf = ctypes.create_unicode_buffer(261)
    fs_name_buf = ctypes.create_unicode_buffer(261)
    serial = ctypes.c_uint(0)
    max_comp = ctypes.c_uint(0)
    fs_flags = ctypes.c_uint(0)

    ok = kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(root_path),
        vol_name_buf,
        ctypes.sizeof(vol_name_buf),
        ctypes.byref(serial),
        ctypes.byref(max_comp),
        ctypes.byref(fs_flags),
        fs_name_buf,
        ctypes.sizeof(fs_name_buf),
    )
    if not ok:
        return "", "", None
    return vol_name_buf.value, fs_name_buf.value, serial.value


def list_removable_drives():
    drives = []
    for letter in string.ascii_uppercase:
        root_path = f"{letter}:\\"
        if not os.path.exists(root_path):
            continue
        if get_drive_type(root_path) == DRIVE_REMOVABLE:
            label, fs, serial = get_volume_info(root_path)
            drives.append({"letter": letter, "root": root_path, "label": label, "fs": fs, "serial": serial})
    return drives


def refresh_usb_list():
    usb_drives = list_removable_drives()
    usb_combo["values"] = [f"{d['letter']}:  {d['label'] or '(sin etiqueta)'}  [{d['fs'] or 'FS ?'}]" for d in usb_drives]
    usb_combo._drive_map = usb_drives

    if usb_drives:
        usb_combo.current(0)
        usb_count_label.config(text=f"{len(usb_drives)} unidad(es) detectada(s)", fg=COLOR_GREEN)
        log(f"USB detectadas: {len(usb_drives)}")
        for d in usb_drives:
            log(f" - {d['root']} | Label: {d['label'] or '-'} | FS: {d['fs'] or '-'} | Serial: {d['serial']}")
    else:
        usb_combo.set("")
        usb_count_label.config(text="No se detectaron unidades removibles", fg=COLOR_RED)
        log("No se detectaron unidades removibles (USB).")


def get_selected_usb_root():
    drives = getattr(usb_combo, "_drive_map", [])
    idx = usb_combo.current()
    if idx is None or idx < 0 or idx >= len(drives):
        return None
    return drives[idx]["root"]


def test_write_block():
    root_path = get_selected_usb_root()
    if not root_path:
        messagebox.showwarning("USB", "No hay una USB seleccionada para probar.")
        return

    if not messagebox.askyesno(
        "Prueba de Escritura",
        "Esta prueba intentará crear un archivo temporal en la USB para verificar bloqueo.\n"
        "Si se crea, se eliminará inmediatamente.\n\n¿Deseas continuar?",
    ):
        return

    test_path = os.path.join(root_path, TEST_FILE_NAME)
    log(f"Iniciando prueba de escritura en: {test_path}")
    created = False

    try:
        with open(test_path, "xb") as f:
            f.write(b"USBWriteBlocker test\n")
        created = True
        log("RESULTADO: Se PUDO escribir en la USB (bloqueo NO efectivo para esta unidad).")
        messagebox.showwarning("Prueba de Escritura", "Se pudo crear el archivo temporal.\nEsto indica que el bloqueo NO fue efectivo.")
    except PermissionError:
        log("RESULTADO: Permiso denegado (bloqueo efectivo confirmado).")
        messagebox.showinfo("Prueba de Escritura", "Permiso denegado al intentar escribir.\nEsto confirma que el bloqueo de escritura está activo.")
    except FileExistsError:
        log("El archivo de prueba ya existía. Se intentará eliminar para repetir prueba.")
        try:
            os.remove(test_path)
            log("Archivo de prueba previo eliminado.")
            test_write_block()
            return
        except Exception as e:
            log(f"No se pudo eliminar archivo previo: {e}")
            messagebox.showerror("Prueba de Escritura", f"No se pudo eliminar el archivo previo: {e}")
    except Exception as e:
        log(f"Error inesperado en prueba de escritura: {e}")
        messagebox.showerror("Prueba de Escritura", f"Error inesperado: {e}")
    finally:
        if created:
            try:
                os.remove(test_path)
                log("Limpieza: archivo temporal eliminado.")
            except Exception as e:
                log(f"Advertencia: no se pudo eliminar el archivo temporal: {e}")

# =========================
# Exportación de log + SHA256 + Nota técnica
# =========================
def get_terminal_text():
    return terminal_widget.get("1.0", tk.END).strip()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_log_header():
    meta = get_system_metadata()
    status_text, _, status_val = check_current_status()
    header = [
        f"{APP_NAME} v{APP_VERSION}",
        f"Timestamp: {meta['timestamp']}",
        f"User: {meta['user']}",
        f"Hostname: {meta['hostname']}",
        f"OS: {meta['os']}",
        f"Windows Version: {meta['windows_version']}",
        f"Admin: {meta['admin']}",
        f"Registry Path: HKLM\\{REG_PATH}",
        f"Registry Value: {REG_KEY_NAME} = {status_val}",
        f"Status: {status_text}",
        "-" * 70,
        "",
    ]
    return "\n".join(header)


def export_log_txt():
    terminal_text = get_terminal_text()
    if not terminal_text:
        messagebox.showwarning("Exportar Log", "No hay contenido en el log para exportar.")
        return

    default_name = f"USBWriteBlocker_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
    save_path = filedialog.asksaveasfilename(title="Guardar log (TXT)", defaultextension=".txt", initialfile=default_name, filetypes=[("Text file", "*.txt")])
    if not save_path:
        return

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(build_log_header() + terminal_text + "\n")

        digest = sha256_file(save_path)
        sha_path = save_path + ".sha256"
        with open(sha_path, "w", encoding="utf-8") as f:
            f.write(f"{digest}  {os.path.basename(save_path)}\n")

        log(f"Log exportado: {save_path}")
        log(f"SHA256: {digest}")
        log(f"Archivo SHA256: {sha_path}")
        messagebox.showinfo("Exportar Log", f"Log exportado correctamente.\n\nArchivo: {save_path}\nSHA256: {digest}\n\nSe generó: {sha_path}")
    except Exception as e:
        log(f"Error al exportar log: {e}")
        messagebox.showerror("Exportar Log", f"No se pudo exportar el log: {e}")


def generate_technical_note():
    meta = get_system_metadata()
    status_text, _, status_val = check_current_status()
    usb_drives = list_removable_drives()
    usb_lines = []

    if usb_drives:
        for d in usb_drives:
            usb_lines.append(f" - {d['root']} | Label: {d['label'] or '-'} | FS: {d['fs'] or '-'} | Serial: {d['serial']}")
    else:
        usb_lines.append(" - (No se detectaron unidades removibles al momento del reporte)")

    default_name = f"USBWriteBlocker_nota_tecnica_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
    save_path = filedialog.asksaveasfilename(title="Guardar Nota Técnica (TXT)", defaultextension=".txt", initialfile=default_name, filetypes=[("Text file", "*.txt")])
    if not save_path:
        return

    note = f"""
NOTA TÉCNICA
Herramienta: {APP_NAME} v{APP_VERSION}

Fecha/Hora: {meta['timestamp']}
Usuario: {meta['user']}
Equipo (Hostname): {meta['hostname']}
Sistema: {meta['os']}
Windows Version: {meta['windows_version']}
Privilegios admin: {meta['admin']}

Parámetro verificado:
 - Ruta de registro: HKLM\\{REG_PATH}
 - Valor: {REG_KEY_NAME} = {status_val}
 - Estado interpretado: {status_text}

Unidades removibles detectadas (al momento de generar la nota):
{os.linesep.join(usb_lines)}

Observaciones:
 - Esta nota técnica documenta acciones/estado de configuración relativos a control de escritura USB.
 - Para bitácora detallada, anexar el LOG exportado y su SHA256 correspondiente.
""".strip()

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(note + "\n")

        digest = sha256_file(save_path)
        sha_path = save_path + ".sha256"
        with open(sha_path, "w", encoding="utf-8") as f:
            f.write(f"{digest}  {os.path.basename(save_path)}\n")

        log(f"Nota técnica generada: {save_path}")
        log(f"SHA256 Nota: {digest}")
        messagebox.showinfo("Nota Técnica", f"Nota técnica generada.\n\nArchivo: {save_path}\nSHA256: {digest}\n\nSe generó: {sha_path}")
    except Exception as e:
        log(f"Error al generar nota técnica: {e}")
        messagebox.showerror("Nota Técnica", f"No se pudo generar la nota técnica: {e}")


def clear_log():
    terminal_widget.configure(state="normal")
    terminal_widget.delete("1.0", tk.END)
    terminal_widget.configure(state="disabled")
    log("Registro de procesos limpiado.")

# ============================================================
# SECCIÓN: CONFIGURACIÓN INICIAL DE LA INTERFAZ GRÁFICA
# Crea la ventana principal y configura tamaño, color base e icono.
# ============================================================
configure_windows_app_id()

root = tk.Tk()
root.title(f"{APP_NAME} v{APP_VERSION}")
root.geometry("820x840")
root.minsize(760, 810)
root.configure(bg=COLOR_BG)

# ============================================================
# SECCIÓN: CONFIGURACIÓN DE ICONO DE VENTANA
# Este icono aparece en la ventana, barra de tareas y Alt+Tab.
# Para PyInstaller, compilar agregando --add-data del archivo .ico.
# ============================================================
apply_window_icon(root)

# ============================================================
# SECCIÓN: MENÚ SUPERIOR
# Opciones: Ayuda, Administración y Exportación.
# ============================================================
menubar = Menu(root)
root.config(menu=menubar)

helpmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Ayuda", menu=helpmenu)
helpmenu.add_command(label="Acerca de...", command=show_about)

adminmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Administración", menu=adminmenu)
adminmenu.add_command(label="Reiniciar como Administrador", command=restart_as_admin)

exportmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Exportación", menu=exportmenu)
exportmenu.add_command(label="Exportar Log (TXT + SHA256)", command=export_log_txt)
exportmenu.add_command(label="Generar Nota Técnica (TXT + SHA256)", command=generate_technical_note)

# ============================================================
# SECCIÓN: ESTILO TTK
# Configuración visual para controles ttk, como Combobox.
# ============================================================
style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass
style.configure("TCombobox", padding=5, font=FONT_NORMAL)

# ============================================================
# SECCIÓN: CONTENEDOR PRINCIPAL
# Marco base donde se colocan todas las tarjetas de la interfaz.
# ============================================================
app = tk.Frame(root, bg=COLOR_BG)
app.pack(fill="both", expand=True, padx=22, pady=18)

# ============================================================
# SECCIÓN: ENCABEZADO PRINCIPAL
# Bloque superior de identidad de la aplicación.
# Se mantiene compacto para evitar cortes visuales en resoluciones pequeñas.
# ============================================================
header = tk.Frame(app, bg=COLOR_HEADER)
header.pack(fill="x")

# Contenedor izquierdo del encabezado: título y descripción.
header_left = tk.Frame(header, bg=COLOR_HEADER)
header_left.pack(side="left", fill="both", expand=True, padx=24, pady=22)

# Contenedor derecho del encabezado: botón GitHub.
header_right = tk.Frame(header, bg=COLOR_HEADER)
header_right.pack(side="right", padx=24, pady=22)

# Fila del título y nombre técnico corto.
title_row = tk.Frame(header_left, bg=COLOR_HEADER)
title_row.pack(anchor="w", fill="x")

tk.Label(
    title_row,
    text=f"{APP_NAME} v{APP_VERSION}",
    bg=COLOR_HEADER,
    fg="white",
    font=FONT_TITLE,
).pack(side="left")

tk.Label(
    title_row,
    text="  ·  USB Write Blocker",
    bg=COLOR_HEADER,
    fg="#dbeafe",
    font=("Segoe UI", 11, "bold"),
).pack(side="left", padx=(8, 0), pady=(5, 0))

# Descripción técnica corta.
tk.Label(
    header_left,
    text="Control de protección contra escritura USB mediante configuración segura del registro de Windows.",
    bg=COLOR_HEADER,
    fg="#e5e7eb",
    font=FONT_SUBTITLE,
    wraplength=610,
    justify="left",
).pack(anchor="w", pady=(14, 0))

# Recomendación compacta para que el encabezado no se corte.
tk.Label(
    header_left,
    text="Recomendación: active el bloqueador ANTES de conectar la unidad USB.",
    bg=COLOR_HEADER,
    fg="#fde68a",
    font=("Segoe UI", 10, "bold"),
    wraplength=610,
    justify="left",
).pack(anchor="w", pady=(8, 0))

# Botón para abrir el repositorio oficial.
repo_btn = tk.Button(header_right, text="GitHub", command=lambda: webbrowser.open(REPO_URL))
style_button(repo_btn, COLOR_BLUE, "white", COLOR_BLUE_HOVER)
repo_btn.pack()

if not is_admin():
    alert = tk.Frame(app, bg=COLOR_LIGHT_RED, highlightbackground="#fecaca", highlightthickness=1)
    alert.pack(fill="x", pady=(14, 0))
    tk.Label(
        alert,
        text="ATENCIÓN: Ejecute como administrador para funcionalidad completa.",
        bg=COLOR_LIGHT_RED,
        fg=COLOR_RED,
        font=("Segoe UI", 10, "bold"),
        padx=14,
        pady=10,
    ).pack(anchor="w")

# ============================================================
# SECCIÓN: ESTADO ACTUAL Y ACCIONES PRINCIPALES
# Muestra si la protección está activa y botones principales.
# ============================================================
status_actions = tk.Frame(app, bg=COLOR_BG)
status_actions.pack(fill="x", pady=(16, 0))

status_card, status_inner = make_card(status_actions, padx=18, pady=16)
status_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

tk.Label(status_inner, text="Estado actual", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SECTION).pack(anchor="w")

status_row = tk.Frame(status_inner, bg=COLOR_CARD)
status_row.pack(fill="x", pady=(10, 4))
status_indicator = tk.Frame(status_row, width=14, height=14, bg=COLOR_SUBTLE)
status_indicator.pack(side="left", padx=(0, 8))
status_indicator.pack_propagate(False)
status_value_label = tk.Label(status_row, text="CARGANDO...", bg=COLOR_CARD, fg=COLOR_BLUE, font=("Segoe UI", 17, "bold"))
status_value_label.pack(side="left")

status_description = tk.Label(status_inner, text="Verificando configuración del registro...", bg=COLOR_CARD, fg=COLOR_MUTED, font=FONT_NORMAL, justify="left", wraplength=340)
status_description.pack(anchor="w", pady=(4, 0))

actions_card, actions_inner = make_card(status_actions, padx=18, pady=16)
actions_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

tk.Label(actions_inner, text="Acciones principales", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SECTION).pack(anchor="w")

buttons_grid = tk.Frame(actions_inner, bg=COLOR_CARD)
buttons_grid.pack(fill="x", pady=(12, 0))

enable_button = tk.Button(buttons_grid, text="Activar Protección (ON)", command=lambda: set_write_protect(True))
style_button(enable_button, COLOR_BLUE, "white", COLOR_BLUE_HOVER)
enable_button.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))

disable_button = tk.Button(buttons_grid, text="Desactivar (OFF)", command=lambda: set_write_protect(False))
style_button(disable_button, COLOR_LIGHT_GRAY, COLOR_TEXT, "#d1d5db")
disable_button.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 8))

export_button = tk.Button(buttons_grid, text="Exportar Log", command=export_log_txt)
style_button(export_button, COLOR_LIGHT_GRAY, COLOR_TEXT, "#d1d5db")
export_button.grid(row=1, column=0, sticky="ew", padx=(0, 8))

note_top_btn = tk.Button(buttons_grid, text="Nota Técnica", command=generate_technical_note)
style_button(note_top_btn, COLOR_LIGHT_GRAY, COLOR_TEXT, "#d1d5db")
note_top_btn.grid(row=1, column=1, sticky="ew", padx=(8, 0))

buttons_grid.columnconfigure(0, weight=1)
buttons_grid.columnconfigure(1, weight=1)

# ============================================================
# SECCIÓN: VERIFICACIÓN USB
# Detecta unidades removibles y permite realizar prueba controlada de escritura.
# ============================================================
usb_card, usb_inner = make_card(app, padx=18, pady=16)
usb_card.pack(fill="x", pady=(14, 0))

usb_title_row = tk.Frame(usb_inner, bg=COLOR_CARD)
usb_title_row.pack(fill="x")
tk.Label(usb_title_row, text="Verificación USB", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SECTION).pack(side="left")
usb_count_label = tk.Label(usb_title_row, text="Pendiente de detección", bg=COLOR_CARD, fg=COLOR_SUBTLE, font=FONT_SMALL)
usb_count_label.pack(side="right")

tk.Label(usb_inner, text="Estado real / prueba controlada de escritura", bg=COLOR_CARD, fg=COLOR_SUBTLE, font=FONT_SMALL).pack(anchor="w", pady=(2, 10))

usb_row = tk.Frame(usb_inner, bg=COLOR_CARD)
usb_row.pack(fill="x")

tk.Label(usb_row, text="USB detectadas:", bg=COLOR_CARD, fg=COLOR_MUTED, font=FONT_NORMAL).pack(side="left", padx=(0, 8))
usb_combo = ttk.Combobox(usb_row, state="readonly", width=56)
usb_combo.pack(side="left", fill="x", expand=True, padx=(0, 10))

usb_refresh_btn = tk.Button(usb_row, text="Detectar USB", command=refresh_usb_list)
style_button(usb_refresh_btn, COLOR_BLUE, "white", COLOR_BLUE_HOVER)
usb_refresh_btn.pack(side="left")

usb_action_row = tk.Frame(usb_inner, bg=COLOR_CARD)
usb_action_row.pack(fill="x", pady=(12, 0))

usb_test_btn = tk.Button(usb_action_row, text="Probar bloqueo (escritura)", command=test_write_block)
style_button(usb_test_btn, COLOR_LIGHT_GRAY, COLOR_TEXT, "#d1d5db")
usb_test_btn.pack(side="left", padx=(0, 10))

note_btn = tk.Button(usb_action_row, text="Generar Nota Técnica", command=generate_technical_note)
style_button(note_btn, COLOR_LIGHT_GRAY, COLOR_TEXT, "#d1d5db")
note_btn.pack(side="left")

# ============================================================
# SECCIÓN: REGISTRO DE PROCESOS
# Consola visual donde se documentan las acciones realizadas por la herramienta.
# ============================================================
log_card, log_inner = make_card(app, padx=14, pady=12)
log_card.pack(fill="both", expand=True, pady=(14, 0))

log_header = tk.Frame(log_inner, bg=COLOR_CARD)
log_header.pack(fill="x", pady=(0, 8))
tk.Label(log_header, text="Registro de procesos", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SECTION).pack(side="left")

clear_btn = tk.Button(log_header, text="Limpiar log", command=clear_log)
style_button(clear_btn, COLOR_LIGHT_GRAY, COLOR_TEXT, "#d1d5db")
clear_btn.configure(font=FONT_SMALL, padx=10, pady=5)
clear_btn.pack(side="right")

terminal_widget = scrolledtext.ScrolledText(log_inner, wrap=tk.WORD, state="disabled", height=18, bg=COLOR_LOG_BG, fg=COLOR_LOG_FG, insertbackground=COLOR_LOG_FG, relief="flat", bd=0)
terminal_widget.pack(fill="both", expand=True)
terminal_widget.configure(font=FONT_MONO)
terminal_widget.tag_configure("stdout", foreground=COLOR_LOG_FG)
terminal_widget.tag_configure("stderr", foreground="#fecaca")

stdout_redirector = TextRedirector(terminal_widget, "stdout")
stderr_redirector = TextRedirector(terminal_widget, "stderr")
sys.stdout = stdout_redirector
sys.stderr = stderr_redirector

# ============================================================
# SECCIÓN: PIE DE VENTANA
# Mensaje de uso recomendado y botón de salida.
# ============================================================
footer = tk.Frame(app, bg=COLOR_BG)
footer.pack(fill="x", pady=(10, 0))

tk.Label(footer, text="Uso recomendado: activar protección antes de conectar la evidencia USB.", bg=COLOR_BG, fg=COLOR_SUBTLE, font=FONT_SMALL).pack(side="left")

exit_button = tk.Button(footer, text="Salir", command=root.quit)
style_button(exit_button, COLOR_LIGHT_GRAY, COLOR_TEXT, "#d1d5db")
exit_button.pack(side="right")

# ============================================================
# SECCIÓN: INICIALIZACIÓN
# Arranque de logs, verificación del estado y detección inicial de USB.
# ============================================================
log("Aplicación iniciada.")
meta = get_system_metadata()
log(f"Fecha y Hora: {meta['timestamp']}")
log(f"Usuario: {meta['user']} | Hostname: {meta['hostname']} | Admin: {meta['admin']}")
update_status_display()
refresh_usb_list()

root.mainloop()
#Actualización v1.1.0: rediseño de interfaz e integración de icono

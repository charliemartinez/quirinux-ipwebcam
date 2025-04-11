# ======================================================================
# File:       quirinux ipwebcam
# Author:     Charlie Martínez® <cmartinez@quirinux.org>
# License:    https://choosealicense.com/licenses/bsd-3-clause/
# Purpose:    Use 
# Supported:  Multi-distro (originally for Quirinux 2.0)
# ======================================================================

# Virtual camera to use a mobile phone as a webcam. 
#
# How to use
#
# First, download and install this app on your phone:
# https://play.google.com/store/apps/details?id=com.pas.webcam&hl=es&pli=1
#
# Then, launch the app and tap on “Start server” (at the bottom).
# After that, open my program and enter your phone’s IP address.
# It will load two modules (click accept), and finally it will notify
# you that the camera is connected (on your phone you'll also see 
# “video connections: 1”).
# 
# Now, you can select PhoneCam in Tahoma2D (press "Refresh" 
# if itnot appears).
#
# Copyright (c) 2019-2025 Charlie Martinez. All rights reserved.
# License: https://www.gnu.org/licenses/gpl-2.0.txt
# For permitted and unauthorized uses of the Quirinux trademark:
# Visit https://www.quirinux.org/aviso-legal


import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import socket
import os
import locale
import time
import threading

# Dark theme colors
DARK_BG = "#1e1e1e"
LIGHT_TEXT = "white"
BUTTON_BG = "#2c2c2c"
BUTTON_ACTIVE = "#444"
HIGHLIGHT_COLOR = "#c792ea"
FONT_FAMILY = "Ubuntu"

ffmpeg_process = None

try:
    locale.setlocale(locale.LC_ALL, '')
    current_lang = locale.getlocale()[0][:2]
except:
    current_lang = "en"


SUPPORTED_LANGS = {
    'en': "English", 'es': "Español", 'fr': "Français", 'de': "Deutsch", 'pt': "Português", 'gl': "Galego"
}

# Translations dictionary
translations = {
    "Quirinux IP Webcam": {
        "es": "Cámara IP Quirinux", "en": "Quirinux IP Webcam", "fr": "Webcam IP Quirinux",
        "de": "Quirinux IP-Webcam", "pt": "Webcam IP Quirinux", "gl": "Cámara IP Quirinux"
    },
    "(c) Charlie Martínez - BSD 3-Clause 'New'": {lang: "(c) Charlie Martínez - BSD 3-Clause 'New'" for lang in SUPPORTED_LANGS},
    "Mobile IP address:": {
        "es": "Dirección IP del móvil:", "en": "Mobile IP address:", "fr": "Adresse IP du mobile :",
        "de": "IP-Adresse des Handys:", "pt": "Endereço IP do celular:", "gl": "Enderezo IP do móbil:"
    },
    "Port (default: 8080):": {
        "es": "Puerto (por defecto: 8080):", "en": "Port (default: 8080):", "fr": "Port (défaut : 8080) :",
        "de": "Port (Standard: 8080):", "pt": "Porta (padrão: 8080):", "gl": "Porto (por defecto: 8080):"
    },
    "Connect camera": {
        "es": "Conectar cámara", "en": "Connect camera", "fr": "Connecter la caméra",
        "de": "Kamera verbinden", "pt": "Conectar câmera", "gl": "Conectar cámara"
    },
    "Stop": {
        "es": "Detener", "en": "Stop", "fr": "Arrêter", "de": "Stoppen", "pt": "Parar", "gl": "Deter"
    },
    "Exit": {
        "es": "Salir", "en": "Exit", "fr": "Quitter", "de": "Beenden", "pt": "Sair", "gl": "Saír"
    },
    "Waiting for connection...": {
        "es": "Esperando conexión...", "en": "Waiting for connection...", "fr": "En attente de connexion...",
        "de": "Warte auf Verbindung...", "pt": "Aguardando conexão...", "gl": "Agardando conexión..."
    },
    "Camera active on": {
        "es": "Cámara activa en", "en": "Camera active on", "fr": "Caméra active sur",
        "de": "Kamera aktiv auf", "pt": "Câmera ativa em", "gl": "Cámara activa en"
    },
    "Camera stopped": {
        "es": "Cámara detenida", "en": "Camera stopped", "fr": "Caméra arrêtée",
        "de": "Kamera gestoppt", "pt": "Câmera parada", "gl": "Cámara detida"
    },
    "Missing data": {
        "es": "Faltan datos", "en": "Missing data", "fr": "Données manquantes",
        "de": "Fehlende Daten", "pt": "Faltam dados", "gl": "Faltan datos"
    },
    "You must enter IP and port": {
        "es": "Debes ingresar IP y puerto", "en": "You must enter IP and port", "fr": "Vous devez entrer l'IP et le port",
        "de": "Bitte IP und Port eingeben", "pt": "Você deve inserir IP e porta", "gl": "Debes introducir IP e porto"
    },
    "Could not start ffmpeg: ": {
        "es": "No se pudo iniciar ffmpeg: ", "en": "Could not start ffmpeg: ", "fr": "Impossible de démarrer ffmpeg : ",
        "de": "ffmpeg konnte nicht gestartet werden: ", "pt": "Não foi possível iniciar o ffmpeg: ", "gl": "Non se puido iniciar ffmpeg: "
    },
    "Error": {
        "es": "Error", "en": "Error", "fr": "Erreur", "de": "Fehler", "pt": "Erro", "gl": "Erro"
    },
    "Language": {
        "es": "Idioma", "en": "Language", "fr": "Langue", "de": "Sprache", "pt": "Idioma", "gl": "Lingua"
    },
    "Loopback device not found. Please load v4l2loopback module.": {
        "es": "Dispositivo loopback no encontrado. Cargue el módulo v4l2loopback.",
        "en": "Loopback device not found. Please load v4l2loopback module.",
        "fr": "Périphérique loopback introuvable. Chargez le module v4l2loopback.",
        "de": "Loopback-Gerät nicht gefunden. Bitte v4l2loopback-Modul laden.",
        "pt": "Dispositivo loopback não encontrado. Carregue o módulo v4l2loopback.",
        "gl": "Dispositivo loopback non atopado. Cargue o módulo v4l2loopback."
    },
    "Check module": {
        "es": "Verificar módulo", "en": "Check module", "fr": "Vérifier le module",
        "de": "Modul prüfen", "pt": "Verificar módulo", "gl": "Verificar módulo"
    },
    "Module status": {
        "es": "Estado del módulo", "en": "Module status", "fr": "État du module",
        "de": "Modulstatus", "pt": "Status do módulo", "gl": "Estado do módulo"
    },
    "Module loaded in kernel": {
        "es": "Módulo cargado en el kernel", "en": "Module loaded in kernel", "fr": "Module chargé dans le noyau",
        "de": "Modul im Kernel geladen", "pt": "Módulo carregado no kernel", "gl": "Módulo cargado no kernel"
    },
    "Module not loaded in kernel": {
        "es": "Módulo no cargado en el kernel", "en": "Module not loaded in kernel", "fr": "Module non chargé dans le noyau",
        "de": "Modul nicht im Kernel geladen", "pt": "Módulo não carregado no kernel", "gl": "Módulo non cargado no kernel"
    },
    "Could not verify module status": {
        "es": "No se pudo verificar el estado del módulo", "en": "Could not verify module status", "fr": "Impossible de vérifier l'état du module",
        "de": "Modulstatus konnte nicht überprüft werden", "pt": "Não foi possível verificar o status do módulo", "gl": "Non se puido verificar o estado do módulo"
    },
    "Device found": {
        "es": "Dispositivo encontrado", "en": "Device found", "fr": "Périphérique trouvé",
        "de": "Gerät gefunden", "pt": "Dispositivo encontrado", "gl": "Dispositivo atopado"
    },
    "Device not found": {
        "es": "Dispositivo no encontrado", "en": "Device not found", "fr": "Périphérique non trouvé",
        "de": "Gerät nicht gefunden", "pt": "Dispositivo não encontrado", "gl": "Dispositivo non atopado"
    },
    "Configuration file found": {
        "es": "Archivo de configuración encontrado", "en": "Configuration file found", "fr": "Fichier de configuration trouvé",
        "de": "Konfigurationsdatei gefunden", "pt": "Arquivo de configuração encontrado", "gl": "Arquivo de configuración atopado"
    },
    "Configuration file not found": {
        "es": "Archivo de configuración no encontrado", "en": "Configuration file not found", "fr": "Fichier de configuration non trouvé",
        "de": "Konfigurationsdatei nicht gefunden", "pt": "Arquivo de configuração não encontrado", "gl": "Arquivo de configuración non atopado"
    },
    "Module in /etc/modules": {
        "es": "Módulo en /etc/modules", "en": "Module in /etc/modules", "fr": "Module dans /etc/modules",
        "de": "Modul in /etc/modules", "pt": "Módulo em /etc/modules", "gl": "Módulo en /etc/modules"
    },
    "Module not in /etc/modules": {
        "es": "Módulo no está en /etc/modules", "en": "Module not in /etc/modules", "fr": "Module absent de /etc/modules",
        "de": "Modul nicht in /etc/modules", "pt": "Módulo não está em /etc/modules", "gl": "Módulo non está en /etc/modules"
    },
    "Try to load module": {
        "es": "Intentar cargar módulo", "en": "Try to load module", "fr": "Essayer de charger le module",
        "de": "Versuche Modul zu laden", "pt": "Tentar carregar módulo", "gl": "Intentar cargar módulo"
    },
    "Module loaded successfully": {
        "es": "Módulo cargado correctamente", "en": "Module loaded successfully", "fr": "Module chargé avec succès",
        "de": "Modul erfolgreich geladen", "pt": "Módulo carregado com sucesso", "gl": "Módulo cargado correctamente"
    },
    "Failed to load module": {
        "es": "Error al cargar el módulo", "en": "Failed to load module", "fr": "Échec du chargement du module",
        "de": "Fehler beim Laden des Moduls", "pt": "Falha ao carregar o módulo", "gl": "Erro ao cargar o módulo"
    },
    "Creating virtual camera...": {
        "es": "Creando cámara virtual...", "en": "Creating virtual camera...", "fr": "Création de caméra virtuelle...",
        "de": "Erstelle virtuelle Kamera...", "pt": "Criando câmera virtual...", "gl": "Creando cámara virtual..."
    },
    "Advanced module options:": {
        "es": "Opciones avanzadas del módulo:", "en": "Advanced module options:", "fr": "Options avancées du module:",
        "de": "Erweiterte Moduloptionen:", "pt": "Opções avançadas do módulo:", "gl": "Opcións avanzadas do módulo:"
    },
    "Unload module first": {
        "es": "Descargar módulo primero", "en": "Unload module first", "fr": "Décharger le module d'abord",
        "de": "Modul zuerst entladen", "pt": "Descarregar módulo primeiro", "gl": "Descargar módulo primeiro"
    },
    "DO NOT CLOSE THIS WINDOW WHILE USING YOUR PHONE CAMERA": {
    "es": "NO CIERRES ESTA VENTANA\nMIENTRAS NECESITES USAR\nLA CÁMARA DE TU TELÉFONO",
    "en": "DO NOT CLOSE THIS WINDOW\nWHILE USING YOUR\nPHONE CAMERA",
    "fr": "NE FERMEZ PAS CETTE FENÊTRE\nPENDANT QUE VOUS UTILISEZ\nLA CAMÉRA DE VOTRE TÉLÉPHONE",
    "de": "FENSTER NICHT SCHLIESSEN,\nSOLANGE SIE DIE\nHANDYKAMERA VERWENDEN",
    "pt": "NÃO FECHE ESTA JANELA\nENQUANTO ESTIVER USANDO\nA CÂMERA DO CELULAR",
    "gl": "NON PECHES ESTA XANELA\nMENTRES USES A CÁMARA\nDO TEU TELÉFONO"
    }
}

# Common format definitions for better compatibility
RESOLUTIONS = [
    "640x480",  # VGA
    "1280x720", # 720p
    "1920x1080" # 1080p
]

def _(text):
    # Translate text based on current language
    if text in translations and current_lang in translations[text]:
        return translations[text][current_lang]
    return text

def change_language(lang):
    global current_lang
    current_lang = lang
    rebuild_gui()

# Improved module unloading
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Improved module unloading
def unload_v4l2loopback():
    try:
        subprocess.run(["sudo", "rmmod", "v4l2loopback"], capture_output=True, text=True)
        time.sleep(3)  # Give system more time to remove device
        return True
    except Exception as e:
        messagebox.showerror(_("Error"), str(e))
        return False

# Check if module is loaded and try to load it if not
def ensure_v4l2loopback_loaded():
    status_label.config(text=_("Creating virtual camera..."), fg=HIGHLIGHT_COLOR)
    root.update()
    
    # Unload the module first
    unload_v4l2loopback()
    time.sleep(3)
    
    # Specific configuration for guvcview (based on known working setups)
    try:
        # Simplest possible configuration
        result = subprocess.run(
            ["sudo", "modprobe", "v4l2loopback", "exclusive_caps=0"], 
            capture_output=True, text=True
        )
        time.sleep(5)
        
        # Check that there is a v4l2loopback device
        devices = []
        for i in range(0, 30):
            if os.path.exists(f"/dev/video{i}"):
                devices.append(f"/dev/video{i}")
        
        if result.returncode == 0 and devices:
            # Find out which device is v4l2loopback
            loopback_device = None
            try:
                for dev in devices:
                    info = subprocess.run(["v4l2-ctl", "--device", dev, "--info"], capture_output=True, text=True)
                    if "v4l2loopback" in info.stdout:
                        loopback_device = dev
                        break
            except:
                pass
            
            # If unable to identify, use highest available number
            if not loopback_device and devices:
                loopback_device = max(devices, key=lambda x: int(x.replace("/dev/video", "")))
            
            if loopback_device:
                # Ensure permissions
                subprocess.run(["sudo", "chmod", "666", loopback_device], capture_output=True)
                
                # Save device for later use
                global output_device
                output_device = loopback_device
                
                messagebox.showinfo(_("Module status"), _("Module loaded successfully") + f" - {loopback_device}")
                status_label.config(text=_("Waiting for connection..."), fg=HIGHLIGHT_COLOR)
                return True
            else:
                messagebox.showerror(_("Error"), _("Could not find v4l2loopback device"))
        else:
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                messagebox.showerror(_("Error"), _("Failed to load module") + ": " + error_msg)
            else:
                messagebox.showerror(_("Error"), _("No devices found"))
            status_label.config(text=_("Waiting for connection..."), fg=HIGHLIGHT_COLOR)
            return False
    except Exception as e:
        messagebox.showerror(_("Error"), str(e))
        status_label.config(text=_("Waiting for connection..."), fg=HIGHLIGHT_COLOR)
        return False

# Start ffmpeg and stream to the virtual device with improved compatibility
# Add this global variable at the top of the file
output_device = "/dev/video0"

def start_ffmpeg(ip, port):
    global ffmpeg_process, output_device
    
    # Ensure the module is properly loaded
    if not ensure_v4l2loopback_loaded():
        messagebox.showerror(_("Error"), _("Loopback device not found. Please load v4l2loopback module."))
        return

    # Check that the device exists
    if not os.path.exists(output_device):
        messagebox.showerror(_("Error"), f"Device {output_device} does not exist after loading module.")
        return

    url = f"http://{ip}:{port}/video"
    
    # Get selected resolution
    resolution = resolution_var.get()
    framerate = framerate_var.get()
    
    try:
        # Stop any existing process
        stop_ffmpeg()
        
        # FFmpeg command dramatically simplified for guvcview compatibility
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", url,
            "-pix_fmt", "yuv420p",
            "-f", "v4l2",
            output_device
        ]
        
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE)

        # Wait to check if ffmpeg starts correctly
        time.sleep(2)
        
        # Check if ffmpeg is still running
        if ffmpeg_process.poll() is not None:
            error = ffmpeg_process.stderr.read().decode('utf-8')
            raise Exception(f"FFmpeg error: {error}")
            
        status_label.config(text=f"✅ {_('Camera active on')} {output_device}", fg=HIGHLIGHT_COLOR)
        
        # Show information
        messagebox.showinfo(_("Camera connected"), 
                          _("Your phone camera is now available as webcam on") + 
                          f" {output_device}")
    except Exception as e:
        messagebox.showerror(_("Error"), _("Could not start ffmpeg: ") + str(e))
        if ffmpeg_process and ffmpeg_process.poll() is None:
            ffmpeg_process.terminate()
            ffmpeg_process = None
            
# Stop ffmpeg stream
def stop_ffmpeg():
    global ffmpeg_process
    if ffmpeg_process:
        ffmpeg_process.terminate()
        try:
            ffmpeg_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ffmpeg_process.kill()
        ffmpeg_process = None
        status_label.config(text="🛑 " + _("Camera stopped"), fg=LIGHT_TEXT)

def on_connect():
    ip = ip_entry.get().strip()
    port = port_entry.get().strip()
    if not ip or not port:
        messagebox.showwarning(_("Missing data"), _("You must enter IP and port"))
        return
    
    show_progress_and_connect(ip, port)
    
    # Always unload and reload the module for a clean setup
    if ensure_v4l2loopback_loaded():
        start_ffmpeg(ip, port)
    else:
        messagebox.showerror(_("Error"), _("Failed to prepare virtual camera device"))

def on_quit():
    stop_ffmpeg()
    root.destroy()

# Advanced module loading with specific parameters
def load_module_advanced():
    # Create a new window for advanced options
    adv_window = tk.Toplevel(root)
    adv_window.title(_("Advanced module options"))
    adv_window.configure(bg=DARK_BG)
    adv_window.geometry("400x350")
    
    # Add a checkbox to unload module first
    unload_var = tk.BooleanVar(value=True)
    unload_checkbox = tk.Checkbutton(adv_window, text=_("Unload module first"), 
                                    variable=unload_var, bg=DARK_BG, fg=LIGHT_TEXT,
                                    selectcolor=BUTTON_BG, activebackground=DARK_BG)
    unload_checkbox.pack(pady=10)
    
    # Add entry fields for common parameters
    tk.Label(adv_window, text=_("Device number:"), fg=LIGHT_TEXT, bg=DARK_BG).pack()
    device_nr = tk.Entry(adv_window, bg=BUTTON_BG, fg=LIGHT_TEXT)
    device_nr.insert(0, "20")
    device_nr.pack()
    
    tk.Label(adv_window, text=_("Card label:"), fg=LIGHT_TEXT, bg=DARK_BG).pack()
    card_label = tk.Entry(adv_window, bg=BUTTON_BG, fg=LIGHT_TEXT)
    card_label.insert(0, "PhoneCam")
    card_label.pack()
    
    # Additional options for better compatibility
    exclusive_var = tk.BooleanVar(value=True)
    exclusive_checkbox = tk.Checkbutton(adv_window, text="exclusive_caps=1", 
                                      variable=exclusive_var, bg=DARK_BG, fg=LIGHT_TEXT,
                                      selectcolor=BUTTON_BG, activebackground=DARK_BG)
    exclusive_checkbox.pack(pady=5)
    
    # Buffer option (important for compatibility)
    max_buffers_var = tk.BooleanVar(value=True)
    max_buffers_checkbox = tk.Checkbutton(adv_window, text="max_buffers=2", 
                                       variable=max_buffers_var, bg=DARK_BG, fg=LIGHT_TEXT,
                                       selectcolor=BUTTON_BG, activebackground=DARK_BG)
    max_buffers_checkbox.pack(pady=5)
    
    # announce_all_caps option (helps with compatibility)
    announce_caps_var = tk.BooleanVar(value=True)
    announce_caps_checkbox = tk.Checkbutton(adv_window, text="announce_all_caps=1", 
                                         variable=announce_caps_var, bg=DARK_BG, fg=LIGHT_TEXT,
                                         selectcolor=BUTTON_BG, activebackground=DARK_BG)
    announce_caps_checkbox.pack(pady=5)
    
    # Add apply button
    def apply_settings():
        if unload_var.get():
            unload_v4l2loopback()
            time.sleep(2)
        
        try:
            cmd = ["sudo", "modprobe", "v4l2loopback", 
                  f"video_nr={device_nr.get()}", 
                  f"card_label='{card_label.get()}'"]
            
            if exclusive_var.get():
                cmd.append("exclusive_caps=1")
                
            if max_buffers_var.get():
                cmd.append("max_buffers=2")
                
            if announce_caps_var.get():
                cmd.append("announce_all_caps=1")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            time.sleep(3)
            
            device_path = f"/dev/video{device_nr.get()}"
            if result.returncode == 0 and os.path.exists(device_path):
                messagebox.showinfo(_("Module status"), _("Module loaded successfully"))
            else:
                messagebox.showerror(_("Error"), _("Failed to load module") + 
                                    (f": {result.stderr}" if result.stderr else ""))
        except Exception as e:
            messagebox.showerror(_("Error"), str(e))
        
        adv_window.destroy()
    
    tk.Button(adv_window, text=_("Apply"), command=apply_settings, 
             bg=BUTTON_BG, fg=LIGHT_TEXT, activebackground=BUTTON_ACTIVE).pack(pady=20)

# Function to install v4l2loopback module if not installed
def install_v4l2loopback():
    try:
        # Check if the module exists
        result = subprocess.run(["modinfo", "v4l2loopback"], capture_output=True)
        if result.returncode == 0:
            messagebox.showinfo(_("Module status"), _("v4l2loopback module is already installed"))
            return
            
        # Install the module
        messagebox.showinfo(_("Installing Module"), _("This will install v4l2loopback module. Please enter your password when prompted."))
        
        if os.path.exists("/usr/bin/apt"):
            install_cmd = ["sudo", "apt", "install", "-y", "v4l2loopback-dkms"]
        elif os.path.exists("/usr/bin/dnf"):
            install_cmd = ["sudo", "dnf", "install", "-y", "v4l2loopback"]
        elif os.path.exists("/usr/bin/pacman"):
            install_cmd = ["sudo", "pacman", "-S", "--noconfirm", "v4l2loopback-dkms"]
        else:
            messagebox.showerror(_("Error"), _("Could not determine package manager. Please install v4l2loopback manually."))
            return
            
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            messagebox.showinfo(_("Success"), _("v4l2loopback module installed successfully"))
            # Load the module
            load_module()
        else:
            messagebox.showerror(_("Error"), _("Failed to install module") + f": {result.stderr}")
    except Exception as e:
        messagebox.showerror(_("Error"), str(e))

# Check module status and show detailed information
def check_module_status():
    status = ""
    
    # Check if module is installed
    try:
        modinfo = subprocess.run(["modinfo", "v4l2loopback"], capture_output=True)
        if modinfo.returncode == 0:
            status += "✅ " + _("Module is installed") + "\n"
        else:
            status += "❌ " + _("Module is not installed") + "\n"
            messagebox.showinfo(_("Module status"), status)
            if messagebox.askyesno(_("Install module"), _("Would you like to install the v4l2loopback module now?")):
                install_v4l2loopback()
            return
    except:
        status += "❓ " + _("Could not check module installation") + "\n"
    
    # Check if module is loaded in kernel
    try:
        lsmod = subprocess.check_output(["lsmod"], text=True)
        if "v4l2loopback" in lsmod:
            status += "✅ " + _("Module loaded in kernel") + "\n"
        else:
            status += "❌ " + _("Module not loaded in kernel") + "\n"
    except:
        status += "❓ " + _("Could not verify module status") + "\n"
    
    # Check if device exists
    output_device = "/dev/video20"
    if os.path.exists(output_device):
        status += "✅ " + _("Device found") + f": {output_device}\n"
    else:
        status += "❌ " + _("Device not found") + f": {output_device}\n"
    
    # List all available video devices
    video_devices = []
    for i in range(30):  # Buscar hasta video29
        if os.path.exists(f"/dev/video{i}"):
            video_devices.append(f"/dev/video{i}")
    
    if video_devices:
        status += "\n" + _("Available video devices") + ":\n"
        for dev in video_devices:
            status += f"- {dev}\n"
    
    # Show list of cameras detected by the system
    try:
        v4l2_devices = subprocess.check_output(["v4l2-ctl", "--list-devices"], text=True, stderr=subprocess.STDOUT)
        status += "\n" + _("System detected cameras") + ":\n"
        status += v4l2_devices
    except:
        status += "\n" + _("Could not list system cameras") + "\n"

    messagebox.showinfo(_("Module status"), status)
    
    # Offer actions depending on the status
    if not os.path.exists(output_device):
        if messagebox.askyesno(_("Load module"), _("Would you like to load the v4l2loopback module now?")):
            load_module()

# Try to load the module
def load_module():
    ensure_v4l2loopback_loaded()

# Build or rebuild the interface
# Build or rebuild the interface
def rebuild_gui():
    global resolution_var, framerate_var
    
    root.title(_("Quirinux IP Webcam"))
    root.configure(bg=DARK_BG)

    for widget in root.winfo_children():
        widget.destroy()

    menu_bar = tk.Menu(root, bg=BUTTON_BG, fg=LIGHT_TEXT, activebackground=BUTTON_ACTIVE)
    
    # Add language menu
    language_menu = tk.Menu(menu_bar, tearoff=0, bg=BUTTON_BG, fg=LIGHT_TEXT, activebackground=BUTTON_ACTIVE)
    for lang_code, lang_name in SUPPORTED_LANGS.items():
        language_menu.add_command(label=lang_name, command=lambda l=lang_code: change_language(l))
    menu_bar.add_cascade(label=_("Language"), menu=language_menu)
    
    root.config(menu=menu_bar)

    tk.Label(root, text=_("Quirinux IP Webcam"), font=(FONT_FAMILY, 14, "bold"), fg=HIGHLIGHT_COLOR, bg=DARK_BG).pack(pady=(5, 0))
    tk.Label(root, text=_("(c) Charlie Martínez - BSD 3-Clause 'New'"), font=(FONT_FAMILY, 9, "italic"), fg=LIGHT_TEXT, bg=DARK_BG).pack(pady=(0, 10))

    # Basic elements
    tk.Label(root, text=_("Mobile IP address:"), fg=LIGHT_TEXT, bg=DARK_BG, font=(FONT_FAMILY, 10)).pack()
    global ip_entry
    ip_entry = tk.Entry(root, bg=BUTTON_BG, fg=LIGHT_TEXT, insertbackground=LIGHT_TEXT, font=(FONT_FAMILY, 10))
    ip_entry.pack()
    if local_ip:
        parts = local_ip.split('.')
        parts[-1] = "133"
        ip_entry.insert(0, ".".join(parts))

    tk.Label(root, text=_("Port (default: 8080):"), fg=LIGHT_TEXT, bg=DARK_BG, font=(FONT_FAMILY, 10)).pack(pady=(10, 0))
    global port_entry
    port_entry = tk.Entry(root, bg=BUTTON_BG, fg=LIGHT_TEXT, insertbackground=LIGHT_TEXT, font=(FONT_FAMILY, 10))
    port_entry.pack()
    port_entry.insert(0, "8080")
    
    # Add video options for better compatibility
    # video_frame = tk.Frame(root, bg=DARK_BG)
    # video_frame.pack(pady=(10, 0))
    
    # Resolution options
    # tk.Label(video_frame, text=_("Resolution:"), fg=LIGHT_TEXT, bg=DARK_BG, font=(FONT_FAMILY, 10)).grid(row=0, column=0, padx=5)
    # resolution_var = tk.StringVar(value="640x480")
    # resolution_combo = ttk.Combobox(video_frame, textvariable=resolution_var, values=RESOLUTIONS, width=10)
    # resolution_combo.grid(row=0, column=1, padx=5)
    
    # Framerate options
    # tk.Label(video_frame, text=_("Framerate:"), fg=LIGHT_TEXT, bg=DARK_BG, font=(FONT_FAMILY, 10)).grid(row=0, column=2, padx=5)
    # framerate_var = tk.StringVar(value="30")
    # framerate_combo = ttk.Combobox(video_frame, textvariable=framerate_var, values=["15", "24", "25", "30"], width=5)
    # framerate_combo.grid(row=0, column=3, padx=5)

    # Style configuration for comboboxes
    # style = ttk.Style()
    # style.configure('TCombobox', fieldbackground=BUTTON_BG, background=DARK_BG, foreground=LIGHT_TEXT)
    # style.map('TCombobox', fieldbackground=[('readonly', BUTTON_BG)], 
    #        selectbackground=[('readonly', BUTTON_ACTIVE)],
    #        selectforeground=[('readonly', LIGHT_TEXT)])

    # Make comboboxes read-only
    # resolution_combo.state(['readonly'])
    # framerate_combo.state(['readonly'])

    # Main buttons frame (Connect and Stop) - larger buttons
    main_btn_frame = tk.Frame(root, bg=DARK_BG)
    main_btn_frame.pack(pady=(15, 5))

    # Make the main buttons larger
    main_button_width = 15
    main_button_height = 2

    connect_btn = tk.Button(main_btn_frame, text=_("Connect camera"), command=on_connect, 
                          bg=BUTTON_BG, fg=LIGHT_TEXT, activebackground=BUTTON_ACTIVE, 
                          font=(FONT_FAMILY, 12, "bold"), relief="flat",
                          width=main_button_width, height=main_button_height)
    connect_btn.pack(side="left", padx=10)

    stop_btn = tk.Button(main_btn_frame, text=_("Stop"), command=stop_ffmpeg,
                       bg=BUTTON_BG, fg=LIGHT_TEXT, activebackground=BUTTON_ACTIVE,
                       font=(FONT_FAMILY, 12, "bold"), relief="flat",
                       width=main_button_width, height=main_button_height)
    stop_btn.pack(side="left", padx=10)

    # exit_btn = tk.Button(root, text=_("Exit"), command=on_quit,
    #                  bg=BUTTON_BG, fg=LIGHT_TEXT, activebackground=BUTTON_ACTIVE,
    #                  font=(FONT_FAMILY, 9), relief="flat")
    # exit_btn.pack(pady=(10, 0))

    global status_label
    status_label = tk.Label(root, text=_("Waiting for connection..."), fg=HIGHLIGHT_COLOR, bg=DARK_BG, font=(FONT_FAMILY, 10, "italic"))
    status_label.pack(pady=(10, 0))
    
    global warning_label
    warning_label = tk.Label(root, text=_("DO NOT CLOSE THIS WINDOW WHILE USING YOUR PHONE CAMERA"), 
                             fg="yellow", bg=DARK_BG, font=(FONT_FAMILY, 9, "bold"))
    warning_label.pack(pady=(5, 0))
    
# Improved module initialization that will properly unload and reload if needed
def initialize_app():
    # Check if v4l2loopback module is installed
    try:
        modinfo = subprocess.run(["modinfo", "v4l2loopback"], capture_output=True)
        if modinfo.returncode != 0:
            return
    except:
        return

    # Do nothing else - we will load the module when needed

# App initialization
local_ip = get_local_ip()
root = tk.Tk()
root.geometry("460x350")  # Ligeramente más grande para acomodar nuevos controles
initialize_app()  # Try to load module on startup
rebuild_gui()

# Check module installation after showing the interface
def check_module_installation():
    try:
        modinfo = subprocess.run(["modinfo", "v4l2loopback"], capture_output=True)
        if modinfo.returncode != 0:
            if messagebox.askyesno(_("Module not installed"), 
                                 _("The v4l2loopback module is not installed. Would you like to install it now?")):
                install_v4l2loopback()
    except:
        pass
def show_progress_and_connect(ip, port):
    progress_window = tk.Toplevel(root)
    progress_window.title(_("Connecting camera"))
    progress_window.configure(bg=DARK_BG)
    progress_window.geometry("300x100")
    progress_window.transient(root)
    progress_window.grab_set()
    
    # Progress label
    progress_label = tk.Label(progress_window, text=_("Creating virtual camera..."), 
                            fg=LIGHT_TEXT, bg=DARK_BG, font=(FONT_FAMILY, 10))
    progress_label.pack(pady=(10, 5))
    
    # Progress bar
    progress_bar = ttk.Progressbar(progress_window, length=250, mode='determinate')
    progress_bar.pack(pady=5)
    
    # Function to update the bar
    def update_progress(step, message, progress=None):
        if progress_window.winfo_exists():
            progress_label.config(text=message)
            if progress is not None:
                progress_bar['value'] = progress
            progress_window.update()
    
    # Function for the background process
    def connect_process():
        try:
            # Step 1: Unload module
            update_progress(1, _("Unloading previous modules..."), 10)
            unload_v4l2loopback()
            time.sleep(1)
            
            # Step 2: Load module
            update_progress(2, _("Loading v4l2loopback module..."), 30)
            result = subprocess.run(
                ["sudo", "modprobe", "v4l2loopback", "exclusive_caps=0"], 
                capture_output=True, text=True
            )
            time.sleep(3)
            
            if result.returncode != 0:
                progress_window.destroy()
                messagebox.showerror(_("Error"), _("Failed to load module") + ": " + result.stderr)
                return
            
            # Step 3: Find device
            update_progress(3, _("Finding virtual device..."), 50)
            devices = []
            for i in range(0, 30):
                if os.path.exists(f"/dev/video{i}"):
                    devices.append(f"/dev/video{i}")
            
            loopback_device = None
            for dev in devices:
                try:
                    info = subprocess.run(["v4l2-ctl", "--device", dev, "--info"], capture_output=True, text=True)
                    if "v4l2loopback" in info.stdout:
                        loopback_device = dev
                        break
                except:
                    pass
            
            if not loopback_device and devices:
                loopback_device = max(devices, key=lambda x: int(x.replace("/dev/video", "")))
            
            if not loopback_device:
                progress_window.destroy()
                messagebox.showerror(_("Error"), _("Could not find v4l2loopback device"))
                return
            
            # Step 4: Set up permissions
            update_progress(4, _("Setting up permissions..."), 70)
            subprocess.run(["sudo", "chmod", "666", loopback_device], capture_output=True)
            global output_device
            output_device = loopback_device
            
            # Step 5: Start FFmpeg
            update_progress(5, _("Starting camera stream..."), 90)
            url = f"http://{ip}:{port}/video"
            
            # Stop any existing process
            stop_ffmpeg()
            
            # Simplified FFmpeg command
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", url,
                "-pix_fmt", "yuv420p",
                "-f", "v4l2",
                output_device
            ]
            
            global ffmpeg_process
            ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE)
            
            # Check if ffmpeg starts correctly
            time.sleep(2)

            if ffmpeg_process.poll() is not None:
                error = ffmpeg_process.stderr.read().decode('utf-8')
                progress_window.destroy()
                messagebox.showerror(_("Error"), _("Could not start ffmpeg: ") + error)
                return
            
            # Finish
            update_progress(6, _("Connection complete!"), 100)
            time.sleep(1)
            progress_window.destroy()
            
            # Update status and show success message
            status_label.config(text=f"✅ {_('Camera active on')} {output_device}", fg=HIGHLIGHT_COLOR)
            messagebox.showinfo(_("Camera connected"), 
                              _("Your phone camera is now available as webcam on") + 
                              f" {output_device}")
            
        except Exception as e:
            progress_window.destroy()
            messagebox.showerror(_("Error"), str(e))
            if ffmpeg_process and ffmpeg_process.poll() is None:
                ffmpeg_process.terminate()
                ffmpeg_process = None
    
    # Start the process in a separate thread
    import threading
    thread = threading.Thread(target=connect_process)
    thread.daemon = True
    thread.start()

root.after(1000, check_module_installation)
root.protocol("WM_DELETE_WINDOW", on_quit)
root.mainloop()

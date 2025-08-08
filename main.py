"""
Jarvis - Asistente Virtual de Escritorio
Módulo principal que inicializa la aplicación
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import webbrowser
import os
import subprocess
import json
from pathlib import Path
import datetime
from typing import Optional, List, Dict, Any

from core.file_manager import FileManager
from core.web_manager import WebManager  
from core.conversation_engine import ConversationEngine
from core.voice_manager import VoiceManager
from ui.main_window import MainWindow

class JarvisAssistant:
    """Clase principal del asistente virtual Jarvis"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        
        # Inicializar componentes
        self.file_manager = FileManager()
        self.web_manager = WebManager()
        self.conversation_engine = ConversationEngine()
        self.voice_manager = VoiceManager()
        
        # Configurar la interfaz
        self.main_window = MainWindow(self.root, self)
        
    def setup_main_window(self):
        """Configurar la ventana principal"""
        self.root.title("Jarvis - Asistente Virtual")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")
        
        # Configurar el icono de la ventana si existe
        try:
            self.root.iconbitmap("assets/jarvis_icon.ico")
        except:
            pass
    
    def run(self):
        """Ejecutar la aplicación principal"""
        print("🤖 Jarvis iniciando...")
        self.root.mainloop()

if __name__ == "__main__":
    app = JarvisAssistant()
    app.run()

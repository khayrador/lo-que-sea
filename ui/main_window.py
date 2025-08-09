"""
Interfaz principal de Jarvis
Maneja la ventana principal y la interacción con el usuario
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import threading
from typing import Dict, Any, Optional
from datetime import datetime

class MainWindow:
    """Clase para la ventana principal de Jarvis"""
    
    def __init__(self, root: tk.Tk, assistant):
        self.root = root
        self.assistant = assistant
        
        # Variables de estado
        self.is_voice_mode = False
        self.current_theme = "dark"
        
        # Configurar estilos
        self.setup_styles()
        
        # Crear interfaz
        self.create_interface()
        
        # Configurar eventos
        self.setup_events()
        
        # Mensaje de bienvenida
        self.add_message("Jarvis", "¡Hola! Soy Jarvis, tu asistente virtual. ¿En qué puedo ayudarte?", "assistant")
    
    def setup_styles(self):
        """Configurar estilos de la interfaz"""
        
        # Colores modernos y vibrantes
        self.colors = {
            "bg_primary": "#1a1a2e",
            "bg_secondary": "#16213e",
            "bg_tertiary": "#0f3460",
            "bg_card": "#16213e",
            "text_primary": "#eee",
            "text_secondary": "#bbb",
            "accent": "#00d4ff",
            "accent_hover": "#00b8e6",
            "success": "#00ff88",
            "warning": "#ffaa00",
            "error": "#ff4757",
            "voice_active": "#ff6b6b",
            "voice_inactive": "#74b9ff"
        }
        
        # Variables de estado visual
        self.is_voice_active = False
        self.voice_animation_id = None
        
        # Configurar estilo ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos personalizados modernos
        style.configure("Custom.TButton",
                       background=self.colors["accent"],
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none",
                       relief="flat",
                       padding=(15, 8))
        
        style.map("Custom.TButton",
                 background=[('active', self.colors["accent_hover"]),
                           ('pressed', '#0099cc')])
        
        # Estilo para botón de voz
        style.configure("Voice.TButton",
                       background=self.colors["voice_inactive"],
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none",
                       relief="flat",
                       padding=(20, 10))
        
        style.map("Voice.TButton",
                 background=[('active', self.colors["voice_active"])])
        
        # Estilo para botones de acción
        style.configure("Action.TButton",
                       background=self.colors["success"],
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none",
                       relief="flat",
                       padding=(12, 6))
    
    def create_interface(self):
        """Crear la interfaz principal moderna y vibrante"""
        
        # Marco principal con gradiente visual
        main_frame = tk.Frame(self.root, bg=self.colors["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header con diseño moderno
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_secondary"], relief="flat", bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Título con efecto visual
        title_frame = tk.Frame(header_frame, bg=self.colors["bg_secondary"])
        title_frame.pack(fill=tk.X, padx=20, pady=15)
        
        title_label = tk.Label(title_frame, 
                              text="🤖 J.A.R.V.I.S",
                              font=("Segoe UI", 22, "bold"),
                              bg=self.colors["bg_secondary"],
                              fg=self.colors["accent"])
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(title_frame,
                                 text="Asistente Virtual Inteligente",
                                 font=("Segoe UI", 10, "italic"),
                                 bg=self.colors["bg_secondary"],
                                 fg=self.colors["text_secondary"])
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Indicador de estado con animación
        self.status_indicator = tk.Label(title_frame,
                                        text="●",
                                        font=("Segoe UI", 16),
                                        bg=self.colors["bg_secondary"],
                                        fg=self.colors["success"])
        self.status_indicator.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Frame superior para controles principales
        controls_main_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        controls_main_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Panel de control de voz destacado
        voice_panel = tk.Frame(controls_main_frame, bg=self.colors["bg_card"], relief="flat", bd=0)
        voice_panel.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        voice_title = tk.Label(voice_panel,
                              text="🎤 Control de Voz",
                              font=("Segoe UI", 12, "bold"),
                              bg=self.colors["bg_card"],
                              fg=self.colors["accent"])
        voice_title.pack(pady=(10, 5))
        
        # Botones de voz con mejor diseño
        voice_buttons_frame = tk.Frame(voice_panel, bg=self.colors["bg_card"])
        voice_buttons_frame.pack(pady=(0, 15))
        
        self.voice_button = ttk.Button(voice_buttons_frame,
                                      text="🎤 Escuchar",
                                      style="Voice.TButton",
                                      command=self.toggle_voice_mode)
        self.voice_button.pack(side=tk.LEFT, padx=5)
        
        self.conversation_button = ttk.Button(voice_buttons_frame,
                                            text="💬 Conversar",
                                            style="Voice.TButton",
                                            command=self.start_conversation_mode)
        self.conversation_button.pack(side=tk.LEFT, padx=5)
        
        # Panel de acciones rápidas
        actions_panel = tk.Frame(controls_main_frame, bg=self.colors["bg_card"], relief="flat", bd=0)
        actions_panel.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        actions_title = tk.Label(actions_panel,
                               text="⚡ Acciones Rápidas",
                               font=("Segoe UI", 12, "bold"),
                               bg=self.colors["bg_card"],
                               fg=self.colors["accent"])
        actions_title.pack(pady=(10, 5))
        
        # Botones de acción con iconos
        actions_buttons_frame = tk.Frame(actions_panel, bg=self.colors["bg_card"])
        actions_buttons_frame.pack(pady=(0, 15))
        
        # Fila 1 de botones
        actions_row1 = tk.Frame(actions_buttons_frame, bg=self.colors["bg_card"])
        actions_row1.pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_row1, text="📁 Archivos", style="Action.TButton",
                  command=self.open_file_manager).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(actions_row1, text="🌐 Web", style="Action.TButton",
                  command=self.open_web_controls).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(actions_row1, text="🔍 Buscar", style="Action.TButton",
                  command=self.focus_input).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(actions_row1, text="❓ Ayuda", style="Action.TButton",
                  command=self.show_help).pack(side=tk.LEFT, padx=3)
        
        # Fila 2 de botones
        actions_row2 = tk.Frame(actions_buttons_frame, bg=self.colors["bg_card"])
        actions_row2.pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_row2, text="📊 Estadísticas", style="Action.TButton",
                  command=self.show_stats).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(actions_row2, text="⚙️ Config", style="Action.TButton",
                  command=self.open_settings).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(actions_row2, text="💡 Ejemplos", style="Action.TButton",
                  command=self.show_examples).pack(side=tk.LEFT, padx=3)
        control_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones de control
        self.create_control_buttons(control_frame)
        
        # Área de conversación
        self.create_chat_area(main_frame)
        
        # Área de entrada
        self.create_input_area(main_frame)
        
        # Barra de estado
        self.create_status_bar(main_frame)
    
    def create_control_buttons(self, parent):
        """Crear botones de control"""
        
        # Frame izquierdo para botones principales
        left_frame = tk.Frame(parent, bg=self.colors["bg_primary"])
        left_frame.pack(side=tk.LEFT)
        
        # Botón de voz
        self.voice_button = ttk.Button(left_frame,
                                      text="🎤 Voz",
                                      style="Custom.TButton",
                                      command=self.toggle_voice_mode)
        self.voice_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón de archivos
        files_button = ttk.Button(left_frame,
                                 text="📁 Archivos",
                                 style="Custom.TButton",
                                 command=self.open_file_manager)
        files_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón de micrófono
        mic_button = ttk.Button(left_frame,
                               text="�️ Micrófono",
                               style="Custom.TButton",
                               command=self.start_voice_listening)
        # Botón de web
        web_button = ttk.Button(left_frame,
                               text="🌐 Web",
                               style="Custom.TButton",
                               command=self.open_web_controls)
        web_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame derecho para configuración
        right_frame = tk.Frame(parent, bg=self.colors["bg_primary"])
        right_frame.pack(side=tk.RIGHT)
        
        # Botón de ayuda
        help_button = ttk.Button(right_frame,
                                text="❓ Ayuda",
                                style="Custom.TButton",
                                command=self.show_help)
        help_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botón de configuración
        config_button = ttk.Button(right_frame,
                                  text="⚙️ Config",
                                  style="Custom.TButton",
                                  command=self.open_settings)
        config_button.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_chat_area(self, parent):
        """Crear área de chat moderna e interactiva"""
        
        # Frame del chat con diseño moderno
        chat_container = tk.Frame(parent, bg=self.colors["bg_primary"])
        chat_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Header del chat
        chat_header = tk.Frame(chat_container, bg=self.colors["bg_card"], height=40)
        chat_header.pack(fill=tk.X, padx=5, pady=(0, 5))
        chat_header.pack_propagate(False)
        
        chat_title = tk.Label(chat_header,
                             text="💬 Conversación con J.A.R.V.I.S",
                             font=("Segoe UI", 11, "bold"),
                             bg=self.colors["bg_card"],
                             fg=self.colors["accent"])
        chat_title.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Indicador de actividad
        self.activity_indicator = tk.Label(chat_header,
                                          text="💤 Inactivo",
                                          font=("Segoe UI", 9),
                                          bg=self.colors["bg_card"],
                                          fg=self.colors["text_secondary"])
        self.activity_indicator.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Área de chat principal
        chat_frame = tk.Frame(chat_container, bg=self.colors["bg_secondary"], relief="flat", bd=0)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Área de texto del chat mejorada
        self.chat_area = scrolledtext.ScrolledText(chat_frame,
                                                  wrap=tk.WORD,
                                                  bg=self.colors["bg_tertiary"],
                                                  fg=self.colors["text_primary"],
                                                  font=("Segoe UI", 11),
                                                  state=tk.DISABLED,
                                                  insertbackground=self.colors["accent"],
                                                  relief="flat",
                                                  bd=0,
                                                  padx=15,
                                                  pady=10,
                                                  selectbackground=self.colors["accent"],
                                                  selectforeground="white")
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar tags para diferentes tipos de mensajes con estilos modernos
        self.chat_area.tag_configure("user", 
                                    foreground=self.colors["accent"],
                                    font=("Segoe UI", 11, "bold"))
        
        self.chat_area.tag_configure("assistant", 
                                    foreground=self.colors["success"],
                                    font=("Segoe UI", 11, "bold"))
        
        self.chat_area.tag_configure("voice_user",
                                    foreground=self.colors["warning"],
                                    font=("Segoe UI", 11, "bold"))
        
        self.chat_area.tag_configure("system", 
                                    foreground=self.colors["text_secondary"],
                                    font=("Segoe UI", 10, "italic"))
        
        self.chat_area.tag_configure("error", 
                                    foreground=self.colors["error"],
                                    font=("Segoe UI", 10, "bold"))
        
        self.chat_area.tag_configure("timestamp", 
                                    foreground=self.colors["text_secondary"],
                                    font=("Segoe UI", 9))
        
        self.chat_area.tag_configure("highlight",
                                    background=self.colors["bg_card"],
                                    foreground=self.colors["text_primary"])
        
        # Mensaje de bienvenida
        self.add_welcome_message()
    
    def create_input_area(self, parent):
        """Crear área de entrada moderna"""
        
        # Frame contenedor de entrada
        input_container = tk.Frame(parent, bg=self.colors["bg_primary"])
        input_container.pack(fill=tk.X, pady=(0, 15))
        
        # Panel de entrada con diseño moderno
        input_panel = tk.Frame(input_container, bg=self.colors["bg_card"], relief="flat", bd=0)
        input_panel.pack(fill=tk.X, padx=5)
        
        # Header del input
        input_header = tk.Frame(input_panel, bg=self.colors["bg_card"])
        input_header.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        input_title = tk.Label(input_header,
                              text="💭 Escribe tu mensaje",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.colors["bg_card"],
                              fg=self.colors["accent"])
        input_title.pack(side=tk.LEFT)
        
        # Indicador de estado del input
        self.input_status = tk.Label(input_header,
                                    text="✍️ Listo para escribir",
                                    font=("Segoe UI", 9),
                                    bg=self.colors["bg_card"],
                                    fg=self.colors["text_secondary"])
        self.input_status.pack(side=tk.RIGHT)
        
        # Frame de entrada principal
        entry_frame = tk.Frame(input_panel, bg=self.colors["bg_card"])
        entry_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Campo de entrada mejorado
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(entry_frame,
                             textvariable=self.entry_var,
                             bg=self.colors["bg_tertiary"],
                             fg=self.colors["text_primary"],
                             font=("Segoe UI", 12),
                             insertbackground=self.colors["accent"],
                             relief="flat",
                             bd=0,
                             highlightthickness=2,
                             highlightcolor=self.colors["accent"],
                             highlightbackground=self.colors["bg_tertiary"])
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        
        # Botones de acción
        buttons_frame = tk.Frame(entry_frame, bg=self.colors["bg_card"])
        buttons_frame.pack(side=tk.RIGHT)
        
        # Botón de envío principal
        self.send_button = ttk.Button(buttons_frame,
                                     text="🚀 Enviar",
                                     style="Custom.TButton",
                                     command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=2)
        
        # Botón de limpieza
        clear_button = ttk.Button(buttons_frame,
                                 text="🗑️",
                                 style="Action.TButton",
                                 command=self.clear_input)
        clear_button.pack(side=tk.LEFT, padx=2)
        
        # Configurar eventos del entry
        self.entry.bind("<Return>", lambda e: self.send_message())
        self.entry.bind("<KeyPress>", self.on_key_press)
        self.entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.entry.bind("<FocusOut>", self.on_entry_focus_out)
        
        # Sugerencias rápidas
        suggestions_frame = tk.Frame(input_panel, bg=self.colors["bg_card"])
        suggestions_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        suggestions_label = tk.Label(suggestions_frame,
                                   text="💡 Sugerencias:",
                                   font=("Segoe UI", 9, "bold"),
                                   bg=self.colors["bg_card"],
                                   fg=self.colors["text_secondary"])
        suggestions_label.pack(side=tk.LEFT)
        
        # Botones de sugerencias
        suggestions = ["¿Qué hora es?", "Buscar archivos", "Analizar web", "Conversación por voz"]
        for suggestion in suggestions:
            btn = tk.Button(suggestions_frame,
                          text=suggestion,
                          font=("Segoe UI", 8),
                          bg=self.colors["bg_tertiary"],
                          fg=self.colors["text_secondary"],
                          relief="flat",
                          bd=0,
                          padx=8,
                          pady=2,
                          command=lambda s=suggestion: self.insert_suggestion(s))
            btn.pack(side=tk.LEFT, padx=2)
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_button_hover(b, False))
    
    def create_status_bar(self, parent):
        """Crear barra de estado"""
        
        self.status_frame = tk.Frame(parent, bg=self.colors["bg_tertiary"], relief=tk.SUNKEN, bd=1)
        self.status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(self.status_frame,
                                    text="Listo",
                                    bg=self.colors["bg_tertiary"],
                                    fg=self.colors["text_secondary"],
                                    font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Indicadores de estado
        self.voice_indicator = tk.Label(self.status_frame,
                                       text="🔇",
                                       bg=self.colors["bg_tertiary"],
                                       fg=self.colors["text_secondary"])
        self.voice_indicator.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def setup_events(self):
        """Configurar eventos"""
        
        # Enter para enviar mensaje
        self.entry.bind('<Return>', lambda e: self.send_message())
        
        # Foco inicial en el campo de entrada
        self.entry.focus()
    
    def send_message(self):
        """Enviar mensaje del usuario"""
        
        message = self.entry_var.get().strip()
        if not message:
            return
        
        # Limpiar entrada
        self.entry_var.set("")
        
        # Mostrar mensaje del usuario
        self.add_message("Usuario", message, "user")
        
        # Procesar mensaje en hilo separado
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
    
    def process_message(self, message: str):
        """Procesar mensaje del usuario"""
        
        try:
            # Actualizar estado
            self.update_status("Procesando...")
            
            # Procesar con el motor de conversación
            response = self.assistant.conversation_engine.process_message(message)
            
            # Manejar diferentes tipos de respuesta
            if response["type"] == "command":
                self.handle_command(response)
            elif response["type"] == "response":
                self.add_message("Jarvis", response["content"], "assistant")
                
                # Reproducir respuesta por voz si está habilitado
                if self.is_voice_mode and self.assistant.voice_manager.tts_enabled:
                    self.assistant.voice_manager.speak(response["content"])
            
            self.update_status("Listo")
            
        except Exception as e:
            error_msg = f"Error procesando mensaje: {str(e)}"
            self.add_message("Sistema", error_msg, "error")
            self.update_status("Error")
    
    def handle_command(self, command_response: Dict[str, Any]):
        """Manejar comandos específicos con funcionalidades mejoradas"""
        
        command = command_response.get("command", "")
        parameter = command_response.get("parameter", "")
        
        # Agregar confirmación por voz
        self.confirm_voice_command(command, parameter)
        
        try:
            if command == "buscar_archivo":
                self.search_files(parameter)
            elif command == "buscar_archivo_inteligente":
                self.smart_search_files(parameter)
            elif command == "buscar_por_categoria":
                self.search_files_by_category(parameter)
            elif command == "buscar_en_contenido":
                self.search_in_file_content(parameter)
            elif command == "abrir_archivo":
                self.open_file(parameter)
            elif command == "crear_archivo":
                self.create_file(parameter)
            elif command == "abrir_web":
                self.open_website(parameter)
            elif command == "buscar_web":
                self.search_web(parameter)
            elif command == "analizar_web":
                self.analyze_webpage(parameter)
            elif command == "buscar_analizar":
                # Primero buscar, luego ofrecer analizar
                self.search_and_analyze(parameter)
            elif command == "escuchar_microfono":
                self.start_voice_listening()
            elif command == "conversacion_continua":
                self.start_conversation_mode()
            else:
                self.add_message("Jarvis", command_response.get("content", "Comando no reconocido"), "assistant")
                
        except Exception as e:
            self.add_message("Sistema", f"Error ejecutando comando: {str(e)}", "error")
    
    def search_files(self, query: str):
        """Buscar archivos"""
        if not query:
            self.add_message("Jarvis", "Por favor especifica qué archivo buscar", "assistant")
            return
            
        results = self.assistant.file_manager.search_files(query, max_results=10)
        
        if results:
            response = f"Encontré {len(results)} archivos:\n\n"
            for i, file_info in enumerate(results, 1):
                response += f"{i}. {file_info['name']} ({file_info['parent']})\n"
            
            self.add_message("Jarvis", response, "assistant")
        else:
            self.add_message("Jarvis", f"No encontré archivos con '{query}'", "assistant")
    
    def open_file(self, filename: str):
        """Abrir archivo"""
        if not filename:
            # Abrir diálogo de archivo
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo",
                filetypes=[("Todos los archivos", "*.*")]
            )
            if file_path:
                self.show_file_content(file_path)
        else:
            # Buscar archivo por nombre
            results = self.assistant.file_manager.search_files(filename, max_results=1)
            if results:
                self.show_file_content(results[0]["path"])
            else:
                self.add_message("Jarvis", f"No encontré el archivo '{filename}'", "assistant")
    
    def show_file_content(self, file_path: str):
        """Mostrar contenido de archivo"""
        file_info = self.assistant.file_manager.read_file(file_path)
        
        if "error" in file_info:
            self.add_message("Sistema", file_info["error"], "error")
            return
        
        # Crear ventana para mostrar contenido
        content_window = tk.Toplevel(self.root)
        content_window.title(f"Archivo: {file_info['name']}")
        content_window.geometry("800x600")
        content_window.configure(bg=self.colors["bg_primary"])
        
        # Área de texto
        text_area = scrolledtext.ScrolledText(content_window,
                                             wrap=tk.WORD,
                                             bg=self.colors["bg_secondary"],
                                             fg=self.colors["text_primary"],
                                             font=("Consolas", 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insertar contenido
        text_area.insert(tk.END, file_info["content"])
        text_area.config(state=tk.DISABLED)
        
        self.add_message("Jarvis", f"Abriendo archivo: {file_info['name']}", "assistant")
    
    def create_file(self, filename: str):
        """Crear nuevo archivo"""
        if not filename:
            filename = simpledialog.askstring("Nuevo archivo", "Nombre del archivo:")
            
        if filename:
            content = simpledialog.askstring("Contenido", "Contenido inicial (opcional):", initialvalue="")
            result = self.assistant.file_manager.write_file(filename, content or "")
            
            if result["success"]:
                self.add_message("Jarvis", f"Archivo '{filename}' creado exitosamente", "assistant")
            else:
                self.add_message("Sistema", result["error"], "error")
    
    def open_website(self, url: str):
        """Abrir sitio web"""
        if not url:
            url = simpledialog.askstring("Abrir sitio", "URL del sitio web:")
            
        if url:
            result = self.assistant.web_manager.open_url(url)
            if result["success"]:
                self.add_message("Jarvis", f"Abriendo: {url}", "assistant")
            else:
                self.add_message("Sistema", result["error"], "error")
    
    def search_web(self, query: str):
        """Buscar en web"""
        if not query:
            query = simpledialog.askstring("Búsqueda web", "¿Qué quieres buscar?")
            
        if query:
            result = self.assistant.web_manager.search_web(query)
            if result["success"]:
                self.add_message("Jarvis", f"Buscando: {query}", "assistant")
            else:
                self.add_message("Sistema", result["error"], "error")
    
    def analyze_webpage(self, url: str):
        """Analizar página web"""
        if not url:
            url = simpledialog.askstring("Analizar página", "URL de la página web:")
            
        if url:
            self.update_status("Analizando página web...")
            
            # Ejecutar análisis en hilo separado
            def analyze_async():
                try:
                    result = self.assistant.web_manager.get_page_summary(url)
                    
                    if result["success"]:
                        summary = result["summary"]
                        
                        # Crear reporte detallado
                        report = f"""
🔍 **Análisis de {url}**

📋 **Información básica:**
• Título: {summary['title']}
• Descripción: {summary['description'][:100]}{'...' if len(summary['description']) > 100 else ''}
• Tiempo de carga: {summary['load_time']}
• Seguridad: {'🔒 Segura (HTTPS)' if summary['is_secure'] else '⚠️ No segura (HTTP)'}

🎥 **Contenido multimedia:**
• {'✅ Contiene videos' if summary['has_videos'] else '❌ No contiene videos'}
• Cantidad de videos: {summary['video_count']}

💻 **Tecnologías detectadas:**
• {summary['technologies_summary']}

🔐 **Puntuación de seguridad:**
• {summary['security_score']}

¿Necesitas un análisis más detallado de algún aspecto?
                        """
                        
                        self.add_message("Jarvis", report.strip(), "assistant")
                        
                        # Información adicional sobre videos si los hay
                        if summary['has_videos']:
                            full_analysis = result.get("full_analysis", {})
                            videos = full_analysis.get("media", {}).get("videos", [])
                            
                            if videos:
                                video_info = "\n🎬 **Videos encontrados:**\n"
                                for i, video in enumerate(videos[:3], 1):  # Máximo 3 videos
                                    video_info += f"• {video['type']}: {video['url'][:50]}...\n"
                                
                                self.add_message("Jarvis", video_info, "assistant")
                        
                    else:
                        error_msg = result['error']
                        suggestion = result.get('suggestion', '')
                        
                        if suggestion:
                            full_error = f"❌ {error_msg}\n\n💡 {suggestion}"
                        else:
                            full_error = f"❌ {error_msg}"
                        
                        self.add_message("Sistema", full_error, "error")
                        
                except Exception as e:
                    self.add_message("Sistema", f"Error en análisis: {str(e)}", "error")
                finally:
                    self.update_status("Listo")
            
            thread = threading.Thread(target=analyze_async, daemon=True)
            thread.start()
    
    def search_and_analyze(self, query: str):
        """Buscar y ofrecer análisis"""
        if not query:
            query = simpledialog.askstring("Búsqueda", "¿Qué quieres buscar?")
            
        if query:
            # Realizar búsqueda
            result = self.assistant.web_manager.search_web(query)
            if result["success"]:
                response = f"🔍 Realizando búsqueda de '{query}' en Google...\n\n"
                response += "¿Te gustaría que analice algún sitio web específico relacionado con tu búsqueda?\n"
                response += "Puedes decirme: 'analizar [sitio.com]'"
                
                self.add_message("Jarvis", response, "assistant")
            else:
                self.add_message("Sistema", result["error"], "error")
    
    def start_voice_listening(self):
        """Iniciar escucha por micrófono con interfaz mejorada"""
        if not self.assistant.voice_manager.recognition_enabled:
            self.add_message("Sistema", "❌ Reconocimiento de voz no disponible. Instala: pip install SpeechRecognition pyaudio", "error")
            return
        
        # Confirmación de que está escuchando
        self.voice_feedback("Te estoy escuchando, habla ahora")
        self.start_voice_animation()
        self.update_status("🎤 Escuchando...")
        
        def listen_async():
            try:
                result = self.assistant.voice_manager.listen_once(timeout=10)
                
                if result["success"]:
                    recognized_text = result["text"]
                    # Confirmación de que se escuchó
                    self.voice_feedback(f"Te escuché decir: {recognized_text}")
                    
                    # Mostrar el comando de voz en la conversación con estilo especial
                    self.add_message("👤 Usuario (Voz)", f"🎤 \"{recognized_text}\"", "voice_user")
                    
                    # Procesar el comando reconocido
                    threading.Thread(target=self.process_message, args=(recognized_text,), daemon=True).start()
                    
                else:
                    error_msg = result.get('error', 'Error desconocido')
                    suggestion = result.get('suggestion', '')
                    full_error = f"❌ {error_msg}"
                    if suggestion:
                        full_error += f"\n💡 Sugerencia: {suggestion}"
                    
                    self.add_message("Sistema", full_error, "error")
                    # Confirmación de error por voz
                    self.voice_feedback("No pude escucharte correctamente, intenta de nuevo")
                    
            except Exception as e:
                self.add_message("Sistema", f"❌ Error en reconocimiento de voz: {str(e)}", "error")
            finally:
                self.stop_voice_animation()
                self.update_status("Listo")
        
        thread = threading.Thread(target=listen_async, daemon=True)
        thread.start()
    
    def toggle_voice_mode(self):
        """Alternar modo de voz mejorado"""
        self.is_voice_mode = not self.is_voice_mode
        
        if self.is_voice_mode:
            self.voice_button.configure(text="🎤 Activo")
            self.update_activity_indicator("Modo voz activo", True)
            self.add_message("Sistema", "✅ Modo de voz activado - Las respuestas se reproducirán por audio", "system")
        else:
            self.voice_button.configure(text="🎤 Escuchar")  
            self.update_activity_indicator("Inactivo", False)
            self.add_message("Sistema", "⏸️ Modo de voz desactivado", "system")
    
    def open_file_manager(self):
        """Abrir gestor de archivos mejorado con funcionalidad completa"""
        # Crear ventana del gestor de archivos
        file_window = tk.Toplevel(self.root)
        file_window.title("📁 Gestor de Archivos - J.A.R.V.I.S")
        file_window.geometry("800x600")
        file_window.configure(bg=self.colors["bg_primary"])
        file_window.resizable(True, True)
        
        # Frame principal
        main_frame = tk.Frame(file_window, bg=self.colors["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header del gestor
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_card"], relief="flat", bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(header_frame,
                              text="📁 Gestor de Archivos Inteligente",
                              font=("Segoe UI", 16, "bold"),
                              bg=self.colors["bg_card"],
                              fg=self.colors["accent"])
        title_label.pack(pady=15)
        
        # Frame de búsqueda
        search_frame = tk.Frame(main_frame, bg=self.colors["bg_card"], relief="flat", bd=0)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Título de búsqueda
        search_title = tk.Label(search_frame,
                               text="🔍 Búsqueda Inteligente",
                               font=("Segoe UI", 12, "bold"),
                               bg=self.colors["bg_card"],
                               fg=self.colors["accent"])
        search_title.pack(pady=(10, 5))
        
        # Campo de búsqueda
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                               textvariable=search_var,
                               bg=self.colors["bg_tertiary"],
                               fg=self.colors["text_primary"],
                               font=("Segoe UI", 11),
                               width=60)
        search_entry.pack(pady=5, padx=15)
        
        # Botones de búsqueda
        buttons_frame = tk.Frame(search_frame, bg=self.colors["bg_card"])
        buttons_frame.pack(pady=(5, 15))
        
        # Fila 1 de botones
        row1_frame = tk.Frame(buttons_frame, bg=self.colors["bg_card"])
        row1_frame.pack(pady=2)
        
        ttk.Button(row1_frame, text="🔍 Buscar",
                  command=lambda: self.search_files_in_manager(search_var.get(), results_area)).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(row1_frame, text="📄 Documentos",
                  command=lambda: self.search_category_in_manager("documentos", results_area)).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(row1_frame, text="🖼️ Imágenes",
                  command=lambda: self.search_category_in_manager("imagenes", results_area)).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(row1_frame, text="🎥 Videos",
                  command=lambda: self.search_category_in_manager("videos", results_area)).pack(side=tk.LEFT, padx=3)
        
        # Fila 2 de botones
        row2_frame = tk.Frame(buttons_frame, bg=self.colors["bg_card"])
        row2_frame.pack(pady=2)
        
        ttk.Button(row2_frame, text="💾 Código",
                  command=lambda: self.search_category_in_manager("codigo", results_area)).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(row2_frame, text="🎵 Audio",
                  command=lambda: self.search_category_in_manager("audio", results_area)).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(row2_frame, text="📊 Recientes",
                  command=lambda: self.search_recent_in_manager(results_area)).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(row2_frame, text="📏 Grandes",
                  command=lambda: self.search_large_in_manager(results_area)).pack(side=tk.LEFT, padx=3)
        
        # Área de resultados
        results_frame = tk.Frame(main_frame, bg=self.colors["bg_secondary"], relief="flat", bd=0)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header de resultados
        results_header = tk.Frame(results_frame, bg=self.colors["bg_card"])
        results_header.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        results_title = tk.Label(results_header,
                                text="📋 Resultados",
                                font=("Segoe UI", 11, "bold"),
                                bg=self.colors["bg_card"],
                                fg=self.colors["accent"])
        results_title.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Área de texto para resultados
        results_area = scrolledtext.ScrolledText(results_frame,
                                               wrap=tk.WORD,
                                               bg=self.colors["bg_tertiary"],
                                               fg=self.colors["text_primary"],
                                               font=("Segoe UI", 10),
                                               state=tk.NORMAL,
                                               height=20)
        results_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mensaje inicial
        results_area.insert(tk.END, """🎯 Bienvenido al Gestor de Archivos de J.A.R.V.I.S

💡 Instrucciones:
• Escribe en el campo de búsqueda y presiona "🔍 Buscar"
• Usa los botones de categoría para búsquedas rápidas
• Ejemplos de búsqueda:
  - "archivos python del último mes"
  - "imágenes grandes"
  - "documentos recientes"
  - "config"

🚀 ¡Empezar a buscar!""")
        
        results_area.config(state=tk.DISABLED)
        
        # Configurar eventos
        search_entry.bind("<Return>", lambda e: self.search_files_in_manager(search_var.get(), results_area))
        search_entry.focus()
    
    def search_files_in_manager(self, query, results_area):
        """Buscar archivos usando el file manager inteligente"""
        if not query.strip():
            self.show_manager_error(results_area, "Por favor ingresa un término de búsqueda")
            return
        
        try:
            # Usar el file manager para búsqueda inteligente
            results = self.assistant.file_manager.smart_search_files(query)
            self.display_search_results(results_area, results, f"🔍 Búsqueda: '{query}'")
        except Exception as e:
            self.show_manager_error(results_area, f"Error en la búsqueda: {str(e)}")
    
    def search_category_in_manager(self, category, results_area):
        """Buscar archivos por categoría"""
        category_queries = {
            "documentos": "archivos tipo documento word excel powerpoint pdf txt",
            "imagenes": "archivos tipo imagen jpg jpeg png gif bmp",
            "videos": "archivos tipo video mp4 avi mkv wmv mov",
            "codigo": "archivos tipo código python java js html css",
            "audio": "archivos tipo audio mp3 wav flac m4a"
        }
        
        query = category_queries.get(category, category)
        try:
            results = self.assistant.file_manager.smart_search_files(query)
            emoji_map = {
                "documentos": "📄",
                "imagenes": "🖼️",
                "videos": "🎥",
                "codigo": "💾",
                "audio": "🎵"
            }
            emoji = emoji_map.get(category, "📁")
            self.display_search_results(results_area, results, f"{emoji} Categoría: {category.title()}")
        except Exception as e:
            self.show_manager_error(results_area, f"Error buscando categoría {category}: {str(e)}")
    
    def search_recent_in_manager(self, results_area):
        """Buscar archivos recientes"""
        try:
            results = self.assistant.file_manager.smart_search_files("archivos recientes del último mes")
            self.display_search_results(results_area, results, "📊 Archivos Recientes (último mes)")
        except Exception as e:
            self.show_manager_error(results_area, f"Error buscando archivos recientes: {str(e)}")
    
    def search_large_in_manager(self, results_area):
        """Buscar archivos grandes"""
        try:
            results = self.assistant.file_manager.smart_search_files("archivos grandes más de 10MB")
            self.display_search_results(results_area, results, "📏 Archivos Grandes (>10MB)")
        except Exception as e:
            self.show_manager_error(results_area, f"Error buscando archivos grandes: {str(e)}")
    
    def display_search_results(self, results_area, results, title):
        """Mostrar resultados de búsqueda en el área de texto"""
        results_area.config(state=tk.NORMAL)
        results_area.delete(1.0, tk.END)
        
        # Header
        results_area.insert(tk.END, f"{title}\n")
        results_area.insert(tk.END, "=" * 50 + "\n\n")
        
        if not results:
            results_area.insert(tk.END, "❌ No se encontraron archivos que coincidan con tu búsqueda.\n\n")
            results_area.insert(tk.END, "💡 Sugerencias:\n")
            results_area.insert(tk.END, "• Intenta con términos más generales\n")
            results_area.insert(tk.END, "• Verifica la ortografía\n")
            results_area.insert(tk.END, "• Usa diferentes categorías\n")
        else:
            results_area.insert(tk.END, f"✅ Encontrados {len(results)} archivo(s):\n\n")
            
            for i, file_path in enumerate(results, 1):
                try:
                    import os
                    from pathlib import Path
                    
                    path_obj = Path(file_path)
                    file_name = path_obj.name
                    file_dir = path_obj.parent
                    
                    # Obtener información del archivo
                    if path_obj.exists():
                        file_size = path_obj.stat().st_size
                        size_mb = file_size / (1024 * 1024)
                        
                        if size_mb >= 1:
                            size_str = f"{size_mb:.1f} MB"
                        else:
                            size_str = f"{file_size / 1024:.1f} KB"
                        
                        # Determinar icono por extensión
                        ext = path_obj.suffix.lower()
                        icon = "📄"
                        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                            icon = "🖼️"
                        elif ext in ['.mp4', '.avi', '.mkv', '.wmv', '.mov']:
                            icon = "🎥"
                        elif ext in ['.mp3', '.wav', '.flac', '.m4a']:
                            icon = "🎵"
                        elif ext in ['.py', '.js', '.html', '.css', '.java']:
                            icon = "💾"
                        elif ext in ['.exe', '.msi']:
                            icon = "⚙️"
                        elif ext in ['.zip', '.rar', '.7z']:
                            icon = "📦"
                        
                        results_area.insert(tk.END, f"{i}. {icon} {file_name}\n")
                        results_area.insert(tk.END, f"   📁 {file_dir}\n")
                        results_area.insert(tk.END, f"   📏 {size_str}\n")
                        results_area.insert(tk.END, f"   🔗 {file_path}\n\n")
                    else:
                        results_area.insert(tk.END, f"{i}. ❌ {file_name} (archivo no existe)\n\n")
                        
                except Exception as e:
                    results_area.insert(tk.END, f"{i}. ⚠️ Error procesando: {file_path}\n\n")
        
        results_area.config(state=tk.DISABLED)
        # Scroll al inicio
        results_area.see(1.0)
    
    def show_manager_error(self, results_area, error_message):
        """Mostrar mensaje de error en el gestor"""
        results_area.config(state=tk.NORMAL)
        results_area.delete(1.0, tk.END)
        results_area.insert(tk.END, f"❌ Error: {error_message}\n\n")
        results_area.insert(tk.END, "💡 Consejos:\n")
        results_area.insert(tk.END, "• Verifica que tengas permisos para acceder a los archivos\n")
        results_area.insert(tk.END, "• Intenta con una búsqueda diferente\n")
        results_area.insert(tk.END, "• Revisa la configuración de rutas\n")
        results_area.config(state=tk.DISABLED)
    
    def open_web_controls(self):
        """Abrir controles web"""
        # Crear ventana de controles web
        web_window = tk.Toplevel(self.root)
        web_window.title("Controles Web - Jarvis")
        web_window.geometry("500x400")
        web_window.configure(bg=self.colors["bg_primary"])
        
        # Título
        tk.Label(web_window, text="🌐 Controles Web",
                font=("Segoe UI", 14, "bold"),
                bg=self.colors["bg_primary"],
                fg=self.colors["text_primary"]).pack(pady=10)
        
        # Frame para controles
        controls_frame = tk.Frame(web_window, bg=self.colors["bg_primary"])
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Campo URL
        tk.Label(controls_frame, text="URL:", 
                bg=self.colors["bg_primary"],
                fg=self.colors["text_primary"]).pack(anchor=tk.W)
        
        url_var = tk.StringVar()
        url_entry = tk.Entry(controls_frame, textvariable=url_var,
                            bg=self.colors["bg_tertiary"],
                            fg=self.colors["text_primary"],
                            font=("Segoe UI", 10),
                            width=50)
        url_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Botones de acción
        buttons_frame = tk.Frame(controls_frame, bg=self.colors["bg_primary"])
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Botón abrir
        ttk.Button(buttons_frame, text="🌐 Abrir",
                  command=lambda: self.open_website(url_var.get())).pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón analizar
        ttk.Button(buttons_frame, text="🔍 Analizar",
                  command=lambda: self.analyze_webpage(url_var.get())).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separador
        tk.Label(controls_frame, text="━" * 50,
                bg=self.colors["bg_primary"],
                fg=self.colors["text_secondary"]).pack(pady=15)
        
        # Búsquedas rápidas
        tk.Label(controls_frame, text="🔍 Búsquedas Rápidas:",
                font=("Segoe UI", 11, "bold"),
                bg=self.colors["bg_primary"],
                fg=self.colors["text_primary"]).pack(anchor=tk.W)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(controls_frame, textvariable=search_var,
                               bg=self.colors["bg_tertiary"],
                               fg=self.colors["text_primary"],
                               font=("Segoe UI", 10),
                               width=50)
        search_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Botones de búsqueda
        search_buttons_frame = tk.Frame(controls_frame, bg=self.colors["bg_primary"])
        search_buttons_frame.pack(fill=tk.X, pady=5)
        
        search_engines = [
            ("Google", "google"),
            ("YouTube", "youtube"), 
            ("Wikipedia", "wikipedia")
        ]
        
        for name, engine in search_engines:
            ttk.Button(search_buttons_frame, text=name,
                      command=lambda e=engine: self.assistant.web_manager.search_web(search_var.get(), e)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Focus en URL
        url_entry.focus()
    
    def show_help(self):
        """Mostrar ayuda"""
        help_text = self.assistant.conversation_engine.get_help_text()
        self.add_message("Jarvis", help_text, "assistant")
    
    def open_settings(self):
        """Abrir configuración"""
        # Crear ventana de configuración
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configuración")
        settings_window.geometry("500x400")
        settings_window.configure(bg=self.colors["bg_primary"])
        
        tk.Label(settings_window, text="Configuración de Jarvis",
                font=("Segoe UI", 14, "bold"),
                bg=self.colors["bg_primary"],
                fg=self.colors["text_primary"]).pack(pady=10)
    
    def add_message(self, sender: str, content: str, msg_type: str = "normal"):
        """Agregar mensaje al chat con formato mejorado"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Habilitar edición temporalmente
        self.chat_area.config(state=tk.NORMAL)
        
        # Separador visual para mensajes importantes
        if msg_type in ["assistant", "voice_user"]:
            self.chat_area.insert(tk.END, "─" * 50 + "\n", "highlight")
        
        # Agregar timestamp con mejor formato
        self.chat_area.insert(tk.END, f"[{timestamp}]  ", "timestamp")
        
        # Agregar sender con formato especial
        if msg_type == "voice_user":
            self.chat_area.insert(tk.END, f"🎤 {sender}\n", "voice_user")
        else:
            self.chat_area.insert(tk.END, f"{sender}\n", msg_type)
        
        # Agregar contenido con indentación
        content_lines = content.split('\n')
        for i, line in enumerate(content_lines):
            if line.strip():  # Solo líneas no vacías
                if msg_type == "voice_user":
                    self.chat_area.insert(tk.END, f"   {line}\n", "voice_user")
                else:
                    self.chat_area.insert(tk.END, f"   {line}\n", "highlight")
        
        # Espacio extra después del mensaje
        self.chat_area.insert(tk.END, "\n")
        
        # Deshabilitar edición
        self.chat_area.config(state=tk.DISABLED)
        
        # Scroll hacia abajo con animación suave
        self.chat_area.see(tk.END)
        
        # Actualizar indicador de actividad
        if msg_type == "voice_user":
            self.update_activity_indicator("Comando por voz recibido", True)
        elif msg_type == "assistant":
            self.update_activity_indicator("Respuesta generada", True)
        
        # Volver a inactivo después de un momento
        self.root.after(2000, lambda: self.update_activity_indicator("Inactivo", False))
    
    def update_status(self, text: str):
        """Actualizar barra de estado"""
        self.status_label.config(text=text)
    
    def smart_search_files(self, query: str):
        """Búsqueda inteligente de archivos con análisis de lenguaje natural"""
        def search_thread():
            try:
                self.update_status("🔍 Realizando búsqueda inteligente...")
                
                result = self.assistant.file_manager.smart_search_files(query, max_results=50)
                
                if result['success'] and result['results']:
                    files_found = len(result['results'])
                    stats = result['stats']
                    
                    # Mostrar resumen
                    summary = f"🎯 Búsqueda inteligente: '{query}'\n"
                    summary += f"📊 Encontrados: {files_found} archivos en {stats['search_time']:.2f}s\n\n"
                    
                    # Mostrar estadísticas por tipo
                    if stats['by_type']:
                        summary += "📁 Por tipo:\n"
                        for file_type, count in stats['by_type'].items():
                            summary += f"  • {file_type}: {count} archivos\n"
                        summary += "\n"
                    
                    # Mostrar estadísticas por ubicación
                    if stats['by_location']:
                        summary += "📍 Por ubicación:\n"
                        for location, count in stats['by_location'].items():
                            if count > 0:
                                summary += f"  • {location}: {count} archivos\n"
                        summary += "\n"
                    
                    self.add_message("Jarvis", summary, "assistant")
                    
                    # Mostrar primeros archivos encontrados
                    display_count = min(10, len(result['results']))
                    files_text = f"🗂️ Primeros {display_count} resultados:\n\n"
                    
                    for i, file_info in enumerate(result['results'][:display_count], 1):
                        files_text += f"{i}. 📄 {file_info['name']}\n"
                        files_text += f"   📁 {file_info.get('directory', 'N/A')}\n"
                        files_text += f"   📏 {file_info.get('size_human', 'N/A')}"
                        files_text += f"   📅 {file_info.get('modified_human', 'N/A')}\n"
                        if file_info.get('content_match'):
                            files_text += "   🔍 ¡Coincidencia en contenido!\n"
                        files_text += "\n"
                    
                    self.add_message("Jarvis", files_text, "assistant")
                    
                    # Mostrar sugerencias si las hay
                    if result.get('suggestions'):
                        suggestions_text = "💡 Sugerencias:\n"
                        for suggestion in result['suggestions']:
                            suggestions_text += f"  • {suggestion}\n"
                        self.add_message("Jarvis", suggestions_text, "assistant")
                    
                else:
                    self.add_message("Jarvis", f"❌ No se encontraron archivos para '{query}'", "assistant")
                    if result.get('suggestions'):
                        suggestions_text = "💡 Sugerencias:\n"
                        for suggestion in result['suggestions']:
                            suggestions_text += f"  • {suggestion}\n"
                        self.add_message("Jarvis", suggestions_text, "assistant")
                
                self.update_status("Listo")
                
            except Exception as e:
                self.add_message("Sistema", f"❌ Error en búsqueda inteligente: {str(e)}", "error")
                self.update_status("Error")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def search_files_by_category(self, category: str):
        """Buscar archivos por categoría específica"""
        def search_thread():
            try:
                self.update_status(f"📁 Buscando archivos de {category}...")
                
                result = self.assistant.file_manager.find_by_category(category, max_results=30)
                
                if result['success'] and result['results']:
                    files_found = len(result['results'])
                    
                    response = f"📁 Archivos de categoría '{category}': {files_found} encontrados\n\n"
                    
                    for i, file_info in enumerate(result['results'][:15], 1):
                        response += f"{i}. {file_info['name']}\n"
                        response += f"   📍 {file_info.get('directory', 'N/A')}\n"
                        response += f"   📏 {file_info.get('size_human', 'N/A')}\n\n"
                    
                    if files_found > 15:
                        response += f"... y {files_found - 15} archivos más.\n"
                    
                    self.add_message("Jarvis", response, "assistant")
                else:
                    self.add_message("Jarvis", f"❌ No se encontraron archivos de categoría '{category}'", "assistant")
                
                self.update_status("Listo")
                
            except Exception as e:
                self.add_message("Sistema", f"❌ Error buscando por categoría: {str(e)}", "error")
                self.update_status("Error")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def search_in_file_content(self, keywords: str):
        """Buscar en contenido de archivos"""
        def search_thread():
            try:
                self.update_status(f"🔎 Buscando '{keywords}' en contenido de archivos...")
                
                result = self.assistant.file_manager.search_in_content(keywords, max_results=20)
                
                if result['success'] and result['results']:
                    files_found = len(result['results'])
                    content_matches = result['stats'].get('content_matches', 0)
                    
                    response = f"🔍 Búsqueda en contenido: '{keywords}'\n"
                    response += f"📄 {files_found} archivos analizados, {content_matches} con coincidencias\n\n"
                    
                    for i, file_info in enumerate(result['results'][:10], 1):
                        if file_info.get('content_match'):
                            response += f"{i}. ✅ {file_info['name']}\n"
                            response += f"   📁 {file_info.get('directory', 'N/A')}\n"
                            response += f"   📏 {file_info.get('size_human', 'N/A')}\n\n"
                    
                    self.add_message("Jarvis", response, "assistant")
                else:
                    self.add_message("Jarvis", f"❌ No se encontró '{keywords}' en el contenido de archivos", "assistant")
                
                self.update_status("Listo")
                
            except Exception as e:
                self.add_message("Sistema", f"❌ Error buscando en contenido: {str(e)}", "error")
                self.update_status("Error")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def start_conversation_mode(self):
        """Iniciar modo conversación continua por voz con interfaz mejorada"""
        if not self.assistant.voice_manager.recognition_enabled:
            self.add_message("Sistema", "❌ Reconocimiento de voz no disponible para conversación continua", "error")
            return
        
        # Confirmación inicial por voz
        self.voice_feedback("Iniciando modo conversación continua. Di parar cuando quieras terminar")
            
        def conversation_thread():
            try:
                self.start_voice_animation()
                self.update_activity_indicator("Conversación por voz", True)
                
                # Función callback mejorada para mostrar conversación completa
                def process_voice_command(text: str) -> str:
                    try:
                        # Confirmación de que se escuchó
                        self.root.after(0, lambda: self.voice_feedback(f"Te escuché decir: {text}"))
                        
                        # Mostrar lo que dijo el usuario
                        self.root.after(0, lambda: self.add_message("👤 Usuario (Voz)", f"🎤 \"{text}\"", "voice_user"))
                        
                        # Procesar comando
                        response = self.assistant.conversation_engine.process_message(text)
                        
                        if response["type"] == "command":
                            # Ejecutar comando y mostrar resultado
                            self.root.after(0, lambda: self.handle_command(response))
                            return f"Ejecutando: {response.get('content', 'Comando procesado')}"
                        else:
                            # Mostrar respuesta en la interfaz
                            response_text = response.get("content", "Procesado")
                            self.root.after(0, lambda: self.add_message("🤖 J.A.R.V.I.S", response_text, "assistant"))
                            return response_text
                            
                    except Exception as e:
                        error_msg = f"Error procesando comando: {str(e)}"
                        self.root.after(0, lambda: self.add_message("Sistema", error_msg, "error"))
                        self.root.after(0, lambda: self.voice_feedback("Hubo un error procesando tu comando"))
                        return error_msg
                
                # Iniciar conversación
                result = self.assistant.voice_manager.start_conversation_mode(process_voice_command)
                
                if result['success']:
                    welcome_msg = f"✅ {result['message']}\n💬 {result.get('instructions', 'Di parar para terminar')}"
                    self.add_message("J.A.R.V.I.S", welcome_msg, "assistant")
                    # Confirmación final por voz
                    self.voice_feedback("Conversación iniciada correctamente. Te estoy escuchando")
                else:
                    self.add_message("J.A.R.V.I.S", f"❌ Error iniciando conversación: {result['error']}", "error")
                    self.voice_feedback("No pude iniciar el modo conversación")
                    self.stop_voice_animation()
                    self.update_activity_indicator("Error", False)
                
            except Exception as e:
                self.add_message("Sistema", f"❌ Error en modo conversación: {str(e)}", "error")
                self.voice_feedback("Error en el modo conversación")
                self.stop_voice_animation()
                self.update_activity_indicator("Error", False)
        
        threading.Thread(target=conversation_thread, daemon=True).start()
    
    # ===== FUNCIONES AUXILIARES PARA LA INTERFAZ MEJORADA =====
    
    def add_welcome_message(self):
        """Agregar mensaje de bienvenida"""
        welcome_msg = """🎉 ¡Bienvenido a J.A.R.V.I.S!

🎤 Para usar voz: "conversación por voz" o click en 💬 Conversar
🔍 Para buscar archivos: "buscar archivos python" o "documentos recientes"
🌐 Para analizar web: "analizar google.com"
❓ Para ayuda: "¿qué puedes hacer?" o click en ❓ Ayuda

¡Estoy listo para asistirte! ✨"""
        self.add_message("J.A.R.V.I.S", welcome_msg, "assistant")
    
    def on_key_press(self, event):
        """Manejar teclas presionadas en el input"""
        self.update_input_status("✍️ Escribiendo...")
        # Cancelar timer previo si existe
        if hasattr(self, '_typing_timer'):
            self.root.after_cancel(self._typing_timer)
        # Configurar nuevo timer
        self._typing_timer = self.root.after(1000, lambda: self.update_input_status("✍️ Listo para escribir"))
    
    def on_entry_focus_in(self, event):
        """Cuando el campo de entrada recibe focus"""
        self.entry.config(highlightbackground=self.colors["accent"])
        self.update_input_status("✍️ Escribiendo...")
    
    def on_entry_focus_out(self, event):
        """Cuando el campo de entrada pierde focus"""
        self.entry.config(highlightbackground=self.colors["bg_tertiary"])
        self.update_input_status("✍️ Listo para escribir")
    
    def on_button_hover(self, button, is_hovering):
        """Efecto hover para botones"""
        if is_hovering:
            button.config(bg=self.colors["accent"], fg="white")
        else:
            button.config(bg=self.colors["bg_tertiary"], fg=self.colors["text_secondary"])
    
    def insert_suggestion(self, suggestion):
        """Insertar sugerencia en el campo de entrada"""
        self.entry_var.set(suggestion)
        self.entry.focus()
        self.entry.icursor(tk.END)
    
    def clear_input(self):
        """Limpiar campo de entrada"""
        self.entry_var.set("")
        self.update_input_status("🗑️ Campo limpiado")
        self.root.after(1000, lambda: self.update_input_status("✍️ Listo para escribir"))
    
    def focus_input(self):
        """Dar focus al campo de entrada"""
        self.entry.focus()
        self.update_input_status("✍️ Campo activo")
    
    def update_input_status(self, status):
        """Actualizar estado del input"""
        self.input_status.config(text=status)
    
    def update_activity_indicator(self, activity, is_active=False):
        """Actualizar indicador de actividad"""
        if is_active:
            self.activity_indicator.config(text=f"⚡ {activity}", fg=self.colors["success"])
        else:
            self.activity_indicator.config(text=f"💤 {activity}", fg=self.colors["text_secondary"])
    
    def show_stats(self):
        """Mostrar estadísticas del sistema"""
        stats_msg = """📊 Estadísticas de J.A.R.V.I.S:

🎤 Voz disponible: """ + ("✅ Sí" if self.assistant.voice_manager.recognition_enabled else "❌ No") + """
🔊 TTS disponible: """ + ("✅ Sí" if self.assistant.voice_manager.tts_enabled else "❌ No") + """
💾 Memoria de conversación: """ + str(len(self.assistant.conversation_engine.conversation_history)) + """ mensajes
🕐 Tiempo activo: Desde el inicio de sesión

🎯 Funciones principales:
• Reconocimiento de voz inteligente
• Búsqueda de archivos avanzada
• Análisis web completo
• Conversación natural"""
        
        self.add_message("Sistema", stats_msg, "system")
    
    def show_examples(self):
        """Mostrar ejemplos de comandos"""
        examples_msg = """💡 Ejemplos de comandos:

🎤 Comandos de voz:
• "conversación por voz" - Modo diálogo
• "escuchar micrófono" - Escucha única

🔍 Búsqueda de archivos:
• "buscar archivos python del último mes"
• "documentos grandes recientes"
• "imágenes jpg pequeñas"

🌐 Análisis web:
• "analizar google.com"
• "examinar youtube.com"

💬 Conversación:
• "¿qué hora es?"
• "¿qué puedes hacer?"
• "ayuda con archivos"

¡Prueba cualquiera de estos comandos! ✨"""
        
        self.add_message("J.A.R.V.I.S", examples_msg, "assistant")
    
    def animate_voice_button(self):
        """Animar botón de voz cuando está activo"""
        if self.is_voice_active:
            current_text = self.voice_button.cget("text")
            if "🎤" in current_text:
                self.voice_button.config(text="🔴 Escuchando...")
            else:
                self.voice_button.config(text="🎤 Escuchar")
            
            # Programar próxima animación
            self.voice_animation_id = self.root.after(500, self.animate_voice_button)
    
    def start_voice_animation(self):
        """Iniciar animación de voz"""
        self.is_voice_active = True
        self.animate_voice_button()
        self.update_activity_indicator("Escuchando por voz", True)
    
    def stop_voice_animation(self):
        """Detener animación de voz"""
        self.is_voice_active = False
        if self.voice_animation_id:
            self.root.after_cancel(self.voice_animation_id)
        self.voice_button.config(text="🎤 Escuchar")
        self.update_activity_indicator("Inactivo", False)

    def confirm_voice_command(self, command: str, parameter: str):
        """Confirmar por voz que se escuchó y entendió el comando"""
        confirmations = {
            "buscar_archivo": f"Entendido, buscando archivo: {parameter}",
            "buscar_archivo_inteligente": f"Te escuché, realizando búsqueda inteligente de: {parameter}",
            "buscar_por_categoria": f"Perfecto, buscando archivos de categoría: {parameter}",
            "buscar_en_contenido": f"Confirmado, buscando contenido en archivos: {parameter}",
            "abrir_archivo": f"Te escuché, abriendo archivo: {parameter}",
            "crear_archivo": f"Entendido, creando archivo: {parameter}",
            "abrir_web": f"Confirmado, abriendo página web: {parameter}",
            "buscar_web": f"Te escuché, buscando en web: {parameter}",
            "analizar_web": f"Perfecto, analizando página web: {parameter}",
            "buscar_analizar": f"Entendido, buscando y analizando: {parameter}",
            "escuchar_microfono": "Te escuché, activando micrófono",
            "conversacion_continua": "Confirmado, iniciando modo conversación continua"
        }
        
        # Obtener confirmación específica o genérica
        confirmation = confirmations.get(command, f"Te escuché, ejecutando: {command}")
        
        # Agregar mensaje visual de confirmación
        self.add_message("Jarvis", f"🎯 {confirmation}", "assistant")
        
        # Intentar confirmar por voz si está disponible
        try:
            if hasattr(self.assistant, 'voice_manager') and self.assistant.voice_manager:
                # Ejecutar en hilo separado para no bloquear la UI
                import threading
                threading.Thread(
                    target=lambda: self.assistant.voice_manager.speak(confirmation),
                    daemon=True
                ).start()
        except Exception as e:
            # Si hay error con TTS, solo mostrar en texto
            print(f"No se pudo usar TTS: {e}")

    def voice_feedback(self, message: str):
        """Proporcionar retroalimentación por voz y visual"""
        # Mensaje visual
        self.add_message("Jarvis", f"🔊 {message}", "assistant")
        
        # Mensaje por voz
        try:
            if hasattr(self.assistant, 'voice_manager') and self.assistant.voice_manager:
                import threading
                threading.Thread(
                    target=lambda: self.assistant.voice_manager.speak(message),
                    daemon=True
                ).start()
        except Exception as e:
            print(f"Error con TTS: {e}")

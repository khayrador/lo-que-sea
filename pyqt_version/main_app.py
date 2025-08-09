"""
Aplicación Principal de Jarvis PyQt5
Conecta la UI con el backend usando threads
"""

import sys
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtGui import QIcon

# Importar nuestros módulos
from ui_designs.main_window_base import JarvisMainWindowUI
from workers.jarvis_worker import JarvisWorker
from backend.audio_manager import AudioManager
from backend.config_manager import ConfigManager


class JarvisApp(JarvisMainWindowUI):
    """Aplicación principal que conecta UI y backend"""
    
    def __init__(self):
        super().__init__()
        
        # Configurar logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Iniciando Jarvis PyQt5")
        
        # Cargar configuración
        self.config = self.load_configuration()
        
        # Inicializar componentes
        self.audio_manager = AudioManager(self.config)
        self.worker = None
        
        # Conectar señales de la UI
        self.connect_ui_signals()
        
        # Configurar timers
        self.setup_timers()
        
        # Estado inicial
        self.current_state = 'IDLE'
        self.update_ui_state('IDLE')
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/jarvis.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def load_configuration(self) -> Dict[str, Any]:
        """Cargar configuración desde .env"""
        # Cargar .env
        env_path = '.env'
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        # Configuración por defecto
        config = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
            'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY', ''),
            'VOICE_PROVIDER': os.getenv('VOICE_PROVIDER', 'elevenlabs'),
            'TTS_VOICE_ID': os.getenv('TTS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB'),
            'STT_LANGUAGE': os.getenv('STT_LANGUAGE', 'es-ES'),
            'STT_TIMEOUT': os.getenv('STT_TIMEOUT', '5'),
            'STT_PHRASE_TIMEOUT': os.getenv('STT_PHRASE_TIMEOUT', '1'),
            'UI_TRANSPARENCY': float(os.getenv('UI_TRANSPARENCY', '0.95')),
            'DEBUG_MODE': os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        }
        
        return config
    
    def connect_ui_signals(self):
        """Conectar señales de la interfaz"""
        # Botón del micrófono
        self.mic_button.clicked.connect(self.on_mic_button_clicked)
        
        # Botones de control
        self.minimize_btn.clicked.connect(self.hide)
        self.close_btn.clicked.connect(self.close_application)
        
        # Botones secundarios
        self.settings_btn.clicked.connect(self.show_settings)
        self.history_btn.clicked.connect(self.show_history)
        self.help_btn.clicked.connect(self.show_help)
    
    def setup_timers(self):
        """Configurar timers para animaciones y actualizaciones"""
        # Timer para animación del indicador de estado
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_status_animation)
        
        # Timer para monitoreo del sistema
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_system_info)
        self.system_timer.start(5000)  # Cada 5 segundos
    
    @pyqtSlot()
    def on_mic_button_clicked(self):
        """Manejar clic en botón del micrófono"""
        self.logger.info("Botón del micrófono presionado")
        
        if self.current_state == 'IDLE':
            self.start_listening()
        elif self.current_state == 'LISTENING':
            self.stop_listening()
        else:
            self.logger.warning(f"Botón presionado en estado: {self.current_state}")
    
    def start_listening(self):
        """Iniciar proceso de escucha"""
        try:
            # Crear y configurar worker si no existe
            if self.worker is None or not self.worker.isRunning():
                self.worker = JarvisWorker(self.config)
                self.connect_worker_signals()
                self.worker.start()
            
            # Iniciar escucha
            self.worker.iniciar_escucha()
            self.logger.info("Escucha iniciada")
            
        except Exception as e:
            self.logger.error(f"Error iniciando escucha: {e}")
            self.show_error(f"Error iniciando escucha: {e}")
    
    def stop_listening(self):
        """Detener proceso de escucha"""
        try:
            if self.worker:
                self.worker.detener_escucha()
            self.logger.info("Escucha detenida")
            
        except Exception as e:
            self.logger.error(f"Error deteniendo escucha: {e}")
    
    def connect_worker_signals(self):
        """Conectar señales del worker thread"""
        if self.worker:
            self.worker.estadoCambiado.connect(self.on_state_changed)
            self.worker.respuestaLista.connect(self.on_response_ready)
            self.worker.errorOcurrido.connect(self.on_error_occurred)
            self.worker.comandoReconocido.connect(self.on_command_recognized)
            self.worker.audioDetectado.connect(self.on_audio_detected)
    
    @pyqtSlot(str)
    def on_state_changed(self, new_state: str):
        """Manejar cambio de estado"""
        self.logger.info(f"Estado cambiado: {self.current_state} -> {new_state}")
        self.current_state = new_state
        self.update_ui_state(new_state)
    
    @pyqtSlot(str)
    def on_response_ready(self, response: str):
        """Manejar respuesta lista"""
        self.logger.info(f"Respuesta lista: {response}")
        
        # Mostrar en UI
        self.response_area.append(f"🤖 Jarvis: {response}")
        
        # Generar y reproducir audio
        self.generate_and_play_audio(response)
    
    @pyqtSlot(str)
    def on_error_occurred(self, error_message: str):
        """Manejar error ocurrido"""
        self.logger.error(f"Error del worker: {error_message}")
        self.show_error(error_message)
    
    @pyqtSlot(str)
    def on_command_recognized(self, command: str):
        """Manejar comando reconocido"""
        self.logger.info(f"Comando reconocido: {command}")
        self.response_area.append(f"👤 Usuario: {command}")
    
    @pyqtSlot(float)
    def on_audio_detected(self, audio_level: float):
        """Manejar nivel de audio detectado"""
        # Actualizar visualización de audio
        self.audio_progress.setValue(int(audio_level * 100))
    
    def update_ui_state(self, state: str):
        """Actualizar UI según el estado"""
        state_config = {
            'IDLE': {
                'status_text': 'IDLE',
                'status_color': '#00ff41',
                'mic_text': '🎤',
                'animation': False
            },
            'LISTENING': {
                'status_text': 'ESCUCHANDO',
                'status_color': '#ff4141',
                'mic_text': '🔴',
                'animation': True
            },
            'THINKING': {
                'status_text': 'PROCESANDO',
                'status_color': '#4141ff',
                'mic_text': '🧠',
                'animation': True
            },
            'SPEAKING': {
                'status_text': 'HABLANDO',
                'status_color': '#41ff41',
                'mic_text': '🔊',
                'animation': True
            }
        }
        
        config = state_config.get(state, state_config['IDLE'])
        
        # Actualizar textos
        self.status_text.setText(config['status_text'])
        self.mic_button.setText(config['mic_text'])
        
        # Actualizar colores
        self.status_indicator.setStyleSheet(f"color: {config['status_color']};")
        
        # Manejar animaciones
        if config['animation']:
            self.start_status_animation()
            self.audio_progress.setVisible(True)
        else:
            self.stop_status_animation()
            self.audio_progress.setVisible(False)
    
    def generate_and_play_audio(self, text: str):\n        \"\"\"Generar y reproducir audio para la respuesta\"\"\"\n        try:\n            self.audio_manager.speak_text(text)\n        except Exception as e:\n            self.logger.error(f\"Error generando audio: {e}\")\n    \n    def start_status_animation(self):\n        \"\"\"Iniciar animación del indicador de estado\"\"\"\n        if not self.animation_timer.isActive():\n            self.animation_timer.start(500)  # Cada 500ms\n    \n    def stop_status_animation(self):\n        \"\"\"Detener animación del indicador de estado\"\"\"\n        self.animation_timer.stop()\n    \n    def update_status_animation(self):\n        \"\"\"Actualizar animación del indicador\"\"\"\n        current_opacity = self.status_indicator.windowOpacity()\n        new_opacity = 0.3 if current_opacity > 0.7 else 1.0\n        self.status_indicator.setWindowOpacity(new_opacity)\n    \n    def update_system_info(self):\n        \"\"\"Actualizar información del sistema\"\"\"\n        # Aquí se puede agregar monitoreo del sistema\n        pass\n    \n    def show_error(self, message: str):\n        \"\"\"Mostrar mensaje de error\"\"\"\n        self.response_area.append(f\"❌ Error: {message}\")\n    \n    def show_settings(self):\n        \"\"\"Mostrar ventana de configuración\"\"\"\n        self.logger.info(\"Mostrando configuración\")\n        # TODO: Implementar ventana de configuración\n    \n    def show_history(self):\n        \"\"\"Mostrar historial de conversaciones\"\"\"\n        self.logger.info(\"Mostrando historial\")\n        # TODO: Implementar ventana de historial\n    \n    def show_help(self):\n        \"\"\"Mostrar ayuda\"\"\"\n        self.logger.info(\"Mostrando ayuda\")\n        # TODO: Implementar ventana de ayuda\n    \n    def close_application(self):\n        \"\"\"Cerrar aplicación completamente\"\"\"\n        self.logger.info(\"Cerrando aplicación\")\n        \n        # Detener worker\n        if self.worker and self.worker.isRunning():\n            self.worker.quit()\n            self.worker.wait(3000)  # Esperar máximo 3 segundos\n        \n        # Cerrar aplicación\n        QApplication.quit()\n\n\ndef main():\n    \"\"\"Función principal\"\"\"\n    # Crear aplicación\n    app = QApplication(sys.argv)\n    app.setQuitOnLastWindowClosed(False)  # Permitir minimizar a bandeja\n    \n    # Verificar soporte de bandeja del sistema\n    if not QSystemTrayIcon.isSystemTrayAvailable():\n        print(\"Sistema de bandeja no disponible\")\n    \n    # Crear y mostrar ventana principal\n    jarvis_app = JarvisApp()\n    jarvis_app.show()\n    \n    # Ejecutar aplicación\n    sys.exit(app.exec_())\n\n\nif __name__ == \"__main__\":\n    main()"

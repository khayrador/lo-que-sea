#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis - Asistente Virtual con PyQt5
Aplicación principal con interfaz gráfica profesional
"""

import sys
import os
import logging
from typing import Dict, Any
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QSystemTrayIcon, QMenu, QProgressBar, QFrame)
from PyQt5.QtCore import QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log'),
        logging.StreamHandler()
    ]
)

# Importar módulos locales
try:
    from backend.audio_manager import AudioManager
    from workers.jarvis_worker import JarvisWorker
    from ui_designs.main_window_base import MainWindowBase
except ImportError as e:
    logging.error(f"Error importando módulos: {e}")
    sys.exit(1)


class JarvisApp(QMainWindow):
    """Aplicación principal de Jarvis"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Configuración
        self.config = self.load_config()
        
        # Componentes
        self.audio_manager = None
        self.worker = None
        self.tray_icon = None
        
        # Timers
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_status_animation)
        
        # Inicializar UI
        self.init_ui()
        self.init_audio_manager()
        self.init_worker()
        self.init_tray_icon()
        
        self.logger.info("Jarvis iniciado correctamente")
    
    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde variables de entorno"""
        return {
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
            'VOICE_PROVIDER': os.getenv('VOICE_PROVIDER', 'pyttsx3'),
            'TTS_MODEL': os.getenv('TTS_MODEL', 'tts_models/multilingual/multi-dataset/xtts_v2'),
            'TTS_SPEAKER': os.getenv('TTS_SPEAKER', 'Dionisio Schuyler'),
            'TTS_LANGUAGE': os.getenv('TTS_LANGUAGE', 'es'),
            'STT_LANGUAGE': os.getenv('STT_LANGUAGE', 'es-ES'),
            'STT_TIMEOUT': int(os.getenv('STT_TIMEOUT', 5)),
        }
    
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle("Jarvis - Asistente Virtual")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Título
        title_label = QLabel("🤖 JARVIS - Asistente Virtual (Powered by Gemini)")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # Área de respuestas
        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        self.response_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.response_area)
        
        # Barra de progreso de audio
        self.audio_progress = QProgressBar()
        self.audio_progress.setVisible(False)
        layout.addWidget(self.audio_progress)
        
        # Botones de control
        button_layout = QHBoxLayout()
        
        self.listen_button = QPushButton("🎤 Escuchar")
        self.listen_button.clicked.connect(self.toggle_listening)
        self.listen_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(self.listen_button)
        
        self.stop_button = QPushButton("⏹️ Parar")
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Indicador de estado
        self.status_indicator = QLabel("💤 Inactivo")
        self.status_indicator.setStyleSheet("padding: 5px; background-color: #e9ecef; border-radius: 3px;")
        layout.addWidget(self.status_indicator)
        
        # Aplicar tema
        self.apply_theme()
    
    def apply_theme(self):
        """Aplicar tema visual"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
    
    def init_audio_manager(self):
        """Inicializar gestor de audio"""
        try:
            self.audio_manager = AudioManager(self.config)
            self.audio_manager.audioFinished.connect(self.on_audio_finished)
            self.audio_manager.audioError.connect(self.on_audio_error)
            self.logger.info("Audio manager inicializado")
        except Exception as e:
            self.logger.error(f"Error inicializando audio manager: {e}")
            self.show_error(f"Error de audio: {e}")
    
    def init_worker(self):
        """Inicializar worker de procesamiento"""
        try:
            self.worker = JarvisWorker(self.config)
            self.worker.responseReady.connect(self.on_response_ready)
            self.worker.errorOcurrido.connect(self.on_error)
            self.worker.estadoCambiado.connect(self.on_status_changed)
            self.worker.start()
            self.logger.info("Worker iniciado")
        except Exception as e:
            self.logger.error(f"Error inicializando worker: {e}")
            self.show_error(f"Error del sistema: {e}")
    
    def init_tray_icon(self):
        """Inicializar icono de bandeja del sistema"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Menú del icono de bandeja
            tray_menu = QMenu()
            
            show_action = tray_menu.addAction("Mostrar")
            show_action.triggered.connect(self.show)
            
            quit_action = tray_menu.addAction("Salir")
            quit_action.triggered.connect(self.close_application)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            self.logger.info("Icono de bandeja inicializado")
    
    def toggle_listening(self):
        """Alternar estado de escucha"""
        if self.worker:
            if hasattr(self.worker, 'is_listening') and self.worker.is_listening:
                self.stop_listening()
            else:
                self.start_listening()
    
    def start_listening(self):
        """Iniciar escucha"""
        if self.worker:
            self.worker.iniciar_escucha()
            self.listen_button.setText("🔴 Escuchando...")
            self.listen_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
            self.start_status_animation()
    
    def stop_listening(self):
        """Detener escucha"""
        if self.worker:
            self.worker.detener_escucha()
            self.listen_button.setText("🎤 Escuchar")
            self.listen_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.stop_status_animation()
    
    def on_response_ready(self, response: str):
        """Manejar respuesta lista"""
        self.response_area.append(f"🤖 Jarvis: {response}")
        
        # Generar audio si está configurado
        if self.audio_manager:
            self.generate_and_play_audio(response)
    
    def on_error(self, error: str):
        """Manejar errores"""
        self.show_error(error)
    
    def on_status_changed(self, status: str):
        """Manejar cambio de estado"""
        status_icons = {
            'IDLE': '💤 Inactivo',
            'LISTENING': '🎤 Escuchando...',
            'PROCESSING': '🧠 Procesando...',
            'SPEAKING': '🗣️ Hablando...',
            'ERROR': '❌ Error'
        }
        
        display_status = status_icons.get(status, f'🔄 {status}')
        self.status_indicator.setText(display_status)
    
    def on_audio_finished(self):
        """Manejar fin de reproducción de audio"""
        self.audio_progress.setVisible(False)
        self.stop_status_animation()
    
    def on_audio_error(self, error: str):
        """Manejar error de audio"""
        self.show_error(f"Error de audio: {error}")
    
    def generate_and_play_audio(self, text: str):
        """Generar y reproducir audio para la respuesta"""
        try:
            if self.audio_manager:
                self.audio_progress.setVisible(True)
                self.start_status_animation()
                self.audio_manager.speak_text(text)
        except Exception as e:
            self.logger.error(f"Error generando audio: {e}")
    
    def start_status_animation(self):
        """Iniciar animación del indicador de estado"""
        if not self.animation_timer.isActive():
            self.animation_timer.start(500)  # Cada 500ms
    
    def stop_status_animation(self):
        """Detener animación del indicador de estado"""
        self.animation_timer.stop()
    
    def update_status_animation(self):
        """Actualizar animación del indicador"""
        # Alternar opacidad para efecto de parpadeo
        current_text = self.status_indicator.text()
        if current_text.endswith('...'):
            self.status_indicator.setText(current_text[:-3])
        else:
            self.status_indicator.setText(current_text + '...')
    
    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        self.response_area.append(f"❌ Error: {message}")
        self.logger.error(message)
    
    def closeEvent(self, event):
        """Manejar evento de cierre"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.close_application()
    
    def close_application(self):
        """Cerrar aplicación completamente"""
        self.logger.info("Cerrando aplicación")
        
        # Detener worker
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(3000)  # Esperar máximo 3 segundos
        
        # Cerrar aplicación
        QApplication.quit()


def main():
    """Función principal"""
    # Crear aplicación
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Permitir minimizar a bandeja
    
    # Verificar soporte de bandeja del sistema
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("Sistema de bandeja no disponible")
    
    # Crear y mostrar ventana principal
    jarvis_app = JarvisApp()
    jarvis_app.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

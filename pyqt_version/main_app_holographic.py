#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis - Interfaz Holográfica Avanzada
Efectos visuales futuristas inspirados en Iron Man
"""

import sys
import os
import logging
import math
import re
from typing import Dict, Any
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QSystemTrayIcon, QMenu, QProgressBar, QFrame,
                             QLineEdit, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
                             QFileDialog, QDesktopWidget)
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPainter, QLinearGradient, QBrush, QPen, QPixmap
from PyQt5.QtCore import Qt, QSize
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
except ImportError as e:
    logging.error(f"Error importando módulos: {e}")
    sys.exit(1)


class HolographicWidget(QWidget):
    """Widget con efectos holográficos avanzados"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.glow_intensity = 0.8
        self.scan_line_position = 0
        self.setup_effects()
        
        # Timer para animaciones
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_effects)
        self.animation_timer.start(50)  # 20 FPS
    
    def setup_effects(self):
        """Configurar efectos visuales"""
        # Efecto de sombra/brillo
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(20)
        self.glow_effect.setColor(QColor(0, 255, 255, 180))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)
    
    def update_effects(self):
        """Actualizar efectos de animación"""
        # Animación de brillo pulsante
        self.glow_intensity = 0.3 + 0.5 * (1 + math.sin(self.animation_timer.remainingTime() * 0.01)) / 2
        self.glow_effect.setColor(QColor(0, 255, 255, int(180 * self.glow_intensity)))
        
        # Líneas de escaneo
        self.scan_line_position = (self.scan_line_position + 2) % self.height()
        self.update()
    
    def paintEvent(self, event):
        """Dibujar efectos holográficos personalizados"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Líneas de escaneo horizontales
        pen = QPen(QColor(0, 255, 255, 50), 1)
        painter.setPen(pen)
        
        for i in range(0, self.height(), 8):
            y = (i + self.scan_line_position) % self.height()
            painter.drawLine(0, y, self.width(), y)
        
        # Borde holográfico
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(0, 255, 255, 100))
        gradient.setColorAt(0.5, QColor(255, 255, 255, 50))
        gradient.setColorAt(1, QColor(0, 255, 255, 100))
        
        pen = QPen(QBrush(gradient), 2)
        painter.setPen(pen)
        painter.drawRect(self.rect())


class PulsingButton(QPushButton):
    """Botón con efecto de pulsación holográfica"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.pulse_intensity = 0.0
        self.is_active = False
        
        # Timer para animación
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.update_pulse)
        self.pulse_timer.start(50)
        
        self.setup_style()
    
    def setup_style(self):
        """Configurar estilo holográfico"""
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 100),
                    stop:0.5 rgba(0, 150, 150, 80),
                    stop:1 rgba(0, 255, 255, 100));
                border: 2px solid cyan;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 150),
                    stop:0.5 rgba(0, 200, 200, 120),
                    stop:1 rgba(0, 255, 255, 150));
                box-shadow: 0 0 20px cyan;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 0, 150),
                    stop:0.5 rgba(255, 200, 0, 120),
                    stop:1 rgba(255, 255, 0, 150));
                border-color: yellow;
            }
        """)
        
        # Efecto de brillo
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(15)
        self.glow_effect.setColor(QColor(0, 255, 255, 150))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)
    
    def update_pulse(self):
        """Actualizar efecto de pulsación"""
        if self.is_active:
            self.pulse_intensity = 0.5 + 0.5 * math.sin(self.pulse_timer.remainingTime() * 0.02)
            glow_alpha = int(100 + 100 * self.pulse_intensity)
            self.glow_effect.setColor(QColor(255, 255, 0, glow_alpha))
        else:
            self.pulse_intensity = 0.3 + 0.2 * math.sin(self.pulse_timer.remainingTime() * 0.01)
            glow_alpha = int(50 + 100 * self.pulse_intensity)
            self.glow_effect.setColor(QColor(0, 255, 255, glow_alpha))
    
    def set_active(self, active):
        """Cambiar estado activo"""
        self.is_active = active


class HolographicTextArea(QTextEdit):
    """Área de texto con efectos holográficos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_holographic_style()
        
        # Animación de texto
        self.text_timer = QTimer()
        self.text_timer.timeout.connect(self.update_text_effects)
        self.text_timer.start(100)
    
    def setup_holographic_style(self):
        """Configurar estilo holográfico para texto"""
        self.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 50, 50, 200),
                    stop:0.5 rgba(0, 20, 20, 180),
                    stop:1 rgba(0, 50, 50, 200));
                border: 1px solid cyan;
                border-radius: 8px;
                color: #00ffff;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                selection-background-color: rgba(0, 255, 255, 100);
                padding: 10px;
            }
            QScrollBar:vertical {
                background: rgba(0, 50, 50, 100);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 255, 255, 150),
                    stop:1 rgba(0, 150, 150, 100));
                border-radius: 6px;
            }
        """)
        
        # Efecto de brillo sutil
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(10)
        glow.setColor(QColor(0, 255, 255, 100))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)
    
    def update_text_effects(self):
        """Actualizar efectos de texto"""
        # Hacer que el cursor parpadee con efecto holográfico
        pass


class JarvisHolographicApp(QMainWindow):
    """Aplicación principal de Jarvis con interfaz holográfica"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Configuración
        self.config = self.load_config()
        
        # Componentes
        self.audio_manager = None
        self.worker = None
        self.tray_icon = None
        
        # Efectos y animaciones
        self.opacity_animation = None
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_scan_lines)
        self.scan_timer.start(100)
        
        # Inicializar
        self.init_ui()
        self.init_audio_manager()
        self.init_worker()
        self.init_tray_icon()
        self.setup_holographic_effects()
        
        self.logger.info("Jarvis Holográfico iniciado correctamente")
    
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
            'UI_TRANSPARENCY': float(os.getenv('UI_TRANSPARENCY', 0.9)),
            'UI_ALWAYS_ON_TOP': os.getenv('UI_ALWAYS_ON_TOP', 'true').lower() == 'true',
        }
    
    def init_ui(self):
        """Inicializar interfaz holográfica"""
        self.setWindowTitle("J.A.R.V.I.S - Holographic Interface")
        
        # Auto-ajustar a la pantalla (80% del tamaño de pantalla)
        screen = QApplication.desktop().screenGeometry()
        window_width = int(screen.width() * 0.8)
        window_height = int(screen.height() * 0.8)
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)
        
        # Configurar ventana con controles personalizados
        self.setAttribute(Qt.WA_TranslucentBackground)
        window_flags = Qt.FramelessWindowHint
        if self.config.get('UI_ALWAYS_ON_TOP'):
            window_flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        
        # Variables para arrastrar ventana
        self.dragging = False
        self.drag_position = None
        
        # Widget central holográfico
        central_widget = HolographicWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Barra de título personalizada
        self.create_custom_title_bar(layout)
        
        # Header holográfico
        self.create_holographic_header(layout)
        
        # Área de conversación
        self.response_area = HolographicTextArea()
        self.response_area.setMinimumHeight(300)
        layout.addWidget(self.response_area)
        
        # Barra de progreso holográfica
        self.create_holographic_progress(layout)
        
        # Panel de control
        self.create_control_panel(layout)
        
        # Status bar holográfico
        self.create_status_bar(layout)
        
        # Aplicar transparencia
        self.setWindowOpacity(self.config.get('UI_TRANSPARENCY', 0.9))
    
    def create_custom_title_bar(self, layout):
        """Crear barra de título personalizada con controles de ventana"""
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 50, 50, 200),
                    stop:0.5 rgba(0, 100, 100, 180),
                    stop:1 rgba(0, 50, 50, 200));
                border: 1px solid cyan;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        # Icono y título
        title_label = QLabel("◊ J.A.R.V.I.S ◊ Holographic Interface")
        title_label.setFont(QFont("Orbitron", 12, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                background: transparent;
                padding: 5px;
            }
        """)
        title_layout.addWidget(title_label)
        
        # Espaciador
        title_layout.addStretch()
        
        # Botones de control de ventana
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(5)
        
        # Botón minimizar
        self.minimize_button = QPushButton("◈")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 0, 120),
                    stop:1 rgba(200, 200, 0, 100));
                border: 1px solid #ffff00;
                border-radius: 15px;
                color: black;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 0, 160),
                    stop:1 rgba(220, 220, 0, 140));
                box-shadow: 0 0 10px #ffff00;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 200, 0, 120),
                    stop:1 rgba(150, 150, 0, 100));
            }
        """)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.minimize_button.setToolTip("Minimizar")
        controls_layout.addWidget(self.minimize_button)
        
        # Botón maximizar/restaurar
        self.maximize_button = QPushButton("◊")
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 0, 120),
                    stop:1 rgba(0, 200, 0, 100));
                border: 1px solid #00ff00;
                border-radius: 15px;
                color: black;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 0, 160),
                    stop:1 rgba(0, 220, 0, 140));
                box-shadow: 0 0 10px #00ff00;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 200, 0, 120),
                    stop:1 rgba(0, 150, 0, 100));
            }
        """)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.maximize_button.setToolTip("Maximizar/Restaurar")
        controls_layout.addWidget(self.maximize_button)
        
        # Botón cerrar
        close_button = QPushButton("◐")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 0, 0, 120),
                    stop:1 rgba(200, 0, 0, 100));
                border: 1px solid #ff0000;
                border-radius: 15px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 0, 0, 160),
                    stop:1 rgba(220, 0, 0, 140));
                box-shadow: 0 0 10px #ff0000;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 0, 0, 120),
                    stop:1 rgba(150, 0, 0, 100));
            }
        """)
        close_button.clicked.connect(self.exit_application)
        close_button.setToolTip("Cerrar")
        controls_layout.addWidget(close_button)
        
        title_layout.addWidget(controls_frame)
        
        # Hacer que la barra de título sea arrastrable
        title_bar.mousePressEvent = self.title_bar_mouse_press
        title_bar.mouseMoveEvent = self.title_bar_mouse_move
        title_bar.mouseReleaseEvent = self.title_bar_mouse_release
        
        layout.addWidget(title_bar)
    
    def create_holographic_header(self, layout):
        """Crear header holográfico"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 100, 100, 150),
                    stop:0.5 rgba(0, 255, 255, 100),
                    stop:1 rgba(0, 100, 100, 150));
                border: 2px solid cyan;
                border-radius: 15px;
                margin: 5px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        # Título principal
        title_label = QLabel("◊ J.A.R.V.I.S ◊")
        title_label.setFont(QFont("Orbitron", 24, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                background: transparent;
                padding: 10px;
                text-align: center;
                text-shadow: 0 0 10px #00ffff;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("◈ HOLOGRAPHIC ARTIFICIAL INTELLIGENCE INTERFACE ◈")
        subtitle_label.setFont(QFont("Courier New", 10, QFont.Bold))
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #88ffff;
                background: transparent;
                padding: 5px;
                text-align: center;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        # Powered by Gemini
        gemini_label = QLabel("⬢ POWERED BY GOOGLE GEMINI ⬢")
        gemini_label.setFont(QFont("Arial", 8, QFont.Bold))
        gemini_label.setStyleSheet("""
            QLabel {
                color: #44ffff;
                background: transparent;
                padding: 5px;
                text-align: center;
            }
        """)
        gemini_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(gemini_label)
        
        layout.addWidget(header_frame)
    
    def create_holographic_progress(self, layout):
        """Crear barra de progreso holográfica"""
        self.audio_progress = QProgressBar()
        self.audio_progress.setVisible(False)
        self.audio_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid cyan;
                border-radius: 8px;
                background: rgba(0, 50, 50, 150);
                color: white;
                font-weight: bold;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 255, 255, 200),
                    stop:0.5 rgba(255, 255, 0, 200),
                    stop:1 rgba(0, 255, 255, 200));
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.audio_progress)
    
    def create_control_panel(self, layout):
        """Crear panel de control holográfico"""
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 30, 30, 180);
                border: 1px solid cyan;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(15)
        
        # Área de entrada de texto
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_area = QLineEdit()
        self.input_area.setPlaceholderText("◈ TYPE YOUR MESSAGE TO JARVIS ◈")
        self.input_area.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 50, 50, 200),
                    stop:0.5 rgba(0, 20, 20, 180),
                    stop:1 rgba(0, 50, 50, 200));
                border: 2px solid cyan;
                border-radius: 8px;
                color: #00ffff;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #00ffff;
                box-shadow: 0 0 10px cyan;
            }
        """)
        self.input_area.returnPressed.connect(self.send_text_message)
        input_layout.addWidget(self.input_area)
        
        # Botón de envío
        send_button = PulsingButton("◆ SEND ◆")
        send_button.clicked.connect(self.send_text_message)
        send_button.setFixedWidth(80)
        input_layout.addWidget(send_button)
        
        control_layout.addWidget(input_frame)
        
        # Panel de botones
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(15)
        
        # Botón de escucha
        self.listen_button = PulsingButton("◈ ACTIVATE LISTENING ◈")
        self.listen_button.clicked.connect(self.toggle_listening)
        button_layout.addWidget(self.listen_button)
        
        # Botón de parada
        self.stop_button = PulsingButton("◊ STOP PROCESS ◊")
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 100, 100, 100),
                    stop:0.5 rgba(200, 50, 50, 80),
                    stop:1 rgba(255, 100, 100, 100));
                border: 2px solid #ff4444;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                box-shadow: 0 0 20px #ff4444;
            }
        """)
        button_layout.addWidget(self.stop_button)
        
        # Botón para examinar páginas web
        web_button = PulsingButton("🌐 WEB BROWSER 🌐")
        web_button.clicked.connect(self.open_web_browser)
        web_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 100, 255, 120),
                    stop:0.5 rgba(0, 50, 200, 100),
                    stop:1 rgba(0, 100, 255, 120));
                border: 2px solid #0066ff;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                box-shadow: 0 0 20px #0066ff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 120, 255, 140),
                    stop:0.5 rgba(0, 70, 220, 120),
                    stop:1 rgba(0, 120, 255, 140));
            }
        """)
        button_layout.addWidget(web_button)
        
        # Botón de configuración
        config_button = PulsingButton("⚙ SYSTEM CONFIG ⚙")
        config_button.clicked.connect(self.show_config)
        button_layout.addWidget(config_button)
        
        # Botón de auto-ajuste
        auto_resize_button = PulsingButton("📐 AUTO RESIZE 📐")
        auto_resize_button.clicked.connect(self.auto_resize_to_content)
        auto_resize_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 200, 255, 120),
                    stop:0.5 rgba(50, 150, 255, 100),
                    stop:1 rgba(100, 200, 255, 120));
                border: 2px solid #64c8ff;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                box-shadow: 0 0 20px #64c8ff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(120, 220, 255, 140),
                    stop:0.5 rgba(70, 170, 255, 120),
                    stop:1 rgba(120, 220, 255, 140));
            }
        """)
        button_layout.addWidget(auto_resize_button)
        
        # Separador visual
        separator1 = QLabel("═" * 50)
        separator1.setAlignment(Qt.AlignCenter)
        separator1.setStyleSheet("color: #00ffff; font-size: 8px; padding: 5px;")
        button_layout.addWidget(separator1)
        
        # BOTONES DE FUNCIONALIDADES AVANZADAS
        
        # Botón de Traductor de Código
        code_translator_btn = PulsingButton("🔄 CODE TRANSLATOR 🔄")
        code_translator_btn.clicked.connect(self.open_code_translator)
        code_translator_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 165, 0, 120),
                    stop:0.5 rgba(255, 140, 0, 100),
                    stop:1 rgba(255, 165, 0, 120));
                border: 2px solid #ffa500;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                box-shadow: 0 0 20px #ffa500;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 185, 0, 140),
                    stop:0.5 rgba(255, 160, 0, 120),
                    stop:1 rgba(255, 185, 0, 140));
            }
        """)
        button_layout.addWidget(code_translator_btn)
        
        # Botón de Migrador de BD
        db_migrator_btn = PulsingButton("🗄️ DATABASE MIGRATOR 🗄️")
        db_migrator_btn.clicked.connect(self.open_db_migrator)
        db_migrator_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(128, 0, 128, 120),
                    stop:0.5 rgba(100, 0, 100, 100),
                    stop:1 rgba(128, 0, 128, 120));
                border: 2px solid #800080;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                box-shadow: 0 0 20px #800080;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(148, 0, 148, 140),
                    stop:0.5 rgba(120, 0, 120, 120),
                    stop:1 rgba(148, 0, 148, 140));
            }
        """)
        button_layout.addWidget(db_migrator_btn)
        
        # Botón de Visualizador de Archivos
        file_viewer_btn = PulsingButton("📄 FILE ANALYZER 📄")
        file_viewer_btn.clicked.connect(self.open_file_analyzer)
        file_viewer_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 128, 0, 120),
                    stop:0.5 rgba(0, 100, 0, 100),
                    stop:1 rgba(0, 128, 0, 120));
                border: 2px solid #008000;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                box-shadow: 0 0 20px #008000;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 148, 0, 140),
                    stop:0.5 rgba(0, 120, 0, 120),
                    stop:1 rgba(0, 148, 0, 140));
            }
        """)
        button_layout.addWidget(file_viewer_btn)
        
        # Botón de Gestor de Correo
        email_manager_btn = PulsingButton("📧 EMAIL MANAGER 📧")
        email_manager_btn.clicked.connect(self.open_email_manager)
        email_manager_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(220, 20, 60, 120),
                    stop:0.5 rgba(200, 20, 40, 100),
                    stop:1 rgba(220, 20, 60, 120));
                border: 2px solid #dc143c;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                box-shadow: 0 0 20px #dc143c;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(240, 40, 80, 140),
                    stop:0.5 rgba(220, 40, 60, 120),
                    stop:1 rgba(240, 40, 80, 140));
            }
        """)
        button_layout.addWidget(email_manager_btn)
        
        # Botón de Buscador de Archivos
        file_search_btn = PulsingButton("🔍 FILE SEARCH 🔍")
        file_search_btn.clicked.connect(self.open_file_search)
        file_search_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 215, 0, 120),
                    stop:0.5 rgba(255, 195, 0, 100),
                    stop:1 rgba(255, 215, 0, 120));
                border: 2px solid #ffd700;
                border-radius: 10px;
                color: black;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                box-shadow: 0 0 20px #ffd700;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 235, 0, 140),
                    stop:0.5 rgba(255, 215, 0, 120),
                    stop:1 rgba(255, 235, 0, 140));
            }
        """)
        button_layout.addWidget(file_search_btn)
        
        # Separador visual
        separator2 = QLabel("═" * 50)
        separator2.setAlignment(Qt.AlignCenter)
        separator2.setStyleSheet("color: #00ffff; font-size: 8px; padding: 5px;")
        button_layout.addWidget(separator2)
        
        # Botón de salir
        exit_button = PulsingButton("◊ EXIT SYSTEM ◊")
        exit_button.clicked.connect(self.exit_application)
        exit_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 50, 50, 120),
                    stop:0.5 rgba(200, 20, 20, 100),
                    stop:1 rgba(255, 50, 50, 120));
                border: 2px solid #ff2222;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                box-shadow: 0 0 20px #ff2222;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 80, 80, 140),
                    stop:0.5 rgba(220, 40, 40, 120),
                    stop:1 rgba(255, 80, 80, 140));
            }
        """)
        button_layout.addWidget(exit_button)
        
        control_layout.addWidget(button_frame)
        layout.addWidget(control_frame)
    
    def create_status_bar(self, layout):
        """Crear barra de estado holográfica"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 50, 50, 120),
                    stop:0.5 rgba(0, 80, 80, 100),
                    stop:1 rgba(0, 50, 50, 120));
                border: 1px solid cyan;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        
        # Indicador de estado
        self.status_indicator = QLabel("◈ SYSTEM IDLE ◈")
        self.status_indicator.setFont(QFont("Courier New", 10, QFont.Bold))
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #00ffff;
                background: transparent;
                padding: 8px;
            }
        """)
        status_layout.addWidget(self.status_indicator)
        
        # Espaciador
        status_layout.addStretch()
        
        # Información del sistema
        system_info = QLabel("◊ NEURAL NETWORK: ACTIVE ◊ VOICE SYNTHESIS: READY ◊")
        system_info.setFont(QFont("Courier New", 8))
        system_info.setStyleSheet("""
            QLabel {
                color: #88ffff;
                background: transparent;
                padding: 5px;
            }
        """)
        status_layout.addWidget(system_info)
        
        layout.addWidget(status_frame)
    
    def send_text_message(self):
        """Enviar mensaje de texto al worker"""
        text = self.input_area.text().strip()
        if not text:
            return
            
        # Mostrar mensaje del usuario en el área de respuesta
        user_message = f"""
╔════════════════════════════════════════════════════════╗
║  USER MESSAGE:                                          ║
║  {text:<54} ║
╚════════════════════════════════════════════════════════╝
"""
        self.response_area.append(user_message)
        
        # Limpiar el área de entrada
        self.input_area.clear()
        
        # Enviar al worker para procesamiento
        if hasattr(self.worker, 'procesar_comando_texto'):
            self.worker.procesar_comando_texto(text)
        else:
            self.show_error("Worker no disponible para procesar texto")
    
    def setup_holographic_effects(self):
        """Configurar efectos holográficos avanzados"""
        # Efecto de entrada
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(2000)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(self.config.get('UI_TRANSPARENCY', 0.9))
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.opacity_animation.start()
        
        # Mensaje de bienvenida holográfico
        welcome_msg = """
╔═══════════════════════════════════════════════════════╗
║             J.A.R.V.I.S SYSTEM INITIALIZED             ║
║                                                        ║
║  ◈ Holographic Interface: ACTIVE                      ║
║  ◈ Neural Network: GOOGLE GEMINI                      ║
║  ◈ Voice Synthesis: LOCAL PYTTSX3                     ║
║  ◈ Speech Recognition: READY                          ║
║  ◈ All Systems: OPERATIONAL                           ║
║                                                        ║
║         "At your service, sir."                       ║
╚═══════════════════════════════════════════════════════╝
        """
        self.response_area.append(welcome_msg)
    
    def update_scan_lines(self):
        """Actualizar líneas de escaneo"""
        # Este método se llama para efectos de escaneo continuos
        pass
    
    # Resto de métodos de la clase original...
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
            self.worker.respuestaLista.connect(self.on_response_ready)  # Conectar también la señal principal
            self.worker.errorOcurrido.connect(self.on_error)
            self.worker.estadoCambiado.connect(self.on_status_changed)
            self.worker.comandoReconocido.connect(self.on_voice_command_recognized)
            self.worker.start()
            self.logger.info("Worker iniciado")
        except Exception as e:
            self.logger.error(f"Error inicializando worker: {e}")
            self.show_error(f"Error del sistema: {e}")
    
    def init_tray_icon(self):
        """Inicializar icono de bandeja del sistema"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Mostrar J.A.R.V.I.S")
            show_action.triggered.connect(self.show)
            
            quit_action = tray_menu.addAction("Desactivar Sistema")
            quit_action.triggered.connect(self.close_application)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
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
            self.listen_button.setText("◈ LISTENING ACTIVE ◈")
            self.listen_button.set_active(True)
    
    def stop_listening(self):
        """Detener escucha"""
        if self.worker:
            self.worker.detener_escucha()
            self.listen_button.setText("◈ ACTIVATE LISTENING ◈")
            self.listen_button.set_active(False)
    
    def on_voice_command_recognized(self, command: str):
        """Manejar comando de voz reconocido"""
        # Mostrar comando reconocido en la interfaz
        voice_message = f"""
╔════════════════════════════════════════════════════════╗
║  🎤 VOICE COMMAND RECOGNIZED:                          ║
║  {command:<54} ║
╚════════════════════════════════════════════════════════╝
"""
        self.response_area.append(voice_message)
        
        # Log para depuración
        self.logger.info(f"Comando de voz reconocido en interfaz: {command}")
        
        # Enfocar área de respuesta para que el usuario vea el comando
        self.response_area.ensureCursorVisible()

    def on_response_ready(self, response: str):
        """Manejar respuesta lista - mantener hilo de conversación con comentario más reciente"""
        # Mostrar respuesta completa en pantalla
        formatted_response = f"""
┌─ J.A.R.V.I.S RESPONSE ─────────────────────────────────┐
│ {response:<54} │
└────────────────────────────────────────────────────────┘
        """
        self.response_area.append(formatted_response)
        
        # Para audio, extraer solo el comentario/respuesta más reciente
        if self.audio_manager:
            # Extraer el comentario más reciente para mantener hilo de conversación
            latest_comment = self.extract_latest_conversation_point(response)
            if latest_comment:
                self.generate_and_play_audio(latest_comment)
    
    def extract_latest_conversation_point(self, response: str) -> str:
        """Extraer el comentario/respuesta más reciente para mantener hilo de conversación"""
        try:
            # Limpiar caracteres especiales de formato
            clean_text = response.replace('🔍', '').replace('📄', '').replace('📁', '')
            clean_text = clean_text.replace('📏', '').replace('🏷️', '').replace('📂', '')
            clean_text = clean_text.replace('📅', '').replace('✅', '').replace('💡', '')
            clean_text = clean_text.replace('═', '').replace('─', '').replace('**', '')
            clean_text = clean_text.replace('┌', '').replace('┐', '').replace('└', '')
            clean_text = clean_text.replace('┘', '').replace('│', '').replace('╔', '')
            clean_text = clean_text.replace('╗', '').replace('╚', '').replace('╝', '')
            clean_text = clean_text.replace('║', '').replace('🌐', '').replace('◈', '')
            
            # Dividir en líneas y limpiar
            lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
            
            if not lines:
                return "Respuesta procesada"
            
            # Buscar patrones de respuesta directa (comentarios recientes)
            conversation_patterns = [
                # Respuestas directas
                r'(?:Te he|He|Aquí tienes|Encontré|Puedo|Claro|Por supuesto|Perfecto)',
                # Confirmaciones
                r'(?:Listo|Terminado|Completado|Realizado|Ejecutado)',
                # Preguntas de seguimiento
                r'(?:¿|¿.*\?|¿Necesitas|¿Te gustaría|¿Quieres)',
                # Explicaciones
                r'(?:Esto significa|En resumen|Básicamente|En otras palabras)'
            ]
            
            # Buscar la línea más relevante para TTS (comentario directo)
            import re
            for line in lines:
                if len(line) > 15:  # Líneas con contenido sustancial
                    for pattern in conversation_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Encontró un comentario directo - usar esta línea
                            return self.clean_line_for_speech(line)
            
            # Si no encuentra patrones específicos, analizar tipo de respuesta
            response_lower = clean_text.lower()
            
            # Listas de archivos o resultados múltiples
            if ('archivos encontrados' in response_lower or 
                'resultados' in response_lower or
                len(lines) > 8):
                first_meaningful = next((line for line in lines if len(line) > 20), lines[0])
                return f"{self.clean_line_for_speech(first_meaningful)}. Consulta la pantalla para ver todos los detalles."
            
            # Respuestas técnicas (código, configuración, etc.)
            if any(keyword in response_lower for keyword in ['código', 'función', 'configuración', 'sistema', 'comando']):
                # Tomar primera línea explicativa
                explanation_line = next((line for line in lines if len(line) > 15 and not line.startswith('{')), lines[0])
                return f"{self.clean_line_for_speech(explanation_line)}. Revisa la pantalla para los detalles técnicos."
            
            # Conversación normal - tomar las primeras 2-3 líneas más relevantes
            meaningful_lines = [line for line in lines[:5] if len(line) > 10]
            if meaningful_lines:
                # Combinar las primeras líneas para mantener contexto
                conversation_text = '. '.join(meaningful_lines[:2])
                if len(conversation_text) > 150:
                    conversation_text = meaningful_lines[0]
                return self.clean_line_for_speech(conversation_text)
            
            # Fallback - primera línea disponible
            return self.clean_line_for_speech(lines[0])
            
        except Exception as e:
            self.logger.error(f"Error extrayendo comentario de conversación: {e}")
            return "He procesado tu solicitud. Consulta la pantalla para más detalles."
    
    def clean_line_for_speech(self, line: str) -> str:
        """Limpiar una línea específica para síntesis de voz"""
        try:
            # Eliminar caracteres especiales restantes
            cleaned = line.replace('*', '').replace('#', '').replace('>', '').replace('<', '')
            cleaned = cleaned.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
            cleaned = cleaned.replace('{', '').replace('}', '').replace('|', '')
            cleaned = cleaned.replace('`', '').replace('~', '').replace('^', '')
            
            # Eliminar espacios múltiples
            cleaned = ' '.join(cleaned.split())
            
            # Truncar si es muy largo
            if len(cleaned) > 120:
                # Buscar último punto o coma antes del límite
                truncate_pos = 120
                for i in range(120, max(80, len(cleaned)-40), -1):
                    if cleaned[i] in '.,:;':
                        truncate_pos = i + 1
                        break
                cleaned = cleaned[:truncate_pos].strip()
            
            return cleaned.strip()
            
        except Exception as e:
            self.logger.error(f"Error limpiando línea para voz: {e}")
            return line.strip()

    def clean_response_for_tts(self, response: str) -> str:
        """Limpiar respuesta para síntesis de voz - solo contenido esencial"""
        try:
            # Eliminar caracteres especiales de formato
            clean_text = response.replace('🔍', '').replace('📄', '').replace('📁', '')
            clean_text = clean_text.replace('📏', '').replace('🏷️', '').replace('📂', '')
            clean_text = clean_text.replace('📅', '').replace('✅', '').replace('💡', '')
            clean_text = clean_text.replace('═', '').replace('─', '').replace('**', '')
            clean_text = clean_text.replace('┌', '').replace('┐', '').replace('└', '')
            clean_text = clean_text.replace('┘', '').replace('│', '').replace('╔', '')
            clean_text = clean_text.replace('╗', '').replace('╚', '').replace('╝', '')
            clean_text = clean_text.replace('║', '').replace('🌐', '').replace('◈', '')
            
            # Limpiar líneas vacías múltiples
            lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
            
            # Si es una lista de archivos, resumir para TTS
            if len(lines) > 5 and any('archivos' in line.lower() for line in lines[:3]):
                # Es una lista de archivos - crear resumen hablado
                first_line = lines[0] if lines else ""
                return f"{first_line}. Consulte la pantalla para ver todos los detalles."
            
            # Si es muy largo, truncar para TTS pero mantener información clave
            text_to_speak = ' '.join(lines)
            if len(text_to_speak) > 200:
                # Tomar las primeras líneas importantes
                important_lines = [line for line in lines[:3] if len(line) > 10]
                text_to_speak = ' '.join(important_lines[:2])
                text_to_speak += ". Consulte la pantalla para más detalles."
            
            return text_to_speak.strip()
            
        except Exception as e:
            self.logger.error(f"Error limpiando respuesta para TTS: {e}")
            return "Respuesta procesada. Consulte la pantalla para detalles."
    
    def on_error(self, error: str):
        """Manejar errores"""
        self.show_error(error)
    
    def on_status_changed(self, status: str):
        """Manejar cambio de estado"""
        status_icons = {
            'IDLE': '◈ SYSTEM IDLE ◈',
            'LISTENING': '◈ LISTENING MODE ACTIVE ◈',
            'PROCESSING': '◈ NEURAL PROCESSING ◈',
            'SPEAKING': '◈ VOICE SYNTHESIS ACTIVE ◈',
            'ERROR': '◈ SYSTEM ERROR ◈'
        }
        
        display_status = status_icons.get(status, f'◈ {status} ◈')
        self.status_indicator.setText(display_status)
    
    def on_audio_finished(self):
        """Manejar fin de reproducción de audio"""
        self.audio_progress.setVisible(False)
    
    def on_audio_error(self, error: str):
        """Manejar error de audio"""
        self.show_error(f"Error de audio: {error}")
    
    def generate_and_play_audio(self, text: str):
        """Generar y reproducir audio"""
        try:
            if self.audio_manager:
                self.audio_progress.setVisible(True)
                self.audio_manager.speak_text(text)
        except Exception as e:
            self.logger.error(f"Error generando audio: {e}")
    
    def show_error(self, message: str):
        """Mostrar mensaje de error holográfico"""
        error_msg = f"""
╔══ SYSTEM ERROR ═══════════════════════════════════════╗
║ ⚠ {message:<50} ⚠ ║
╚═══════════════════════════════════════════════════════╝
        """
        self.response_area.append(error_msg)
        self.logger.error(message)
    
    def show_config(self):
        """Mostrar configuración"""
        config_msg = """
╔══ SYSTEM CONFIGURATION ═══════════════════════════════╗
║  ◈ AI Engine: Google Gemini Pro                      ║
║  ◈ Voice Provider: PyTTSx3 Local                     ║
║  ◈ Speech Recognition: Google                        ║
║  ◈ Interface: Holographic Mode                       ║
║  ◈ Status: All Systems Operational                   ║
║                                                       ║
║  ◈ WINDOW CONTROLS:                                   ║
║  • Minimize: ◈ button or Ctrl+Esc                   ║
║  • Maximize: ◊ button or F11 or Alt+Enter           ║
║  • Auto-resize: 📐 button or Ctrl+0                  ║
║  • Drag: Click and drag title bar                    ║
║  • Close: ◐ button or standard exit                  ║
║                                                       ║
║  ◈ AUTO-ADJUSTMENT FEATURES:                          ║
║  • Smart screen sizing (80% of display)              ║
║  • Content-based auto-resize                         ║
║  • Responsive layout scaling                         ║
║  • Holographic effects adaptation                    ║
╚═══════════════════════════════════════════════════════╝
        """
        self.response_area.append(config_msg)
    
    def open_web_browser(self):
        """Abrir navegador web para examinar páginas"""
        try:
            # Mostrar mensaje al usuario
            web_prompt = """
╔═══════════════════════════════════════════════════════╗
║             WEB BROWSER INTERFACE                     ║
║                                                       ║
║  Para examinar páginas web, use comandos como:       ║
║                                                       ║
║  • "abrir página google"                             ║
║  • "examinar web youtube"                            ║  
║  • "ir a facebook"                                   ║
║  • "abrir sitio github.com"                         ║
║  • "navegar a https://www.ejemplo.com"              ║
║                                                       ║
║  También puedo buscar en Google cualquier tema.      ║
╚═══════════════════════════════════════════════════════╝

💡 Escriba su comando en el área de texto y presione SEND.
            """
            self.response_area.append(web_prompt)
            
            # Enfocar el área de entrada para que el usuario pueda escribir
            self.input_area.setFocus()
            
            self.logger.info("Interfaz web activada - esperando comandos del usuario")
            
        except Exception as e:
            self.logger.error(f"Error activando interfaz web: {e}")
            self.show_error(f"Error activando navegador web: {e}")
    
    def exit_application(self):
        """Salir de la aplicación de forma segura"""
        try:
            self.logger.info("Iniciando cierre seguro de JARVIS...")
            
            # Mostrar mensaje de despedida
            goodbye_msg = """
╔═══════════════════════════════════════════════════════╗
║             JARVIS SYSTEM SHUTDOWN                    ║
║                                                       ║
║  ◈ Disconnecting neural networks...                  ║
║  ◈ Saving system state...                           ║
║  ◈ Powering down holographic interface...           ║
║                                                       ║
║           Until next time, sir. JARVIS out.          ║
╚═══════════════════════════════════════════════════════╝
            """
            self.response_area.append(goodbye_msg)
            
            # Detener worker si está ejecutándose
            if hasattr(self, 'worker') and self.worker:
                if self.worker.isRunning():
                    self.worker.quit()
                    self.worker.wait(3000)  # Esperar máximo 3 segundos
            
            # Detener audio manager
            if hasattr(self, 'audio_manager') and self.audio_manager:
                # Detener cualquier reproducción en curso
                if hasattr(self.audio_manager, 'media_player'):
                    self.audio_manager.media_player.stop()
            
            self.logger.info("JARVIS desconectado correctamente")
            
            # Cerrar aplicación después de un breve delay
            QTimer.singleShot(2000, QApplication.quit)
            
        except Exception as e:
            self.logger.error(f"Error durante el cierre: {e}")
            QApplication.quit()
    
    def closeEvent(self, event):
        """Manejar evento de cierre"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.close_application()
    
    def open_code_translator(self):
        """Abrir interfaz del traductor de código"""
        try:
            translator_prompt = """
╔═══════════════════════════════════════════════════════╗
║                CODE TRANSLATOR INTERFACE              ║
║                                                       ║
║  🔄 Traduzca código entre 17 lenguajes diferentes:    ║
║                                                       ║
║  📋 LENGUAJES SOPORTADOS:                             ║
║  • Python ↔ Java, JavaScript, TypeScript, C++, C#    ║
║  • Java ↔ Python, JavaScript, Kotlin, Scala          ║
║  • JavaScript ↔ Python, Java, TypeScript, Go         ║
║  • C++ ↔ Python, Java, C#, Rust                      ║
║  • Y muchos más...                                    ║
║                                                       ║
║  💡 EJEMPLOS DE COMANDOS:                             ║
║  • "traducir código de python a java"                ║
║  • "convertir archivo main.py de python a javascript"║
║  • "migrar código de java a kotlin"                  ║
║  • "transformar de c++ a rust"                       ║
║                                                       ║
║  📁 SELECCIÓN DE ARCHIVO:                             ║
║  • Use el comando con nombre de archivo específico    ║
║  • O proporcione el código directamente               ║
║                                                       ║
║  ✅ CARACTERÍSTICAS:                                  ║
║  • Preserva lógica del código original               ║
║  • Optimiza para el lenguaje destino                 ║
║  • Guarda automáticamente en Desktop                 ║
║  • Incluye comentarios explicativos                  ║
╚═══════════════════════════════════════════════════════╝

💻 Escriba su comando de traducción en el área de texto.
📎 Ejemplo: "traducir archivo main.py de python a java"
            """
            self.response_area.append(translator_prompt)
            self.input_area.setFocus()
            self.logger.info("Interfaz de traductor de código activada")
            
        except Exception as e:
            self.logger.error(f"Error activando traductor de código: {e}")
            self.show_error(f"Error en traductor de código: {e}")
    
    def open_db_migrator(self):
        """Abrir interfaz del migrador de bases de datos"""
        try:
            migrator_prompt = """
╔═══════════════════════════════════════════════════════╗
║               DATABASE MIGRATOR INTERFACE             ║
║                                                       ║
║  🗄️ Migre esquemas entre 12 sistemas de BD:          ║
║                                                       ║
║  📋 SISTEMAS SOPORTADOS:                              ║
║  • RELACIONALES: PostgreSQL, MySQL, SQL Server       ║
║  • RELACIONALES: Oracle, SQLite, MariaDB             ║
║  • NoSQL: MongoDB, Firebase, Cassandra               ║
║  • OTROS: Redis, DynamoDB, Neo4j                     ║
║                                                       ║
║  💡 EJEMPLOS DE COMANDOS:                             ║
║  • "migrar de postgresql a mysql"                    ║
║  • "convertir esquema.sql de mysql a postgresql"     ║
║  • "transformar de mongodb a postgresql"             ║
║  • "migrar de sql server a postgresql"               ║
║                                                       ║
║  📁 SELECCIÓN DE ARCHIVO:                             ║
║  • Use el comando con nombre de archivo .sql         ║
║  • O proporcione el esquema directamente             ║
║                                                       ║
║  ✅ CARACTERÍSTICAS:                                  ║
║  • Conversión automática de tipos de datos           ║
║  • Adapta sintaxis específica de cada motor          ║
║  • Preserva integridad referencial                   ║
║  • Optimiza para el sistema destino                  ║
╚═══════════════════════════════════════════════════════╝

🗄️ Escriba su comando de migración en el área de texto.
📎 Ejemplo: "migrar archivo esquema.sql de postgresql a mysql"
            """
            self.response_area.append(migrator_prompt)
            self.input_area.setFocus()
            self.logger.info("Interfaz de migrador de BD activada")
            
        except Exception as e:
            self.logger.error(f"Error activando migrador de BD: {e}")
            self.show_error(f"Error en migrador de BD: {e}")
    
    def open_file_analyzer(self):
        """Abrir interfaz del analizador de archivos"""
        try:
            analyzer_prompt = """
╔═══════════════════════════════════════════════════════╗
║                FILE ANALYZER INTERFACE                ║
║                                                       ║
║  📄 Analice cualquier tipo de archivo:               ║
║                                                       ║
║  📋 TIPOS SOPORTADOS:                                 ║
║  • TEXTO: .txt, .py, .js, .html, .css, .json, .sql  ║
║  • IMÁGENES: .jpg, .png, .gif, .bmp, .webp, .tiff   ║
║  • VIDEOS: .mp4, .avi, .mkv, .mov, .wmv, .flv       ║
║  • AUDIO: .mp3, .wav, .flac, .aac, .ogg, .m4a       ║
║  • DOCUMENTOS: .pdf, .docx, .xlsx, .pptx             ║
║  • COMPRIMIDOS: .zip, .rar, .7z, .tar, .gz          ║
║                                                       ║
║  💡 EJEMPLOS DE COMANDOS:                             ║
║  • "mostrar archivo documento.pdf"                   ║
║  • "ver archivo imagen.jpg"                          ║
║  • "analizar archivo codigo.py"                      ║
║  • "examinar archivo base_datos.sql"                 ║
║                                                       ║
║  📁 SELECCIÓN DIRECTA:                                ║
║  Haga clic aquí para seleccionar archivo →           ║
║                                                       ║
║  ✅ INFORMACIÓN PROPORCIONADA:                        ║
║  • Ubicación completa del archivo                    ║
║  • Tamaño formateado y fecha de modificación         ║
║  • Tipo MIME y metadatos específicos                 ║
║  • Preview de contenido (archivos de texto)          ║
╚═══════════════════════════════════════════════════════╝

📄 Escriba su comando de análisis en el área de texto.
📎 O use: "mostrar archivo [nombre_archivo]"
            """
            self.response_area.append(analyzer_prompt)
            self.input_area.setFocus()
            self.logger.info("Interfaz de analizador de archivos activada")
            
        except Exception as e:
            self.logger.error(f"Error activando analizador de archivos: {e}")
            self.show_error(f"Error en analizador de archivos: {e}")
    
    def open_email_manager(self):
        """Abrir interfaz del gestor de correo"""
        try:
            email_prompt = """
╔═══════════════════════════════════════════════════════╗
║                EMAIL MANAGER INTERFACE                ║
║                                                       ║
║  📧 Gestione su correo Outlook de forma inteligente: ║
║                                                       ║
║  📋 FUNCIONALIDADES:                                  ║
║  • 📥 LECTURA: Abre Outlook automáticamente          ║
║  • 📤 RESPUESTAS: Genera respuestas profesionales    ║
║  • ✍️ REDACCIÓN: Asistencia en escritura de correos  ║
║  • 🌐 FALLBACK: Outlook Web si es necesario          ║
║                                                       ║
║  💡 EJEMPLOS DE COMANDOS:                             ║
║  • "revisar correo outlook"                          ║
║  • "responder correo sobre reunión"                  ║
║  • "contestar correo de agradecimiento"              ║
║  • "redactar correo formal"                          ║
║  • "escribir correo de seguimiento"                  ║
║                                                       ║
║  🚀 ACCESO DIRECTO:                                   ║
║  Este botón también abre Outlook automáticamente     ║
║                                                       ║
║  ✅ TIPOS DE RESPUESTA:                               ║
║  • Profesional formal • Amigable corporativo         ║
║  • Conciso y directo • Detallado e informativo       ║
║  • Diplomático • Confirmaciones de reuniones         ║
╚═══════════════════════════════════════════════════════╝

📧 Escriba su comando de correo en el área de texto.
📎 O simplemente comenzaré a abrir Outlook...
            """
            self.response_area.append(email_prompt)
            
            # Intentar abrir Outlook directamente también
            try:
                import subprocess
                subprocess.Popen("outlook", shell=True)
                self.response_area.append("\n✅ Outlook se está abriendo automáticamente...")
            except Exception:
                self.response_area.append("\n💡 Use comandos de voz para gestionar correo.")
            
            self.input_area.setFocus()
            self.logger.info("Interfaz de gestor de correo activada")
            
        except Exception as e:
            self.logger.error(f"Error activando gestor de correo: {e}")
            self.show_error(f"Error en gestor de correo: {e}")
    
    def open_file_search(self):
        """Abrir interfaz del buscador de archivos"""
        try:
            search_prompt = """
╔═══════════════════════════════════════════════════════╗
║                FILE SEARCH INTERFACE                  ║
║                                                       ║
║  🔍 Busque archivos en todo su sistema:              ║
║                                                       ║
║  📋 ÁREAS DE BÚSQUEDA:                                ║
║  • 🏠 Directorio de usuario completo                  ║
║  • 🖥️ Escritorio y Documentos                        ║
║  • 📥 Descargas y OneDrive                            ║
║  • 🖼️ Imágenes, Videos y Música                       ║
║  • 📂 Carpetas públicas del sistema                   ║
║                                                       ║
║  💡 EJEMPLOS DE COMANDOS:                             ║
║  • "buscar archivos python en mi pc"                 ║
║  • "encontrar documentos pdf"                        ║
║  • "localizar imágenes jpg"                          ║
║  • "buscar archivos sql"                             ║
║  • "encontrar archivos config"                       ║
║                                                       ║
║  🎯 BÚSQUEDA RÁPIDA:                                  ║
║  • "python" - encuentra archivos .py                 ║
║  • "pdf" - encuentra documentos PDF                  ║
║  • "imagen" - encuentra archivos de imagen           ║
║                                                       ║
║  ✅ INFORMACIÓN DETALLADA:                            ║
║  • Nombre completo y ubicación                       ║
║  • Tamaño y fecha de modificación                    ║
║  • Tipo de archivo y extensión                       ║
║  • Ordenado por relevancia y fecha                   ║
╚═══════════════════════════════════════════════════════╝

🔍 Escriba su término de búsqueda en el área de texto.
📎 Ejemplo: "buscar archivos python" o solo "python"
            """
            self.response_area.append(search_prompt)
            self.input_area.setFocus()
            self.logger.info("Interfaz de búsqueda de archivos activada")
            
        except Exception as e:
            self.logger.error(f"Error activando buscador de archivos: {e}")
            self.show_error(f"Error en buscador de archivos: {e}")
    
    def title_bar_mouse_press(self, event):
        """Manejar clic en barra de título para arrastrar"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def title_bar_mouse_move(self, event):
        """Manejar movimiento del mouse para arrastrar ventana"""
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def title_bar_mouse_release(self, event):
        """Manejar liberación del mouse"""
        self.dragging = False
        event.accept()
    
    def toggle_maximize(self):
        """Alternar entre maximizado y tamaño normal"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_button.setText("◊")
            self.maximize_button.setToolTip("Maximizar")
        else:
            self.showMaximized()
            self.maximize_button.setText("◈")
            self.maximize_button.setToolTip("Restaurar")
    
    def auto_resize_to_content(self):
        """Auto-ajustar ventana al contenido"""
        try:
            # Calcular tamaño mínimo necesario basado en contenido
            content_height = 0
            
            # Altura mínima para diferentes elementos
            title_bar_height = 40
            header_height = 120
            response_area_min = 300
            controls_height = 200
            status_bar_height = 60
            margins = 80
            
            content_height = (title_bar_height + header_height + 
                            response_area_min + controls_height + 
                            status_bar_height + margins)
            
            # Obtener tamaño de pantalla
            screen = QApplication.desktop().screenGeometry()
            
            # Calcular nuevo tamaño (mínimo 800x600, máximo 80% de pantalla)
            new_width = max(800, min(1200, int(screen.width() * 0.8)))
            new_height = max(600, min(content_height, int(screen.height() * 0.8)))
            
            # Centrar en pantalla
            x = (screen.width() - new_width) // 2
            y = (screen.height() - new_height) // 2
            
            self.setGeometry(x, y, new_width, new_height)
            
            self.logger.info(f"Ventana auto-redimensionada a {new_width}x{new_height}")
            
        except Exception as e:
            self.logger.error(f"Error en auto-redimensionamiento: {e}")
    
    def keyPressEvent(self, event):
        """Manejar teclas de acceso rápido"""
        # Alt + Enter: Toggle maximizar
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.AltModifier:
            self.toggle_maximize()
        # F11: Toggle maximizar
        elif event.key() == Qt.Key_F11:
            self.toggle_maximize()
        # Escape: Minimizar
        elif event.key() == Qt.Key_Escape and event.modifiers() == Qt.ControlModifier:
            self.showMinimized()
        # Ctrl + 0: Auto-redimensionar
        elif event.key() == Qt.Key_0 and event.modifiers() == Qt.ControlModifier:
            self.auto_resize_to_content()
        else:
            super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        """Manejar evento de redimensionamiento"""
        super().resizeEvent(event)
        # Actualizar efectos holográficos al redimensionar
        if hasattr(self, 'centralWidget'):
            self.centralWidget().update()
    
    def close_application(self):
        """Cerrar aplicación completamente"""
        self.logger.info("Cerrando J.A.R.V.I.S")
        
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(3000)
        
        QApplication.quit()


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Verificar soporte de bandeja del sistema
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("Sistema de bandeja no disponible")
    
    # Crear y mostrar interfaz holográfica
    jarvis_app = JarvisHolographicApp()
    jarvis_app.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

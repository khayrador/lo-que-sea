"""
Diseño base para Jarvis PyQt5 - Ventana principal
Este archivo simula lo que sería generado por Qt Designer
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFrame, QProgressBar, QTextEdit,
                            QSystemTrayIcon, QMenu, QAction, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QBrush
import sys


class JarvisMainWindowUI(QMainWindow):
    """Clase base de la interfaz de usuario de Jarvis"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_animations()
        self.setup_tray_icon()
    
    def init_ui(self):
        """Inicializar elementos de la interfaz"""
        self.setWindowTitle("J.A.R.V.I.S - Asistente Virtual")
        self.setGeometry(100, 100, 400, 600)
        
        # Ventana semi-transparente
        self.setWindowOpacity(0.95)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # === HEADER ===
        self.create_header()
        
        # === ÁREA DE ESTADO ===
        self.create_status_area()
        
        # === ÁREA DE VISUALIZACIÓN ===
        self.create_visualization_area()
        
        # === CONTROLES ===
        self.create_controls()
        
        # === ÁREA DE RESPUESTAS ===
        self.create_response_area()
        
        # Aplicar estilo
        self.apply_jarvis_style()
    
    def create_header(self):
        """Crear encabezado con logo y título"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Logo/Título
        self.title_label = QLabel("🤖 J.A.R.V.I.S")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        
        # Botones de control de ventana
        self.minimize_btn = QPushButton("_")
        self.close_btn = QPushButton("×")
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.minimize_btn)
        header_layout.addWidget(self.close_btn)
        
        self.main_layout.addWidget(header_frame)
    
    def create_status_area(self):
        """Crear área de estado con indicador circular"""
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        
        # Indicador de estado (círculo animado)
        self.status_indicator = QLabel("●")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setFont(QFont("Arial", 48))
        self.status_indicator.setStyleSheet("color: #00ff41;")
        
        # Texto de estado
        self.status_text = QLabel("IDLE")
        self.status_text.setAlignment(Qt.AlignCenter)
        self.status_text.setFont(QFont("Arial", 14, QFont.Bold))
        
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_text)
        
        self.main_layout.addWidget(status_frame)
    
    def create_visualization_area(self):
        """Crear área para visualizaciones (ondas de sonido, etc.)"""
        self.visualization_frame = QFrame()
        self.visualization_frame.setMinimumHeight(100)
        self.visualization_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 255, 65, 0.1);
                border: 2px solid #00ff41;
                border-radius: 10px;
            }
        """)
        
        # Barra de progreso para audio
        vis_layout = QVBoxLayout(self.visualization_frame)
        self.audio_progress = QProgressBar()
        self.audio_progress.setVisible(False)
        vis_layout.addWidget(self.audio_progress)
        
        self.main_layout.addWidget(self.visualization_frame)
    
    def create_controls(self):
        """Crear controles principales"""
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        
        # Botón principal del micrófono
        self.mic_button = QPushButton("🎤")
        self.mic_button.setFixedSize(80, 80)
        self.mic_button.setFont(QFont("Arial", 24))
        
        # Botones secundarios
        self.settings_btn = QPushButton("⚙️")
        self.history_btn = QPushButton("📚")
        self.help_btn = QPushButton("❓")
        
        controls_layout.addWidget(self.settings_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.mic_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.history_btn)
        controls_layout.addWidget(self.help_btn)
        
        self.main_layout.addWidget(controls_frame)
    
    def create_response_area(self):
        """Crear área para mostrar respuestas"""
        self.response_area = QTextEdit()
        self.response_area.setMaximumHeight(150)
        self.response_area.setPlaceholderText("Las respuestas de Jarvis aparecerán aquí...")
        self.response_area.setReadOnly(True)
        
        self.main_layout.addWidget(self.response_area)
    
    def setup_animations(self):
        """Configurar animaciones"""
        # Animación del indicador de estado
        self.status_animation = QPropertyAnimation(self.status_indicator, b"geometry")
        self.status_animation.setDuration(1000)
        self.status_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Efecto de opacidad para el micrófono
        self.mic_opacity_effect = QGraphicsOpacityEffect()
        self.mic_button.setGraphicsEffect(self.mic_opacity_effect)
        
        self.mic_animation = QPropertyAnimation(self.mic_opacity_effect, b"opacity")
        self.mic_animation.setDuration(500)
        self.mic_animation.setStartValue(1.0)
        self.mic_animation.setEndValue(0.5)
    
    def setup_tray_icon(self):
        """Configurar icono de bandeja del sistema"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Menú del icono de bandeja
        tray_menu = QMenu()
        
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show)
        
        quit_action = QAction("Salir", self)
        quit_action.triggered.connect(self.close)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def apply_jarvis_style(self):
        """Aplicar estilo visual tipo J.A.R.V.I.S"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
                color: #00ff41;
            }
            
            QLabel {
                color: #00ff41;
                background-color: transparent;
            }
            
            QFrame {
                background-color: rgba(0, 255, 65, 0.05);
                border: 1px solid #00ff41;
                border-radius: 5px;
            }
            
            QPushButton {
                background-color: rgba(0, 255, 65, 0.1);
                border: 2px solid #00ff41;
                border-radius: 5px;
                color: #00ff41;
                font-weight: bold;
                padding: 8px;
            }
            
            QPushButton:hover {
                background-color: rgba(0, 255, 65, 0.2);
                border: 2px solid #00ff65;
            }
            
            QPushButton:pressed {
                background-color: rgba(0, 255, 65, 0.3);
            }
            
            QTextEdit {
                background-color: rgba(0, 255, 65, 0.05);
                border: 1px solid #00ff41;
                border-radius: 5px;
                color: #00ff41;
                font-family: 'Courier New';
                padding: 10px;
            }
            
            QProgressBar {
                background-color: rgba(0, 255, 65, 0.1);
                border: 1px solid #00ff41;
                border-radius: 3px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #00ff41;
                border-radius: 3px;
            }
        """)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Permitir minimizar a bandeja
    
    window = JarvisMainWindowUI()
    window.show()
    
    sys.exit(app.exec_())

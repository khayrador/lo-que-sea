"""
Audio Manager para Jarvis PyQt5
Maneja síntesis de voz usando Coqui TTS y otros proveedores
"""

import os
import io
import logging
import tempfile
from typing import Dict, Any, Optional
import requests
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


class AudioManager(QObject):
    """Gestor de audio para síntesis de voz con Coqui TTS"""
    
    audioFinished = pyqtSignal()
    audioError = pyqtSignal(str)
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuración
        self.provider = config.get('VOICE_PROVIDER', 'pyttsx3')  # Cambiar default a pyttsx3
        self.tts_model = config.get('TTS_MODEL', 'tts_models/multilingual/multi-dataset/xtts_v2')
        self.tts_speaker = config.get('TTS_SPEAKER', 'Dionisio Schuyler')
        self.tts_language = config.get('TTS_LANGUAGE', 'es')
        self.tts_rate = float(config.get('TTS_RATE', 1.0))
        
        # Reproductor de audio
        self.media_player = QMediaPlayer()
        self.media_player.stateChanged.connect(self.on_player_state_changed)
        
        # Directorio temporal
        self.temp_dir = tempfile.mkdtemp()
        
        # Inicializar Coqui TTS
        self.tts_engine = None
        self.init_coqui_tts()
    
    def init_coqui_tts(self):
        """Inicializar Coqui TTS"""
        try:
            from TTS.api import TTS
            
            self.logger.info(f"Inicializando Coqui TTS con modelo: {self.tts_model}")
            
            # Inicializar TTS con el modelo especificado
            self.tts_engine = TTS(self.tts_model)
            
            # Verificar si el modelo soporta múltiples hablantes
            if hasattr(self.tts_engine, 'speakers') and self.tts_engine.speakers:
                available_speakers = self.tts_engine.speakers
                self.logger.info(f"Hablantes disponibles: {available_speakers}")
                
                # Verificar si el hablante configurado existe
                if self.tts_speaker not in available_speakers:
                    # Usar el primer hablante disponible
                    self.tts_speaker = available_speakers[0]
                    self.logger.warning(f"Hablante configurado no encontrado, usando: {self.tts_speaker}")
            
            self.logger.info("Coqui TTS inicializado exitosamente")
            
        except ImportError:
            # Coqui TTS no está instalado - usar pyttsx3 silenciosamente
            self.logger.info("Coqui TTS no disponible, usando pyttsx3 como alternativa")
            self.tts_engine = None
        except Exception as e:
            self.logger.warning(f"Coqui TTS no disponible: {e}")
            self.tts_engine = None
    
    def speak_text(self, text: str):
        """Convertir texto a voz y reproducirlo"""
        try:
            if self.provider == 'coqui':
                audio_file = self.generate_coqui_audio(text)
            elif self.provider == 'elevenlabs':
                audio_data = self.generate_elevenlabs_audio(text)
                audio_file = self.save_audio_data(audio_data) if audio_data else None
            else:
                # Fallback a pyttsx3
                audio_file = self.generate_fallback_audio(text)
            
            if audio_file and os.path.exists(audio_file):
                self.play_audio_file(audio_file)
            else:
                self.audioError.emit("No se pudo generar audio")
                
        except Exception as e:
            self.logger.error(f"Error en síntesis de voz: {e}")
            self.audioError.emit(f"Error de audio: {e}")
    
    def generate_coqui_audio(self, text: str) -> Optional[str]:
        """Generar audio usando Coqui TTS"""
        try:
            if not self.tts_engine:
                raise ValueError("Coqui TTS no está inicializado")
            
            # Crear archivo temporal
            temp_file = os.path.join(self.temp_dir, "coqui_output.wav")
            
            self.logger.info(f"Generando audio con Coqui TTS: '{text[:50]}...'")
            
            # Generar audio con Coqui TTS
            if hasattr(self.tts_engine, 'speakers') and self.tts_engine.speakers:
                # Modelo con múltiples hablantes
                self.tts_engine.tts_to_file(
                    text=text,
                    file_path=temp_file,
                    speaker=self.tts_speaker,
                    language=self.tts_language,
                    speed=self.tts_rate
                )
            else:
                # Modelo con hablante único
                self.tts_engine.tts_to_file(
                    text=text,
                    file_path=temp_file,
                    language=self.tts_language,
                    speed=self.tts_rate
                )
            
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                self.logger.info("Audio generado exitosamente con Coqui TTS")
                return temp_file
            else:
                self.logger.error("Archivo de audio vacío o no generado")
                return None
                
        except Exception as e:
            self.logger.error(f"Error con Coqui TTS: {e}")
            return None
    
    def generate_elevenlabs_audio(self, text: str) -> Optional[bytes]:
        """Generar audio usando ElevenLabs (método legacy)"""
        try:
            elevenlabs_api_key = self.config.get('ELEVENLABS_API_KEY')
            voice_id = self.config.get('TTS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
            
            if not elevenlabs_api_key:
                raise ValueError("API key de ElevenLabs no configurada")
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.content
            else:
                self.logger.error(f"ElevenLabs error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error con ElevenLabs: {e}")
            return None
    
    def generate_fallback_audio(self, text: str) -> Optional[str]:
        """Generar audio usando método fallback (pyttsx3)"""
        try:
            import pyttsx3
            
            # Crear archivo temporal
            temp_file = os.path.join(self.temp_dir, "fallback_audio.wav")
            
            # Configurar pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', int(self.tts_rate * 180))  # Convertir rate
            engine.setProperty('volume', float(self.config.get('TTS_VOLUME', 0.8)))
            
            # Configurar voz en español si está disponible
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            # Generar archivo
            engine.save_to_file(text, temp_file)
            engine.runAndWait()
            engine.stop()
            
            # Verificar que el archivo se generó
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                return temp_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error con fallback TTS: {e}")
            return None
    
    def save_audio_data(self, audio_data: bytes) -> Optional[str]:
        """Guardar datos de audio en archivo temporal"""
        try:
            temp_file = os.path.join(self.temp_dir, "audio_data.mp3")
            
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            
            return temp_file if os.path.exists(temp_file) else None
            
        except Exception as e:
            self.logger.error(f"Error guardando audio: {e}")
            return None
    
    def play_audio_file(self, audio_file: str):
        """Reproducir archivo de audio"""
        try:
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_file}")
            
            # Reproducir usando QMediaPlayer
            url = QUrl.fromLocalFile(audio_file)
            content = QMediaContent(url)
            
            self.media_player.setMedia(content)
            self.media_player.setVolume(int(float(self.config.get('TTS_VOLUME', 0.8)) * 100))
            self.media_player.play()
            
            self.logger.info(f"Reproduciendo audio: {audio_file}")
            
        except Exception as e:
            self.logger.error(f"Error reproduciendo audio: {e}")
            self.audioError.emit(f"Error de reproducción: {e}")
    
    def play_audio_data(self, audio_data: bytes):
        """Reproducir datos de audio (método legacy)"""
        temp_file = self.save_audio_data(audio_data)
        if temp_file:
            self.play_audio_file(temp_file)
    
    def on_player_state_changed(self, state):
        """Manejar cambios de estado del reproductor"""
        if state == QMediaPlayer.StoppedState:
            self.audioFinished.emit()
            self.cleanup_temp_files()
        elif state == QMediaPlayer.InvalidMedia:
            self.audioError.emit("Media inválida")
    
    def stop_audio(self):
        """Detener reproducción de audio"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()
    
    def cleanup_temp_files(self):
        """Limpiar archivos temporales usados"""
        try:
            for filename in os.listdir(self.temp_dir):
                if filename.startswith(('coqui_output', 'fallback_audio', 'audio_data')):
                    file_path = os.path.join(self.temp_dir, filename)
                    try:
                        os.remove(file_path)
                    except:
                        pass  # Ignorar errores de limpieza
        except Exception as e:
            self.logger.warning(f"Error limpiando archivos temporales: {e}")
    
    def cleanup(self):
        """Limpiar recursos"""
        self.stop_audio()
        
        # Limpiar archivos temporales
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def get_available_coqui_models(self) -> list:
        """Obtener lista de modelos Coqui TTS disponibles"""
        try:
            from TTS.api import TTS
            return TTS.list_models()
        except Exception as e:
            self.logger.error(f"Error obteniendo modelos Coqui: {e}")
            return []
    
    def get_available_speakers(self) -> list:
        """Obtener lista de hablantes disponibles para el modelo actual"""
        try:
            if self.tts_engine and hasattr(self.tts_engine, 'speakers'):
                return self.tts_engine.speakers or []
            return []
        except Exception as e:
            self.logger.error(f"Error obteniendo hablantes: {e}")
            return []

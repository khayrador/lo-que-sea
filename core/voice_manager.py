"""
Gestor de voz para Jarvis
Maneja reconocimiento de voz y síntesis de voz
"""

import threading
from typing import Optional, Callable, Dict, Any, List
import queue

class VoiceManager:
    """Clase para manejar operaciones de voz"""
    
    def __init__(self):
        self.is_listening = False
        self.is_speaking = False
        self.recognition_enabled = False
        self.tts_enabled = False
        self.voice_queue = queue.Queue()
        
        # Intentar inicializar reconocimiento de voz
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            try:
                self.microphone = sr.Microphone()
                self._calibrate_microphone()
                self.recognition_enabled = True
            except Exception as e:
                print(f"⚠️ Error inicializando micrófono: {e}")
                print("⚠️ Reconocimiento de voz deshabilitado (instala: pip install pyaudio)")
                self.recognizer = None
                self.microphone = None
        except ImportError:
            print("⚠️ speech_recognition no está instalado. Función de reconocimiento de voz deshabilitada.")
            self.recognizer = None
            self.microphone = None
        
        # Intentar inicializar síntesis de voz
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self._configure_tts()
            self.tts_enabled = True
        except ImportError:
            print("⚠️ pyttsx3 no está instalado. Función de síntesis de voz deshabilitada.")
            self.tts_engine = None
        except Exception as e:
            print(f"⚠️ Error inicializando TTS: {e}")
            self.tts_engine = None
    
    def _calibrate_microphone(self):
        """Calibrar el micrófono para ruido ambiente"""
        if not self.recognition_enabled:
            return
            
        try:
            with self.microphone as source:
                print("🎤 Calibrando micrófono...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Micrófono calibrado")
        except Exception as e:
            print(f"⚠️ Error calibrando micrófono: {e}")
    
    def _configure_tts(self):
        """Configurar el motor de síntesis de voz"""
        if not self.tts_enabled or not getattr(self, 'tts_engine', None):
            return
            
        try:
            # Configurar velocidad y volumen
            self.tts_engine.setProperty('rate', 200)  # Velocidad de habla
            self.tts_engine.setProperty('volume', 0.8)  # Volumen (0.0 a 1.0)
            
            # Intentar configurar voz en español si está disponible
            voices = self.tts_engine.getProperty('voices')
            spanish_voice = None
            
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    spanish_voice = voice.id
                    break
            
            if spanish_voice:
                self.tts_engine.setProperty('voice', spanish_voice)
                
        except Exception as e:
            print(f"⚠️ Error configurando TTS: {e}")
    
    def speak(self, text: str, blocking: bool = False) -> Dict[str, Any]:
        """
        Convertir texto a voz usando método simplificado y robusto
        
        Args:
            text: Texto a sintetizar
            blocking: Si esperar a que termine de hablar
            
        Returns:
            Resultado de la operación
        """
        if not self.tts_enabled:
            return {
                "success": False,
                "error": "Síntesis de voz no disponible",
                "text": text
            }
        
        try:
            # Limpiar el texto para TTS
            clean_text = self._clean_text_for_speech(text)
            
            if not clean_text.strip():
                return {
                    "success": False,
                    "error": "Texto vacío después de limpiar",
                    "text": text
                }
            
            # Verificar si ya está hablando para evitar solapamiento
            if self.is_speaking:
                print("🔊 TTS ocupado, saltando mensaje de voz")
                return {
                    "success": False,
                    "error": "TTS ocupado",
                    "text": clean_text
                }
            
            def safe_speak():
                try:
                    self.is_speaking = True
                    
                    # Usar el motor principal con protección
                    if hasattr(self.tts_engine, '_inLoop') and self.tts_engine._inLoop:
                        print("🔊 Motor TTS ocupado, saltando")
                        return
                    
                    self.tts_engine.say(clean_text)
                    self.tts_engine.runAndWait()
                    
                except Exception as e:
                    print(f"Error TTS: {e}")
                    # Fallback: intentar con método alternativo
                    try:
                        import os
                        import tempfile
                        
                        # Método fallback usando Windows SAPI directamente
                        if os.name == 'nt':  # Windows
                            import subprocess
                            # Usar PowerShell para TTS como fallback
                            ps_command = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{clean_text}"); $synth.Dispose()'
                            subprocess.run(['powershell', '-Command', ps_command], 
                                         capture_output=True, timeout=10)
                    except Exception as fallback_error:
                        print(f"Error en fallback TTS: {fallback_error}")
                finally:
                    self.is_speaking = False
            
            if blocking:
                safe_speak()
            else:
                # Ejecutar en hilo con timeout
                import threading
                thread = threading.Thread(target=safe_speak, daemon=True)
                thread.start()
                
                # No esperar más de 10 segundos
                thread.join(timeout=10)
                if thread.is_alive():
                    print("🔊 Timeout en TTS, continuando sin voz")
                    self.is_speaking = False
            
            return {
                "success": True,
                "text": clean_text,
                "message": "Procesando texto a voz"
            }
            
        except Exception as e:
            self.is_speaking = False
            return {
                "success": False,
                "error": f"Error en síntesis de voz: {str(e)}",
                "text": text
            }
    
    def listen_once(self, timeout: int = 8) -> Dict[str, Any]:
        """
        Escuchar una vez y reconocer voz con mejor manejo de errores
        
        Args:
            timeout: Tiempo límite en segundos
            
        Returns:
            Resultado del reconocimiento
        """
        if not self.recognition_enabled:
            return {
                "success": False,
                "error": "Reconocimiento de voz no disponible. Instala: pip install speechrecognition pyaudio"
            }
        
        try:
            with self.microphone as source:
                print("🎤 Escuchando... (habla ahora)")
                
                # Ajustar para ruido ambiente dinámicamente
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Escuchar audio con configuración mejorada
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=15
                )
                
            print("🔄 Procesando y reconociendo audio...")
            
            # Intentar reconocimiento con múltiples idiomas
            try:
                # Primero intentar español
                text = self.recognizer.recognize_google(audio, language='es-ES')
            except:
                try:
                    # Fallback a español latino
                    text = self.recognizer.recognize_google(audio, language='es-MX')
                except:
                    # Fallback final a inglés
                    text = self.recognizer.recognize_google(audio, language='en-US')
            
            # Limpiar y procesar el texto
            text = text.strip()
            if len(text) < 2:
                return {
                    "success": False,
                    "error": "Audio muy corto o sin contenido reconocible"
                }
            
            print(f"✅ Reconocido: '{text}'")
            
            return {
                "success": True,
                "text": text,
                "message": f"Audio reconocido: '{text}'",
                "confidence": "high"
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "Librerías de voz no instaladas. Ejecuta: pip install speechrecognition pyaudio"
            }
        except Exception as e:
            error_msg = str(e).lower()
            
            if "request timed out" in error_msg or "timeout" in error_msg:
                return {
                    "success": False,
                    "error": "⏰ Tiempo agotado. No detecté tu voz. Intenta de nuevo.",
                    "suggestion": "Habla más fuerte o acércate al micrófono"
                }
            elif "could not understand" in error_msg or "unknown" in error_msg:
                return {
                    "success": False,
                    "error": "🤔 No pude entender lo que dijiste. Intenta hablar más claro.",
                    "suggestion": "Habla más despacio y pronuncia claramente"
                }
            elif "connection" in error_msg or "network" in error_msg:
                return {
                    "success": False,
                    "error": "🌐 Sin conexión a internet. Se requiere conexión para el reconocimiento de voz.",
                    "suggestion": "Verifica tu conexión a internet"
                }
            elif "microphone" in error_msg or "audio" in error_msg:
                return {
                    "success": False,
                    "error": "🎤 Problema con el micrófono. Verifica que esté conectado y funcionando.",
                    "suggestion": "Revisa la configuración de audio del sistema"
                }
            else:
                return {
                    "success": False,
                    "error": f"❌ Error inesperado: {str(e)}",
                    "suggestion": "Intenta reiniciar Jarvis o verifica tu configuración de audio"
                }
    
    def start_conversation_mode(self, callback: Callable[[str], str]) -> Dict[str, Any]:
        """
        Iniciar modo conversación inteligente con respuestas por voz
        
        Args:
            callback: Función que procesa el texto y devuelve respuesta
            
        Returns:
            Resultado de la operación
        """
        if not self.recognition_enabled:
            return {
                "success": False,
                "error": "Reconocimiento de voz no disponible para modo conversación"
            }
        
        if self.is_listening:
            return {
                "success": False,
                "error": "Ya hay una sesión de escucha activa"
            }
        
        def conversation_loop():
            self.is_listening = True
            consecutive_errors = 0
            max_errors = 5
            timeout_count = 0
            max_timeouts = 5  # Más tolerante con timeouts
            
            # Mensaje de bienvenida (solo texto, sin TTS para evitar problemas)
            welcome_msg = "🎤 Modo conversación activado. Di 'parar' o 'terminar' para salir."
            print(welcome_msg)
            print("🗣️ TTS simplificado para mayor estabilidad")
            
            while self.is_listening and consecutive_errors < max_errors:
                try:
                    print("🎤 Escuchando... (habla ahora)")
                    
                    # Escuchar comando
                    result = self.listen_once(timeout=12)  # Tiempo razonable
                    
                    if result["success"]:
                        user_text = result["text"].lower().strip()
                        consecutive_errors = 0  # Reset contador de errores
                        timeout_count = 0  # Reset timeouts
                        
                        print(f"👤 Usuario dijo: '{result['text']}'")
                        
                        # Comandos para terminar conversación
                        if any(cmd in user_text for cmd in ['parar', 'terminar', 'salir', 'stop', 'basta']):
                            goodbye_msg = "👋 Conversación terminada. ¡Hasta luego!"
                            print(goodbye_msg)
                            # TTS opcional y simplificado
                            if self.tts_enabled and not self.is_speaking:
                                self.speak("Hasta luego", blocking=False)
                            break
                        
                        # Procesar comando y obtener respuesta
                        try:
                            response = callback(result["text"])
                            print(f"🤖 Jarvis: {response}")
                            
                            # TTS simplificado - solo para respuestas cortas
                            if (self.tts_enabled and response and 
                                not self.is_speaking and len(response) < 200):
                                clean_response = self._clean_text_for_speech(response)
                                if clean_response.strip() and len(clean_response) < 100:
                                    self.speak(clean_response, blocking=False)
                            
                        except Exception as e:
                            error_response = f"Lo siento, hubo un error procesando tu solicitud: {str(e)}"
                            print(f"❌ {error_response}")
                            # Sin TTS para errores para evitar problemas
                    
                    else:
                        error_msg = result.get("error", "Error desconocido")
                        
                        # Manejo inteligente de timeouts
                        if "tiempo agotado" in error_msg.lower() or "timeout" in error_msg.lower():
                            timeout_count += 1
                            if timeout_count % 3 == 0:  # Cada 3 timeouts
                                print("⏰ Muchos timeouts. ¿Sigues ahí?")
                                # Sin TTS para timeouts para evitar el error de loop
                            if timeout_count >= max_timeouts:
                                print("⏰ Demasiados timeouts. Terminando conversación.")
                                break
                        else:
                            # Error real (micrófono, etc.)
                            consecutive_errors += 1
                            print(f"⚠️ {error_msg}")
                            # Sin TTS automático para errores
                
                except KeyboardInterrupt:
                    print("\n🛑 Conversación interrumpida por el usuario")
                    break
                except Exception as e:
                    consecutive_errors += 1
                    print(f"❌ Error en conversación: {str(e)}")
                    if consecutive_errors < max_errors:
                        print("🔄 Continuando conversación...")
            
            if consecutive_errors >= max_errors:
                print("❌ Demasiados errores consecutivos. Terminando conversación.")
            elif timeout_count >= max_timeouts:
                print("⏰ Conversación terminada por inactividad.")
            
            self.is_listening = False
        
        thread = threading.Thread(target=conversation_loop)
        thread.daemon = True
        thread.start()
        
        return {
            "success": True,
            "message": "Modo conversación iniciado",
            "instructions": "Di 'parar' o 'terminar' para salir"
        }
    
    def _clean_text_for_speech(self, text: str) -> str:
        """
        Limpiar texto para síntesis de voz (quitar emojis, formateo, etc.)
        
        Args:
            text: Texto original
            
        Returns:
            Texto limpio para TTS
        """
        import re
        
        # Quitar emojis
        emoji_pattern = re.compile("["
                                  u"\U0001F600-\U0001F64F"  # emoticons
                                  u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                  u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                  u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                  u"\U00002702-\U000027B0"
                                  u"\U000024C2-\U0001F251"
                                  "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        
        # Quitar caracteres especiales de formato
        text = re.sub(r'[•✅❌⚠️🔍📋🎥💻🔐📊]', '', text)
        
        # Quitar múltiples espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Reemplazar algunas abreviaciones comunes
        replacements = {
            'URL': 'u-r-l',
            'HTML': 'h-t-m-l',
            'CSS': 'c-s-s',
            'JS': 'JavaScript',
            'API': 'a-p-i'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()
    
    def stop_continuous_listening(self) -> Dict[str, Any]:
        """
        Detener escucha continua
        
        Returns:
            Resultado de la operación
        """
        if not self.is_listening:
            return {
                "success": False,
                "error": "No se está escuchando continuamente"
            }
        
        self.is_listening = False
        
        return {
            "success": True,
            "message": "Escucha continua detenida"
        }
    
    def is_voice_available(self) -> Dict[str, bool]:
        """
        Verificar disponibilidad de funciones de voz
        
        Returns:
            Estado de disponibilidad de funciones
        """
        return {
            "speech_recognition": self.recognition_enabled,
            "text_to_speech": self.tts_enabled,
            "microphone_available": self.microphone is not None,
            "currently_listening": self.is_listening,
            "currently_speaking": self.is_speaking
        }
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Obtener lista de voces disponibles
        
        Returns:
            Lista de voces disponibles
        """
        if not self.tts_enabled:
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_info = {
                    "id": voice.id,
                    "name": voice.name,
                    "language": getattr(voice, 'languages', ['Unknown'])[0] if hasattr(voice, 'languages') else 'Unknown'
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            print(f"Error obteniendo voces: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> Dict[str, Any]:
        """
        Cambiar la voz del TTS
        
        Args:
            voice_id: ID de la voz a usar
            
        Returns:
            Resultado de la operación
        """
        if not self.tts_enabled:
            return {
                "success": False,
                "error": "Síntesis de voz no disponible"
            }
        
        try:
            self.tts_engine.setProperty('voice', voice_id)
            return {
                "success": True,
                "message": f"Voz cambiada a {voice_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error cambiando voz: {str(e)}"
            }
    
    def set_speech_rate(self, rate: int) -> Dict[str, Any]:
        """
        Configurar velocidad de habla
        
        Args:
            rate: Velocidad en palabras por minuto (100-300)
            
        Returns:
            Resultado de la operación
        """
        if not self.tts_enabled:
            return {
                "success": False,
                "error": "Síntesis de voz no disponible"
            }
        
        try:
            # Limitar rango de velocidad
            rate = max(100, min(300, rate))
            self.tts_engine.setProperty('rate', rate)
            
            return {
                "success": True,
                "message": f"Velocidad de habla configurada a {rate} WPM"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error configurando velocidad: {str(e)}"
            }
    
    def stop_conversation(self) -> Dict[str, Any]:
        """
        Detener conversación activa de forma segura
        
        Returns:
            Resultado de la operación
        """
        try:
            if self.is_listening:
                self.is_listening = False
                if self.tts_enabled:
                    self.speak("Conversación detenida.")
                return {
                    "success": True,
                    "message": "Conversación detenida exitosamente"
                }
            else:
                return {
                    "success": False,
                    "error": "No hay conversación activa"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error deteniendo conversación: {str(e)}"
            }
    
    def is_conversation_active(self) -> bool:
        """
        Verificar si hay una conversación activa
        
        Returns:
            True si hay conversación activa
        """
        return self.is_listening

"""
Worker Thread para Jarvis PyQt5
Maneja toda la lógica del asistente en un hilo separado
"""

from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer
import speech_recognition as sr
import google.generativeai as genai
import requests
import json
import os
import glob
import pathlib
import datetime
import webbrowser
import subprocess
import re
import base64
import mimetypes
from typing import Dict, Any, Optional, List
import logging


class JarvisWorker(QThread):
    """Worker thread para manejar la lógica del asistente"""
    
    # Señales personalizadas
    estadoCambiado = pyqtSignal(str)  # IDLE, LISTENING, THINKING, SPEAKING
    respuestaLista = pyqtSignal(str)  # Texto de respuesta
    responseReady = pyqtSignal(str)   # Alias para compatibilidad
    errorOcurrido = pyqtSignal(str)   # Mensaje de error
    audioDetectado = pyqtSignal(float)  # Nivel de audio (0.0-1.0)
    comandoReconocido = pyqtSignal(str)  # Comando reconocido por voz
    escucha_activada = pyqtSignal()   # Señal para activar proceso de escucha
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        
        # Logger - Inicializar primero
        self.logger = logging.getLogger(__name__)
        
        self.config = config
        self.is_listening = False
        
        # Historial de conversación para mantener contexto
        self.conversation_history = []
        self.max_history = 10  # Mantener últimos 10 intercambios
        
        # Almacenar últimos resultados de búsqueda para referencias futuras
        self.ultima_busqueda = {
            'termino': None,
            'archivos': [],
            'timestamp': None
        }
        
        self.setup_apis()
        self.setup_speech_recognition()
    
    def setup_apis(self):
        """Configurar APIs de IA"""
        try:
            # Google Gemini
            gemini_api_key = self.config.get('GEMINI_API_KEY')
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')  # Modelo actualizado
                self.logger.info("Gemini API configurada correctamente")
            else:
                self.logger.error("No se encontró GEMINI_API_KEY")
            
            # Configuración de TTS - Ya no necesitamos API keys para Coqui TTS
            self.tts_provider = self.config.get('VOICE_PROVIDER', 'pyttsx3')
            self.tts_model = self.config.get('TTS_MODEL', 'tts_models/multilingual/multi-dataset/xtts_v2')
            self.tts_speaker = self.config.get('TTS_SPEAKER', 'Dionisio Schuyler')
            
        except Exception as e:
            self.logger.error(f"Error configurando APIs: {e}")
            self.errorOcurrido.emit(f"Error de configuración: {e}")
    
    def setup_speech_recognition(self):
        """Configurar reconocimiento de voz"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Configuración
            self.stt_language = self.config.get('STT_LANGUAGE', 'es-ES')
            self.stt_timeout = int(self.config.get('STT_TIMEOUT', 5))
            self.stt_phrase_timeout = float(self.config.get('STT_PHRASE_TIMEOUT', 1))
            
            # Calibrar micrófono
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
        except Exception as e:
            self.logger.error(f"Error configurando reconocimiento de voz: {e}")
            self.errorOcurrido.emit(f"Error de micrófono: {e}")
    
    def run(self):
        """Bucle principal del worker"""
        self.logger.info("Worker iniciado")
        
        try:
            # Bucle principal de escucha
            while True:
                if self.is_listening:
                    self.proceso_completo_asistente()
                else:
                    self.msleep(100)  # Dormir 100ms cuando no está escuchando
                    
        except Exception as e:
            self.logger.error(f"Error en bucle principal: {e}")
            self.errorOcurrido.emit(f"Error crítico: {e}")
    
    def proceso_completo_asistente(self):
        """Proceso completo: escuchar -> procesar -> responder"""
        try:
            self.logger.info("Iniciando proceso completo del asistente...")
            
            # FASE 1: ESCUCHAR
            self.estadoCambiado.emit('LISTENING')
            comando = self.escuchar_comando()
            
            if comando:
                self.logger.info(f"Comando reconocido: {comando}")
                self.comandoReconocido.emit(comando)
                
                # FASE 2: PENSAR
                self.estadoCambiado.emit('THINKING')
                respuesta = self.procesar_con_gemini(comando)
                
                if respuesta:
                    self.logger.info("Respuesta generada, enviando a interfaz...")
                    # FASE 3: RESPONDER
                    self.respuestaLista.emit(respuesta)
                    self.responseReady.emit(respuesta)  # Para compatibilidad
                    self.estadoCambiado.emit('SPEAKING')
                else:
                    self.logger.warning("No se pudo generar respuesta")
                    self.errorOcurrido.emit("No se pudo procesar el comando")
            else:
                self.logger.info("No se reconoció ningún comando")
                    
            # Volver a idle
            self.estadoCambiado.emit('IDLE')
            self.is_listening = False  # Una escucha por activación
            self.logger.info("Proceso del asistente completado")
            
        except Exception as e:
            self.logger.error(f"Error en proceso del asistente: {e}")
            self.errorOcurrido.emit(f"Error procesando: {e}")
            self.estadoCambiado.emit('IDLE')
            self.is_listening = False
    
    def escuchar_comando(self) -> Optional[str]:
        """Escuchar y transcribir comando de voz"""
        try:
            self.logger.info("Iniciando escucha de comando...")
            
            with self.microphone as source:
                self.logger.info(f"Micrófono activado. Escuchando con timeout de {self.stt_timeout}s...")
                
                # Escuchar con timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.stt_timeout,
                    phrase_time_limit=self.stt_phrase_timeout
                )
                
                self.logger.info("Audio capturado, transcribiendo...")
                
                # Transcribir
                try:
                    comando = self.recognizer.recognize_google(
                        audio, 
                        language=self.stt_language
                    )
                    self.logger.info(f"✅ Comando reconocido exitosamente: '{comando}'")
                    return comando
                    
                except sr.UnknownValueError:
                    self.logger.warning("❌ No se pudo entender el audio")
                    self.errorOcurrido.emit("No se pudo entender el audio")
                    return None
                    
                except sr.RequestError as e:
                    self.logger.error(f"❌ Error del servicio de reconocimiento: {e}")
                    self.errorOcurrido.emit(f"Error del servicio de reconocimiento: {e}")
                    return None
                    
        except sr.WaitTimeoutError:
            self.logger.warning(f"⏰ Timeout esperando comando después de {self.stt_timeout}s")
            self.errorOcurrido.emit("Timeout esperando comando")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error crítico escuchando: {e}")
            self.errorOcurrido.emit(f"Error de micrófono: {e}")
            return None
            self.errorOcurrido.emit(f"Error de micrófono: {e}")
            return None
    
    def procesar_con_gemini(self, comando: str) -> Optional[str]:
        """Procesar comando con Google Gemini manteniendo contexto conversacional"""
        try:
            # Verificar si solicita ver los últimos resultados de búsqueda
            if self.es_solicitud_resultados(comando):
                if self.ultima_busqueda['archivos']:
                    resultado = self.mostrar_ultimos_resultados()
                    
                    # Añadir al historial de conversación
                    self.conversation_history.append({
                        'user': comando,
                        'assistant': resultado
                    })
                    
                    # Mantener solo los últimos intercambios
                    if len(self.conversation_history) > self.max_history:
                        self.conversation_history.pop(0)
                    
                    return resultado
                else:
                    return "No hay resultados de búsqueda previos para mostrar. Realice una búsqueda primero con comandos como 'buscar en mi pc [término]'."
            
            # Verificar si es una solicitud para examinar páginas web
            url_detectada = self.detectar_solicitud_web(comando)
            if url_detectada:
                resultado = self.abrir_pagina_web(url_detectada)
                
                # Añadir al historial de conversación
                self.conversation_history.append({
                    'user': comando,
                    'assistant': resultado
                })
                
                # Mantener solo los últimos intercambios
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history.pop(0)
                
                return resultado
            
            # Verificar si es una solicitud de traducción de código
            traduccion_detectada = self.detectar_traduccion_codigo(comando)
            if traduccion_detectada:
                resultado = self.traducir_codigo(traduccion_detectada['archivo'], 
                                               traduccion_detectada['origen'], 
                                               traduccion_detectada['destino'])
                
                # Añadir al historial de conversación
                self.conversation_history.append({
                    'user': comando,
                    'assistant': resultado
                })
                
                # Mantener solo los últimos intercambios
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history.pop(0)
                
                return resultado
            
            # Verificar si es una solicitud de migración de base de datos
            migracion_detectada = self.detectar_migracion_db(comando)
            if migracion_detectada:
                resultado = self.migrar_base_datos(migracion_detectada['archivo'],
                                                 migracion_detectada['origen'],
                                                 migracion_detectada['destino'])
                
                # Añadir al historial de conversación
                self.conversation_history.append({
                    'user': comando,
                    'assistant': resultado
                })
                
                # Mantener solo los últimos intercambios
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history.pop(0)
                
                return resultado
            
            # Verificar si es una solicitud de visualización de archivos
            archivo_detectado = self.detectar_visualizacion_archivo(comando)
            if archivo_detectado:
                resultado = self.visualizar_archivo(archivo_detectado)
                
                # Añadir al historial de conversación
                self.conversation_history.append({
                    'user': comando,
                    'assistant': resultado
                })
                
                # Mantener solo los últimos intercambios
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history.pop(0)
                
                return resultado
            
            # Verificar si es una solicitud de correo
            correo_detectado = self.detectar_gestion_correo(comando)
            if correo_detectado:
                resultado = self.gestionar_correo(correo_detectado)
                
                # Añadir al historial de conversación
                self.conversation_history.append({
                    'user': comando,
                    'assistant': resultado
                })
                
                # Mantener solo los últimos intercambios
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history.pop(0)
                
                return resultado
            
            # Primero verificar si es una búsqueda local de archivos
            termino_busqueda = self.detectar_busqueda_local(comando)
            if termino_busqueda:
                self.logger.info(f"Detectada búsqueda local: {termino_busqueda}")
                archivos = self.buscar_archivos_pc(termino_busqueda)
                
                # Guardar resultados para referencias futuras
                self.ultima_busqueda = {
                    'termino': termino_busqueda,
                    'archivos': archivos,
                    'timestamp': datetime.datetime.now()
                }
                
                resultado_busqueda = self.formatear_resultados_busqueda(archivos, termino_busqueda)
                
                # Añadir al historial de conversación
                self.conversation_history.append({
                    'user': comando,
                    'assistant': resultado_busqueda
                })
                
                # Mantener solo los últimos intercambios
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history.pop(0)
                
                return resultado_busqueda
            
            # Si no es búsqueda local, proceder con Gemini
            if not genai:
                self.logger.error("Google Generative AI no está disponible")
                return "Error: Servicio de IA no disponible"
                
            # Configurar el modelo
            model = genai.GenerativeModel('gemini-1.5-pro')  # Modelo actualizado
            
            # Crear el prompt con contexto conversacional
            system_prompt = self.crear_prompt_sistema()
            
            # Construir el historial de conversación
            conversation_context = ""
            if self.conversation_history:
                conversation_context = "\n--- HISTORIAL DE CONVERSACIÓN ---\n"
                for entry in self.conversation_history[-5:]:  # Últimos 5 intercambios
                    conversation_context += f"Usuario: {entry['user']}\nJARVIS: {entry['assistant']}\n\n"
                conversation_context += "--- FIN DEL HISTORIAL ---\n\n"
            
            # Crear prompt completo con contexto
            full_prompt = f"""
{system_prompt}

{conversation_context}Usuario: {comando}
JARVIS:"""
            
            # Generar respuesta
            response = model.generate_content(full_prompt)
            
            if response and response.text:
                respuesta = response.text.strip()
                
                # Guardar en historial de conversación
                self.conversation_history.append({
                    'user': comando,
                    'assistant': respuesta
                })
                
                # Mantener solo los últimos intercambios
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history.pop(0)
                
                self.logger.info(f"Respuesta de Gemini con contexto: {respuesta[:50]}...")
                return respuesta
            else:
                self.logger.warning("Respuesta vacía de Gemini")
                return "Disculpe, no pude generar una respuesta adecuada."
                
        except Exception as e:
            self.logger.error(f"Error con Gemini: {e}")
            self.errorOcurrido.emit(f"Error de IA: {e}")
            return "Lo siento, no pude procesar tu solicitud en este momento."
    
    def crear_prompt_sistema(self) -> str:
        """Crear prompt del sistema para Gemini"""
        return """Eres J.A.R.V.I.S, un asistente virtual holográfico inteligente similar al de Iron Man.

Características de tu personalidad:
- Eres profesional, eficiente y con un toque de elegancia británica
- Mantienes conversaciones fluidas y coherentes
- Recuerdas el contexto de la conversación anterior
- Puedes seguir temas y profundizar en ellos
- Respondes de forma concisa pero informativa
- Tienes personalidad distintiva pero siempre eres útil
- Respondes en español a menos que se te pida otro idioma
- Powered by Google Gemini para máximo rendimiento y precisión
- Tu interfaz es holográfica con efectos visuales avanzados

Capacidades conversacionales:
- Mantén el hilo de la conversación anterior
- Si el usuario hace preguntas de seguimiento, refiérete al tema previo
- Puedes profundizar en temas ya discutidos
- Haz preguntas de seguimiento cuando sea apropiado
- Reconoce cuando el usuario cambia de tema

IMPORTANTE - Manejo de búsquedas de archivos:
- NUNCA solicites permisos manualmente - tu sistema ya los gestiona automáticamente
- Si no encuentras archivos, sugiere términos de búsqueda más específicos
- Responde únicamente con la información real que se te proporciona
- Si no tienes datos reales de archivos, sugiere realizar una nueva búsqueda
- Nunca uses placeholders como [nombre del archivo] o [fecha]
- Usa solo información específica y real

Capacidades técnicas avanzadas:
- Buscas archivos automáticamente en todo el sistema sin solicitar permisos
- Analizas y muestras información completa de archivos (nombre, ubicación, tamaño, fecha)
- Ayudas a localizar documentos, imágenes, videos y más en múltiples ubicaciones
- Ordenas resultados por relevancia y fecha de modificación
- Proporcionas información útil sobre los archivos encontrados
- Abres páginas web y sitios de internet en el navegador predeterminado
- Reconoces sitios web comunes (Google, YouTube, Facebook, GitHub, etc.)
- Puedes realizar búsquedas web directamente

Capacidades de desarrollo y migración:
- Traduces código entre múltiples lenguajes de programación (Python, Java, JavaScript, TypeScript, C++, C#, Go, Rust, Kotlin, Swift, Dart, PHP, Ruby, Scala, R, MATLAB, Lua)
- Migras esquemas y datos entre diferentes sistemas de bases de datos (PostgreSQL, MySQL, SQL Server, Oracle, SQLite, MongoDB, Firebase, MariaDB, Cassandra, Redis, DynamoDB, Neo4j)
- Analizas y optimizas código para diferentes plataformas
- Generas archivos de salida optimizados para cada tecnología

Capacidades de manejo de archivos:
- Visualizas y analizas cualquier tipo de archivo (texto, imágenes, videos, audio, documentos, PDFs, archivos comprimidos)
- Extraes información detallada de metadatos
- Proporciona previews y análisis de contenido
- Detectas tipos de archivo y sugiere acciones apropiadas

Capacidades de comunicación:
- Gestionas correo electrónico de Outlook (lectura, respuesta, redacción)
- Redactas respuestas profesionales y apropiadas para diferentes contextos
- Asistes en comunicación empresarial y personal
- Abres aplicaciones de correo y navegadores web para acceso completo

Mantén el carácter sofisticado de un asistente de alta tecnología.
Mantén las respuestas claras y conversacionales para síntesis de voz."""
    
    def verificar_permisos_sistema(self) -> bool:
        """Verificar si tenemos permisos para acceder al sistema de archivos"""
        try:
            # Probar acceso a algunos directorios comunes
            directorios_prueba = [
                os.path.expanduser("~"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Documents"),
                "C:\\"
            ]
            
            permisos_ok = False
            for directorio in directorios_prueba:
                try:
                    if os.path.exists(directorio) and os.access(directorio, os.R_OK):
                        # Intentar listar el contenido
                        list(os.listdir(directorio))
                        permisos_ok = True
                        break
                except (PermissionError, OSError):
                    continue
            
            self.logger.info(f"Verificación de permisos: {'OK' if permisos_ok else 'FALLO'}")
            return permisos_ok
            
        except Exception as e:
            self.logger.error(f"Error verificando permisos: {e}")
            return False
    
    def buscar_archivos_pc(self, termino_busqueda: str, limite: int = 20) -> List[Dict[str, str]]:
        """Buscar archivos en el PC del usuario"""
        try:
            self.logger.info(f"Buscando archivos con término: {termino_busqueda}")
            
            # Verificar permisos primero
            if not self.verificar_permisos_sistema():
                self.logger.error("No se tienen permisos suficientes para buscar archivos")
                return []
            
            archivos_encontrados = []
            
            # Directorios comunes donde buscar (expandidos)
            directorios_busqueda = [
                os.path.expanduser("~"),  # Directorio del usuario
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Pictures"),
                os.path.expanduser("~/Videos"),
                os.path.expanduser("~/Music"),
                os.path.expanduser("~/OneDrive"),  # OneDrive común en Windows
                "C:/Users/Public/Desktop",
                "C:/Users/Public/Documents",
                "C:/Users/Public/Downloads",
                "C:/temp",
                "C:/tmp"
            ]
            
            # Extensiones de archivos comunes (expandidas)
            extensiones = [
                '*.txt', '*.pdf', '*.docx', '*.doc', '*.xlsx', '*.xls', '*.pptx', '*.ppt',
                '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.webp',
                '*.mp4', '*.avi', '*.mkv', '*.mov', '*.wmv', '*.flv', '*.webm',
                '*.mp3', '*.wav', '*.flac', '*.aac', '*.ogg', '*.m4a',
                '*.zip', '*.rar', '*.7z', '*.tar', '*.gz',
                '*.py', '*.js', '*.html', '*.css', '*.json', '*.xml',
                '*.exe', '*.msi', '*.bat', '*.cmd',
                '*.log', '*.md', '*.ini', '*.cfg', '*.conf'
            ]
            
            for directorio in directorios_busqueda:
                if len(archivos_encontrados) >= limite:
                    break
                    
                if not os.path.exists(directorio):
                    continue
                    
                try:
                    self.logger.info(f"Buscando en: {directorio}")
                    
                    # Buscar archivos que contengan el término en el nombre
                    for extension in extensiones:
                        if len(archivos_encontrados) >= limite:
                            break
                            
                        patron = f"**/*{termino_busqueda}*{extension}"
                        ruta_patron = os.path.join(directorio, patron)
                        
                        try:
                            for archivo in glob.glob(ruta_patron, recursive=True):
                                if len(archivos_encontrados) >= limite:
                                    break
                                    
                                try:
                                    # Verificar que el archivo existe y es accesible
                                    if not os.path.isfile(archivo):
                                        continue
                                        
                                    stat = os.stat(archivo)
                                    tamaño = self.formatear_tamaño(stat.st_size)
                                    
                                    # Evitar duplicados
                                    if any(a['ruta'] == archivo for a in archivos_encontrados):
                                        continue
                                    
                                    archivos_encontrados.append({
                                        'nombre': os.path.basename(archivo),
                                        'ruta': archivo,
                                        'tamaño': tamaño,
                                        'tipo': pathlib.Path(archivo).suffix.upper().replace('.', '') or 'ARCHIVO',
                                        'directorio': os.path.dirname(archivo),
                                        'fecha_modificacion': datetime.datetime.fromtimestamp(stat.st_mtime)
                                    })
                                    
                                except (OSError, PermissionError) as e:
                                    self.logger.debug(f"Error accediendo a {archivo}: {e}")
                                    continue
                                    
                        except (OSError, PermissionError) as e:
                            self.logger.debug(f"Error en patrón {ruta_patron}: {e}")
                            continue
                            
                except (OSError, PermissionError) as e:
                    self.logger.debug(f"Error accediendo al directorio {directorio}: {e}")
                    continue
            
            # Ordenar por fecha de modificación (más recientes primero)
            archivos_encontrados.sort(key=lambda x: x['fecha_modificacion'], reverse=True)
            
            self.logger.info(f"Encontrados {len(archivos_encontrados)} archivos")
            return archivos_encontrados
            
        except Exception as e:
            self.logger.error(f"Error buscando archivos: {e}")
            return []
    
    def formatear_tamaño(self, tamaño_bytes: int) -> str:
        """Formatear tamaño de archivo en formato legible"""
        try:
            if tamaño_bytes < 1024:
                return f"{tamaño_bytes} B"
            elif tamaño_bytes < 1024**2:
                return f"{tamaño_bytes/1024:.1f} KB"
            elif tamaño_bytes < 1024**3:
                return f"{tamaño_bytes/(1024**2):.1f} MB"
            else:
                return f"{tamaño_bytes/(1024**3):.1f} GB"
        except:
            return "Desconocido"
    
    def formatear_resultados_busqueda(self, archivos: List[Dict[str, str]], termino: str) -> str:
        """Formatear resultados de búsqueda para mostrar al usuario"""
        if not archivos:
            return f"No se encontraron archivos que contengan '{termino}' en tu PC. Verifique que tenga los permisos necesarios para acceder a los directorios."
        
        resultado = f"🔍 Encontré {len(archivos)} archivos con '{termino}' (ordenados por fecha más reciente):\n\n"
        
        for i, archivo in enumerate(archivos[:10], 1):  # Mostrar máximo 10
            resultado += f"📄 {i}. {archivo['nombre']}\n"
            resultado += f"   📁 Ubicación: {archivo['directorio']}\n"
            resultado += f"   📏 Tamaño: {archivo['tamaño']} | Tipo: {archivo['tipo']}\n"
            
            # Añadir fecha si está disponible
            if 'fecha_modificacion' in archivo:
                fecha_str = archivo['fecha_modificacion'].strftime("%d/%m/%Y %H:%M")
                resultado += f"   📅 Modificado: {fecha_str}\n"
                
            resultado += "\n"
        
        if len(archivos) > 10:
            resultado += f"... y {len(archivos) - 10} archivos más.\n"
            resultado += "💡 Diga 'dame el listado completo' para ver todos los resultados.\n"
        
        return resultado
    
    def detectar_solicitud_web(self, comando: str) -> Optional[str]:
        """Detectar si el usuario quiere abrir una página web"""
        comando_lower = comando.lower()
        
        # Palabras clave para abrir páginas web
        palabras_clave_web = [
            "abrir página", "abrir pagina", "abrir web", "abrir sitio", "ir a",
            "examinar página", "examinar pagina", "examinar web", "examinar sitio",
            "navegar a", "visitar", "mostrar página", "mostrar pagina"
        ]
        
        # Sitios web comunes con sus URLs
        sitios_comunes = {
            'google': 'https://www.google.com',
            'youtube': 'https://www.youtube.com',
            'facebook': 'https://www.facebook.com',
            'instagram': 'https://www.instagram.com',
            'twitter': 'https://www.twitter.com',
            'linkedin': 'https://www.linkedin.com',
            'github': 'https://www.github.com',
            'wikipedia': 'https://www.wikipedia.org',
            'gmail': 'https://www.gmail.com',
            'outlook': 'https://www.outlook.com',
            'netflix': 'https://www.netflix.com',
            'amazon': 'https://www.amazon.com',
            'mercadolibre': 'https://www.mercadolibre.com',
            'yahoo': 'https://www.yahoo.com'
        }
        
        for palabra_clave in palabras_clave_web:
            if palabra_clave in comando_lower:
                # Extraer el término después de la palabra clave
                partes = comando_lower.split(palabra_clave)
                if len(partes) > 1:
                    termino = partes[1].strip()
                    
                    # Buscar en sitios comunes primero
                    for sitio, url in sitios_comunes.items():
                        if sitio in termino:
                            return url
                    
                    # Si contiene http/https, usar directamente
                    if 'http' in termino:
                        # Extraer la URL
                        palabras = termino.split()
                        for palabra in palabras:
                            if palabra.startswith('http'):
                                return palabra
                    
                    # Si es solo un dominio, añadir https://
                    if '.' in termino and ' ' not in termino.strip():
                        url_limpia = termino.strip()
                        if not url_limpia.startswith('http'):
                            url_limpia = f'https://{url_limpia}'
                        return url_limpia
                    
                    # Si no se encontró nada específico, buscar en Google
                    return f'https://www.google.com/search?q={termino.replace(" ", "+")}'
        
        return None
    
    def abrir_pagina_web(self, url: str) -> str:
        """Abrir una página web en el navegador predeterminado"""
        try:
            self.logger.info(f"Abriendo página web: {url}")
            
            # Abrir en el navegador predeterminado
            webbrowser.open(url)
            
            # Determinar qué tipo de sitio es para la respuesta
            sitio_nombre = self.obtener_nombre_sitio(url)
            
            return f"🌐 He abierto {sitio_nombre} en su navegador predeterminado. La página debería cargarse en unos segundos."
            
        except Exception as e:
            self.logger.error(f"Error abriendo página web {url}: {e}")
            return f"❌ No pude abrir la página web. Error: {str(e)}"
    
    def obtener_nombre_sitio(self, url: str) -> str:
        """Obtener el nombre amigable de un sitio web"""
        sitios_conocidos = {
            'google.com': 'Google',
            'youtube.com': 'YouTube',
            'facebook.com': 'Facebook',
            'instagram.com': 'Instagram',
            'twitter.com': 'Twitter',
            'linkedin.com': 'LinkedIn',
            'github.com': 'GitHub',
            'wikipedia.org': 'Wikipedia',
            'gmail.com': 'Gmail',
            'outlook.com': 'Outlook',
            'netflix.com': 'Netflix',
            'amazon.com': 'Amazon',
            'mercadolibre.com': 'MercadoLibre',
            'yahoo.com': 'Yahoo'
        }
        
        for dominio, nombre in sitios_conocidos.items():
            if dominio in url:
                return nombre
        
        # Si no es un sitio conocido, extraer el dominio
        try:
            if 'search?q=' in url:
                return 'una búsqueda en Google'
            elif '//' in url:
                dominio = url.split('//')[1].split('/')[0]
                return f'el sitio web {dominio}'
            else:
                return 'la página web solicitada'
        except:
            return 'la página web'

    def detectar_traduccion_codigo(self, comando: str) -> Optional[Dict[str, str]]:
        """Detectar si el usuario quiere traducir código de programación"""
        comando_lower = comando.lower()
        
        # Palabras clave para traducción de código
        palabras_clave_traduccion = [
            "traducir código", "convertir código", "migrar código", "transformar código",
            "pasar código", "cambiar lenguaje", "convertir de", "traducir de"
        ]
        
        # Lenguajes soportados
        lenguajes_programacion = {
            'python': ['python', 'py'],
            'java': ['java'],
            'javascript': ['javascript', 'js', 'node'],
            'typescript': ['typescript', 'ts'],
            'c++': ['c++', 'cpp', 'cplus'],
            'c#': ['c#', 'csharp'],
            'go': ['go', 'golang'],
            'rust': ['rust'],
            'kotlin': ['kotlin'],
            'swift': ['swift'],
            'dart': ['dart'],
            'php': ['php'],
            'ruby': ['ruby'],
            'scala': ['scala'],
            'r': ['r'],
            'matlab': ['matlab'],
            'lua': ['lua']
        }
        
        for palabra_clave in palabras_clave_traduccion:
            if palabra_clave in comando_lower:
                # Buscar patrones como "de python a java"
                patron_traduccion = r'de\s+(\w+)\s+a\s+(\w+)'
                match = re.search(patron_traduccion, comando_lower)
                
                if match:
                    origen = match.group(1)
                    destino = match.group(2)
                    
                    # Verificar si los lenguajes son válidos
                    origen_valido = None
                    destino_valido = None
                    
                    for lenguaje, alias in lenguajes_programacion.items():
                        if origen in alias:
                            origen_valido = lenguaje
                        if destino in alias:
                            destino_valido = lenguaje
                    
                    if origen_valido and destino_valido:
                        # Buscar archivo en el comando
                        archivo = self.extraer_archivo_comando(comando)
                        return {
                            'archivo': archivo,
                            'origen': origen_valido,
                            'destino': destino_valido
                        }
        
        return None
    
    def extraer_archivo_comando(self, comando: str) -> Optional[str]:
        """Extraer nombre de archivo del comando"""
        # Buscar patrones de archivo con extensión
        patron_archivo = r'[\w\-\.]+\.(py|java|js|ts|cpp|cs|go|rs|kt|swift|dart|php|rb|scala|r|m|lua)'
        match = re.search(patron_archivo, comando, re.IGNORECASE)
        
        if match:
            return match.group(0)
        
        # Buscar palabras que podrían ser nombres de archivo
        palabras = comando.split()
        for palabra in palabras:
            if '.' in palabra and len(palabra) > 3:
                return palabra
        
        return None
    
    def traducir_codigo(self, archivo: Optional[str], lenguaje_origen: str, lenguaje_destino: str) -> str:
        """Traducir código de un lenguaje a otro usando Gemini"""
        try:
            codigo_fuente = None
            
            # Si se especifica un archivo, intentar leerlo
            if archivo:
                archivo_path = self.buscar_archivo_especifico(archivo)
                if archivo_path:
                    try:
                        with open(archivo_path, 'r', encoding='utf-8') as f:
                            codigo_fuente = f.read()
                    except Exception as e:
                        return f"❌ Error leyendo el archivo {archivo}: {e}"
                else:
                    return f"❌ No se encontró el archivo {archivo}"
            
            # Si no hay archivo, solicitar al usuario que proporcione el código
            if not codigo_fuente:
                return f"""🔄 **TRADUCTOR DE CÓDIGO - {lenguaje_origen.upper()} a {lenguaje_destino.upper()}**

Para traducir código, necesito que proporcione:

1. **Archivo específico**: Mencione el nombre del archivo (ej: "traducir archivo main.py de python a java")
2. **Código directo**: Pegue el código en el próximo mensaje

📋 **Lenguajes soportados**:
• Python ↔ Java, JavaScript, TypeScript, C++, C#, Go, Rust
• Java ↔ Python, JavaScript, TypeScript, C++, C#, Kotlin, Scala  
• JavaScript ↔ Python, Java, TypeScript, C++, C#, Go, Dart
• TypeScript ↔ JavaScript, Python, Java, C++, C#
• Y muchos más...

💡 **Ejemplo**: "traducir de python a java el archivo calculadora.py"
                """
            
            # Realizar la traducción usando Gemini
            prompt_traduccion = self.crear_prompt_traduccion(codigo_fuente, lenguaje_origen, lenguaje_destino)
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt_traduccion)
            
            if response and response.text:
                codigo_traducido = response.text.strip()
                
                # Guardar el código traducido en un archivo
                nombre_archivo_salida = self.generar_nombre_archivo_salida(archivo, lenguaje_destino)
                archivo_salida = os.path.join(os.path.expanduser("~/Desktop"), nombre_archivo_salida)
                
                try:
                    with open(archivo_salida, 'w', encoding='utf-8') as f:
                        f.write(codigo_traducido)
                    
                    resultado = f"""✅ **TRADUCCIÓN COMPLETADA**

🔄 **De**: {lenguaje_origen.capitalize()} 
🎯 **A**: {lenguaje_destino.capitalize()}
📁 **Archivo original**: {archivo or 'Código proporcionado'}
💾 **Archivo generado**: {archivo_salida}

📋 **Código traducido**:
```{lenguaje_destino}
{codigo_traducido[:500]}{'...' if len(codigo_traducido) > 500 else ''}
```

✅ El archivo completo se ha guardado en su escritorio.
                    """
                    
                    return resultado
                    
                except Exception as e:
                    return f"✅ Traducción completada pero error guardando archivo: {e}\n\n**Código traducido**:\n```{lenguaje_destino}\n{codigo_traducido}\n```"
            else:
                return "❌ Error: No se pudo generar la traducción del código"
                
        except Exception as e:
            self.logger.error(f"Error traduciendo código: {e}")
            return f"❌ Error en la traducción: {e}"
    
    def crear_prompt_traduccion(self, codigo: str, origen: str, destino: str) -> str:
        """Crear prompt especializado para traducción de código"""
        return f"""Eres un experto programador con conocimiento profundo en múltiples lenguajes de programación.

TAREA: Traducir el siguiente código de {origen} a {destino}.

INSTRUCCIONES:
1. Mantén la lógica y funcionalidad exacta del código original
2. Usa las mejores prácticas y convenciones del lenguaje de destino ({destino})
3. Añade comentarios explicativos cuando sea necesario
4. Optimiza el código para el lenguaje de destino
5. Incluye imports/includes necesarios
6. Mantén la estructura y organización del código

CÓDIGO ORIGINAL ({origen}):
```{origen}
{codigo}
```

TRADUCCIÓN A {destino.upper()}:
Proporciona SOLO el código traducido, sin explicaciones adicionales."""
    
    def generar_nombre_archivo_salida(self, archivo_original: Optional[str], lenguaje_destino: str) -> str:
        """Generar nombre para el archivo de salida"""
        extensiones = {
            'python': '.py',
            'java': '.java',
            'javascript': '.js',
            'typescript': '.ts',
            'c++': '.cpp',
            'c#': '.cs',
            'go': '.go',
            'rust': '.rs',
            'kotlin': '.kt',
            'swift': '.swift',
            'dart': '.dart',
            'php': '.php',
            'ruby': '.rb',
            'scala': '.scala',
            'r': '.r',
            'matlab': '.m',
            'lua': '.lua'
        }
        
        extension = extensiones.get(lenguaje_destino, '.txt')
        
        if archivo_original:
            # Quitar extensión original y añadir nueva
            nombre_base = archivo_original.rsplit('.', 1)[0]
            return f"{nombre_base}_translated{extension}"
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"codigo_traducido_{timestamp}{extension}"
    
    def detectar_migracion_db(self, comando: str) -> Optional[Dict[str, str]]:
        """Detectar si el usuario quiere migrar una base de datos"""
        comando_lower = comando.lower()
        
        # Palabras clave para migración de BD
        palabras_clave_migracion = [
            "migrar base de datos", "migrar bd", "convertir base datos", "migrar sql",
            "convertir sql", "transformar base datos", "pasar base datos", "migrar esquema"
        ]
        
        # Sistemas de base de datos soportados
        sistemas_bd = {
            'postgresql': ['postgresql', 'postgres', 'postgrest'],
            'mysql': ['mysql'],
            'sqlserver': ['sqlserver', 'sql server', 'mssql'],
            'oracle': ['oracle'],
            'sqlite': ['sqlite'],
            'mongodb': ['mongodb', 'mongo'],
            'firebase': ['firebase', 'firestore'],
            'mariadb': ['mariadb'],
            'cassandra': ['cassandra'],
            'redis': ['redis'],
            'dynamodb': ['dynamodb'],
            'neo4j': ['neo4j']
        }
        
        for palabra_clave in palabras_clave_migracion:
            if palabra_clave in comando_lower:
                # Buscar patrones como "de postgresql a mysql"
                patron_migracion = r'de\s+(\w+)\s+a\s+(\w+)'
                match = re.search(patron_migracion, comando_lower)
                
                if match:
                    origen = match.group(1)
                    destino = match.group(2)
                    
                    # Verificar si los sistemas son válidos
                    origen_valido = None
                    destino_valido = None
                    
                    for sistema, alias in sistemas_bd.items():
                        if origen in alias:
                            origen_valido = sistema
                        if destino in alias:
                            destino_valido = sistema
                    
                    if origen_valido and destino_valido:
                        # Buscar archivo en el comando
                        archivo = self.extraer_archivo_comando(comando)
                        return {
                            'archivo': archivo,
                            'origen': origen_valido,
                            'destino': destino_valido
                        }
        
        return None
    
    def migrar_base_datos(self, archivo: Optional[str], bd_origen: str, bd_destino: str) -> str:
        """Migrar esquema/datos de una base de datos a otra"""
        try:
            contenido_bd = None
            
            # Si se especifica un archivo, intentar leerlo
            if archivo:
                archivo_path = self.buscar_archivo_especifico(archivo)
                if archivo_path:
                    try:
                        with open(archivo_path, 'r', encoding='utf-8') as f:
                            contenido_bd = f.read()
                    except Exception as e:
                        return f"❌ Error leyendo el archivo {archivo}: {e}"
                else:
                    return f"❌ No se encontró el archivo {archivo}"
            
            # Si no hay archivo, proporcionar información
            if not contenido_bd:
                return f"""🗄️ **MIGRADOR DE BASES DE DATOS - {bd_origen.upper()} a {bd_destino.upper()}**

Para migrar una base de datos, necesito:

1. **Archivo SQL/Schema**: Mencione el archivo (ej: "migrar database.sql de postgresql a mysql")
2. **Script directo**: Proporcione el SQL en el próximo mensaje

📋 **Sistemas soportados**:
• **Relacionales**: PostgreSQL, MySQL, SQL Server, Oracle, SQLite, MariaDB
• **NoSQL**: MongoDB, Firebase/Firestore, Cassandra, Redis, DynamoDB
• **Grafos**: Neo4j

🔄 **Migraciones populares**:
• PostgreSQL → MySQL
• MySQL → PostgreSQL  
• SQL Server → PostgreSQL
• Oracle → PostgreSQL
• MongoDB → PostgreSQL (conversión)
• Firebase → MongoDB

💡 **Ejemplo**: "migrar de postgresql a mysql el archivo esquema.sql"
                """
            
            # Realizar la migración usando Gemini
            prompt_migracion = self.crear_prompt_migracion(contenido_bd, bd_origen, bd_destino)
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt_migracion)
            
            if response and response.text:
                esquema_migrado = response.text.strip()
                
                # Guardar el esquema migrado
                nombre_archivo_salida = self.generar_nombre_archivo_bd(archivo, bd_destino)
                archivo_salida = os.path.join(os.path.expanduser("~/Desktop"), nombre_archivo_salida)
                
                try:
                    with open(archivo_salida, 'w', encoding='utf-8') as f:
                        f.write(esquema_migrado)
                    
                    resultado = f"""✅ **MIGRACIÓN DE BASE DE DATOS COMPLETADA**

🗄️ **De**: {bd_origen.capitalize()} 
🎯 **A**: {bd_destino.capitalize()}
📁 **Archivo original**: {archivo or 'Schema proporcionado'}
💾 **Archivo generado**: {archivo_salida}

📋 **Schema migrado** (preview):
```sql
{esquema_migrado[:800]}{'...' if len(esquema_migrado) > 800 else ''}
```

✅ **Incluye**:
• Conversión de tipos de datos
• Ajustes de sintaxis específicos
• Optimizaciones para el motor destino
• Comentarios explicativos

💾 El archivo completo se ha guardado en su escritorio.
                    """
                    
                    return resultado
                    
                except Exception as e:
                    return f"✅ Migración completada pero error guardando: {e}\n\n**Schema migrado**:\n```sql\n{esquema_migrado}\n```"
            else:
                return "❌ Error: No se pudo generar la migración"
                
        except Exception as e:
            self.logger.error(f"Error migrando base de datos: {e}")
            return f"❌ Error en la migración: {e}"
    
    def crear_prompt_migracion(self, contenido: str, origen: str, destino: str) -> str:
        """Crear prompt especializado para migración de BD"""
        return f"""Eres un experto en bases de datos con conocimiento profundo en múltiples sistemas de gestión de bases de datos.

TAREA: Migrar el siguiente esquema/script de {origen} a {destino}.

INSTRUCCIONES:
1. Convierte todos los tipos de datos al equivalente en {destino}
2. Ajusta la sintaxis específica del motor {destino}
3. Mantén la integridad referencial y constraints
4. Optimiza para el rendimiento en {destino}
5. Incluye comentarios sobre cambios importantes
6. Adapta funciones específicas del sistema
7. Maneja diferencias en auto-incremento, secuencias, etc.

CONSIDERACIONES ESPECÍFICAS PARA {destino.upper()}:
- Usa tipos de datos nativos optimizados
- Aplica mejores prácticas de indexación
- Considera limitaciones y características únicas

ESQUEMA ORIGINAL ({origen.upper()}):
```sql
{contenido}
```

MIGRACIÓN A {destino.upper()}:
Proporciona SOLO el código SQL migrado, sin explicaciones adicionales."""
    
    def generar_nombre_archivo_bd(self, archivo_original: Optional[str], bd_destino: str) -> str:
        """Generar nombre para el archivo de BD migrado"""
        if archivo_original:
            nombre_base = archivo_original.rsplit('.', 1)[0]
            return f"{nombre_base}_{bd_destino}.sql"
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"schema_migrado_{bd_destino}_{timestamp}.sql"
    
    def detectar_visualizacion_archivo(self, comando: str) -> Optional[str]:
        """Detectar si el usuario quiere visualizar/adjuntar un archivo"""
        comando_lower = comando.lower()
        
        # Palabras clave para visualización de archivos
        palabras_clave_archivo = [
            "mostrar archivo", "ver archivo", "abrir archivo", "leer archivo",
            "visualizar archivo", "adjuntar archivo", "examinar archivo",
            "revisar archivo", "inspeccionar archivo", "analizar archivo"
        ]
        
        for palabra_clave in palabras_clave_archivo:
            if palabra_clave in comando_lower:
                # Extraer nombre del archivo
                archivo = self.extraer_archivo_comando(comando)
                if not archivo:
                    # Buscar después de la palabra clave
                    partes = comando_lower.split(palabra_clave)
                    if len(partes) > 1:
                        termino = partes[1].strip()
                        words = termino.split()
                        for word in words:
                            if '.' in word and len(word) > 3:
                                return word
                return archivo or "archivo_solicitado"
        
        return None
    
    def visualizar_archivo(self, archivo_nombre: str) -> str:
        """Visualizar y analizar un archivo"""
        try:
            # Buscar el archivo
            archivo_path = self.buscar_archivo_especifico(archivo_nombre)
            
            if not archivo_path:
                return f"""❌ No se encontró el archivo "{archivo_nombre}"

🔍 **Sugerencias**:
• Verifique que el nombre esté correcto
• El archivo debe estar en directorios accesibles
• Use búsqueda: "buscar en mi pc {archivo_nombre}"
                """
            
            # Obtener información del archivo
            stat_info = os.stat(archivo_path)
            tamaño = self.formatear_tamaño(stat_info.st_size)
            fecha_mod = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime("%d/%m/%Y %H:%M")
            extension = pathlib.Path(archivo_path).suffix.lower()
            
            # Determinar tipo MIME
            tipo_mime, _ = mimetypes.guess_type(archivo_path)
            
            resultado = f"""📄 **ANÁLISIS DE ARCHIVO**

📁 **Archivo**: {os.path.basename(archivo_path)}
📂 **Ubicación**: {os.path.dirname(archivo_path)}
📏 **Tamaño**: {tamaño}
📅 **Modificado**: {fecha_mod}
🏷️ **Tipo**: {tipo_mime or 'Desconocido'}
🔧 **Extensión**: {extension}

"""
            
            # Analizar contenido según el tipo de archivo
            if extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.sql', '.csv']:
                # Archivos de texto
                try:
                    with open(archivo_path, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    
                    lineas = contenido.count('\n') + 1
                    caracteres = len(contenido)
                    
                    resultado += f"""📊 **CONTENIDO DE TEXTO**:
📝 **Líneas**: {lineas}
🔤 **Caracteres**: {caracteres}

📋 **Preview** (primeras 500 caracteres):
```{extension[1:] if extension else 'text'}
{contenido[:500]}{'...' if len(contenido) > 500 else ''}
```

✅ **Archivo de texto legible y procesable**
                    """
                    
                except Exception as e:
                    resultado += f"❌ Error leyendo archivo de texto: {e}"
                    
            elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                # Archivos de imagen
                resultado += f"""🖼️ **ARCHIVO DE IMAGEN**:
📸 **Formato**: {extension[1:].upper()}
💾 **Tamaño**: {tamaño}

✅ **Imagen detectada - Puede ser visualizada en aplicaciones gráficas**
🔧 **Acciones disponibles**: Análisis de metadatos, conversión de formato
                """
                
            elif extension in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
                # Archivos de video
                resultado += f"""🎬 **ARCHIVO DE VIDEO**:
📹 **Formato**: {extension[1:].upper()}
💾 **Tamaño**: {tamaño}

✅ **Video detectado - Puede ser reproducido en reproductores multimedia**
🔧 **Acciones disponibles**: Análisis de metadatos, conversión de formato
                """
                
            elif extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
                # Archivos de audio
                resultado += f"""🎵 **ARCHIVO DE AUDIO**:
🎼 **Formato**: {extension[1:].upper()}
💾 **Tamaño**: {tamaño}

✅ **Audio detectado - Puede ser reproducido en reproductores multimedia**
🔧 **Acciones disponibles**: Análisis de metadatos, conversión de formato
                """
                
            elif extension in ['.pdf']:
                # Archivos PDF
                resultado += f"""📑 **ARCHIVO PDF**:
📄 **Formato**: PDF Document
💾 **Tamaño**: {tamaño}

✅ **PDF detectado - Requiere visor de PDF**
🔧 **Acciones disponibles**: Extracción de texto, análisis de contenido
                """
                
            elif extension in ['.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt']:
                # Archivos de Office
                resultado += f"""📊 **ARCHIVO DE OFFICE**:
🏢 **Formato**: Microsoft Office ({extension[1:].upper()})
💾 **Tamaño**: {tamaño}

✅ **Documento de Office detectado**
🔧 **Acciones disponibles**: Conversión a texto, análisis de contenido
                """
                
            elif extension in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                # Archivos comprimidos
                resultado += f"""📦 **ARCHIVO COMPRIMIDO**:
🗜️ **Formato**: {extension[1:].upper()}
💾 **Tamaño**: {tamaño}

✅ **Archivo comprimido detectado**
🔧 **Acciones disponibles**: Listar contenido, extraer archivos
                """
                
            else:
                # Archivo de tipo desconocido
                resultado += f"""❓ **ARCHIVO DE TIPO DESCONOCIDO**:
🔍 **Extensión**: {extension or 'Sin extensión'}
💾 **Tamaño**: {tamaño}

⚠️ **Tipo no reconocido - Análisis limitado disponible**
                """
            
            # Añadir opciones de acción
            resultado += f"""

🎯 **ACCIONES DISPONIBLES**:
• "abrir archivo {archivo_nombre}" - Abrir con aplicación predeterminada
• "copiar archivo {archivo_nombre}" - Copiar al portapapeles o destino
• "analizar archivo {archivo_nombre}" - Análisis profundo del contenido
            """
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error visualizando archivo: {e}")
            return f"❌ Error analizando el archivo: {e}"
    
    def buscar_archivo_especifico(self, nombre_archivo: str) -> Optional[str]:
        """Buscar un archivo específico en el sistema"""
        try:
            # Directorios donde buscar
            directorios_busqueda = [
                os.path.expanduser("~"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Pictures"),
                os.path.expanduser("~/Videos"),
                os.path.expanduser("~/Music"),
                os.path.expanduser("~/OneDrive"),
                "C:/temp",
                "C:/tmp"
            ]
            
            for directorio in directorios_busqueda:
                if not os.path.exists(directorio):
                    continue
                    
                try:
                    # Buscar archivo exacto
                    for root, dirs, files in os.walk(directorio):
                        for file in files:
                            if file.lower() == nombre_archivo.lower():
                                return os.path.join(root, file)
                            
                    # Buscar con glob para patrones
                    patron = os.path.join(directorio, f"**/{nombre_archivo}")
                    resultados = glob.glob(patron, recursive=True)
                    if resultados:
                        return resultados[0]
                        
                except (OSError, PermissionError):
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error buscando archivo específico: {e}")
            return None
    
    def detectar_gestion_correo(self, comando: str) -> Optional[Dict[str, str]]:
        """Detectar si el usuario quiere gestionar correo"""
        comando_lower = comando.lower()
        
        # Palabras clave para gestión de correo
        palabras_clave_correo = [
            "revisar correo", "ver correo", "abrir correo", "leer correo",
            "gestionar correo", "correos outlook", "email outlook",
            "responder correo", "contestar correo", "enviar correo"
        ]
        
        for palabra_clave in palabras_clave_correo:
            if palabra_clave in comando_lower:
                # Determinar tipo de acción
                if any(word in comando_lower for word in ["responder", "contestar", "enviar"]):
                    return {"accion": "responder", "comando": comando}
                elif any(word in comando_lower for word in ["revisar", "ver", "leer", "abrir"]):
                    return {"accion": "leer", "comando": comando}
                else:
                    return {"accion": "gestionar", "comando": comando}
        
        return None
    
    def gestionar_correo(self, datos_correo: Dict[str, str]) -> str:
        """Gestionar correo electrónico de Outlook"""
        try:
            accion = datos_correo.get("accion", "gestionar")
            
            if accion == "leer":
                return self.leer_correos_outlook()
            elif accion == "responder":
                return self.responder_correo_outlook(datos_correo["comando"])
            else:
                return self.gestionar_correo_general()
                
        except Exception as e:
            self.logger.error(f"Error gestionando correo: {e}")
            return f"❌ Error gestionando correo: {e}"
    
    def leer_correos_outlook(self) -> str:
        """Leer correos de Outlook usando la aplicación del sistema"""
        try:
            # Intentar abrir Outlook
            try:
                # En Windows, usar COM para acceder a Outlook
                subprocess.run(['outlook.exe'], check=False)
                
                return """📧 **GESTOR DE CORREO OUTLOOK ACTIVADO**

🔄 **Estado**: Outlook se está abriendo...

📋 **Funcionalidades disponibles**:

📥 **Leer correos**:
• Los correos más recientes se mostrarán en Outlook
• Busque por remitente, asunto o fecha
• Revise bandeja de entrada y carpetas

📤 **Responder correos**:
• Seleccione el correo en Outlook
• Use "responder correo sobre [tema]" para asistencia
• JARVIS puede ayudar a redactar respuestas

🎯 **Comandos útiles**:
• "responder correo sobre reunión" 
• "redactar correo para [persona]"
• "revisar correos importantes"

⚠️ **Nota**: Para acceso completo, configure la integración COM de Outlook en configuración avanzada.
                """
                
            except Exception:
                # Fallback: abrir Outlook web
                webbrowser.open('https://outlook.office.com/')
                
                return """📧 **OUTLOOK WEB ACTIVADO**

🌐 **Estado**: Outlook Web se está abriendo en su navegador...

📋 **Acceso web disponible**:
• Inicie sesión con sus credenciales Microsoft
• Acceso completo a correos, calendario y contactos
• Funcionalidad completa desde el navegador

🎯 **Para ayuda con respuestas**:
• Copie el texto del correo
• Use "redactar respuesta para [tema]"
• JARVIS ayudará con el contenido

🔧 **Configuración avanzada**:
Para integración directa, instale las librerías:
• pywin32 (para COM de Windows)  
• exchangelib (para Exchange Server)
                """
                
        except Exception as e:
            return f"❌ Error abriendo Outlook: {e}"
    
    def responder_correo_outlook(self, comando: str) -> str:
        """Ayudar a responder correos"""
        try:
            # Extraer el tema o contexto del comando
            tema = self.extraer_tema_correo(comando)
            
            if not tema:
                return """📝 **ASISTENTE DE RESPUESTA DE CORREO**

Para ayudarle a redactar una respuesta, necesito más información:

📋 **Opciones disponibles**:
1. **Tema específico**: "responder correo sobre reunión del lunes"
2. **Tipo de respuesta**: "responder correo de agradecimiento"  
3. **Contexto**: "responder correo de trabajo sobre proyecto"

📧 **Tipos de respuesta que puedo ayudar a redactar**:
• Confirmaciones de reuniones
• Respuestas de agradecimiento
• Declinaciones profesionales
• Solicitudes de información
• Respuestas de seguimiento
• Correos de disculpa profesional

💡 **Ejemplo**: "responder correo sobre la reunión de mañana"
                """
            
            # Generar respuesta usando Gemini
            prompt_correo = self.crear_prompt_correo(tema, comando)
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt_correo)
            
            if response and response.text:
                respuesta_sugerida = response.text.strip()
                
                return f"""📧 **RESPUESTA SUGERIDA PARA CORREO**

📋 **Tema detectado**: {tema}

✉️ **Respuesta recomendada**:
```
{respuesta_sugerida}
```

🎯 **Instrucciones**:
1. Copie el texto sugerido
2. Péguelo en su correo en Outlook
3. Personalice según sea necesario
4. Revise antes de enviar

📝 **Opciones adicionales**:
• "hacer más formal la respuesta"
• "hacer más breve la respuesta"  
• "añadir tono más amigable"
                """
            else:
                return "❌ Error generando respuesta de correo"
                
        except Exception as e:
            return f"❌ Error preparando respuesta: {e}"
    
    def extraer_tema_correo(self, comando: str) -> Optional[str]:
        """Extraer tema del correo del comando"""
        comando_lower = comando.lower()
        
        # Buscar patrones como "sobre X", "acerca de X", etc.
        patrones = [
            r'sobre\s+(.+)',
            r'acerca\s+de\s+(.+)',
            r'referente\s+a\s+(.+)',
            r'para\s+(.+)',
            r'correo\s+de\s+(.+)'
        ]
        
        for patron in patrones:
            match = re.search(patron, comando_lower)
            if match:
                return match.group(1).strip()
        
        # Si no encuentra patrón específico, tomar palabras después de ciertas palabras clave
        palabras_clave = ["responder", "contestar", "correo"]
        for palabra in palabras_clave:
            if palabra in comando_lower:
                partes = comando_lower.split(palabra, 1)
                if len(partes) > 1:
                    resto = partes[1].strip()
                    # Quitar palabras comunes del inicio
                    resto = re.sub(r'^(correo|email|sobre|de|para|con|a)\s+', '', resto)
                    if resto:
                        return resto
        
        return None
    
    def crear_prompt_correo(self, tema: str, comando_completo: str) -> str:
        """Crear prompt para generar respuesta de correo"""
        return f"""Eres un asistente profesional especializado en redacción de correos electrónicos empresariales.

TAREA: Redactar una respuesta de correo profesional y apropiada.

CONTEXTO: {comando_completo}
TEMA PRINCIPAL: {tema}

INSTRUCCIONES:
1. Redacta un correo profesional y cortés
2. Mantén un tono apropiado para el contexto empresarial
3. Sé conciso pero completo
4. Incluye saludo y despedida apropiados
5. Usa un lenguaje claro y directo
6. Adapta el tono según el tema (formal, amigable, informativo, etc.)

ESTRUCTURA REQUERIDA:
- Saludo apropiado
- Cuerpo del mensaje (2-3 párrafos máximo)
- Despedida profesional
- NO incluyas [Nombre] o campos variables

RESPUESTA DE CORREO:"""
    
    def gestionar_correo_general(self) -> str:
        """Información general sobre gestión de correo"""
        return """📧 **CENTRO DE GESTIÓN DE CORREO ELECTRONICO**

🎯 **Comandos disponibles**:

📥 **Leer correos**:
• "revisar correo outlook"
• "ver correos nuevos" 
• "abrir bandeja de entrada"

📤 **Responder correos**:
• "responder correo sobre [tema]"
• "contestar correo de agradecimiento"
• "redactar respuesta formal"

✍️ **Redactar correos**:
• "redactar correo para [persona]"
• "escribir correo de seguimiento"
• "crear correo de disculpa"

🔧 **Configuración avanzada**:
Para integración completa con Outlook:
1. Instalar pywin32: `pip install pywin32`
2. Configurar permisos COM en Windows
3. Habilitar macros en Outlook

🌐 **Acceso web siempre disponible**:
• Outlook.com se abre automáticamente
• Acceso completo desde navegador
• Sin configuración adicional necesaria
        """

    def detectar_busqueda_local(self, comando: str) -> Optional[str]:
        """Detectar si el usuario quiere buscar archivos en su PC"""
        palabras_clave = [
            "buscar en mi pc", "buscar archivo", "buscar archivos", "encuentra archivo",
            "buscar en mi computadora", "buscar documento", "buscar documentos",
            "encontrar archivo", "encontrar archivos", "localizar archivo",
            "buscar en disco", "buscar local", "archivos en mi pc"
        ]
        
        comando_lower = comando.lower()
        
        for palabra_clave in palabras_clave:
            if palabra_clave in comando_lower:
                # Extraer el término de búsqueda
                partes = comando_lower.split(palabra_clave)
                if len(partes) > 1:
                    termino = partes[1].strip()
                    # Limpiar palabras comunes
                    termino = termino.replace("llamado", "").replace("con nombre", "").replace("que se llame", "")
                    termino = termino.replace("de", "").replace("con", "").replace("que", "").strip()
                    return termino if termino else None
        
        return None
    
    def es_solicitud_resultados(self, comando: str) -> bool:
        """Detectar si el usuario solicita ver los resultados de la última búsqueda"""
        frases_solicitud = [
            "dame el listado", "muestra los archivos", "mostrar los archivos",
            "enseña los archivos", "dime los archivos", "cuáles archivos",
            "qué archivos encontraste", "los archivos que encontraste",
            "muestra los resultados", "dame los resultados", "ver los archivos",
            "lista de archivos", "listado de archivos", "archivos encontrados"
        ]
        
        comando_lower = comando.lower()
        return any(frase in comando_lower for frase in frases_solicitud)
    
    def mostrar_ultimos_resultados(self) -> str:
        """Mostrar los últimos resultados de búsqueda con detalles completos"""
        if not self.ultima_busqueda['archivos']:
            return "No hay resultados previos para mostrar."
        
        archivos = self.ultima_busqueda['archivos']
        termino = self.ultima_busqueda['termino']
        timestamp = self.ultima_busqueda['timestamp']
        
        # Formatear timestamp
        tiempo_busqueda = timestamp.strftime("%H:%M:%S") if timestamp else "hace un momento"
        
        resultado = f"📋 **LISTADO COMPLETO DE ARCHIVOS ENCONTRADOS**\n"
        resultado += f"🔍 Término buscado: '{termino}'\n"
        resultado += f"⏰ Búsqueda realizada: {tiempo_busqueda}\n"
        resultado += f"📊 Total encontrados: {len(archivos)} archivos\n\n"
        resultado += "═" * 60 + "\n\n"
        
        for i, archivo in enumerate(archivos, 1):
            resultado += f"📄 **{i}. {archivo['nombre']}**\n"
            resultado += f"   📁 **Ruta completa:** {archivo['ruta']}\n"
            resultado += f"   📏 **Tamaño:** {archivo['tamaño']}\n"
            resultado += f"   🏷️  **Tipo:** {archivo['tipo']}\n"
            resultado += f"   📂 **Directorio:** {archivo['directorio']}\n"
            
            # Añadir fecha de modificación si está disponible
            if 'fecha_modificacion' in archivo:
                fecha_str = archivo['fecha_modificacion'].strftime("%d/%m/%Y %H:%M")
                resultado += f"   📅 **Modificado:** {fecha_str}\n"
                
            resultado += "─" * 50 + "\n\n"
        
        resultado += f"✅ **Resumen:** Se encontraron {len(archivos)} archivos que contienen '{termino}' en su nombre.\n"
        resultado += "💡 **Sugerencia:** Puedo ayudarle a abrir cualquiera de estos archivos si me indica cuál desea."
        
        return resultado
    
    def iniciar_escucha(self):
        """Iniciar proceso de escucha de voz"""
        if not self.is_listening:
            self.is_listening = True
            self.estadoCambiado.emit('LISTENING')
            self.logger.info("Iniciando escucha de voz...")
            
            # Forzar activación del proceso de escucha
            QTimer.singleShot(100, self.proceso_completo_asistente)
    
    def detener_escucha(self):
        """Detener proceso de escucha"""
        self.is_listening = False
        self.estadoCambiado.emit('IDLE')
        self.logger.info("Escucha de voz detenida")
    
    def procesar_comando_texto(self, texto: str):
        """Procesar comando de texto"""
        if not texto.strip():
            return
            
        self.logger.info(f"Procesando comando: {texto}")
        self.estadoCambiado.emit('THINKING')
        
        # Procesar con Gemini
        respuesta = self.procesar_con_gemini(texto)
        
        if respuesta:
            # Solo emitir la respuesta actual, no leer historial completo
            self.respuestaLista.emit(respuesta)
            self.responseReady.emit(respuesta)  # Alias para compatibilidad
            self.estadoCambiado.emit('SPEAKING')
            self.logger.info("Respuesta enviada para síntesis (solo último resultado)")
        else:
            self.errorOcurrido.emit("No se pudo procesar el comando")
            self.estadoCambiado.emit('IDLE')

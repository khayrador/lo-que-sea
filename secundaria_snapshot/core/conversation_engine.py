"""
Motor de conversación para Jarvis
Maneja el procesamiento de lenguaje natural y respuestas inteligentes
"""

import json
import random
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import os

class ConversationEngine:
    """Motor de conversación para el asistente"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.user_name = "Usuario"
        self.assistant_name = "Jarvis"
        
        # Patrones de comando mejorados
        self.command_patterns = {
            "abrir_archivo": [
                r"abr[ie]r?\s+(?:el\s+)?archivo\s+(.+)",
                r"mostrar\s+(?:el\s+)?archivo\s+(.+)",
                r"ver\s+(?:el\s+)?archivo\s+(.+)"
            ],
            "buscar_archivo": [
                r"buscar\s+archivos?\s+(.+)",
                r"encontrar\s+archivos?\s+(.+)",
                r"localizar\s+archivos?\s+(.+)",
                r"archivos?\s+(?:de\s+)?(.+)"
            ],
            "buscar_archivo_inteligente": [
                r"buscar\s+(?:mis\s+)?archivos?\s+(.+)",
                r"encontrar\s+(?:todos\s+los\s+)?archivos?\s+(.+)",
                r"archivos?\s+recientes?\s+(.+)",
                r"archivos?\s+grandes?\s+(.+)",
                r"archivos?\s+(?:de\s+)?(.+?)\s+(?:del|de)\s+(.+)"
            ],
            "buscar_por_categoria": [
                r"(?:buscar\s+)?(?:mis\s+)?(documentos?|imágenes?|videos?|música|audio|código|datos)",
                r"(?:encontrar\s+)?(?:todos\s+los\s+)?(documentos?|imágenes?|videos?|música|audio|código|datos)",
                r"(?:ver\s+)?(?:mis\s+)?(documentos?|imágenes?|videos?|música|audio|código|datos)"
            ],
            "buscar_en_contenido": [
                r"buscar\s+(?:en\s+)?(?:el\s+)?contenido\s+(.+)",
                r"archivos?\s+(?:que\s+)?conten(?:ga|gan)\s+(.+)",
                r"encontrar\s+(?:texto\s+)?(.+)\s+en\s+archivos?"
            ],
            "abrir_web": [
                r"abr[ie]r?\s+(?:la\s+)?(?:página\s+)?(?:web\s+)?(.+)",
                r"ir\s+a\s+(.+)",
                r"navegar\s+a\s+(.+)"
            ],
            "buscar_web": [
                r"buscar\s+(?:en\s+)?(?:google\s+)?(.+)",
                r"googlear\s+(.+)",
                r"busca\s+(.+)"
            ],
            "crear_archivo": [
                r"crear\s+(?:un\s+)?archivo\s+(.+)",
                r"nuevo\s+archivo\s+(.+)",
                r"hacer\s+archivo\s+(.+)"
            ],
            "tiempo": [
                r"qué\s+hora\s+es",
                r"hora\s+actual",
                r"dime\s+la\s+hora"
            ],
            "fecha": [
                r"qué\s+día\s+es",
                r"fecha\s+actual",
                r"dime\s+la\s+fecha"
            ],
            "analizar_web": [
                r"analizar?\s+(?:la\s+)?(?:página\s+)?(?:web\s+)?(.+)",
                r"examinar?\s+(?:la\s+)?(?:página\s+)?(?:web\s+)?(.+)",
                r"revisar?\s+(?:la\s+)?(?:página\s+)?(?:web\s+)?(.+)",
                r"inspeccionar?\s+(?:la\s+)?(?:página\s+)?(?:web\s+)?(.+)"
            ],
            "buscar_analizar": [
                r"buscar\s+y\s+analizar\s+(.+)",
                r"analizar\s+búsqueda\s+(.+)",
                r"buscar\s+información\s+(?:sobre\s+)?(.+)"
            ],
            "escuchar_microfono": [
                r"escuchar?\s+micrófono",
                r"activar?\s+micrófono",
                r"usar?\s+micrófono",
                r"escuchar?\s+voz",
                r"modo\s+conversación"
            ],
            "conversacion_continua": [
                r"hablar\s+(?:por\s+)?voz",
                r"conversación\s+(?:por\s+)?voz",
                r"modo\s+conversación",
                r"empezar\s+conversación",
                r"conversar"
            ]
        }
        
        # Respuestas predefinidas
        self.responses = {
            "saludo": [
                "¡Hola! Soy Jarvis, tu asistente virtual. ¿En qué puedo ayudarte?",
                "¡Saludos! ¿Qué necesitas que haga por ti hoy?",
                "¡Hola! Estoy aquí para asistirte. ¿Qué tarea tienes para mí?"
            ],
            "despedida": [
                "¡Hasta luego! Ha sido un placer asistirte.",
                "¡Adiós! Estaré aquí cuando me necesites.",
                "¡Nos vemos! Que tengas un excelente día."
            ],
            "agradecimiento": [
                "¡De nada! Para eso estoy aquí.",
                "¡Un placer ayudarte!",
                "¡Siempre a tu servicio!"
            ],
            "no_entiendo": [
                "No estoy seguro de entender. ¿Podrías reformular tu solicitud?",
                "Disculpa, no comprendo completamente. ¿Puedes ser más específico?",
                "No he podido procesar esa solicitud. ¿Podrías explicarla de otra manera?"
            ],
            "error": [
                "Ha ocurrido un error al procesar tu solicitud.",
                "Algo no salió como esperaba. Intentémoslo de nuevo.",
                "Ups, parece que hubo un problema. ¿Puedes intentar otra vez?"
            ]
        }
        
        # Cargar configuración de personalidad si existe
        self.load_personality_config()
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Procesar un mensaje del usuario
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Diccionario con tipo de respuesta y contenido
        """
        message = message.strip().lower()
        
        # Agregar a historial
        self.add_to_history("user", message)
        
        # Detectar tipo de mensaje
        message_type = self.detect_message_type(message)
        
        # Procesar según el tipo
        if message_type == "command":
            return self.process_command(message)
        elif message_type == "question":
            return self.process_question(message)
        elif message_type == "greeting":
            response = random.choice(self.responses["saludo"])
            return {"type": "response", "content": response}
        elif message_type == "farewell":
            response = random.choice(self.responses["despedida"])
            return {"type": "response", "content": response}
        elif message_type == "thanks":
            response = random.choice(self.responses["agradecimiento"])
            return {"type": "response", "content": response}
        else:
            return self.generate_general_response(message)
    
    def detect_message_type(self, message: str) -> str:
        """Detectar el tipo de mensaje"""
        
        # Saludos
        greeting_patterns = [
            r"\b(hola|buenos?\s+(días?|tardes?|noches?)|saludos?|hey)\b"
        ]
        
        # Despedidas
        farewell_patterns = [
            r"\b(adiós?|hasta\s+luego|nos\s+vemos|chau|bye|hasta\s+la\s+vista)\b"
        ]
        
        # Agradecimientos
        thanks_patterns = [
            r"\b(gracias?|muchas\s+gracias|te\s+agradezco|thanks)\b"
        ]
        
        # Comandos
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return "command"
        
        # Otros tipos
        for pattern in greeting_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return "greeting"
                
        for pattern in farewell_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return "farewell"
                
        for pattern in thanks_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return "thanks"
        
        # Preguntas
        if message.startswith(("qué", "cómo", "cuándo", "dónde", "por qué", "quién")):
            return "question"
            
        return "general"
    
    def process_command(self, message: str) -> Dict[str, Any]:
        """Procesar comandos específicos con funcionalidades mejoradas"""
        
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    if command_type == "tiempo":
                        current_time = datetime.now().strftime("%H:%M:%S")
                        return {
                            "type": "response",
                            "content": f"🕐 Son las {current_time}"
                        }
                    elif command_type == "fecha":
                        current_date = datetime.now().strftime("%d/%m/%Y")
                        day_name = datetime.now().strftime("%A")
                        day_names = {
                            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                        }
                        spanish_day = day_names.get(day_name, day_name)
                        return {
                            "type": "response", 
                            "content": f"📅 Hoy es {spanish_day}, {current_date}"
                        }
                    elif command_type == "buscar_archivo_inteligente":
                        param = match.group(1) if match.groups() else ""
                        return {
                            "type": "command",
                            "command": "buscar_archivo_inteligente",
                            "parameter": param.strip(),
                            "content": f"🔍 Búsqueda inteligente de archivos: '{param}'"
                        }
                    elif command_type == "buscar_por_categoria":
                        categoria = match.group(1).lower() if match.groups() else ""
                        return {
                            "type": "command",
                            "command": "buscar_por_categoria",
                            "parameter": categoria,
                            "content": f"📁 Buscando archivos de categoría: '{categoria}'"
                        }
                    elif command_type == "buscar_en_contenido":
                        param = match.group(1) if match.groups() else ""
                        return {
                            "type": "command",
                            "command": "buscar_en_contenido",
                            "parameter": param.strip(),
                            "content": f"🔎 Buscando en contenido de archivos: '{param}'"
                        }
                    elif command_type == "conversacion_continua":
                        return {
                            "type": "command",
                            "command": "conversacion_continua",
                            "parameter": "",
                            "content": "🎤 Iniciando modo conversación por voz..."
                        }
                    else:
                        # Comandos que requieren parámetros
                        param = match.group(1) if match.groups() else ""
                        return {
                            "type": "command",
                            "command": command_type,
                            "parameter": param.strip(),
                            "content": f"Ejecutando: {command_type} con parámetro '{param}'"
                        }
        
        return {"type": "response", "content": random.choice(self.responses["no_entiendo"])}
    
    def process_question(self, message: str) -> Dict[str, Any]:
        """Procesar preguntas generales"""
        
        # Respuestas a preguntas comunes
        qa_patterns = {
            r"qué\s+puedes?\s+hacer": "Puedo ayudarte a buscar archivos, abrir páginas web, crear y editar archivos, realizar búsquedas en internet, analizar sitios web (tecnologías, seguridad, videos), y mantener conversaciones contigo. También puedo usar reconocimiento de voz si tienes micrófono.",
            r"cómo\s+(?:te\s+)?llamas?": f"Soy {self.assistant_name}, tu asistente virtual personal.",
            r"quién\s+eres": f"Soy {self.assistant_name}, un asistente virtual diseñado para ayudarte con tareas de escritorio y conversación.",
            r"cómo\s+estás": "¡Estoy funcionando perfectamente y listo para ayudarte!",
            r"qué\s+hora\s+es": datetime.now().strftime("Son las %H:%M:%S"),
            r"qué\s+día\s+es": datetime.now().strftime("Hoy es %A, %d de %B de %Y"),
            r"cómo\s+analizar?\s+(?:una\s+)?(?:página\s+)?web": "Para analizar una página web, usa: 'analizar [sitio.com]' o 'examinar [URL]'. Por ejemplo: 'analizar google.com' o 'examinar https://github.com'. Puedo detectar tecnologías, videos, seguridad y más.",
            r"qué\s+sitios?\s+puedo\s+analizar": "Puedes analizar cualquier sitio web público. Ejemplos: 'analizar youtube.com', 'examinar netflix.com', 'revisar github.com'. Detectaré tecnologías, videos, seguridad y contenido multimedia."
        }
        
        for pattern, answer in qa_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                return {"type": "response", "content": answer}
        
        return {"type": "response", "content": "Esa es una pregunta interesante. ¿Hay algo específico en lo que pueda ayudarte?"}
    
    def generate_general_response(self, message: str) -> Dict[str, Any]:
        """Generar respuesta general para mensajes no categorizados"""
        
        general_responses = [
            "Entiendo. ¿Hay algo específico que necesites que haga?",
            "Interesante. ¿En qué puedo asistirte?", 
            "Ya veo. ¿Qué tarea puedo realizar por ti?",
            "Comprendo. ¿Necesitas ayuda con algún archivo o búsqueda web?"
        ]
        
        return {"type": "response", "content": random.choice(general_responses)}
    
    def add_to_history(self, sender: str, content: str):
        """Agregar mensaje al historial"""
        self.conversation_history.append({
            "sender": sender,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mantener solo los últimos 50 mensajes
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Obtener historial de conversación"""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Limpiar historial de conversación"""
        self.conversation_history.clear()
    
    def load_personality_config(self):
        """Cargar configuración de personalidad desde archivo"""
        config_path = "config/personality.json"
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.assistant_name = config.get("assistant_name", self.assistant_name)
                
                # Actualizar respuestas si están definidas
                if "custom_responses" in config:
                    self.responses.update(config["custom_responses"])
                    
            except Exception as e:
                print(f"Error cargando configuración de personalidad: {e}")
    
    def save_conversation(self, filename: Optional[str] = None):
        """Guardar conversación actual"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            
        try:
            with open(f"conversations/{filename}", 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
                
            return f"Conversación guardada como {filename}"
            
        except Exception as e:
            return f"Error guardando conversación: {e}"
    
    def get_help_text(self) -> str:
        """Obtener texto de ayuda con comandos disponibles"""
        help_text = """
🤖 **Comandos disponibles:**

**Archivos:**
- "Abrir archivo [nombre]" - Abre un archivo
- "Buscar archivo [nombre]" - Busca archivos en el sistema
- "Crear archivo [nombre]" - Crea un nuevo archivo

**Web:**
- "Abrir [url/sitio]" - Abre una página web
- "Buscar [término]" - Realiza búsqueda en Google
- "ir a [sitio]" - Navega a un sitio web
- "Analizar [url/sitio]" - Analiza una página web (tecnologías, seguridad, videos)

**Micrófono:**
- "Escuchar micrófono" - Activa el reconocimiento de voz
- "Activar micrófono" - Inicia la escucha por voz

**Información:**
- "¿Qué hora es?" - Muestra la hora actual
- "¿Qué día es?" - Muestra la fecha actual
- "¿Qué puedes hacer?" - Lista de capacidades

**Conversación:**
- Puedes preguntarme cualquier cosa o simplemente charlar conmigo
- Dime "hola" para saludar o "adiós" para despedirte

¡Estoy aquí para ayudarte! 😊
        """
        return help_text.strip()

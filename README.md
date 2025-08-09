# Jarvis - Asistente Virtual de Escritorio

Un asistente virtual inteligente desarrollado en Python con interfaz gráfica que te ayuda con tareas del escritorio como gestión de archivos, navegación web y conversación fluida.

## 🚀 Características principales

- **Interfaz gráfica intuitiva** con tema oscuro moderno
- **Gestión de archivos**: Buscar, abrir, crear y editar archivos
- **Navegación web**: Abrir sitios web y realizar búsquedas
- **Conversación inteligente**: Procesamiento de lenguaje natural en español
- **Reconocimiento de voz** (opcional)
- **Síntesis de voz** (opcional)
- **Sistema de comandos** natural y fácil de usar

## 📋 Requisitos del sistema

- Windows 10/11
- Python 3.7 o superior
- Micrófono (opcional, para reconocimiento de voz)
- Altavoces/auriculares (opcional, para síntesis de voz)

## 🛠️ Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd jarvis
   ```

2. **Instalar dependencias básicas**
   ```bash
   pip install -r requirements.txt
   ```

3. **Instalar dependencias opcionales de voz**
   ```bash
   # Para reconocimiento de voz
   pip install SpeechRecognition
   
   # Para síntesis de voz
   pip install pyttsx3
   
   # Para papelera de reciclaje
   pip install send2trash
   ```

## 🚀 Uso

### Ejecutar la aplicación
```bash
python main.py
```

### Comandos disponibles

**Gestión de archivos:**
- "Abrir archivo [nombre]" - Abre un archivo específico
- "Buscar archivo [nombre]" - Busca archivos en el sistema
- "Crear archivo [nombre]" - Crea un nuevo archivo

**Navegación web:**
- "Abrir [sitio/URL]" - Abre una página web
- "Buscar [término]" - Realiza búsqueda en Google
- "ir a [sitio]" - Navega a un sitio específico

**Información:**
- "¿Qué hora es?" - Muestra la hora actual
- "¿Qué día es?" - Muestra la fecha actual
- "¿Qué puedes hacer?" - Lista de capacidades

**Conversación:**
- Puedes charlar naturalmente con Jarvis
- Saludar con "hola" y despedirse con "adiós"
- Hacer preguntas generales

## 🎛️ Interfaz de usuario

### Elementos principales:
- **Área de chat**: Conversación con Jarvis
- **Campo de entrada**: Para escribir mensajes y comandos  
- **Botones de control**:
  - 🎤 **Voz**: Activar/desactivar modo de voz
  - 📁 **Archivos**: Acceso rápido al gestor de archivos
  - 🌐 **Web**: Controles de navegación web
  - ❓ **Ayuda**: Mostrar comandos disponibles
  - ⚙️ **Config**: Configuración del asistente

### Atajos de teclado:
- **Enter**: Enviar mensaje
- **Escape**: Limpiar campo de entrada

## 📁 Estructura del proyecto

```
jarvis/
├── main.py                 # Aplicación principal
├── requirements.txt        # Dependencias
├── README.md              # Este archivo
├── config/
│   └── settings.json      # Configuración
├── core/
│   ├── __init__.py
│   ├── file_manager.py    # Gestión de archivos
│   ├── web_manager.py     # Gestión web
│   ├── conversation_engine.py  # Motor de conversación
│   └── voice_manager.py   # Gestión de voz
├── ui/
│   ├── __init__.py
│   └── main_window.py     # Interfaz principal  
└── .github/
    └── copilot-instructions.md
```

## ⚙️ Configuración

Edita `config/settings.json` para personalizar:

- **Nombre del asistente**
- **Idioma de reconocimiento de voz**
- **Rutas de búsqueda de archivos**
- **Motor de búsqueda predeterminado**
- **Respuestas personalizadas**

## 🔧 Desarrollo y personalización

### Agregar nuevos comandos:
1. Edita `core/conversation_engine.py`
2. Agrega patrones en `command_patterns`
3. Implementa el manejador en `ui/main_window.py`

### Personalizar la interfaz:
1. Modifica colores en `ui/main_window.py`
2. Ajusta estilos en `setup_styles()`
3. Agrega nuevos elementos en `create_interface()`

## 🤝 Funcionalidades futuras

- [ ] Integración con APIs de IA (OpenAI, etc.)
- [ ] Sistema de plugins
- [ ] Automatización de tareas más avanzada
- [ ] Soporte para múltiples idiomas
- [ ] Integración con calendarios y recordatorios
- [ ] Control de aplicaciones del sistema
- [ ] Análisis y edición de documentos

## 📝 Notas técnicas

### Dependencias opcionales:
- **SpeechRecognition**: Para reconocimiento de voz
- **pyttsx3**: Para síntesis de voz  
- **send2trash**: Para papelera de reciclage
- **requests**: Para funciones web avanzadas

### Compatibilidad:
- Desarrollado y probado en Windows
- Interfaz responsiva que se adapta a diferentes resoluciones
- Tema oscuro para reducir fatiga visual

## 🆘 Solución de problemas

### La aplicación no inicia:
- Verifica que Python 3.7+ esté instalado
- Instala las dependencias: `pip install -r requirements.txt`

### El reconocimiento de voz no funciona:
- Instala: `pip install SpeechRecognition`
- Verifica que el micrófono esté conectado
- Otorga permisos de micrófono a Python

### La síntesis de voz no funciona:
- Instala: `pip install pyttsx3`
- Verifica que los altavoces estén conectados

## 📄 Licencia

Este proyecto es de código abierto. Puedes usarlo, modificarlo y distribuirlo libremente.

---

**¡Disfruta usando Jarvis! 🤖**

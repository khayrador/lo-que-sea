# Instalación de Dependencias de Voz para Jarvis

## 🎤 Para habilitar el reconocimiento de voz

### Opción 1: Instalación automática
```bash
pip install SpeechRecognition pyttsx3 pyaudio
```

### Opción 2: Instalación paso a paso

1. **SpeechRecognition** (reconocimiento de voz)
```bash
pip install SpeechRecognition
```

2. **pyttsx3** (síntesis de voz)
```bash
pip install pyttsx3
```

3. **pyaudio** (interfaz de audio)
```bash
pip install pyaudio
```

## ⚠️ Solución de problemas en Windows

### Si pyaudio falla al instalar:

**Opción A:** Descargar wheel precompilado
```bash
pip install pipwin
pipwin install pyaudio
```

**Opción B:** Instalar desde Microsoft Store
1. Instalar "Microsoft C++ Build Tools" desde Microsoft Store
2. Reiniciar PowerShell
3. Ejecutar: `pip install pyaudio`

**Opción C:** Usar conda (si tienes Anaconda)
```bash
conda install pyaudio
```

## 🎯 Verificación de instalación

Ejecutar este comando para verificar:
```bash
python -c "import speech_recognition as sr; import pyttsx3; print('✅ Dependencias de voz instaladas correctamente')"
```

## 🔧 Configuración adicional

### Para mejor calidad de reconocimiento:
1. Usar un micrófono de buena calidad
2. Minimizar ruido ambiente
3. Hablar claramente y a velocidad normal

### Comandos de voz disponibles una vez instalado:
- "Escuchar micrófono" - Activa reconocimiento
- "Activar micrófono" - Inicia escucha
- Cualquier comando normal de Jarvis por voz

## 🚀 Funcionalidades de voz habilitadas:

✅ **Reconocimiento de voz** - Convierte voz a texto
✅ **Síntesis de voz** - Jarvis puede responder por audio  
✅ **Comandos por voz** - Todos los comandos disponibles por voz
✅ **Modo conversacional** - Interacción natural por voz

---

**Nota:** Las funciones básicas de Jarvis funcionan sin estas dependencias. La voz es una característica adicional opcional.

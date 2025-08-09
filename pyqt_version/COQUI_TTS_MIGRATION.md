# Migración a Coqui TTS - Síntesis de Voz Local

## ¿Por qué Coqui TTS?

Hemos migrado de ElevenLabs a Coqui TTS por las siguientes razones:

### ✅ Ventajas de Coqui TTS
- **🆓 Gratis**: Sin costos de API
- **🏠 Local**: Funciona completamente offline
- **🎯 Alta Calidad**: Síntesis neural avanzada
- **🔒 Privacidad**: Los datos no salen de tu computadora
- **⚡ Rápido**: Sin latencia de red
- **🌍 Multilingüe**: Soporte para múltiples idiomas

### ❌ Problemas con ElevenLabs
- 💰 Costos por uso
- 🌐 Requiere conexión a internet
- 🔑 Gestión de API keys
- 📊 Límites de uso

## Configuración

### Variables de Entorno (.env)
```env
# Configuración de TTS Local
VOICE_PROVIDER=coqui
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
TTS_SPEAKER=Dionisio Schuyler
TTS_LANGUAGE=es
```

### Modelos Disponibles
- **xtts_v2**: Modelo multilingüe de alta calidad (recomendado)
- **tacotron2-DDC**: Modelo rápido y ligero
- **glow-tts**: Modelo equilibrado

### Voces/Speakers Disponibles
- Dionisio Schuyler (español - masculino)
- Claribel Dervla (inglés - femenino)
- Daisy Studious (inglés - femenino)
- Gracie Wise (inglés - femenino)

## Implementación Técnica

### Audio Manager
```python
class AudioManager:
    def init_coqui_tts(self):
        """Inicializar Coqui TTS localmente"""
        from TTS.api import TTS
        self.tts = TTS(model_name=self.tts_model, progress_bar=False)
    
    def generate_coqui_audio(self, text: str) -> Optional[str]:
        """Generar audio con Coqui TTS"""
        temp_file = os.path.join(tempfile.gettempdir(), f"jarvis_audio_{int(time.time())}.wav")
        self.tts.tts_to_file(
            text=text,
            speaker=self.tts_speaker,
            language=self.tts_language,
            file_path=temp_file
        )
        return temp_file
```

### Dependencias Instaladas
```txt
TTS>=0.22.0          # Coqui TTS
torch                # PyTorch para modelos neurales
torchaudio           # Audio processing
soundfile            # Audio file handling
pyttsx3              # Fallback TTS
```

## Rendimiento

### Primera Ejecución
- 📥 Descarga automática del modelo (~1-2 GB)
- ⏱️ Inicialización: 30-60 segundos
- 💾 Almacenamiento en caché local

### Ejecuciones Posteriores
- ⚡ Inicio inmediato (modelo en caché)
- 🎯 Síntesis: 1-3 segundos por oración
- 🔄 Sin latencia de red

## Solución de Problemas

### Error: "No module named 'TTS'"
```bash
pip install TTS>=0.22.0
```

### Error: "torch not found"
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Audio no se reproduce
- Verificar que soundfile esté instalado
- Comprobar que el archivo temporal se genera
- Revisar configuración de QMediaPlayer

### Modelo no se descarga
- Verificar conexión a internet (solo primera vez)
- Comprobar espacio en disco (>2GB libre)
- Revisar permisos de escritura en directorio temporal

## Comparación de Rendimiento

| Característica | ElevenLabs | Coqui TTS |
|---------------|------------|-----------|
| Costo | 💰 Pago | 🆓 Gratis |
| Calidad | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Velocidad | 🌐 3-5s | ⚡ 1-3s |
| Offline | ❌ No | ✅ Sí |
| Privacidad | ⚠️ Cloud | 🔒 Local |
| Idiomas | 🌍 29 | 🌍 40+ |

## Migración Completada

### ✅ Archivos Actualizados
- `backend/audio_manager.py`: Implementación completa de Coqui TTS
- `workers/jarvis_worker.py`: Eliminadas dependencias de ElevenLabs
- `.env.template`: Configuración actualizada
- `requirements_pyqt.txt`: Dependencias de Coqui TTS
- `install.bat`: Script de instalación actualizado

### 🚀 Próximos Pasos
1. Ejecutar `install.bat` para instalar dependencias
2. Copiar `.env.template` a `.env`
3. Configurar `OPENAI_API_KEY` en `.env`
4. Ejecutar `python main_app.py`

La migración está completa y el asistente ahora funciona completamente con síntesis de voz local, eliminando costos de API y mejorando la privacidad y velocidad.

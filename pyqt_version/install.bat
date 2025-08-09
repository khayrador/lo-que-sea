@echo off
echo ========================================
echo     INSTALADOR DE JARVIS PYQT5
echo         CON COQUI TTS LOCAL
echo ========================================
echo.

echo [1/7] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en PATH
    pause
    exit /b 1
)

echo.
echo [2/7] Creando entorno virtual...
python -m venv jarvis_env
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo.
echo [3/7] Activando entorno virtual...
call jarvis_env\Scripts\activate.bat

echo.
echo [4/7] Actualizando pip...
python -m pip install --upgrade pip

echo.
echo [5/7] Instalando dependencias básicas...
pip install PyQt5>=5.15.0
pip install PyQt5-tools>=5.15.0.3.2
pip install python-dotenv>=0.19.0
pip install requests>=2.25.0
pip install SpeechRecognition>=3.10.0

echo.
echo [6/7] Instalando dependencias de IA...
echo Instalando OpenAI...
pip install openai>=1.0.0

echo.
echo [7/7] Instalando Coqui TTS para síntesis de voz local...
echo Esto puede tardar varios minutos...
pip install TTS>=0.22.0
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install soundfile
pip install pyttsx3

echo Intentando instalar pyaudio...
pip install pyaudio
if %errorlevel% neq 0 (
    echo ADVERTENCIA: pyaudio falló. Intentando con pipwin...
    pip install pipwin
    pipwin install pyaudio
    if %errorlevel% neq 0 (
        echo ADVERTENCIA: No se pudo instalar pyaudio. El reconocimiento de voz puede no funcionar.
    )
)

echo.
echo [OPCIONAL] Instalando dependencias de desarrollo...
pip install matplotlib>=3.5.0
pip install numpy>=1.21.0
pip install Pillow>=8.3.0

echo.
echo ========================================
echo        INSTALACIÓN COMPLETADA
echo         CON COQUI TTS LOCAL
echo ========================================
echo.
echo Configuración siguiente:
echo 1. Copia .env.template a .env
echo 2. Configura tu API key de OpenAI en .env
echo 3. Ejecuta: python main_app.py
echo.
echo VENTAJAS DE COQUI TTS:
echo - Síntesis de voz completamente local
echo - Sin costos de API
echo - Alta calidad de audio
echo - Funciona sin conexión a internet
echo.
echo Para activar el entorno en el futuro:
echo jarvis_env\Scripts\activate.bat
echo.
pause

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar los modelos disponibles en Google Gemini
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_gemini_models():
    """Probar qué modelos están disponibles"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ No se encontró GEMINI_API_KEY")
            return
        
        # Configurar API
        genai.configure(api_key=api_key)
        
        print("🔍 Listando modelos disponibles:")
        models = genai.list_models()
        
        for model in models:
            print(f"  📋 {model.name}")
            print(f"     Soporte para: {model.supported_generation_methods}")
            print()
        
        # Probar con diferentes nombres de modelo
        model_names = [
            'gemini-pro',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'models/gemini-pro',
            'models/gemini-1.5-pro',
            'models/gemini-1.5-flash'
        ]
        
        for model_name in model_names:
            try:
                print(f"🧪 Probando modelo: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Di hola en español")
                print(f"  ✅ Funciona: {response.text[:50]}...")
                print()
                break  # Si funciona, usar este modelo
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                print()
                
    except Exception as e:
        print(f"❌ Error general: {str(e)}")

if __name__ == "__main__":
    test_gemini_models()

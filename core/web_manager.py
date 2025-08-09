"""
Gestor web para Jarvis
Maneja operaciones de navegación web y pestañas
"""

import webbrowser
import requests
from typing import List, Dict, Optional, Any
import urllib.parse
from urllib.parse import urlparse
import re
import time

class WebManager:
    """Clase para manejar operaciones web"""
    
    def __init__(self):
        self.default_browser = None
        self.search_engines = {
            "google": "https://www.google.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "youtube": "https://www.youtube.com/results?search_query={}",
            "wikipedia": "https://es.wikipedia.org/wiki/Special:Search/{}"
        }
        
    def open_url(self, url: str, new_tab: bool = True) -> Dict[str, Any]:
        """
        Abrir una URL en el navegador
        
        Args:
            url: URL a abrir
            new_tab: Si abrir en nueva pestaña
            
        Returns:
            Diccionario con el resultado de la operación
        """
        try:
            # Validar y formatear URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            if new_tab:
                webbrowser.open(url, new=2)  # new=2 para nueva pestaña
            else:
                webbrowser.open(url, new=1)  # new=1 para nueva ventana
                
            return {
                "success": True,
                "url": url,
                "message": f"Abriendo {url} en el navegador"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al abrir URL: {str(e)}",
                "url": url
            }
    
    def search_web(self, query: str, engine: str = "google", new_tab: bool = True) -> Dict[str, Any]:
        """
        Realizar búsqueda web
        
        Args:
            query: Término de búsqueda
            engine: Motor de búsqueda a usar
            new_tab: Si abrir en nueva pestaña
            
        Returns:
            Diccionario con el resultado de la operación
        """
        try:
            if engine.lower() not in self.search_engines:
                engine = "google"
                
            # Codificar la consulta para URL
            encoded_query = urllib.parse.quote_plus(query)
            search_url = self.search_engines[engine.lower()].format(encoded_query)
            
            return self.open_url(search_url, new_tab)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en búsqueda web: {str(e)}",
                "query": query
            }
    
    def open_multiple_tabs(self, urls: List[str]) -> Dict[str, Any]:
        """
        Abrir múltiples URLs en pestañas
        
        Args:
            urls: Lista de URLs a abrir
            
        Returns:
            Diccionario con el resultado de la operación
        """
        results = []
        success_count = 0
        
        for url in urls:
            result = self.open_url(url, new_tab=True)
            results.append(result)
            if result.get("success"):
                success_count += 1
                
        return {
            "success": success_count > 0,
            "opened_tabs": success_count,
            "total_requested": len(urls),
            "results": results,
            "message": f"Se abrieron {success_count} de {len(urls)} pestañas"
        }
    
    def get_page_title(self, url: str) -> Optional[str]:
        """
        Obtener el título de una página web
        
        Args:
            url: URL de la página
            
        Returns:
            Título de la página o None si hay error
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Extraer título usando regex simple
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', response.text, re.IGNORECASE)
            
            if title_match:
                return title_match.group(1).strip()
                
        except Exception:
            pass
            
        return None
    
    def check_internet_connection(self) -> bool:
        """
        Verificar conexión a internet
        
        Returns:
            True si hay conexión, False en caso contrario
        """
        try:
            response = requests.get("http://www.google.com", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def open_social_media(self, platform: str, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Abrir redes sociales
        
        Args:
            platform: Plataforma social (facebook, twitter, instagram, etc.)
            username: Usuario específico (opcional)
            
        Returns:
            Resultado de la operación
        """
        social_urls = {
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "youtube": "https://www.youtube.com",
            "tiktok": "https://www.tiktok.com",
            "github": "https://www.github.com"
        }
        
        platform = platform.lower()
        
        if platform not in social_urls:
            return {
                "success": False,
                "error": f"Plataforma '{platform}' no reconocida",
                "available_platforms": list(social_urls.keys())
            }
        
        url = social_urls[platform]
        
        if username:
            url += f"/{username}"
            
        return self.open_url(url)
    
    def open_email(self, provider: str = "gmail") -> Dict[str, Any]:
        """
        Abrir cliente de email web
        
        Args:
            provider: Proveedor de email
            
        Returns:
            Resultado de la operación
        """
        email_urls = {
            "gmail": "https://mail.google.com",
            "outlook": "https://outlook.live.com",
            "yahoo": "https://mail.yahoo.com",
            "hotmail": "https://outlook.live.com"
        }
        
        provider = provider.lower()
        
        if provider not in email_urls:
            provider = "gmail"
            
        return self.open_url(email_urls[provider])
    
    def quick_search_shortcuts(self, query: str) -> Dict[str, Any]:
        """
        Búsquedas rápidas con atajos
        
        Args:
            query: Consulta con posible atajo (ej: "yt música relajante")
            
        Returns:
            Resultado de la operación
        """
        shortcuts = {
            "yt": "youtube",
            "wiki": "wikipedia",
            "g": "google",
            "dd": "duckduckgo"
        }
        
        words = query.split()
        if not words:
            return self.search_web(query)
            
        first_word = words[0].lower()
        
        if first_word in shortcuts:
            engine = shortcuts[first_word]
            remaining_query = " ".join(words[1:]) if len(words) > 1 else ""
            return self.search_web(remaining_query, engine)
        
        return self.search_web(query)
    
    def analyze_webpage(self, url: str) -> Dict[str, Any]:
        """
        Analizar una página web en detalle
        
        Args:
            url: URL de la página a analizar
            
        Returns:
            Diccionario con análisis completo de la página
        """
        try:
            # Validar y limpiar URL
            processed_url = self._process_url_input(url)
            if not processed_url:
                return {
                    "success": False,
                    "error": f"'{url}' no parece ser una URL válida. Intenta con algo como 'google.com' o 'https://ejemplo.com'",
                    "url": url
                }
            
            # Realizar petición con headers realistas
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            start_time = time.time()
            response = requests.get(processed_url, timeout=15, headers=headers)
            load_time = time.time() - start_time
            
            response.raise_for_status()
            
            # Información básica
            analysis = {
                "url": processed_url,
                "status_code": response.status_code,
                "load_time": round(load_time, 2),
                "content_length": len(response.content),
                "encoding": response.encoding,
                "headers": dict(response.headers)
            }
            
            # Analizar contenido HTML
            html_content = response.text
            analysis.update(self._analyze_html_content(html_content))
            
            # Analizar tecnologías
            analysis["technologies"] = self._detect_technologies(html_content, response.headers)
            
            # Analizar seguridad
            analysis["security"] = self._analyze_security(processed_url, response.headers)
            
            # Analizar medios
            analysis["media"] = self._analyze_media_content(html_content, processed_url)
            
            # Analizar SEO básico
            analysis["seo"] = self._analyze_seo(html_content)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error accediendo a la página: {str(e)}",
                "url": url,
                "suggestion": "Verifica que la URL sea correcta y que tengas conexión a internet"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error analizando página: {str(e)}",
                "url": url
            }
    
    def _process_url_input(self, url_input: str) -> Optional[str]:
        """
        Procesar y validar entrada de URL
        
        Args:
            url_input: Entrada del usuario (puede ser URL o texto)
            
        Returns:
            URL válida o None si no es válida
        """
        if not url_input or not url_input.strip():
            return None
        
        url_input = url_input.strip()
        
        # Si ya tiene protocolo, validar que sea una URL
        if url_input.startswith(('http://', 'https://')):
            parsed = urlparse(url_input)
            if parsed.netloc and '.' in parsed.netloc:
                return url_input
            return None
        
        # Si parece ser solo un dominio (tiene punto y no espacios)
        if '.' in url_input and ' ' not in url_input and len(url_input.split('.')) >= 2:
            # Verificar que no tenga caracteres extraños
            if re.match(r'^[a-zA-Z0-9.-]+$', url_input):
                return 'https://' + url_input
        
        # Si contiene espacios o caracteres especiales, probablemente no es una URL
        if ' ' in url_input or any(char in url_input for char in ['?', '&'] if not url_input.startswith('http')):
            return None
        
        # Intentar como dominio si tiene formato válido
        if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', url_input):
            return 'https://' + url_input
        
        return None
    
    def _analyze_html_content(self, html: str) -> Dict[str, Any]:
        """Analizar contenido HTML"""
        
        # Extraer título
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Sin título"
        
        # Extraer meta descripción
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else ""
        
        # Contar elementos
        links_count = len(re.findall(r'<a[^>]*href=', html, re.IGNORECASE))
        images_count = len(re.findall(r'<img[^>]*src=', html, re.IGNORECASE))
        forms_count = len(re.findall(r'<form[^>]*>', html, re.IGNORECASE))
        scripts_count = len(re.findall(r'<script[^>]*>', html, re.IGNORECASE))
        
        # Extraer idioma
        lang_match = re.search(r'<html[^>]*lang=["\']([^"\']*)["\']', html, re.IGNORECASE)
        language = lang_match.group(1) if lang_match else "No especificado"
        
        return {
            "title": title,
            "description": description,
            "language": language,
            "elements": {
                "links": links_count,
                "images": images_count,
                "forms": forms_count,
                "scripts": scripts_count
            }
        }
    
    def _detect_technologies(self, html: str, headers: Dict[str, str]) -> Dict[str, List[str]]:
        """Detectar tecnologías utilizadas"""
        
        technologies = {
            "frameworks": [],
            "cms": [],
            "analytics": [],
            "javascript": [],
            "css": [],
            "server": []
        }
        
        # Detectar por headers del servidor
        server = headers.get('Server', '').lower()
        if server:
            if 'apache' in server:
                technologies["server"].append("Apache")
            elif 'nginx' in server:
                technologies["server"].append("Nginx")
            elif 'iis' in server:
                technologies["server"].append("IIS")
        
        # Detectar por contenido HTML
        html_lower = html.lower()
        
        # Frameworks CSS
        if 'bootstrap' in html_lower:
            technologies["css"].append("Bootstrap")
        if 'tailwind' in html_lower:
            technologies["css"].append("Tailwind CSS")
        if 'materialize' in html_lower:
            technologies["css"].append("Materialize")
        
        # JavaScript frameworks
        if 'react' in html_lower:
            technologies["javascript"].append("React")
        if 'vue' in html_lower:
            technologies["javascript"].append("Vue.js")
        if 'angular' in html_lower:
            technologies["javascript"].append("Angular")
        if 'jquery' in html_lower:
            technologies["javascript"].append("jQuery")
        
        # CMS
        if 'wp-content' in html_lower or 'wordpress' in html_lower:
            technologies["cms"].append("WordPress")
        if 'drupal' in html_lower:
            technologies["cms"].append("Drupal")
        if 'joomla' in html_lower:
            technologies["cms"].append("Joomla")
        
        # Analytics
        if 'google-analytics' in html_lower or 'gtag' in html_lower:
            technologies["analytics"].append("Google Analytics")
        if 'facebook.com/tr' in html_lower:
            technologies["analytics"].append("Facebook Pixel")
        if 'hotjar' in html_lower:
            technologies["analytics"].append("Hotjar")
        
        return technologies
    
    def _analyze_security(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analizar aspectos de seguridad"""
        
        security = {
            "https": url.startswith('https://'),
            "security_headers": {},
            "certificates": {},
            "vulnerabilities": []
        }
        
        # Verificar headers de seguridad
        security_headers = [
            'strict-transport-security',
            'content-security-policy',  
            'x-frame-options',
            'x-content-type-options',
            'x-xss-protection',
            'referrer-policy'
        ]
        
        for header in security_headers:
            value = headers.get(header, headers.get(header.title(), ''))
            security["security_headers"][header] = value if value else "No configurado"
        
        # Verificar vulnerabilidades comunes
        if not security["https"]:
            security["vulnerabilities"].append("Conexión no segura (HTTP)")
        
        if not security["security_headers"]["strict-transport-security"]:
            security["vulnerabilities"].append("HSTS no configurado")
        
        if not security["security_headers"]["content-security-policy"]:
            security["vulnerabilities"].append("CSP no configurado")
        
        return security
    
    def _analyze_media_content(self, html: str, base_url: str) -> Dict[str, Any]:
        """Analizar contenido multimedia"""
        
        media = {
            "videos": [],
            "audio": [],
            "images": {"count": 0, "formats": []},
            "embeds": []
        }
        
        # Detectar videos
        video_patterns = [
            r'<video[^>]*src=["\'](.*?)["\']',
            r'<iframe[^>]*src=["\'](.*?youtube\.com.*?)["\']',
            r'<iframe[^>]*src=["\'](.*?vimeo\.com.*?)["\']',
            r'<iframe[^>]*src=["\'](.*?dailymotion\.com.*?)["\']',
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if 'youtube' in match:
                    media["videos"].append({"type": "YouTube", "url": match})
                elif 'vimeo' in match:
                    media["videos"].append({"type": "Vimeo", "url": match})
                elif 'dailymotion' in match:
                    media["videos"].append({"type": "Dailymotion", "url": match})
                else:
                    media["videos"].append({"type": "Video HTML5", "url": match})
        
        # Detectar audio
        audio_matches = re.findall(r'<audio[^>]*src=["\'](.*?)["\']', html, re.IGNORECASE)
        for match in audio_matches:
            media["audio"].append(match)
        
        # Analizar imágenes
        img_matches = re.findall(r'<img[^>]*src=["\'](.*?)["\']', html, re.IGNORECASE)
        media["images"]["count"] = len(img_matches)
        
        formats = set()
        for img in img_matches:
            ext = img.split('.')[-1].lower()[:3]  # Primeros 3 caracteres de la extensión
            if ext in ['jpg', 'png', 'gif', 'svg', 'web', 'bmp']:
                formats.add(ext)
        
        media["images"]["formats"] = list(formats)
        
        # Detectar embeds de redes sociales
        embed_patterns = {
            "Twitter": r'twitter\.com/.*?/status/',
            "Instagram": r'instagram\.com/p/',
            "Facebook": r'facebook\.com/.*?/posts/',
            "TikTok": r'tiktok\.com/@.*?/video/'
        }
        
        for platform, pattern in embed_patterns.items():
            if re.search(pattern, html, re.IGNORECASE):
                media["embeds"].append(platform)
        
        return media
    
    def get_page_summary(self, url: str) -> Dict[str, Any]:
        """
        Obtener resumen rápido de una página
        
        Args:
            url: URL de la página
            
        Returns:
            Resumen de la página
        """
        # Primero validar la entrada
        if not url or not url.strip():
            return {
                "success": False,
                "error": "Por favor proporciona una URL válida",
                "suggestion": "Ejemplo: 'google.com' o 'https://ejemplo.com'"
            }
        
        analysis_result = self.analyze_webpage(url)
        
        if not analysis_result["success"]:
            # Si parece ser una búsqueda en lugar de URL, sugerir búsqueda
            if " " in url.strip() or not self._process_url_input(url):
                return {
                    "success": False,
                    "error": f"'{url}' parece ser una búsqueda, no una URL",
                    "suggestion": f"¿Querías buscar '{url}' en Google? Usa: buscar {url}"
                }
            return analysis_result
        
        analysis = analysis_result["analysis"]
        
        # Crear resumen legible
        summary = {
            "title": analysis.get("title", "Sin título"),
            "description": analysis.get("description", "Sin descripción"),
            "load_time": f"{analysis.get('load_time', 0)} segundos",
            "has_videos": len(analysis.get("media", {}).get("videos", [])) > 0,
            "video_count": len(analysis.get("media", {}).get("videos", [])),
            "technologies_summary": self._get_tech_summary(analysis.get("technologies", {})),
            "security_score": self._calculate_security_score(analysis.get("security", {})),
            "is_secure": analysis.get("security", {}).get("https", False)
        }
        
        return {
            "success": True,
            "summary": summary,
            "full_analysis": analysis
        }
    
    def _get_tech_summary(self, technologies: Dict[str, List[str]]) -> str:
        """Crear resumen de tecnologías"""
        tech_list = []
        
        for category, techs in technologies.items():
            if techs:
                tech_list.extend(techs)
        
        if not tech_list:
            return "No se detectaron tecnologías específicas"
        
        return ", ".join(tech_list[:5])  # Máximo 5 tecnologías principales
    
    def _calculate_security_score(self, security: Dict[str, Any]) -> str:
        """Calcular puntuación de seguridad"""
        score = 0
        max_score = 10
        
        # HTTPS (+3 puntos)
        if security.get("https", False):
            score += 3
        
        # Headers de seguridad (+1 punto cada uno, máximo 7)
        headers = security.get("security_headers", {})
        for header, value in headers.items():
            if value and value != "No configurado":
                score += 1
        
        # Convertir a porcentaje y clasificar
        percentage = (score / max_score) * 100
        
        if percentage >= 80:
            return f"Excelente ({percentage:.0f}%)"
        elif percentage >= 60:
            return f"Bueno ({percentage:.0f}%)"
        elif percentage >= 40:
            return f"Regular ({percentage:.0f}%)"
        else:
            return f"Deficiente ({percentage:.0f}%)"

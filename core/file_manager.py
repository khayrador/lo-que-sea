"""
Gestor de archivos para Jarvis
Maneja operaciones de búsqueda, lectura y modificación de archivos
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import json
import mimetypes
import re
from datetime import datetime, timedelta
import fnmatch

class FileManager:
    """Clase para manejar operaciones con archivos"""
    
    def __init__(self):
        # Rutas comunes de búsqueda con prioridad
        self.search_paths = [
            Path.home() / "Desktop",
            Path.home() / "Documents", 
            Path.home() / "Downloads",
            Path.home() / "Pictures",
            Path.home() / "Videos",
            Path.home() / "Music",
            Path.home(),
            Path("C:/") if os.name == 'nt' else Path("/"),
        ]
        
        # Extensiones categorizadas
        self.file_categories = {
            'documentos': ['.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt', '.md'],
            'imagenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'codigo': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.go', '.rs'],
            'datos': ['.json', '.xml', '.csv', '.xlsx', '.xls', '.db', '.sqlite'],
            'comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'ejecutables': ['.exe', '.msi', '.dmg', '.deb', '.rpm', '.app']
        }
        
    def smart_search_files(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Búsqueda inteligente de archivos con múltiples criterios
        
        Args:
            query: Término de búsqueda natural (ej: "archivos python del último mes")
            **kwargs: Parámetros adicionales
                - max_results: Número máximo de resultados (default: 100)
                - include_content: Buscar también en contenido de archivos (default: False)
                - recent_days: Buscar archivos modificados en los últimos N días
                - min_size: Tamaño mínimo en bytes
                - max_size: Tamaño máximo en bytes
                
        Returns:
            Diccionario con resultados de búsqueda y estadísticas
        """
        max_results = kwargs.get('max_results', 100)
        include_content = kwargs.get('include_content', False)
        recent_days = kwargs.get('recent_days', None)
        min_size = kwargs.get('min_size', None)
        max_size = kwargs.get('max_size', None)
        
        # Analizar consulta natural
        search_params = self._parse_natural_query(query)
        
        # Combinar parámetros
        if recent_days:
            search_params['recent_days'] = recent_days
        if min_size:
            search_params['min_size'] = min_size
        if max_size:
            search_params['max_size'] = max_size
            
        results = []
        stats = {
            'total_found': 0,
            'by_type': {},
            'by_location': {},
            'search_time': 0,
            'content_matches': 0
        }
        
        start_time = datetime.now()
        
        # Realizar búsqueda
        for search_path in self.search_paths:
            if not search_path.exists():
                continue
                
            location_name = search_path.name or str(search_path)
            stats['by_location'][location_name] = 0
                
            try:
                for file_path in search_path.rglob("*"):
                    if len(results) >= max_results:
                        break
                        
                    if not file_path.is_file():
                        continue
                    
                    # Aplicar filtros
                    if not self._matches_criteria(file_path, search_params):
                        continue
                    
                    # Buscar en contenido si se especifica
                    content_match = False
                    if include_content and self._is_text_file(file_path):
                        content_match = self._search_in_content(file_path, search_params['keywords'])
                        if content_match:
                            stats['content_matches'] += 1
                    
                    # Si no coincide ni nombre ni contenido, saltar
                    if not (self._matches_filename(file_path, search_params['keywords']) or content_match):
                        continue
                    
                    # Obtener información del archivo
                    file_info = self._get_detailed_file_info(file_path)
                    file_info['content_match'] = content_match
                    
                    results.append(file_info)
                    stats['total_found'] += 1
                    stats['by_location'][location_name] += 1
                    
                    # Actualizar estadísticas por tipo
                    file_type = file_info.get('category', 'otros')
                    stats['by_type'][file_type] = stats['by_type'].get(file_type, 0) + 1
                        
            except (PermissionError, OSError) as e:
                continue
        
        # Ordenar resultados por relevancia
        results = self._sort_by_relevance(results, search_params['keywords'])
        
        stats['search_time'] = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': True,
            'query': query,
            'results': results,
            'stats': stats,
            'suggestions': self._get_search_suggestions(query, stats)
        }
    
    def _parse_natural_query(self, query: str) -> Dict[str, Any]:
        """
        Analizar consulta en lenguaje natural y extraer parámetros
        
        Args:
            query: Consulta en lenguaje natural
            
        Returns:
            Diccionario con parámetros de búsqueda
        """
        query_lower = query.lower()
        params = {
            'keywords': [],
            'file_types': [],
            'categories': [],
            'recent_days': None,
            'size_range': None
        }
        
        # Extraer categorías de archivos
        for category, extensions in self.file_categories.items():
            if category in query_lower or any(cat in query_lower for cat in [category[:-1], category.rstrip('s')]):
                params['categories'].append(category)
                params['file_types'].extend(extensions)
        
        # Extraer extensiones específicas
        extension_pattern = r'\.([\w]+)'
        extensions = re.findall(extension_pattern, query)
        for ext in extensions:
            if not ext.startswith('.'):
                ext = '.' + ext
            params['file_types'].append(ext.lower())
        
        # Extraer términos temporales
        if any(term in query_lower for term in ['hoy', 'today', 'reciente']):
            params['recent_days'] = 1
        elif any(term in query_lower for term in ['ayer', 'yesterday']):
            params['recent_days'] = 2
        elif any(term in query_lower for term in ['esta semana', 'this week', 'semana']):
            params['recent_days'] = 7
        elif any(term in query_lower for term in ['este mes', 'this month', 'mes']):
            params['recent_days'] = 30
        elif 'último' in query_lower or 'last' in query_lower:
            # Buscar números seguidos de tiempo
            time_match = re.search(r'(\d+)\s*(día|días|day|days|semana|semanas|week|weeks)', query_lower)
            if time_match:
                num = int(time_match.group(1))
                unit = time_match.group(2)
                if 'día' in unit or 'day' in unit:
                    params['recent_days'] = num
                elif 'semana' in unit or 'week' in unit:
                    params['recent_days'] = num * 7
        
        # Extraer términos de tamaño
        if any(term in query_lower for term in ['grande', 'grandes', 'large', 'big']):
            params['size_range'] = (10*1024*1024, None)  # Más de 10MB
        elif any(term in query_lower for term in ['pequeño', 'pequeños', 'small', 'tiny']):
            params['size_range'] = (None, 1024*1024)  # Menos de 1MB
        
        # Extraer palabras clave (excluir palabras funcionales)
        stop_words = {
            'archivos', 'archivo', 'files', 'file', 'buscar', 'search', 'find', 'encontrar',
            'del', 'de', 'la', 'el', 'en', 'con', 'por', 'para', 'un', 'una', 'los', 'las',
            'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
        }
        
        # Limpiar query y extraer keywords
        clean_keywords = []
        words = re.findall(r'\b\w+\b', query_lower)
        for word in words:
            if len(word) > 2 and word not in stop_words:
                # No incluir si ya es una categoría o extensión
                if not any(word in cat for cat in self.file_categories.keys()):
                    clean_keywords.append(word)
        
        params['keywords'] = clean_keywords
        
        return params
    
    def _matches_criteria(self, file_path: Path, params: Dict[str, Any]) -> bool:
        """
        Verificar si un archivo cumple con los criterios de búsqueda
        """
        try:
            stat = file_path.stat()
            
            # Filtro por tipo de archivo
            if params['file_types']:
                file_ext = file_path.suffix.lower()
                if file_ext not in params['file_types']:
                    return False
            
            # Filtro temporal
            if params['recent_days']:
                cutoff_date = datetime.now() - timedelta(days=params['recent_days'])
                file_date = datetime.fromtimestamp(stat.st_mtime)
                if file_date < cutoff_date:
                    return False
            
            # Filtro por tamaño
            if params.get('size_range'):
                min_size, max_size = params['size_range']
                if min_size and stat.st_size < min_size:
                    return False
                if max_size and stat.st_size > max_size:
                    return False
            
            return True
            
        except (OSError, PermissionError):
            return False
    
    def _matches_filename(self, file_path: Path, keywords: List[str]) -> bool:
        """
        Verificar si el nombre del archivo coincide con las palabras clave
        """
        if not keywords:
            return True
            
        filename_lower = file_path.name.lower()
        return any(keyword in filename_lower for keyword in keywords)
    
    def _search_in_content(self, file_path: Path, keywords: List[str]) -> bool:
        """
        Buscar palabras clave en el contenido del archivo
        """
        if not keywords:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Leer solo los primeros 10KB para evitar archivos muy grandes
                content = f.read(10240).lower()
                return any(keyword in content for keyword in keywords)
        except:
            return False
    
    def _is_text_file(self, file_path: Path) -> bool:
        """
        Verificar si un archivo es de texto (searchable)
        """
        text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md', 
                          '.csv', '.log', '.ini', '.cfg', '.conf', '.yaml', '.yml'}
        return file_path.suffix.lower() in text_extensions
    
    def _get_detailed_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Obtener información detallada de un archivo
        """
        try:
            stat = file_path.stat()
            
            # Determinar categoría
            category = 'otros'
            file_ext = file_path.suffix.lower()
            for cat, extensions in self.file_categories.items():
                if file_ext in extensions:
                    category = cat
                    break
            
            return {
                'path': str(file_path),
                'name': file_path.name,
                'size': stat.st_size,
                'size_human': self._format_file_size(stat.st_size),
                'modified': stat.st_mtime,
                'modified_human': self._format_date(datetime.fromtimestamp(stat.st_mtime)),
                'extension': file_ext,
                'category': category,
                'directory': str(file_path.parent),
                'is_hidden': file_path.name.startswith('.'),
                'mime_type': mimetypes.guess_type(str(file_path))[0]
            }
        except:
            return {
                'path': str(file_path),
                'name': file_path.name,
                'error': 'No se pudo acceder al archivo'
            }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Formatear tamaño de archivo en formato legible
        """
        if size_bytes == 0:
            return '0 B'
        
        size_names = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f'{size:.1f} {size_names[i]}'
    
    def _format_date(self, date_obj: datetime) -> str:
        """
        Formatear fecha en formato legible
        """
        now = datetime.now()
        diff = now - date_obj
        
        if diff.days == 0:
            return 'Hoy'
        elif diff.days == 1:
            return 'Ayer'
        elif diff.days < 7:
            return f'Hace {diff.days} días'
        elif diff.days < 30:
            weeks = diff.days // 7
            return f'Hace {weeks} semana{"s" if weeks > 1 else ""}'
        else:
            return date_obj.strftime('%d/%m/%Y')
    
    def _sort_by_relevance(self, results: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        Ordenar resultados por relevancia
        """
        def relevance_score(file_info):
            score = 0
            filename = file_info['name'].lower()
            
            for keyword in keywords:
                # Más puntos si coincide exactamente
                if keyword == filename.lower():
                    score += 100
                # Puntos si el keyword está al inicio del nombre
                elif filename.startswith(keyword):
                    score += 50
                # Puntos por cada coincidencia en el nombre
                elif keyword in filename:
                    score += 20
                # Puntos extra por coincidencia en contenido
                if file_info.get('content_match'):
                    score += 10
            
            # Puntos por fecha reciente
            days_old = (datetime.now().timestamp() - file_info.get('modified', 0)) / 86400
            if days_old < 1:
                score += 30
            elif days_old < 7:
                score += 20
            elif days_old < 30:
                score += 10
            
            return score
        
        return sorted(results, key=relevance_score, reverse=True)
    
    def _get_search_suggestions(self, query: str, stats: Dict) -> List[str]:
        """
        Generar sugerencias basadas en la búsqueda
        """
        suggestions = []
        
        if stats['total_found'] == 0:
            suggestions.extend([
                "Intenta usar términos más generales",
                "Verifica la ortografía de tu búsqueda",
                "Usa categorías como 'imágenes', 'documentos', 'videos'",
                "Prueba con extensiones específicas como '.txt' o '.jpg'"
            ])
        elif stats['total_found'] > 50:
            suggestions.extend([
                "Usa términos más específicos para filtrar resultados",
                "Añade criterios temporales como 'reciente' o 'este mes'",
                "Especifica el tipo de archivo que buscas"
            ])
        
        if stats['by_type']:
            most_common = max(stats['by_type'], key=stats['by_type'].get)
            suggestions.append(f"Muchos resultados son '{most_common}', especifica si quieres otro tipo")
        
        return suggestions[:3]  # Máximo 3 sugerencias
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Leer contenido de un archivo
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Diccionario con información del archivo y su contenido
        """
        path = Path(file_path)
        
        if not path.exists():
            return {"error": "Archivo no encontrado", "path": file_path}
            
        if not path.is_file():
            return {"error": "La ruta no corresponde a un archivo", "path": file_path}
            
        try:
            # Determinar el tipo de archivo
            mime_type, _ = mimetypes.guess_type(str(path))
            
            # Leer archivos de texto
            if mime_type and mime_type.startswith('text'):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # Para archivos binarios, solo mostrar información
                content = f"[Archivo binario - {mime_type or 'tipo desconocido'}]"
                
            return {
                "path": str(path),
                "name": path.name,
                "size": path.stat().st_size,
                "modified": path.stat().st_mtime,
                "content": content,
                "mime_type": mime_type
            }
            
        except Exception as e:
            return {"error": f"Error al leer archivo: {str(e)}", "path": file_path}
    
    def write_file(self, file_path: str, content: str, backup: bool = True) -> Dict[str, Any]:
        """
        Escribir contenido a un archivo
        
        Args:
            file_path: Ruta del archivo
            content: Contenido a escribir
            backup: Si crear una copia de seguridad
            
        Returns:
            Diccionario con el resultado de la operación
        """
        path = Path(file_path)
        
        try:
            # Crear backup si el archivo existe
            if backup and path.exists():
                backup_path = path.with_suffix(f"{path.suffix}.bak")
                shutil.copy2(path, backup_path)
                
            # Crear directorios padre si no existen
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir el archivo
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return {
                "success": True,
                "path": str(path),
                "message": "Archivo guardado exitosamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al escribir archivo: {str(e)}",
                "path": file_path
            }
    
    def delete_file(self, file_path: str, to_recycle: bool = True) -> Dict[str, Any]:
        """
        Eliminar un archivo
        
        Args:
            file_path: Ruta del archivo
            to_recycle: Si mover a la papelera de reciclaje
            
        Returns:
            Diccionario con el resultado de la operación
        """
        path = Path(file_path)
        
        if not path.exists():
            return {"success": False, "error": "Archivo no encontrado", "path": file_path}
            
        try:
            if to_recycle:
                # En Windows, usar send2trash si está disponible
                try:
                    import send2trash
                    send2trash.send2trash(str(path))
                except ImportError:
                    # Fallback: eliminación permanente
                    path.unlink()
            else:
                path.unlink()
                
            return {
                "success": True,
                "path": str(path),
                "message": "Archivo eliminado exitosamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al eliminar archivo: {str(e)}",
                "path": file_path
            }
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Obtener información básica de un archivo"""
        try:
            stat = file_path.stat()
            return {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "extension": file_path.suffix,
                "parent": str(file_path.parent)
            }
        except Exception as e:
            return {
                "path": str(file_path),
                "name": file_path.name,
                "error": str(e)
            }
    
    def get_recent_files(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Obtener archivos modificados recientemente
        
        Args:
            max_results: Número máximo de resultados
            
        Returns:
            Lista de archivos ordenados por fecha de modificación
        """
        files = []
        
        for search_path in self.search_paths:
            if not search_path.exists():
                continue
                
            try:
                for file_path in search_path.rglob("*"):
                    if not file_path.is_file():
                        continue
                        
                    file_info = self._get_file_info(file_path)
                    if "error" not in file_info:
                        files.append(file_info)
                        
            except (PermissionError, OSError):
                continue
        
        # Ordenar por fecha de modificación (más reciente primero)
        files.sort(key=lambda x: x.get("modified", 0), reverse=True)
        
        return files[:max_results]
    
    def search_files(self, query: str, file_types: Optional[List[str]] = None, 
                    max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Búsqueda simple de archivos (compatibilidad con versión anterior)
        
        Args:
            query: Término de búsqueda
            file_types: Lista de extensiones a buscar (ej: ['.txt', '.py'])
            max_results: Número máximo de resultados
            
        Returns:
            Lista de diccionarios con información de archivos encontrados
        """
        # Usar la búsqueda inteligente pero simplificar el resultado
        kwargs = {
            'max_results': max_results
        }
        
        # Si se especifican tipos de archivo, agregarlos a la consulta
        if file_types:
            type_query = ' '.join(file_types)
            query = f"{query} {type_query}"
        
        smart_result = self.smart_search_files(query, **kwargs)
        
        if smart_result['success']:
            return smart_result['results']
        else:
            return []
    
    def find_recent_files(self, days: int = 7, file_types: Optional[List[str]] = None, 
                         max_results: int = 30) -> Dict[str, Any]:
        """
        Encontrar archivos modificados recientemente
        
        Args:
            days: Archivos modificados en los últimos N días
            file_types: Tipos de archivo a incluir
            max_results: Número máximo de resultados
            
        Returns:
            Diccionario con archivos recientes y estadísticas
        """
        query = f"archivos recientes últimos {days} días"
        
        kwargs = {
            'max_results': max_results,
            'recent_days': days
        }
        
        if file_types:
            kwargs['file_types'] = file_types
        
        return self.smart_search_files(query, **kwargs)
    
    def find_large_files(self, min_size_mb: float = 100, max_results: int = 20) -> Dict[str, Any]:
        """
        Encontrar archivos grandes
        
        Args:
            min_size_mb: Tamaño mínimo en MB
            max_results: Número máximo de resultados
            
        Returns:
            Diccionario con archivos grandes y estadísticas
        """
        min_size_bytes = int(min_size_mb * 1024 * 1024)
        
        return self.smart_search_files(
            f"archivos grandes más de {min_size_mb}MB",
            max_results=max_results,
            min_size=min_size_bytes
        )
    
    def find_by_category(self, category: str, max_results: int = 50) -> Dict[str, Any]:
        """
        Buscar archivos por categoría
        
        Args:
            category: Categoría (documentos, imagenes, videos, etc.)
            max_results: Número máximo de resultados
            
        Returns:
            Diccionario con archivos de la categoría y estadísticas
        """
        return self.smart_search_files(
            f"archivos {category}",
            max_results=max_results
        )
    
    def search_in_content(self, keywords: str, file_types: Optional[List[str]] = None,
                         max_results: int = 30) -> Dict[str, Any]:
        """
        Buscar archivos que contengan ciertas palabras clave en su contenido
        
        Args:
            keywords: Palabras clave a buscar
            file_types: Tipos de archivo donde buscar
            max_results: Número máximo de resultados
            
        Returns:
            Diccionario con archivos que contienen las palabras y estadísticas
        """
        kwargs = {
            'max_results': max_results,
            'include_content': True
        }
        
        if file_types:
            type_query = ' '.join(file_types)
            keywords = f"{keywords} {type_query}"
        
        return self.smart_search_files(keywords, **kwargs)

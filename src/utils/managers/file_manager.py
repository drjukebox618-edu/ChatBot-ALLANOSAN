"""
Gerenciador centralizado de arquivos.
"""
import os
import shutil
import fnmatch
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """Gerenciador centralizado de operações com arquivos."""
    
    def __init__(self):
        self.supported_extensions = {
            'code': ['.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.php', '.cpp', '.c', '.java'],
            'text': ['.txt', '.md', '.rst', '.log'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'],
            'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg'],
            'document': ['.pdf', '.doc', '.docx', '.odt']
        }
        
        self.ignore_patterns = [
            '__pycache__', '*.pyc', '.git', '.gitignore', 'node_modules',
            '.vscode', '.idea', '*.egg-info', 'dist', 'build'
        ]
    
    def scan_directory(self, directory: str, max_files: int = 1000, 
                      max_depth: int = 5, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """Escaneia diretório e retorna informações de arquivos."""
        directory_path = Path(directory)
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Diretório inválido: {directory}")
        
        files_info = []
        extensions_filter = set()
        
        # Preparar filtro de extensões
        if file_types:
            for file_type in file_types:
                if file_type in self.supported_extensions:
                    extensions_filter.update(self.supported_extensions[file_type])
        
        def scan_recursive(path: Path, current_depth: int = 0):
            if current_depth > max_depth or len(files_info) >= max_files:
                return
            
            try:
                for item in path.iterdir():
                    # Verificar se deve ignorar
                    if self._should_ignore(item.name):
                        continue
                    
                    if item.is_file():
                        # Filtrar por extensão se especificado
                        if extensions_filter and item.suffix.lower() not in extensions_filter:
                            continue
                        
                        file_info = self._get_file_info(item)
                        if file_info:
                            files_info.append(file_info)
                    
                    elif item.is_dir():
                        scan_recursive(item, current_depth + 1)
                        
            except (PermissionError, OSError) as e:
                logger.warning(f"Erro ao acessar {path}: {e}")
        
        scan_recursive(directory_path)
        return files_info[:max_files]
    
    def _should_ignore(self, name: str) -> bool:
        """Verifica se arquivo/diretório deve ser ignorado."""
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False
    
    def _get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Obtém informações de um arquivo."""
        try:
            stat = file_path.stat()
            
            return {
                'path': str(file_path),
                'name': file_path.name,
                'extension': file_path.suffix.lower(),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': self._classify_file(file_path.suffix.lower())
            }
        except (OSError, PermissionError) as e:
            logger.warning(f"Erro ao obter info de {file_path}: {e}")
            return None
    
    def _classify_file(self, extension: str) -> str:
        """Classifica arquivo por tipo."""
        for file_type, extensions in self.supported_extensions.items():
            if extension in extensions:
                return file_type
        return 'other'
    
    def copy_files(self, source_files: List[str], destination_dir: str, 
                  preserve_structure: bool = True) -> Dict[str, bool]:
        """Copia arquivos para diretório de destino."""
        dest_path = Path(destination_dir)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for source_file in source_files:
            source_path = Path(source_file)
            if not source_path.exists():
                results[source_file] = False
                continue
            
            try:
                if preserve_structure:
                    # Manter estrutura de diretórios
                    relative_path = source_path.relative_to(source_path.anchor)
                    dest_file = dest_path / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Arquivo direto no destino
                    dest_file = dest_path / source_path.name
                
                shutil.copy2(source_path, dest_file)
                results[source_file] = True
                
            except (OSError, PermissionError) as e:
                logger.error(f"Erro ao copiar {source_file}: {e}")
                results[source_file] = False
        
        return results
    
    def get_directory_stats(self, directory: str) -> Dict[str, Any]:
        """Obtém estatísticas de um diretório."""
        files_info = self.scan_directory(directory)
        
        stats = {
            'total_files': len(files_info),
            'total_size': sum(f['size'] for f in files_info),
            'types_count': {},
            'largest_files': [],
            'newest_files': []
        }
        
        # Contar por tipo
        for file_info in files_info:
            file_type = file_info['type']
            stats['types_count'][file_type] = stats['types_count'].get(file_type, 0) + 1
        
        # Maiores arquivos (top 5)
        files_by_size = sorted(files_info, key=lambda x: x['size'], reverse=True)
        stats['largest_files'] = files_by_size[:5]
        
        # Arquivos mais recentes (top 5)
        files_by_date = sorted(files_info, key=lambda x: x['modified'], reverse=True)
        stats['newest_files'] = files_by_date[:5]
        
        return stats
    
    def cleanup_directory(self, directory: str, patterns: List[str] = None) -> int:
        """Remove arquivos que correspondem aos padrões."""
        patterns = patterns or ['*.tmp', '*.log', '*~', '*.bak']
        removed_count = 0
        
        directory_path = Path(directory)
        if not directory_path.exists():
            return 0
        
        for pattern in patterns:
            for file_path in directory_path.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        removed_count += 1
                        logger.debug(f"Removido: {file_path}")
                except (OSError, PermissionError) as e:
                    logger.warning(f"Erro ao remover {file_path}: {e}")
        
        return removed_count
    
    def find_files(self, directory: str, pattern: str, case_sensitive: bool = False) -> List[str]:
        """Encontra arquivos que correspondem ao padrão."""
        directory_path = Path(directory)
        if not directory_path.exists():
            return []
        
        matches = []
        
        try:
            if case_sensitive:
                for file_path in directory_path.rglob(pattern):
                    if file_path.is_file():
                        matches.append(str(file_path))
            else:
                # Busca case-insensitive usando fnmatch
                for file_path in directory_path.rglob('*'):
                    if file_path.is_file():
                        if fnmatch.fnmatch(file_path.name.lower(), pattern.lower()):
                            matches.append(str(file_path))
        
        except (OSError, PermissionError) as e:
            logger.warning(f"Erro na busca em {directory}: {e}")
        
        return matches

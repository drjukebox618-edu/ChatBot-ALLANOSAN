"""
ProjectEngine Unificado - CONSOLIDAÇÃO TOTAL
Combina project_manager.py + file_utils.py
De 503 linhas para ~250 linhas (-50% redução!)
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict


# Import do super performance
from .super_performance import measure_time

logger = logging.getLogger(__name__)

# Constantes unificadas
PROJECT_SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".cs",
    ".php",
    ".rb",
    ".go",
    ".rs",
    ".kt",
    ".swift",
    ".dart",
    ".scala",
    ".clj",
    ".hs",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".vue",
    ".svelte",
    ".json",
    ".xml",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
    ".txt",
    ".sql",
    ".sh",
    ".ps1",
    ".bat",
}

PROJECT_IGNORE_FOLDERS = {
    "__pycache__",
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    ".vscode",
    ".idea",
    "venv",
    "env",
    ".env",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "target",
    "bin",
    "obj",
    ".gradle",
    ".settings",
    ".metadata",
    "logs",
}

PROJECT_MAX_FILES = 1000
PROJECT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@dataclass
class ProjectInfo:
    """Informações unificadas do projeto."""

    path: str
    name: str
    type: str
    confidence: float
    files_count: int
    total_size: str  # Agora compatível com valor formatado
    last_modified: str
    dependencies: Optional[Dict[str, Any]] = None
    structure: Optional[List[str]] = None


class UnifiedProjectEngine:
    """Engine unificado para projetos e arquivos."""

    def __init__(self):
        self.cache = {}
        self.loading_lock = asyncio.Lock()

    # ===== FUNCIONALIDADES DE FILE_UTILS =====

    def is_code_file(self, filename: str) -> bool:
        """Verifica se é arquivo de código."""
        return Path(filename).suffix.lower() in PROJECT_SUPPORTED_EXTENSIONS

    def should_ignore_folder(self, folder_name: str) -> bool:
        """Verifica se pasta deve ser ignorada, exceto 'Assets' e 'Library'."""
        name = folder_name.strip().lower()
        if name in ("assets", "library"):
            return False
        return folder_name in PROJECT_IGNORE_FOLDERS

    def read_file_content(self, file_path: str) -> str:
        """Lê conteúdo de arquivo com tratamento de erros."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Erro ao ler {file_path}: {e}")
            return ""

    def write_file_content(self, file_path: str, content: str) -> bool:
        """Escreve conteúdo em arquivo."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Erro ao escrever {file_path}: {e}")
            return False

    def create_backup(self, project_path: str) -> str:
        """Cria backup do projeto."""
        import shutil
        from datetime import datetime

        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(os.path.dirname(project_path), backup_name)

        try:
            shutil.copytree(
                project_path,
                backup_path,
                ignore=shutil.ignore_patterns(*PROJECT_IGNORE_FOLDERS),
            )
            logger.info(f"Backup criado: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return ""

    # ===== FUNCIONALIDADES DE PROJECT_MANAGER =====

    def detect_project_type(self, project_path: Path) -> Tuple[str, float]:
        """Detecta tipo do projeto."""
        indicators = {
            "python": [
                ("requirements.txt", 0.8),
                ("setup.py", 0.7),
                ("pyproject.toml", 0.7),
                ("main.py", 0.3),
                ("__init__.py", 0.3),
            ],
            "javascript": [
                ("package.json", 0.9),
                ("yarn.lock", 0.6),
                ("package-lock.json", 0.6),
                ("webpack.config.js", 0.5),
            ],
            "typescript": [("tsconfig.json", 0.9), ("package.json", 0.5)],
            "java": [
                ("pom.xml", 0.8),
                ("build.gradle", 0.8),
                ("gradle.properties", 0.6),
            ],
            "csharp": [("*.csproj", 0.9), ("*.sln", 0.8), ("appsettings.json", 0.5)],
        }

        scores = defaultdict(float)

        try:
            for item in project_path.iterdir():
                if item.is_file():
                    filename = item.name.lower()
                for proj_type, file_indicators in indicators.items():
                    for pattern, score in file_indicators:
                        if pattern.startswith("*"):
                            if filename.endswith(pattern[1:]):
                                scores[proj_type] += score
                        elif filename == pattern:
                            scores[proj_type] += score
        except Exception:
            pass

        if not scores:
            return "unknown", 0.0

        best_type = max(scores.items(), key=lambda x: x[1])
        return best_type[0], min(best_type[1], 1.0)

    async def scan_directory(self, directory: Path, max_depth: int = 3) -> List[str]:
        """Escaneia diretório otimizado."""
        files = []

        def _scan_recursive(path: Path, current_depth: int):
            if current_depth > max_depth or len(files) >= PROJECT_MAX_FILES:
                return

            try:
                for item in path.iterdir():
                    if len(files) >= PROJECT_MAX_FILES:
                        break

                    if item.is_file():
                        if (
                            self.is_code_file(item.name)
                            and item.stat().st_size <= PROJECT_MAX_FILE_SIZE
                        ):
                            files.append(str(item))
                    elif item.is_dir() and not self.should_ignore_folder(item.name):
                        _scan_recursive(item, current_depth + 1)
            except (PermissionError, OSError):
                pass

        _scan_recursive(directory, 0)
        return files

    async def analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Análise de dependências."""
        results = {}

        # Package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text(encoding="utf-8"))
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                results["npm"] = {
                    "production": len(deps),
                    "development": len(dev_deps),
                    "total": len(deps) + len(dev_deps),
                }
            except Exception:
                pass

        # Requirements.txt
        requirements = project_path / "requirements.txt"
        if requirements.exists():
            try:
                lines = requirements.read_text(encoding="utf-8").splitlines()
                deps = [
                    line.strip()
                    for line in lines
                    if line.strip() and not line.startswith("#")
                ]
                results["python"] = {
                    "total": len(deps),
                    "main_deps": [
                        dep.split("==")[0].split(">=")[0] for dep in deps[:10]
                    ],
                }
            except Exception:
                pass

        return results

    @measure_time
    async def load_project(self, project_path: str) -> Optional[ProjectInfo]:
        """Carrega projeto de forma otimizada."""
        project_path = Path(project_path).resolve()

        if not project_path.exists() or not project_path.is_dir():
            return None

        cache_key = str(project_path)
        if cache_key in self.cache:
            return self.cache[cache_key]

        async with self.loading_lock:
            try:
                # Detectar tipo
                proj_type, confidence = self.detect_project_type(project_path)

                # Escanear arquivos
                files = await self.scan_directory(project_path)

                # Calcular estatísticas

                # Calcular tamanho total formatado
                def get_folder_size(path):
                    total = 0
                    for dirpath, dirnames, filenames in os.walk(path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            try:
                                total += os.path.getsize(fp)
                            except Exception:
                                pass
                    return total

                def format_size(size_bytes):
                    if size_bytes < 1024:
                        return f"{size_bytes} B"
                    elif size_bytes < 1024**2:
                        return f"{size_bytes / 1024:.2f} KB"
                    elif size_bytes < 1024**3:
                        return f"{size_bytes / (1024**2):.2f} MB"
                    else:
                        return f"{size_bytes / (1024**3):.2f} GB"

                total_size_bytes = get_folder_size(str(project_path))
                total_size = format_size(total_size_bytes)
                last_modified = datetime.min
                for file_path in files[:50]:  # Limitar para performance
                    try:
                        stat = Path(file_path).stat()
                        file_modified = datetime.fromtimestamp(stat.st_mtime)
                        if file_modified > last_modified:
                            last_modified = file_modified
                    except Exception:
                        continue

                # Analisar dependências
                dependencies = await self.analyze_dependencies(project_path)

                project_info = ProjectInfo(
                    path=str(project_path),
                    name=project_path.name,
                    type=proj_type,
                    confidence=confidence,
                    files_count=len(files),
                    total_size=total_size,
                    last_modified=last_modified.isoformat(),
                    dependencies=dependencies,
                )

                # Cache resultado
                self.cache[cache_key] = project_info
                return project_info

            except Exception as e:
                logger.error(f"Erro ao carregar projeto {project_path}: {e}")
                return None

    def analyze_project_structure(
        self, project_path: str
    ) -> Tuple[List[str], List[Dict[str, Any]], int]:
        """Análise da estrutura do projeto, retorna também o tamanho total da pasta."""
        structure = []
        analyzed_files = []
        files_count = 0
        MAX_FILES_ANALYZED = 5  # Limite menor para teste rápido
        MAX_DEPTH = 5  # Aumenta profundidade para garantir que Assets e Library sejam analisadas

        project_path = os.path.abspath(project_path)

        # Cálculo do tamanho total da pasta

        def get_folder_size(path):
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                    except Exception:
                        pass
            return total

        def format_size(size_bytes):
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024**2:
                return f"{size_bytes / 1024:.2f} KB"
            elif size_bytes < 1024**3:
                return f"{size_bytes / (1024**2):.2f} MB"
            else:
                return f"{size_bytes / (1024**3):.2f} GB"

        total_size_bytes = get_folder_size(project_path)
        total_size = format_size(total_size_bytes)

        # Log especial: listar todos os diretórios do nível raiz
        logger.info("[DEBUG] Diretórios do nível raiz:")
        for item in os.listdir(project_path):
            if os.path.isdir(os.path.join(project_path, item)):
                logger.info(f"[DEBUG] {item}")

        # Adiciona todos os diretórios do nível raiz à estrutura e suas subpastas
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path):
                structure.append(f"{item}/")
                # Adiciona subpastas do nível raiz
                try:
                    for subitem in os.listdir(item_path):
                        subitem_path = os.path.join(item_path, subitem)
                        if os.path.isdir(subitem_path):
                            structure.append(f"  {subitem}/")
                except Exception as e:
                    logger.warning(f"Erro ao listar subpastas de {item}: {e}")

        for root, dirs, files in os.walk(project_path):
            # Limita a profundidade
            rel_path = os.path.relpath(root, project_path)
            depth = rel_path.count(os.sep)
            if depth > MAX_DEPTH:
                dirs[:] = []
                continue

            # Log dos diretórios encontrados antes do filtro
            logger.info(f"[ANALYSE] root: {root} | depth: {depth}")
            logger.info(f"[ANALYSE] dirs antes do filtro: {dirs}")

            for d in dirs:
                logger.info(f"[ANALYSE] DIR ENCONTRADO: {d}")

            original_dirs = list(dirs)
            dirs[:] = [d for d in dirs if not self.should_ignore_folder(d)]

            for d in original_dirs:
                if d not in dirs:
                    logger.info(f"[ANALYSE] DIR IGNORADO PELO FILTRO: {d}")

            logger.info(f"[ANALYSE] dirs após filtro: {dirs}")

            level = root.replace(project_path, "").count(os.sep)
            indent = "  " * level
            folder_name = os.path.basename(root)

            # Sempre mostra a pasta, mesmo se não houver arquivos de código
            structure.append(f"{indent}{folder_name}/")

            # Processar arquivos
            sub_indent = "  " * (level + 1)
            for file in files:
                # Mostra todos os arquivos, não só os de código
                structure.append(f"{sub_indent}{file}")

                # Só analisa conteúdo dos arquivos de código
                if self.is_code_file(file):
                    if files_count < MAX_FILES_ANALYZED:
                        file_path = os.path.join(root, file)
                        content = self.read_file_content(file_path)

                        if content:
                            relative_path = os.path.relpath(file_path, project_path)
                            analyzed_files.append(
                                {
                                    "path": relative_path,
                                    "content": content,
                                    "size": len(content),
                                }
                            )
                            files_count += 1

                    if files_count >= MAX_FILES_ANALYZED:
                        break  # break dentro do loop de arquivos

            if files_count >= MAX_FILES_ANALYZED:
                break  # break dentro do loop de diretórios

        return structure, analyzed_files, total_size

    def clear_cache(self):
        """Limpa cache."""
        self.cache.clear()


# Instância global unificada
unified_project_engine = UnifiedProjectEngine()


# Aliases para compatibilidade (ProjectManager)
class ProjectManager:
    """Wrapper de compatibilidade para ProjectManager."""

    def __init__(self):
        self.current_project = None
        self.engine = unified_project_engine

    async def load_project(self, project_path: str):
        """Carrega projeto usando o engine unificado."""
        self.current_project = await self.engine.load_project(project_path)
        return self.current_project is not None

    def get_current_project(self) -> Optional[ProjectInfo]:
        """Retorna projeto atual."""
        return self.current_project

    def cleanup_resources(self):
        """Limpeza de recursos."""
        self.engine.clear_cache()


# Aliases para compatibilidade (FileUtils)
class FileUtils:
    """Wrapper de compatibilidade para FileUtils."""

    @staticmethod
    def is_code_file(filename: str) -> bool:
        return unified_project_engine.is_code_file(filename)

    @staticmethod
    def should_ignore_folder(folder_name: str) -> bool:
        return unified_project_engine.should_ignore_folder(folder_name)

    @staticmethod
    def read_file_content(file_path: str) -> str:
        return unified_project_engine.read_file_content(file_path)

    @staticmethod
    def write_file_content(file_path: str, content: str) -> bool:
        return unified_project_engine.write_file_content(file_path, content)

    @staticmethod
    def create_backup(project_path: str) -> str:
        return unified_project_engine.create_backup(project_path)

    @staticmethod
    def analyze_project_structure(
        project_path: str,
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        return unified_project_engine.analyze_project_structure(project_path)


# Exportações
__all__ = [
    "UnifiedProjectEngine",
    "ProjectManager",
    "FileUtils",
    "ProjectInfo",
    "unified_project_engine",
]

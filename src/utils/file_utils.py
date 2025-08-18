"""
Wrapper de compatibilidade para file_utils.py
PRESERVA 100% DAS FUNCIONALIDADES ANTIGAS
"""

# Importar engine unificado
from ..core.project_engine import (
    FileUtils,
    unified_project_engine
)

# Para compatibilidade total
from ..core.project_engine import FileUtils

# Exportar tudo
__all__ = ['FileUtils']

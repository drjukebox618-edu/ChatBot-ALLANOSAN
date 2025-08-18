"""
Wrapper de compatibilidade para project_manager.py
PRESERVA 100% DAS FUNCIONALIDADES ANTIGAS
"""

# Importar engine unificado
from .project_engine import (
    UnifiedProjectEngine,
    ProjectManager,
    ProjectInfo,
    unified_project_engine
)

# Para compatibilidade total
from .project_engine import *

# Instâncias para compatibilidade
project_manager = ProjectManager()

# Exportar tudo
__all__ = [
    'ProjectManager', 'ProjectInfo', 'UnifiedProjectEngine',
    'project_manager', 'unified_project_engine'
]

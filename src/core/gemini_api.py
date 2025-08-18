"""
Wrapper de compatibilidade para gemini_api.py
PRESERVA 100% DAS FUNCIONALIDADES ANTIGAS
"""

# Importar API unificada
from .unified_api import (
    UnifiedGeminiAPI as GeminiAPI,
    unified_api
)

# Aliases para compatibilidade total
# GeminiAPI já importado como alias

# Instância global para compatibilidade
gemini_api = unified_api

# Exportar tudo
__all__ = ['GeminiAPI', 'gemini_api']

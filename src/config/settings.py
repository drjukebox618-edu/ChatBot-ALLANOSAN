"""
Wrapper de compatibilidade para settings.py
PRESERVA 100% DAS FUNCIONALIDADES ANTIGAS
"""

# Importar sistema unificado
from .super_config import (
    SuperConfigManager,
    SuperAppConfig,
    SettingsManager,
    AI_MODELS_CONFIG,
    super_config_manager,
    get_settings_manager,
    DEFAULT_AI_MODEL,
    GEMINI_MODEL,
    STREAMING_SETTINGS,
    PROJECT_SUPPORTED_EXTENSIONS,
    PROJECT_IGNORE_FOLDERS
)

# Aliases específicos para compatibilidade
GEMINI_API_KEY = ""  # Será obtido das configurações
GEMINI_MODEL = "gemini-2.5-flash"

# Configurações compatíveis
PROJECT_MAX_FILES = 1000
PROJECT_MAX_FILE_SIZE = 5 * 1024 * 1024

# Para compatibilidade total
from .super_config import *

# Exportar tudo
__all__ = [
    'SuperConfigManager', 'SuperAppConfig', 'SettingsManager',
    'AI_MODELS_CONFIG', 'super_config_manager', 'get_settings_manager',
    'DEFAULT_AI_MODEL', 'GEMINI_MODEL', 'GEMINI_API_KEY',
    'STREAMING_SETTINGS', 'PROJECT_SUPPORTED_EXTENSIONS', 
    'PROJECT_IGNORE_FOLDERS', 'PROJECT_MAX_FILES', 'PROJECT_MAX_FILE_SIZE'
]

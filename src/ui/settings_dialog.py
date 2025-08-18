"""
Janela de configurações funcional para o ChatBot.
CONSOLIDADO: Usando arquitetura modular para reduzir linhas de código.
"""

# Importar o diálogo moderno modular
from .settings.modern_dialog import ModernSettingsDialog

# Alias para compatibilidade com código existente
SettingsDialog = ModernSettingsDialog

# Exportar para uso externo
__all__ = ["SettingsDialog"]

"""
Sistema de exportação e importação consolidado.
CONSOLIDADO: Usando arquitetura modular para reduzir linhas de código.
"""

# Importar exportadores modulares
from .exporters.base_exporters import (
    ExportManager,
    JSONExporter,
    CSVExporter, 
    TXTExporter,
    BaseExporter
)

# Aliases para compatibilidade
def export_conversation_history(conversations, format_type="json", filename=None):
    """Função de compatibilidade para exportação."""
    manager = ExportManager()
    return manager.export_conversations(conversations, format_type, filename)

def import_conversation_history(filename):
    """Função de compatibilidade para importação.""" 
    manager = ExportManager()
    return manager.import_conversations(filename)

# Exportar para uso externo
__all__ = [
    'ExportManager',
    'JSONExporter', 
    'CSVExporter',
    'TXTExporter',
    'BaseExporter',
    'export_conversation_history',
    'import_conversation_history'
]

"""
Wrapper de compatibilidade para performance.py
PRESERVA 100% DAS FUNCIONALIDADES ANTIGAS
"""

# Importar sistema unificado
from .super_performance import (
    SuperPerformanceOptimizer,
    UnifiedCache,
    ThreadManager,
    super_performance,
    cached_function,
    measure_time
)

# Aliases para compatibilidade total
PerformanceOptimizer = SuperPerformanceOptimizer
PerformanceCache = UnifiedCache
performance_optimizer = super_performance

# Instância global (para compatibilidade com código antigo)
performance_optimizer = super_performance

# Exportar tudo para manter compatibilidade
__all__ = [
    'PerformanceOptimizer', 'PerformanceCache', 'ThreadManager',
    'performance_optimizer', 'cached_function', 'measure_time'
]

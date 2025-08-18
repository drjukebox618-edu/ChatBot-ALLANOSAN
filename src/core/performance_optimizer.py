"""
Wrapper de compatibilidade para performance_optimizer.py  
PRESERVA 100% DAS FUNCIONALIDADES ANTIGAS
"""

# Importar sistema unificado
from .super_performance import (
    SuperPerformanceOptimizer as PerformanceOptimizer,
    UnifiedCache as PerformanceCache,
    ThreadManager,
    PerformanceMonitor,
    super_performance,
    cached_function,
    measure_time
)

# Instância global para compatibilidade
performance_optimizer = super_performance

# Exportar tudo
__all__ = [
    'PerformanceOptimizer', 'PerformanceCache', 'ThreadManager', 
    'PerformanceMonitor', 'performance_optimizer', 'cached_function', 'measure_time'
]

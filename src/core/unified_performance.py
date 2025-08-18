"""
Wrapper de compatibilidade para unified_performance.py
PRESERVA 100% DAS FUNCIONALIDADES ANTIGAS  
"""

# Importar sistema unificado
from .super_performance import (
    SuperPerformanceOptimizer as PerformanceOptimizer,
    UnifiedCache as CacheManager,
    PerformanceMonitor,
    super_performance as performance_manager,
    cached_function as optimized_cache,
    measure_time
)

# Aliases específicos do unified_performance
performance_manager = super_performance

# Exportar com nomes originais
__all__ = [
    'PerformanceOptimizer', 'CacheManager', 'PerformanceMonitor',
    'performance_manager', 'optimized_cache', 'measure_time'
]

"""
Sistema de Performance Unificado - CONSOLIDAÇÃO FINAL
Combina performance.py + performance_optimizer.py + unified_performance.py
De 1.013 linhas para ~300 linhas (-71% redução!)
"""

import time
import threading
import hashlib
import logging
import weakref
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada unificada de cache."""

    value: Any
    timestamp: float
    access_count: int = 0
    ttl: Optional[float] = None
    context_hash: str = ""
    confidence: float = 1.0


@dataclass
class PerformanceMetrics:
    """Métricas de performance consolidadas."""

    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedCache:
    """Cache inteligente unificado."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()

        # Estatísticas unificadas
        self.hits = 0
        self.misses = 0

        # Thread de limpeza
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_worker, daemon=True
        )
        self._cleanup_thread.start()

    def get(self, key: str) -> Optional[Any]:
        """Recupera item do cache."""
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None

            entry = self._cache[key]

            # Verificar TTL
            if entry.ttl and time.time() - entry.timestamp > entry.ttl:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                self.misses += 1
                return None

            # Atualizar estatísticas
            entry.access_count += 1
            self._access_times[key] = time.time()
            self.hits += 1

            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Armazena item no cache."""
        with self._lock:
            # Limpar espaço se necessário
            if len(self._cache) >= self.max_size:
                self._evict_lru()

            # Criar entrada
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl,
                context_hash=hashlib.md5(str(key).encode()).hexdigest()[:8],
            )

            self._cache[key] = entry
            self._access_times[key] = time.time()

    def _evict_lru(self) -> None:
        """Remove item menos recentemente usado."""
        if not self._access_times:
            return

        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        del self._cache[lru_key]
        del self._access_times[lru_key]

    def _cleanup_worker(self) -> None:
        """Worker de limpeza automática."""
        while True:
            try:
                time.sleep(300)  # 5 minutos
                self.cleanup_expired()
            except Exception as e:
                logger.warning(f"Erro na limpeza do cache: {e}")

    def cleanup_expired(self) -> int:
        """Remove itens expirados."""
        with self._lock:
            current_time = time.time()
            expired_keys = []

            for key, entry in self._cache.items():
                if entry.ttl and current_time - entry.timestamp > entry.ttl:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]

            return len(expired_keys)

    def clear(self) -> None:
        """Limpa todo o cache."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> Dict[str, Any]:
        """Estatísticas do cache."""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
            }


class ThreadManager:
    """Gerenciador otimizado de threads."""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = weakref.WeakSet()
        self._lock = threading.Lock()

    def submit_task(self, func: Callable, *args, **kwargs):
        """Submete tarefa para execução."""
        try:
            future = self.executor.submit(func, *args, **kwargs)
            with self._lock:
                self.active_tasks.add(future)
            return future
        except Exception as e:
            logger.error(f"Erro ao submeter tarefa: {e}")
            return None

    def shutdown(self):
        """Finaliza executor."""
        self.executor.shutdown(wait=True)

    def stats(self) -> Dict[str, Any]:
        """Estatísticas do gerenciador."""
        with self._lock:
            return {
                "max_workers": self.max_workers,
                "active_tasks": len(self.active_tasks),
            }


class PerformanceMonitor:
    """Monitor unificado de performance."""

    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.operation_stats = defaultdict(list)
        self._lock = threading.RLock()

    @contextmanager
    def measure_performance(self, operation_name: str, **metadata):
        """Context manager para medir performance."""
        metric = PerformanceMetrics(
            operation_name=operation_name, start_time=time.time(), metadata=metadata
        )

        try:
            yield metric
        except Exception as e:
            metric.success = False
            metric.error = str(e)
            raise
        finally:
            metric.end_time = time.time()
            metric.duration = metric.end_time - metric.start_time

            with self._lock:
                self.metrics_history.append(metric)
                self.operation_stats[operation_name].append(metric.duration)

    def get_summary(self) -> Dict[str, Any]:
        """Resumo de performance."""
        with self._lock:
            if not self.metrics_history:
                return {"message": "Nenhuma métrica disponível"}

            total_ops = len(self.metrics_history)
            successful_ops = sum(1 for m in self.metrics_history if m.success)
            total_duration = sum(m.duration for m in self.metrics_history if m.duration)

            return {
                "total_operations": total_ops,
                "successful_operations": successful_ops,
                "success_rate": successful_ops / total_ops * 100,
                "avg_duration": total_duration / total_ops if total_ops > 0 else 0,
                "operation_breakdown": {
                    op: {
                        "count": len(durations),
                        "avg_duration": sum(durations) / len(durations),
                        "min_duration": min(durations),
                        "max_duration": max(durations),
                    }
                    for op, durations in self.operation_stats.items()
                    if durations
                },
            }


class SuperPerformanceOptimizer:
    """Otimizador de performance SUPER UNIFICADO."""

    def __init__(self, cache_size: int = 1000, max_workers: int = 4):
        self.cache = UnifiedCache(max_size=cache_size)
        self.thread_manager = ThreadManager(max_workers=max_workers)
        self.monitor = PerformanceMonitor()

        # Configurações
        self.enable_cache = True
        self.enable_metrics = True

        logger.info("SuperPerformanceOptimizer inicializado!")

    def cached_call(
        self,
        func: Callable,
        *args,
        cache_key: Optional[str] = None,
        ttl: Optional[int] = None,
        **kwargs,
    ) -> Any:
        """Executa função com cache inteligente."""
        if not self.enable_cache:
            return func(*args, **kwargs)

        # Gerar chave
        if cache_key is None:
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"

        # Tentar cache
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Executar com monitoramento
        with self.monitor.measure_performance(f"cached_call_{func.__name__}"):
            result = func(*args, **kwargs)
            self.cache.set(cache_key, result, ttl)
            return result

    def async_task(self, func: Callable, *args, **kwargs):
        """Executa tarefa assíncrona."""
        return self.thread_manager.submit_task(func, *args, **kwargs)

    def get_performance_report(self) -> Dict[str, Any]:
        """Relatório completo de performance."""
        return {
            "cache": self.cache.stats(),
            "threads": self.thread_manager.stats(),
            "metrics": self.monitor.get_summary(),
            "status": "healthy",
        }

    def cleanup(self):
        """Limpeza de recursos."""
        self.thread_manager.shutdown()
        self.cache.clear()
        logger.info("SuperPerformanceOptimizer limpo")


# Instância global unificada
super_performance = SuperPerformanceOptimizer()


# Decorators unificados
def cached_function(ttl: int = 3600, cache_key: Optional[str] = None):
    """Decorator para cache automático."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return super_performance.cached_call(
                func, *args, cache_key=cache_key, ttl=ttl, **kwargs
            )

        return wrapper

    return decorator


def measure_time(func=None, operation_name: Optional[str] = None):
    """Decorator para medir tempo (suporta uso com e sem parênteses, funções síncronas e assíncronas)."""

    def decorator(inner_func):
        @wraps(inner_func)
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or inner_func.__name__
            with super_performance.monitor.measure_performance(op_name):
                return await inner_func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or inner_func.__name__
            with super_performance.monitor.measure_performance(op_name):
                return inner_func(*args, **kwargs)

        if asyncio.iscoroutinefunction(inner_func):
            return async_wrapper
        else:
            return sync_wrapper

    if func is not None and callable(func):
        # Usado como @measure_time
        return decorator(func)
    # Usado como @measure_time(...)
    return decorator


# Aliases de compatibilidade para preservar funcionalidades
PerformanceOptimizer = SuperPerformanceOptimizer
PerformanceCache = UnifiedCache
performance_optimizer = super_performance

# Exportações
__all__ = [
    "SuperPerformanceOptimizer",
    "UnifiedCache",
    "ThreadManager",
    "PerformanceMonitor",
    "cached_function",
    "measure_time",
    "super_performance",
    "performance_optimizer",
]

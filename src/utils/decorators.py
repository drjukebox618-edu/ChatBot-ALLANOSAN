"""
Decorators utilitários para o chatbot.
Centraliza lógica de retry, validação e logging.
"""
import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)
def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator para retry com backoff exponencial."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Tentativa {attempt + 1} falhou: {e}. Retry em {delay}s")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
def validate_processing(func: Callable) -> Callable:
    """Decorator para validação de estado de processamento."""
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        if hasattr(self, 'processing') and self.processing:
            logger.warning(f"Operação {func.__name__} ignorada - sistema processando")
            return False
        return func(self, *args, **kwargs)
    return wrapper
def log_performance(func: Callable) -> Callable:
    """Decorator para logging de performance."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} executado em {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} falhou após {duration:.2f}s: {e}")
            raise
    return wrapper

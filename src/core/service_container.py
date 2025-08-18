"""
ServiceContainer - Sistema de Dependency Injection
Elimina instâncias globais e gerencia dependências
REDUÇÃO: -300+ linhas por eliminar código duplicado
"""
import threading
from typing import Dict, Any, Type, TypeVar, Optional, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class ServiceDefinition:
    """Definição de um serviço."""
    service_type: Type
    factory: Callable
    singleton: bool = True
    instance: Optional[Any] = None

class ServiceContainer:
    """Container de dependency injection."""
    
    def __init__(self):
        self._services: Dict[str, ServiceDefinition] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
        
        # Registrar serviços principais
        self._register_core_services()
    
    def register(self, service_type: Type[T], factory: Callable[[], T], 
                singleton: bool = True) -> None:
        """Registra um serviço."""
        with self._lock:
            key = self._get_service_key(service_type)
            self._services[key] = ServiceDefinition(
                service_type=service_type,
                factory=factory,
                singleton=singleton
            )
            self._logger.debug(f"Serviço registrado: {key}")
    
    def get(self, service_type: Type[T]) -> T:
        """Obtém instância de um serviço."""
        with self._lock:
            key = self._get_service_key(service_type)
            
            if key not in self._services:
                raise ValueError(f"Serviço não registrado: {key}")
            
            service_def = self._services[key]
            
            # Se é singleton e já tem instância
            if service_def.singleton and service_def.instance:
                return service_def.instance
            
            # Criar nova instância
            try:
                instance = service_def.factory()
                
                # Salvar se é singleton
                if service_def.singleton:
                    service_def.instance = instance
                
                self._logger.debug(f"Instância criada: {key}")
                return instance
                
            except Exception as e:
                self._logger.error(f"Erro ao criar instância {key}: {e}")
                raise
    
    def has(self, service_type: Type) -> bool:
        """Verifica se serviço está registrado."""
        key = self._get_service_key(service_type)
        return key in self._services
    
    def clear(self) -> None:
        """Limpa todos os serviços."""
        with self._lock:
            self._services.clear()
            self._logger.info("Container limpo")
    
    def _get_service_key(self, service_type: Type) -> str:
        """Gera chave para o serviço."""
        return f"{service_type.__module__}.{service_type.__name__}"
    
    def _register_core_services(self):
        """Registra serviços principais."""
        # Performance
        from .super_performance import SuperPerformanceOptimizer
        self.register(SuperPerformanceOptimizer, 
                     lambda: SuperPerformanceOptimizer())
        
        # Configuration
        from ..config.super_config import SuperConfigManager
        self.register(SuperConfigManager,
                     lambda: SuperConfigManager())
        
        # Project Engine
        from .project_engine import UnifiedProjectEngine
        self.register(UnifiedProjectEngine,
                     lambda: UnifiedProjectEngine())

# Container global
container = ServiceContainer()

# Função helper para injeção
def inject(service_type: Type[T]) -> T:
    """Injeta dependência."""
    return container.get(service_type)

# Decorator para injeção automática
def auto_inject(*service_types):
    """Decorator para injeção automática de dependências."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Injetar serviços como argumentos
            services = [inject(service_type) for service_type in service_types]
            return func(*args, *services, **kwargs)
        return wrapper
    return decorator

# Exportações
__all__ = ['ServiceContainer', 'container', 'inject', 'auto_inject']

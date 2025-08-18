"""
PluginSystem - Arquitetura de Plugins
Converte módulos grandes em plugins carregáveis
Sistema de hooks e eventos - REDUÇÃO: -400+ linhas
"""
import importlib
import inspect
import logging
from typing import Dict, List, Any, Callable, Optional, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PluginInfo:
    """Informações do plugin."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    enabled: bool = True

class IPlugin(ABC):
    """Interface base para plugins."""
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Retorna informações do plugin."""
        pass
    
    @abstractmethod
    def initialize(self, plugin_manager: 'PluginManager') -> bool:
        """Inicializa o plugin."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Finaliza o plugin."""
        pass

class EventSystem:
    """Sistema de eventos para plugins."""
    
    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {}
        self._filters: Dict[str, List[Callable]] = {}
    
    def add_hook(self, event: str, callback: Callable, priority: int = 10):
        """Adiciona hook para evento."""
        if event not in self._hooks:
            self._hooks[event] = []
        
        self._hooks[event].append((priority, callback))
        self._hooks[event].sort(key=lambda x: x[0])  # Ordenar por prioridade
    
    def trigger_hook(self, event: str, *args, **kwargs):
        """Dispara hooks de um evento."""
        if event in self._hooks:
            for priority, callback in self._hooks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Erro em hook {event}: {e}")
    
    def add_filter(self, filter_name: str, callback: Callable, priority: int = 10):
        """Adiciona filtro."""
        if filter_name not in self._filters:
            self._filters[filter_name] = []
        
        self._filters[filter_name].append((priority, callback))
        self._filters[filter_name].sort(key=lambda x: x[0])
    
    def apply_filter(self, filter_name: str, value: Any, *args, **kwargs) -> Any:
        """Aplica filtros a um valor."""
        if filter_name in self._filters:
            for priority, callback in self._filters[filter_name]:
                try:
                    value = callback(value, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Erro em filtro {filter_name}: {e}")
        
        return value

class PluginManager:
    """Gerenciador de plugins."""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, IPlugin] = {}
        self.events = EventSystem()
        
        # Garantir que diretório existe
        self.plugin_dir.mkdir(exist_ok=True)
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Carrega um plugin específico."""
        try:
            # Importar módulo do plugin
            plugin_path = f"{self.plugin_dir.name}.{plugin_name}"
            module = importlib.import_module(plugin_path)
            
            # Encontrar classe do plugin
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, IPlugin) and 
                    obj != IPlugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.error(f"Classe de plugin não encontrada em {plugin_name}")
                return False
            
            # Instanciar e inicializar
            plugin_instance = plugin_class()
            
            if plugin_instance.initialize(self):
                self.plugins[plugin_name] = plugin_instance
                logger.info(f"Plugin carregado: {plugin_name}")
                
                # Disparar evento
                self.events.trigger_hook('plugin_loaded', plugin_name, plugin_instance)
                return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar plugin {plugin_name}: {e}")
        
        return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Descarrega um plugin."""
        try:
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                plugin.shutdown()
                del self.plugins[plugin_name]
                
                # Disparar evento
                self.events.trigger_hook('plugin_unloaded', plugin_name)
                logger.info(f"Plugin descarregado: {plugin_name}")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao descarregar plugin {plugin_name}: {e}")
        
        return False
    
    def load_all_plugins(self) -> int:
        """Carrega todos os plugins disponíveis."""
        loaded_count = 0
        
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            plugin_name = plugin_file.stem
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        logger.info(f"Carregados {loaded_count} plugins")
        return loaded_count
    
    def get_plugin(self, plugin_name: str) -> Optional[IPlugin]:
        """Obtém instância de um plugin."""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """Lista informações de todos os plugins."""
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def shutdown_all(self):
        """Finaliza todos os plugins."""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)

# Plugins built-in para módulos existentes

class PerformancePlugin(IPlugin):
    """Plugin para sistema de performance."""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="performance",
            version="1.0.0",
            description="Sistema de performance e cache",
            author="ChatBot Team",
            dependencies=[]
        )
    
    def initialize(self, plugin_manager: PluginManager) -> bool:
        try:
            from .super_performance import super_performance
            
            # Registrar hooks
            plugin_manager.events.add_hook('app_startup', self._on_startup)
            plugin_manager.events.add_hook('app_shutdown', self._on_shutdown)
            
            # Registrar filtros
            plugin_manager.events.add_filter('cache_key', self._filter_cache_key)
            
            self.performance = super_performance
            return True
        except Exception as e:
            logger.error(f"Erro ao inicializar PerformancePlugin: {e}")
            return False
    
    def shutdown(self) -> None:
        if hasattr(self, 'performance'):
            self.performance.cleanup()
    
    def _on_startup(self):
        logger.info("Performance system iniciado via plugin")
    
    def _on_shutdown(self):
        logger.info("Performance system finalizado via plugin")
    
    def _filter_cache_key(self, key: str) -> str:
        # Normalizar chave de cache
        return key.lower().strip()

class ProjectPlugin(IPlugin):
    """Plugin para gerenciamento de projetos."""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="project_manager",
            version="1.0.0", 
            description="Gerenciamento de projetos",
            author="ChatBot Team",
            dependencies=["performance"]
        )
    
    def initialize(self, plugin_manager: PluginManager) -> bool:
        try:
            from .project_engine import unified_project_engine
            
            # Registrar hooks
            plugin_manager.events.add_hook('project_loaded', self._on_project_loaded)
            plugin_manager.events.add_filter('project_files', self._filter_project_files)
            
            self.engine = unified_project_engine
            return True
        except Exception as e:
            logger.error(f"Erro ao inicializar ProjectPlugin: {e}")
            return False
    
    def shutdown(self) -> None:
        if hasattr(self, 'engine'):
            self.engine.clear_cache()
    
    def _on_project_loaded(self, project_path: str):
        logger.info(f"Projeto carregado via plugin: {project_path}")
    
    def _filter_project_files(self, files: List[str]) -> List[str]:
        # Filtrar arquivos por extensão
        return [f for f in files if self.engine.is_code_file(f)]

# Plugin manager global
plugin_manager = PluginManager()

# Registrar plugins built-in
plugin_manager.plugins['performance'] = PerformancePlugin()
plugin_manager.plugins['project_manager'] = ProjectPlugin()

# Inicializar plugins built-in
for plugin in plugin_manager.plugins.values():
    plugin.initialize(plugin_manager)

# Decoradores para plugins
def hook(event: str, priority: int = 10):
    """Decorator para registrar hook."""
    def decorator(func):
        plugin_manager.events.add_hook(event, func, priority)
        return func
    return decorator

def filter_hook(filter_name: str, priority: int = 10):
    """Decorator para registrar filtro."""
    def decorator(func):
        plugin_manager.events.add_filter(filter_name, func, priority)
        return func
    return decorator

# Exportações
__all__ = [
    'IPlugin', 'PluginManager', 'EventSystem', 'PluginInfo',
    'plugin_manager', 'hook', 'filter_hook'
]

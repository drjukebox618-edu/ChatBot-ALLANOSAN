"""
SuperConfig - Sistema de Configuração Unificado
Combina settings.py + config_manager.py
De 531 linhas para ~200 linhas (-62% redução!)
"""
import json
import os
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional
from pathlib import Path

# Constantes de configuração
GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_AI_MODEL = "Gemini Pro"

@dataclass
class SuperAppConfig:
    """Configuração super unificada da aplicação."""
    
    # API Configuration
    api_key: str = ""
    model_name: str = GEMINI_MODEL
    temperature: float = 0.7
    max_tokens: int = 8192
    timeout: int = 30
    
    # UI Configuration
    theme: str = "dark"
    font_family: str = "Segoe UI"
    font_size: int = 10
    window_opacity: float = 1.0
    accent_color: str = "#007ACC"
    
    # Chat Configuration
    auto_scroll: bool = True
    message_limit: int = 1000
    save_history: bool = True
    streaming: bool = True
    
    # System Configuration
    cache_enabled: bool = True
    cache_size: int = 1000
    cache_ttl: int = 3600
    max_workers: int = 4
    log_level: str = "INFO"
    
    # Project Configuration
    auto_backup: bool = True
    max_project_size: int = 100 * 1024 * 1024  # 100MB
    ignored_folders: List[str] = field(default_factory=lambda: [
        '__pycache__', '.git', 'node_modules', '.vscode'
    ])
    
    # Performance Configuration
    enable_performance_monitoring: bool = True
    performance_cache_size: int = 500
    thread_pool_size: int = 4

# Modelos de IA disponíveis
AI_MODELS_CONFIG = {
    "Gemini Pro": {
        "api_type": "gemini",
        "model_name": "gemini-2.5-flash",
        "max_tokens": 8192,
        "supports_images": True,
        "supports_streaming": True
    },
    "GPT-4": {
        "api_type": "openai",
        "model_name": "gpt-4",
        "max_tokens": 4096,
        "supports_images": True,
        "supports_streaming": True
    },
    "Claude-3": {
        "api_type": "anthropic",
        "model_name": "claude-3-sonnet",
        "max_tokens": 4096,
        "supports_images": True,
        "supports_streaming": True
    }
}

class SuperConfigManager:
    """Gerenciador super unificado de configurações."""
    
    def __init__(self, config_file: str = "user_settings.json"):
        self.config_file = Path(config_file)
        self.config = SuperAppConfig()
        self.load_config()
    
    def load_config(self) -> SuperAppConfig:
        """Carrega configurações do arquivo."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Atualizar configurações existentes
                for key, value in data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                # Validar configurações
                self._validate_config()
                
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            self.config = SuperAppConfig()  # Usar padrões
        
        return self.config
    
    def save_config(self) -> bool:
        """Salva configurações no arquivo."""
        try:
            # Criar diretório se não existir
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Salvar configurações
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def get_config(self) -> SuperAppConfig:
        """Retorna configuração atual."""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Atualiza configurações."""
        try:
            for key, value in updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            self._validate_config()
            return self.save_config()
            
        except Exception as e:
            print(f"Erro ao atualizar configurações: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reseta para configurações padrão."""
        try:
            self.config = SuperAppConfig()
            return self.save_config()
        except Exception as e:
            print(f"Erro ao resetar configurações: {e}")
            return False
    
    def _validate_config(self):
        """Valida configurações."""
        # Validar temperatura
        if not 0.0 <= self.config.temperature <= 2.0:
            self.config.temperature = 0.7
        
        # Validar max_tokens
        if not 1 <= self.config.max_tokens <= 32768:
            self.config.max_tokens = 8192
        
        # Validar font_size
        if not 8 <= self.config.font_size <= 24:
            self.config.font_size = 10
        
        # Validar opacity
        if not 0.1 <= self.config.window_opacity <= 1.0:
            self.config.window_opacity = 1.0
        
        # Validar cache_size
        if not 100 <= self.config.cache_size <= 10000:
            self.config.cache_size = 1000
    
    def get_ai_model_config(self, model_name: str = None) -> Dict[str, Any]:
        """Retorna configuração do modelo de IA."""
        model_name = model_name or self.config.model_name
        
        # Procurar por nome do modelo
        for name, config in AI_MODELS_CONFIG.items():
            if (config.get('model_name') == model_name or 
                name.lower() == model_name.lower()):
                return {
                    **config,
                    'api_key': self.config.api_key,
                    'temperature': self.config.temperature,
                    'max_tokens': self.config.max_tokens
                }
        
        # Modelo padrão
        return {
            **AI_MODELS_CONFIG[DEFAULT_AI_MODEL],
            'api_key': self.config.api_key,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Retorna configurações de UI."""
        return {
            'theme': self.config.theme,
            'font_family': self.config.font_family,
            'font_size': self.config.font_size,
            'window_opacity': self.config.window_opacity,
            'accent_color': self.config.accent_color
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Retorna configurações de performance."""
        return {
            'cache_enabled': self.config.cache_enabled,
            'cache_size': self.config.cache_size,
            'cache_ttl': self.config.cache_ttl,
            'max_workers': self.config.max_workers,
            'enable_monitoring': self.config.enable_performance_monitoring
        }

# Instância global unificada
super_config_manager = SuperConfigManager()

# Aliases para compatibilidade
class SettingsManager:
    """Wrapper de compatibilidade."""
    
    def __init__(self):
        self.manager = super_config_manager
    
    def load_settings(self):
        return self.manager.load_config()
    
    def save_settings(self, settings):
        return self.manager.update_config(asdict(settings) if hasattr(settings, '__dict__') else settings)
    
    def get_settings(self):
        return self.manager.get_config()

# Função de compatibilidade
def get_settings_manager() -> SettingsManager:
    """Retorna instância do gerenciador."""
    return SettingsManager()

# Configurações de streaming (compatibilidade)
STREAMING_SETTINGS = {
    'chunk_size': 1024,
    'buffer_size': 4096,
    'timeout': 30
}

# Configurações de projeto (compatibilidade)
PROJECT_SUPPORTED_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs'
}

PROJECT_IGNORE_FOLDERS = super_config_manager.config.ignored_folders

# Exportações
__all__ = [
    'SuperConfigManager', 'SuperAppConfig', 'SettingsManager',
    'AI_MODELS_CONFIG', 'super_config_manager', 'get_settings_manager',
    'DEFAULT_AI_MODEL', 'GEMINI_MODEL', 'STREAMING_SETTINGS',
    'PROJECT_SUPPORTED_EXTENSIONS', 'PROJECT_IGNORE_FOLDERS'
]

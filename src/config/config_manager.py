"""
Configurações de API e Interface
ChatBot v3.0 - Sistema Unificado
"""

import os
import json
import logging
from typing import Dict
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """Configuração de API"""

    gemini_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Modelos padrão
    default_gemini_model: str = "gemini-2.5-flash"
    default_gpt_model: str = "gpt-4o"
    default_claude_model: str = "claude-sonnet-4-20250514"

    # Configurações gerais
    default_temperature: float = 0.7
    default_max_tokens: int = 4000
    stream_responses: bool = True


@dataclass
class UIConfig:
    """Configuração da Interface"""

    # Tema
    theme: str = "dark"  # dark, light

    # Janela
    window_width: int = 1200
    window_height: int = 800
    window_maximized: bool = False

    # Funcionalidades
    floating_menu_enabled: bool = True
    history_sidebar_visible: bool = True
    settings_panel_visible: bool = False

    # Cores do tema
    primary_color: str = "#2196F3"
    secondary_color: str = "#FFC107"
    background_color: str = "#1e1e1e"
    text_color: str = "#ffffff"

    # Font
    font_family: str = "Segoe UI"
    font_size: int = 10

    # Chat
    show_timestamps: bool = True
    auto_scroll: bool = True
    word_wrap: bool = True


@dataclass
class ChatConfig:
    """Configuração do Chat"""

    # Histórico
    max_history_items: int = 1000
    save_history: bool = True
    auto_save_interval: int = 30  # segundos

    # Comportamento
    auto_copy_responses: bool = False
    show_typing_indicator: bool = True
    enable_sound_notifications: bool = False

    # Atalhos
    send_message_shortcut: str = "Ctrl+Return"
    new_conversation_shortcut: str = "Ctrl+N"
    clear_chat_shortcut: str = "Ctrl+L"
    toggle_sidebar_shortcut: str = "F9"

    # Sistema
    enable_project_analysis: bool = True
    enable_ocr: bool = True
    max_file_size_mb: int = 10


class ConfigManager:
    """Gerenciador de configurações"""

    def __init__(self):
        self.config_dir = Path("src/config")
        self.config_dir.mkdir(exist_ok=True)

        self.api_config_file = self.config_dir / "api_config.json"
        self.ui_config_file = self.config_dir / "ui_config.json"
        self.chat_config_file = self.config_dir / "chat_config.json"

        # Configurações
        self.api_config = APIConfig()
        self.ui_config = UIConfig()
        self.chat_config = ChatConfig()

        self.load_all_configs()

    def load_all_configs(self):
        """Carrega todas as configurações"""
        self.load_api_config()
        self.load_ui_config()
        self.load_chat_config()
        self._load_environment_variables()

    def load_api_config(self):
        """Carrega configurações de API"""
        try:
            if self.api_config_file.exists():
                with open(self.api_config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Atualiza apenas os campos existentes
                for key, value in data.items():
                    if hasattr(self.api_config, key):
                        setattr(self.api_config, key, value)

                logger.info("Configurações de API carregadas")
            else:
                logger.info(
                    "Arquivo de configuração de API não encontrado, usando padrões"
                )

        except Exception as e:
            logger.error(f"Erro ao carregar configurações de API: {e}")

    def load_ui_config(self):
        """Carrega configurações de UI"""
        try:
            if self.ui_config_file.exists():
                with open(self.ui_config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for key, value in data.items():
                    if hasattr(self.ui_config, key):
                        setattr(self.ui_config, key, value)

                logger.info("Configurações de UI carregadas")
            else:
                logger.info(
                    "Arquivo de configuração de UI não encontrado, usando padrões"
                )

        except Exception as e:
            logger.error(f"Erro ao carregar configurações de UI: {e}")

    def load_chat_config(self):
        """Carrega configurações do chat"""
        try:
            if self.chat_config_file.exists():
                with open(self.chat_config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for key, value in data.items():
                    if hasattr(self.chat_config, key):
                        setattr(self.chat_config, key, value)

                logger.info("Configurações do chat carregadas")
            else:
                logger.info(
                    "Arquivo de configuração do chat não encontrado, usando padrões"
                )

        except Exception as e:
            logger.error(f"Erro ao carregar configurações do chat: {e}")

    def _load_environment_variables(self):
        """Carrega chaves de API das variáveis de ambiente"""
        # Gemini
        if not self.api_config.gemini_api_key:
            self.api_config.gemini_api_key = (
                os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
            )

        # OpenAI
        if not self.api_config.openai_api_key:
            self.api_config.openai_api_key = os.getenv("OPENAI_API_KEY") or ""

        # Anthropic
        if not self.api_config.anthropic_api_key:
            self.api_config.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY") or ""

        if any(
            [
                self.api_config.gemini_api_key,
                self.api_config.openai_api_key,
                self.api_config.anthropic_api_key,
            ]
        ):
            logger.info("Chaves de API carregadas das variáveis de ambiente")

    def save_api_config(self):
        """Salva configurações de API"""
        try:
            data = asdict(self.api_config)
            with open(self.api_config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Configurações de API salvas")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações de API: {e}")

    def save_ui_config(self):
        """Salva configurações de UI"""
        try:
            data = asdict(self.ui_config)
            with open(self.ui_config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Configurações de UI salvas")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações de UI: {e}")

    def save_chat_config(self):
        """Salva configurações do chat"""
        try:
            data = asdict(self.chat_config)
            with open(self.chat_config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Configurações do chat salvas")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações do chat: {e}")

    def save_all_configs(self):
        """Salva todas as configurações"""
        self.save_api_config()
        self.save_ui_config()
        self.save_chat_config()

    def update_api_key(self, provider: str, api_key: str):
        """Atualiza chave de API"""
        provider_map = {
            "gemini": "gemini_api_key",
            "gpt": "openai_api_key",
            "claude": "anthropic_api_key",
        }

        if provider in provider_map:
            setattr(self.api_config, provider_map[provider], api_key)
            self.save_api_config()
            logger.info(f"Chave de API atualizada para {provider}")

    def get_api_key(self, provider: str) -> str:
        """Obtém chave de API"""
        provider_map = {
            "gemini": "gemini_api_key",
            "gpt": "openai_api_key",
            "claude": "anthropic_api_key",
        }

        if provider in provider_map:
            return getattr(self.api_config, provider_map[provider], "")
        return ""

    def has_valid_api_keys(self) -> Dict[str, bool]:
        """Verifica quais chaves de API estão configuradas"""
        return {
            "gemini": bool(self.api_config.gemini_api_key),
            "gpt": bool(self.api_config.openai_api_key),
            "claude": bool(self.api_config.anthropic_api_key),
        }

    def get_theme_colors(self) -> Dict[str, str]:
        """Retorna cores do tema atual"""
        if self.ui_config.theme == "light":
            return {
                "primary": "#1976D2",
                "secondary": "#FF9800",
                "background": "#ffffff",
                "text": "#000000",
                "surface": "#f5f5f5",
                "on_surface": "#424242",
            }
        else:  # dark
            return {
                "primary": "#2196F3",
                "secondary": "#FFC107",
                "background": "#1e1e1e",
                "text": "#ffffff",
                "surface": "#2d2d2d",
                "on_surface": "#e0e0e0",
            }

    def toggle_theme(self):
        """Alterna entre tema claro e escuro"""
        self.ui_config.theme = "light" if self.ui_config.theme == "dark" else "dark"
        self.save_ui_config()
        logger.info(f"Tema alterado para: {self.ui_config.theme}")

    def reset_to_defaults(self, config_type: str = "all"):
        """Restaura configurações padrão"""
        if config_type in ["all", "api"]:
            # Preserve API keys
            keys = {
                "gemini": self.api_config.gemini_api_key,
                "openai": self.api_config.openai_api_key,
                "anthropic": self.api_config.anthropic_api_key,
            }
            self.api_config = APIConfig()
            self.api_config.gemini_api_key = keys["gemini"]
            self.api_config.openai_api_key = keys["openai"]
            self.api_config.anthropic_api_key = keys["anthropic"]

        if config_type in ["all", "ui"]:
            self.ui_config = UIConfig()

        if config_type in ["all", "chat"]:
            self.chat_config = ChatConfig()

        self.save_all_configs()
        logger.info(f"Configurações {config_type} restauradas para padrão")

    def export_config(self, file_path: str):
        """Exporta configurações para arquivo"""
        try:
            export_data = {
                "api_config": asdict(self.api_config),
                "ui_config": asdict(self.ui_config),
                "chat_config": asdict(self.chat_config),
            }

            # Remove chaves de API sensíveis
            export_data["api_config"]["gemini_api_key"] = ""
            export_data["api_config"]["openai_api_key"] = ""
            export_data["api_config"]["anthropic_api_key"] = ""

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Configurações exportadas para: {file_path}")

        except Exception as e:
            logger.error(f"Erro ao exportar configurações: {e}")
            raise

    def import_config(self, file_path: str):
        """Importa configurações de arquivo"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            # Aplica configurações importadas
            if "api_config" in import_data:
                for key, value in import_data["api_config"].items():
                    if hasattr(self.api_config, key) and key not in [
                        "gemini_api_key",
                        "openai_api_key",
                        "anthropic_api_key",
                    ]:
                        setattr(self.api_config, key, value)

            if "ui_config" in import_data:
                for key, value in import_data["ui_config"].items():
                    if hasattr(self.ui_config, key):
                        setattr(self.ui_config, key, value)

            if "chat_config" in import_data:
                for key, value in import_data["chat_config"].items():
                    if hasattr(self.chat_config, key):
                        setattr(self.chat_config, key, value)

            self.save_all_configs()
            logger.info(f"Configurações importadas de: {file_path}")

        except Exception as e:
            logger.error(f"Erro ao importar configurações: {e}")
            raise


# Instância global do gerenciador
config_manager = ConfigManager()

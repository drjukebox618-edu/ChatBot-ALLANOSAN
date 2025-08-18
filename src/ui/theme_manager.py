"""
Gerenciador de temas para o ChatBot.
Sistema modular e otimizado para temas.
"""

from typing import Dict
from dataclasses import dataclass
from PyQt6.QtWidgets import QApplication
@dataclass
class ThemeConfig:
    """Configuração de tema."""
    name: str
    background: str
    text: str
    accent: str
    border: str
    button_bg: str
    button_hover: str
class ThemeManager:
    """Gerenciador central de temas."""
    
    def __init__(self):
        self.themes = self._load_themes()
        self.current_theme = "dark"
        self.callbacks = []
    
    def _load_themes(self) -> Dict[str, ThemeConfig]:
        """Carrega temas predefinidos."""
        return {
            "dark": ThemeConfig(
                name="Escuro",
                background="#1e1e1e",
                text="#d4d4d4",
                accent="#007acc",
                border="#555555",
                button_bg="#0078d4",
                button_hover="#106ebe"
            ),
            "light": ThemeConfig(
                name="Claro",
                background="#ffffff",
                text="#000000",
                accent="#0078d4",
                border="#cccccc",
                button_bg="#0078d4",
                button_hover="#106ebe"
            ),
            "blue": ThemeConfig(
                name="Azul",
                background="#1a1a2e",
                text="#e5e5e5",
                accent="#16213e",
                border="#0f3460",
                button_bg="#e94560",
                button_hover="#c73650"
            )
        }
    
    def set_theme(self, theme_name: str):
        """Define tema atual."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self._notify_theme_change()
    
    def get_current_theme(self) -> ThemeConfig:
        """Retorna tema atual."""
        return self.themes[self.current_theme]
    
    def get_theme_names(self) -> list:
        """Retorna nomes dos temas disponíveis."""
        return list(self.themes.keys())
    
    def register_callback(self, callback):
        """Registra callback para mudança de tema."""
        self.callbacks.append(callback)
    
    def _notify_theme_change(self):
        """Notifica mudança de tema."""
        theme = self.get_current_theme()
        for callback in self.callbacks:
            try:
                callback(theme)
            except Exception as e:
                print(f"Erro em callback de tema: {e}")
    
    def apply_global_theme(self):
        """Aplica tema globalmente à aplicação."""
        theme = self.get_current_theme()
        app = QApplication.instance()
        if app:
            style = f"""
                QMainWindow {{
                    background-color: {theme.background};
                    color: {theme.text};
                }}
                QWidget {{
                    background-color: {theme.background};
                    color: {theme.text};
                }}
                QPushButton {{
                    background-color: {theme.button_bg};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {theme.button_hover};
                }}
                QTextEdit, QLineEdit {{
                    background-color: {theme.background};
                    color: {theme.text};
                    border: 1px solid {theme.border};
                    border-radius: 4px;
                    padding: 4px;
                }}
                QMenuBar {{
                    background-color: {theme.background};
                    color: {theme.text};
                    border-bottom: 1px solid {theme.border};
                }}
                QMenuBar::item:selected {{
                    background-color: {theme.accent};
                }}
                QMenu {{
                    background-color: {theme.background};
                    color: {theme.text};
                    border: 1px solid {theme.border};
                }}
                QMenu::item:selected {{
                    background-color: {theme.accent};
                }}
                QStatusBar {{
                    background-color: {theme.background};
                    color: {theme.text};
                    border-top: 1px solid {theme.border};
                }}
            """
            app.setStyleSheet(style)

"""
Configurações da API.
"""
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import pyqtSignal

from src.config.settings import AI_MODELS_CONFIG, DEFAULT_AI_MODEL


class APISettingsTab(QWidget):
    """Tab de configurações da API."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings: Dict[str, Any]):
        super().__init__()
        self.settings = settings
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface."""
        layout = QVBoxLayout(self)
        
        # Grupo API
        api_group = QGroupBox("Configurações da API")
        api_layout = QGridLayout(api_group)
        
        # API Key
        api_layout.addWidget(QLabel("Chave da API:"), 0, 0)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(self.settings.get("api_key", ""))
        api_layout.addWidget(self.api_key_input, 0, 1)
        
        # Modelo
        api_layout.addWidget(QLabel("Modelo:"), 1, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(list(AI_MODELS_CONFIG.keys()))
        current_model = self.settings.get("model", DEFAULT_AI_MODEL)
        if current_model in AI_MODELS_CONFIG:
            self.model_combo.setCurrentText(current_model)
        api_layout.addWidget(self.model_combo, 1, 1)
        
        # Timeout
        api_layout.addWidget(QLabel("Timeout (s):"), 2, 0)
        self.timeout_input = QLineEdit()
        self.timeout_input.setText(str(self.settings.get("timeout", 30)))
        api_layout.addWidget(self.timeout_input, 2, 1)
        
        layout.addWidget(api_group)
        
        # Conectar sinais
        self.api_key_input.textChanged.connect(self.on_settings_changed)
        self.model_combo.currentTextChanged.connect(self.on_settings_changed)
        self.timeout_input.textChanged.connect(self.on_settings_changed)
    
    def on_settings_changed(self):
        """Emite sinal quando configurações mudam."""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
    
    def get_settings(self) -> Dict[str, Any]:
        """Retorna configurações atuais."""
        return {
            "api_key": self.api_key_input.text(),
            "model": self.model_combo.currentText(),
            "timeout": int(self.timeout_input.text()) if self.timeout_input.text().isdigit() else 30
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Atualiza configurações."""
        self.settings.update(settings)
        self.api_key_input.setText(settings.get("api_key", ""))
        
        model = settings.get("model", DEFAULT_AI_MODEL)
        if model in AI_MODELS_CONFIG:
            self.model_combo.setCurrentText(model)
        
        self.timeout_input.setText(str(settings.get("timeout", 30)))

"""
Configurações de Modelo.
"""
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSlider, 
    QCheckBox, QGroupBox, QGridLayout, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal


class ModelSettingsTab(QWidget):
    """Tab de configurações do modelo."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings: Dict[str, Any]):
        super().__init__()
        self.settings = settings
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface."""
        layout = QVBoxLayout(self)
        
        # Grupo Parâmetros
        params_group = QGroupBox("Parâmetros do Modelo")
        params_layout = QGridLayout(params_group)
        
        # Temperature
        params_layout.addWidget(QLabel("Temperature:"), 0, 0)
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(int(self.settings.get("temperature", 70)))
        params_layout.addWidget(self.temperature_slider, 0, 1)
        
        # Max tokens
        params_layout.addWidget(QLabel("Max Tokens:"), 1, 0)
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 8192)
        self.max_tokens_spin.setValue(self.settings.get("max_tokens", 4096))
        params_layout.addWidget(self.max_tokens_spin, 1, 1)
        
        layout.addWidget(params_group)
        
        # Grupo Streaming
        streaming_group = QGroupBox("Streaming")
        streaming_layout = QGridLayout(streaming_group)
        
        # Habilitar streaming
        self.streaming_enabled = QCheckBox("Habilitar respostas em tempo real")
        self.streaming_enabled.setChecked(self.settings.get("streaming_enabled", True))
        streaming_layout.addWidget(self.streaming_enabled, 0, 0, 1, 2)
        
        layout.addWidget(streaming_group)
        
        # Conectar sinais
        self.temperature_slider.valueChanged.connect(self.on_settings_changed)
        self.max_tokens_spin.valueChanged.connect(self.on_settings_changed)
        self.streaming_enabled.toggled.connect(self.on_settings_changed)
    
    def on_settings_changed(self):
        """Emite sinal quando configurações mudam."""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
    
    def get_settings(self) -> Dict[str, Any]:
        """Retorna configurações atuais."""
        return {
            "temperature": self.temperature_slider.value() / 100.0,
            "max_tokens": self.max_tokens_spin.value(),
            "streaming_enabled": self.streaming_enabled.isChecked()
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Atualiza configurações."""
        self.settings.update(settings)
        self.temperature_slider.setValue(int(settings.get("temperature", 0.7) * 100))
        self.max_tokens_spin.setValue(settings.get("max_tokens", 4096))
        self.streaming_enabled.setChecked(settings.get("streaming_enabled", True))

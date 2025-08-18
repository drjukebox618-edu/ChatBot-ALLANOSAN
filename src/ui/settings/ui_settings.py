"""
Configurações da Interface.
"""
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSlider, QCheckBox, QGroupBox, QGridLayout,
    QPushButton, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class UISettingsTab(QWidget):
    """Tab de configurações da interface."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings: Dict[str, Any]):
        super().__init__()
        self.settings = settings
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface."""
        layout = QVBoxLayout(self)
        
        # Grupo Aparência
        appearance_group = QGroupBox("Aparência")
        appearance_layout = QGridLayout(appearance_group)
        
        # Tema
        appearance_layout.addWidget(QLabel("Tema:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "auto"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "dark"))
        appearance_layout.addWidget(self.theme_combo, 0, 1)
        
        # Opacidade
        appearance_layout.addWidget(QLabel("Opacidade:"), 1, 0)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(int(self.settings.get("opacity", 95)))
        appearance_layout.addWidget(self.opacity_slider, 1, 1)
        
        # Cor de destaque
        appearance_layout.addWidget(QLabel("Cor de destaque:"), 2, 0)
        self.accent_color_btn = QPushButton()
        self.accent_color_btn.setStyleSheet(f"background-color: {self.settings.get('accent_color', '#007acc')}")
        self.accent_color_btn.clicked.connect(self.choose_accent_color)
        appearance_layout.addWidget(self.accent_color_btn, 2, 1)
        
        layout.addWidget(appearance_group)
        
        # Grupo Comportamento
        behavior_group = QGroupBox("Comportamento")
        behavior_layout = QGridLayout(behavior_group)
        
        # Minimizar para bandeja
        self.minimize_to_tray = QCheckBox("Minimizar para bandeja do sistema")
        self.minimize_to_tray.setChecked(self.settings.get("minimize_to_tray", False))
        behavior_layout.addWidget(self.minimize_to_tray, 0, 0, 1, 2)
        
        # Auto-salvar
        self.auto_save = QCheckBox("Salvar automaticamente conversas")
        self.auto_save.setChecked(self.settings.get("auto_save", True))
        behavior_layout.addWidget(self.auto_save, 1, 0, 1, 2)
        
        layout.addWidget(behavior_group)
        
        # Conectar sinais
        self.theme_combo.currentTextChanged.connect(self.on_settings_changed)
        self.opacity_slider.valueChanged.connect(self.on_settings_changed)
        self.minimize_to_tray.toggled.connect(self.on_settings_changed)
        self.auto_save.toggled.connect(self.on_settings_changed)
    
    def choose_accent_color(self):
        """Abre diálogo para escolher cor de destaque."""
        color = QColorDialog.getColor(QColor(self.settings.get("accent_color", "#007acc")), self)
        if color.isValid():
            color_name = color.name()
            self.accent_color_btn.setStyleSheet(f"background-color: {color_name}")
            self.settings["accent_color"] = color_name
            self.on_settings_changed()
    
    def on_settings_changed(self):
        """Emite sinal quando configurações mudam."""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
    
    def get_settings(self) -> Dict[str, Any]:
        """Retorna configurações atuais."""
        return {
            "theme": self.theme_combo.currentText(),
            "opacity": self.opacity_slider.value(),
            "accent_color": self.settings.get("accent_color", "#007acc"),
            "minimize_to_tray": self.minimize_to_tray.isChecked(),
            "auto_save": self.auto_save.isChecked()
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Atualiza configurações."""
        self.settings.update(settings)
        self.theme_combo.setCurrentText(settings.get("theme", "dark"))
        self.opacity_slider.setValue(settings.get("opacity", 95))
        self.minimize_to_tray.setChecked(settings.get("minimize_to_tray", False))
        self.auto_save.setChecked(settings.get("auto_save", True))

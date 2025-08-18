"""
Diálogo de configurações modular.
"""
import os
import json
from typing import Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from .api_settings import APISettingsTab
from .ui_settings import UISettingsTab  
from .model_settings import ModelSettingsTab

import logging
logger = logging.getLogger(__name__)


class ModernSettingsDialog(QDialog):
    """Diálogo de configurações modular."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = self.load_settings()
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Configura a interface."""
        self.setWindowTitle("Configurações")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Tabs
        self.tab_widget = QTabWidget()
        
        # Criar tabs
        self.api_tab = APISettingsTab(self.settings)
        self.ui_tab = UISettingsTab(self.settings)
        self.model_tab = ModelSettingsTab(self.settings)
        
        # Adicionar tabs
        self.tab_widget.addTab(self.api_tab, "API")
        self.tab_widget.addTab(self.ui_tab, "Interface")
        self.tab_widget.addTab(self.model_tab, "Modelo")
        
        layout.addWidget(self.tab_widget)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Aplicar")
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancelar")
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def setup_connections(self):
        """Configura conexões de sinais."""
        # Conectar tabs
        self.api_tab.settings_changed.connect(self.on_tab_settings_changed)
        self.ui_tab.settings_changed.connect(self.on_tab_settings_changed)
        self.model_tab.settings_changed.connect(self.on_tab_settings_changed)
        
        # Conectar botões
        self.apply_btn.clicked.connect(self.apply_settings)
        self.ok_btn.clicked.connect(self.ok_clicked)
        self.cancel_btn.clicked.connect(self.reject)
    
    def on_tab_settings_changed(self, tab_settings: Dict[str, Any]):
        """Atualiza configurações quando uma tab muda."""
        self.settings.update(tab_settings)
    
    def apply_settings(self):
        """Aplica configurações."""
        try:
            # Coletar todas as configurações
            all_settings = {}
            all_settings.update(self.api_tab.get_settings())
            all_settings.update(self.ui_tab.get_settings())
            all_settings.update(self.model_tab.get_settings())
            
            # Salvar
            self.save_settings(all_settings)
            
            # Emitir sinal
            self.settings_changed.emit(all_settings)
            
            QMessageBox.information(self, "Sucesso", "Configurações aplicadas com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar configurações: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar configurações: {str(e)}")
    
    def ok_clicked(self):
        """OK clicado."""
        self.apply_settings()
        self.accept()
    
    def load_settings(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo."""
        try:
            if os.path.exists("src/user_settings.json"):
                with open("src/user_settings.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar configurações: {e}")
        
        # Configurações padrão
        return {
            "api_key": "",
            "model": "gemini-2.0-flash-exp",
            "timeout": 30,
            "theme": "dark",
            "opacity": 95,
            "accent_color": "#007acc",
            "minimize_to_tray": False,
            "auto_save": True,
            "temperature": 0.7,
            "max_tokens": 4096,
            "streaming_enabled": True
        }
    
    def save_settings(self, settings: Dict[str, Any]):
        """Salva configurações no arquivo."""
        try:
            os.makedirs("src", exist_ok=True)
            with open("src/user_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            raise

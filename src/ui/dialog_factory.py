"""
Factory para criação de diálogos unificados.
"""
from typing import Dict, Any, Optional, Type
from PyQt6.QtWidgets import QDialog, QWidget
from abc import ABC, abstractmethod

from src.ui.settings.modern_dialog import ModernSettingsDialog


class DialogFactory:
    """Factory para criação de diálogos."""
    
    _dialogs = {
        'settings': ModernSettingsDialog,
    }
    
    @classmethod
    def create_dialog(cls, dialog_type: str, parent: Optional[QWidget] = None, **kwargs) -> QDialog:
        """Cria diálogo do tipo especificado."""
        if dialog_type not in cls._dialogs:
            raise ValueError(f"Tipo de diálogo '{dialog_type}' não suportado")
        
        dialog_class = cls._dialogs[dialog_type]
        return dialog_class(parent, **kwargs)
    
    @classmethod
    def register_dialog(cls, dialog_type: str, dialog_class: Type[QDialog]):
        """Registra novo tipo de diálogo."""
        cls._dialogs[dialog_type] = dialog_class
    
    @classmethod
    def get_available_dialogs(cls) -> list:
        """Retorna tipos de diálogos disponíveis."""
        return list(cls._dialogs.keys())


class BaseDialog(QDialog, ABC):
    """Classe base para diálogos padronizados."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_base_ui()
        self.setup_dialog_ui()
        self.setup_connections()
    
    def setup_base_ui(self):
        """Configuração base da UI."""
        self.setModal(True)
        self.setFixedSize(600, 400)
    
    @abstractmethod
    def setup_dialog_ui(self):
        """Configuração específica da UI do diálogo."""
        pass
    
    @abstractmethod
    def setup_connections(self):
        """Configuração de conexões de sinais."""
        pass


class FormComponent(QWidget):
    """Componente reutilizável de formulário."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.fields = {}
        self.validators = {}
    
    def add_field(self, name: str, widget: QWidget, validator=None):
        """Adiciona campo ao formulário."""
        self.fields[name] = widget
        if validator:
            self.validators[name] = validator
    
    def get_values(self) -> Dict[str, Any]:
        """Retorna valores dos campos."""
        values = {}
        for name, widget in self.fields.items():
            if hasattr(widget, 'text'):
                values[name] = widget.text()
            elif hasattr(widget, 'isChecked'):
                values[name] = widget.isChecked()
            elif hasattr(widget, 'currentText'):
                values[name] = widget.currentText()
            elif hasattr(widget, 'value'):
                values[name] = widget.value()
        return values
    
    def set_values(self, values: Dict[str, Any]):
        """Define valores dos campos."""
        for name, value in values.items():
            if name in self.fields:
                widget = self.fields[name]
                if hasattr(widget, 'setText'):
                    widget.setText(str(value))
                elif hasattr(widget, 'setChecked'):
                    widget.setChecked(bool(value))
                elif hasattr(widget, 'setCurrentText'):
                    widget.setCurrentText(str(value))
                elif hasattr(widget, 'setValue'):
                    widget.setValue(value)
    
    def validate(self) -> tuple[bool, str]:
        """Valida campos do formulário."""
        for name, validator in self.validators.items():
            if name in self.fields:
                widget = self.fields[name]
                value = None
                
                if hasattr(widget, 'text'):
                    value = widget.text()
                elif hasattr(widget, 'isChecked'):
                    value = widget.isChecked()
                elif hasattr(widget, 'value'):
                    value = widget.value()
                
                if value is not None:
                    is_valid, error_msg = validator(value)
                    if not is_valid:
                        return False, f"Campo '{name}': {error_msg}"
        
        return True, ""

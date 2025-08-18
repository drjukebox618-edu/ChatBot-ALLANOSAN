"""
Gerenciador de menus para o ChatBot.
Sistema modular para criação e gerenciamento de menus.
"""

from typing import Callable
from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import pyqtSignal, QObject
class MenuManager(QObject):
    """Gerenciador centralizado de menus."""
    
    # Signals para ações do menu
    new_conversation = pyqtSignal()
    load_project = pyqtSignal()
    load_image = pyqtSignal()
    export_conversation = pyqtSignal()
    open_settings = pyqtSignal()
    show_about = pyqtSignal()
    clear_chat = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.menu_bar = None
        self.actions = {}
    
    def create_menu_bar(self) -> QMenuBar:
        """Cria barra de menu otimizada."""
        self.menu_bar = QMenuBar(self.parent)
        
        # Menu Arquivo
        self._create_file_menu()
        
        # Menu Projeto
        self._create_project_menu()
        
        # Menu Ferramentas
        self._create_tools_menu()
        
        # Menu Ajuda
        self._create_help_menu()
        
        return self.menu_bar
    
    def _create_file_menu(self):
        """Cria menu Arquivo."""
        file_menu = self.menu_bar.addMenu("📁 Arquivo")
        
        # Nova Conversa
        self._add_action(
            file_menu, "Nova Conversa", "Ctrl+N",
            self.new_conversation.emit
        )
        
        file_menu.addSeparator()
        
        # Exportar
        self._add_action(
            file_menu, "Exportar Conversa", "Ctrl+E",
            self.export_conversation.emit
        )
        
        file_menu.addSeparator()
        
        # Limpar Chat
        self._add_action(
            file_menu, "Limpar Chat", "Ctrl+L",
            self.clear_chat.emit
        )
    
    def _create_project_menu(self):
        """Cria menu Projeto."""
        project_menu = self.menu_bar.addMenu("📁 Projeto")
        
        # Carregar Projeto
        self._add_action(
            project_menu, "Carregar Pasta", "Ctrl+O",
            self.load_project.emit
        )
        
        project_menu.addSeparator()
        
        # Carregar Imagem
        self._add_action(
            project_menu, "Carregar Imagem", "Ctrl+I",
            self.load_image.emit
        )
    
    def _create_tools_menu(self):
        """Cria menu Ferramentas."""
        tools_menu = self.menu_bar.addMenu("🔧 Ferramentas")
        
        # Configurações
        self._add_action(
            tools_menu, "Configurações", "Ctrl+,",
            self.open_settings.emit
        )
    
    def _create_help_menu(self):
        """Cria menu Ajuda."""
        help_menu = self.menu_bar.addMenu("❓ Ajuda")
        
        # Sobre
        self._add_action(
            help_menu, "Sobre", None,
            self.show_about.emit
        )
    
    def _add_action(self, menu: QMenu, text: str, shortcut: str, callback: Callable):
        """Adiciona ação ao menu."""
        action = QAction(text, self.parent)
        
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        
        action.triggered.connect(callback)
        menu.addAction(action)
        
        # Armazenar referência
        self.actions[text] = action
        
        return action
    
    def enable_action(self, text: str, enabled: bool = True):
        """Habilita/desabilita ação."""
        if text in self.actions:
            self.actions[text].setEnabled(enabled)
    
    def set_action_text(self, text: str, new_text: str):
        """Altera texto da ação."""
        if text in self.actions:
            self.actions[text].setText(new_text)

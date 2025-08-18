"""
Componentes UI reutilizáveis para o ChatBot.
Widgets especializados e modulares.
"""

from typing import List
from PyQt6.QtWidgets import (
    QTextEdit, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent

import logging
logger = logging.getLogger(__name__)
class ChatDisplay(QTextEdit):
    """Widget otimizado para exibição do chat com drag & drop."""
    
    files_dropped = pyqtSignal(list)  # Signal para arquivos dropados
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._setup_widget()
    
    def _setup_widget(self):
        """Configura widget inicialmente."""
        self.setReadOnly(True)
        self.setAcceptDrops(True)
        self.setHtml("")  # Força modo HTML
        
        # Fonte otimizada
        font = QFont("Consolas", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        
        self.update_theme_style()
    
    def update_theme_style(self, theme: str = "dark"):
        """Atualiza estilo baseado no tema."""
        styles = {
            "dark": """
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 10px;
                }
            """,
            "light": """
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 10px;
                }
            """
        }
        self.setStyleSheet(styles.get(theme, styles["dark"]))
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Evento drag enter otimizado."""
        if event.mimeData().hasUrls():
            event.accept()
            self.setStyleSheet("""
                QTextEdit {
                    background-color: #2a2a2a;
                    border: 2px dashed #007acc;
                    border-radius: 5px;
                }
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Evento drag leave."""
        self.update_theme_style()

    def dropEvent(self, event: QDropEvent):
        """Evento drop otimizado."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.files_dropped.emit(files)
        self.update_theme_style()
        event.accept()
class ConversationsList(QListWidget):
    """Lista otimizada de conversas."""
    
    conversation_selected = pyqtSignal(str)  # Signal com ID da conversa
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_widget()
    
    def _setup_widget(self):
        """Configura lista."""
        self.setMaximumWidth(250)
        self.setMinimumWidth(200)
        self.update_theme_style()
    
    def update_theme_style(self, theme: str = "dark"):
        """Atualiza estilo da lista."""
        styles = {
            "dark": """
                QListWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 5px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #444444;
                }
                QListWidget::item:selected {
                    background-color: #007acc;
                }
            """,
            "light": """
                QListWidget {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #eeeeee;
                }
                QListWidget::item:selected {
                    background-color: #0078d4;
                }
            """
        }
        self.setStyleSheet(styles.get(theme, styles["dark"]))
    
    def load_conversations(self, conversations: List[dict]):
        """Carrega lista de conversas de forma otimizada."""
        self.clear()
        for conv in conversations:
            item = QListWidgetItem(conv.get('title', 'Conversa sem título'))
            item.setData(Qt.ItemDataRole.UserRole, conv.get('id'))
            self.addItem(item)
    
    def mousePressEvent(self, event):
        """Evento de clique otimizado."""
        super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            conv_id = item.data(Qt.ItemDataRole.UserRole)
            if conv_id:
                self.conversation_selected.emit(conv_id)
class ControlPanel(QWidget):
    """Painel de controles otimizado."""
    
    message_send = pyqtSignal(str)  # Signal para enviar mensagem
    new_conversation = pyqtSignal()  # Signal para nova conversa
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface do painel."""
        layout = QVBoxLayout(self)
        
        # Input de mensagem
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("Digite sua mensagem...")
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self._send_message)
        
        self.new_button = QPushButton("Nova Conversa")
        self.new_button.clicked.connect(self.new_conversation.emit)
        
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.new_button)
        button_layout.addStretch()
        
        layout.addWidget(self.message_input)
        layout.addLayout(button_layout)
        
        self.update_theme_style()
    
    def _send_message(self):
        """Envia mensagem."""
        text = self.message_input.toPlainText().strip()
        if text:
            self.message_send.emit(text)
            self.message_input.clear()
    
    def update_theme_style(self, theme: str = "dark"):
        """Atualiza estilo do painel."""
        styles = {
            "dark": """
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    border-radius: 5px;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """,
            "light": """
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """
        }
        self.setStyleSheet(styles.get(theme, styles["dark"]))
class StatusBar(QWidget):
    """Barra de status otimizada."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura barra de status."""
        layout = QHBoxLayout(self)
        
        self.status_label = QLabel("Pronto")
        self.project_label = QLabel("Nenhum projeto")
        self.model_label = QLabel("Gemini Pro")
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.project_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.model_label)
        
        self.update_theme_style()
    
    def update_status(self, status: str):
        """Atualiza status."""
        self.status_label.setText(status)
    
    def update_project(self, project: str):
        """Atualiza projeto."""
        self.project_label.setText(f"Projeto: {project}")
    
    def update_model(self, model: str):
        """Atualiza modelo."""
        self.model_label.setText(f"Modelo: {model}")
    
    def update_theme_style(self, theme: str = "dark"):
        """Atualiza estilo."""
        styles = {
            "dark": """
                QLabel {
                    color: #d4d4d4;
                    padding: 4px;
                }
            """,
            "light": """
                QLabel {
                    color: #000000;
                    padding: 4px;
                }
            """
        }
        self.setStyleSheet(styles.get(theme, styles["dark"]))

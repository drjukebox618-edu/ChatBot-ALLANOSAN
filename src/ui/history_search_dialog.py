"""
Diálogo de Busca no Histórico - ChatBot v3.0
Interface para buscar conversas anteriores
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QTextEdit,
    QSplitter,
    QGroupBox,
    QCheckBox,
    QDateEdit,
    QComboBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
import logging
import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


class HistorySearchDialog(QDialog):
    """Diálogo para busca no histórico"""

    conversation_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Buscar no Histórico - ChatBot v3.0")
        self.setMinimumSize(800, 600)
        self.setModal(True)

        # Dados fictícios para demonstração
        self.conversations = self.generate_sample_conversations()
        self.filtered_conversations = self.conversations.copy()

        self.setup_ui()
        self.setup_connections()
        self.populate_results()

    def setup_ui(self):
        """Configura interface"""
        layout = QVBoxLayout(self)

        # Área de busca
        search_group = QGroupBox("🔍 Critérios de Busca")
        search_layout = QVBoxLayout(search_group)

        # Linha 1: Busca por texto
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Texto:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite palavras-chave para buscar...")
        text_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("🔍 Buscar")
        text_layout.addWidget(self.search_btn)

        search_layout.addLayout(text_layout)

        # Linha 2: Filtros
        filters_layout = QHBoxLayout()

        # Filtro por data
        filters_layout.addWidget(QLabel("De:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        filters_layout.addWidget(self.date_from)

        filters_layout.addWidget(QLabel("Até:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filters_layout.addWidget(self.date_to)

        # Filtro por IA
        filters_layout.addWidget(QLabel("IA:"))
        self.ai_filter = QComboBox()
        self.ai_filter.addItems(["Todas", "Gemini", "GPT-4", "Claude"])
        filters_layout.addWidget(self.ai_filter)

        # Opções de busca
        self.case_sensitive = QCheckBox("Maiúsculas/minúsculas")
        self.whole_words = QCheckBox("Palavras inteiras")
        filters_layout.addWidget(self.case_sensitive)
        filters_layout.addWidget(self.whole_words)

        filters_layout.addStretch()

        search_layout.addLayout(filters_layout)
        layout.addWidget(search_group)

        # Splitter para resultados
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Lista de conversas
        left_panel = QGroupBox("📋 Conversas Encontradas")
        left_layout = QVBoxLayout(left_panel)

        self.results_label = QLabel("0 conversas encontradas")
        left_layout.addWidget(self.results_label)

        self.conversations_list = QListWidget()
        self.conversations_list.itemSelectionChanged.connect(
            self.on_conversation_selected
        )
        left_layout.addWidget(self.conversations_list)

        splitter.addWidget(left_panel)

        # Preview da conversa
        right_panel = QGroupBox("👁️ Preview da Conversa")
        right_layout = QVBoxLayout(right_panel)

        self.preview_info = QLabel("Selecione uma conversa para ver o preview")
        self.preview_info.setWordWrap(True)
        right_layout.addWidget(self.preview_info)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 9))
        right_layout.addWidget(self.preview_text)

        splitter.addWidget(right_panel)

        # Configurar proporções
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)

        # Botões
        buttons_layout = QHBoxLayout()

        clear_btn = QPushButton("🗑️ Limpar Busca")
        clear_btn.clicked.connect(self.clear_search)

        export_btn = QPushButton("💾 Exportar Resultados")
        export_btn.clicked.connect(self.export_results)

        load_btn = QPushButton("📂 Carregar Conversa")
        load_btn.clicked.connect(self.load_selected_conversation)

        close_btn = QPushButton("❌ Fechar")
        close_btn.clicked.connect(self.accept)

        buttons_layout.addWidget(clear_btn)
        buttons_layout.addWidget(export_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(load_btn)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        self.apply_style()

    def setup_connections(self):
        """Configura conexões"""
        self.search_btn.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)
        self.ai_filter.currentTextChanged.connect(self.perform_search)
        self.date_from.dateChanged.connect(self.perform_search)
        self.date_to.dateChanged.connect(self.perform_search)
        self.case_sensitive.toggled.connect(self.perform_search)
        self.whole_words.toggled.connect(self.perform_search)

    def generate_sample_conversations(self) -> List[Dict]:
        """Gera conversas de exemplo"""
        # Dados de exemplo
        sample_data = [
            {
                "id": 1,
                "title": "Ajuda com Python",
                "date": "2024-01-15",
                "time": "14:30",
                "ai": "Gemini",
                "messages": [
                    {"user": True, "content": "Como posso melhorar meu código Python?"},
                    {
                        "user": False,
                        "content": "Aqui estão algumas dicas para melhorar seu código Python: Use PEP 8, docstrings, type hints...",
                    },
                ],
            },
            {
                "id": 2,
                "title": "Análise de Projeto React",
                "date": "2024-01-14",
                "time": "09:15",
                "ai": "GPT-4",
                "messages": [
                    {"user": True, "content": "Preciso analisar meu projeto React"},
                    {
                        "user": False,
                        "content": "Vou analisar seu projeto React. Primeiro, me conte sobre a estrutura...",
                    },
                ],
            },
            {
                "id": 3,
                "title": "Debugging JavaScript",
                "date": "2024-01-13",
                "time": "16:45",
                "ai": "Claude",
                "messages": [
                    {"user": True, "content": "Estou com um bug no meu JavaScript"},
                    {
                        "user": False,
                        "content": "Vamos resolver esse bug. Pode me mostrar o código problemático?",
                    },
                ],
            },
            {
                "id": 4,
                "title": "Machine Learning com Python",
                "date": "2024-01-12",
                "time": "11:20",
                "ai": "Gemini",
                "messages": [
                    {"user": True, "content": "Como começar com machine learning?"},
                    {
                        "user": False,
                        "content": "Machine Learning é um campo fascinante! Vou te guiar pelos primeiros passos...",
                    },
                ],
            },
            {
                "id": 5,
                "title": "Docker e Containers",
                "date": "2024-01-11",
                "time": "13:50",
                "ai": "GPT-4",
                "messages": [
                    {"user": True, "content": "Explique Docker para iniciantes"},
                    {
                        "user": False,
                        "content": "Docker é uma tecnologia de containerização. Imagine containers como caixas...",
                    },
                ],
            },
        ]

        return sample_data

    def perform_search(self):
        """Executa busca"""
        search_text = self.search_input.text().lower()
        ai_filter = self.ai_filter.currentText()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        case_sensitive = self.case_sensitive.isChecked()
        whole_words = self.whole_words.isChecked()

        self.filtered_conversations = []

        for conv in self.conversations:
            # Filtro por data
            conv_date = datetime.datetime.strptime(conv["date"], "%Y-%m-%d").date()
            if not (date_from <= conv_date <= date_to):
                continue

            # Filtro por IA
            if ai_filter != "Todas" and conv["ai"] != ai_filter:
                continue

            # Filtro por texto
            if search_text:
                text_to_search = conv["title"]
                for msg in conv["messages"]:
                    text_to_search += " " + msg["content"]

                if not case_sensitive:
                    text_to_search = text_to_search.lower()

                # Busca simples (pode ser melhorada)
                if whole_words:
                    import re

                    pattern = r"\b" + re.escape(search_text) + r"\b"
                    if not re.search(
                        pattern,
                        text_to_search,
                        re.IGNORECASE if not case_sensitive else 0,
                    ):
                        continue
                else:
                    if search_text not in text_to_search:
                        continue

            self.filtered_conversations.append(conv)

        self.populate_results()

    def populate_results(self):
        """Popula lista de resultados"""
        self.conversations_list.clear()

        for conv in self.filtered_conversations:
            item_text = (
                f"🗓️ {conv['date']} {conv['time']} - {conv['ai']}: {conv['title']}"
            )
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, conv)
            self.conversations_list.addItem(item)

        count = len(self.filtered_conversations)
        self.results_label.setText(
            f"{count} conversa{'s' if count != 1 else ''} encontrada{'s' if count != 1 else ''}"
        )

    def on_conversation_selected(self):
        """Evento de seleção de conversa"""
        current_item = self.conversations_list.currentItem()
        if not current_item:
            return

        conv = current_item.data(Qt.ItemDataRole.UserRole)

        # Atualizar info
        info = f"""
<b>Título:</b> {conv["title"]}<br>
<b>Data:</b> {conv["date"]} às {conv["time"]}<br>
<b>IA Utilizada:</b> {conv["ai"]}<br>
<b>Número de mensagens:</b> {len(conv["messages"])}<br>
"""
        self.preview_info.setText(info)

        # Atualizar preview
        preview_text = ""
        for i, msg in enumerate(conv["messages"]):
            sender = "👤 USUÁRIO" if msg["user"] else f"🤖 {conv['ai'].upper()}"
            preview_text += f"{sender}:\n{msg['content']}\n\n"

            # Limitar preview
            if i >= 4:  # Primeiras 5 mensagens
                preview_text += "... (conversa continua)\n"
                break

        self.preview_text.setText(preview_text)

    def clear_search(self):
        """Limpa busca"""
        self.search_input.clear()
        self.ai_filter.setCurrentText("Todas")
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.case_sensitive.setChecked(False)
        self.whole_words.setChecked(False)

        self.filtered_conversations = self.conversations.copy()
        self.populate_results()

        self.preview_info.setText("Selecione uma conversa para ver o preview")
        self.preview_text.clear()

    def export_results(self):
        """Exporta resultados"""
        if not self.filtered_conversations:
            QMessageBox.information(self, "Exportar", "Nenhum resultado para exportar!")
            return

        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Resultados da Busca",
            f"busca_historico_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Arquivos de Texto (*.txt)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("RESULTADOS DA BUSCA NO HISTÓRICO\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(
                        f"Busca realizada em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                    )
                    f.write(f"Termo buscado: {self.search_input.text()}\n")
                    f.write(
                        f"Resultados encontrados: {len(self.filtered_conversations)}\n\n"
                    )

                    for conv in self.filtered_conversations:
                        f.write(f"CONVERSA: {conv['title']}\n")
                        f.write(f"Data: {conv['date']} {conv['time']}\n")
                        f.write(f"IA: {conv['ai']}\n")
                        f.write("-" * 30 + "\n")

                        for msg in conv["messages"]:
                            sender = "USUÁRIO" if msg["user"] else conv["ai"]
                            f.write(f"{sender}: {msg['content']}\n\n")

                        f.write("=" * 50 + "\n\n")

                QMessageBox.information(
                    self, "Exportar", f"Resultados exportados para:\n{file_path}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")

    def load_selected_conversation(self):
        """Carrega conversa selecionada"""
        current_item = self.conversations_list.currentItem()
        if not current_item:
            QMessageBox.information(
                self, "Carregar", "Selecione uma conversa primeiro!"
            )
            return

        conv = current_item.data(Qt.ItemDataRole.UserRole)
        self.conversation_selected.emit(conv)

        QMessageBox.information(
            self,
            "Conversa Carregada",
            f"Conversa '{conv['title']}' foi carregada no chat principal!",
        )

        self.accept()

    def apply_style(self):
        """Aplica estilo"""
        style = """
        QDialog {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 5px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QLineEdit {
            padding: 8px;
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
            selection-background-color: #2196F3;
        }
        
        QLineEdit:focus {
            border-color: #2196F3;
        }
        
        QPushButton {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            background-color: #2196F3;
            color: white;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #1976D2;
        }
        
        QPushButton:pressed {
            background-color: #1565C0;
        }
        
        QListWidget {
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
            alternate-background-color: #353535;
        }
        
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #444;
        }
        
        QListWidget::item:selected {
            background-color: #2196F3;
        }
        
        QTextEdit {
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
            padding: 8px;
        }
        
        QComboBox {
            padding: 6px;
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QDateEdit {
            padding: 6px;
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
        }
        
        QCheckBox {
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 2px solid #555;
            border-radius: 3px;
            background-color: #2d2d2d;
        }
        
        QCheckBox::indicator:checked {
            border: 2px solid #2196F3;
            border-radius: 3px;
            background-color: #2196F3;
        }
        """
        self.setStyleSheet(style)


# Exportar para uso externo
__all__ = ["HistorySearchDialog"]

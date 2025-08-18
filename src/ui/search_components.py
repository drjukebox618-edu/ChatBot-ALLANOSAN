"""
Sistema de filtros para busca no histórico.
"""
from typing import Dict, Any, List, Tuple
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QComboBox, QCheckBox, QDateEdit, QGroupBox, QGridLayout
)
from PyQt6.QtCore import QDate, pyqtSignal


class SearchFilters(QWidget):
    """Widget de filtros de busca."""
    
    filters_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura interface dos filtros."""
        layout = QVBoxLayout(self)
        
        # Grupo de filtros básicos
        basic_group = QGroupBox("Filtros de Busca")
        basic_layout = QGridLayout(basic_group)
        
        # Texto de busca
        basic_layout.addWidget(QLabel("Buscar:"), 0, 0)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para buscar...")
        basic_layout.addWidget(self.search_input, 0, 1, 1, 2)
        
        # Filtro por remetente
        basic_layout.addWidget(QLabel("Remetente:"), 1, 0)
        self.sender_combo = QComboBox()
        self.sender_combo.addItems(["Todos", "Você", "Assistente", "Sistema"])
        basic_layout.addWidget(self.sender_combo, 1, 1)
        
        # Filtro por data
        basic_layout.addWidget(QLabel("Data (de):"), 2, 0)
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        basic_layout.addWidget(self.date_from, 2, 1)
        
        basic_layout.addWidget(QLabel("Data (até):"), 2, 2)
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        basic_layout.addWidget(self.date_to, 2, 3)
        
        # Opções avançadas
        self.case_sensitive = QCheckBox("Diferenciar maiúsculas/minúsculas")
        basic_layout.addWidget(self.case_sensitive, 3, 0, 1, 2)
        
        self.whole_words = QCheckBox("Palavras inteiras apenas")
        basic_layout.addWidget(self.whole_words, 3, 2, 1, 2)
        
        layout.addWidget(basic_group)
        
        # Conectar sinais
        self.search_input.textChanged.connect(self.emit_filters_changed)
        self.sender_combo.currentTextChanged.connect(self.emit_filters_changed)
        self.date_from.dateChanged.connect(self.emit_filters_changed)
        self.date_to.dateChanged.connect(self.emit_filters_changed)
        self.case_sensitive.toggled.connect(self.emit_filters_changed)
        self.whole_words.toggled.connect(self.emit_filters_changed)
    
    def emit_filters_changed(self):
        """Emite sinal de mudança nos filtros."""
        filters = self.get_filters()
        self.filters_changed.emit(filters)
    
    def get_filters(self) -> Dict[str, Any]:
        """Retorna filtros atuais."""
        return {
            'search_text': self.search_input.text(),
            'sender_filter': self.sender_combo.currentText().lower(),
            'date_from': self.date_from.date().toPython(),
            'date_to': self.date_to.date().toPython(),
            'case_sensitive': self.case_sensitive.isChecked(),
            'whole_words': self.whole_words.isChecked()
        }
    
    def clear_filters(self):
        """Limpa todos os filtros."""
        self.search_input.clear()
        self.sender_combo.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.case_sensitive.setChecked(False)
        self.whole_words.setChecked(False)


class SearchEngine:
    """Motor de busca para conversas."""
    
    def __init__(self):
        self.conversations = []
    
    def set_conversations(self, conversations: List[Dict]):
        """Define conversas para busca."""
        self.conversations = conversations
    
    def search(self, filters: Dict[str, Any]) -> List[Tuple[str, Dict, float]]:
        """Executa busca com filtros."""
        results = []
        
        for conv_id, conversation in enumerate(self.conversations):
            score = self._calculate_relevance(conversation, filters)
            if score > 0:
                results.append((conv_id, conversation, score))
        
        # Ordenar por relevância
        results.sort(key=lambda x: x[2], reverse=True)
        return results
    
    def _calculate_relevance(self, conversation: Dict, filters: Dict[str, Any]) -> float:
        """Calcula relevância da conversa com os filtros."""
        score = 0.0
        
        # Filtro de texto
        search_text = filters.get('search_text', '').strip()
        if search_text:
            text_score = self._search_in_conversation(conversation, search_text, filters)
            if text_score == 0:
                return 0  # Se não encontrou texto, irrelevante
            score += text_score
        else:
            score = 1.0  # Sem filtro de texto, todas são relevantes
        
        # Filtro de remetente
        sender_filter = filters.get('sender_filter', 'todos')
        if sender_filter != 'todos':
            if not self._match_sender(conversation, sender_filter):
                return 0
        
        # Filtro de data
        if not self._match_date_range(conversation, filters):
            return 0
        
        return score
    
    def _search_in_conversation(self, conversation: Dict, search_text: str, filters: Dict) -> float:
        """Busca texto na conversa."""
        case_sensitive = filters.get('case_sensitive', False)
        whole_words = filters.get('whole_words', False)
        
        if not case_sensitive:
            search_text = search_text.lower()
        
        score = 0.0
        total_matches = 0
        
        # Buscar no título
        title = conversation.get('title', '')
        if not case_sensitive:
            title = title.lower()
        
        if whole_words:
            if f" {search_text} " in f" {title} ":
                score += 2.0
                total_matches += 1
        else:
            if search_text in title:
                score += 2.0
                total_matches += 1
        
        # Buscar nas mensagens
        messages = conversation.get('messages', [])
        for message in messages:
            content = message.get('content', '')
            if not case_sensitive:
                content = content.lower()
            
            if whole_words:
                if f" {search_text} " in f" {content} ":
                    score += 1.0
                    total_matches += 1
            else:
                count = content.count(search_text)
                if count > 0:
                    score += count * 0.5
                    total_matches += count
        
        return score
    
    def _match_sender(self, conversation: Dict, sender_filter: str) -> bool:
        """Verifica se conversa tem mensagens do remetente especificado."""
        messages = conversation.get('messages', [])
        
        for message in messages:
            role = message.get('role', '').lower()
            if (sender_filter == 'você' and role == 'user') or \
               (sender_filter == 'assistente' and role == 'assistant') or \
               (sender_filter == 'sistema' and role == 'system'):
                return True
        
        return False
    
    def _match_date_range(self, conversation: Dict, filters: Dict) -> bool:
        """Verifica se conversa está no intervalo de datas."""
        try:
            conv_date_str = conversation.get('created_at', '')
            if not conv_date_str:
                return True  # Se não tem data, incluir
            
            conv_date = datetime.fromisoformat(conv_date_str.replace('Z', '+00:00')).date()
            
            date_from = filters.get('date_from')
            date_to = filters.get('date_to')
            
            if date_from and conv_date < date_from:
                return False
            
            if date_to and conv_date > date_to:
                return False
            
            return True
            
        except Exception:
            return True  # Em caso de erro, incluir

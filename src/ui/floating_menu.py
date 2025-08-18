"""
Sistema de Menu Flutuante - ChatBot v3.0
Menu contextual avançado com todas as funcionalidades
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QApplication,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QObject, QEvent, QPoint, QRect
from PyQt6.QtGui import QCursor
from typing import Dict, List, Callable
import logging

logger = logging.getLogger(__name__)


class FloatingMenuAction:
    """Ação do menu flutuante"""

    def __init__(
        self,
        text: str,
        icon: str = None,
        callback: Callable = None,
        shortcut: str = None,
        tooltip: str = None,
        enabled: bool = True,
    ):
        self.text = text
        self.icon = icon
        self.callback = callback
        self.shortcut = shortcut
        self.tooltip = tooltip
        self.enabled = enabled


class FloatingMenuSection:
    """Seção do menu flutuante"""

    def __init__(self, title: str, actions: List[FloatingMenuAction] = None):
        self.title = title
        self.actions = actions or []

    def add_action(self, action: FloatingMenuAction):
        """Adiciona ação à seção"""
        self.actions.append(action)


class FloatingMenu(QWidget):
    """Menu flutuante customizado"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Configurações
        self.animation_duration = 200
        self.menu_radius = 8
        self.menu_padding = 10
        self.item_height = 32
        self.section_spacing = 8

        # Layout
        self.setup_ui()

        # Animações
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(self.animation_duration)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(0.95)

        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(self.animation_duration)
        self.fade_out_animation.setStartValue(0.95)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.finished.connect(self.hide)

        # Estados
        self.is_visible = False
        self.sections: List[FloatingMenuSection] = []

        # Configurar menu padrão
        self.setup_default_menu()

    def setup_ui(self):
        """Configura interface"""
        self.setFixedSize(280, 400)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Widget de conteúdo com background customizado
        self.content_widget = QWidget()
        self.content_widget.setObjectName("floatingMenuContent")
        layout.addWidget(self.content_widget)

        # Layout do conteúdo
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(
            self.menu_padding, self.menu_padding, self.menu_padding, self.menu_padding
        )
        self.content_layout.setSpacing(self.section_spacing)

        # Estilo
        self.apply_style()

    def apply_style(self):
        """Aplica estilo ao menu"""
        style = """
        QWidget#floatingMenuContent {
            background-color: rgba(30, 30, 30, 240);
            border: 1px solid #2196F3;
            border-radius: 8px;
        }
        QLabel.menuSectionTitle {
            color: #2196F3;
            font-weight: bold;
            font-size: 12px;
            padding: 6px 8px 4px 8px;
            background-color: rgba(33, 150, 243, 30);
            border-radius: 4px;
            margin-bottom: 4px;
        }
        QPushButton.menuAction {
            text-align: left;
            padding: 4px 10px;
            min-height: 28px;
            max-height: 32px;
            border: none;
            border-radius: 4px;
            background-color: transparent;
            color: #fff;
            font-size: 11px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QPushButton.menuAction:hover {
            background-color: #1976D2;
            color: #fff;
        }
        QPushButton.menuAction:pressed {
            background-color: #1565C0;
            color: #fff;
        }
        QPushButton.menuAction:disabled {
            color: #888;
            background-color: transparent;
        }
        QFrame.menuSeparator {
            background-color: #2196F3;
            max-height: 1px;
            min-height: 1px;
            margin: 6px 0px;
        }
        """
        self.setStyleSheet(style)

    def setup_default_menu(self):
        """Configura menu padrão"""
        # Seção IA
        ai_section = FloatingMenuSection("🤖 Inteligência Artificial")
        ai_section.add_action(
            FloatingMenuAction(
                "Gemini (Padrão)",
                "🔮",
                self.switch_to_gemini,
                "Ctrl+1",
                "Trocar para Gemini",
            )
        )
        ai_section.add_action(
            FloatingMenuAction(
                "GPT-4", "🧠", self.switch_to_gpt, "Ctrl+2", "Trocar para GPT-4"
            )
        )
        ai_section.add_action(
            FloatingMenuAction(
                "Claude", "🎭", self.switch_to_claude, "Ctrl+3", "Trocar para Claude"
            )
        )

        # Seção Chat
        chat_section = FloatingMenuSection("💬 Conversas")
        chat_section.add_action(
            FloatingMenuAction(
                "Nova Conversa",
                "➕",
                self.new_conversation,
                "Ctrl+N",
                "Iniciar nova conversa",
            )
        )
        chat_section.add_action(
            FloatingMenuAction(
                "Limpar Chat", "🗑️", self.clear_chat, "Ctrl+L", "Limpar chat atual"
            )
        )
        chat_section.add_action(
            FloatingMenuAction(
                "Histórico",
                "📚",
                self.toggle_history,
                "F9",
                "Mostrar/ocultar histórico",
            )
        )
        chat_section.add_action(
            FloatingMenuAction(
                "Buscar Histórico",
                "🔍",
                self.search_history,
                "Ctrl+F",
                "Buscar no histórico",
            )
        )

        # Seção Projeto
        project_section = FloatingMenuSection("📁 Projeto")
        project_section.add_action(
            FloatingMenuAction(
                "Carregar Projeto",
                "📂",
                self.load_project,
                "Ctrl+O",
                "Carregar projeto completo",
            )
        )
        project_section.add_action(
            FloatingMenuAction(
                "Analisar Código",
                "🔬",
                self.analyze_code,
                "Ctrl+A",
                "Analisar código do projeto",
            )
        )
        project_section.add_action(
            FloatingMenuAction(
                "Sugerir Melhorias",
                "💡",
                self.suggest_improvements,
                "Ctrl+I",
                "Sugerir melhorias",
            )
        )

        # Seção Ferramentas
        tools_section = FloatingMenuSection("🛠️ Ferramentas")
        tools_section.add_action(
            FloatingMenuAction(
                "OCR de Imagem",
                "📷",
                self.ocr_image,
                "Ctrl+Shift+O",
                "Extrair texto de imagem",
            )
        )
        tools_section.add_action(
            FloatingMenuAction(
                "Analisar Imagem",
                "🖼️",
                self.analyze_image,
                "Ctrl+Shift+I",
                "Analisar conteúdo de imagem",
            )
        )
        tools_section.add_action(
            FloatingMenuAction(
                "Exportar Chat", "💾", self.export_chat, "Ctrl+E", "Exportar conversa"
            )
        )

        # Seção Configurações
        settings_section = FloatingMenuSection("⚙️ Configurações")
        settings_section.add_action(
            FloatingMenuAction(
                "Criatividade",
                "🎨",
                self.adjust_creativity,
                "Ctrl+T",
                "Ajustar temperatura (criatividade)",
            )
        )
        settings_section.add_action(
            FloatingMenuAction(
                "Tema Claro/Escuro", "🌙", self.toggle_theme, "F11", "Alternar tema"
            )
        )
        settings_section.add_action(
            FloatingMenuAction(
                "Configurar APIs",
                "🔑",
                self.configure_apis,
                "Ctrl+K",
                "Configurar chaves de API",
            )
        )
        settings_section.add_action(
            FloatingMenuAction(
                "Preferências", "⚙️", self.open_settings, "Ctrl+,", "Abrir configurações"
            )
        )

        # Adicionar seções
        self.sections = [
            ai_section,
            chat_section,
            project_section,
            tools_section,
            settings_section,
        ]
        self.build_menu()

    def build_menu(self):
        """Constrói o menu visual"""
        # Limpar layout
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)

        # Adicionar seções
        for i, section in enumerate(self.sections):
            if i > 0:
                # Separador entre seções
                separator = QFrame()
                separator.setObjectName("menuSeparator")
                separator.setFrameShape(QFrame.Shape.HLine)
                self.content_layout.addWidget(separator)

            # Título da seção
            title_label = QLabel(section.title)
            title_label.setObjectName("menuSectionTitle")
            self.content_layout.addWidget(title_label)

            # Ações da seção
            for action in section.actions:
                btn = QPushButton()
                btn.setObjectName("menuAction")
                btn.setEnabled(action.enabled)
                btn.setMinimumHeight(28)
                btn.setMaximumHeight(32)
                # Ícone/texto
                if action.icon:
                    btn.setText(f"{action.icon}  {action.text}")
                else:
                    btn.setText(action.text)
                if action.tooltip:
                    btn.setToolTip(
                        f"{action.tooltip}\n{action.shortcut}"
                        if action.shortcut
                        else action.tooltip
                    )
                if action.callback:
                    btn.clicked.connect(action.callback)
                self.content_layout.addWidget(btn)

        # Espaçador no final
        self.content_layout.addStretch()

    def show_at_position(self, position: QPoint):
        """Mostra o menu em uma posição específica"""
        if self.is_visible:
            self.hide_menu()
            return

        # Ajustar posição para não sair da tela
        screen = QApplication.primaryScreen().geometry()
        menu_rect = QRect(position, self.size())

        if menu_rect.right() > screen.right():
            position.setX(screen.right() - self.width())
        if menu_rect.bottom() > screen.bottom():
            position.setY(screen.bottom() - self.height())
        if position.x() < screen.left():
            position.setX(screen.left())
        if position.y() < screen.top():
            position.setY(screen.top())

        self.move(position)
        self.show()
        self.fade_in_animation.start()
        self.is_visible = True

        logger.info(f"Menu flutuante mostrado em: {position}")

    def hide_menu(self):
        """Esconde o menu com animação"""
        if self.is_visible:
            self.fade_out_animation.start()
            self.is_visible = False

    def mousePressEvent(self, event):
        """Evento de clique"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Verificar se clicou fora do menu
            if not self.content_widget.geometry().contains(event.pos()):
                self.hide_menu()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """Evento de tecla"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_menu()
        super().keyPressEvent(event)

    # Callbacks dos menus (implementar na classe principal)
    def switch_to_gemini(self):
        """Trocar para Gemini"""
        if hasattr(self.parent(), "switch_ai_provider"):
            self.parent().switch_ai_provider("gemini")
        self.hide_menu()

    def switch_to_gpt(self):
        """Trocar para GPT"""
        if hasattr(self.parent(), "switch_ai_provider"):
            self.parent().switch_ai_provider("gpt")
        self.hide_menu()

    def switch_to_claude(self):
        """Trocar para Claude"""
        if hasattr(self.parent(), "switch_ai_provider"):
            self.parent().switch_ai_provider("claude")
        self.hide_menu()

    def new_conversation(self):
        """Nova conversa"""
        if hasattr(self.parent(), "new_conversation"):
            self.parent().new_conversation()
        self.hide_menu()

    def clear_chat(self):
        """Limpar chat"""
        if hasattr(self.parent(), "clear_chat"):
            self.parent().clear_chat()
        self.hide_menu()

    def toggle_history(self):
        """Alternar histórico"""
        if hasattr(self.parent(), "toggle_history_sidebar"):
            self.parent().toggle_history_sidebar()
        self.hide_menu()

    def search_history(self):
        """Buscar histórico"""
        if hasattr(self.parent(), "open_history_search"):
            self.parent().open_history_search()
        self.hide_menu()

    def load_project(self):
        """Carregar projeto"""
        if hasattr(self.parent(), "load_project"):
            self.parent().load_project()
        self.hide_menu()

    def analyze_code(self):
        """Analisar código"""
        if hasattr(self.parent(), "analyze_project_code"):
            self.parent().analyze_project_code()
        self.hide_menu()

    def suggest_improvements(self):
        """Sugerir melhorias"""
        if hasattr(self.parent(), "suggest_project_improvements"):
            self.parent().suggest_project_improvements()
        self.hide_menu()

    def ocr_image(self):
        """OCR de imagem"""
        if hasattr(self.parent(), "ocr_image"):
            self.parent().ocr_image()
        self.hide_menu()

    def analyze_image(self):
        """Analisar imagem"""
        if hasattr(self.parent(), "analyze_image"):
            self.parent().analyze_image()
        self.hide_menu()

    def export_chat(self):
        """Exportar chat"""
        if hasattr(self.parent(), "export_conversation"):
            self.parent().export_conversation()
        self.hide_menu()

    def adjust_creativity(self):
        """Ajustar criatividade"""
        if hasattr(self.parent(), "open_creativity_dialog"):
            self.parent().open_creativity_dialog()
        self.hide_menu()

    def toggle_theme(self):
        """Alternar tema"""
        if hasattr(self.parent(), "toggle_theme"):
            self.parent().toggle_theme()
        self.hide_menu()

    def configure_apis(self):
        """Configurar APIs"""
        if hasattr(self.parent(), "open_api_config"):
            self.parent().open_api_config()
        self.hide_menu()

    def open_settings(self):
        """Abrir configurações"""
        if hasattr(self.parent(), "open_settings_dialog"):
            self.parent().open_settings_dialog()
        self.hide_menu()


class FloatingMenuManager(QObject):
    """Gerenciador do menu flutuante"""

    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.floating_menu = FloatingMenu(parent_widget)

        # Configurar eventos globais
        self.setup_global_events()

    def setup_global_events(self):
        """Configura eventos globais"""
        # Instalar filtro de eventos para capturar clique direito
        self.parent_widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Filtro de eventos"""
        if event.type() == QEvent.Type.ContextMenu:
            # Mostrar menu no clique direito
            self.show_menu_at_cursor()
            return True

        return super().eventFilter(obj, event)

    def show_menu_at_cursor(self):
        """Mostra menu na posição do cursor"""
        cursor_pos = QCursor.pos()
        self.floating_menu.show_at_position(cursor_pos)

    def show_menu_at_position(self, position: QPoint):
        """Mostra menu em posição específica"""
        self.floating_menu.show_at_position(position)

    def toggle_menu(self):
        """Alterna visibilidade do menu"""
        if self.floating_menu.is_visible:
            self.floating_menu.hide_menu()
        else:
            self.show_menu_at_cursor()

    def hide_menu(self):
        """Esconde o menu"""
        self.floating_menu.hide_menu()

    def update_menu_actions(self, provider_status: Dict[str, bool]):
        """Atualiza status das ações baseado nos provedores disponíveis"""
        # Encontrar seção de IA
        for section in self.floating_menu.sections:
            if "Inteligência Artificial" in section.title:
                for action in section.actions:
                    if "Gemini" in action.text:
                        action.enabled = provider_status.get("gemini", False)
                    elif "GPT" in action.text:
                        action.enabled = provider_status.get("gpt", False)
                    elif "Claude" in action.text:
                        action.enabled = provider_status.get("claude", False)

        # Reconstruir menu
        self.floating_menu.build_menu()

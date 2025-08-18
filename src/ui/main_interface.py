"""
ChatBot v3.0 - Interface Principal Completa
Sistema unificado com todas as funcionalidades restauradas
"""

import sys
import os
import logging
import datetime
from typing import List

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QSplitter,
    QLabel,
    QMessageBox,
    QFileDialog,
    QDockWidget,
    QListWidget,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QSpinBox,
)
from PyQt6.QtCore import (
    Qt,
    QTimer,
)
from PyQt6.QtGui import (
    QFont,
    QPixmap,
    QAction,
    QKeySequence,
    QShortcut,
    QTextCursor,
)

# Imports locais
from src.core.ai_provider import ai_manager, AIProvider
from src.config.config_manager import config_manager
from src.ui.floating_menu import FloatingMenuManager
from src.ui.api_config_dialog import APIConfigDialog
from src.ui.creativity_dialog import CreativityDialog
from src.core.project_analyzer import ProjectAnalysisDialog

logger = logging.getLogger(__name__)


class ChatMessage:
    """Mensagem do chat"""

    def __init__(self, content: str, is_user: bool, timestamp: str = None):
        import datetime

        self.content = content
        self.is_user = is_user
        self.timestamp = timestamp or datetime.datetime.now().strftime("%H:%M:%S")


class AdvancedChatBotGUI(QMainWindow):
    """Interface principal do ChatBot v3.0"""

    def __init__(self):
        super().__init__()

        # Estado da aplicação
        self.conversation_history: List[ChatMessage] = []
        self.current_temperature = 0.7
        self.current_provider = AIProvider.GEMINI
        self.is_streaming = False
        self.settings_panel_visible = False

        # Componentes
        self.floating_menu_manager = None
        self.history_dialog = None
        self.ocr_dialog = None

        # Histórico real
        from src.core.conversation_history import ConversationHistory

        self.history_manager = ConversationHistory()
        self.current_conversation_id = self.history_manager.create_conversation()

        # Configurar aplicação
        self.setup_application()
        self.setup_ui()
        self.setup_menu_and_toolbar()
        self.setup_floating_menu()
        self.setup_shortcuts()
        self.create_status_elements()
        self.setup_ai_providers()
        self.apply_theme()

        # Carregar configurações
        self.load_settings()

        logger.info("ChatBot v3.0 iniciado com sucesso")

    def setup_application(self):
        """Configura aplicação"""
        self.setWindowTitle("🤖 ChatBot v3.0 - Sistema Completo com IA")
        self.setMinimumSize(1000, 700)

        # Ícone (se disponível)
        try:
            # self.setWindowIcon(QIcon("assets/icon.png"))
            pass
        except Exception:
            pass

    def setup_ui(self):
        """Configura interface principal"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Splitter principal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar esquerda (histórico)
        self.setup_sidebar(main_splitter)

        # Área central do chat
        self.setup_chat_area(main_splitter)

        # Criar sidebar de configurações (inicialmente oculta)
        self.create_settings_sidebar()

        # Configurar proporções do splitter (2 painéis: sidebar + chat)
        main_splitter.setSizes([250, 750])

        # Configurar collapsible apenas para painéis existentes
        if main_splitter.count() >= 1:
            main_splitter.setCollapsible(0, False)  # Histórico fixo (não recolhível)
        if main_splitter.count() >= 2:
            main_splitter.setCollapsible(
                1, False
            )  # Chat sempre visível        # Armazenar referência do splitter
        self.main_splitter = main_splitter

        main_layout.addWidget(main_splitter)

        # Status bar
        self.setup_status_bar()

        # Cabeçalho estilo barra, igual ao 'Histórico de Conversas'
        header_bar = QWidget()
        header_bar.setStyleSheet(
            "background-color: #f5f5f5; border-bottom: 1px solid #ccc;"
        )
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(12, 0, 0, 0)
        header_layout.setSpacing(8)
        header_icon = QLabel()
        header_icon.setPixmap(
            QPixmap(":/icons/chatbot.png").scaled(
                24,
                24,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        header_label = QLabel(
            "<span style='font-size:18px; font-weight:bold; color:#222;'>ChatBot IA 3.0</span>"
        )
        header_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        main_layout.insertWidget(0, header_bar)

        # Mensagem de boas-vindas ao abrir o chat
        self.chat_display.append(
            "<b>Bem-vindo ao ChatBot IA 3.0</b><br>"
            "<br>Este sistema integra múltiplos provedores de IA (Gemini, GPT-4, Claude), OCR, análise de projetos e histórico persistente."
            "<br><br><b>Principais recursos:</b>"
            "<ul>"
            "<li>Troca dinâmica de IA (menu flutuante ou configurações)</li>"
            "<li>OCR e processamento de imagens</li>"
            "<li>Carregamento e análise de projetos</li>"
            "<li>Histórico de conversas clicável e persistente</li>"
            "<li>Configurações avançadas de API e criatividade</li>"
            "<li>Atalhos: F9 (Histórico), F10 (Configurações), F11 (Tema)</li>"
            "</ul>"
            "<br><b>Tecnologias e integrações para programador sênior:</b>"
            "<ul>"
            "<li>Python 3.12, PyQt6, asyncio, multiprocessamento</li>"
            "<li>APIs RESTful, WebSocket, integração com OpenAI, Google Gemini, Anthropic Claude</li>"
            "<li>OCR (Tesseract, Google Vision)</li>"
            "<li>Manipulação de arquivos JSON, YAML, XML</li>"
            "<li>Logs avançados, encoding UTF-8, suporte multiplataforma</li>"
            "<li>Extensível para automação, análise de dados, integração com sistemas legados</li>"
            "<li>Pronto para CI/CD, Docker, ambientes Anaconda/Conda</li>"
            "</ul>"
            "<br>Utilize o menu flutuante (botão direito) para acessar funções rápidas."
            "<br>Qualquer dúvida, consulte o README ou explore as opções do sistema."
        )

    def create_settings_sidebar(self):
        """Cria sidebar de configurações simplificada (não adiciona ao layout)"""
        self.settings_widget = QWidget()
        self.settings_widget.setFixedWidth(250)
        settings_layout = QVBoxLayout(self.settings_widget)
        settings_layout.setContentsMargins(10, 10, 10, 10)

        # Título
        title_label = QLabel("⚙️ Configurações")
        title_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-bottom: 10px;"
        )
        settings_layout.addWidget(title_label)

        # Grupo de Status das APIs
        api_group = QGroupBox("🤖 Status das APIs")
        api_layout = QFormLayout(api_group)

        # Status dos provedores
        self.gemini_status = QLabel("❌ Não configurado")
        self.gpt_status = QLabel("❌ Não configurado")
        self.claude_status = QLabel("❌ Não configurado")

        api_layout.addRow("Gemini:", self.gemini_status)
        api_layout.addRow("GPT-4:", self.gpt_status)
        api_layout.addRow("Claude:", self.claude_status)

        settings_layout.addWidget(api_group)

        # Grupo de Status do Sistema
        system_group = QGroupBox("📊 Status do Sistema")
        system_layout = QVBoxLayout(system_group)

        # Informações básicas
        provider_label = QLabel("Provedor Atual: Gemini")
        provider_label.setObjectName("current_provider")
        system_layout.addWidget(provider_label)

        model_label = QLabel("Modelo: gemini-2.5-flash")
        model_label.setObjectName("current_model")
        system_layout.addWidget(model_label)

        temp_label = QLabel("Temperatura: 0.7")
        temp_label.setObjectName("current_temp")
        system_layout.addWidget(temp_label)

        settings_layout.addWidget(system_group)

        # Espaçador
        settings_layout.addStretch()

        # Botão de configurações avançadas
        advanced_btn = QPushButton("🔧 Configurações Avançadas")
        advanced_btn.clicked.connect(self.open_settings_dialog)
        settings_layout.addWidget(advanced_btn)

        # Criar checkboxes para compatibilidade (não visíveis na interface)
        self.streaming_checkbox = QCheckBox("Streaming de respostas")
        self.streaming_checkbox.setChecked(True)

        self.auto_save_checkbox = QCheckBox("Auto-salvar conversas")
        self.auto_save_checkbox.setChecked(True)

        # Inicialmente invisível
        self.settings_widget.setVisible(False)
        self.settings_panel_visible = False

    def setup_sidebar(self, parent_splitter):
        """Configura sidebar do histórico"""
        # Dock widget para histórico
        self.history_dock = QDockWidget("📚 Histórico de Conversas", self)
        self.history_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        # Widget do histórico
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)

        # Botões do histórico
        history_buttons = QHBoxLayout()

        search_btn = QPushButton("🔍 Buscar")
        search_btn.clicked.connect(self.open_history_search)
        search_btn.setToolTip("Buscar no histórico (Ctrl+F)")

        history_buttons.addWidget(search_btn)

        history_layout.addLayout(history_buttons)

        # Lista de conversas
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_conversation)
        history_layout.addWidget(self.history_list)

        # Preencher lista de conversas com nome, data e horário
        self.update_history_list()

        self.history_dock.setWidget(history_widget)

        # Adicionar como dock widget
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.history_dock)

    def update_history_list(self):
        """Atualiza a lista de conversas no painel de histórico"""
        self.history_list.clear()
        if hasattr(self, "history_manager"):
            conversas = self.history_manager.get_conversations_list()
            for conv in conversas:
                # Formata: Nome (data/hora)
                dt = conv["created_at"][:16].replace("T", " ")  # yyyy-mm-dd HH:MM
                item_text = f"{conv['title']} ({dt})"
                self.history_list.addItem(item_text)

    def setup_chat_area(self, parent_splitter):
        """Configura área principal do chat"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)

        # Cabeçalho do chat
        self.setup_chat_header(chat_layout)

        # Área de mensagens
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 10))
        chat_layout.addWidget(self.chat_display)

        # Área de entrada
        self.setup_input_area(chat_layout)

        parent_splitter.addWidget(chat_widget)

    def setup_chat_header(self, parent_layout):
        """Configura cabeçalho do chat"""
        header_layout = QHBoxLayout()

        # Provedor atual
        self.provider_label = QLabel("🔮 Gemini")
        self.provider_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

        # Selector de provedor
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["🔮 Gemini", "🧠 GPT-4", "🎭 Claude"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)

        header_layout.addWidget(self.provider_label)
        header_layout.addWidget(self.provider_combo)
        header_layout.addStretch()
        # Botão de configurações removido

        parent_layout.addLayout(header_layout)

    def setup_input_area(self, parent_layout):
        """Configura área de entrada"""
        input_layout = QVBoxLayout()

        # Área de texto para entrada
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText(
            "Digite sua mensagem aqui... (Ctrl+Enter para enviar, Shift+Enter para nova linha)"
        )
        self.message_input.keyPressEvent = self.handle_input_key_press
        input_layout.addWidget(self.message_input)

        # Botões de ação
        buttons_layout = QHBoxLayout()

        # Botão de envio
        self.send_btn = QPushButton("📤 Enviar")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setDefault(True)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.send_btn)

        input_layout.addLayout(buttons_layout)
        parent_layout.addLayout(input_layout)

    def setup_settings_panel(self, parent_splitter):
        """Configura painel de configurações"""
        # Dock widget para configurações
        self.settings_dock = QDockWidget("⚙️ Configurações", self)
        self.settings_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        # Widget de configurações
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)

        # Grupo de IA
        ai_group = QGroupBox("🤖 Inteligência Artificial")
        ai_layout = QFormLayout(ai_group)

        ai_layout.addRow("Provedor atual:", QLabel("Use o menu IA para trocar"))

        settings_layout.addWidget(ai_group)

        # Grupo de funcionalidades
        features_group = QGroupBox("🛠️ Funcionalidades")
        features_layout = QVBoxLayout(features_group)

        self.streaming_checkbox = QCheckBox("Streaming de respostas")
        self.streaming_checkbox.setChecked(True)

        self.auto_save_checkbox = QCheckBox("Auto-salvar conversas")
        self.auto_save_checkbox.setChecked(True)

        self.sound_checkbox = QCheckBox("Notificações sonoras")

        features_layout.addWidget(self.streaming_checkbox)
        features_layout.addWidget(self.auto_save_checkbox)
        features_layout.addWidget(self.sound_checkbox)

        settings_layout.addWidget(features_group)

        # Grupo de tema
        theme_group = QGroupBox("🎨 Aparência")
        theme_layout = QVBoxLayout(theme_group)

        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Tamanho da fonte:"))

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(20)
        self.font_size_spin.setValue(10)
        self.font_size_spin.valueChanged.connect(self.change_font_size)

        font_size_layout.addWidget(self.font_size_spin)

        theme_layout.addLayout(font_size_layout)

        settings_layout.addWidget(theme_group)

        settings_layout.addStretch()

        self.settings_dock.setWidget(settings_widget)

        # Adicionar como dock widget
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.settings_dock)

    def setup_menu_and_toolbar(self):
        """Configura menu e toolbar"""
        # Menu bar
        menubar = self.menuBar()

        # Menu Arquivo
        file_menu = menubar.addMenu("📁 Arquivo")

        new_action = QAction("➕ Nova Conversa", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.new_conversation)
        file_menu.addAction(new_action)

        open_project_action = QAction("📂 Carregar Projeto", self)
        open_project_action.setShortcut(QKeySequence("Ctrl+O"))
        open_project_action.triggered.connect(self.load_project)
        file_menu.addAction(open_project_action)

        file_menu.addSeparator()

        export_action = QAction("💾 Exportar Conversa", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_conversation)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("❌ Sair", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Editar
        edit_menu = menubar.addMenu("✏️ Editar")

        clear_action = QAction("🗑️ Limpar Chat", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.triggered.connect(self.clear_chat)
        edit_menu.addAction(clear_action)

        # Menu IA
        ai_menu = menubar.addMenu("🤖 IA")

        gemini_action = QAction("🔮 Gemini", self)
        gemini_action.setShortcut(QKeySequence("Ctrl+1"))
        gemini_action.triggered.connect(lambda: self.switch_ai_provider("gemini"))
        ai_menu.addAction(gemini_action)

        gpt_action = QAction("🧠 GPT-4", self)
        gpt_action.setShortcut(QKeySequence("Ctrl+2"))
        gpt_action.triggered.connect(lambda: self.switch_ai_provider("gpt"))
        ai_menu.addAction(gpt_action)

        claude_action = QAction("🎭 Claude", self)
        claude_action.setShortcut(QKeySequence("Ctrl+3"))
        claude_action.triggered.connect(lambda: self.switch_ai_provider("claude"))
        ai_menu.addAction(claude_action)

        ai_menu.addSeparator()

        creativity_action = QAction("🎨 Ajustar Criatividade", self)
        creativity_action.setShortcut(QKeySequence("Ctrl+T"))
        creativity_action.triggered.connect(self.open_creativity_dialog)
        ai_menu.addAction(creativity_action)

        # Menu Ferramentas
        tools_menu = menubar.addMenu("🛠️ Ferramentas")

        ocr_action = QAction("📷 OCR de Imagem", self)
        ocr_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        ocr_action.triggered.connect(self.ocr_image)
        tools_menu.addAction(ocr_action)

        analyze_action = QAction("🔬 Analisar Projeto", self)
        analyze_action.setShortcut(QKeySequence("Ctrl+A"))
        analyze_action.triggered.connect(self.analyze_project_code)
        tools_menu.addAction(analyze_action)

        # Menu Visualizar
        view_menu = menubar.addMenu("👁️ Visualizar")

        history_action = QAction("📚 Alternar Histórico", self)
        history_action.setShortcut(QKeySequence("F9"))
        history_action.triggered.connect(self.toggle_history_sidebar)
        view_menu.addAction(history_action)

        settings_action = QAction("⚙️ Alternar Configurações", self)
        settings_action.setShortcut(QKeySequence("F10"))
        settings_action.triggered.connect(self.toggle_settings_panel)
        view_menu.addAction(settings_action)

        theme_action = QAction("🌙 Alternar Tema", self)
        theme_action.setShortcut(QKeySequence("F11"))
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)

        # Menu Ajuda
        help_menu = menubar.addMenu("❓ Ajuda")

        about_action = QAction("ℹ️ Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_elements(self):
        """Cria elementos de status necessários para compatibilidade"""
        # Settings dock para compatibilidade (invisível)
        self.settings_dock = QDockWidget("⚙️ Configurações", self)
        self.settings_dock.setVisible(False)

        # Estes elementos não são adicionados à interface, apenas criados para compatibilidade
        # A funcionalidade real é controlada através dos menus e toolbar

    def setup_floating_menu(self):
        """Configura menu flutuante"""
        self.floating_menu_manager = FloatingMenuManager(self)

    def setup_shortcuts(self):
        """Configura atalhos adicionais"""
        # Atalho para menu flutuante
        menu_shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        menu_shortcut.activated.connect(self.floating_menu_manager.toggle_menu)

        # Atalho para busca no histórico
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.open_history_search)

    def setup_ai_providers(self):
        """Configura provedores de IA"""
        # Configurar ai_manager com as chaves das configurações
        try:
            config = config_manager

            if config.api_config.gemini_api_key:
                ai_manager.set_api_key(
                    AIProvider.GEMINI, config.api_config.gemini_api_key
                )

            if config.api_config.openai_api_key:
                ai_manager.set_api_key(AIProvider.GPT, config.api_config.openai_api_key)

            if config.api_config.anthropic_api_key:
                ai_manager.set_api_key(
                    AIProvider.CLAUDE, config.api_config.anthropic_api_key
                )

            # Definir Gemini como padrão
            if config.api_config.gemini_api_key:
                ai_manager.switch_provider(AIProvider.GEMINI)

            self.update_provider_status()

        except Exception as e:
            logger.error(f"Erro ao configurar provedores de IA: {e}")

    def setup_status_bar(self):
        """Configura barra de status"""
        status_bar = self.statusBar()

        # Labels permanentes
        self.status_provider = QLabel("🔮 Gemini")
        self.status_temperature = QLabel("🎨 0.7")
        self.status_tokens = QLabel("📊 0 tokens")

        status_bar.addPermanentWidget(self.status_provider)
        status_bar.addPermanentWidget(self.status_temperature)
        status_bar.addPermanentWidget(self.status_tokens)

        status_bar.showMessage("✅ ChatBot v3.0 pronto para uso!")

    def apply_theme(self):
        """Aplica tema baseado na configuração"""
        colors = config_manager.get_theme_colors()

        style = f"""
        QMainWindow {{
            background-color: {colors["background"]};
            color: {colors["text"]};
        }}
        
        QTextEdit {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            border: 1px solid #555;
            border-radius: 4px;
            padding: 8px;
            font-family: 'Segoe UI', sans-serif;
        }}
        
        QPushButton {{
            background-color: {colors["primary"]};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors["secondary"]};
        }}
        
        QPushButton:pressed {{
            background-color: #1565C0;
        }}
        
        QComboBox, QLineEdit, QSpinBox {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            border: 1px solid #555;
            border-radius: 4px;
            padding: 6px;
        }}
        
        QListWidget {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            border: 1px solid #555;
            border-radius: 4px;
            alternate-background-color: {colors["background"]};
        }}
        
        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid #444;
        }}
        
        QListWidget::item:selected {{
            background-color: {colors["primary"]};
        }}
        
        QDockWidget {{
            background-color: {colors["background"]};
            color: {colors["text"]};
            titlebar-close-icon: url(close.png);
        }}
        
        QDockWidget::title {{
            background-color: {colors["surface"]};
            padding: 8px;
            border-bottom: 1px solid #555;
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 2px solid #555;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 5px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        
        QSlider::groove:horizontal {{
            border: 1px solid #555;
            height: 8px;
            background: {colors["surface"]};
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background: {colors["primary"]};
            border: 1px solid {colors["primary"]};
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }}
        
        QMenuBar {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            border-bottom: 1px solid #555;
        }}
        
        QMenuBar::item {{
            padding: 6px 12px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors["primary"]};
        }}
        
        QMenu {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            border: 1px solid #555;
        }}
        
        QMenu::item {{
            padding: 8px 24px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors["primary"]};
        }}
        
        QToolBar {{
            background-color: {colors["surface"]};
            border: 1px solid #555;
            spacing: 3px;
        }}
        
        QStatusBar {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            border-top: 1px solid #555;
        }}
        """

        self.setStyleSheet(style)

    def load_settings(self):
        """Carrega configurações"""
        config = config_manager

        # Aplicar configurações da UI
        self.resize(config.ui_config.window_width, config.ui_config.window_height)
        if config.ui_config.window_maximized:
            self.showMaximized()

        # Configurações do chat
        self.current_temperature = config.api_config.default_temperature
        # Slider removido - temperatura configurada via menu
        self.streaming_checkbox.setChecked(config.api_config.stream_responses)

        # Visibilidade dos painéis
        self.history_dock.setVisible(config.ui_config.history_sidebar_visible)
        self.settings_dock.setVisible(config.ui_config.settings_panel_visible)

        logger.info("Configurações carregadas")

    def save_settings(self):
        """Salva configurações"""
        config = config_manager

        # Configurações da janela
        config.ui_config.window_width = self.width()
        config.ui_config.window_height = self.height()
        config.ui_config.window_maximized = self.isMaximized()

        # Visibilidade dos painéis
        config.ui_config.history_sidebar_visible = self.history_dock.isVisible()
        config.ui_config.settings_panel_visible = self.settings_dock.isVisible()

        # Configurações da IA
        config.api_config.default_temperature = self.current_temperature
        config.api_config.stream_responses = self.streaming_checkbox.isChecked()

        config.save_all_configs()
        logger.info("Configurações salvas")

    # Eventos de teclado
    def handle_input_key_press(self, event):
        """Manipula eventos de teclado na entrada"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.send_message()
                return

        # Comportamento padrão
        QTextEdit.keyPressEvent(self.message_input, event)

    # Métodos de IA e comunicação
    async def send_message_async(self, message: str):
        """Envia mensagem de forma assíncrona"""
        try:
            import src.config.config_manager as config_manager

            temp = config_manager.config_manager.api_config.default_temperature
            if self.streaming_checkbox.isChecked():
                # Streaming
                response_parts = []
                async for chunk in ai_manager.generate_stream(
                    message, temperature=temp
                ):
                    response_parts.append(chunk)
                    # Atualizar display em tempo real aqui

                response = "".join(response_parts)
            else:
                # Resposta única
                response = await ai_manager.generate_text(message, temperature=temp)

            return response

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return f"❌ Erro: {str(e)}"

    def send_message(self):
        """Envia mensagem"""
        message = self.message_input.toPlainText().strip()
        if not message:
            return

        # Intercepta comandos de análise de projeto e enriquece o prompt
        lower_msg = message.lower()
        if any(
            cmd in lower_msg
            for cmd in ["analise meu projeto", "analisar projeto", "análise do projeto"]
        ):
            try:
                import json
                from src.core.project_manager import project_manager

                project = project_manager.get_current_project()
                if project:
                    # Garante que a estrutura do projeto está presente
                    estrutura = project.structure
                    if not estrutura:
                        from src.core.project_manager import unified_project_engine

                        estrutura, _, _ = (
                            unified_project_engine.analyze_project_structure(
                                project.path
                            )
                        )
                    estrutura_str = "\n".join(estrutura or [])
                    prompt = (
                        f"ANÁLISE DE PROJETO\n\n"
                        f"Nome: {project.name}\n"
                        f"Tipo: {project.type}\n"
                        f"Caminho: {project.path}\n"
                        f"Arquivos: {project.files_count}\n"
                        f"Tamanho total: {project.total_size} bytes\n"
                        f"Última modificação: {project.last_modified}\n"
                        f"Dependências: {json.dumps(project.dependencies, ensure_ascii=False, indent=2) if project.dependencies else 'Nenhuma'}\n"
                        f"Estrutura:\n{estrutura_str}\n\n"
                        f"Pergunta do usuário: {message}"
                    )
                    message = prompt
                else:
                    message = "Não há projeto carregado! Por favor, carregue um projeto antes de solicitar a análise."
            except Exception as e:
                logger.warning(
                    f"Não foi possível enriquecer prompt de análise de projeto: {e}"
                )
                message += "\n[Erro ao acessar dados do projeto carregado]"

        # Adicionar mensagem do usuário
        self.add_message_to_chat(message, is_user=True)
        self.message_input.clear()

        self.send_btn.setEnabled(False)
        self.send_btn.setText("⏳ Enviando...")

        # Verificar se há API key configurada para o provedor atual
        from src.core.ai_provider import ai_manager

        provider = ai_manager.current_provider
        api_key = ai_manager.api_keys.get(provider)

        if api_key:
            # Chamar IA real (executar assíncrono via QTimer para não travar UI)
            def run_real_ai():
                import asyncio

                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(self.send_message_async(message))
                except Exception as e:
                    response = f"❌ Erro: {str(e)}"
                self.add_message_to_chat(response, is_user=False)
                self.send_btn.setEnabled(True)
                self.send_btn.setText("📤 Enviar")

            QTimer.singleShot(100, run_real_ai)
        else:
            # Sem API key: mostrar resposta simulada
            QTimer.singleShot(1000, lambda: self.simulate_ai_response(message))

    def simulate_ai_response(self, user_message: str):
        """Simula resposta da IA (temporário)"""
        response = (
            f"Echo: {user_message} (Simulação - Configure as APIs para usar IA real)"
        )
        self.add_message_to_chat(response, is_user=False)

        self.send_btn.setEnabled(True)
        self.send_btn.setText("📤 Enviar")

    def add_message_to_chat(self, content: str, is_user: bool):
        """Adiciona mensagem ao chat e salva no histórico real"""
        import datetime

        # Criar mensagem
        message = ChatMessage(
            content, is_user, datetime.datetime.now().strftime("%H:%M:%S")
        )
        self.conversation_history.append(message)

        # Salvar no histórico real
        role = "user" if is_user else "assistant"
        self.history_manager.add_message(self.current_conversation_id, role, content)

        # Formatar e adicionar ao display
        sender = "Você" if is_user else ai_manager.current_provider.value.title()
        icon = "👤" if is_user else "🤖"

        formatted_message = f"""
<div style="margin: 10px 0; padding: 10px; border-left: 3px solid {"#2196F3" if is_user else "#4CAF50"};">
    <strong>{icon} {sender} ({message.timestamp})</strong><br>
    {content.replace("\n", "<br>")}
</div>
"""

        self.chat_display.insertHtml(formatted_message)

        # Scroll para o final
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    # Métodos de interface
    def new_conversation(self):
        """Inicia nova conversa e cria no histórico real"""
        self.conversation_history.clear()
        self.chat_display.clear()
        self.current_conversation_id = self.history_manager.create_conversation()
        self.update_history_list()
        self.statusBar().showMessage("🆕 Nova conversa iniciada")
        logger.info("Nova conversa iniciada")

    def clear_chat(self):
        """Limpa o chat atual"""
        reply = QMessageBox.question(
            self,
            "Limpar Chat",
            "Tem certeza que deseja limpar o chat atual?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.chat_display.clear()
            self.statusBar().showMessage("🗑️ Chat limpo")

    def toggle_history_sidebar(self):
        """Alterna visibilidade do histórico"""
        visible = not self.history_dock.isVisible()
        self.history_dock.setVisible(visible)
        status = "mostrado" if visible else "ocultado"
        self.statusBar().showMessage(f"📚 Histórico {status}")

    def toggle_settings_panel(self):
        """Alterna visibilidade do painel de configurações"""
        if not hasattr(self, "settings_panel_visible"):
            self.settings_panel_visible = False

        if not self.settings_panel_visible:
            # Mostrar painel - adicionar ao splitter
            if not hasattr(self, "settings_widget"):
                self.create_settings_sidebar()

            # Adicionar widget ao splitter
            self.main_splitter.addWidget(self.settings_widget)
            self.settings_widget.setVisible(True)

            # Verificar quantidade de painéis e configurar proporções
            count = self.main_splitter.count()
            if count == 3:
                self.main_splitter.setSizes([200, 500, 250])
                # Configurar collapsible com segurança
                self.main_splitter.setCollapsible(
                    0, False
                )  # Histórico fixo (não recolhível)
                self.main_splitter.setCollapsible(1, False)  # Chat sempre visível
                self.main_splitter.setCollapsible(
                    2, True
                )  # Configurações podem ser recolhidas

            self.settings_panel_visible = True

            # Atualizar status dos provedores quando mostrar o painel
            self.update_provider_status()

            status = "mostrado"
        else:
            # Ocultar painel - usar setParent para remover
            if hasattr(self, "settings_widget"):
                self.settings_widget.setVisible(False)
                self.settings_widget.setParent(None)  # Remove do splitter

            # Reajustar proporções para 2 painéis
            count = self.main_splitter.count()
            if count == 2:
                self.main_splitter.setSizes([250, 750])
                # Reconfigurar collapsible para 2 painéis
                self.main_splitter.setCollapsible(
                    0, False
                )  # Histórico fixo (não recolhível)
                self.main_splitter.setCollapsible(1, False)  # Chat sempre visível

            self.settings_panel_visible = False
            status = "ocultado"

        self.statusBar().showMessage(f"⚙️ Painel de configurações {status}")

    def toggle_theme(self):
        """Alterna tema"""
        config_manager.toggle_theme()
        self.apply_theme()

        self.statusBar().showMessage(
            f"🎨 Tema alterado para {config_manager.ui_config.theme}"
        )
        logger.info(f"Tema alterado para: {config_manager.ui_config.theme}")

    def change_font_size(self, size: int):
        """Altera tamanho da fonte"""
        font = self.chat_display.font()
        font.setPointSize(size)
        self.chat_display.setFont(font)
        self.message_input.setFont(font)

    # Métodos de IA
    def switch_ai_provider(self, provider: str):
        """Troca provedor de IA"""
        provider_map = {
            "gemini": AIProvider.GEMINI,
            "gpt": AIProvider.GPT,
            "claude": AIProvider.CLAUDE,
        }

        if provider in provider_map:
            try:
                ai_manager.switch_provider(provider_map[provider])
                self.current_provider = provider_map[provider]

                # Atualizar interface
                icons = {"gemini": "🔮", "gpt": "🧠", "claude": "🎭"}
                self.provider_label.setText(f"{icons[provider]} {provider.title()}")
                self.status_provider.setText(f"{icons[provider]} {provider.title()}")

                self.statusBar().showMessage(
                    f"🤖 Provedor alterado para {provider.title()}"
                )

            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao trocar provedor:\n{str(e)}")

    def on_provider_changed(self, text: str):
        """Evento de mudança de provedor"""
        provider_map = {"🔮 Gemini": "gemini", "🧠 GPT-4": "gpt", "🎭 Claude": "claude"}

        if text in provider_map:
            self.switch_ai_provider(provider_map[text])

    def on_creativity_changed(self, value: int):
        """Evento de mudança de criatividade"""
        self.current_temperature = value / 100.0
        # Slider removido - tooltip removido
        self.status_temperature.setText(f"🎨 {self.current_temperature:.1f}")

    def update_provider_status(self):
        """Atualiza status dos provedores"""
        try:
            status = ai_manager.get_provider_status()
            logger.info(f"Status dos provedores: {status}")

            # Verificar se os elementos existem antes de atualizar
            if hasattr(self, "gemini_status"):
                self.gemini_status.setText(
                    "✅ Configurado"
                    if status["gemini"]["has_api_key"]
                    else "❌ Não configurado"
                )
            if hasattr(self, "gpt_status"):
                self.gpt_status.setText(
                    "✅ Configurado"
                    if status["gpt"]["has_api_key"]
                    else "❌ Não configurado"
                )
            if hasattr(self, "claude_status"):
                self.claude_status.setText(
                    "✅ Configurado"
                    if status["claude"]["has_api_key"]
                    else "❌ Não configurado"
                )

        except Exception as e:
            logger.error(f"Erro ao atualizar status dos provedores: {e}")

    # Métodos de diálogos
    def open_api_config(self):
        """Abre configuração de APIs"""
        dialog = APIConfigDialog(config_manager, self)
        dialog.config_updated.connect(self.setup_ai_providers)
        dialog.exec()

    def open_creativity_dialog(self):
        """Abre diálogo de criatividade"""
        dialog = CreativityDialog(self.current_temperature, self)
        dialog.creativity_changed.connect(self.set_creativity)
        dialog.exec()

    def set_creativity(self, temperature: float):
        """Define criatividade"""
        self.current_temperature = temperature
        # Slider removido - atualiza apenas status
        self.status_temperature.setText(f"🎨 {temperature:.1f}")

    def open_history_search(self):
        """Abre busca no histórico"""
        if not hasattr(self, "history_search_dialog"):
            from src.ui.history_search_dialog import HistorySearchDialog

            self.history_search_dialog = HistorySearchDialog(self)

        self.history_search_dialog.show()

    # Métodos de ferramentas
    def load_project(self):
        """Carrega projeto e exibe mensagem de confirmação"""
        project_path = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta do Projeto", os.path.expanduser("~")
        )

        if project_path:
            # Chama o carregamento real do projeto
            from src.core.unified_api import SuperChatBot
            from src.core.project_manager import project_manager

            chatbot = SuperChatBot()
            success = chatbot.load_project(project_path)

            # Sincroniza o projeto carregado na instância global para análise
            import asyncio

            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loaded_project = loop.run_until_complete(
                    chatbot.project_manager.engine.load_project(project_path)
                )
                project_manager.current_project = loaded_project
            except Exception as e:
                import logging

                logging.warning(f"Falha ao sincronizar projeto carregado: {e}")

            if success:
                self.statusBar().showMessage(
                    f"✅ Projeto carregado com sucesso: {os.path.basename(project_path)}"
                )
            else:
                self.statusBar().showMessage(
                    f"❌ Erro ao carregar projeto: {os.path.basename(project_path)}"
                )

    def analyze_project_code(self):
        """Analisa código do projeto"""
        if not ai_manager.get_current_provider():
            QMessageBox.warning(self, "Erro", "Configure um provedor de IA primeiro!")
            return

        dialog = ProjectAnalysisDialog(ai_manager.get_current_provider(), self)
        dialog.exec()

    def suggest_project_improvements(self):
        """Sugere melhorias no projeto"""
        self.statusBar().showMessage("💡 Analisando projeto para sugestões...")
        # Implementar lógica

    def ocr_image(self):
        """OCR de imagem"""
        try:
            if not hasattr(self, "ocr_dialog") or self.ocr_dialog is None:
                from src.ui.ocr_dialog import OCRDialog

                self.ocr_dialog = OCRDialog(self)
                self.ocr_dialog.text_extracted.connect(self.add_user_message)

            self.ocr_dialog.show()
            self.ocr_dialog.raise_()
            self.ocr_dialog.activateWindow()
        except Exception as e:
            logger.error(f"Erro ao abrir OCR: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao abrir OCR:\n{str(e)}")

    def process_ocr_analysis(self, text, prompt):
        """Processa análise OCR"""
        full_prompt = (
            f"Analise este texto extraído via OCR:\n\n{text}\n\nPrompt: {prompt}"
        )
        self.add_user_message(full_prompt)

    def analyze_image(self):
        """Analisa imagem"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Imagem", "", "Imagens (*.png *.jpg *.jpeg *.gif *.bmp)"
        )

        if file_path:
            self.statusBar().showMessage(
                f"🖼️ Analisando imagem: {os.path.basename(file_path)}"
            )
            # Implementar análise de imagem

    def export_conversation(self):
        """Exporta conversa"""
        if not self.conversation_history:
            QMessageBox.information(self, "Exportar", "Nenhuma conversa para exportar!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Conversa",
            f"conversa_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Arquivos de Texto (*.txt)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("CONVERSA - ChatBot v3.0\n")
                    f.write(
                        f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                    )
                    f.write("=" * 50 + "\n\n")

                    for msg in self.conversation_history:
                        sender = "USUÁRIO" if msg.is_user else "IA"
                        f.write(f"[{msg.timestamp}] {sender}:\n{msg.content}\n\n")

                self.statusBar().showMessage(
                    f"💾 Conversa exportada: {os.path.basename(file_path)}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")

    def load_conversation(self, item):
        """Carrega conversa do histórico e restaura no chat"""
        # Extrai o nome/título da conversa
        item_text = item.text()
        # Busca pelo título (pode ser melhorado para buscar pelo id)
        conversas = self.history_manager.get_conversations_list()
        for conv in conversas:
            dt = conv["created_at"][:16].replace("T", " ")
            expected_text = f"{conv['title']} ({dt})"
            if item_text == expected_text:
                conversation_id = conv["id"]
                self.current_conversation_id = conversation_id
                conversa = self.history_manager.get_conversation(conversation_id)
                self.conversation_history.clear()
                self.chat_display.clear()
                # Adiciona todas as mensagens da conversa ao chat
                for msg in conversa.get("messages", []):
                    is_user = msg["role"] == "user"
                    self.add_message_to_chat(msg["content"], is_user)
                self.statusBar().showMessage(f"📚 Conversa carregada: {conv['title']}")
                # Sinaliza para a IA que a conversa foi restaurada
                self.ia_conversation_restored = True
                return

    def open_settings_dialog(self):
        """Abre diálogo de configurações"""
        self.open_api_config()

    def show_about(self):
        """Mostra informações sobre o app"""
        QMessageBox.about(
            self,
            "Sobre ChatBot v3.0",
            """
<h2>🤖 ChatBot v3.0</h2>
<p><b>Sistema Completo de IA Conversacional</b></p>

<p><b>Funcionalidades:</b></p>
<ul>
<li>🔮 Suporte para Gemini, GPT-4 e Claude</li>
<li>📁 Análise completa de projetos</li>
<li>📷 OCR e análise de imagens</li>
<li>🎨 Controle de criatividade (0.0-2.0)</li>
<li>📚 Histórico de conversas</li>
<li>🌙 Tema claro/escuro</li>
<li>⌨️ Atalhos de teclado</li>
<li>💾 Exportação de conversas</li>
</ul>

<p><b>Desenvolvido com:</b> PyQt6, Python 3.8+</p>
<p><b>Versão:</b> 3.0.0</p>
            """,
        )

    def closeEvent(self, event):
        """Evento de fechamento"""
        self.save_settings()
        self.history_manager.save_conversations()
        event.accept()


def main():
    """Função principal"""
    app = QApplication(sys.argv)
    app.setApplicationName("ChatBot v3.0")
    app.setApplicationVersion("3.0.0")

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Criar janela principal
    window = AdvancedChatBotGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

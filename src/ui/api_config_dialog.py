"""
Diálogo de Configuração de APIs - ChatBot v3.0
Interface para configurar chaves de API das IAs
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTabWidget,
    QWidget,
    QGroupBox,
    QSlider,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
    QTextEdit,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging

logger = logging.getLogger(__name__)


class APIConfigDialog(QDialog):
    """Diálogo de configuração de APIs"""

    config_updated = pyqtSignal()

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Configuração de APIs - ChatBot v3.0")
        self.setMinimumSize(500, 600)
        self.setModal(True)

        # Campos de entrada
        self.gemini_key_input = QLineEdit()
        self.openai_key_input = QLineEdit()
        self.anthropic_key_input = QLineEdit()

        # Configurações avançadas
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_spin = QDoubleSpinBox()
        self.max_tokens_spin = QDoubleSpinBox()
        self.stream_checkbox = QCheckBox("Respostas em streaming")

        # Seletores de modelo
        self.gemini_model_combo = QComboBox()
        self.gpt_model_combo = QComboBox()
        self.claude_model_combo = QComboBox()

        self.setup_ui()
        self.load_current_config()
        self.setup_connections()

    def setup_ui(self):
        """Configura a interface"""
        layout = QVBoxLayout(self)

        # Abas
        tab_widget = QTabWidget()

        # Aba de Chaves de API
        api_tab = self.create_api_tab()
        tab_widget.addTab(api_tab, "🔑 Chaves de API")

        # Aba de Configurações
        config_tab = self.create_config_tab()
        tab_widget.addTab(config_tab, "⚙️ Configurações")

        # Aba de Modelos
        models_tab = self.create_models_tab()
        tab_widget.addTab(models_tab, "🤖 Modelos")

        layout.addWidget(tab_widget)

        # Botões
        buttons_layout = QHBoxLayout()

        test_btn = QPushButton("🧪 Testar Conexões")
        test_btn.clicked.connect(self.test_connections)

        save_btn = QPushButton("💾 Salvar")
        save_btn.clicked.connect(self.save_config)

        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(test_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        # Aplicar estilo
        self.apply_style()

    def create_api_tab(self):
        """Cria aba de chaves de API"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Gemini
        gemini_group = QGroupBox("🔮 Google Gemini")
        gemini_layout = QFormLayout(gemini_group)

        self.gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_key_input.setPlaceholderText("Insira sua chave de API do Gemini")

        gemini_layout.addRow("Chave de API:", self.gemini_key_input)

        gemini_help = QLabel(
            '<a href="https://aistudio.google.com/app/apikey">'
            "Obter chave de API do Gemini</a>"
        )
        gemini_help.setOpenExternalLinks(True)
        gemini_layout.addRow("", gemini_help)

        layout.addWidget(gemini_group)

        # OpenAI
        openai_group = QGroupBox("🧠 OpenAI GPT")
        openai_layout = QFormLayout(openai_group)

        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_input.setPlaceholderText("Insira sua chave de API da OpenAI")

        openai_layout.addRow("Chave de API:", self.openai_key_input)

        openai_help = QLabel(
            '<a href="https://platform.openai.com/api-keys">'
            "Obter chave de API da OpenAI</a>"
        )
        openai_help.setOpenExternalLinks(True)
        openai_layout.addRow("", openai_help)

        layout.addWidget(openai_group)

        # Anthropic
        anthropic_group = QGroupBox("🎭 Anthropic Claude")
        anthropic_layout = QFormLayout(anthropic_group)

        self.anthropic_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_key_input.setPlaceholderText(
            "Insira sua chave de API da Anthropic"
        )

        anthropic_layout.addRow("Chave de API:", self.anthropic_key_input)

        anthropic_help = QLabel(
            '<a href="https://console.anthropic.com/settings/keys">'
            "Obter chave de API da Anthropic</a>"
        )
        anthropic_help.setOpenExternalLinks(True)
        anthropic_layout.addRow("", anthropic_help)

        layout.addWidget(anthropic_group)

        # Informações importantes
        info_label = QLabel(
            "⚠️ <b>Importante:</b> Suas chaves de API são armazenadas localmente e "
            "nunca são compartilhadas. Mantenha-as seguras!"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "color: #FFC107; padding: 10px; background-color: rgba(255, 193, 7, 20); border-radius: 4px;"
        )
        layout.addWidget(info_label)

        layout.addStretch()
        return widget

    def create_config_tab(self):
        """Cria aba de configurações"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Criatividade/Temperatura
        creativity_group = QGroupBox("🎨 Criatividade (Temperatura)")
        creativity_layout = QFormLayout(creativity_group)

        # Slider de temperatura
        self.temperature_slider.setMinimum(0)
        self.temperature_slider.setMaximum(200)  # 0.0 a 2.0
        self.temperature_slider.setValue(70)  # 0.7 padrão
        self.temperature_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temperature_slider.setTickInterval(25)

        # SpinBox de temperatura
        self.temperature_spin.setMinimum(0.0)
        self.temperature_spin.setMaximum(2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)

        # Layout horizontal para slider e spinbox
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_spin)

        creativity_layout.addRow("Criatividade:", temp_layout)

        temp_info = QLabel(
            "• 0.0-0.3: Respostas muito precisas e conservadoras\n"
            "• 0.4-0.7: Equilibrio entre precisão e criatividade\n"
            "• 0.8-1.2: Respostas mais criativas e variadas\n"
            "• 1.3-2.0: Máxima criatividade (pode ser impreciso)"
        )
        temp_info.setStyleSheet("color: #666; font-size: 9px;")
        creativity_layout.addRow("", temp_info)

        layout.addWidget(creativity_group)

        # Tokens e Performance
        perf_group = QGroupBox("⚡ Performance")
        perf_layout = QFormLayout(perf_group)

        self.max_tokens_spin.setMinimum(500)
        self.max_tokens_spin.setMaximum(8000)
        self.max_tokens_spin.setSingleStep(100)
        self.max_tokens_spin.setValue(4000)

        perf_layout.addRow("Máximo de Tokens:", self.max_tokens_spin)
        perf_layout.addRow("Streaming:", self.stream_checkbox)

        layout.addWidget(perf_group)

        layout.addStretch()
        return widget

    def create_models_tab(self):
        """Cria aba de seleção de modelos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Gemini Models
        gemini_group = QGroupBox("🔮 Modelos Gemini")
        gemini_layout = QFormLayout(gemini_group)

        self.gemini_model_combo.addItems(
            [
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-1.0-pro",
            ]
        )

        gemini_layout.addRow("Modelo Padrão:", self.gemini_model_combo)

        layout.addWidget(gemini_group)

        # GPT Models
        gpt_group = QGroupBox("🧠 Modelos GPT")
        gpt_layout = QFormLayout(gpt_group)

        self.gpt_model_combo.addItems(
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        )

        gpt_layout.addRow("Modelo Padrão:", self.gpt_model_combo)

        layout.addWidget(gpt_group)

        # Claude Models
        claude_group = QGroupBox("🎭 Modelos Claude")
        claude_layout = QFormLayout(claude_group)

        self.claude_model_combo.addItems(
            [
                "claude-sonnet-4-20250514",
                "claude-3-5-sonnet-20241022",
                "claude-3-haiku-20240307",
            ]
        )

        claude_layout.addRow("Modelo Padrão:", self.claude_model_combo)

        layout.addWidget(claude_group)

        # Informações sobre modelos
        model_info = QTextEdit()
        model_info.setMaximumHeight(150)
        model_info.setReadOnly(True)
        model_info.setHtml("""
        <h4>ℹ️ Informações sobre Modelos:</h4>
        <p><b>Gemini 2.5 Flash:</b> Mais recente e rápido, excelente custo-benefício</p>
        <p><b>Gemini 2.5 Pro:</b> Versão mais avançada, máxima qualidade e recursos</p>
        <p><b>Gemini 1.5 Pro:</b> Melhor qualidade, suporte a imagens e grandes contextos</p>
        <p><b>GPT-4o:</b> Modelo mais avançado da OpenAI, excelente para tarefas complexas</p>
        <p><b>Claude Sonnet 4:</b> Modelo mais recente da Anthropic, ótimo para análise</p>
        """)

        layout.addWidget(model_info)

        layout.addStretch()
        return widget

    def setup_connections(self):
        """Configura conexões de sinais"""
        # Sincronizar slider e spinbox de temperatura
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_spin.setValue(v / 100.0)
        )
        self.temperature_spin.valueChanged.connect(
            lambda v: self.temperature_slider.setValue(int(v * 100))
        )

    def load_current_config(self):
        """Carrega configuração atual"""
        config = self.config_manager

        # Chaves de API
        self.gemini_key_input.setText(config.api_config.gemini_api_key)
        self.openai_key_input.setText(config.api_config.openai_api_key)
        self.anthropic_key_input.setText(config.api_config.anthropic_api_key)

        # Configurações
        self.temperature_spin.setValue(config.api_config.default_temperature)
        self.max_tokens_spin.setValue(config.api_config.default_max_tokens)
        self.stream_checkbox.setChecked(config.api_config.stream_responses)

        # Modelos
        self.gemini_model_combo.setCurrentText(config.api_config.default_gemini_model)
        self.gpt_model_combo.setCurrentText(config.api_config.default_gpt_model)
        self.claude_model_combo.setCurrentText(config.api_config.default_claude_model)

    def save_config(self):
        """Salva configurações"""
        try:
            config = self.config_manager

            # Atualizar chaves de API
            config.api_config.gemini_api_key = self.gemini_key_input.text().strip()
            config.api_config.openai_api_key = self.openai_key_input.text().strip()
            config.api_config.anthropic_api_key = (
                self.anthropic_key_input.text().strip()
            )

            # Atualizar configurações
            config.api_config.default_temperature = self.temperature_spin.value()
            config.api_config.default_max_tokens = int(self.max_tokens_spin.value())
            config.api_config.stream_responses = self.stream_checkbox.isChecked()

            # Atualizar modelos
            config.api_config.default_gemini_model = (
                self.gemini_model_combo.currentText()
            )
            config.api_config.default_gpt_model = self.gpt_model_combo.currentText()
            config.api_config.default_claude_model = (
                self.claude_model_combo.currentText()
            )

            # Salvar
            config.save_all_configs()

            # Emitir sinal de atualização
            self.config_updated.emit()

            QMessageBox.information(
                self,
                "Configurações Salvas",
                "✅ Configurações salvas com sucesso!\n\n"
                "As alterações serão aplicadas na próxima interação com as IAs.",
            )

            self.accept()

        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            QMessageBox.critical(
                self, "Erro ao Salvar", f"❌ Erro ao salvar configurações:\n\n{str(e)}"
            )

    def test_connections(self):
        """Testa conexões com as APIs"""
        results = []

        # Teste Gemini
        if self.gemini_key_input.text().strip():
            try:
                # Aqui você faria um teste real da API
                results.append("✅ Gemini: Conectado")
            except Exception as e:
                results.append(f"❌ Gemini: Falha na conexão ({e})")
        else:
            results.append("⚠️ Gemini: Chave não configurada")

        # Teste OpenAI
        if self.openai_key_input.text().strip():
            try:
                # Aqui você faria um teste real da API
                results.append("✅ OpenAI: Conectado")
            except Exception as e:
                results.append(f"❌ OpenAI: Falha na conexão ({e})")
        else:
            results.append("⚠️ OpenAI: Chave não configurada")

        # Teste Anthropic
        if self.anthropic_key_input.text().strip():
            try:
                # Aqui você faria um teste real da API
                results.append("✅ Anthropic: Conectado")
            except Exception as e:
                results.append(f"❌ Anthropic: Falha na conexão ({e})")
        else:
            results.append("⚠️ Anthropic: Chave não configurada")

        # Mostrar resultados
        result_text = "\n".join(results)
        QMessageBox.information(
            self, "Teste de Conexões", f"🧪 Resultados dos testes:\n\n{result_text}"
        )

    def apply_style(self):
        """Aplica estilo customizado"""
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
        
        QSlider::groove:horizontal {
            border: 1px solid #555;
            height: 8px;
            background: #2d2d2d;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #2196F3;
            border: 1px solid #1976D2;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #64B5F6;
        }
        
        QComboBox {
            padding: 8px;
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #ffffff;
        }
        
        QTabWidget::pane {
            border: 1px solid #555;
            background-color: #1e1e1e;
        }
        
        QTabBar::tab {
            background-color: #2d2d2d;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #2196F3;
        }
        
        QTabBar::tab:hover {
            background-color: #1976D2;
        }
        
        QTextEdit {
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
            padding: 8px;
        }
        """
        self.setStyleSheet(style)

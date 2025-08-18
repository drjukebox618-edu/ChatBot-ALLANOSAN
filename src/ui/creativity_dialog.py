"""
Diálogo de Controle de Criatividade - ChatBot v3.0
Interface para ajustar temperatura/criatividade das IAs
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QTextEdit,
    QProgressBar,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class CreativityDialog(QDialog):
    """Diálogo para controle de criatividade"""

    creativity_changed = pyqtSignal(float)

    def __init__(self, current_temperature: float = 0.7, parent=None):
        super().__init__(parent)
        self.current_temperature = current_temperature

        self.setWindowTitle("🎨 Controle de Criatividade - ChatBot v3.0")
        self.setFixedSize(450, 500)
        self.setModal(True)

        # Widgets principais
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_spin = QDoubleSpinBox()
        self.creativity_bar = QProgressBar()
        self.description_text = QTextEdit()
        self.examples_text = QTextEdit()

        self.setup_ui()
        self.setup_connections()
        self.set_temperature(current_temperature)

    def setup_ui(self):
        """Configura interface"""
        layout = QVBoxLayout(self)

        # Título
        title = QLabel("🎨 Ajustar Criatividade da IA")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Grupo de controle principal
        control_group = QGroupBox("🎚️ Nível de Criatividade")
        control_layout = QVBoxLayout(control_group)

        # Slider e valor
        value_layout = QHBoxLayout()

        # Configurar slider
        self.temperature_slider.setMinimum(0)
        self.temperature_slider.setMaximum(200)  # 0.0 a 2.0
        self.temperature_slider.setValue(70)  # 0.7 padrão
        self.temperature_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temperature_slider.setTickInterval(25)

        # Configurar spinbox
        self.temperature_spin.setMinimum(0.0)
        self.temperature_spin.setMaximum(2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)
        self.temperature_spin.setDecimals(1)
        self.temperature_spin.setSuffix(" °")

        value_layout.addWidget(QLabel("Conservador"))
        value_layout.addWidget(self.temperature_slider)
        value_layout.addWidget(QLabel("Criativo"))
        value_layout.addWidget(self.temperature_spin)

        control_layout.addLayout(value_layout)

        # Barra visual de criatividade
        creativity_label = QLabel("Nível Atual:")
        control_layout.addWidget(creativity_label)

        self.creativity_bar.setMinimum(0)
        self.creativity_bar.setMaximum(200)
        self.creativity_bar.setValue(70)
        self.creativity_bar.setTextVisible(False)
        control_layout.addWidget(self.creativity_bar)

        # Labels dos extremos
        extremes_layout = QHBoxLayout()
        extremes_layout.addWidget(QLabel("🔒 Preciso"))
        extremes_layout.addStretch()
        extremes_layout.addWidget(QLabel("🎭 Experimental"))
        control_layout.addLayout(extremes_layout)

        layout.addWidget(control_group)

        # Descrição do nível atual
        desc_group = QGroupBox("📋 Descrição do Nível")
        desc_layout = QVBoxLayout(desc_group)

        self.description_text.setMaximumHeight(100)
        self.description_text.setReadOnly(True)
        desc_layout.addWidget(self.description_text)

        layout.addWidget(desc_group)

        # Exemplos
        examples_group = QGroupBox("💭 Exemplos de Comportamento")
        examples_layout = QVBoxLayout(examples_group)

        self.examples_text.setMaximumHeight(120)
        self.examples_text.setReadOnly(True)
        examples_layout.addWidget(self.examples_text)

        layout.addWidget(examples_group)

        # Presets rápidos
        presets_group = QGroupBox("⚡ Presets Rápidos")
        presets_layout = QHBoxLayout(presets_group)

        conservative_btn = QPushButton("🔒 Conservador\n(0.2)")
        balanced_btn = QPushButton("⚖️ Equilibrado\n(0.7)")
        creative_btn = QPushButton("🎨 Criativo\n(1.2)")
        experimental_btn = QPushButton("🎭 Experimental\n(1.8)")

        conservative_btn.clicked.connect(lambda: self.set_temperature(0.2))
        balanced_btn.clicked.connect(lambda: self.set_temperature(0.7))
        creative_btn.clicked.connect(lambda: self.set_temperature(1.2))
        experimental_btn.clicked.connect(lambda: self.set_temperature(1.8))

        presets_layout.addWidget(conservative_btn)
        presets_layout.addWidget(balanced_btn)
        presets_layout.addWidget(creative_btn)
        presets_layout.addWidget(experimental_btn)

        layout.addWidget(presets_group)

        # Botões
        buttons_layout = QHBoxLayout()

        apply_btn = QPushButton("✅ Aplicar")
        apply_btn.clicked.connect(self.apply_changes)

        reset_btn = QPushButton("🔄 Resetar")
        reset_btn.clicked.connect(lambda: self.set_temperature(0.7))

        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(apply_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        self.apply_style()

    def setup_connections(self):
        """Configura conexões de sinais"""
        # Sincronizar slider e spinbox
        self.temperature_slider.valueChanged.connect(
            lambda v: self.update_from_slider(v)
        )
        self.temperature_spin.valueChanged.connect(
            lambda v: self.update_from_spinbox(v)
        )

    def update_from_slider(self, value: int):
        """Atualiza valor a partir do slider"""
        temperature = value / 100.0
        self.temperature_spin.blockSignals(True)
        self.temperature_spin.setValue(temperature)
        self.temperature_spin.blockSignals(False)
        self.update_display(temperature)

    def update_from_spinbox(self, temperature: float):
        """Atualiza valor a partir do spinbox"""
        value = int(temperature * 100)
        self.temperature_slider.blockSignals(True)
        self.temperature_slider.setValue(value)
        self.temperature_slider.blockSignals(False)
        self.update_display(temperature)

    def set_temperature(self, temperature: float):
        """Define temperatura específica"""
        self.temperature_spin.setValue(temperature)
        self.update_display(temperature)

    def update_display(self, temperature: float):
        """Atualiza displays informativos"""
        # Atualizar barra
        self.creativity_bar.setValue(int(temperature * 100))

        # Atualizar cor da barra baseada no valor
        if temperature <= 0.3:
            color = "#4CAF50"  # Verde (conservador)
        elif temperature <= 0.7:
            color = "#2196F3"  # Azul (equilibrado)
        elif temperature <= 1.2:
            color = "#FF9800"  # Laranja (criativo)
        else:
            color = "#F44336"  # Vermelho (experimental)

        self.creativity_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)

        # Atualizar descrição
        description = self.get_temperature_description(temperature)
        self.description_text.setText(description)

        # Atualizar exemplos
        examples = self.get_temperature_examples(temperature)
        self.examples_text.setText(examples)

    def get_temperature_description(self, temperature: float) -> str:
        """Retorna descrição da temperatura"""
        if temperature <= 0.1:
            return """
🔒 MODO DETERMINÍSTICO (0.0-0.1)
• Respostas sempre iguais para a mesma pergunta
• Máxima precisão e consistência
• Ideal para: Cálculos, programação, dados técnicos
• Pode ser repetitivo
"""
        elif temperature <= 0.3:
            return """
🎯 MODO CONSERVADOR (0.1-0.3)
• Respostas muito precisas e diretas
• Pouca variação criativa
• Ideal para: Análises técnicas, documentação, explicações científicas
• Foco em fatos e precisão
"""
        elif temperature <= 0.7:
            return """
⚖️ MODO EQUILIBRADO (0.3-0.7)
• Bom equilíbrio entre precisão e criatividade
• Respostas úteis e variadas
• Ideal para: Conversas gerais, aprendizado, suporte
• Configuração recomendada para uso geral
"""
        elif temperature <= 1.2:
            return """
🎨 MODO CRIATIVO (0.7-1.2)
• Respostas mais originais e imaginativas
• Boa para brainstorming e ideias
• Ideal para: Escrita criativa, ideias, soluções inovadoras
• Pode ser menos preciso em fatos técnicos
"""
        else:
            return """
🎭 MODO EXPERIMENTAL (1.2-2.0)
• Máxima criatividade e variação
• Respostas muito originais e únicas
• Ideal para: Arte, ficção, experimentação
• ⚠️ Pode gerar conteúdo impreciso ou incoerente
"""

    def get_temperature_examples(self, temperature: float) -> str:
        """Retorna exemplos para a temperatura"""
        if temperature <= 0.1:
            return """
Pergunta: "Como está o tempo?"
Resposta típica: "Não tenho acesso a dados meteorológicos em tempo real."

Características:
• Sempre a mesma resposta
• Muito factual
• Zero criatividade
"""
        elif temperature <= 0.3:
            return """
Pergunta: "Como posso melhorar meu código Python?"
Resposta típica: "Use PEP 8, docstrings, type hints e testes unitários."

Características:
• Direto e técnico
• Foco em melhores práticas
• Pouca elaboração criativa
"""
        elif temperature <= 0.7:
            return """
Pergunta: "Explique machine learning"
Resposta típica: "Machine learning é um subcampo da IA onde algoritmos aprendem padrões dos dados para fazer predições..."

Características:
• Explicações claras e didáticas
• Exemplos relevantes
• Bom equilíbrio informativo
"""
        elif temperature <= 1.2:
            return """
Pergunta: "Como resolver problemas criativamente?"
Resposta típica: "Imagine seu problema como um quebra-cabeças 🧩. Tente abordagens não convencionais..."

Características:
• Metáforas e analogias criativas
• Múltiplas perspectivas
• Sugestões inovadoras
"""
        else:
            return """
Pergunta: "O que é programação?"
Resposta típica: "Programação é como ser um mago digital 🧙‍♂️ que sussurra encantamentos em linguagens místicas..."

Características:
• Muito imaginativo e metafórico
• Respostas únicas e surpreendentes
• Pode ser inconsistente
"""

    def apply_changes(self):
        """Aplica as mudanças"""
        temperature = self.temperature_spin.value()
        self.creativity_changed.emit(temperature)
        self.accept()

        logger.info(f"Criatividade alterada para: {temperature}")

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
        
        QPushButton {
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            background-color: #2196F3;
            color: white;
            font-weight: bold;
            min-height: 20px;
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
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4CAF50, stop:0.25 #2196F3, 
                stop:0.75 #FF9800, stop:1 #F44336);
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #ffffff;
            border: 2px solid #2196F3;
            width: 20px;
            margin: -6px 0;
            border-radius: 10px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #64B5F6;
            border-color: #1976D2;
        }
        
        QDoubleSpinBox {
            padding: 6px;
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
            min-width: 60px;
        }
        
        QProgressBar {
            border: 1px solid #555;
            border-radius: 4px;
            text-align: center;
            background-color: #2d2d2d;
            height: 20px;
        }
        
        QProgressBar::chunk {
            background-color: #2196F3;
            border-radius: 3px;
        }
        
        QTextEdit {
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
            padding: 8px;
            font-size: 9px;
        }
        
        QLabel {
            color: #ffffff;
        }
        
        QFrame[frameShape="4"] {
            color: #555;
        }
        """
        self.setStyleSheet(style)

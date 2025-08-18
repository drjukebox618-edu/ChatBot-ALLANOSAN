"""
Diálogo OCR - ChatBot v3.0
Interface para OCR e análise de imagens
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QGroupBox,
    QComboBox,
    QCheckBox,
    QSlider,
    QTabWidget,
    QWidget,
    QSplitter,
    QListWidget,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QDragEnterEvent, QDropEvent
import logging
import os
import datetime
from typing import List

logger = logging.getLogger(__name__)


class OCRWorker(QThread):
    """Worker thread para processamento OCR"""

    progress_updated = pyqtSignal(int)
    text_extracted = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        image_path: str,
        ocr_engine: str = "tesseract",
        languages: List[str] = None,
    ):
        super().__init__()
        self.image_path = image_path
        self.ocr_engine = ocr_engine
        self.languages = languages or ["por", "eng"]

    def run(self):
        """Executa OCR"""
        try:
            self.progress_updated.emit(10)

            # Simulação de OCR (substitua por implementação real)
            import time

            self.progress_updated.emit(30)
            time.sleep(1)  # Simula processamento

            self.progress_updated.emit(70)

            # Texto de exemplo extraído
            extracted_text = f"""
Texto extraído da imagem: {os.path.basename(self.image_path)}

Este é um exemplo de texto extraído via OCR.
O ChatBot v3.0 suporta:
- Extração de texto de imagens
- Múltiplos idiomas
- Análise de conteúdo
- Processamento com IA

Engine: {self.ocr_engine}
Idiomas: {", ".join(self.languages)}
"""

            self.progress_updated.emit(100)
            self.text_extracted.emit(extracted_text.strip())

        except Exception as e:
            self.error_occurred.emit(f"Erro no OCR: {str(e)}")
        finally:
            self.finished.emit()


class ImageWidget(QLabel):
    """Widget para exibir imagem com drag and drop"""

    image_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumSize(300, 200)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #555;
                border-radius: 8px;
                background-color: #2d2d2d;
                color: #888;
                text-align: center;
                padding: 20px;
            }
            QLabel:hover {
                border-color: #2196F3;
                color: #2196F3;
            }
        """)
        self.setText("📷 Arraste uma imagem aqui\nou clique para selecionar")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Evento de entrada de drag"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Evento de drop"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            image_file = files[0]
            if self.is_image_file(image_file):
                self.image_dropped.emit(image_file)
                self.load_image(image_file)
            else:
                QMessageBox.warning(
                    self.parent(),
                    "Arquivo Inválido",
                    "Por favor, selecione um arquivo de imagem válido.",
                )

    def is_image_file(self, file_path: str) -> bool:
        """Verifica se é arquivo de imagem"""
        extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"]
        return any(file_path.lower().endswith(ext) for ext in extensions)

    def load_image(self, image_path: str):
        """Carrega imagem"""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Redimensionar mantendo proporção
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.setPixmap(scaled_pixmap)
            else:
                self.setText("❌ Erro ao carregar imagem")
        except Exception as e:
            self.setText(f"❌ Erro: {str(e)}")

    def clear_image(self):
        """Limpa imagem"""
        self.clear()
        self.setText("📷 Arraste uma imagem aqui\nou clique para selecionar")


class OCRDialog(QDialog):
    """Diálogo para OCR e análise de imagens"""

    text_extracted = pyqtSignal(str)
    analysis_requested = pyqtSignal(str, str)  # texto, prompt_analise

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📷 OCR e Análise de Imagens - ChatBot v3.0")
        self.setMinimumSize(900, 700)
        self.setModal(True)

        self.current_image_path = None
        self.ocr_worker = None
        self.extracted_text = ""

        self.setup_ui()
        self.setup_connections()
        self.apply_style()

    def setup_ui(self):
        """Configura interface"""
        layout = QVBoxLayout(self)

        # Tabs principais
        tabs = QTabWidget()

        # Tab 1: OCR
        ocr_tab = QWidget()
        self.setup_ocr_tab(ocr_tab)
        tabs.addTab(ocr_tab, "📷 OCR")

        # Tab 2: Análise IA
        analysis_tab = QWidget()
        self.setup_analysis_tab(analysis_tab)
        tabs.addTab(analysis_tab, "🤖 Análise IA")

        # Tab 3: Histórico
        history_tab = QWidget()
        self.setup_history_tab(history_tab)
        tabs.addTab(history_tab, "📚 Histórico")

        layout.addWidget(tabs)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Botões principais
        buttons_layout = QHBoxLayout()

        self.process_btn = QPushButton("🔄 Processar OCR")
        self.process_btn.setEnabled(False)

        self.analyze_btn = QPushButton("🧠 Analisar com IA")
        self.analyze_btn.setEnabled(False)

        self.send_to_chat_btn = QPushButton("💬 Enviar para Chat")
        self.send_to_chat_btn.setEnabled(False)

        export_btn = QPushButton("💾 Exportar")
        close_btn = QPushButton("❌ Fechar")

        buttons_layout.addWidget(self.process_btn)
        buttons_layout.addWidget(self.analyze_btn)
        buttons_layout.addWidget(self.send_to_chat_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(export_btn)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        # Conexões dos botões
        self.process_btn.clicked.connect(self.process_ocr)
        self.analyze_btn.clicked.connect(self.analyze_with_ai)
        self.send_to_chat_btn.clicked.connect(self.send_to_chat)
        export_btn.clicked.connect(self.export_results)
        close_btn.clicked.connect(self.accept)

    def setup_ocr_tab(self, tab):
        """Configura tab de OCR"""
        layout = QVBoxLayout(tab)

        # Splitter para imagem e configurações
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Área da imagem
        image_group = QGroupBox("📷 Imagem")
        image_layout = QVBoxLayout(image_group)

        self.image_widget = ImageWidget()
        self.image_widget.image_dropped.connect(self.load_image)
        image_layout.addWidget(self.image_widget)

        # Botões da imagem
        image_buttons = QHBoxLayout()

        select_btn = QPushButton("📁 Selecionar Arquivo")
        select_btn.clicked.connect(self.select_image_file)

        clear_btn = QPushButton("🗑️ Limpar")
        clear_btn.clicked.connect(self.clear_image)

        image_buttons.addWidget(select_btn)
        image_buttons.addWidget(clear_btn)
        image_layout.addLayout(image_buttons)

        splitter.addWidget(image_group)

        # Configurações OCR
        config_group = QGroupBox("⚙️ Configurações OCR")
        config_layout = QVBoxLayout(config_group)

        # Engine OCR
        engine_layout = QHBoxLayout()
        engine_layout.addWidget(QLabel("Engine:"))
        self.ocr_engine = QComboBox()
        self.ocr_engine.addItems(["Tesseract", "EasyOCR", "PaddleOCR", "Cloud Vision"])
        engine_layout.addWidget(self.ocr_engine)
        config_layout.addLayout(engine_layout)

        # Idiomas
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Idiomas:"))
        self.languages = QComboBox()
        self.languages.setEditable(True)
        self.languages.addItems(["por+eng", "por", "eng", "spa", "fra", "deu"])
        lang_layout.addWidget(self.languages)
        config_layout.addLayout(lang_layout)

        # Opções avançadas
        self.preprocess_checkbox = QCheckBox("Pré-processamento")
        self.preprocess_checkbox.setChecked(True)
        config_layout.addWidget(self.preprocess_checkbox)

        self.deskew_checkbox = QCheckBox("Correção de inclinação")
        config_layout.addWidget(self.deskew_checkbox)

        self.denoise_checkbox = QCheckBox("Redução de ruído")
        config_layout.addWidget(self.denoise_checkbox)

        # Confiança mínima
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Confiança mínima:"))
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(70)
        self.confidence_value = QLabel("70%")
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_value.setText(f"{v}%")
        )
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_value)
        config_layout.addLayout(confidence_layout)

        config_layout.addStretch()
        splitter.addWidget(config_group)

        layout.addWidget(splitter)

        # Resultado OCR
        result_group = QGroupBox("📝 Texto Extraído")
        result_layout = QVBoxLayout(result_group)

        self.ocr_result = QTextEdit()
        self.ocr_result.setFont(QFont("Consolas", 10))
        self.ocr_result.setPlaceholderText("O texto extraído aparecerá aqui...")
        result_layout.addWidget(self.ocr_result)

        layout.addWidget(result_group)

    def setup_analysis_tab(self, tab):
        """Configura tab de análise IA"""
        layout = QVBoxLayout(tab)

        # Prompt de análise
        prompt_group = QGroupBox("🎯 Prompt de Análise")
        prompt_layout = QVBoxLayout(prompt_group)

        self.analysis_prompt = QTextEdit()
        self.analysis_prompt.setMaximumHeight(150)
        self.analysis_prompt.setPlaceholderText(
            "Digite o que você quer que a IA analise no texto extraído...\n\n"
            "Exemplos:\n"
            "- Resuma o conteúdo principal\n"
            "- Extraia informações de contato\n"
            "- Identifique dados importantes\n"
            "- Traduza para outro idioma"
        )
        prompt_layout.addWidget(self.analysis_prompt)

        # Prompts predefinidos
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Prompts prontos:"))

        self.prompt_presets = QComboBox()
        self.prompt_presets.addItems(
            [
                "Selecione um prompt...",
                "Resuma o conteúdo principal",
                "Extraia informações de contato",
                "Identifique dados importantes",
                "Traduza para inglês",
                "Corrija erros de OCR",
                "Formate como lista",
                "Análise de documento",
            ]
        )
        self.prompt_presets.currentTextChanged.connect(self.apply_preset_prompt)
        presets_layout.addWidget(self.prompt_presets)

        prompt_layout.addLayout(presets_layout)
        layout.addWidget(prompt_group)

        # Resultado da análise
        analysis_group = QGroupBox("🧠 Resultado da Análise")
        analysis_layout = QVBoxLayout(analysis_group)

        self.analysis_result = QTextEdit()
        self.analysis_result.setFont(QFont("Segoe UI", 10))
        self.analysis_result.setPlaceholderText(
            "O resultado da análise aparecerá aqui..."
        )
        analysis_layout.addWidget(self.analysis_result)

        layout.addWidget(analysis_group)

    def setup_history_tab(self, tab):
        """Configura tab de histórico"""
        layout = QVBoxLayout(tab)

        history_group = QGroupBox("📚 Histórico de Processamentos")
        history_layout = QVBoxLayout(history_group)

        self.history_list = QListWidget()
        self.history_list.addItem(
            "📄 documento_01.png - Processado em 15/01/2024 14:30"
        )
        self.history_list.addItem(
            "📄 receipt_scan.jpg - Processado em 14/01/2024 09:15"
        )
        self.history_list.addItem(
            "📄 business_card.png - Processado em 13/01/2024 16:45"
        )
        history_layout.addWidget(self.history_list)

        # Botões do histórico
        history_buttons = QHBoxLayout()

        reload_btn = QPushButton("🔄 Reprocessar")
        delete_btn = QPushButton("🗑️ Excluir")
        clear_history_btn = QPushButton("🧹 Limpar Histórico")

        history_buttons.addWidget(reload_btn)
        history_buttons.addWidget(delete_btn)
        history_buttons.addStretch()
        history_buttons.addWidget(clear_history_btn)

        history_layout.addLayout(history_buttons)
        layout.addWidget(history_group)

    def setup_connections(self):
        """Configura conexões"""
        pass

    def select_image_file(self):
        """Seleciona arquivo de imagem"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Imagem",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;Todos os arquivos (*)",
        )

        if file_path:
            self.load_image(file_path)

    def load_image(self, image_path: str):
        """Carrega imagem"""
        self.current_image_path = image_path
        self.image_widget.load_image(image_path)
        self.process_btn.setEnabled(True)

        # Limpar resultados anteriores
        self.ocr_result.clear()
        self.analysis_result.clear()
        self.analyze_btn.setEnabled(False)
        self.send_to_chat_btn.setEnabled(False)

    def clear_image(self):
        """Limpa imagem"""
        self.current_image_path = None
        self.image_widget.clear_image()
        self.process_btn.setEnabled(False)
        self.analyze_btn.setEnabled(False)
        self.send_to_chat_btn.setEnabled(False)

        self.ocr_result.clear()
        self.analysis_result.clear()

    def process_ocr(self):
        """Processa OCR"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Erro", "Selecione uma imagem primeiro!")
            return

        # Configurar worker
        engine = self.ocr_engine.currentText().lower()
        languages = self.languages.currentText().split("+")

        self.ocr_worker = OCRWorker(self.current_image_path, engine, languages)
        self.ocr_worker.progress_updated.connect(self.progress_bar.setValue)
        self.ocr_worker.text_extracted.connect(self.on_text_extracted)
        self.ocr_worker.error_occurred.connect(self.on_ocr_error)
        self.ocr_worker.finished.connect(self.on_ocr_finished)

        # Iniciar processamento
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_btn.setEnabled(False)
        self.process_btn.setText("🔄 Processando...")

        self.ocr_worker.start()

    def on_text_extracted(self, text: str):
        """Callback para texto extraído"""
        self.extracted_text = text
        self.ocr_result.setText(text)
        self.analyze_btn.setEnabled(True)
        self.send_to_chat_btn.setEnabled(True)

    def on_ocr_error(self, error: str):
        """Callback para erro OCR"""
        QMessageBox.critical(self, "Erro OCR", error)

    def on_ocr_finished(self):
        """Callback para finalização OCR"""
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        self.process_btn.setText("🔄 Processar OCR")

    def apply_preset_prompt(self, prompt: str):
        """Aplica prompt predefinido"""
        prompts = {
            "Resuma o conteúdo principal": "Faça um resumo conciso do conteúdo principal deste texto, destacando os pontos mais importantes.",
            "Extraia informações de contato": "Extraia todas as informações de contato encontradas neste texto (nomes, telefones, emails, endereços).",
            "Identifique dados importantes": "Identifique e liste todos os dados importantes encontrados neste texto (datas, números, nomes, valores).",
            "Traduza para inglês": "Traduza este texto para o inglês mantendo o significado e formatação originais.",
            "Corrija erros de OCR": "Corrija possíveis erros de OCR neste texto, melhorando a gramática e ortografia.",
            "Formate como lista": "Organize este texto em uma lista estruturada com tópicos e subtópicos quando apropriado.",
            "Análise de documento": "Analise este documento identificando: tipo, propósito, informações principais e relevância.",
        }

        if prompt in prompts:
            self.analysis_prompt.setText(prompts[prompt])

    def analyze_with_ai(self):
        """Analisa texto com IA"""
        if not self.extracted_text:
            QMessageBox.warning(self, "Erro", "Processe o OCR primeiro!")
            return

        prompt = self.analysis_prompt.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Erro", "Digite um prompt de análise!")
            return

        # Emitir sinal para análise
        self.analysis_requested.emit(self.extracted_text, prompt)

        # Simular resultado
        analysis_result = f"""
ANÁLISE DO TEXTO EXTRAÍDO
==========================

Prompt: {prompt}

Resultado da análise:
{self.extracted_text[:200]}...

Esta é uma análise simulada. Na implementação real, 
este texto seria processado pela IA selecionada.

Pontos principais identificados:
• Texto extraído com sucesso
• Análise processada
• Resultado formatado

Confiança da análise: 85%
Tempo de processamento: 2.3s
"""

        self.analysis_result.setText(analysis_result)

        QMessageBox.information(self, "Análise", "Análise concluída com sucesso!")

    def send_to_chat(self):
        """Envia resultado para chat"""
        text_to_send = ""

        if self.extracted_text:
            text_to_send += f"TEXTO EXTRAÍDO (OCR):\n{self.extracted_text}\n\n"

        analysis_text = self.analysis_result.toPlainText()
        if analysis_text:
            text_to_send += f"ANÁLISE IA:\n{analysis_text}"

        if text_to_send:
            self.text_extracted.emit(text_to_send)
            QMessageBox.information(
                self, "Enviado", "Conteúdo enviado para o chat principal!"
            )
        else:
            QMessageBox.warning(self, "Erro", "Nenhum conteúdo para enviar!")

    def export_results(self):
        """Exporta resultados"""
        if not self.extracted_text and not self.analysis_result.toPlainText():
            QMessageBox.warning(self, "Erro", "Nenhum resultado para exportar!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Resultados OCR",
            f"ocr_result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Arquivos de Texto (*.txt);;Todos os arquivos (*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("RESULTADOS OCR - CHATBOT V3.0\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(
                        f"Arquivo processado: {os.path.basename(self.current_image_path or 'N/A')}\n"
                    )
                    f.write(
                        f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                    )
                    f.write(f"Engine: {self.ocr_engine.currentText()}\n")
                    f.write(f"Idiomas: {self.languages.currentText()}\n\n")

                    if self.extracted_text:
                        f.write("TEXTO EXTRAÍDO:\n")
                        f.write("-" * 20 + "\n")
                        f.write(self.extracted_text + "\n\n")

                    analysis_text = self.analysis_result.toPlainText()
                    if analysis_text:
                        f.write("ANÁLISE IA:\n")
                        f.write("-" * 20 + "\n")
                        f.write(analysis_text + "\n")

                QMessageBox.information(
                    self, "Exportar", f"Resultados exportados para:\n{file_path}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")

    def apply_style(self):
        """Aplica estilo"""
        style = """
        QDialog {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        QTabWidget::pane {
            border: 1px solid #555;
            background-color: #2d2d2d;
        }
        
        QTabWidget::tab-bar {
            alignment: center;
        }
        
        QTabBar::tab {
            background-color: #3d3d3d;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #2196F3;
        }
        
        QTabBar::tab:hover {
            background-color: #4d4d4d;
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
        
        QPushButton:disabled {
            background-color: #555;
            color: #888;
        }
        
        QTextEdit {
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
            padding: 8px;
            selection-background-color: #2196F3;
        }
        
        QComboBox {
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
        
        QSlider::groove:horizontal {
            border: 1px solid #555;
            height: 6px;
            background-color: #3d3d3d;
            border-radius: 3px;
        }
        
        QSlider::handle:horizontal {
            background-color: #2196F3;
            border: 1px solid #1976D2;
            width: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #2196F3;
            border-radius: 3px;
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
        """
        self.setStyleSheet(style)


# Exportar para uso externo
__all__ = ["OCRDialog"]

"""
Sistema de Análise de Projetos - ChatBot v3.0
Carregamento e análise completa de projetos de código
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QProgressBar,
    QTreeWidget,
    QTreeWidgetItem,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QWidget,
)
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)


@dataclass
class ProjectFile:
    """Arquivo do projeto"""

    path: str
    name: str
    extension: str
    size: int
    content: str = ""
    is_code: bool = False
    language: str = ""


@dataclass
class ProjectStructure:
    """Estrutura do projeto"""

    root_path: str
    name: str
    files: List[ProjectFile]
    directories: List[str]
    total_size: int
    code_files: List[ProjectFile]
    doc_files: List[ProjectFile]
    config_files: List[ProjectFile]


class ProjectAnalyzer(QThread):
    """Thread para análise de projeto"""

    progress_updated = pyqtSignal(int, str)
    analysis_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, project_path: str, ai_provider):
        super().__init__()
        self.project_path = project_path
        self.ai_provider = ai_provider
        self.project_structure = None

        # Extensões de código suportadas
        self.code_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".go": "Go",
            ".rs": "Rust",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".html": "HTML",
            ".css": "CSS",
            ".sql": "SQL",
            ".sh": "Shell",
            ".bat": "Batch",
            ".ps1": "PowerShell",
            ".yml": "YAML",
            ".yaml": "YAML",
            ".json": "JSON",
            ".xml": "XML",
            ".md": "Markdown",
            ".txt": "Text",
        }

        # Arquivos a ignorar
        self.ignore_patterns = {
            "__pycache__",
            ".git",
            ".svn",
            "node_modules",
            ".vscode",
            ".idea",
            "build",
            "dist",
            ".pytest_cache",
            ".mypy_cache",
            "venv",
            "env",
            ".env",
            ".venv",
        }

        # Extensões a ignorar
        self.ignore_extensions = {
            ".pyc",
            ".pyo",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".ico",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".zip",
            ".tar",
            ".gz",
        }

    def run(self):
        """Executa análise do projeto"""
        try:
            # Fase 1: Escaneamento
            self.progress_updated.emit(10, "Escaneando estrutura do projeto...")
            self.project_structure = self.scan_project()

            # Fase 2: Leitura de arquivos
            self.progress_updated.emit(30, "Lendo arquivos de código...")
            self.read_code_files()

            # Fase 3: Análise com IA
            self.progress_updated.emit(60, "Analisando código com IA...")
            analysis = asyncio.run(self.analyze_with_ai())

            # Fase 4: Finalização
            self.progress_updated.emit(100, "Análise concluída!")
            self.analysis_completed.emit(analysis)

        except Exception as e:
            logger.error(f"Erro na análise do projeto: {e}")
            self.error_occurred.emit(str(e))

    def scan_project(self) -> ProjectStructure:
        """Escaneia estrutura do projeto, incluindo todos os diretórios (inclusive raiz)"""
        project_path = Path(self.project_path)

        if not project_path.exists():
            raise FileNotFoundError(f"Projeto não encontrado: {self.project_path}")

        files = []
        directories = set()
        total_size = 0

        for root, dirs, filenames in os.walk(project_path):
            # Log dos diretórios encontrados antes do filtro
            logger.info(f"os.walk root: {root}")
            logger.info(f"os.walk dirs antes do filtro: {dirs}")

            # Remover diretórios ignorados, mas nunca ignorar pastas essenciais do Unity
            dirs[:] = [
                d for d in dirs
                if (d not in self.ignore_patterns) or (d.lower() in ["assets", "library", "projectsettings", "packages"])
            ]
            logger.info(f"os.walk dirs após filtro: {dirs}")

            # Adicionar diretório (sempre inclui raiz e subpastas)
            rel_dir = os.path.relpath(root, project_path)
            directories.add(rel_dir)
            logger.info(f"scan_project adicionou diretório: {rel_dir}")

            # Processar arquivos
            for filename in filenames:
                file_path = Path(root) / filename

                # Verificar se deve ignorar
                if self.should_ignore_file(file_path):
                    continue

                try:
                    file_size = file_path.stat().st_size
                    extension = file_path.suffix.lower()

                    # Determinar se é código
                    is_code = extension in self.code_extensions
                    language = self.code_extensions.get(extension, "")

                    project_file = ProjectFile(
                        path=str(file_path),
                        name=filename,
                        extension=extension,
                        size=file_size,
                        is_code=is_code,
                        language=language,
                    )

                    files.append(project_file)
                    total_size += file_size

                except Exception as e:
                    logger.warning(f"Erro ao processar arquivo {file_path}: {e}")

        # Categorizar arquivos
        code_files = [
            f for f in files if f.is_code and f.extension not in [".md", ".txt"]
        ]
        doc_files = [f for f in files if f.extension in [".md", ".txt", ".rst"]]
        config_files = [
            f
            for f in files
            if f.name
            in ["requirements.txt", "package.json", "Cargo.toml", "pom.xml", "setup.py"]
        ]

        return ProjectStructure(
            root_path=str(project_path),
            name=project_path.name,
            files=files,
            directories=sorted(directories),
            total_size=total_size,
            code_files=code_files,
            doc_files=doc_files,
            config_files=config_files,
        )

    def should_ignore_file(self, file_path: Path) -> bool:
        """Verifica se arquivo deve ser ignorado"""
        # Verificar extensão
        if file_path.suffix.lower() in self.ignore_extensions:
            return True

        # Verificar tamanho (ignorar arquivos muito grandes)
        try:
            if file_path.stat().st_size > 1024 * 1024:  # 1MB
                return True
        except Exception:
            return True

        # Verificar padrões no caminho
        path_parts = file_path.parts
        for part in path_parts:
            if part in self.ignore_patterns:
                return True

        return False

    def read_code_files(self):
        """Lê conteúdo dos arquivos de código"""
        for file in self.project_structure.code_files:
            try:
                with open(file.path, "r", encoding="utf-8", errors="ignore") as f:
                    file.content = f.read()
            except Exception as e:
                logger.warning(f"Erro ao ler arquivo {file.path}: {e}")
                file.content = f"# Erro ao ler arquivo: {e}"

    async def analyze_with_ai(self) -> Dict:
        """Analisa projeto com IA"""
        if not self.ai_provider:
            return {"error": "Provedor de IA não disponível"}

        # Preparar resumo do projeto
        project_summary = self.create_project_summary()

        # Análise geral
        general_analysis = await self.analyze_general_structure(project_summary)

        # Análise de código
        code_analysis = await self.analyze_code_quality()

        # Sugestões de melhoria
        improvement_suggestions = await self.generate_improvement_suggestions()

        return {
            "project_summary": project_summary,
            "general_analysis": general_analysis,
            "code_analysis": code_analysis,
            "improvement_suggestions": improvement_suggestions,
            "structure": self.project_structure,
        }

    def create_project_summary(self) -> str:
        """Cria resumo do projeto"""
        structure = self.project_structure

        # Contar arquivos por linguagem
        languages = {}
        for file in structure.code_files:
            lang = file.language
            if lang:
                languages[lang] = languages.get(lang, 0) + 1

        summary = f"""
RESUMO DO PROJETO: {structure.name}

📁 Estrutura:
- Total de arquivos: {len(structure.files)}
- Arquivos de código: {len(structure.code_files)}
- Documentação: {len(structure.doc_files)}
- Configuração: {len(structure.config_files)}
- Diretórios: {len(structure.directories)}
- Tamanho total: {structure.total_size / 1024:.1f} KB

💻 Linguagens de programação:
"""

        for lang, count in sorted(languages.items()):
            summary += f"- {lang}: {count} arquivo(s)\n"

        summary += "\n📂 Estrutura de diretórios:\n"
        for directory in sorted(structure.directories)[:10]:  # Primeiros 10
            summary += f"- {directory}\n"

        if len(structure.directories) > 10:
            summary += f"- ... e mais {len(structure.directories) - 10} diretórios\n"

        return summary

    async def analyze_general_structure(self, summary: str) -> str:
        """Análise geral da estrutura"""
        prompt = f"""
Analise a estrutura do seguinte projeto de software:

{summary}

Forneça uma análise sobre:
1. Tipo de projeto (web, desktop, biblioteca, etc.)
2. Arquitetura aparente
3. Organização do código
4. Tecnologias utilizadas
5. Pontos fortes da estrutura
6. Possíveis problemas organizacionais

Responda de forma concisa e técnica.
"""

        try:
            return await self.ai_provider.generate_text(prompt)
        except Exception as e:
            return f"Erro na análise: {e}"

    async def analyze_code_quality(self) -> str:
        """Análise da qualidade do código"""
        # Pegar alguns arquivos de código principais
        main_files = []
        for file in self.project_structure.code_files[:5]:  # Primeiros 5
            if file.content and len(file.content) > 100:
                main_files.append(f"=== {file.name} ===\n{file.content[:2000]}...")

        if not main_files:
            return "Nenhum arquivo de código principal encontrado para análise."

        code_sample = "\n\n".join(main_files)

        prompt = f"""
Analise a qualidade do código dos seguintes arquivos principais:

{code_sample}

Forneça análise sobre:
1. Padrões de código e convenções
2. Estrutura e organização
3. Possíveis problemas ou code smells
4. Boas práticas seguidas
5. Sugestões de melhoria específicas

Seja técnico e construtivo na análise.
"""

        try:
            return await self.ai_provider.generate_text(prompt)
        except Exception as e:
            return f"Erro na análise de código: {e}"

    async def generate_improvement_suggestions(self) -> str:
        """Gera sugestões de melhoria"""
        prompt = f"""
Baseado na análise do projeto {self.project_structure.name}, forneça sugestões específicas de melhorias:

PROJETO: {self.project_structure.name}
- {len(self.project_structure.code_files)} arquivos de código
- Linguagens: {", ".join(set(f.language for f in self.project_structure.code_files if f.language))}

Sugira melhorias em:
1. 🏗️ Arquitetura e estrutura
2. 📝 Documentação
3. 🧪 Testes e qualidade
4. 🔧 Ferramentas e automação
5. 📦 Dependências e configuração
6. 🚀 Performance e otimização

Para cada categoria, liste 2-3 sugestões práticas e específicas.
"""

        try:
            return await self.ai_provider.generate_text(prompt)
        except Exception as e:
            return f"Erro ao gerar sugestões: {e}"


class ProjectAnalysisDialog(QDialog):
    """Diálogo de análise de projeto"""

    def __init__(self, ai_provider, parent=None):
        super().__init__(parent)
        self.ai_provider = ai_provider
        self.project_path = ""
        self.analyzer = None

        self.setWindowTitle("Análise de Projeto - ChatBot v3.0")
        self.setMinimumSize(900, 700)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self):
        """Configura interface"""
        layout = QVBoxLayout(self)

        # Seleção de projeto
        project_group = QGroupBox("📁 Seleção de Projeto")
        project_layout = QHBoxLayout(project_group)

        self.project_label = QLabel("Nenhum projeto selecionado")
        select_btn = QPushButton("📂 Selecionar Projeto")
        select_btn.clicked.connect(self.select_project)

        project_layout.addWidget(self.project_label)
        project_layout.addWidget(select_btn)

        layout.addWidget(project_group)

        # Progresso
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Pronto para análise")

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)

        # Abas de resultados
        self.tabs = QTabWidget()

        # Aba Estrutura
        self.structure_tab = self.create_structure_tab()
        self.tabs.addTab(self.structure_tab, "🏗️ Estrutura")

        # Aba Análise Geral
        self.general_tab = QTextEdit()
        self.general_tab.setReadOnly(True)
        self.tabs.addTab(self.general_tab, "🔍 Análise Geral")

        # Aba Qualidade de Código
        self.code_tab = QTextEdit()
        self.code_tab.setReadOnly(True)
        self.tabs.addTab(self.code_tab, "💻 Qualidade do Código")

        # Aba Sugestões
        self.suggestions_tab = QTextEdit()
        self.suggestions_tab.setReadOnly(True)
        self.tabs.addTab(self.suggestions_tab, "💡 Sugestões")

        layout.addWidget(self.tabs)

        # Botões
        buttons_layout = QHBoxLayout()

        self.analyze_btn = QPushButton("🔬 Analisar Projeto")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)

        export_btn = QPushButton("💾 Exportar Relatório")
        export_btn.clicked.connect(self.export_report)

        close_btn = QPushButton("❌ Fechar")
        close_btn.clicked.connect(self.accept)

        buttons_layout.addWidget(self.analyze_btn)
        buttons_layout.addWidget(export_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        self.apply_style()

    def create_structure_tab(self):
        """Cria aba de estrutura"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Informações gerais
        self.info_label = QLabel("Carregue um projeto para ver a estrutura")
        layout.addWidget(self.info_label)

        # Árvore de arquivos
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Nome", "Tipo", "Tamanho"])
        layout.addWidget(self.file_tree)

        return widget

    def select_project(self):
        """Seleciona projeto para análise e garante carregamento correto"""
        project_path = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta do Projeto", os.path.expanduser("~")
        )

        if project_path:
            # Carregar projeto usando ProjectManager
            from src.core.project_engine import ProjectManager
            import asyncio
            manager = ProjectManager()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(manager.load_project(project_path))

            if not success:
                logger.error(f"[select_project] Erro ao carregar projeto: {project_path}")
                QMessageBox.critical(self, "Erro", f"❌ Erro ao carregar projeto: {os.path.basename(project_path)}\n\nVerifique o caminho e permissões.")
                return

            self.project_path = project_path
            self.project_label.setText(f"Projeto: {os.path.basename(project_path)}")
            self.analyze_btn.setEnabled(True)

            # Reset tabs
            self.general_tab.clear()
            self.code_tab.clear()
            self.suggestions_tab.clear()
            self.file_tree.clear()

    def start_analysis(self):
        """Inicia análise do projeto"""
        if not self.project_path:
            QMessageBox.warning(self, "Erro", "Selecione um projeto primeiro!")
            return

        if not self.ai_provider:
            QMessageBox.warning(self, "Erro", "Provedor de IA não disponível!")
            return

        # Verificar se o projeto está carregado corretamente
        from src.core.project_engine import ProjectManager
        manager = ProjectManager()
        current_project = manager.get_current_project()
        if not current_project:
            logger.error("[start_analysis] Nenhum projeto carregado! Caminho: %s", self.project_path)
            QMessageBox.critical(self, "Erro", "[Erro ao acessar dados do projeto carregado]\n\nCertifique-se de carregar o projeto antes de iniciar a análise.")
            return

        # Desabilitar botão
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        # Iniciar análise
        self.analyzer = ProjectAnalyzer(self.project_path, self.ai_provider)
        self.analyzer.progress_updated.connect(self.update_progress)
        self.analyzer.analysis_completed.connect(self.show_results)
        self.analyzer.error_occurred.connect(self.show_error)
        self.analyzer.start()

    def update_progress(self, value: int, message: str):
        """Atualiza progresso"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)

    def show_results(self, analysis: Dict):
        """Mostra resultados da análise"""
        self.analyze_btn.setEnabled(True)

        # Estrutura
        if "structure" in analysis:
            self.populate_structure_tab(analysis["structure"])

        # Análise geral
        if "general_analysis" in analysis:
            self.general_tab.setPlainText(analysis["general_analysis"])

        # Análise de código
        if "code_analysis" in analysis:
            self.code_tab.setPlainText(analysis["code_analysis"])

        # Sugestões
        if "improvement_suggestions" in analysis:
            self.suggestions_tab.setPlainText(analysis["improvement_suggestions"])

        self.progress_label.setText("✅ Análise concluída com sucesso!")

    def populate_structure_tab(self, structure: ProjectStructure):
        """Popula aba de estrutura, exibindo diretórios e arquivos dentro de cada um"""
        # Atualizar informações
        info_text = f"""
📊 Informações do Projeto: {structure.name}

📁 Total de arquivos: {len(structure.files)}
💻 Arquivos de código: {len(structure.code_files)}
📚 Documentação: {len(structure.doc_files)}
⚙️ Configuração: {len(structure.config_files)}
📂 Diretórios: {len(structure.directories)}
💾 Tamanho total: {structure.total_size / 1024:.1f} KB
"""
        self.info_label.setText(info_text)

        # Limpar árvore
        self.file_tree.clear()

        # Mapear arquivos por diretório relativo
        files_by_dir = {}
        for file in structure.files:
            # Pega diretório relativo
            rel_dir = os.path.relpath(os.path.dirname(file.path), structure.root_path)
            if rel_dir == ".":
                rel_dir = "(raiz)"
            files_by_dir.setdefault(rel_dir, []).append(file)

        # Pastas essenciais do Unity
        unity_dirs = ["Assets", "Library", "ProjectSettings", "Packages"]
        # Adicionar diretórios essenciais primeiro, se existirem
        for dir_name in unity_dirs:
            if dir_name in files_by_dir or dir_name in structure.directories:
                dir_item = QTreeWidgetItem([f"📁 {dir_name}", "Diretório", ""])
                for file in files_by_dir.get(dir_name, []):
                    tipo = "Código" if file.is_code else ("Documentação" if file.extension in [".md", ".txt", ".rst"] else "Configuração" if file.name in ["requirements.txt", "package.json", "Cargo.toml", "pom.xml", "setup.py"] else "Outro")
                    item = QTreeWidgetItem([
                        file.name,
                        tipo,
                        f"{file.size / 1024:.1f} KB"
                    ])
                    dir_item.addChild(item)
                self.file_tree.addTopLevelItem(dir_item)

        # Adicionar demais diretórios como itens principais
        for dir_name in sorted(structure.directories):
            if dir_name not in unity_dirs:
                dir_item = QTreeWidgetItem([f"📁 {dir_name}", "Diretório", ""])
                for file in files_by_dir.get(dir_name, []):
                    tipo = "Código" if file.is_code else ("Documentação" if file.extension in [".md", ".txt", ".rst"] else "Configuração" if file.name in ["requirements.txt", "package.json", "Cargo.toml", "pom.xml", "setup.py"] else "Outro")
                    item = QTreeWidgetItem([
                        file.name,
                        tipo,
                        f"{file.size / 1024:.1f} KB"
                    ])
                    dir_item.addChild(item)
                self.file_tree.addTopLevelItem(dir_item)

        # Adicionar arquivos da raiz (caso existam)
        if "(raiz)" in files_by_dir:
            root_item = QTreeWidgetItem(["📁 (raiz)", "Diretório", ""])
            for file in files_by_dir["(raiz)"]:
                tipo = "Código" if file.is_code else ("Documentação" if file.extension in [".md", ".txt", ".rst"] else "Configuração" if file.name in ["requirements.txt", "package.json", "Cargo.toml", "pom.xml", "setup.py"] else "Outro")
                item = QTreeWidgetItem([
                    file.name,
                    tipo,
                    f"{file.size / 1024:.1f} KB"
                ])
                root_item.addChild(item)
            self.file_tree.addTopLevelItem(root_item)

        # Expandir tudo
        self.file_tree.expandAll()

    def show_error(self, error_message: str):
        """Mostra erro"""
        self.analyze_btn.setEnabled(True)
        self.progress_label.setText(f"❌ Erro: {error_message}")
        QMessageBox.critical(
            self, "Erro na Análise", f"Erro durante a análise:\n\n{error_message}"
        )

    def export_report(self):
        """Exporta relatório"""
        if not self.general_tab.toPlainText():
            QMessageBox.information(self, "Exportar", "Execute uma análise primeiro!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            f"relatorio_projeto_{os.path.basename(self.project_path)}.txt",
            "Arquivos de Texto (*.txt)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"RELATÓRIO DE ANÁLISE - {os.path.basename(self.project_path)}\n"
                    )
                    f.write("=" * 60 + "\n\n")

                    f.write("ANÁLISE GERAL\n")
                    f.write("-" * 20 + "\n")
                    f.write(self.general_tab.toPlainText() + "\n\n")

                    f.write("QUALIDADE DO CÓDIGO\n")
                    f.write("-" * 20 + "\n")
                    f.write(self.code_tab.toPlainText() + "\n\n")

                    f.write("SUGESTÕES DE MELHORIA\n")
                    f.write("-" * 20 + "\n")
                    f.write(self.suggestions_tab.toPlainText() + "\n")

                QMessageBox.information(
                    self, "Exportar", f"Relatório salvo em:\n{file_path}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar relatório:\n{e}")

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
        
        QPushButton:disabled {
            background-color: #666666;
        }
        
        QTextEdit {
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
            padding: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        
        QTreeWidget {
            border: 1px solid #555;
            border-radius: 4px;
            background-color: #2d2d2d;
            alternate-background-color: #353535;
        }
        
        QTreeWidget::item {
            padding: 4px;
        }
        
        QTreeWidget::item:selected {
            background-color: #2196F3;
        }
        
        QProgressBar {
            border: 1px solid #555;
            border-radius: 4px;
            text-align: center;
            background-color: #2d2d2d;
        }
        
        QProgressBar::chunk {
            background-color: #2196F3;
            border-radius: 3px;
        }
        """
        self.setStyleSheet(style)

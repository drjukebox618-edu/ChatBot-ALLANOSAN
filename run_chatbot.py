#!/usr/bin/env python3
"""
ChatBot v3.0 - Launcher Principal
Sistema completo com todas as funcionalidades solicitadas
"""

import sys
import io
import logging
from pathlib import Path

# Configurar path do projeto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar logging
log_dir = project_root / "logs_app"
log_dir.mkdir(exist_ok=True)

# Configurar stdout com encoding correto para Git Bash
stdout_handler = logging.StreamHandler(
    io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "chatbot.log", encoding="utf-8"),
        stdout_handler,
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Função principal"""
    try:
        logger.info("🚀 Iniciando ChatBot v3.0...")

        # Verificar PyQt6
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
        except ImportError as e:
            logger.error(f"❌ Erro ao importar PyQt6: {e}")
            print("\n❌ ERRO: PyQt6 não está instalado!")
            print("💡 Para instalar, execute: pip install PyQt6")
            return 1

        # Configurar aplicação
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setApplicationName("ChatBot v3.0")
        app.setApplicationVersion("3.0.0")
        app.setOrganizationName("ChatBot AI")

        # Aplicar tema escuro
        app.setStyle("Fusion")


        # Importar interface principal
        try:
            from src.ui.main_interface import AdvancedChatBotGUI
            logger.info("✅ Interface principal carregada")
        except ImportError as e:
            logger.error(f"❌ Erro ao importar interface: {e}")
            print(f"\n❌ ERRO ao carregar interface: {e}")
            return 1

        # Criar e exibir janela principal
        window = AdvancedChatBotGUI()
        window.show()

        logger.info("ChatBot v3.0 iniciado com sucesso!")
        logger.info("Funcionalidades disponíveis:")
        logger.info("   Multi-AI (Gemini, GPT-4, Claude)")
        logger.info("   Menu flutuante")
        logger.info("   Histórico clicável")
        logger.info("   Atalhos de teclado")
        logger.info("   Análise de projetos")
        logger.info("   OCR e análise de imagens")
        logger.info("   Controle de criatividade")
        logger.info("   Temas claro/escuro")
        logger.info("   Configurações avançadas")

        # Executar aplicação
        return app.exec()

    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        print(f"\n❌ ERRO CRÍTICO: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

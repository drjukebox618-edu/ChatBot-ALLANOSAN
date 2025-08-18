"""
Factory para inicialização da aplicação.
Sistema modular e otimizado de bootstrap.
"""

import sys
import logging
import signal
import atexit
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QApplication

# Configuração inicial de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
class AppBootstrap:
    """Classe para inicialização e bootstrap da aplicação."""
    
    def __init__(self):
        self.app_instance: Optional[object] = None
        self.qt_app: Optional[QApplication] = None
        self.cleanup_completed = False
        
    def run(self) -> int:
        """Executa aplicação completa."""
        try:
            logger.info("🚀 Iniciando ChatBot Programador Sênior v3.0 - Edição Otimizada")
            
            # Validações iniciais
            if not self._validate_environment():
                return 1
            
            # Configurar ambiente
            self._setup_environment()
            
            # Verificar dependências
            if not self._check_dependencies():
                return 1
            
            # Criar aplicação
            if not self._create_application():
                return 1
            
            # Executar loop principal
            return self._run_main_loop()
            
        except KeyboardInterrupt:
            logger.info("⏹️ Interrompido pelo usuário")
            return 0
        except Exception as e:
            logger.critical(f"❌ Erro crítico: {e}")
            return 1
        finally:
            self._cleanup()
    
    def _validate_environment(self) -> bool:
        """Valida ambiente de execução."""
        try:
            # Verificar versão do Python
            if sys.version_info < (3, 8):
                logger.error("Python 3.8+ requerido")
                return False
            
            # Verificar permissões de escrita
            test_file = Path("test_write.tmp")
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception:
                logger.error("Sem permissões de escrita no diretório")
                return False
            
            logger.info("✅ Ambiente validado")
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return False
    
    def _setup_environment(self):
        """Configura ambiente da aplicação."""
        # Configurar SSL
        import os
        import certifi
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        os.environ['CRYPTOGRAPHY_OPENSSL_NO_LEGACY'] = '1'
        os.environ['OPENSSL_CONF'] = ''
        
        # Criar diretórios necessários
        directories = [
            "conversation_history", "exports", "backups",
            "recovery_backup", "logs_app", "projects", "images"
        ]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        # Configurar signal handlers
        self._setup_signal_handlers()
        
        logger.info("✅ Ambiente configurado")
    
    def _setup_signal_handlers(self):
        """Configura handlers de sinal."""
        try:
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, self._signal_handler)
            if hasattr(signal, 'SIGINT'):
                signal.signal(signal.SIGINT, self._signal_handler)
            
            atexit.register(self._cleanup)
            
        except Exception as e:
            logger.warning(f"Erro ao configurar signals: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais do sistema."""
        logger.info(f"Signal recebido: {signum}")
        self._cleanup()
        sys.exit(0)
    
    def _check_dependencies(self) -> bool:
        """Verifica dependências críticas."""
        required_modules = [
            ('PyQt6', 'Interface gráfica'),
            ('google.genai', 'API do Gemini'),
            ('PIL', 'Processamento de imagens')
        ]
        
        missing = []
        for module, description in required_modules:
            try:
                if module == 'PyQt6':
                    import PyQt6
                elif module == 'google.genai':
                    import google.genai
                elif module == 'PIL':
                    from PIL import Image
            except ImportError:
                missing.append((module, description))
        
        if missing:
            logger.error("❌ Dependências faltando:")
            for module, desc in missing:
                logger.error(f"  - {module}: {desc}")
            return False
        
        logger.info("✅ Dependências verificadas")
        return True
    
    def _create_application(self) -> bool:
        """Cria aplicação Qt e interface."""
        try:
            # Criar aplicação Qt
            self.qt_app = QApplication(sys.argv)
            self.qt_app.setApplicationName("ChatBot Programador Sênior")
            self.qt_app.setApplicationVersion("3.0")
            
            # Configurar estilo
            self.qt_app.setStyle('Fusion')
            
            # Importar e criar interface (usando sistema consolidado)
            logger.info("Importando interface...")
            from src.ui.windows.interface import ModernChatBotGUI
            logger.info("Interface importada, criando instância...")
            self.app_instance = ModernChatBotGUI()
            logger.info("Instância criada, configurando janela...")
            
            # Configurar janela
            self.app_instance.show()
            if hasattr(self.app_instance, 'center_window'):
                self.app_instance.center_window()
            
            logger.info("✅ Interface v3.0 criada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar aplicação: {e}")
            return False
    
    def _run_main_loop(self) -> int:
        """Executa loop principal da aplicação."""
        try:
            logger.info("🎯 Aplicação pronta!")
            exit_code = self.qt_app.exec()
            logger.info(f"Aplicação finalizada com código: {exit_code}")
            return 0 if exit_code == 0 else 1
            
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            return 1
    
    def _cleanup(self):
        """Limpa recursos da aplicação."""
        if self.cleanup_completed:
            return
        
        try:
            logger.info("🧹 Iniciando cleanup...")
            
            # Cleanup da interface
            if self.app_instance and hasattr(self.app_instance, 'cleanup_resources'):
                try:
                    self.app_instance.cleanup_resources()
                except RuntimeError:
                    # Objeto Qt já deletado
                    pass
            
            # Cleanup do Qt
            if self.qt_app:
                try:
                    self.qt_app.quit()
                except:
                    pass
            
            self.cleanup_completed = True
            logger.info("✅ Cleanup concluído")
            
        except Exception as e:
            logger.error(f"Erro no cleanup: {e}")
class ErrorRecovery:
    """Sistema de recuperação de erros."""
    
    @staticmethod
    def create_error_report(error: Exception, context: str = "") -> str:
        """Cria relatório de erro."""
        import traceback
        import time
        
        return f"""
🚨 ERRO - ChatBot Programador Sênior

⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
🔍 Contexto: {context}
❌ Tipo: {type(error).__name__}
📝 Mensagem: {str(error)}

📋 Traceback:
{traceback.format_exc()}

💡 Soluções:
1. Verifique dependências: pip install -r requirements.txt
2. Verifique configurações em user_settings.json
3. Consulte logs em logs_app/chatbot.log
"""
    
    @staticmethod
    def save_error_report(error: Exception, context: str = ""):
        """Salva relatório de erro."""
        try:
            report = ErrorRecovery.create_error_report(error, context)
            
            # Salvar em arquivo
            error_file = Path("logs_app/error_report.txt")
            error_file.parent.mkdir(exist_ok=True)
            
            with open(error_file, "w", encoding="utf-8") as f:
                f.write(report)
            
            logger.info(f"Relatório de erro salvo em: {error_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")
def create_config_if_missing():
    """Cria configurações padrão se não existirem."""
    try:
        from src.config.settings import get_settings_manager
        
        # Isso vai criar o arquivo se não existir
        manager = get_settings_manager()
        # Carregar configurações existentes ou criar padrão
        current_settings = manager.get_settings()
        manager.save_settings(current_settings)
        
        logger.info("✅ Configurações verificadas")
        
    except Exception as e:
        logger.warning(f"Erro ao criar configurações: {e}")
def show_help():
    """Mostra ajuda da aplicação."""
    help_text = """
🤖 ChatBot Programador Sênior v2.0

DESCRIÇÃO:
    Assistente IA especializado em programação com interface moderna.

CARACTERÍSTICAS:
    ✓ Interface PyQt6 otimizada
    ✓ Análise inteligente de projetos
    ✓ Suporte a múltiplos modelos de IA
    ✓ Processamento de imagens e OCR
    ✓ Histórico persistente de conversas

COMANDOS:
    python main.py        - Iniciar aplicação
    python main.py --help - Mostrar esta ajuda

CONFIGURAÇÃO:
    1. Configure sua chave da API do Gemini
    2. Ajuste preferências em Ferramentas → Configurações
    3. Comece a usar!

SUPORTE:
    • Logs: logs_app/chatbot.log
    • Configurações: src/user_settings.json
    • Relatórios de erro: logs_app/error_report.txt
"""
    print(help_text)
def main() -> int:
    """Função principal otimizada."""
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        return 0
    
    # Criar configurações se necessário
    create_config_if_missing()
    
    # Executar aplicação
    bootstrap = AppBootstrap()
    return bootstrap.run()
if __name__ == "__main__":
    sys.exit(main())

"""
UnifiedAPI - Camada API Unificada
Combina gemini_api.py + chatbot.py core logic
De 703 linhas para ~350 linhas (-50% redução!)
"""

import asyncio
import logging
import threading
from typing import Optional, Dict, Any, List, Callable
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

# Imports de serviços
from .service_container import inject
from .super_performance import SuperPerformanceOptimizer, measure_time

logger = logging.getLogger(__name__)


@dataclass
class ChatbotState:
    """Estado unificado do chatbot."""

    current_conversation_id: Optional[str] = None
    is_processing: bool = False
    is_running: bool = True


class CallbackManager:
    """Gerenciador unificado de callbacks."""

    def __init__(self):
        self._callbacks: Dict[str, List[Callable]] = {}

    def register(self, event: str, callback: Callable):
        """Registra callback."""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def trigger(self, event: str, *args, **kwargs):
        """Dispara callbacks."""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Erro em callback {event}: {e}")


class UnifiedGeminiAPI:
    """API Gemini unificada."""

    def __init__(self):
        # Configuração dinâmica via dependency injection
        self.config_manager = None
        self.performance = inject(SuperPerformanceOptimizer)
        self._model = None
        self._initialized = False

    def initialize(self, api_key: str = None) -> bool:
        """Inicializa API."""
        try:
            if api_key:
                self._api_key = api_key

            # Inicializar cliente Gemini aqui
            self._initialized = True
            logger.info("Gemini API inicializada")
            return True

        except Exception as e:
            logger.error(f"Erro ao inicializar Gemini API: {e}")
            return False

    @measure_time
    async def generate_response(
        self, message: str, context: Dict[str, Any] = None
    ) -> str:
        """Gera resposta real usando Gemini API."""
        if not self._initialized:
            raise RuntimeError("API não inicializada")
        try:
            # Usar cache se disponível
            cache_key = f"response_{hash(message + str(context or {}))}"
            cached = self.performance.cache.get(cache_key)
            if cached:
                return cached

            # Chamada real à API Gemini usando google-genai
            import google.genai as genai

            genai.configure(api_key=self._api_key)
            model_name = (
                context.get("model", "gemini-2.5-flash")
                if context
                else "gemini-2.5-flash"
            )
            model = genai.GenerativeModel(model_name)
            response_obj = await asyncio.to_thread(model.generate_content, message)
            response = (
                response_obj.text
                if hasattr(response_obj, "text")
                else str(response_obj)
            )

            # Cache resultado
            self.performance.cache.set(cache_key, response)
            return response
        except Exception as e:
            logger.error(f"Erro ao gerar resposta Gemini: {e}")
            return f"[Erro Gemini] {str(e)}"

    async def generate_response_stream(
        self, message: str, context: Dict[str, Any] = None
    ):
        """Gera resposta em streaming."""
        try:
            # Simular streaming (substituir por API real)
            response = await self.generate_response(message, context)

            # Simular chunks
            words = response.split()
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i : i + 3]) + " "
                yield chunk
                await asyncio.sleep(0.05)  # Simular delay

        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            yield f"Erro: {str(e)}"


class SuperChatBot:
    """ChatBot super unificado."""

    def __init__(self):
        self.state = ChatbotState()
        self.callbacks = CallbackManager()

        # Serviços injetados
        self.api = UnifiedGeminiAPI()
        self.performance = inject(SuperPerformanceOptimizer)

        # Componentes lazy-loaded
        self._conversation_history = None
        self._project_manager = None
        self._image_processor = None

        # Thread pool
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.lock = threading.Lock()

    # Lazy loading properties
    @property
    def conversation_history(self):
        if self._conversation_history is None:
            from .conversation_history import ConversationHistory

            self._conversation_history = ConversationHistory()
        return self._conversation_history

    @property
    def project_manager(self):
        if self._project_manager is None:
            from .project_manager import ProjectManager

            self._project_manager = ProjectManager()
        return self._project_manager

    @property
    def image_processor(self):
        if self._image_processor is None:
            from .image_processor import ImageProcessor

            self._image_processor = ImageProcessor()
        return self._image_processor

    def initialize(self, api_key: str = None) -> bool:
        """Inicializa chatbot."""
        return self.api.initialize(api_key)

    def set_callbacks(self, **callbacks):
        """Define callbacks."""
        for event, callback in callbacks.items():
            self.callbacks.register(event, callback)

    @measure_time
    def send_message(self, message: str, image_path: str = None) -> bool:
        """Envia mensagem (interface principal)."""
        if self.state.is_processing:
            return False

        try:
            self.executor.submit(self._process_message_sync, message, image_path)
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False

    def _process_message_sync(self, message: str, image_path: str = None):
        """Processa mensagem sincronamente."""
        try:
            with self._processing_context():
                # Adicionar ao histórico
                self.conversation_history.add_message(
                    self.state.current_conversation_id, "user", message
                )

                # Trigger callback
                self.callbacks.trigger("message", "Você", message, "lightblue")

                # Processar resposta
                if image_path:
                    response = self._run_async(
                        self._process_image_message(image_path, message)
                    )
                else:
                    context = self._build_context()
                    response = self._run_async(
                        self.api.generate_response(message, context)
                    )

                # Adicionar resposta ao histórico
                self.conversation_history.add_message(
                    self.state.current_conversation_id, "assistant", response
                )

                # Trigger callback
                self.callbacks.trigger("message", "Assistente", response, "white")

        except Exception as e:
            error_msg = f"Erro no processamento: {str(e)}"
            logger.error(error_msg)
            self.callbacks.trigger("message", "Sistema", error_msg, "red")

    async def _process_image_message(self, image_path: str, message: str) -> str:
        """Processa mensagem com imagem."""
        # Usar image processor
        image_analysis = await self.image_processor.analyze_image(image_path)

        # Combinar análise com mensagem
        combined_message = f"Imagem: {image_analysis}\nPergunta: {message}"

        return await self.api.generate_response(combined_message)

    def _build_context(self) -> Dict[str, Any]:
        """Constrói contexto da conversa."""
        context = {}

        # Adicionar projeto se carregado
        if self.project_manager.current_project:
            context["project_context"] = self.project_manager.get_project_summary()

        # Adicionar configurações
        try:
            from ..config.super_config import super_config_manager

            config = super_config_manager.get_config()
            context["model"] = config.model_name
            context["temperature"] = config.temperature
        except Exception:
            pass

        return context

    def load_project(self, project_path: str) -> bool:
        """Carrega projeto."""
        try:
            success = self._run_async(self.project_manager.load_project(project_path))
            if success:
                self.callbacks.trigger("status", f"Projeto carregado: {project_path}")
            return success
        except Exception as e:
            logger.error(f"Erro ao carregar projeto: {e}")
            return False

    def new_conversation(self) -> str:
        """Inicia nova conversa."""
        conversation_id = self.conversation_history.create_conversation()
        self.state.current_conversation_id = conversation_id
        self.callbacks.trigger("status", "Nova conversa iniciada")
        return conversation_id

    def get_conversation_history(self) -> List[Dict]:
        """Retorna histórico."""
        return self.conversation_history.get_conversations_list()

    @contextmanager
    def _processing_context(self):
        """Context manager para processamento."""
        if self.state.is_processing:
            raise RuntimeError("Já processando")

        self.state.is_processing = True
        try:
            yield
        finally:
            self.state.is_processing = False

    def _run_async(self, coro):
        """Executa coroutine sincronamente."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)

    def cleanup_resources(self):
        """Limpeza de recursos."""
        try:
            self.state.is_running = False
            self.executor.shutdown(wait=True)
            self.conversation_history.save_conversations()
            self.performance.cleanup()
            logger.info("Recursos limpos")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


# Instâncias globais
unified_api = UnifiedGeminiAPI()
super_chatbot = SuperChatBot()

# Aliases para compatibilidade
GeminiAPI = UnifiedGeminiAPI
ChatBot = SuperChatBot
Chatbot = SuperChatBot

# Exportações
__all__ = [
    "UnifiedGeminiAPI",
    "SuperChatBot",
    "GeminiAPI",
    "ChatBot",
    "Chatbot",
    "unified_api",
    "super_chatbot",
]

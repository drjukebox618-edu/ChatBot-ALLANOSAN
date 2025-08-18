"""
Sistema de Provedores de IA para ChatBot v3.0
Integração com Gemini, GPT e Claude
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

# Configuração de logs
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Provedores de IA disponíveis"""

    GEMINI = "gemini"
    GPT = "gpt"
    CLAUDE = "claude"


@dataclass
class AIModel:
    """Modelo de IA com configurações"""

    name: str
    provider: AIProvider
    display_name: str
    max_tokens: int = 4000
    supports_vision: bool = False
    supports_streaming: bool = True


class AIProviderBase(ABC):
    """Classe base para provedores de IA"""

    def __init__(self, api_key: str, model_name: str = None):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """Inicializa o cliente da API"""
        pass

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Gera texto usando a IA"""
        pass

    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Gera texto em stream"""
        pass

    @abstractmethod
    async def analyze_image(self, image_data: bytes, prompt: str = None) -> str:
        """Analisa imagem (OCR/Vision)"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[AIModel]:
        """Retorna modelos disponíveis"""
        pass


class GeminiProvider(AIProviderBase):
    """Provedor Gemini (Padrão)"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name or "gemini-2.5-flash"
        self.available_models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro",
        ]
        super().__init__(api_key, self.model_name)

    def _initialize_client(self):
        """Inicializa cliente Gemini"""
        try:
            import google.genai as genai

            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Cliente Gemini inicializado com modelo: {self.model_name}")
        except ImportError:
            logger.error("google-genai não instalado. Use: pip install google-genai")
            raise

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Gera texto com Gemini"""
        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 4000)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "response_mime_type": "text/plain",
                },
            )

            return response.text

        except Exception as e:
            logger.error(f"Erro no Gemini: {e}")
            return f"Erro na geração: {str(e)}"

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Gera texto em stream com Gemini"""
        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 4000)

            stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config={"temperature": temperature, "max_output_tokens": max_tokens},
            )

            for chunk in stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Erro no stream Gemini: {e}")
            yield f"Erro no stream: {str(e)}"

    async def analyze_image(
        self, image_data: bytes, prompt: str = "Descreva esta imagem"
    ) -> str:
        """Analisa imagem com Gemini Vision"""
        try:
            import base64

            # Converte para base64
            image_b64 = base64.b64encode(image_data).decode("utf-8")

            response = self.client.models.generate_content(
                model="gemini-1.5-pro-vision",  # Modelo específico para visão
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_b64,
                                }
                            },
                        ],
                    }
                ],
            )

            return response.text

        except Exception as e:
            logger.error(f"Erro na análise de imagem Gemini: {e}")
            return f"Erro na análise: {str(e)}"

    def get_available_models(self) -> List[AIModel]:
        """Modelos Gemini disponíveis"""
        return [
            AIModel(
                "gemini-2.5-flash",
                AIProvider.GEMINI,
                "Gemini 2.5 Flash",
                8192,
                True,
                True,
            ),
            AIModel(
                "gemini-2.5-pro", AIProvider.GEMINI, "Gemini 2.5 Pro", 8192, True, True
            ),
            AIModel(
                "gemini-1.5-pro", AIProvider.GEMINI, "Gemini 1.5 Pro", 8192, True, True
            ),
            AIModel(
                "gemini-1.5-flash",
                AIProvider.GEMINI,
                "Gemini 1.5 Flash",
                8192,
                True,
                True,
            ),
            AIModel(
                "gemini-1.0-pro", AIProvider.GEMINI, "Gemini 1.0 Pro", 4096, False, True
            ),
        ]


class GPTProvider(AIProviderBase):
    """Provedor OpenAI GPT"""

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.model_name = model_name or "gpt-4o"
        super().__init__(api_key, self.model_name)

    def _initialize_client(self):
        """Inicializa cliente OpenAI"""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"Cliente OpenAI inicializado com modelo: {self.model_name}")
        except ImportError:
            logger.error("openai não instalado. Use: pip install openai")
            raise

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Gera texto com GPT"""
        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 4000)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Erro no GPT: {e}")
            return f"Erro na geração: {str(e)}"

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Gera texto em stream com GPT"""
        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 4000)

            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Erro no stream GPT: {e}")
            yield f"Erro no stream: {str(e)}"

    async def analyze_image(
        self, image_data: bytes, prompt: str = "Descreva esta imagem"
    ) -> str:
        """Analisa imagem com GPT Vision"""
        try:
            import base64

            # Converte para base64
            image_b64 = base64.b64encode(image_data).decode("utf-8")

            response = self.client.chat.completions.create(
                model="gpt-4o",  # Modelo com visão
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                },
                            },
                        ],
                    }
                ],
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Erro na análise de imagem GPT: {e}")
            return f"Erro na análise: {str(e)}"

    def get_available_models(self) -> List[AIModel]:
        """Modelos GPT disponíveis"""
        return [
            AIModel("gpt-4o", AIProvider.GPT, "GPT-4o", 4096, True, True),
            AIModel("gpt-4o-mini", AIProvider.GPT, "GPT-4o Mini", 4096, True, True),
            AIModel("gpt-4-turbo", AIProvider.GPT, "GPT-4 Turbo", 4096, True, True),
            AIModel(
                "gpt-3.5-turbo", AIProvider.GPT, "GPT-3.5 Turbo", 4096, False, True
            ),
        ]


class ClaudeProvider(AIProviderBase):
    """Provedor Anthropic Claude"""

    def __init__(self, api_key: str, model_name: str = "claude-sonnet-4-20250514"):
        self.model_name = model_name or "claude-sonnet-4-20250514"
        super().__init__(api_key, self.model_name)

    def _initialize_client(self):
        """Inicializa cliente Anthropic"""
        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=self.api_key)
            logger.info(f"Cliente Claude inicializado com modelo: {self.model_name}")
        except ImportError:
            logger.error("anthropic não instalado. Use: pip install anthropic")
            raise

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Gera texto com Claude"""
        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 4000)

            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"Erro no Claude: {e}")
            return f"Erro na geração: {str(e)}"

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Gera texto em stream com Claude"""
        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 4000)

            stream = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )

            for event in stream:
                if event.type == "content_block_delta":
                    yield event.delta.text

        except Exception as e:
            logger.error(f"Erro no stream Claude: {e}")
            yield f"Erro no stream: {str(e)}"

    async def analyze_image(
        self, image_data: bytes, prompt: str = "Descreva esta imagem"
    ) -> str:
        """Analisa imagem com Claude Vision"""
        try:
            import base64

            # Converte para base64
            image_b64 = base64.b64encode(image_data).decode("utf-8")

            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_b64,
                                },
                            },
                        ],
                    }
                ],
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"Erro na análise de imagem Claude: {e}")
            return f"Erro na análise: {str(e)}"

    def get_available_models(self) -> List[AIModel]:
        """Modelos Claude disponíveis"""
        return [
            AIModel(
                "claude-sonnet-4-20250514",
                AIProvider.CLAUDE,
                "Claude 4 Sonnet",
                4096,
                True,
                True,
            ),
            AIModel(
                "claude-3-5-sonnet-20241022",
                AIProvider.CLAUDE,
                "Claude 3.5 Sonnet",
                4096,
                True,
                True,
            ),
            AIModel(
                "claude-3-haiku-20240307",
                AIProvider.CLAUDE,
                "Claude 3 Haiku",
                4096,
                True,
                True,
            ),
        ]


class AIProviderManager:
    """Gerenciador de provedores de IA"""

    def __init__(self):
        self.providers: Dict[AIProvider, AIProviderBase] = {}
        self.current_provider = AIProvider.GEMINI  # Padrão
        self.api_keys = {}
        self._load_api_keys()

    def _load_api_keys(self):
        """Carrega chaves de API das variáveis de ambiente"""
        self.api_keys = {
            AIProvider.GEMINI: os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY"),
            AIProvider.GPT: os.getenv("OPENAI_API_KEY"),
            AIProvider.CLAUDE: os.getenv("ANTHROPIC_API_KEY"),
        }

    def set_api_key(self, provider: AIProvider, api_key: str):
        """Define chave de API para um provedor"""
        self.api_keys[provider] = api_key

        # Reinicializa o provedor se já existir
        if provider in self.providers:
            self._initialize_provider(provider)

    def _initialize_provider(self, provider: AIProvider, model_name: str = None):
        """Inicializa um provedor específico"""
        api_key = self.api_keys.get(provider)
        if not api_key:
            raise ValueError(f"Chave de API não configurada para {provider.value}")

        try:
            if provider == AIProvider.GEMINI:
                self.providers[provider] = GeminiProvider(api_key, model_name)
            elif provider == AIProvider.GPT:
                self.providers[provider] = GPTProvider(api_key, model_name)
            elif provider == AIProvider.CLAUDE:
                self.providers[provider] = ClaudeProvider(api_key, model_name)

            logger.info(f"Provedor {provider.value} inicializado com sucesso")

        except Exception as e:
            logger.error(f"Erro ao inicializar provedor {provider.value}: {e}")
            raise

    def switch_provider(self, provider: AIProvider, model_name: str = None):
        """Troca o provedor atual"""
        if provider not in self.providers:
            self._initialize_provider(provider, model_name)

        self.current_provider = provider
        logger.info(f"Provedor alterado para: {provider.value}")

    def get_current_provider(self) -> AIProviderBase:
        """Retorna o provedor atual"""
        if self.current_provider not in self.providers:
            self._initialize_provider(self.current_provider)

        return self.providers[self.current_provider]

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Gera texto usando o provedor atual"""
        provider = self.get_current_provider()
        return await provider.generate_text(prompt, **kwargs)

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Gera texto em stream usando o provedor atual"""
        provider = self.get_current_provider()
        async for chunk in provider.generate_stream(prompt, **kwargs):
            yield chunk

    async def analyze_image(self, image_data: bytes, prompt: str = None) -> str:
        """Analisa imagem usando o provedor atual"""
        provider = self.get_current_provider()
        return await provider.analyze_image(image_data, prompt)

    def get_available_providers(self) -> List[AIProvider]:
        """Retorna provedores disponíveis (com chaves configuradas)"""
        available = []
        for provider in AIProvider:
            if self.api_keys.get(provider):
                available.append(provider)
        return available

    def get_all_models(self) -> Dict[AIProvider, List[AIModel]]:
        """Retorna todos os modelos disponíveis por provedor"""
        models = {}

        for provider in AIProvider:
            try:
                if provider not in self.providers and self.api_keys.get(provider):
                    self._initialize_provider(provider)

                if provider in self.providers:
                    models[provider] = self.providers[provider].get_available_models()
            except Exception as e:
                logger.warning(
                    f"Não foi possível carregar modelos para {provider.value}: {e}"
                )

        return models

    def get_provider_status(self) -> Dict[str, Any]:
        """Retorna status dos provedores"""
        status = {}

        for provider in AIProvider:
            has_key = bool(self.api_keys.get(provider))
            is_initialized = provider in self.providers
            is_current = provider == self.current_provider

            status[provider.value] = {
                "has_api_key": has_key,
                "is_initialized": is_initialized,
                "is_current": is_current,
                "display_name": provider.value.title(),
            }

        return status

    def set_temperature(self, temperature: float):
        """Define a temperatura para o provedor atual"""
        try:
            provider = self.get_current_provider()
            if hasattr(provider, "set_temperature"):
                provider.set_temperature(temperature)
                logger.info(
                    f"Temperatura definida para {temperature} no provedor {self.current_provider.value}"
                )
            else:
                logger.warning(
                    f"Provedor {self.current_provider.value} não suporta configuração de temperatura"
                )
        except Exception as e:
            logger.error(f"Erro ao definir temperatura: {e}")


# Instância global do gerenciador
ai_manager = AIProviderManager()

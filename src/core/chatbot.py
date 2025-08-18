"""
Wrapper de compatibilidade para chatbot.py
PRESERVA 100% DAS FUNCIONALIDADES ANTIGAS
"""

# Importar API unificada
from .unified_api import (
    SuperChatBot as ChatBot,
    SuperChatBot as Chatbot,
    super_chatbot
)

# Aliases para compatibilidade
# ChatBot e Chatbot já importados como aliases

# Instância global para compatibilidade
chatbot = super_chatbot

# Exportar tudo
__all__ = ['ChatBot', 'Chatbot', 'chatbot', 'super_chatbot']

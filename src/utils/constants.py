"""
Templates de prompts e constantes centralizados.
"""

PROJECT_ANALYSIS_TEMPLATE = """🔍 ANÁLISE COMPLETA DO PROJETO

Analise meu projeto e forneça:

1. 🏗️ **Arquitetura:** Estrutura, padrões, organização
2. 🔍 **Code Review:** Qualidade, boas práticas, problemas
3. 🚀 **Melhorias:** Performance, segurança, refatorações
4. 📋 **Prioridades:** Classifique por Alta/Média/Baixa

Seja específico e prático!"""

IMPLEMENTATION_TEMPLATE = """⚡ IMPLEMENTAÇÃO AUTOMÁTICA

Implemente as melhorias modificando os arquivos.

**FORMATO OBRIGATÓRIO:**
```ARQUIVO: nome_do_arquivo.py
[código completo do arquivo atualizado]
```

**REGRAS:**
- Apenas melhorias de ALTA/MÉDIA prioridade
- Manter TODA funcionalidade existente
- Arquivos COMPLETOS (não trechos)
- Nomes de arquivo EXATOS"""

# Configurações padrão
DEFAULT_SETTINGS = {
    "theme": "dark",
    "model": "gemini-2.5-flash", 
    "temperature": 0.7,
    "max_tokens": 8192,
    "timeout": 30.0,
    "cache_size": 100
}

# Mensagens de status
STATUS_MESSAGES = {
    "processing": "🤖 Processando...",
    "analyzing": "🔍 Analisando projeto...",
    "implementing": "⚡ Implementando melhorias...",
    "loading_image": "🖼️ Carregando imagem...",
    "saving": "💾 Salvando conversa..."
}

# Limites do sistema
LIMITS = {
    "max_message_length": 50000,
    "max_cache_size": 100,
    "max_conversation_messages": 500,
    "max_file_size_kb": 5000
}

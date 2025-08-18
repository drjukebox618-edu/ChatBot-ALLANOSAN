"""
Gerenciador otimizado de histórico de conversas.
Versão enxuta com funcionalidades essenciais.
"""

import json
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
import threading
from pathlib import Path
from src.utils.decorators import log_performance

logger = logging.getLogger(__name__)


class ConversationHistory:
    """Gerenciador otimizado de histórico de conversas."""

    def __init__(self, history_dir: str = "conversation_history"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)

        self.history_file = self.history_dir / "conversation_history.json"
        self.conversations: Dict[str, Dict] = {}
        self.search_index: Dict[str, Set[str]] = defaultdict(set)
        self.lock = threading.Lock()

        self.load_conversations()

    @log_performance
    def load_conversations(self):
        """Carrega conversas do arquivo."""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.conversations = data.get("conversations", {})
                    self._rebuild_search_index()
            logger.info(f"Carregadas {len(self.conversations)} conversas")
        except Exception as e:
            logger.error(f"Erro ao carregar conversas: {e}")
            self.conversations = {}

    @log_performance
    def save_conversations(self):
        """Salva conversas no arquivo."""
        try:
            with self.lock:
                data = {
                    "conversations": self.conversations,
                    "last_updated": datetime.now().isoformat(),
                }

                # Backup antes de salvar
                if self.history_file.exists():
                    backup_file = self.history_file.with_suffix(".bak")
                    if backup_file.exists():
                        backup_file.unlink()  # Remove o .bak se já existir
                    self.history_file.rename(backup_file)

                with open(self.history_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.debug("Conversas salvas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar conversas: {e}")

    def create_conversation(self, title: Optional[str] = None) -> str:
        """Cria nova conversa."""
        conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        conversation = {
            "id": conversation_id,
            "title": title or f"Conversa {datetime.now().strftime('%d/%m %H:%M')}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "metadata": {"model": "gemini-2.5-flash", "message_count": 0},
        }

        with self.lock:
            self.conversations[conversation_id] = conversation
            self._update_search_index(conversation_id, conversation)

        self.save_conversations()
        logger.info(f"Nova conversa criada: {conversation_id}")
        return conversation_id

    def add_message(self, conversation_id: str, role: str, content: str):
        """Adiciona mensagem à conversa."""
        if conversation_id not in self.conversations:
            conversation_id = self.create_conversation()

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        with self.lock:
            self.conversations[conversation_id]["messages"].append(message)
            self.conversations[conversation_id]["updated_at"] = (
                datetime.now().isoformat()
            )
            self.conversations[conversation_id]["metadata"]["message_count"] += 1

            # Atualizar índice de busca
            self._update_search_index(
                conversation_id, self.conversations[conversation_id]
            )

        # Salvar periodicamente
        if len(self.conversations[conversation_id]["messages"]) % 5 == 0:
            self.save_conversations()

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Retorna conversa por ID."""
        return self.conversations.get(conversation_id)

    def get_conversations_list(self) -> List[Dict]:
        """Retorna lista de conversas ordenada por data."""
        conversations = []
        for conv_id, conv in self.conversations.items():
            conversations.append(
                {
                    "id": conv_id,
                    "title": conv["title"],
                    "created_at": conv["created_at"],
                    "updated_at": conv["updated_at"],
                    "message_count": conv["metadata"]["message_count"],
                }
            )

        # Ordenar por data de atualização (mais recente primeiro)
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        """Remove conversa."""
        if conversation_id in self.conversations:
            with self.lock:
                del self.conversations[conversation_id]
                self._remove_from_search_index(conversation_id)
            self.save_conversations()
            logger.info(f"Conversa removida: {conversation_id}")
            return True
        return False

    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """Busca conversas por termo."""
        if not query.strip():
            return self.get_conversations_list()[:limit]

        query_words = self._tokenize(query.lower())
        if not query_words:
            return []

        # Calcular relevância
        scores = defaultdict(float)
        for word in query_words:
            for conv_id in self.search_index.get(word, []):
                scores[conv_id] += 1.0 / len(query_words)

        # Ordenar por relevância
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[
            :limit
        ]

        # Montar resultados
        results = []
        for conv_id in sorted_ids:
            if conv_id in self.conversations:
                conv = self.conversations[conv_id]
                results.append(
                    {
                        "id": conv_id,
                        "title": conv["title"],
                        "updated_at": conv["updated_at"],
                        "relevance": scores[conv_id],
                        "message_count": conv["metadata"]["message_count"],
                    }
                )

        return results

    def cleanup_empty_conversations(self) -> int:
        """Remove conversas vazias."""
        empty_ids = [
            conv_id
            for conv_id, conv in self.conversations.items()
            if len(conv.get("messages", [])) == 0
        ]

        for conv_id in empty_ids:
            self.delete_conversation(conv_id)

        logger.info(f"Removidas {len(empty_ids)} conversas vazias")
        return len(empty_ids)

    def export_conversation(
        self, conversation_id: str, format_type: str = "json"
    ) -> Optional[str]:
        """Exporta conversa para arquivo."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None

        try:
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)

            filename = f"conversa_{conversation_id}.{format_type}"
            filepath = export_dir / filename

            if format_type == "json":
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(conversation, f, indent=2, ensure_ascii=False)
            elif format_type == "txt":
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {conversation['title']}\n\n")
                    for msg in conversation["messages"]:
                        f.write(f"**{msg['role'].title()}:** {msg['content']}\n\n")

            logger.info(f"Conversa exportada: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Erro ao exportar conversa: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas das conversas."""
        total_conversations = len(self.conversations)
        total_messages = sum(
            len(conv.get("messages", [])) for conv in self.conversations.values()
        )

        # Conversas por mês
        monthly_count = defaultdict(int)
        for conv in self.conversations.values():
            try:
                date = datetime.fromisoformat(conv["created_at"])
                month_key = date.strftime("%Y-%m")
                monthly_count[month_key] += 1
            except Exception:
                pass

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": total_messages
            / max(total_conversations, 1),
            "monthly_conversations": dict(monthly_count),
            "index_size": len(self.search_index),
        }

    # Métodos internos otimizados

    def _tokenize(self, text: str) -> Set[str]:
        """Tokeniza texto para busca."""
        if not text:
            return set()

        words = re.findall(r"\b\w+\b", text.lower())
        stop_words = {
            "a",
            "o",
            "e",
            "de",
            "do",
            "da",
            "em",
            "um",
            "uma",
            "para",
            "com",
            "por",
            "que",
            "se",
            "é",
            "não",
        }
        return {word for word in words if len(word) >= 3 and word not in stop_words}

    def _update_search_index(self, conversation_id: str, conversation: Dict):
        """Atualiza índice de busca para uma conversa."""
        # Remover da index primeiro
        self._remove_from_search_index(conversation_id)

        # Extrair texto
        text_parts = [conversation.get("title", "")]
        for msg in conversation.get("messages", []):
            text_parts.append(msg.get("content", ""))

        # Tokenizar e indexar
        all_words = set()
        for text in text_parts:
            words = self._tokenize(text)
            all_words.update(words)

        # Adicionar ao índice
        for word in all_words:
            self.search_index[word].add(conversation_id)

    def _remove_from_search_index(self, conversation_id: str):
        """Remove conversa do índice de busca."""
        for word_set in self.search_index.values():
            word_set.discard(conversation_id)

    def _rebuild_search_index(self):
        """Reconstrói índice de busca completo."""
        self.search_index.clear()
        for conv_id, conversation in self.conversations.items():
            self._update_search_index(conv_id, conversation)
        logger.debug(f"Índice de busca reconstruído: {len(self.search_index)} termos")

    def cleanup_resources(self):
        """Limpa recursos."""
        self.save_conversations()
        logger.info("Recursos do histórico limpos")

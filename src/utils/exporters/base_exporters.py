"""
Exportador base para conversas.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Classe base para exportadores."""
    
    def __init__(self):
        self.templates = {
            'default': {
                'title': "Histórico de Conversas - {title}",
                'header': "Gerado em {timestamp}",
                'message_format': "{author}: {content}",
                'separator': "=" * 50
            },
            'minimal': {
                'title': "{title}",
                'header': "",
                'message_format': "{content}",
                'separator': ""
            }
        }
    
    @abstractmethod
    def export(self, conversation_data: Dict, filepath: str, **options) -> bool:
        """Exporta conversa para arquivo."""
        pass
    
    def format_conversation(self, conversation_data: Dict, template: str = 'default') -> Dict[str, Any]:
        """Formata dados da conversa usando template."""
        template_config = self.templates.get(template, self.templates['default'])
        
        title = conversation_data.get('title', 'Conversa sem título')
        timestamp = conversation_data.get('created_at', 'Data desconhecida')
        messages = conversation_data.get('messages', [])
        
        formatted_messages = []
        for message in messages:
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            
            # Mapear roles para nomes amigáveis
            role_map = {
                'user': 'Você',
                'assistant': 'Assistente',
                'system': 'Sistema'
            }
            author = role_map.get(role, role.title())
            
            formatted_message = template_config['message_format'].format(
                author=author,
                content=content,
                timestamp=message.get('timestamp', '')
            )
            formatted_messages.append(formatted_message)
        
        return {
            'title': template_config['title'].format(title=title),
            'header': template_config['header'].format(timestamp=timestamp),
            'messages': formatted_messages,
            'separator': template_config['separator']
        }


class TextExporter(BaseExporter):
    """Exportador para formato texto."""
    
    def export(self, conversation_data: Dict, filepath: str, **options) -> bool:
        """Exporta para arquivo texto."""
        try:
            template = options.get('template', 'default')
            formatted = self.format_conversation(conversation_data, template)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Título
                if formatted['title']:
                    f.write(f"{formatted['title']}\n")
                    f.write(f"{formatted['separator']}\n\n")
                
                # Cabeçalho
                if formatted['header']:
                    f.write(f"{formatted['header']}\n\n")
                
                # Mensagens
                for message in formatted['messages']:
                    f.write(f"{message}\n\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar texto: {e}")
            return False


class JSONExporter(BaseExporter):
    """Exportador para formato JSON."""
    
    def export(self, conversation_data: Dict, filepath: str, **options) -> bool:
        """Exporta para arquivo JSON."""
        try:
            import json
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar JSON: {e}")
            return False


class MarkdownExporter(BaseExporter):
    """Exportador para formato Markdown."""
    
    def export(self, conversation_data: Dict, filepath: str, **options) -> bool:
        """Exporta para arquivo Markdown."""
        try:
            formatted = self.format_conversation(conversation_data, 'default')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Título
                title = conversation_data.get('title', 'Conversa')
                f.write(f"# {title}\n\n")
                
                # Cabeçalho
                timestamp = conversation_data.get('created_at', '')
                if timestamp:
                    f.write(f"**Criado em:** {timestamp}\n\n")
                
                # Mensagens
                messages = conversation_data.get('messages', [])
                for message in messages:
                    role = message.get('role', 'unknown')
                    content = message.get('content', '')
                    
                    # Mapear roles
                    role_map = {
                        'user': '🧑 Você',
                        'assistant': '🤖 Assistente', 
                        'system': '⚙️ Sistema'
                    }
                    author = role_map.get(role, role.title())
                    
                    f.write(f"## {author}\n\n")
                    f.write(f"{content}\n\n")
                    f.write("---\n\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar Markdown: {e}")
            return False


class CSVExporter(BaseExporter):
    """Exportador para formato CSV."""
    
    def export(self, conversation_data: Dict, filepath: str, **options) -> bool:
        """Exporta para arquivo CSV."""
        try:
            import csv
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Cabeçalho
                writer.writerow(['Timestamp', 'Role', 'Content'])
                
                # Mensagens
                messages = conversation_data.get('messages', [])
                for message in messages:
                    timestamp = message.get('timestamp', '')
                    role = message.get('role', '')
                    content = message.get('content', '').replace('\n', ' ')
                    
                    writer.writerow([timestamp, role, content])
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar CSV: {e}")
            return False

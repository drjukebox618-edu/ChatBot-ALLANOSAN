import os
from src.core.conversation_history import ConversationHistory


def test_salvar_historico():
    # Cria gerenciador de histórico em pasta temporária
    history = ConversationHistory(history_dir="test_conversation_history")
    conversation_id = history.create_conversation(title="Teste de Salvamento")
    history.add_message(conversation_id, "user", "Mensagem do usuário")
    history.add_message(conversation_id, "assistant", "Mensagem da IA")
    history.save_conversations()

    # Verifica se o arquivo foi criado
    history_file = os.path.join(
        "test_conversation_history", "conversation_history.json"
    )
    assert os.path.exists(history_file), "Arquivo de histórico não foi criado!"

    # Verifica se as mensagens estão salvas
    import json

    with open(history_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        conversas = data.get("conversations", {})
        assert conversation_id in conversas, "Conversa não encontrada no arquivo!"
        msgs = conversas[conversation_id]["messages"]
        assert len(msgs) == 2, "Mensagens não foram salvas corretamente!"
        assert msgs[0]["content"] == "Mensagem do usuário"
        assert msgs[1]["content"] == "Mensagem da IA"

    # Limpeza
    import shutil

    shutil.rmtree("test_conversation_history")
    print("Teste de salvamento de histórico passou!")


if __name__ == "__main__":
    test_salvar_historico()

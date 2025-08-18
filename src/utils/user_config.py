"""
Módulo para carregar e aplicar configurações dinâmicas do usuário.
"""

import json
import os

def load_user_configurations():
    """Carrega configurações do usuário e aplica globalmente."""
    try:
        if os.path.exists("user_settings.json"):
            with open("user_settings.json", "r", encoding="utf-8") as f:
                user_settings = json.load(f)
            
            print(f"📄 Configurações carregadas: {user_settings}")
            
            # Aplicar configurações globalmente IMEDIATAMENTE
            apply_user_settings(user_settings)
            return user_settings
    except Exception as e:
        print(f"Erro ao carregar configurações do usuário: {e}")
    
    return None

def apply_user_settings(user_settings):
    """Aplica as configurações do usuário globalmente."""
    try:
        # Importar módulo settings diretamente para modificar variáveis globais
        import config.settings as settings
        
        print(f"🎨 Aplicando configurações do usuário: {user_settings}")
        
        # Aplicar tema PRIMEIRO e IMEDIATAMENTE
        if "theme" in user_settings:
            theme = user_settings["theme"]
            print(f"🎨 Aplicando tema: {theme}")
            
            # Atualizar variáveis globais ANTES de aplicar no CustomTkinter
            settings.UI_THEME = theme
            settings.THEME_MODE = theme
            settings.THEME_SETTINGS["current_theme"] = theme
            
            # Aplicar tema no CustomTkinter IMEDIATAMENTE
            import customtkinter as ctk
            
            # Força aplicação do tema
            if theme == "light":
                print("   🌞 Configurando CustomTkinter para tema LIGHT")
                ctk.set_appearance_mode("light")
                print("   ✅ Tema LIGHT aplicado com sucesso")
            else:  # dark ou qualquer outro valor
                print("   🌙 Configurando CustomTkinter para tema DARK") 
                ctk.set_appearance_mode("dark")
                print("   ✅ Tema DARK aplicado com sucesso")
            
            print(f"   🎨 Tema {theme} configurado globalmente no CustomTkinter")
        
        # Aplicar modelo
        if "model" in user_settings:
            settings.GEMINI_MODEL = user_settings["model"]
            print(f"🤖 Modelo definido: {settings.GEMINI_MODEL}")
        
        # Aplicar configurações do modelo
        if "temperature" in user_settings:
            settings.MODEL_SETTINGS["temperature"] = user_settings["temperature"]
            print(f"🌡️ Temperature: {user_settings['temperature']}")
        
        if "max_tokens" in user_settings:
            settings.MODEL_SETTINGS["max_output_tokens"] = user_settings["max_tokens"]
            print(f"📝 Max tokens: {user_settings['max_tokens']}")
        
        # Aplicar streaming
        if "streaming" in user_settings:
            settings.STREAMING_SETTINGS["enabled"] = user_settings["streaming"]
            print(f"🔄 Streaming: {user_settings['streaming']}")
            
        # Aplicar auto-save
        if "auto_save" in user_settings:
            settings.AUTOSAVE_SETTINGS["enabled"] = user_settings["auto_save"]
            print(f"💾 Auto-save: {user_settings['auto_save']}")
            
        # Aplicar notificações
        if "notifications" in user_settings:
            settings.NOTIFICATION_SETTINGS["enabled"] = user_settings["notifications"]
            print(f"🔔 Notificações: {user_settings['notifications']}")
            
        print(f"✅ TODAS as configurações do usuário aplicadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar configurações do usuário: {e}")
        import traceback
        traceback.print_exc()
        return False
        print(f"   Tema atual: {settings.UI_THEME}")
        print(f"   Modelo atual: {settings.GEMINI_MODEL}")
        
        if "streaming" in user_settings:
            settings.STREAMING_SETTINGS["enabled"] = user_settings["streaming"]
        
        print(f"✅ Configurações do usuário aplicadas: tema={settings.UI_THEME}, modelo={settings.GEMINI_MODEL}")
        
    except Exception as e:
        print(f"❌ Erro ao aplicar configurações: {e}")
        import traceback
        traceback.print_exc()

def save_current_settings_to_file():
    """Salva as configurações atuais para arquivo."""
    try:
        import config.settings as settings
        
        current_settings = {
            "model": settings.GEMINI_MODEL,
            "temperature": settings.MODEL_SETTINGS["temperature"],
            "max_tokens": settings.MODEL_SETTINGS["max_output_tokens"],
            "theme": settings.UI_THEME,
            "streaming": settings.STREAMING_SETTINGS["enabled"],
            "auto_save": settings.AUTOSAVE_SETTINGS["enabled"],
            "notifications": settings.NOTIFICATION_SETTINGS["enabled"]
        }
        
        with open("user_settings.json", "w", encoding="utf-8") as f:
            json.dump(current_settings, f, indent=2, ensure_ascii=False)
        
        print("✅ Configurações salvas em user_settings.json")
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

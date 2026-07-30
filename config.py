import os
from dotenv import load_dotenv

# Carrega o arquivo .env se ele existir no diretório local.
# Se estiver rodando no GitHub Actions, a função não falha e o os.getenv
# vai buscar automaticamente das Secrets do ambiente.
load_dotenv()

def get_config():
    load_dotenv()
    
    required_keys = [
        "REDMINE_URL",
        "REDMINE_API_KEY",
        "CLOCKIFY_API_KEY",
        "CLOCKIFY_WORKSPACE_ID",
        "DEFAULT_REDMINE_ACTIVITY_ID"
    ]
    
    config = {}
    missing_keys = []
    
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            missing_keys.append(key)
        config[key] = value

    if missing_keys:
        raise ValueError(f"⚠️ As seguintes variáveis de ambiente estão faltando: {', '.join(missing_keys)}")

    # Discord Webhook é opcional
    config["DISCORD_WEBHOOK_URL"] = os.getenv("DISCORD_WEBHOOK_URL")

    return config
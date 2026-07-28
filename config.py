import os
from dotenv import load_dotenv

# Carrega o arquivo .env se ele existir no diretório local.
# Se estiver rodando no GitHub Actions, a função não falha e o os.getenv
# vai buscar automaticamente das Secrets do ambiente.
load_dotenv()

def get_config():
    """Retorna as configurações carregadas do ambiente (.env local ou Secrets do GitHub)."""
    config = {
        "REDMINE_URL": os.getenv("REDMINE_URL"),
        "REDMINE_API_KEY": os.getenv("REDMINE_API_KEY"),
        "CLOCKIFY_API_KEY": os.getenv("CLOCKIFY_API_KEY"),
        "CLOCKIFY_WORKSPACE_ID": os.getenv("CLOCKIFY_WORKSPACE_ID"),
        "DEFAULT_REDMINE_ACTIVITY_ID": int(os.getenv("DEFAULT_REDMINE_ACTIVITY_ID", "9"))
    }

    # Validação para garantir que nenhuma variável obrigatória ficou vazia
    required_keys = ["REDMINE_URL", "REDMINE_API_KEY", "CLOCKIFY_API_KEY", "CLOCKIFY_WORKSPACE_ID"]
    missing_keys = [key for key in required_keys if not config[key]]

    if missing_keys:
        raise ValueError(
            f"❌ Configurações ausentes: {', '.join(missing_keys)}.\n"
            "Verifique se o arquivo .env local existe ou se as Secrets no GitHub foram cadastradas."
        )

    return config
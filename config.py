import json
import os

CONFIG_FILE = "config.json"

def load_config():
    """Carrega as configurações a partir do arquivo config.json."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"Arquivo de configuração '{CONFIG_FILE}' não encontrado. "
            "Certifique-se de criar o arquivo a partir do modelo."
        )
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

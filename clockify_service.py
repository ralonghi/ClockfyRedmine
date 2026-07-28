import re
import requests
from datetime import datetime

def get_user_id(headers):
    """Obtém o ID do usuário no Clockify."""
    url = "https://api.clockify.me/api/v1/user"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()["id"]

def get_time_entries_by_date(headers, workspace_id, user_id, target_date_str):
    """Busca as entradas de tempo para uma data específica (YYYY-MM-DD)."""
    url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{user_id}/time-entries"
    params = {
        "start": f"{target_date_str}T00:00:00Z",
        "end": f"{target_date_str}T23:59:59Z",
        "page-size": 50
    }
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    return res.json()

def extract_redmine_issue_id(description):
    """Extrai o #ID do Redmine presente na descrição."""
    if not description:
        return None
    match = re.search(r'#(\d+)', description)
    return int(match.group(1)) if match else None

def parse_duration_to_hours(start_str, end_str):
    """Calcula a duração em horas decimais."""
    if not end_str:
        return 0.0
    start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
    return round((end - start).total_seconds() / 3600.0, 2)

def extract_comment(description):
    """Extrai o comentário que estiver APÓS o separador '--'."""
    if not description or "--" not in description:
        return ""
    return description.split("--", 1)[1].strip()
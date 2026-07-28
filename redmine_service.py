import requests

def get_current_user_id(redmine_url, headers):
    """Obtém o ID do usuário dono da API Key no Redmine."""
    url = f"{redmine_url.rstrip('/')}/users/current.json"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json().get("user", {}).get("id")

def delete_user_time_entries(redmine_url, headers, user_id, target_date_str):
    """Deleta EXCLUSIVAMENTE os lançamentos do próprio usuário na data especificada."""
    url = f"{redmine_url.rstrip('/')}/time_entries.json"
    params = {
        "user_id": user_id,
        "spent_on": target_date_str,
        "limit": 100
    }
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    
    entries = res.json().get("time_entries", [])
    if not entries:
        print(f"ℹ️  Nenhum registro prévio seu encontrado no Redmine para {target_date_str}.")
        return

    print(f"🧹 Deletando {len(entries)} registro(s) anterior(es) SEUS no Redmine para {target_date_str}...")
    
    for entry in entries:
        entry_id = entry["id"]
        del_url = f"{redmine_url.rstrip('/')}/time_entries/{entry_id}.json"
        del_res = requests.delete(del_url, headers=headers)
        if del_res.status_code in (200, 204):
            print(f"   🗑️  Lançamento anterior #{entry_id} removido com sucesso.")
        else:
            print(f"   ⚠️  Falha ao remover lançamento #{entry_id}: {del_res.text}")

def post_time_entry(redmine_url, headers, activity_id, issue_id, spent_on, hours, comments):
    """Registra uma nova entrada de tempo no Redmine."""
    url = f"{redmine_url.rstrip('/')}/time_entries.json"
    payload = {
        "time_entry": {
            "issue_id": issue_id,
            "spent_on": spent_on,
            "hours": hours,
            "activity_id": activity_id,
            "comments": comments
        }
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code == 201, res.text
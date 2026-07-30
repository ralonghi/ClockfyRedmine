import requests

def get_current_user_id(redmine_url, headers):
    """Obtém o ID do usuário dono da API Key no Redmine."""
    url = f"{redmine_url.rstrip('/')}/users/current.json"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json().get("user", {}).get("id")

def get_issue_subject(redmine_url, headers, issue_id):
    """Busca o título/assunto de uma issue no Redmine."""
    url = f"{redmine_url.rstrip('/')}/issues/{issue_id}.json"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get("issue", {}).get("subject", "Sem título")
    except Exception:
        pass
    return "Sem título"

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

def send_error_notification(target_date, error_message, webhook_url=None):
    """Envia um alerta destacado de falha/erro para o Discord."""
    lines = []
    lines.append("============================================================")
    lines.append("🚨 **FALHA NA SINCRONIZAÇÃO CLOCKIFY -> REDMINE**")
    lines.append("============================================================")
    lines.append(f"**Data de execução:** {target_date}")
    lines.append(f"**Erro:** `{error_message}`")
    lines.append("\n💡 *Verifique os logs no GitHub Actions para mais detalhes.*")
    lines.append("============================================================")

    full_message = "\n".join(lines)
    
    # Imprime no terminal
    print(full_message)

    # Envia para o Discord
    if webhook_url:
        send_discord_message(webhook_url, full_message)
import re
import requests
from datetime import datetime
from collections import defaultdict
from config import load_config

def get_clockify_user_id(clockify_headers):
    """Obtém o ID do usuário logado no Clockify."""
    url = "https://api.clockify.me/api/v1/user"
    res = requests.get(url, headers=clockify_headers)
    res.raise_for_status()
    return res.json()["id"]

def get_clockify_time_entries_by_date(clockify_headers, workspace_id, user_id, target_date_str):
    """Busca as entradas de tempo para uma data específica (YYYY-MM-DD)."""
    url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{user_id}/time-entries"
    
    start_iso = f"{target_date_str}T00:00:00Z"
    end_iso = f"{target_date_str}T23:59:59Z"
    
    params = {
        "start": start_iso,
        "end": end_iso,
        "page-size": 50
    }
    res = requests.get(url, headers=clockify_headers, params=params)
    res.raise_for_status()
    return res.json()

def extract_redmine_issue_id(description):
    """Extrai o ID da issue no padrão #1234."""
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
    
    duration = (end - start).total_seconds() / 3600.0
    return round(duration, 2)

def post_time_entry_to_redmine(redmine_url, redmine_headers, default_activity_id, issue_id, spent_on, hours, comments):
    """Envia o apontamento de horas para o Redmine."""
    url = f"{redmine_url.rstrip('/')}/time_entries.json"
    payload = {
        "time_entry": {
            "issue_id": issue_id,
            "spent_on": spent_on,
            "hours": hours,
            "activity_id": default_activity_id,
            "comments": comments
        }
    }
    res = requests.post(url, headers=redmine_headers, json=payload)
    return res.status_code == 201, res.text

def main():
    print("=== Sincronizador Clockify -> Redmine ===")
    
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        return

    clockify_headers = {
        "X-Api-Key": config["CLOCKIFY_API_KEY"],
        "Content-Type": "application/json"
    }

    redmine_headers = {
        "X-Redmine-API-Key": config["REDMINE_API_KEY"],
        "Content-Type": "application/json"
    }

    # 1. Escolha da data
    data_input = input("Informe a data que deseja sincronizar (YYYY-MM-DD) [Aperte ENTER para HOJE]: ").strip()
    
    if not data_input:
        target_date = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            target_date = datetime.strptime(data_input, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print("❌ Formato de data inválido! Use o formato YYYY-MM-DD.")
            return

    # 2. Modo de teste
    dry_run_input = input("Deseja rodar em MODO DE TESTE (sem enviar ao Redmine)? (s/N): ").strip().lower()
    dry_run = dry_run_input == 's'

    print(f"\n🔎 Buscando apontamentos no Clockify para o dia: {target_date}...")
    
    try:
        user_id = get_clockify_user_id(clockify_headers)
        entries = get_clockify_time_entries_by_date(
            clockify_headers, config["CLOCKIFY_WORKSPACE_ID"], user_id, target_date
        )
    except Exception as e:
        print(f"❌ Erro ao buscar dados do Clockify: {e}")
        return
    
    print(f"Encontrados {len(entries)} registros brutos no Clockify.")

    # ---------------------------------------------------------
    # AGRUPAMENTO POR ISSUE ID
    # ---------------------------------------------------------
    grouped_entries = defaultdict(lambda: {"total_hours": 0.0, "descriptions": []})

    for entry in entries:
        description = entry.get("description", "").strip()
        issue_id = extract_redmine_issue_id(description)
        
        if not issue_id:
            print(f"⚠️  Ignorado: '{description}' (Nenhum #ID encontrado).")
            continue
        
        time_interval = entry.get("timeInterval", {})
        start_time = time_interval.get("start")
        end_time = time_interval.get("end")
        
        hours = parse_duration_to_hours(start_time, end_time)
        if hours <= 0:
            print(f"⚠️  Ignorado Issue #{issue_id}: Duração zerada ou timer em andamento.")
            continue
        
        # Agrupa horas e comentários
        grouped_entries[issue_id]["total_hours"] += hours
        if description and description not in grouped_entries[issue_id]["descriptions"]:
            grouped_entries[issue_id]["descriptions"].append(description)

    print(f"\n📊 Total de {len(grouped_entries)} Issue(s) única(s) consolidada(s) para o dia.\n")

    # ---------------------------------------------------------
    # ENVIO PAR O REDMINE
    # ---------------------------------------------------------
    for issue_id, data in grouped_entries.items():
        total_hours = round(data["total_hours"], 2)
        # Junta as descrições únicas em uma string só
        combined_comment = " | ".join(data["descriptions"])
        
        if dry_run:
            print(f"🧪 [SIMULAÇÃO] Lançaria {total_hours}h na Issue #{issue_id} ({target_date}) - Comentário: '{combined_comment}'")
        else:
            success, response = post_time_entry_to_redmine(
                config["REDMINE_URL"],
                redmine_headers,
                config["DEFAULT_REDMINE_ACTIVITY_ID"],
                issue_id,
                target_date,
                total_hours,
                combined_comment
            )
            if success:
                print(f"✅ Sucesso: {total_hours}h lançadas na Issue #{issue_id} ('{combined_comment}')")
            else:
                print(f"❌ Erro na Issue #{issue_id}: {response}")

if __name__ == "__main__":
    main()
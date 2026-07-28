import sys
from datetime import datetime, timedelta
from collections import defaultdict

from config import get_config
import clockify_service as clockify
import redmine_service as redmine

def main():
    print("=== Sincronizador Clockify -> Redmine ===")

    try:
        cfg = get_config()
    except ValueError as e:
        print(e)
        return

    # Define a data do parâmetro CLI ou assume D-1 por padrão
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
        print(f"🎯 Modo Manual/Teste: Processando data informada: {target_date}")
    else:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"🔎 Modo Automático: Processando dia anterior: {target_date}")

    clockify_headers = {"X-Api-Key": cfg["CLOCKIFY_API_KEY"], "Content-Type": "application/json"}
    redmine_headers = {"X-Redmine-API-Key": cfg["REDMINE_API_KEY"], "Content-Type": "application/json"}

    # 1. Limpeza segura no Redmine
    try:
        redmine_user_id = redmine.get_current_user_id(cfg["REDMINE_URL"], redmine_headers)
        redmine.delete_user_time_entries(cfg["REDMINE_URL"], redmine_headers, redmine_user_id, target_date)
    except Exception as e:
        print(f"⚠️  Erro ao verificar/limpar lançamentos antigos no Redmine: {e}")
        return

    # 2. Busca lançamentos no Clockify
    try:
        clockify_user_id = clockify.get_user_id(clockify_headers)
        entries = clockify.get_time_entries_by_date(
            clockify_headers, cfg["CLOCKIFY_WORKSPACE_ID"], clockify_user_id, target_date
        )
    except Exception as e:
        print(f"❌ Erro na API do Clockify: {e}")
        return

    # 3. Consolidação e Agrupamento por Issue
    grouped_entries = defaultdict(lambda: {"total_hours": 0.0, "comments": []})
    unlinked_entries = []

    for entry in entries:
        description = entry.get("description", "").strip()
        issue_id = clockify.extract_redmine_issue_id(description)
        
        time_interval = entry.get("timeInterval", {})
        hours = clockify.parse_duration_to_hours(time_interval.get("start"), time_interval.get("end"))
        
        if hours <= 0:
            continue

        if not issue_id:
            unlinked_entries.append({"description": description or "(Sem descrição)", "hours": hours})
            continue

        comment = clockify.extract_comment(description)

        grouped_entries[issue_id]["total_hours"] += hours
        if comment and comment not in grouped_entries[issue_id]["comments"]:
            grouped_entries[issue_id]["comments"].append(comment)

    # 4. Envio dos dados consolidados ao Redmine
    print(f"\n📊 Total de {len(grouped_entries)} issue(s) consolidada(s) para lançamento.")

    for issue_id, data in grouped_entries.items():
        total_hours = round(data["total_hours"], 2)
        combined_comment = " | ".join(data["comments"])

        success, response = redmine.post_time_entry(
            cfg["REDMINE_URL"],
            redmine_headers,
            cfg["DEFAULT_REDMINE_ACTIVITY_ID"],
            issue_id,
            target_date,
            total_hours,
            combined_comment
        )
        if success:
            comment_log = f" ('{combined_comment}')" if combined_comment else " (Sem comentário)"
            print(f"✅ Sucesso: {total_hours}h lançadas na Issue #{issue_id}{comment_log}")
        else:
            print(f"❌ Erro na Issue #{issue_id}: {response}")

    # 5. Alerta de registros não vinculados
    if unlinked_entries:
        total_unlinked_hours = sum(e["hours"] for e in unlinked_entries)
        print("\n" + "="*60)
        print("⚠️  ATENÇÃO: EXISTEM REGISTROS NÃO VINCULADOS AO REDMINE!")
        print(f"Foram encontrados {len(unlinked_entries)} apontamento(s) sem #ID ({total_unlinked_hours}h no total).")
        print("Estes registros NÃO foram sincronizados:\n")
        
        for item in unlinked_entries:
            print(f"  • {item['hours']}h - '{item['description']}'")
            
        print("\n💡 RECOMENDAÇÃO: Corrija os registros no Clockify adicionando o #ID ")
        print(f"   e rode novamente o script para a data {target_date}:")
        print(f"   python main.py {target_date}")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
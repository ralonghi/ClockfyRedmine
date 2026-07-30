import sys
import io
from datetime import datetime, timedelta
from collections import defaultdict

from config import get_config
import clockify_service as clockify
import redmine_service as redmine
import reporter_service as reporter

# Garante UTF-8 no console do Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("=== Sincronizador Clockify -> Redmine ===")

    # 1. Carrega configurações
    try:
        cfg = get_config()
    except Exception as e:
        error_msg = f"Erro nas variáveis de ambiente: {e}"
        print(error_msg)
        return

    # Define a data (CLI ou D-1 por padrão)
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
        print(f"🎯 Modo Manual/Teste: Processando data informada: {target_date}")
    else:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"🔎 Modo Automático: Processando dia anterior: {target_date}")

    webhook_url = cfg.get("DISCORD_WEBHOOK_URL")
    clockify_headers = {"X-Api-Key": cfg["CLOCKIFY_API_KEY"], "Content-Type": "application/json"}
    redmine_headers = {"X-Redmine-API-Key": cfg["REDMINE_API_KEY"], "Content-Type": "application/json"}

    try:
        # 2. Limpeza segura no Redmine
        redmine_user_id = redmine.get_current_user_id(cfg["REDMINE_URL"], redmine_headers)
        redmine.delete_user_time_entries(cfg["REDMINE_URL"], redmine_headers, redmine_user_id, target_date)

        # 3. Busca lançamentos no Clockify
        clockify_user_id = clockify.get_user_id(clockify_headers)
        entries = clockify.get_time_entries_by_date(
            clockify_headers, cfg["CLOCKIFY_WORKSPACE_ID"], clockify_user_id, target_date
        )

        # 4. Consolidação dos Dados
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

        # 4.1 Busca título das issues
        for issue_id in grouped_entries.keys():
            grouped_entries[issue_id]["subject"] = redmine.get_issue_subject(
                cfg["REDMINE_URL"], redmine_headers, issue_id
            )

        # 5. Envio ao Redmine
        print(f"\n📊 Total de {len(grouped_entries)} issue(s) consolidada(s) para lançamento.")
        for issue_id, data in grouped_entries.items():
            total_hours = round(data["total_hours"], 2)
            combined_comment = " | ".join(data["comments"])

            success, response = redmine.post_time_entry(
                cfg["REDMINE_URL"], redmine_headers, cfg["DEFAULT_REDMINE_ACTIVITY_ID"],
                issue_id, target_date, total_hours, combined_comment
            )
            if success:
                comment_log = f" ('{combined_comment}')" if combined_comment else " (Sem comentário)"
                print(f"✅ Sucesso: {total_hours}h lançadas na Issue #{issue_id}{comment_log}")
            else:
                print(f"❌ Erro na Issue #{issue_id}: {response}")

        # 6. Relatórios e Alertas de Sucesso
        reporter.print_daily_summary(target_date, grouped_entries, webhook_url)
        reporter.print_unlinked_entries_warning(target_date, unlinked_entries, webhook_url)

    except Exception as e:
        # Se qualquer exceção estourar durante o processo, notifica no Discord
        reporter.send_error_notification(target_date, str(e), webhook_url)
        sys.exit(1) # Força o GitHub Actions a reconhecer que o job falhou

if __name__ == "__main__":
    main()
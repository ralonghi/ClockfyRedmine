import requests

def send_discord_message(webhook_url, message):
    """Envia uma mensagem formatada para o Discord via Webhook."""
    if not webhook_url:
        return
    try:
        payload = {"content": message}
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print(f"⚠️ Erro ao enviar notificação para o Discord: {e}")

def print_daily_summary(target_date, grouped_entries, webhook_url=None):
    """Gera o resumo formatado para a reunião Daily com os títulos das issues."""
    total_day_hours = sum(d["total_hours"] for d in grouped_entries.values())
    total_day_hours_rounded = round(total_day_hours, 2)

    lines = []
    lines.append("============================================================")
    lines.append(f"📋 **RESUMO PARA A DAILY (ONTEM - {target_date})**")
    lines.append("============================================================")

    if grouped_entries:
        for issue_id, data in grouped_entries.items():
            subject = data.get("subject", "Sem título")
            desc = " | ".join(data["comments"]) if data["comments"] else "Sem descrição"
            lines.append(f"• **#{issue_id}** [{subject}], {desc}")
    else:
        lines.append("ℹ️ Nenhum lançamento com issue encontrado para esta data.")

    lines.append(f"\n⏱️ **Total de horas sincronizadas:** {total_day_hours_rounded}h / 8.00h")

    # Alerta de carga horária insuficiente
    if total_day_hours_rounded < 8.0:
        missing_hours = round(8.0 - total_day_hours_rounded, 2)
        lines.append("\n⚠️ **ALERTA DE CARGA HORÁRIA:**")
        lines.append(f"   A soma total de horas ({total_day_hours_rounded}h) é **INFERIOR** a 08:00h!")
        lines.append(f"   Faltam **{missing_hours}h** para completar a jornada diária.")
    
    lines.append("============================================================")

    full_message = "\n".join(lines)
    
    # Imprime no terminal
    print(full_message)

    # Envia para o Discord
    if webhook_url:
        send_discord_message(webhook_url, full_message)

def print_unlinked_entries_warning(target_date, unlinked_entries, webhook_url=None):
    """Exibe alerta destacado caso existam horas sem #ID no Clockify."""
    if not unlinked_entries:
        return

    total_unlinked_hours = round(sum(e["hours"] for e in unlinked_entries), 2)
    
    lines = []
    lines.append("\n============================================================")
    lines.append("⚠️ **ATENÇÃO: EXISTEM REGISTROS NÃO VINCULADOS AO REDMINE!**")
    lines.append(f"Foram encontrados **{len(unlinked_entries)}** apontamento(s) sem #ID ({total_unlinked_hours}h no total).")
    lines.append("Estes registros **NÃO** foram sincronizados:\n")
    
    for item in unlinked_entries:
        lines.append(f"  • {item['hours']}h - `{item['description']}`")
        
    lines.append(f"\n💡 **RECOMENDAÇÃO:** Corrija os registros no Clockify adicionando o #ID e rode novamente o script para {target_date}.")
    lines.append("============================================================")

    full_message = "\n".join(lines)

    # Imprime no terminal
    print(full_message)

    # Envia para o Discord
    if webhook_url:
        send_discord_message(webhook_url, full_message)

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
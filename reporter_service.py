def print_daily_summary(target_date, grouped_entries):
    """Gera o resumo formatado para a reunião Daily e valida a carga horária de 8h."""
    total_day_hours = sum(d["total_hours"] for d in grouped_entries.values())
    total_day_hours_rounded = round(total_day_hours, 2)

    print("\n" + "="*60)
    print(f"📋 RESUMO PARA A DAILY (ONTEM - {target_date})")
    print("="*60)

    if grouped_entries:
        for issue_id, data in grouped_entries.items():
            hrs = round(data["total_hours"], 2)
            desc = " | ".join(data["comments"]) if data["comments"] else "Sem descrição detalhada"
            print(f"• Issue #{issue_id} ({hrs}h): {desc}")
    else:
        print("ℹ️ Nenhum lançamento com issue encontrado para esta data.")

    print(f"\n⏱️ Total de horas sincronizadas: {total_day_hours_rounded}h / 8.00h")

    # Alerta se a carga horária for inferior a 8h
    if total_day_hours_rounded < 8.0:
        missing_hours = round(8.0 - total_day_hours_rounded, 2)
        print("\n⚠️  ALERTA DE CARGA HORÁRIA:")
        print(f"   A soma total de horas ({total_day_hours_rounded}h) é INFERIOR a 08:00h!")
        print(f"   Faltam {missing_hours}h para completar a jornada diária.")
    
    print("="*60)

def print_unlinked_entries_warning(target_date, unlinked_entries):
    """Exibe alerta destacado caso existam horas sem #ID no Clockify."""
    if not unlinked_entries:
        return

    total_unlinked_hours = round(sum(e["hours"] for e in unlinked_entries), 2)
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
import pytest
from unittest.mock import patch, MagicMock
import reporter_service as reporter

WEBHOOK_URL = "https://discord.com/api/webhooks/dummy"

@patch("reporter_service.requests.post")
def test_send_discord_message(mock_post):
    reporter.send_discord_message(WEBHOOK_URL, "Teste de mensagem")
    mock_post.assert_called_once_with(WEBHOOK_URL, json={"content": "Teste de mensagem"})

@patch("reporter_service.requests.post")
def test_send_discord_message_none_url(mock_post):
    reporter.send_discord_message(None, "Mensagem ignorada")
    mock_post.assert_not_called()

@patch("reporter_service.send_discord_message")
def test_print_daily_summary_complete_day(mock_send):
    grouped_entries = {
        102023: {
            "subject": "Ajuste no Painel",
            "total_hours": 8.0,
            "comments": ["Desenvolvimento de nova feature"]
        }
    }
    reporter.print_daily_summary("2026-08-02", grouped_entries, WEBHOOK_URL)

    mock_send.assert_called_once()
    message = mock_send.call_args[0][1]
    assert "#102023" in message
    assert "8.0h / 8.00h" in message
    assert "ALERTA DE CARGA HORÁRIA" not in message

@patch("reporter_service.send_discord_message")
def test_print_daily_summary_incomplete_day_alert(mock_send):
    grouped_entries = {
        102023: {
            "subject": "Ajuste no Painel",
            "total_hours": 5.5,
            "comments": ["Refatoração parcial"]
        }
    }
    reporter.print_daily_summary("2026-08-02", grouped_entries, WEBHOOK_URL)

    mock_send.assert_called_once()
    message = mock_send.call_args[0][1]
    assert "5.5h / 8.00h" in message
    assert "ALERTA DE CARGA HORÁRIA" in message
    assert "Faltam **2.5h**" in message

@patch("reporter_service.send_discord_message")
def test_print_unlinked_entries_warning(mock_send):
    unlinked_entries = [
        {"description": "Reunião de alinhamento sem ID", "hours": 1.5}
    ]
    reporter.print_unlinked_entries_warning("2026-08-02", unlinked_entries, WEBHOOK_URL)

    mock_send.assert_called_once()
    message = mock_send.call_args[0][1]
    assert "EXISTEM REGISTROS NÃO VINCULADOS AO REDMINE!" in message
    assert "1.5h" in message

@patch("reporter_service.send_discord_message")
def test_print_unlinked_entries_warning_empty(mock_send):
    reporter.print_unlinked_entries_warning("2026-08-02", [], WEBHOOK_URL)
    mock_send.assert_not_called()

@patch("reporter_service.send_discord_message")
def test_send_error_notification(mock_send):
    reporter.send_error_notification("2026-08-02", "Erro de conexão com o banco", WEBHOOK_URL)
    mock_send.assert_called_once()
    message = mock_send.call_args[0][1]
    assert "FALHA NA SINCRONIZAÇÃO" in message
    assert "Erro de conexão com o banco" in message

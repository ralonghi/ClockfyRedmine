import pytest
from unittest.mock import patch, MagicMock
import clockify_service as clockify

def test_extract_redmine_issue_id():
    assert clockify.extract_redmine_issue_id("#102023 Validando erro com UX") == 102023
    assert clockify.extract_redmine_issue_id("Ajuste geral #999 na controller") == 999
    assert clockify.extract_redmine_issue_id("Sem id de issue") is None
    assert clockify.extract_redmine_issue_id("") is None
    assert clockify.extract_redmine_issue_id(None) is None

def test_extract_comment():
    assert clockify.extract_comment("#102023 -- Comentário do apontamento") == "Comentário do apontamento"
    assert clockify.extract_comment("#102023 Sem separador") == ""
    assert clockify.extract_comment("") == ""
    assert clockify.extract_comment(None) == ""

def test_parse_duration_to_hours():
    start = "2026-08-02T08:00:00Z"
    end = "2026-08-02T12:30:00Z"
    assert clockify.parse_duration_to_hours(start, end) == 4.5

    # Test when end is missing/running timer
    assert clockify.parse_duration_to_hours(start, None) == 0.0

@patch("clockify_service.requests.get")
def test_get_user_id(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "usr_12345"}
    mock_get.return_value = mock_response

    headers = {"X-Api-Key": "dummy_key"}
    user_id = clockify.get_user_id(headers)

    assert user_id == "usr_12345"
    mock_get.assert_called_once_with("https://api.clockify.me/api/v1/user", headers=headers)

@patch("clockify_service.requests.get")
def test_get_time_entries_by_date(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"id": "entry_1", "description": "#100 test"},
        {"id": "entry_2", "description": "#101 test2"}
    ]
    mock_get.return_value = mock_response

    headers = {"X-Api-Key": "dummy_key"}
    entries = clockify.get_time_entries_by_date(headers, "ws_123", "usr_123", "2026-08-02")

    assert len(entries) == 2
    assert entries[0]["id"] == "entry_1"
    mock_get.assert_called_once()

import pytest
from unittest.mock import patch, MagicMock
import redmine_service as redmine

REDMINE_URL = "https://redmine.example.com"
HEADERS = {"X-Redmine-API-Key": "test_key", "Content-Type": "application/json"}

@patch("redmine_service.requests.get")
def test_get_current_user_id(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"user": {"id": 42, "name": "John"}}
    mock_get.return_value = mock_response

    user_id = redmine.get_current_user_id(REDMINE_URL, HEADERS)
    assert user_id == 42
    mock_get.assert_called_once_with(f"{REDMINE_URL}/users/current.json", headers=HEADERS)

@patch("redmine_service.requests.get")
def test_get_issue_subject_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"issue": {"id": 100, "subject": "Fix login bug"}}
    mock_get.return_value = mock_response

    subject = redmine.get_issue_subject(REDMINE_URL, HEADERS, 100)
    assert subject == "Fix login bug"

@patch("redmine_service.requests.get")
def test_get_issue_subject_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    subject = redmine.get_issue_subject(REDMINE_URL, HEADERS, 99999)
    assert subject == "Sem título"

@patch("redmine_service.requests.delete")
@patch("redmine_service.requests.get")
def test_delete_user_time_entries(mock_get, mock_delete):
    mock_get_res = MagicMock()
    mock_get_res.json.return_value = {
        "time_entries": [
            {"id": 10, "hours": 2.0},
            {"id": 11, "hours": 3.0}
        ]
    }
    mock_get.return_value = mock_get_res

    mock_del_res = MagicMock()
    mock_del_res.status_code = 204
    mock_delete.return_value = mock_del_res

    redmine.delete_user_time_entries(REDMINE_URL, HEADERS, 42, "2026-08-02")

    mock_get.assert_called_once()
    assert mock_delete.call_count == 2

@patch("redmine_service.requests.post")
def test_post_time_entry_success(mock_post):
    mock_res = MagicMock()
    mock_res.status_code = 201
    mock_res.text = '{"time_entry":{"id":500}}'
    mock_post.return_value = mock_res

    success, response_text = redmine.post_time_entry(
        REDMINE_URL, HEADERS, 9, 102023, "2026-08-02", 4.5, "Desenvolvimento"
    )

    assert success is True
    assert "500" in response_text
    mock_post.assert_called_once()

@patch("redmine_service.requests.post")
def test_post_time_entry_failure(mock_post):
    mock_res = MagicMock()
    mock_res.status_code = 422
    mock_res.text = "Unprocessable Entity"
    mock_post.return_value = mock_res

    success, response_text = redmine.post_time_entry(
        REDMINE_URL, HEADERS, 9, 102023, "2026-08-02", 4.5, "Desenvolvimento"
    )

    assert success is False
    assert response_text == "Unprocessable Entity"

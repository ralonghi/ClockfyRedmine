import os
import pytest
from unittest.mock import patch
from config import get_config

@patch("config.load_dotenv")
def test_get_config_success(mock_load_dotenv):
    dummy_env = {
        "REDMINE_URL": "https://redmine.example.com",
        "REDMINE_API_KEY": "redmine_key_123",
        "CLOCKIFY_API_KEY": "clockify_key_123",
        "CLOCKIFY_WORKSPACE_ID": "ws_123",
        "DEFAULT_REDMINE_ACTIVITY_ID": "9",
        "DISCORD_WEBHOOK_URL": "https://discord.example.com/webhook"
    }
    with patch.dict(os.environ, dummy_env, clear=True):
        cfg = get_config()
        assert cfg["REDMINE_URL"] == "https://redmine.example.com"
        assert cfg["REDMINE_API_KEY"] == "redmine_key_123"
        assert cfg["CLOCKIFY_API_KEY"] == "clockify_key_123"
        assert cfg["CLOCKIFY_WORKSPACE_ID"] == "ws_123"
        assert cfg["DEFAULT_REDMINE_ACTIVITY_ID"] == "9"
        assert cfg["DISCORD_WEBHOOK_URL"] == "https://discord.example.com/webhook"

@patch("config.load_dotenv")
def test_get_config_missing_keys(mock_load_dotenv):
    dummy_env = {
        "REDMINE_URL": "https://redmine.example.com"
    }
    with patch.dict(os.environ, dummy_env, clear=True):
        with pytest.raises(ValueError) as excinfo:
            get_config()
        assert "REDMINE_API_KEY" in str(excinfo.value)
        assert "CLOCKIFY_API_KEY" in str(excinfo.value)


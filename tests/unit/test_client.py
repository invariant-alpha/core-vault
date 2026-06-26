import os
import pytest
from unittest.mock import patch, MagicMock

from core_vault.config import VaultConfig
from core_vault.client import VaultClient
from core_vault.exceptions import SecretNotFoundError, VaultConfigurationError

def test_development_mode_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_SECRET=super_secret_value\n")
    
    config = VaultConfig(environment="development", env_file_path=str(env_file))
    client = VaultClient(config)
    
    assert client.get_secret("TEST_SECRET") == "super_secret_value"

def test_development_mode_fallback_os_environ(tmp_path):
    # .env doesn't exist, should fallback to os.environ
    env_file = tmp_path / "nonexistent.env"
    
    config = VaultConfig(environment="development", env_file_path=str(env_file))
    
    with patch.dict(os.environ, {"OS_SECRET": "os_value"}):
        client = VaultClient(config)
        assert client.get_secret("OS_SECRET") == "os_value"

def test_development_mode_secret_not_found(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OTHER_SECRET=value\n")
    
    config = VaultConfig(environment="development", env_file_path=str(env_file))
    client = VaultClient(config)
    
    with pytest.raises(SecretNotFoundError):
        client.get_secret("MISSING_SECRET")

def test_production_mode_missing_token():
    config = VaultConfig(environment="production", infisical_token=None)
    with pytest.raises(VaultConfigurationError, match="infisical_token is required"):
        VaultClient(config)

@patch("core_vault.client.InfisicalClient", create=True)
def test_production_mode_success(mock_infisical_client_class):
    mock_instance = MagicMock()
    mock_infisical_client_class.return_value = mock_instance
    
    # Mocking the response structure
    mock_secret = MagicMock()
    mock_secret.secretValue = "prod_secret_value"
    mock_instance.getSecret.return_value = mock_secret
    
    # Needs to mock the import successfully
    import sys
    sys.modules['infisical_client'] = MagicMock()
    sys.modules['infisical_client'].InfisicalClient = mock_infisical_client_class
    
    config = VaultConfig(environment="production", infisical_token="test_token")
    client = VaultClient(config)
    
    assert client.get_secret("PROD_SECRET") == "prod_secret_value"
    mock_instance.getSecret.assert_called_once_with(secretName="PROD_SECRET")
    
    # Cleanup mock module
    del sys.modules['infisical_client']

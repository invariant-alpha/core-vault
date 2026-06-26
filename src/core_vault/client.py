import os
import logging
from typing import Optional, Dict

from dotenv import dotenv_values
from .config import VaultConfig
from .exceptions import SecretNotFoundError, VaultConfigurationError

logger = logging.getLogger(__name__)

class VaultClient:
    def __init__(self, config: Optional[VaultConfig] = None):
        self.config = config or VaultConfig()
        self._local_secrets: Dict[str, str | None] = {}
        self._infisical_client = None

        if self.config.environment == "development":
            self._load_local_env()
        elif self.config.environment == "production":
            self._init_infisical()
        else:
            raise VaultConfigurationError(f"Unknown environment: {self.config.environment}")

    def _load_local_env(self):
        if os.path.exists(self.config.env_file_path):
            self._local_secrets = dotenv_values(self.config.env_file_path)
            logger.info(f"Loaded secrets from {self.config.env_file_path}")
        else:
            logger.warning(f"Local env file {self.config.env_file_path} not found. Using os.environ as fallback.")
            self._local_secrets = dict(os.environ)

    def _init_infisical(self):
        if not self.config.infisical_token:
            raise VaultConfigurationError("infisical_token is required in production environment.")
        
        try:
            from infisical_client import InfisicalClient
            # Simplified initialization. 
            # In a real setup, we might need project_id, environment names, etc. 
            # based on infisical configuration specifics.
            self._infisical_client = InfisicalClient(token=self.config.infisical_token)
            logger.info("Initialized Infisical client for production secrets.")
        except ImportError:
            raise VaultConfigurationError("infisical-python package is not installed.")
        except Exception as e:
            raise VaultConfigurationError(f"Failed to initialize Infisical client: {e}")

    def get_secret(self, key: str) -> str:
        """
        Retrieve a secret by its key. 
        Raises SecretNotFoundError if the secret does not exist.
        """
        if self.config.environment == "development":
            value = self._local_secrets.get(key)
            if value is None:
                # Fallback to process env variables
                value = os.environ.get(key)
            
            if value is None:
                raise SecretNotFoundError(f"Secret '{key}' not found in local environment.")
            return value
            
        elif self.config.environment == "production":
            try:
                # The Infisical API for getting a secret
                secret = self._infisical_client.getSecret(secretName=key)
                if not secret or not secret.secretValue:
                    raise SecretNotFoundError(f"Secret '{key}' not found in Infisical.")
                return secret.secretValue
            except Exception as e:
                if isinstance(e, SecretNotFoundError):
                    raise
                raise SecretNotFoundError(f"Failed to retrieve secret '{key}' from Infisical: {e}")

        raise SecretNotFoundError(f"Cannot retrieve secret '{key}' in unknown environment.")

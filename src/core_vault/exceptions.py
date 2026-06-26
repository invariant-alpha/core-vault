class VaultError(Exception):
    """Base exception for Vault errors."""
    pass

class SecretNotFoundError(VaultError):
    """Raised when a requested secret cannot be found."""
    pass

class VaultConfigurationError(VaultError):
    """Raised when the vault is incorrectly configured."""
    pass

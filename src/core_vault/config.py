from pydantic import BaseModel, Field

class VaultConfig(BaseModel):
    environment: str = Field(default="development", description="Ambiente di esecuzione (development | production)")
    infisical_token: str | None = Field(default=None, description="Token per accesso a Infisical in produzione")
    env_file_path: str = Field(default=".env", description="Percorso del file .env da usare in sviluppo")

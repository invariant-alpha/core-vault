# Prompt Operativo — CORE_VAULT

## Ruolo nel Sistema
Infrastruttura di base, unico punto di accesso a tutti i segreti del sistema. Fornisce i segreti in memoria agli altri moduli (es. token Telegram, credenziali database, API key dei provider AI). In ambiente di sviluppo carica i segreti da un file `.env` locale, mentre in produzione utilizza `Infisical` per la gestione centralizzata, assicurando che nessuna credenziale finisca nel codice o nei log.

## Lifecycle
CORE_IMMUTABLE — Modulo non controllabile a runtime. È una libreria condivisa importata direttamente dagli altri moduli che ne necessitano, all'avvio.

## Configurazione
```python
from pydantic import BaseModel, Field

class VaultConfig(BaseModel):
    environment: str = Field(default="development", description="Ambiente di esecuzione (development | production)")
    infisical_token: str | None = Field(default=None, description="Token per accesso a Infisical in produzione")
    env_file_path: str = Field(default=".env", description="Percorso del file .env da usare in sviluppo")
```

## Dipendenze
- Moduli già implementati: Nessuno dipendente direttamente.
- Moduli simulati dal Mock Module: Nessuno.
- Non usa il Redis Bus.

## Schema Pydantic Completo
Nessun evento scambiato via Bus, quindi nessuno schema per `EventEnvelope` o payload di interscambio. L'unica astrazione è l'accesso ai segreti (es. `get_secret(key: str) -> str`).

## Contratto Redis Streams
- Stream sottoscritti: Nessuno
- Stream pubblicati: Nessuno
- Dead Letter Queue: N/A
- Politica retry: N/A

## Flusso Principale
1. All'avvio, un modulo istanzia il `VaultClient(config)`.
2. Se `environment == "development"`, il client carica le variabili d'ambiente usando `python-dotenv` dal file specificato.
3. Se `environment == "production"`, il client si autentica su `Infisical` usando il token fornito in environment (unica variabile d'ambiente strettamente necessaria) e fetcherà i segreti richiesti.
4. I moduli richiamano `vault.get_secret("TELEGRAM_BOT_TOKEN")` o metodi tipizzati. Se il segreto non esiste, il Vault solleva una `SecretNotFoundError`.

## Struttura Directory
```
core-vault/
├── Dockerfile
├── pyproject.toml
├── docs/
│   └── prompts/
│       └── CORE_VAULT.md
├── src/
│   └── core_vault/
│       ├── __init__.py
│       ├── client.py
│       ├── config.py
│       └── exceptions.py
└── tests/
    ├── unit/
    └── integration/
```

## Test Richiesti
- Unit test: Fallback su `.env` in sviluppo, sollevamento eccezioni per chiavi mancanti, non loggare i valori.
- Integration test con Mock Module: N/A
- Edge case: Comportamento quando `.env` non esiste, comportamento quando il token Infisical non è valido.

## ADR Collegati
ADR per l'utilizzo di Infisical (in produzione) vs `.env` (in sviluppo).

## Definition of Done
- [ ] Tutti i test passano
- [ ] Nessuna chiamata sincrona bloccante (dove possibile, anche se python-dotenv è sincrono, le API HTTP di Infisical devono essere async o caricate in batch al boot)
- [ ] Nessun segreto hardcoded o loggato
- [ ] Implementazione del fallback .env / Infisical
- [ ] Nessun riferimento ai flussi di business (D7)

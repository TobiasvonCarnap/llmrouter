# FreeRide Integration

FreeRide ist jetzt in den LLMRouter integriert und verwaltet automatisch kostenlose OpenRouter-Modelle.

## Funktionen

- **Automatische Modell-Synchronisation**: Holt alle kostenlosen Modelle von OpenRouter
- **Intelligentes Ranking**: Bewertet Modelle nach Kontext-Länge, Fähigkeiten, Aktualität und Provider-Vertrauen
- **Tier-Zuweisung**: Ordnet Modelle automatisch den Komplexitäts-Tiers zu (super_easy bis super_hard)
- **Konfigurations-Erhaltung**: Behält bestehende Nicht-OpenRouter-Modelle bei
- **API-Endpunkte**: REST-API zur Verwaltung der Free Models

## Verwendung

### CLI: Einmalige Aktualisierung

```bash
cd /Users/tobi/.openclaw/workspace/skills/llmrouter

# Config mit FreeRide-Modellen aktualisieren
python3 server.py --freeride --config config.yaml

# Force-Refresh (ignoriert Cache)
python3 server.py --freeride --freeride-force --config config.yaml
```

### API-Endpunkte (Server muss laufen)

```bash
# Status abfragen
curl http://localhost:4001/v1/admin/freeride/status

# Free Models auflisten
curl "http://localhost:4001/v1/admin/freeride/models?limit=10"

# Config aktualisieren
curl -X POST http://localhost:4001/v1/admin/freeride/update \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

## Konfiguration

Die Konfiguration wird automatisch in `config.yaml` gespeichert:

```yaml
freeride:
  enabled: true
  last_update: '2026-02-14T22:32:55.128815'
  total_free_models: 31
  api_url: https://openrouter.ai/api/v1/models
```

### API-Key

FreeRide benötigt einen OpenRouter API-Key. Dieser kann gesetzt werden:

1. Umgebungsvariable: `export OPENROUTER_API_KEY="sk-or-v1-..."`
2. In `config.yaml` unter `providers.openrouter.api_key`

## Tier-Zuweisung

Modelle werden basierend auf ihren Eigenschaften zugewiesen:

| Tier | Kriterien | Beispiele |
|------|-----------|-----------|
| super_easy | Kleine Modelle (1B-3B) | gemma-2b, nano |
| easy | Klein bis mittel (7B-9B) | llama-3.2, mini |
| medium | Mittel (14B-32B) | mistral, flash |
| hard | Groß, Coder, Reasoning | qwen3-coder, gemini-2.5 |
| super_hard | Top-Tier, Thinking | opus, deepseek-r1, qwen3-235b |

## Ranking-Faktoren

- **Context Length** (40%): Bevorzugt längere Kontexte
- **Capabilities** (30%): Mehr unterstützte Parameter
- **Recency** (20%): Neuere Modelle bevorzugt
- **Provider Trust** (10%): Vertrauenswürdige Provider

## Dateien

- `freeride.py` - Kernmodul mit API-Logik
- `server.py` - Integrierte API-Endpunkte und CLI
- `config.yaml` - Wird automatisch aktualisiert

## Beispiel-Output

```
🆓 FreeRide: ENABLED (31 free models, last update: 2026-02-14)
   API: GET /v1/admin/freeride/status
   API: POST /v1/admin/freeride/update
```

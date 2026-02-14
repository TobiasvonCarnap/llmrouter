# FreeRide Update: Kommentare erhalten & Duplikate verhindern

## Zusammenfassung

Dieses Update verbessert die FreeRide-Funktionalität im LLMRouter, um zwei wichtige Probleme zu lösen:

1. **Kommentare werden erhalten**: Bei Updates der `config.yaml` bleiben auskommentierte Modelle (mit `#`) erhalten
2. **Keine Duplikate**: Pro Level können nicht dieselben Modelle sowohl auskommentiert als auch aktiv vorhanden sein

## Änderungen in `freeride.py`

### Neue Funktionen

#### 1. `parse_yaml_with_comments(config_path)`
- Liest die YAML-Datei und extrahiert Kommentare pro Tier
- Gibt ein Tupel zurück: `(config_dict, tier_comments)`
- `tier_comments` ist ein Dictionary mit Tier-Namen als Keys und Listen von Tupeln `(model_string, is_commented)`

#### 2. `normalize_model_id(model_id)`
- Normalisiert Model-IDs für den Vergleich
- Entfernt Provider-Prefixe (`openrouter:`, `anthropic:`, etc.)
- Entfernt `:free`-Suffix
- Konvertiert zu lowercase für case-insensitive Vergleiche

#### 3. `has_duplicate(tier_entries, new_model)`
- Prüft, ob ein Modell bereits in einem Tier existiert (aktiv oder auskommentiert)
- Verwendet normalisierte IDs für den Vergleich
- Verhindert Duplikate zwischen aktiven und auskommentierten Einträgen

#### 4. `merge_models_with_comments(tier_entries, new_models)`
- Führt neue Modelle mit bestehenden Einträgen zusammen
- Bewahrt Kommentare (Zeilen mit `#`)
- Fügt nur neue Modelle hinzu, die nicht bereits existieren
- Gibt formatierte YAML-Zeilen zurück

#### 5. `save_config_with_comments(config_path, config, tier_comments, new_tiers)`
- Speichert die Konfiguration unter Beibehaltung von Kommentaren
- Durchläuft die Datei zeilenweise und ersetzt nur die Tier-Abschnitte
- Behält alle anderen YAML-Strukturen unverändert

### Modifizierte Funktionen

#### `update_config_with_freeride()`
- Verwendet nun `parse_yaml_with_comments()` statt `yaml.safe_load()`
- Zählt Duplikate und überspringt sie statt sie hinzuzufügen
- Aktualisierte Statistiken:
  - `added`: Neue hinzugefügte Modelle
  - `preserved`: Beibehaltene existierende Einträge (inkl. Kommentare)
  - `skipped_duplicates`: Übersprungene Duplikate
  - `tiers_updated`: Anzahl aktualisierter Tiers

## Beispiel

### Vor dem Update

```yaml
models:
  hard:
    # - anthropic:claude-sonnet-4-20250514
    # - kimi:kimi-k2.5
    - openrouter:free:free
```

### Nach dem Update (neue Free-Models verfügbar)

```yaml
models:
  hard:
    # - anthropic:claude-sonnet-4-20250514
    # - kimi:kimi-k2.5
    - openrouter:free:free
    - openrouter:qwen/qwen3-coder:free
    - openrouter:aurora-alpha:free
```

**Wichtig**: Die auskommentierten Modelle (`anthropic:claude-sonnet...` und `kimi:kimi-k2.5`) bleiben erhalten. Falls `openrouter:free:free` schon existiert, wird es nicht dupliziert.

## Technische Details

### Normalisierung für Duplikat-Erkennung

```python
# Diese Modelle werden als identisch erkannt:
"openrouter:qwen/qwen3-coder:free"
"openrouter:qwen/qwen3-coder"  # ohne :free
"qwen/qwen3-coder:free"        # ohne openrouter:
"qwen/qwen3-coder"             # minimal
```

### Erhalt von Kommentaren

- Kommentare werden als separate Zeilen identifiziert
- Format: `# - model:identifier` oder `# model:identifier`
- Kommentare bleiben an ihrer ursprünglichen Position (am Anfang des Tiers)
- Aktive Modelle werden nach den Kommentaren eingefügt

## Testen

### Manuelles Testen

```bash
# Config mit Kommentaren erstellen
cp config.yaml config.yaml.backup

# FreeRide Update durchführen
python freeride.py --config config.yaml --update

# Prüfen, ob Kommentare erhalten sind
grep -A 10 "^  hard:" config.yaml

# Vergleichen
diff config.yaml.backup config.yaml
```

### API-Test

```bash
# Status abfragen
curl http://localhost:4001/v1/admin/freeride/status

# Update durchführen
curl -X POST http://localhost:4001/v1/admin/freeride/update

# Mit Force-Refresh
curl -X POST http://localhost:4001/v1/admin/freeride/update \
  -d '{"force": true}'
```

## Migration

Bestehende Configs werden automatisch migriert:

1. Beim ersten Update werden alle bestehenden Einträge analysiert
2. Kommentare werden erkannt und gespeichert
3. Neue Modelle werden hinzugefügt (ohne Duplikate)
4. Die Datei wird mit erhaltenen Kommentaren geschrieben

Keine manuelle Migration notwendig!

## Fehlerbehebung

### Kommentare werden nicht erkannt

- Stellen Sie sicher, dass Kommentare das Format `# - model:id` haben
- Leerzeichen nach dem `#` sind optional
- Einrückung sollte 2 Leerzeichen sein (wie im Rest der YAML)

### Duplikate werden trotzdem hinzugefügt

- Prüfen Sie, ob die Model-IDs wirklich identisch sind
- Unterschiedliche Provider-Prefixe werden normalisiert
- Case-Unterschiede werden ignoriert (alles lowercase)

## Version

- **Datum**: 2026-02-15
- **Branch**: `feature/preserve-comments-and-prevent-duplicates`
- **Betrifft**: `freeride.py`

## Autor

OpenClaw Coder Agent für mikrogeophagus-tobi

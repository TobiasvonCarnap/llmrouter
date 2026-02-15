# Release Notes v1.2.0

**Veröffentlicht:** 2026-02-15  
**Branch:** `feature/preserve-comments-and-prevent-duplicates`

---

## 🆕 Neue Features

### 1. Kommentare werden erhalten (`parse_yaml_with_comments`)

Bei Updates der `config.yaml` (z.B. durch `freeride.py`) bleiben jetzt alle YAML-Kommentare erhalten.

**Vorher:**
```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
    # - "anthropic:claude-haiku"  # Backup, falls Exo down
```

Nach `freeride.py --update` (alte Version):
```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
    - "openrouter:openrouter/free:free"  # Kommentar weg!
```

**Nachher (v1.2.0):**
```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
    # - "anthropic:claude-haiku"  # Backup, falls Exo down
    - "openrouter:openrouter/free:free"
```

### 2. Duplikat-Verhinderung (`has_duplicate`)

Neue Modelle werden nicht mehr hinzugefügt, wenn sie bereits existieren — auch wenn sie auskommentiert sind.

**Wie es funktioniert:**
1. Model-ID wird normalisiert (Provider-Prefix entfernt, `:free`-Suffix entfernt)
2. Vergleich mit allen existierenden Einträgen (aktiv + auskommentiert)
3. Nur wenn kein Match → Modell wird hinzugefügt

**Beispiel:**
```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
    # - "anthropic:claude-haiku-4-5-20251001"  # Auskommentiert
```

Wenn `freeride.py` jetzt `anthropic:claude-haiku` hinzufügen möchte:
- ✓ Wird als Duplikat erkannt (normalisiert: `claude-haiku-4-5-20251001`)
- ✓ Nicht hinzugefügt (verhindert doppelte Einträge)

---

## 🔧 Neue Funktionen in `freeride.py`

### `parse_yaml_with_comments(config_path: str)`

Parst YAML und extrahiert Kommentare pro Tier.

```python
from freeride import parse_yaml_with_comments

config, tier_comments = parse_yaml_with_comments("config.yaml")

# tier_comments = {
#   "super_easy": [
#     ("exo:mlx-community/GLM-4.7-Flash-6bit", False),  # aktiv
#     ("anthropic:claude-haiku", True),                  # auskommentiert
#   ]
# }
```

### `has_duplicate(tier_entries: List[Tuple[str, bool]], new_model: str) -> bool`

Prüft, ob ein Modell bereits existiert.

```python
from freeride import has_duplicate

tier_entries = [
    ("exo:GLM-4.7-Flash", False),
    ("anthropic:claude-haiku", True),
]

has_duplicate(tier_entries, "anthropic:claude-haiku-4-5-20251001")
# → True (Duplikat erkannt)
```

### `normalize_model_id(model_id: str) -> str`

Normalisiert Model-IDs für Vergleiche.

```python
from freeride import normalize_model_id

normalize_model_id("anthropic:claude-haiku-4-5-20251001")
# → "claude-haiku-4-5-20251001"

normalize_model_id("openrouter:claude:free")
# → "claude"
```

---

## 🧪 Neuer Test: Multispeedtest

Neuer Beispiel-Test `multispeedtest.py`, der alle konfigurierten Modelle testet.

**Features:**
- Nutzt `parse_yaml_with_comments()` zum Laden der Modelle
- Testet nur aktive Modelle (überspringt auskommentierte)
- Parallele Requests für schnelle Tests
- Export der Ergebnisse als JSON

**Verwendung:**
```bash
# Nur aktive Modelle testen
python multispeedtest.py

# Alle Modelle testen (inkl. auskommentierte)
python multispeedtest.py --all

# Ergebnisse exportieren
python multispeedtest.py --output results.json
```

---

## 📚 Dokumentation

- Neue API-Dokumentation: `API_DOCS.md`
- Beispiel-Code für alle neuen Funktionen
- Integration in `freeride.py` dokumentiert

---

## 🐛 Bugfixes

- Keine (nur neue Features)

---

## Migration

Keine Breaking Changes. Einfach updaten und die neuen Features stehen sofort zur Verfügung.

```bash
git pull origin feature/preserve-comments-and-prevent-duplicates
```

# API Documentation — Config Management Functions

Diese Dokumentation beschreibt die neuen Funktionen in `freeride.py` für das Smart Config Management (v1.2.0+).

---

## `parse_yaml_with_comments(config_path: str)`

Parst eine YAML-Datei und extrahiert Kommentare pro Tier.

### Parameter
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `config_path` | `str` | Pfad zur YAML-Datei |

### Rückgabe
```python
Tuple[Dict, Dict[str, List[Tuple[str, bool]]]]
```

- **Erster Wert:** Der geparste YAML-Content als Dictionary
- **Zweiter Wert:** Ein Dictionary, das Tier-Namen auf Listen von Tupeln abbildet:
  - `Tuple[model_string, is_commented]`
  - `is_commented` ist `True`, wenn die Zeile auskommentiert ist

### Beispiel
```python
from freeride import parse_yaml_with_comments

config, tier_comments = parse_yaml_with_comments("config.yaml")

# Zugriff auf die Kommentare für ein Tier
for model, is_commented in tier_comments["super_easy"]:
    if is_commented:
        print(f"  # - {model}  (deaktiviert)")
    else:
        print(f"  - {model}  (aktiv)")
```

### Ausgabe
```
  - exo:mlx-community/GLM-4.7-Flash-6bit  (aktiv)
  # - anthropic:claude-haiku-4-5-20251001  (deaktiviert)
  - pollinations:claude-fast  (aktiv)
```

---

## `has_duplicate(tier_entries: List[Tuple[str, bool]], new_model: str)`

Prüft, ob ein Modell bereits in einem Tier existiert (aktiv oder auskommentiert).

### Parameter
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `tier_entries` | `List[Tuple[str, bool]]` | Liste der existierenden Einträge |
| `new_model` | `str` | Das zu prüfende Modell |

### Rückgabe
```python
bool
```

- `True` — Das Modell existiert bereits (normalisierte ID stimmt überein)
- `False` — Das Modell ist neu

### Beispiel
```python
from freeride import has_duplicate

tier_entries = [
    ("exo:mlx-community/GLM-4.7-Flash-6bit", False),
    ("anthropic:claude-haiku-4-5-20251001", True),  # auskommentiert
]

# Prüfen, ob ein neues Modell bereits existiert
if has_duplicate(tier_entries, "anthropic:claude-haiku"):
    print("Modell bereits vorhanden (oder auskommentiert)")
else:
    print("Modell kann hinzugefügt werden")
```

### Normalisierung
Die Funktion nutzt intern `normalize_model_id()`:
- Entfernt Provider-Prefixe (`anthropic:`, `exo:`, etc.)
- Entfernt `:free`-Suffix für Vergleiche
- Konvertiert zu lowercase

---

## `normalize_model_id(model_id: str)`

Normalisiert eine Model-ID für den Vergleich.

### Parameter
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `model_id` | `str` | Die zu normalisierende Model-ID |

### Rückgabe
```python
str
```

### Beispiel
```python
from freeride import normalize_model_id

# Entfernt Provider-Prefixe
normalize_model_id("anthropic:claude-haiku-4-5-20251001")
# → "claude-haiku-4-5-20251001"

# Entfernt :free-Suffix
normalize_model_id("openrouter:claude:free")
# → "claude"
```

---

## `merge_models_with_comments(tier_entries, new_models)`

Fügt neue Modelle mit bestehenden Einträgen zusammen, behält Kommentare bei und vermeidet Duplikate.

### Parameter
| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `tier_entries` | `List[Tuple[str, bool]]` | Existierende Einträge aus `parse_yaml_with_comments()` |
| `new_models` | `List[str]` | Neue Modelle zum Hinzufügen |

### Rückgabe
```python
List[str]
```

Liste von YAML-Zeilen für das Tier.

### Beispiel
```python
from freeride import parse_yaml_with_comments, merge_models_with_comments

config, tier_comments = parse_yaml_with_comments("config.yaml")

# Neue Modelle, die hinzugefügt werden sollen
new_models = ["pollinations:deepseek", "anthropic:claude-sonnet"]

# Merge durchführen
result_lines = merge_models_with_comments(
    tier_comments["super_easy"],
    new_models
)

# Ausgabe in YAML-Format
print("super_easy:")
for line in result_lines:
    print(line)
```

---

## Komplettes Beispiel: Config-Update mit Erhaltung von Kommentaren

```python
#!/usr/bin/env python3
"""
Beispiel: Config-Update mit Smart Config Management
"""
from pathlib import Path
import yaml
from freeride import (
    parse_yaml_with_comments,
    has_duplicate,
    merge_models_with_comments
)

def update_config_with_new_models(config_path: str, tier: str, new_models: list):
    """
    Aktualisiert die Config mit neuen Modellen, ohne Kommentare zu verlieren.
    """
    # 1. Parsen mit Kommentarerkennung
    config, tier_comments = parse_yaml_with_comments(config_path)
    
    # 2. Prüfen, welche Modelle wirklich neu sind
    existing_entries = tier_comments.get(tier, [])
    actually_new = []
    
    for model in new_models:
        if not has_duplicate(existing_entries, model):
            actually_new.append(model)
    
    print(f"Neue Modelle für {tier}: {actually_new}")
    print(f"Übersprungen (Duplikate): {set(new_models) - set(actually_new)}")
    
    # 3. Merge durchführen
    merged_lines = merge_models_with_comments(existing_entries, actually_new)
    
    # 4. Config-Datei aktualisieren
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Hier würde die Ersetzung des Tier-Blocks passieren...
    # (siehe freeride.py für vollständige Implementierung)
    
    return merged_lines

# Verwendung
if __name__ == "__main__":
    result = update_config_with_new_models(
        "config.yaml",
        "super_easy",
        ["pollinations:deepseek", "anthropic:claude-haiku"]
    )
    print("\nErgebnis:")
    print("\n".join(result))
```

---

## Integration in freeride.py

Die neuen Funktionen werden in `freeride.py` verwendet:

1. **`update_config_with_freeride()`** — Fügt OpenRouter Free Models hinzu
2. **`update_config_with_openrouter_tiers()`** — Aktualisiert Tier-Mappings

Beide Funktionen nutzen `parse_yaml_with_comments()` und `has_duplicate()`, um:
- Existierende Kommentare zu erhalten
- Duplikate zu vermeiden
- Manuelle Änderungen des Nutzers zu respektieren

---

## Changelog

- **2026-02-15** (v1.2.0)
  - `parse_yaml_with_comments()` hinzugefügt
  - `has_duplicate()` hinzugefügt
  - `normalize_model_id()` hinzugefügt
  - `merge_models_with_comments()` hinzugefügt
  - Kommentarerhaltung bei Config-Updates implementiert
  - Duplikat-Verhinderung implementiert

# Release Notes v1.1.0 - Failover-Chains

## 🚀 Was ist neu?

### Automatische Failover-Chains

Der LLM Router unterstützt jetzt **mehrere Modelle pro Komplexitätsstufe**. Wenn ein Modell nicht verfügbar ist, wird automatisch zum nächsten in der Liste gewechselt – ganz ohne manuellen Eingriff!

**Was bedeutet das für dich?**
- **Höhere Zuverlässigkeit**: Wenn ein Provider down ist, läuft deine Anfrage trotzdem durch
- **Flexibles Routing**: Kombiniere lokale Modelle (Exo, LM Studio) mit Cloud-Providern (Anthropic, Pollinations)
- **Keine Unterbrechungen**: Der Wechsel passiert automatisch im Hintergrund

---

## ⚙️ Wie funktioniert es?

Statt nur einem Modell pro Stufe kannst du jetzt eine **Prioritätenliste** angeben:

```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # 1. Versuch: Lokales Exo
    - "lmstudio:zai-org/glm-4.7-flash"             # 2. Versuch: LM Studio
    - "anthropic:claude-haiku-4-5-20251001"        # 3. Versuch: Anthropic (Fallback)
```

**Ablauf:**
1. Router klassifiziert die Anfrage (z.B. "super_easy")
2. Versucht Modell 1 (Exo)
3. Wenn Exo nicht antwortet → automatisch Versuch mit Modell 2 (LM Studio)
4. Wenn LM Studio nicht antwortet → Versuch mit Modell 3 (Anthropic)
5. Erst wenn alle Modelle fehlschlagen → Fehlermeldung

---

## 📋 Beispiel-Konfiguration

```yaml
# config.yaml - Vollständige Beispiel-Config mit Failover-Chains

models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # Schnell & lokal
    - "lmstudio:zai-org/glm-4.7-flash"             # Lokaler Fallback
    - "anthropic:claude-haiku-4-5-20251001"        # Cloud-Fallback

  easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
    - "lmstudio:zai-org/glm-4.7-flash"
    - "anthropic:claude-haiku-4-5-20251001"

  medium:
    - "pollinations:glm"                           # Kostenlos
    - "pollinations:deepseek"                      # Alternative
    - "anthropic:claude-sonnet-4-20250514"         # Premium-Fallback
    - "lmstudio:zai-org/glm-4.7-flash"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"

  hard:
    - "pollinations:glm"
    - "pollinations:deepseek"
    - "anthropic:claude-sonnet-4-20250514"
    - "lmstudio:zai-org/glm-4.7-flash"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"

  super_hard:
    - "anthropic:claude-opus-4-20250514"           # Bestes Modell
    - "pollinations:glm"                           # Fallback
    - "lmstudio:zai-org/glm-4.7-flash"
    - "exo/mlx-community/GLM-4.7-Flash-6bit"
```

---

## ⚠️ Breaking Changes

**Keine Breaking Changes!** Die alte Syntax mit einzelnem String funktioniert weiterhin:

```yaml
# Alte Syntax (funktioniert weiterhin)
models:
  super_easy: "anthropic:claude-haiku-4-5-20251001"

# Neue Syntax (empfohlen für Failover)
models:
  super_easy:
    - "anthropic:claude-haiku-4-5-20251001"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
```

**Hinweis**: Tool-Calls mit `model:` Override (Option 2) verwenden weiterhin **kein** Failover – sie nutzen explizit das angegebene Modell.

---

## ⬆️ Upgrade-Anleitung

### Schritt 1: Repository aktualisieren
```bash
cd /path/to/llmrouter
git pull origin main
```

### Schritt 2: Config erweitern (optional)
Bearbeite `config.yaml` und füge Failover-Chains hinzu:

```yaml
# Vorher:
models:
  super_easy: "anthropic:claude-haiku-4-5-20251001"

# Nachher:
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # Lokales Modell zuerst (kostenlos)
    - "anthropic:claude-haiku-4-5-20251001"        # Cloud-Fallback
```

### Schritt 3: Server neu starten
```bash
# Falls als Service läuft
launchctl unload ~/Library/LaunchAgents/com.llmrouter.plist
launchctl load ~/Library/LaunchAgents/com.llmrouter.plist

# Oder manuell
python server.py --openclaw
```

---

## 🐛 Bugfixes in diesem Release

- **Null-safe Provider-Loading**: Absturz behoben, wenn Provider-Konfiguration leer war
- **Array-Support**: Config-Parser unterstützt jetzt korrekt Listen/Arrays
- **Robuste Fehlerbehandlung**: Alle Provider müssen fehlschlagen, bevor ein Fehler zurückgegeben wird

---

## 📊 Kompatibilität

- **Python**: 3.10+
- **OpenClaw**: Voll kompatibel
- **Provider**: Alle bisherigen (Anthropic, OpenAI, Google, Kimi, Ollama, Exo, LM Studio, Pollinations)

---

**Viel Spaß mit dem zuverlässigeren Routing!** 🎉

*Release-Datum: 2026-02-13*
*Tag: v1.1.0*

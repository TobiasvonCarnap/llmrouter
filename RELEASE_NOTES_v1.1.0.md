# 🐟 OpenClaw LLM Router — Release Notes v1.1.0

> 🤝 *Auf Basis von [alexrudloff/llmrouter](https://github.com/alexrudloff/llmrouter) — danke Alex für die exzellente Grundlage!*

---

## 🚀 Was ist neu in v1.1.0

### 🔀 Automatische Failover-Chains

Der LLM Router unterstützt jetzt **mehrere Modelle pro Komplexitätsstufe**. Wenn ein Modell nicht verfügbar ist, wird automatisch zum nächsten in der Liste gewechselt — ganz ohne manuellen Eingriff!

| Vorher | Nachher |
|--------|---------|
| Ein Modell pro Stufe | Prioritätenliste mit automatischem Fallback |
| Manuelles Provider-Switching | Nahtloser Failover |
| Ausfallzeit bei Provider-Problemen | Kontinuierlicher Betrieb |

**Was bedeutet das für dich:**
- ✅ **Höhere Zuverlässigkeit** — Wenn ein Provider down ist, läuft deine Anfrage trotzdem durch
- 🔄 **Flexibles Routing** — Kombiniere lokale Modelle (Exo, LM Studio) mit Cloud-Providern (Anthropic, Pollinations)
- ⚡ **Keine Unterbrechungen** — Der Wechsel passiert automatisch im Hintergrund

---

## ⚙️ Wie funktioniert es?

Statt nur einem Modell pro Stufe kannst du jetzt eine **Prioritätenliste** angeben:

```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # 🏠 1.: Lokal (kostenlos)
    - "lmstudio:zai-org/glm-4.7-flash"             # 🏠 2.: Lokaler Fallback
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ 3.: Cloud-Fallback
```

**Ablauf:**
1. 🔍 Router klassifiziert Anfrage (z.B. "super_easy")
2. 🎯 Versucht Modell 1 (Exo)
3. 🔄 Wenn Exo fehlschlägt → automatischer Versuch mit Modell 2 (LM Studio)
4. 🔄 Wenn LM Studio fehlschlägt → Versuch mit Modell 3 (Anthropic)
5. ❌ Erst wenn ALLE Modelle fehlschlagen → Fehler zurückgegeben

---

## 📋 Beispiel-Konfiguration

```yaml
# config.yaml — Komplettes Beispiel mit Failover-Chains

models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # 🚀 Schnell & lokal
    - "lmstudio:zai-org/glm-4.7-flash"             # 🏠 Lokaler Fallback
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ Cloud-Fallback

  easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
    - "lmstudio:zai-org/glm-4.7-flash"
    - "anthropic:claude-haiku-4-5-20251001"

  medium:
    - "pollinations:glm"                           # 🆓 Kostenlos
    - "pollinations:deepseek"                      # 🔄 Alternative
    - "anthropic:claude-sonnet-4-20250514"         # 💎 Premium-Fallback
    - "lmstudio:zai-org/glm-4.7-flash"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"

  hard:
    - "pollinations:glm"
    - "pollinations:deepseek"
    - "anthropic:claude-sonnet-4-20250514"
    - "lmstudio:zai-org/glm-4.7-flash"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"

  super_hard:
    - "anthropic:claude-opus-4-20250514"           # 👑 Bestes Modell
    - "pollinations:glm"                           # 🔄 Fallback
    - "lmstudio:zai-org/glm-4.7-flash"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
```

---

## ⚠️ Breaking Changes

**Keine!** 🎉 Die alte Syntax mit einzelnem String funktioniert weiterhin:

```yaml
# ✨ Alte Syntax (funktioniert weiterhin)
models:
  super_easy: "anthropic:claude-haiku-4-5-20251001"

# 🆕 Neue Syntax (empfohlen für Failover)
models:
  super_easy:
    - "anthropic:claude-haiku-4-5-20251001"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
```

**Hinweis:** Tool-Calls mit `model:`-Override verwenden weiterhin **kein** Failover — sie nutzen explizit das angegebene Modell.

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
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # 🏠 Lokales Modell zuerst (kostenlos)
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ Cloud-Fallback
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

| Problem | Fix |
|---------|-----|
| Absturz bei leerer Provider-Konfiguration | 🛡️ Null-safe Provider-Loading |
| Array-Config nicht unterstützt | ✅ Volle Array/List-Unterstützung |
| Erster Provider-Fail = Total-Fail | 🔄 Alle Provider werden versucht |

---

## 📊 Kompatibilität

| Komponente | Version |
|------------|---------|
| 🐍 Python | 3.10+ |
| 🦞 OpenClaw | Voll kompatibel |
| 🔌 Provider | Alle bisherigen (Anthropic, OpenAI, Google, Kimi, Ollama, Exo, LM Studio, Pollinations) |

---

## 🎯 Schnell-Links

- 📖 [Vollständige Dokumentation](README.md)
- ⚙️ [Beispiel-Konfiguration](config.yaml.example)
- 🐛 [Issues melden](../../issues)

---

**Viel Spaß mit dem zuverlässigeren Routing!** 🎉

*Release-Datum: 2026-02-13*  
*Tag: v1.1.0*  
*Gebaut mit 🐟 OpenClaw*

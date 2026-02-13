# 🐟 OpenClaw LLM Router — Release Notes v1.1.0

> 🤝 *Built on top of [alexrudloff/llmrouter](https://github.com/alexrudloff/llmrouter) — thanks Alex for the excellent foundation!*

---

## 🚀 What's New in v1.1.0

### 🔀 Automatic Failover Chains

The LLM Router now supports **multiple models per complexity level**. If one model is unavailable, it automatically switches to the next in the list — no manual intervention required!

| Before | After |
|--------|-------|
| Single model per tier | Priority list with automatic fallback |
| Manual provider switching | Seamless failover |
| Downtime on provider issues | Continuous operation |

**What this means for you:**
- ✅ **Higher reliability** — If a provider is down, your request still goes through
- 🔄 **Flexible routing** — Combine local models (Exo, LM Studio) with cloud providers (Anthropic, Pollinations)
- ⚡ **No interruptions** — The switch happens automatically in the background

---

## ⚙️ How It Works

Instead of just one model per level, specify a **priority list**:

```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # 🏠 1st: Local (free)
    - "lmstudio:zai-org/glm-4.7-flash"             # 🏠 2nd: Local fallback
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ 3rd: Cloud fallback
```

**Flow:**
1. 🔍 Router classifies request (e.g., "super_easy")
2. 🎯 Attempts Model 1 (Exo)
3. 🔄 If Exo fails → automatic attempt with Model 2 (LM Studio)
4. 🔄 If LM Studio fails → attempt with Model 3 (Anthropic)
5. ❌ Only when ALL models fail → error returned

---

## 📋 Example Configuration

```yaml
# config.yaml — Complete example with failover chains

models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # 🚀 Fast & local
    - "lmstudio:zai-org/glm-4.7-flash"             # 🏠 Local fallback
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ Cloud fallback

  easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
    - "lmstudio:zai-org/glm-4.7-flash"
    - "anthropic:claude-haiku-4-5-20251001"

  medium:
    - "pollinations:glm"                           # 🆓 Free tier
    - "pollinations:deepseek"                      # 🔄 Alternative
    - "anthropic:claude-sonnet-4-20250514"         # 💎 Premium fallback
    - "lmstudio:zai-org/glm-4.7-flash"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"

  hard:
    - "pollinations:glm"
    - "pollinations:deepseek"
    - "anthropic:claude-sonnet-4-20250514"
    - "lmstudio:zai-org/glm-4.7-flash"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"

  super_hard:
    - "anthropic:claude-opus-4-20250514"           # 👑 Best model
    - "pollinations:glm"                           # 🔄 Fallback
    - "lmstudio:zai-org/glm-4.7-flash"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
```

---

## ⚠️ Breaking Changes

**None!** 🎉 The old syntax with single strings continues to work:

```yaml
# ✨ Old syntax (still works)
models:
  super_easy: "anthropic:claude-haiku-4-5-20251001"

# 🆕 New syntax (recommended for failover)
models:
  super_easy:
    - "anthropic:claude-haiku-4-5-20251001"
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
```

**Note:** Tool calls with `model:` override still do **not** use failover — they use the explicitly specified model.

---

## ⬆️ Upgrade Guide

### Step 1: Update Repository
```bash
cd /path/to/llmrouter
git pull origin main
```

### Step 2: Extend Config (Optional)
Edit `config.yaml` and add failover chains:

```yaml
# Before:
models:
  super_easy: "anthropic:claude-haiku-4-5-20251001"

# After:
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # 🏠 Local first (free)
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ Cloud fallback
```

### Step 3: Restart Server
```bash
# If running as a service
launchctl unload ~/Library/LaunchAgents/com.llmrouter.plist
launchctl load ~/Library/LaunchAgents/com.llmrouter.plist

# Or manually
python server.py --openclaw
```

---

## 🐛 Bugfixes in This Release

| Issue | Fix |
|-------|-----|
| Crash on empty provider config | 🛡️ Null-safe provider loading |
| Array config not supported | ✅ Full array/list support |
| First provider fail = total fail | 🔄 Attempt all providers before error |

---

## 📊 Compatibility

| Component | Version |
|-----------|---------|
| 🐍 Python | 3.10+ |
| 🦞 OpenClaw | Fully compatible |
| 🔌 Providers | All previous (Anthropic, OpenAI, Google, Kimi, Ollama, Exo, LM Studio, Pollinations) |

---

## 🎯 Quick Links

- 📖 [Full Documentation](README.md)
- ⚙️ [Example Config](config.yaml.example)
- 🐛 [Report Issues](../../issues)

---

**Enjoy the more reliable routing!** 🎉

*Release Date: 2026-02-13*  
*Tag: v1.1.0*  
*Built with 🐟 OpenClaw*

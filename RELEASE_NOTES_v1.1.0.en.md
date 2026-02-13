<div align="center">

<img src="https://img.shields.io/badge/🦞-OpenClaw_Style-FF4500?style=for-the-badge&labelColor=1a1a1a" alt="OpenClaw Style">

# 🐟 Release Notes v1.1.0

### 🔀 Automatic Failover Chains

<img src="https://img.shields.io/badge/version-v1.1.0-FF4500?style=flat-square">
<img src="https://img.shields.io/badge/status-stable-success?style=flat-square">

</div>

---

<div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #FF4500;">

> 🤝 *Built on top of [alexrudloff/llmrouter](https://github.com/alexrudloff/llmrouter) — thanks Alex for the excellent foundation!*

</div>

---

## 🚀 What's New in v1.1.0

<div style="background: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #FF4500;">

### 🔀 Automatic Failover Chains

The LLM Router now supports **multiple models per complexity level**. If one model is unavailable, it automatically switches to the next in the list — no manual intervention required!

</div>

---

## 📊 Before vs After

| | Before v1.1.0 | After v1.1.0 |
|---|---|---|
| **Models per tier** | Single model | Priority list with auto-fallback |
| **Provider down** | Request fails | Seamless failover |
| **Configuration** | Simple string | Array of strings |
| **Cost optimization** | Limited | Mix local (free) + cloud |

---

## ✨ Benefits

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; text-align: center;">

### ✅ Higher Reliability

If a provider is down, your request still goes through

</div>

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; text-align: center;">

### 🔄 Flexible Routing

Combine local models with cloud providers

</div>

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; text-align: center;">

### ⚡ No Interruptions

Automatic switching in the background

</div>

</div>

---

## ⚙️ How It Works

<div style="background: #1a1a1a; padding: 20px; border-radius: 12px; border-left: 4px solid #FF4500;">

Instead of just one model per level, specify a **priority list**:

```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # 🏠 1st: Local (free)
    - "lmstudio:zai-org/glm-4.7-flash"             # 🏠 2nd: Local fallback
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ 3rd: Cloud fallback
```

</div>

### Flow

```
🔍 Request arrives
    ↓
🎯 Classified as "super_easy"
    ↓
🔄 Try Model 1 (Exo)
    ↓ (if fails)
🔄 Try Model 2 (LM Studio)
    ↓ (if fails)
🔄 Try Model 3 (Anthropic)
    ↓ (if fails)
❌ Return error
```

---

## 📋 Example Configuration

<div style="background: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333;">

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

</div>

---

## ⚠️ Breaking Changes

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; border-left: 4px solid #22c55e;">

### ✅ None!

The old syntax with single strings continues to work:

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

</div>

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

| Issue | Fix | Status |
|-------|-----|--------|
| Crash on empty provider config | 🛡️ Null-safe provider loading | ✅ Fixed |
| Array config not supported | ✅ Full array/list support | ✅ Fixed |
| First provider fail = total fail | 🔄 Attempt all providers | ✅ Fixed |

---

## 📊 Compatibility

| Component | Version | Status |
|-----------|---------|--------|
| 🐍 Python | 3.10+ | ✅ Supported |
| 🦞 OpenClaw | All versions | ✅ Compatible |
| 🔌 Anthropic | All models | ✅ Tested |
| 🔌 OpenAI | GPT + reasoning | ✅ Tested |
| 🔌 Google | Gemini | ✅ Tested |
| 🔌 Kimi | All models | ✅ Tested |
| 🔌 Ollama | Local models | ✅ Tested |
| 🔌 Exo | MLX models | ✅ Tested |
| 🔌 LM Studio | Local API | ✅ Tested |
| 🔌 Pollinations | Free tier | ✅ Tested |

---

<div align="center">

## 🎯 Quick Links

[📖 Full Documentation](README.md) • [⚙️ Example Config](config.yaml.example) • [🐛 Report Issues](../../issues)

---

**Built with** 🦞 **OpenClaw**  
**Release Date:** 2026-02-13 | **Tag:** v1.1.0

</div>

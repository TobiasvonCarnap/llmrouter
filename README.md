<div align="center">

<img src="https://img.shields.io/badge/🦞-Powered%20by%20OpenClaw-FF4500?style=for-the-badge&labelColor=1a1a1a" alt="Powered by OpenClaw">

# 🐟 LLM Router

> **Experimental Fork** — Personal additions by [Tobias von Carnap](https://github.com/TobiasvonCarnap)  
> 🤝 *Built on [alexrudloff/llmrouter](https://github.com/alexrudloff/llmrouter) — thanks Alex!*

<br>

<img src="https://img.shields.io/badge/version-v1.1.0-FF4500?style=flat-square&logoColor=white">
<img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/OpenClaw-Compatible-FF4500?style=flat-square">

</div>

---

<div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #FF4500;">

### 🎯 What is this?

An intelligent proxy that **classifies** incoming requests by complexity and **routes** them to appropriate LLM models.

**Save money** by using cheaper/faster models for simple tasks and reserving expensive models for complex ones.

</div>

---

## 📊 Status

<div align="center">

| Provider | Status |
|----------|--------|
| Anthropic | ✅ Tested |
| OpenAI | ✅ Tested |
| Google Gemini | ✅ Tested |
| Kimi/Moonshot | ✅ Tested |
| Ollama | ✅ Tested |

</div>

---

## 🚀 Latest Release: v1.1.0

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; border: 1px solid #333;">

### 🔀 Automatic Failover Chains

📝 [Release Notes 🇬🇧 EN](RELEASE_NOTES_v1.1.0.en.md) | [🇩🇪 DE](RELEASE_NOTES_v1.1.0.md)

</div>

---

## ✨ Features

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; border-left: 3px solid #FF4500;">

### 🆕 NEW: Failover Chains
Configure multiple models per tier for automatic fallback (v1.1.0+)

</div>

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; border-left: 3px solid #FF4500;">

### 🎯 5-Tier Routing
super_easy → easy → medium → hard → super_hard

</div>

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; border-left: 3px solid #3776AB;">

### 🏠 Local Classification
Use Ollama to classify locally — **zero API costs**

</div>

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; border-left: 3px solid #3776AB;">

### 🔌 Multi-Provider
Anthropic, OpenAI, Gemini, Ollama, Exo, LM Studio

</div>

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; border-left: 3px solid #3776AB;">

### 🧠 OpenAI-Compatible API
Drop-in replacement for existing integrations

</div>

<div style="background: #1a1a1a; padding: 16px; border-radius: 8px; border-left: 3px solid #3776AB;">

### 🔐 OAuth Support
Works with Claude Code tokens (sk-ant-oat*)

</div>

</div>

---

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) (optional — for local classification)
- Anthropic API key or Claude Code OAuth token

---

## ⚡ Quick Start

```bash
# Clone the repo
git clone https://github.com/TobiasvonCarnap/llmrouter.git
cd llmrouter

# Install dependencies
pip install -r requirements.txt

# Pull classifier model
ollama pull qwen2.5:3b

# Copy and customize config
cp config.yaml.example config.yaml

# Start the server
python server.py --openclaw
```

---

## ⚙️ Configuration

<div style="background: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #FF4500;">

### 🔄 Failover Chains (v1.1.0+)

Configure **multiple models per complexity level** for automatic failover.

```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"      # 🏠 Try local first
    - "lmstudio:zai-org/glm-4.7-flash"             # 🔄 Fallback
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ Final fallback
```

**How it works:**
1. 🔍 Router classifies request
2. 🎯 Tries first model
3. 🔄 If it fails → automatically tries next
4. ❌ Only returns error if **ALL** models fail

</div>

---

## 🔧 Model Routing Examples

### 💰 Cost-Optimized (Free → Premium)

```yaml
# Start with free Pollinations models, fallback to paid providers
models:
  super_easy:
    - "pollinations:claude-fast"                   # 🆓 Free tier
    - "pollinations:glm"                           # 🆓 Free alternative
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ Premium fallback

  easy:
    - "pollinations:glm"                           # 🆓 Free tier
    - "pollinations:deepseek"                      # 🆓 Free alternative
    - "anthropic:claude-haiku-4-5-20251001"        # ☁️ Premium fallback

  medium:
    - "pollinations:deepseek"                      # 🆓 Free tier
    - "pollinations:claude-fast"                   # 🆓 Free alternative
    - "anthropic:claude-sonnet-4-20250514"         # 💎 Premium fallback
    - "exo:mlx-community/GLM-4.7-Flash-6bit"       # 🏠 Local fallback

  hard:
    - "pollinations:claude-fast"                   # 🆓 Try free first
    - "anthropic:claude-sonnet-4-20250514"         # 💎 Premium
    - "exo:mlx-community/GLM-4.7-Flash-6bit"       # 🏠 Local

  super_hard:
    - "anthropic:claude-opus-4-20250514"           # 👑 Best model
    - "pollinations:deepseek"                      # 🆓 Free fallback
    - "exo:mlx-community/GLM-4.7-Flash-6bit"       # 🏠 Local fallback
```

### ☁️ Cloud-Only (Anthropic)

```yaml
models:
  super_easy: "anthropic:claude-haiku-4-5-20251001"
  easy: "anthropic:claude-sonnet-4-20250514"
  medium: "anthropic:claude-sonnet-4-20250514"
  hard: "anthropic:claude-opus-4-20250514"
  super_hard: "anthropic:claude-opus-4-20250514"
```

### 🏠 Local-First (Privacy Focused)

```yaml
models:
  super_easy:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"       # 🏠 Local first
    - "lmstudio:zai-org/glm-4.7-flash"             # 🏠 Alternative local
    - "pollinations:glm"                           # 🆓 Cloud fallback

  medium:
    - "exo:mlx-community/GLM-4.7-Flash-6bit"
    - "pollinations:deepseek"
    - "anthropic:claude-sonnet-4-20250514"
```

---

## 🐛 Tool Routing

```yaml
# Option 1: Minimum complexity floor
tools:
  min_complexity: "medium"  # Bumps super_easy/easy → medium

# Option 2: Force specific model for ALL tool calls
tools:
  model: "anthropic:claude-opus-4-20250514"
```

---

## 🌐 Supported Providers

| Provider | Prefix | Example |
|----------|--------|---------|
| Anthropic | `anthropic:` | `anthropic:claude-sonnet-4-20250514` |
| OpenAI | `openai:` | `openai:gpt-4o` |
| Google Gemini | `google:` | `google:gemini-2.0-flash` |
| Kimi/Moonshot | `kimi:` | `kimi:kimi-k2.5` |
| Ollama (local) | `local:` | `local:qwen2.5:3b` |
| Exo (local) | `exo:` | `exo:mlx-community/GLM-4.7-Flash` |
| LM Studio | `lmstudio:` | `lmstudio:zai-org/glm-4.7-flash` |
| Pollinations | `pollinations:` | `pollinations:glm` |
| DeepSeek | `deepseek:` | `deepseek:deepseek-chat` |

> 💚 **Special thanks to:**
> - [Pollinations.ai](https://pollinations.ai/) — for providing free API access
> - [OpenClaw Builders Night](https://luma.com/8k58g33a?tk=CvqEtm) — ([Event Notes](https://vagabond-process-2a0.notion.site/OpenClaw-Builders-Night-30376b54d8ca805288dace54d09648b0))
> - The entire team at [Antler in Continental Europe](https://www.antler.co/location/germany) — especially [Christian-Hauke Poensgen](https://chrispoensgen.com) & [Alan Poensgen](https://www.linkedin.com/in/alan-poensgen/)

---

## 🧪 Testing Classification

```bash
python classifier.py "Write a Python sort function"
# Output: medium

python classifier.py --test
# Runs test suite
```

---

## 🚀 Running as macOS Service

Create `~/Library/LaunchAgents/com.llmrouter.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.llmrouter</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/llmrouter/venv/bin/python</string>
        <string>/path/to/llmrouter/server.py</string>
        <string>--openclaw</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.llmrouter.plist
```

---

<div align="center">

## 🎯 Quick Links

[📖 Documentation](README.md) • [⚙️ Example Config](config.yaml.example) • [🐛 Report Issues](../../issues)

---

**Built with** 🦞 **OpenClaw** | **Thanks to** 🤝 **Alex Rudloff**


## License

MIT
</div>

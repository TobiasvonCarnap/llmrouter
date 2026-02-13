<div align="center">

# 🐟 LLM Router

> **🍴 Experimental Fork** — Personal additions by [Tobias von Carnap](https://github.com/TobiasvonCarnap)  
> 🤝 *Built on [alexrudloff/llmrouter](https://github.com/alexrudloff/llmrouter) — thanks Alex!*

[![Version](https://img.shields.io/badge/version-v1.1.0-FF4500?style=flat-square)](https://gitea.mikrogeophagus.dedyn.io/mikrogeophagus-tobi/llmrouter/releases/tag/v1.1.0)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-FF4500?style=flat-square)](https://github.com/openclaw/openclaw)

</div>

---

## 🎯 What is this?

An intelligent proxy that **classifies** incoming requests by complexity and **routes** them to appropriate LLM models.

**Save money** by using cheaper/faster models for simple tasks and reserving expensive models for complex ones.

---

## 📊 Status

| Provider | Status |
|----------|--------|
| Anthropic | ✅ Tested |
| OpenAI | ✅ Tested |
| Google Gemini | ✅ Tested |
| Kimi/Moonshot | ✅ Tested |
| Ollama | ✅ Tested |

---

## 🚀 Latest Release: v1.1.0 — Failover Chains

📝 [Release Notes 🇬🇧 EN](RELEASE_NOTES_v1.1.0.en.md) | [🇩🇪 DE](RELEASE_NOTES_v1.1.0.md)

---

## ✨ Features

- **🆕 NEW: Automatic failover chains** — Configure multiple models per tier for automatic fallback (v1.1.0+)
- **🎯 5-tier complexity routing** — super_easy → easy → medium → hard → super_hard
- **🏠 Local classification** — Use Ollama to classify locally (zero API costs)
- **🔌 Multi-provider support** — Anthropic, OpenAI, Gemini, Ollama, Exo, LM Studio, Pollinations
- **🧠 OpenAI-compatible API** — Drop-in replacement for existing integrations
- **🔐 OAuth token support** — Works with Claude Code tokens (sk-ant-oat*)

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

**Backward compatible:** Single string syntax still works:
```yaml
models:
  super_easy: "anthropic:claude-haiku-4-5-20251001"  # No failover
```

---

## 🔧 Model Routing Examples

```yaml
# Anthropic routing
models:
  super_easy: "anthropic:claude-haiku-4-5-20251001"
  easy: "anthropic:claude-sonnet-4-20250514"
  medium: "anthropic:claude-sonnet-4-20250514"
  hard: "anthropic:claude-opus-4-20250514"
  super_hard: "anthropic:claude-opus-4-20250514"
```

```yaml
# OpenAI routing
models:
  super_easy: "openai:gpt-4o-mini"
  easy: "openai:gpt-4o-mini"
  medium: "openai:gpt-4o"
  hard: "openai:o3-mini"
  super_hard: "openai:o3"
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

> 💚 **Special thanks to [Pollinations.ai](https://pollinations.ai/)** for providing free API access to their models!
>
> 🙏 **Thanks to the [OpenClaw Builders Night](https://luma.com/8k58g33a?tk=CvqEtm)** — [Event Notes](https://vagabond-process-2a0.notion.site/OpenClaw-Builders-Night-30376b54d8ca805288dace54d09648b0)
>
> 🚀 **Thanks to the entire Antler in Continental Europe team** ([https://www.antler.co/location/germany](https://www.antler.co/location/germany)):
> - [Christian-Hauke Poensgen](https://chrispoensgen.com)
> - [Alan Poensgen](https://www.linkedin.com/in/alan-poensgen/)

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

## 🎯 Quick Links

- 📖 [Full Documentation](README.md)
- ⚙️ [Example Config](config.yaml.example)
- 🐛 [Report Issues](../../issues)

---

<div align="center">

**Built with** 🦞 **OpenClaw**  
**Thanks to** 🤝 **Alex Rudloff**

</div>

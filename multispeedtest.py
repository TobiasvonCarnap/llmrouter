#!/usr/bin/env python3
"""
Multispeedtest — Performance-Test für alle konfigurierten Modelle

Testet alle Modelle in der config.yaml und misst:
- Antwortzeit (Latency)
- Token/s (Throughput)
- Erfolgsrate

Verwendet die Smart Config Functions (parse_yaml_with_comments) aus freeride.py.

CHANGELOG:
- 2026-02-15: Erstellt mit Unterstützung für Kommentarerhaltung und Duplikat-Erkennung
"""

import argparse
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import concurrent.futures

# Versuche, requests zu importieren
try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

# Importiere die neuen Config-Funktionen aus freeride.py
try:
    from freeride import parse_yaml_with_comments, has_duplicate, normalize_model_id
    SMART_CONFIG_AVAILABLE = True
except ImportError:
    SMART_CONFIG_AVAILABLE = False
    print("Warning: freeride.py nicht gefunden. Smart Config Features nicht verfügbar.")


class Multispeedtest:
    """Testet mehrere Modelle und vergleicht deren Performance."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.results: List[Dict] = []
        
    def load_models_from_config(self) -> List[Tuple[str, str, bool]]:
        """
        Lädt alle Modelle aus der config.yaml.
        
        Returns:
            Liste von Tupeln: (tier_name, model_string, is_commented)
        """
        models = []
        
        if SMART_CONFIG_AVAILABLE:
            # Nutze die neue parse_yaml_with_comments() Funktion
            config, tier_comments = parse_yaml_with_comments(self.config_path)
            
            for tier_name, entries in tier_comments.items():
                for model_str, is_commented in entries:
                    models.append((tier_name, model_str, is_commented))
                    
            print(f"📄 {len(models)} Modelle geladen (mit Kommentarerkennung)")
            commented = sum(1 for _, _, c in models if c)
            if commented > 0:
                print(f"   → {commented} auskommentiert, {len(models) - commented} aktiv")
        else:
            # Fallback: Standard YAML-Parsing ohne Kommentare
            import yaml
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            
            for tier_name, tier_models in config.get("models", {}).items():
                if isinstance(tier_models, list):
                    for model in tier_models:
                        models.append((tier_name, model, False))
                elif isinstance(tier_models, str):
                    models.append((tier_name, tier_models, False))
                    
            print(f"📄 {len(models)} Modelle geladen (Standard-Parsing)")
        
        return models
    
    def parse_model_string(self, model_str: str) -> Tuple[str, str]:
        """
        Parst einen Model-String in Provider und Model-Name.
        
        Beispiel: "anthropic:claude-sonnet-4-20250514" → ("anthropic", "claude-sonnet-4-20250514")
        """
        if ":" in model_str:
            provider, model = model_str.split(":", 1)
            return provider, model
        return "unknown", model_str
    
    def get_api_endpoint(self, provider: str) -> Optional[str]:
        """Gibt die API-Endpoint-URL für einen Provider zurück."""
        import yaml
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
        
        providers = config.get("providers", {})
        
        endpoints = {
            "anthropic": "https://api.anthropic.com/v1/messages",
            "openai": "https://api.openai.com/v1/chat/completions",
            "google": "https://generativelanguage.googleapis.com/v1beta/models",
            "kimi": "https://api.moonshot.cn/v1/chat/completions",
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "ollama": "http://localhost:11434/api/chat",
            "exo": "http://localhost:52415/v1/chat/completions",
            "lmstudio": "http://localhost:1234/v1/chat/completions",
            "pollinations": "https://gen.pollinations.ai/v1/chat/completions",
            "nvidia": "https://integrate.api.nvidia.com/v1/chat/completions",
        }
        
        # Verwende Config-URL wenn vorhanden
        if provider in providers and providers[provider]:
            url = providers[provider].get("url")
            if url:
                return url
        
        return endpoints.get(provider)
    
    def test_model(self, tier: str, model_str: str, test_prompt: str = "Say 'OK' and nothing else.") -> Dict:
        """
        Testet ein einzelnes Modell.
        
        Args:
            tier: Der Tier-Name (super_easy, easy, etc.)
            model_str: Das komplette Model-String (z.B. "anthropic:claude-sonnet")
            test_prompt: Der Test-Prompt
            
        Returns:
            Dictionary mit Testergebnissen
        """
        provider, model_name = self.parse_model_string(model_str)
        endpoint = self.get_api_endpoint(provider)
        
        result = {
            "tier": tier,
            "model": model_str,
            "provider": provider,
            "model_name": model_name,
            "endpoint": endpoint,
            "success": False,
            "latency_ms": None,
            "tokens_per_sec": None,
            "error": None,
            "response": None
        }
        
        if not endpoint:
            result["error"] = f"Kein Endpoint für Provider '{provider}'"
            return result
        
        # API-Key aus Umgebung holen
        api_key = self._get_api_key(provider)
        if not api_key:
            result["error"] = f"Kein API-Key für Provider '{provider}'"
            return result
        
        # Request vorbereiten
        start_time = time.time()
        
        try:
            if provider == "anthropic":
                response = self._call_anthropic(endpoint, api_key, model_name, test_prompt)
            elif provider in ["openai", "kimi", "deepseek", "ollama", "exo", "lmstudio", "pollinations", "nvidia"]:
                response = self._call_openai_compatible(endpoint, api_key, model_name, test_prompt)
            elif provider == "google":
                response = self._call_google(endpoint, api_key, model_name, test_prompt)
            else:
                result["error"] = f"Provider '{provider}' nicht unterstützt"
                return result
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            result["success"] = True
            result["latency_ms"] = round(elapsed_ms, 2)
            result["response"] = response.get("content", "")[:100]  # Erste 100 Zeichen
            
            # Berechne Tokens/s wenn verfügbar
            usage = response.get("usage", {})
            total_tokens = usage.get("total_tokens", 0) or usage.get("completion_tokens", 0)
            if total_tokens > 0 and elapsed_ms > 0:
                result["tokens_per_sec"] = round((total_tokens / (elapsed_ms / 1000)), 2)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Holt den API-Key aus Umgebungsvariablen."""
        import os
        env_vars = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
            "kimi": "MOONSHOT_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "nvidia": "NVIDIA_API_KEY",
        }
        
        env_var = env_vars.get(provider)
        if env_var:
            return os.environ.get(env_var)
        
        # Für lokale Provider (ollama, exo, lmstudio) kein Key nötig
        if provider in ["ollama", "exo", "lmstudio", "pollinations"]:
            return "dummy-key"
        
        return None
    
    def _call_anthropic(self, endpoint: str, api_key: str, model: str, prompt: str) -> Dict:
        """Ruft Anthropic API auf."""
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        resp = requests.post(endpoint, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        
        result = resp.json()
        return {
            "content": result["content"][0]["text"],
            "usage": result.get("usage", {})
        }
    
    def _call_openai_compatible(self, endpoint: str, api_key: str, model: str, prompt: str) -> Dict:
        """Ruft OpenAI-kompatible API auf."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024
        }
        
        resp = requests.post(endpoint, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        
        result = resp.json()
        message = result["choices"][0]["message"]
        return {
            "content": message.get("content", ""),
            "usage": result.get("usage", {})
        }
    
    def _call_google(self, endpoint: str, api_key: str, model: str, prompt: str) -> Dict:
        """Ruft Google Gemini API auf."""
        url = f"{endpoint}/{model}:generateContent?key={api_key}"
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        resp = requests.post(url, json=data, timeout=60)
        resp.raise_for_status()
        
        result = resp.json()
        candidates = result.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
        else:
            text = ""
        
        return {
            "content": text,
            "usage": result.get("usageMetadata", {})
        }
    
    def run_tests(self, only_active: bool = True, max_workers: int = 3) -> List[Dict]:
        """
        Führt Tests für alle Modelle durch.
        
        Args:
            only_active: Wenn True, werden nur aktive (nicht auskommentierte) Modelle getestet
            max_workers: Anzahl paralleler Requests
            
        Returns:
            Liste aller Testergebnisse
        """
        models = self.load_models_from_config()
        
        # Filtere auskommentierte Modelle wenn gewünscht
        if only_active:
            models = [(t, m, c) for t, m, c in models if not c]
            print(f"🧪 Teste {len(models)} aktive Modelle...")
        else:
            print(f"🧪 Teste alle {len(models)} Modelle (inkl. auskommentierte)...")
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_model = {
                executor.submit(self.test_model, tier, model): (tier, model)
                for tier, model, _ in models
            }
            
            for future in concurrent.futures.as_completed(future_to_model):
                tier, model = future_to_model[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    status = "✅" if result["success"] else "❌"
                    latency = f"{result['latency_ms']}ms" if result["latency_ms"] else "N/A"
                    print(f"{status} {tier:12} | {model:40} | {latency}")
                    
                except Exception as e:
                    print(f"❌ {tier:12} | {model:40} | ERROR: {e}")
                    results.append({
                        "tier": tier,
                        "model": model,
                        "success": False,
                        "error": str(e)
                    })
        
        self.results = results
        return results
    
    def print_summary(self):
        """Gibt eine Zusammenfassung der Ergebnisse aus."""
        if not self.results:
            print("\n⚠️  Keine Ergebnisse vorhanden.")
            return
        
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        print("\n" + "="*70)
        print("📊 ZUSAMMENFASSUNG")
        print("="*70)
        
        print(f"\n✅ Erfolgreich: {len(successful)}/{len(self.results)}")
        print(f"❌ Fehlgeschlagen: {len(failed)}/{len(self.results)}")
        
        if successful:
            latencies = [r["latency_ms"] for r in successful if r["latency_ms"]]
            if latencies:
                print(f"\n⏱️  Durchschnittliche Latenz: {sum(latencies)/len(latencies):.2f}ms")
                print(f"⚡ Schnellstes Modell: {min(latencies):.2f}ms")
                print(f"🐐 Langsamstes Modell: {max(latencies):.2f}ms")
        
        if failed:
            print("\n❌ Fehlgeschlagene Tests:")
            for r in failed:
                print(f"   • {r['tier']}: {r['model']} — {r['error']}")
        
        # Top 3 schnellste Modelle
        if successful:
            print("\n🏆 TOP 3 (nach Latenz):")
            sorted_results = sorted(
                [r for r in successful if r["latency_ms"]],
                key=lambda x: x["latency_ms"]
            )[:3]
            for i, r in enumerate(sorted_results, 1):
                print(f"   {i}. {r['model']:40} | {r['latency_ms']}ms")
        
        print("\n" + "="*70)
    
    def export_results(self, filename: str):
        """Exportiert Ergebnisse als JSON."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Ergebnisse exportiert nach: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Multispeedtest — Teste alle konfigurierten Modelle"
    )
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Pfad zur config.yaml (default: config.yaml)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Auch auskommentierte Modelle testen"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=3,
        help="Anzahl paralleler Requests (default: 3)"
    )
    parser.add_argument(
        "--output", "-o",
        help="JSON-Datei für Ergebnis-Export"
    )
    parser.add_argument(
        "--prompt", "-p",
        default="Say 'OK' and nothing else.",
        help="Test-Prompt (default: 'Say OK and nothing else.')"
    )
    
    args = parser.parse_args()
    
    # Zeige Info über Smart Config
    if SMART_CONFIG_AVAILABLE:
        print("🔧 Smart Config Features aktiviert (parse_yaml_with_comments)")
    else:
        print("⚠️  Smart Config Features nicht verfügbar (freeride.py nicht gefunden)")
    
    # Führe Tests durch
    tester = Multispeedtest(args.config)
    tester.run_tests(only_active=not args.all, max_workers=args.workers)
    tester.print_summary()
    
    if args.output:
        tester.export_results(args.output)


if __name__ == "__main__":
    main()
